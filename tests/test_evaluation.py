"""R05 invariants: no expected favorable scientific outcome."""
from dataclasses import replace
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest
from valid_point.evaluation.real import (ARMS, VERSIONS, Reference, calibrate, digest,
    episode_grid, fit_references, normalize, require_prediction_seal, score_records,
    write_json, write_records, read_records, raw_from_dict, local_inventory)
from valid_point.evaluation.splits import Fold
from valid_point.evidence.density import CELL_IDS, DensityRaw
from valid_point.evidence.temporal_geometry import GeometryRaw
from valid_point.replay import AllowedSource, replay

FOLD=Fold('F0','C0','C1',('C2','C3'))


def training(n=110):
    def rows(segment):
        return [SimpleNamespace(stream='003',cloud_id=f'{segment}-{i}',input_sha256=str(i),
            density=SimpleNamespace(counts=tuple(i+j for j in range(32))),
            geometry=SimpleNamespace(distance_m=i/100,gap_s=.1),
            as_dict=lambda i=i,s=segment:{'segment':s,'i':i}) for i in range(n)]
    return {'C2':rows('C2'),'C3':rows('C3')}


def test_grouped_fit_actual_quantiles_and_distinct_pooled_support():
    refs=fit_references(training(),FOLD)
    ref=refs[('003','D',CELL_IDS[0])]
    assert ref.status=='SUPPORTED' and ref.distinct_clouds==220
    assert ref.u==pytest.approx(np.quantile(list(range(110))*2,.95))
    assert ref.b==pytest.approx(4*(ref.u-54.5))
    assert ref.segment_counts=={'C2':110,'C3':110}
    sparse=fit_references(training(15),FOLD)
    assert sparse[('003','D','range:r0')].observations==240
    assert sparse[('003','D','range:r0')].status=='LOW_SUPPORT'
    assert sparse[('004','G','all')].status=='LOW_SUPPORT'


def test_lineage_missing_segment_duplicate_and_no_mini7():
    with pytest.raises(ValueError): fit_references({'C2':training()['C2']},FOLD)
    with pytest.raises(ValueError): fit_references({'mini_7':training()['C2'],'C3':[]},FOLD)
    sample=training(); sample['C2']*=2
    with pytest.raises(ValueError): fit_references(sample,FOLD)


def test_all_frozen_attempts_and_benign_identity_separation():
    method=json.loads(Path('configs/replay_evaluation.json').read_text())
    grid=episode_grid(method)
    assert len(grid)==62 and len({s['episode'] for s in grid})==62
    assert sum(s['kind']=='attack' for s in grid)==30
    assert sum(s['kind']=='benign' for s in grid)==26
    assert sum(s['kind']=='identity' for s in grid)==5
    assert all(s['severity']>0 for s in grid if s['kind']=='attack')


def test_thresholds_independent_actual_scores_ties_and_no_power():
    refs=fit_references(training(),FOLD)
    rows=[]
    for version in VERSIONS:
        for arm in ARMS:
            for i in range(220):
                score=i/220 if version=='memoryless' else i/440
                if arm=='G-only': score=None
                rows.append({'sensor':'003','arm':arm,'version':version,'score':score,'raw_record_id':str(i)})
    c=calibrate(rows,FOLD,refs)
    assert c[('003','D-only','memoryless')]['threshold']==pytest.approx(218/220)
    assert c[('003','D-only','EWMA')]['threshold']==pytest.approx(218/440)
    assert c[('003','G-only','EWMA')]['threshold'] is None
    assert len({x['threshold_id'] for x in c.values()})==60
    for row in rows: row['score']=1
    assert calibrate(rows,FOLD,refs)[('003','D-only','EWMA')]['status']=='NO_POWER'


def fixture_pipeline(tmp_path):
    from test_replay_isolation import fixture
    clouds,poses,extras,evaluator,events=fixture(tmp_path)
    refs=fit_references(training(),FOLD)
    def run(evs):
        source=AllowedSource(clouds,poses,extras)
        raw=list(replay(evs,source,poses={'003':[],'004':[],'laser':[]}))
        scores,state=score_records(raw,refs,episode='opaque',first_ns=events[0].source_ns)
        return raw,scores,state,source.access_log
    return events,extras,evaluator,run


def test_production_future_prefix_companions_and_per_episode_reset(tmp_path):
    from valid_point.io.mixed_signals import write_pcd
    from valid_point.evaluation.real import read_values
    events,extras,evaluator,run=fixture_pipeline(tmp_path)
    before=run(events)
    e=next(e for e in events if e.stream=='003' and e.sync_id==10)
    values=read_values(e.path); values[:,0]+=7
    write_pcd(extras/e.cloud_id,values)
    after=run([replace(x,path=extras/x.cloud_id) if x==e else x for x in events])
    assert [r for r in before[1] if r['source_ns']<e.source_ns]==[r for r in after[1] if r['source_ns']<e.source_ns]
    assert [r for r in before[1] if r['sensor']=='004']==[r for r in after[1] if r['sensor']=='004']
    assert before==run(events)
    assert all(s['key'][2] in ('003','004') for v in before[2].values() for s in v['states'])


