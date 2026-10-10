import hashlib
from pathlib import Path

import numpy as np
import pytest

from valid_point.attacks.overlays import apply_overlay, seed_key
from valid_point.io.mixed_signals import write_pcd
from valid_point.replay import AllowedSource, ReplayConfig, replay
from valid_point.development_scores import ExploratoryReference, fit_exploratory, normalize_raw, decide
from valid_point.evidence.density import CELL_IDS
from valid_point.temporal import TemporalEWMA


def fixture(tmp_path):
    clouds=tmp_path/'clouds'; poses=tmp_path/'poses'; extras=tmp_path/'derived'; evaluator=tmp_path/'evaluator'
    for d in (clouds,poses,extras,evaluator): d.mkdir()
    events=[]
    for stream in ('003','004'):
        for i in range(12):
            filename=f'{stream}_{i}_{100+i//10}.{(i%10)*100000000:09d}.pcd'
            values=np.column_stack((np.linspace(10,20,100).astype('f4'),np.ones(100,'f4'),
                                    np.zeros(100,'f4'),np.zeros(100,'f4')))
            values[i,0]+=i*.01
            write_pcd(clouds/filename,values)
    from valid_point.replay import CloudEvent
    from valid_point.io.mixed_signals import parse_cloud_name
    for p in clouds.glob('*.pcd'):
        name=parse_cloud_name(p.name)
        events.append(CloudEvent(name.path,name.stream,name.principal,name.sync_id,name.source_ns,name.source_ns,name.source_ns,p))
    return clouds,poses,extras,evaluator,sorted(events,key=lambda e:(e.source_ns,e.stream))


def decisions(events,source):
    records=replay(events,source,config=ReplayConfig(min_voxels=1),poses={'003':[],'004':[],'laser':[]})
    # Fixed test reference makes scores and state numeric; evaluator files are
    # absent from every operational function signature and allowlist.
    refs={(stream,'D',cell):ExploratoryReference(stream,'D',cell,0.,0.,100.,50,
           'mini_7','supported_exploratory',('fixture',),'test')
          for stream in ('003','004') for cell in CELL_IDS}
    state=TemporalEWMA(.1,.5,min_updates=2)
    out=[]
    for row in records:
        norm=normalize_raw(row,refs,'test')
        d=decide(row,norm,'D-only')
        z=state.update(episode='arm',principal=row.principal,sensor=row.stream,method_arm='D-only',
                       reference_version='test',source_ns=row.source_ns,A=d.A,reason=d.reason)
        out.append((d.as_dict(),z.as_dict()))
    return out,state.checkpoint(),list(source.access_log)


def test_changed_withheld_evaluator_and_positive_leakage_control(tmp_path):
    clouds,poses,extras,evaluator,events=fixture(tmp_path)
    secret=evaluator/'labels_boxes_masks_schedule_clean_outcomes.json'
    secret.write_text('{"GT":1,"attack":true}')
    source=AllowedSource(clouds,poses,extras)
    first=decisions(events,source)
    secret.write_text('{"GT":999,"attack":false}')
    second=decisions(events,AllowedSource(clouds,poses,extras))
    secret.unlink()
    third=decisions(events,AllowedSource(clouds,poses,extras))
    assert first==second==third
    # Deliberate forbidden read must fail through the same source boundary.
    (evaluator/'not_allowed').write_text('forbidden')
    with pytest.raises(PermissionError):
        source._check(evaluator/'not_allowed',source.clouds_dir)
    def leaky(): return secret.read_text() if secret.exists() else 'withheld'
    def require_invariant(left,right): assert left==right
    before=leaky(); secret.write_text('changed'); after=leaky()
    with pytest.raises(AssertionError):
        require_invariant(before,after)


def test_original_companions_and_prefix_invariant(tmp_path):
    clouds,poses,extras,evaluator,events=fixture(tmp_path)
    hashes={e.cloud_id:hashlib.sha256(e.path.read_bytes()).hexdigest() for e in events}
    original=decisions(events,AllowedSource(clouds,poses))
    selected=next(e for e in events if e.stream=='003' and e.sync_id==10)
    from valid_point.io.mixed_signals import read_pcd
    with selected.path.open('rb') as f: _,values=read_pcd(f)
    overlay=apply_overlay(values,family='random_removal',severity=.3,
                          key=seed_key('mini_7','003',selected.cloud_id,'random_removal',.3))
    write_pcd(extras/selected.cloud_id,overlay.values)
    assert all(hashlib.sha256(e.path.read_bytes()).hexdigest()==hashes[e.cloud_id] for e in events)
    from dataclasses import replace
    changed=[replace(e,path=extras/e.cloud_id) if e==selected else e for e in events]
    attacked=decisions(changed,AllowedSource(clouds,poses,extras))
    first_changed=next(i for i,e in enumerate(events) if e==selected)
    assert original[0][:first_changed]==attacked[0][:first_changed]
    assert [x for x,e in zip(original[0],events) if e.stream=='004']==[x for x,e in zip(attacked[0],events) if e.stream=='004']


def test_exploratory_pooled_support_counts_distinct_cloud_rows():
    from types import SimpleNamespace
    sample=[SimpleNamespace(stream='003',cloud_id=f'cloud{i}',
                            density=SimpleNamespace(counts=tuple(i+j for j in range(32))),
                            geometry=SimpleNamespace(distance_m=None,gap_s=None)) for i in range(10)]
    refs=fit_exploratory(sample,segment='mini_7',reference_id='test')
    # Eight sectors per range create 80 values, but only ten actual clouds.
    assert refs[('003','D','range:r0')].observations==80
    assert refs[('003','D','range:r0')].status=='low_support'


def test_attacked_geometry_uses_attacked_prior_cloud(tmp_path):
    from dataclasses import replace
    from valid_point.io.mixed_signals import parse_cloud_name
    from valid_point.replay import CloudEvent, PoseEvent
    clouds=tmp_path/'base'; extra=tmp_path/'derived'; poses_dir=tmp_path/'poses'
    for directory in (clouds,extra,poses_dir): directory.mkdir()
    values=np.array([[0,0,0,0],[2,0,0,0],[4,0,0,0],[6,0,0,0]],dtype=np.float32)
    events=[]
    for index,sub in enumerate(('0','100000000')):
        path=clouds/f'003_{index}_100.{sub}.pcd'
        write_pcd(path,values)
        name=parse_cloud_name(path.name)
        events.append(CloudEvent(name.path,name.stream,name.principal,index,name.source_ns,name.source_ns,name.source_ns,path))
    poses=[PoseEvent(f'pose{i}','003',e.source_ns,e.source_ns,np.eye(4),True) for i,e in enumerate(events)]
    original=replay(events,AllowedSource(clouds,poses_dir),config=ReplayConfig(min_voxels=1),poses={'003':poses})
    changed=values.copy(); changed[0,0]+=1
    write_pcd(extra/events[0].cloud_id,changed)
    attacked_events=[replace(events[0],path=extra/events[0].cloud_id),events[1]]
    attacked=replay(attacked_events,AllowedSource(clouds,poses_dir,extra),config=ReplayConfig(min_voxels=1),poses={'003':poses})
    assert original[1].geometry.status=='known' and original[1].geometry.distance_m==pytest.approx(0)
    assert attacked[1].geometry.status=='known' and attacked[1].geometry.distance_m>0
    assert attacked[1].history_id==events[0].cloud_id