def test_evaluator_withheld_changed_and_leaky_positive_control(tmp_path,monkeypatch):
    events,extras,evaluator,run=fixture_pipeline(tmp_path)
    secret=evaluator/'labels_GT_schedule_masks_clean_outcomes.json'
    secret.write_text('{"value":1}')
    first=run(events)
    def deliberately_leaky_pipeline(): return run(events),secret.read_text()
    leaked_before=deliberately_leaky_pipeline()
    secret.write_text('{"value":999}')
    assert first==run(events)
    with pytest.raises(AssertionError): assert leaked_before==deliberately_leaky_pipeline()
    original_open=Path.open
    def guarded(path,*args,**kwargs):
        if evaluator in path.parents: raise PermissionError('evaluator boundary')
        return original_open(path,*args,**kwargs)
    monkeypatch.setattr(Path,'open',guarded)
    assert first==run(events)
    with pytest.raises(PermissionError): deliberately_leaky_pipeline()


def test_prediction_seal_requires_all_folds_and_detects_extra_or_mutated_file(tmp_path):
    directory=tmp_path/'predictions'; directory.mkdir()
    write_json(directory/'one.json',{'score':None})
    for fold in ('F0','F1','F2','F3'): write_json(directory/fold/'complete.json',{'status':'complete'})
    seal={'folds':['F0','F1','F2','F3'],'files':{str(p.relative_to(directory)):digest(p) for p in directory.rglob('*') if p.is_file()}}
    require_prediction_seal(directory,seal)
    with pytest.raises(ValueError): require_prediction_seal(directory,{**seal,'folds':['F0']})
    (directory/'one.json').write_text('{}')
    with pytest.raises(ValueError): require_prediction_seal(directory,seal)


def test_deterministic_record_serialization_and_no_overwrite(tmp_path):
    a=tmp_path/'a.gz'; b=tmp_path/'b.gz'
    write_records(a,[{'x':None,'y':[1,2]}]); write_records(b,[{'y':[1,2],'x':None}])
    assert digest(a)==digest(b) and read_records(a)==[{'x':None,'y':[1,2]}]
    with pytest.raises(FileExistsError): write_records(a,[])


def test_partial_inventory_is_redundant_without_reading_H(tmp_path):
    roles=json.loads(Path('configs/segment_roles.json').read_text())
    path=tmp_path/'data/mixed_signals'/roles['revision']/'archives/train/mini_11.tar.partial'
    path.parent.mkdir(parents=True); path.write_bytes(b'duplicate')
    result=local_inventory(tmp_path,roles)
    assert result['redundant_partials'][0]['disposition']=='REDUNDANT_DUPLICATE_DO_NOT_RESUME'
    assert not result['H_opened'] and path.read_bytes()==b'duplicate'


def test_grouped_macro_micro_undefined_and_leave_one():
    from valid_point.evaluation.statistics import grouped_rates
    base={'family':'clean','severity':0,'schedule':'none','kind':'clean','sensor':'003','arm':'D-only','version':'memoryless','metric':'eligible_fpr'}
    rows=[{**base,'segment':s,'numerator':n,'denominator':d,'value':None if not d else n/d}
          for s,n,d in [('C0',1,2),('C1',0,8),('C2',0,0),('C3',2,2)]]
    summary=grouped_rates(rows)[0]
    assert summary['macro']==.5 and summary['micro']==.25
    assert summary['omitted_segments']==['C2'] and summary['contributing_segments']==3
    assert summary['leave_one_segment']['C3']==.25
    with pytest.raises(ValueError): grouped_rates(rows+[rows[0]])


def test_schedule_join_preserves_failed_attempt_and_honest_companion():
    from valid_point.evaluation.statistics import join_episode
    base={'cloud_id':'x','sensor':'003','time_s':5.,'cloud_sha256':'hash','state':None,'alarm':True,'score':1.}
    attempts=[{'cloud_id':'x','reader_valid':False,'injection_failed':True,'realized_changed_rows':0}]
    rows=join_episode([base,{**base,'sensor':'004','cloud_id':'y'}],attempts,{},[(5,7)],'003')
    assert rows[0]['scheduled'] and not rows[0]['reader_valid']
    assert rows[1]['reader_valid'] and rows[1]['realized_changed_rows']==0


def test_final_recovery_after_last_burst_includes_earlier_alarm():
    from valid_point.evaluation.statistics import final_recovery
    def r(t,alarm,changed=0,reset=False):
        return {'time_s':t,'alarm':alarm,'reader_valid':True,'realized_changed_rows':changed,'injection_failed':False,'reset':reset}
    rows=[r(5.2,True,10),r(10.2,False,10)]+[r(12+i*.5,False) for i in range(5)]
    assert final_recovery(rows,[(5,7),(10,12)])=={'value_s':2.,'status':'RECOVERED','last_offset_s':12}
    rows[-2]=r(13.5,None)
    assert final_recovery(rows,[(5,7),(10,12)])['status']=='UNDEFINED_INTERRUPTED_SUPPORT'


def test_common_support_retains_all_attempt_and_unknown_time():
    from valid_point.evaluation.statistics import exposure_and_common_support
    rows=[]
    for i in range(3):
        for arm in ARMS:
            for v in VERSIONS:
                rows.append({'sensor':'003','cloud_id':str(i),'arm':arm,'version':v,'time_s':i*.1,
                    'alarm':None if i==1 and v=='EWMA' else False,'reset':False})
    times,common=exposure_and_common_support(rows,{'kind':'clean'},'C0')
    assert all(r['common_known_events']==2 and r['all_attempt_events']==3 for r in common)
    assert next(r for r in times if r['version']=='EWMA')['eligible_seconds']==0


def test_negative_pose_clock_skew_cannot_advance_availability():
    from valid_point.replay import PoseEvent, _select_pose
    real_available=5_000_000_000
    from valid_point.evaluation.real import alignment_poses
    original=PoseEvent('original-stamp-5s','003',real_available,real_available,np.eye(4),True)
    pose=alignment_poses([original],family='modeled_source_clock_skew_ms',severity=-50,first_ns=0,intervals=[(5,7)])[0]
    assert pose.source_ns==real_available-50_000_000 and pose.available_ns==real_available
    selected,reason=_select_pose([pose],4_990_000_000,4_990_000_000,150_000_000)
    assert selected is None and reason=='NO_CAUSAL_POSE'
    assert _select_pose([pose],5_010_000_000,5_010_000_000,150_000_000)[0]==pose


def test_causal_raw_memo_matches_production_and_checks_changed_history(tmp_path):
    from test_replay_isolation import fixture
    from valid_point.evaluation.real import CausalRawMemo,read_values
    from valid_point.replay import PoseEvent
    from valid_point.io.mixed_signals import write_pcd
    clouds,pose_dir,extras,evaluator,events=fixture(tmp_path)
    poses={s:[PoseEvent(s+':'+str(e.source_ns),s,e.source_ns,e.source_ns,np.eye(4),True) for e in events if e.stream==s] for s in ('003','004')}
    expected=replay(events,AllowedSource(clouds,pose_dir,extras),poses=poses)
    memo=CausalRawMemo()
    assert memo.replay(events,AllowedSource(clouds,pose_dir,extras),poses)==expected
    memo.seed(events,expected,poses)
    source=AllowedSource(clouds,pose_dir,extras)
    assert memo.replay(events,source,poses)==expected and len(source.access_log)==len(events)
    e=events[-4]; values=read_values(e.path); values[:,0]+=1
    write_pcd(extras/e.cloud_id,values)
    changed=[replace(x,path=extras/x.cloud_id) if x==e else x for x in events]
    actual=memo.replay(changed,AllowedSource(clouds,pose_dir,extras),poses)
    assert actual==replay(changed,AllowedSource(clouds,pose_dir,extras),poses=poses)
    assert actual[:events.index(e)]==expected[:events.index(e)]


def test_raw_memo_does_not_read_future_event(tmp_path):
    from test_replay_isolation import fixture
    from valid_point.evaluation.real import CausalRawMemo
    clouds,pose_dir,extras,evaluator,events=fixture(tmp_path)
    e=replace(events[0],deadline_ns=events[0].source_ns-1)
    source=AllowedSource(clouds,pose_dir,extras)
    row=CausalRawMemo().replay([e],source,{'003':[]})[0]
    assert row.reason=='FUTURE_SOURCE' and source.access_log==[]


def test_seal_ignores_only_finder_metadata_and_still_rejects_study_changes(tmp_path):
    directory=tmp_path/'predictions'; directory.mkdir()
    for fold in ('F0','F1','F2','F3'): write_json(directory/fold/'complete.json',{'status':'complete'})
    (directory/'.DS_Store').write_bytes(b'original Finder state')
    seal={'folds':['F0','F1','F2','F3'],'files':{str(p.relative_to(directory)):digest(p) for p in directory.rglob('*') if p.is_file()}}
    (directory/'.DS_Store').write_bytes(b'updated Finder state')
    require_prediction_seal(directory,seal)
    (directory/'unexpected.json').write_text('{}')
    with pytest.raises(ValueError): require_prediction_seal(directory,seal)


def test_reporting_recovers_original_ids_after_sorted_protocol_serialization(tmp_path):
    from valid_point.evaluation.statistics import recorded_episode_grid
    method=json.loads(Path('configs/replay_evaluation.json').read_text())
    stored=json.loads(json.dumps(method,sort_keys=True))
    assert episode_grid(method)!=episode_grid(stored)
    config=tmp_path/'configs/replay_evaluation.json';config.parent.mkdir()
    config.write_text(json.dumps(method))
    assert recorded_episode_grid(tmp_path,stored)==episode_grid(method)
    stored['calibration']['alpha']=.02
    with pytest.raises(ValueError): recorded_episode_grid(tmp_path,stored)
