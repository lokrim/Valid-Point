"""Offline R05 summaries. Entry point refuses unsealed predictions."""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv
import json
from pathlib import Path
import numpy as np
from valid_point.evaluation.real import (read_records, write_json, digest,
    episode_grid, require_prediction_seal, ARMS, VERSIONS)
from valid_point.evaluation.metrics import event_metrics, false_alarm_metrics, episode_metrics


def table(run, name, rows):
    keys=list(dict.fromkeys(k for r in rows for k in r)) or ['status']
    with (run/(name+'.csv')).open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys); w.writeheader()
        w.writerows({k:json.dumps(v,sort_keys=True) if isinstance(v,(list,dict,tuple)) else v for k,v in r.items()} for r in rows)
    with (run/(name+'.md')).open('x') as f:
        f.write(f'# {name}\n\nRun {run.name}; complete {len(rows)} rows. Frozen R05 predictions joined offline.\n\n')
        f.write('| '+' | '.join(keys)+' |\n| '+' | '.join('---' for _ in keys)+' |\n')
        for r in rows: f.write('| '+' | '.join(str(r.get(k,'')).replace('|','\\|').replace('\n',' ') for k in keys)+' |\n')
    write_json(run/(name+'.provenance.json'),{'run':run.name,'stage':'R05','rows':len(rows),
        'prediction_seal_sha256':digest(run/'prediction_seal.json'),'units':'metric ratios dimensionless; delay/recovery seconds; raw D points/cell/frame; G metres',
        'files':{suffix:digest(run/(name+suffix)) for suffix in ('.csv','.md')}})


def grouped_rates(rows):
    groups=defaultdict(list)
    for r in rows:
        if 'numerator' not in r: continue
        key=tuple(r[k] for k in ('family','severity','schedule','kind','sensor','arm','version','metric'))
        groups[key].append(r)
    output=[]
    for key,sample in groups.items():
        if len({r['segment'] for r in sample})!=len(sample): raise ValueError('duplicate segment metric')
        values={r['segment']:r['value'] for r in sample if r['value'] is not None}
        omitted=sorted({'C0','C1','C2','C3'}-set(values))
        n=sum(r['numerator'] for r in sample); d=sum(r['denominator'] for r in sample)
        base=dict(zip(('family','severity','schedule','kind','sensor','arm','version','metric'),key))
        output.append({**base,'macro':sum(values.values())/len(values) if values else None,
            'micro':n/d if d else None,'micro_numerator':n,'micro_denominator':d,
            'contributing_segments':len(values),'omitted_segments':omitted,
            'segment_values':values,'range':None if not values else [min(values.values()),max(values.values())],
            'leave_one_segment':{s:sum(v for k,v in values.items() if k!=s)/(len(values)-1) for s in values if len(values)>1},
            'uncertainty':'descriptive only; shared cross-fold training; session independence unverified; no between-session CI'})
    return output


def join_episode(scores, attempts, spec, intervals, sender):
    lookup={a['cloud_id']:a for a in attempts}
    rows=[]
    for p in scores:
        row=dict(p)
        scheduled=any(a<=p['time_s']<b for a,b in intervals)
        a=lookup.get(p['cloud_id'],{}) if p['sensor']==sender else {}
        row.update(reader_valid=a.get('reader_valid',p['cloud_sha256'] is not None),
            realized_changed_rows=a.get('realized_changed_rows',0),injection_failed=a.get('injection_failed',False),
            reset=bool(p['state'] and p['state']['reset']),scheduled=scheduled)
        rows.append(row)
    return rows


def summarize_episode(rows, spec, *, segment, sender, intervals):
    grouped=defaultdict(list)
    for row in rows: grouped[(row['sensor'],row['arm'],row['version'])].append(row)
    metrics=[]; coverage=[]; outcomes=[]
    for (sensor,arm,version),sample in grouped.items():
        base={'segment':segment,**spec,'sensor':sensor,'arm':arm,'version':version}
        reasons=Counter(r['reason'] for r in sample if r['alarm'] is None)
        known=sum(r['alarm'] is not None for r in sample)
        coverage.append({**base,'attempts':len(sample),'known_alarm':known,'unknown_alarm':len(sample)-known,
            'known_score':sum(r['score'] is not None for r in sample),'coverage':known/len(sample) if sample else None,
            'unknown_reasons':dict(reasons)})
        attacked=spec['kind']=='attack' and sensor==sender
        selected=[r for r in sample if r['scheduled']] if attacked else sample
        result=event_metrics([dict(r,segment=segment) for r in selected]) if attacked else false_alarm_metrics(sample)
        for metric,r in result.items():
            if isinstance(r,dict): metrics.append({**base,'population':'scheduled_sender' if attacked else 'honest_companion' if spec['kind']=='attack' else spec['kind'],
                'metric':metric,**r})
        if attacked:
            for index,(onset,offset) in enumerate(intervals):
                outcome=episode_metrics(sample,onset_s=onset,offset_s=offset,end_s=max(offset,max(r['time_s'] for r in sample)))
                outcomes.append({**base,'interval':index,'onset_s':onset,'offset_s':offset,**outcome,
                    'final_recovery':final_recovery(sample,intervals)})
            detected=any(r['alarm'] is True and r['reader_valid'] and r['realized_changed_rows']>0 and not r['injection_failed'] for r in selected)
            realized=any(r['reader_valid'] and r['realized_changed_rows']>0 for r in selected)
            metrics.extend([{**base,'population':'episode','metric':'episode_recall','numerator':int(detected),'denominator':1,'value':float(detected),'status':'defined'},
                {**base,'population':'realized_episode','metric':'realized_episode_recall','numerator':int(detected),'denominator':int(realized),
                 'value':float(detected) if realized else None,'status':'defined' if realized else 'NO_REALIZED_EPISODE'}])
    return metrics,coverage,outcomes


def figure_export(fig,run,stem):
    for ext in ('png','pdf','svg'): fig.savefig(run/f'{stem}.{ext}',dpi=130,bbox_inches='tight')
    write_json(run/(stem+'.provenance.json'),{'run':run.name,'stage':'R05','prediction_seal_sha256':digest(run/'prediction_seal.json'),
        'display_selection':'predeclared displacement 1 m sustained; first/middle/last scheduled geometry; all companion sensors',
        'files':{ext:digest(run/f'{stem}.{ext}') for ext in ('png','pdf','svg')}})


def make_figures(run,method,grid):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    spec=next(s for s in grid if s['kind']=='attack' and s['family']=='displacement' and s['severity']==1 and s['schedule']=='sustained')
    clean_spec=next(s for s in grid if s['kind']=='clean')
    for role in ('C0','C1','C2','C3'):
        fold='F'+role[-1]; directory=run/'predictions'/fold
        if not (directory/spec['episode']/'scores.jsonl.gz').exists(): continue
        raw=read_records(directory/spec['episode']/'raw.jsonl.gz')
        pred=read_records(directory/spec['episode']/'scores.jsonl.gz')
        clean=read_records(directory/clean_spec['episode']/'scores.jsonl.gz')
        first=min(r['source_ns'] for r in raw)
        for arm in ARMS:
            fig,axes=plt.subplots(7,5,figsize=(22,22),sharex='col',layout='constrained')
            for col,sensor in enumerate(('003','004','laser','top','dome')):
                rr=[r for r in raw if r['stream']==sensor]; t=[(r['source_ns']-first)/1e9 for r in rr]
                pp=[p for p in pred if p['sensor']==sensor and p['arm']==arm and p['version']=='EWMA']
                cc=[p for p in clean if p['sensor']==sensor and p['arm']==arm and p['version']=='EWMA']
                def numeric(values): return [np.nan if v is None else v for v in values]
                counts=np.array([r['density']['counts'] if r['density']['counts'] is not None else [np.nan]*32 for r in rr]).T
                heat=axes[0,col].imshow(counts,aspect='auto',origin='lower',extent=(min(t),max(t),-.5,31.5))
                fig.colorbar(heat,ax=axes[0,col],label='points/cell/frame',shrink=.7)
                axes[0,col].set_ylabel('D cell (0–31)'); axes[0,col].set_title(sensor+(' (shared RSU)' if sensor in ('top','dome') else ''))
                axes[1,col].plot(t,numeric([r['geometry']['distance_m'] for r in rr])); axes[1,col].set_ylabel('G q90 (m)')
                for factor in ('d','g'): axes[2,col].plot([p['time_s'] for p in pp],numeric([p['normalized'][factor] for p in pp]),label=factor)
                axes[2,col].set_ylabel('factor anomaly'); axes[2,col].legend(fontsize=7)
                for field in ('A','C'):
                    axes[3,col].plot([p['time_s'] for p in pp],numeric([p[field] for p in pp]),label=field)
                axes[3,col].plot([p['time_s'] for p in cc],numeric([p['A'] for p in cc]),ls=':',label='clean A'); axes[3,col].legend(fontsize=7)
                for field in ('Z','C_time'):
                    axes[4,col].plot([p['time_s'] for p in pp],numeric([p['state'][field] for p in pp]),label=field)
                axes[4,col].plot([p['time_s'] for p in pp],numeric([p['threshold'] for p in pp]),ls='--',label='EWMA threshold'); axes[4,col].legend(fontsize=7)
                axes[5,col].scatter([p['time_s'] for p in pp],[-.2 if p['alarm'] is None else int(p['alarm']) for p in pp],s=3)
                axes[5,col].set_yticks([-.2,0,1],['unknown','quiet','alarm']); axes[5,col].set_ylabel('alarm eligibility')
                axes[6,col].plot(t,numeric([r['pose_age_s'] for r in rr]),label='pose age')
                axes[6,col].plot(t,[np.nan,*np.diff(t)],label='cloud gap'); axes[6,col].legend(fontsize=7); axes[6,col].set_ylabel('seconds'); axes[6,col].set_xlabel('acquisition elapsed (s)')
                for ax in axes[:,col]: ax.axvspan(5,15,alpha=.09,color='red'); ax.grid(alpha=.15)
            fig.suptitle(f'{role} / {fold} / {arm}: clean and displacement 1 m; evaluator interval added after seal\nNaN gaps are unknown; null thresholds remain unavailable; all five streams retained')
            figure_export(fig,run,f'F_R05_timelines_{role}_{fold}_{arm.replace("/","_")}_{run.name}'); plt.close(fig)
        files=sorted((run/'evaluator'/role/spec['episode']).glob('geometry_*.npz'))
        if not files:
            fig,ax=plt.subplots(figsize=(8,3)); ax.axis('off'); ax.text(.05,.5,'Geometry unavailable: all selected injections failed; see attempt ledger.')
            figure_export(fig,run,f'F_R05_geometry_{role}_{fold}_{run.name}'); plt.close(fig)
            continue
        fig,axes=plt.subplots(len(files),4,figsize=(18,5*len(files)),squeeze=False,layout='constrained')
        for i,path in enumerate(files):
            with np.load(path) as z:
                clouds=[z['clean'][:,:3],z['derived'][:,:3]]; pose=z['pose']; cloud_id=str(z['cloud_id'])
            from valid_point.io.mixed_signals import TOP_FROM_MAP
            for j,cloud in enumerate(clouds):
                axes[i,j].scatter(cloud[:,0],cloud[:,1],s=.15); axes[i,j].set(xlim=(-80,80),ylim=(-80,80),xlabel='native x (m)',ylabel='native y (m)',title=('clean' if j==0 else 'attacked')+' '+cloud_id)
                common=cloud@pose[:3,:3].T+pose[:3,3]+TOP_FROM_MAP
                axes[i,j+2].scatter(common[:,0],common[:,1],s=.15); axes[i,j+2].set(xlim=(-100,100),ylim=(-100,100),xlabel='top x (m)',ylabel='top y (m)',title='top frame '+('clean' if j==0 else 'attacked'))
                axes[i,j].set_aspect('equal'); axes[i,j+2].set_aspect('equal')
        fig.suptitle(f'{role}/{fold}: deterministic first/middle/last scheduled displacement; metre geometry, fixed bounds')
        figure_export(fig,run,f'F_R05_geometry_{role}_{fold}_{run.name}'); plt.close(fig)
    with (run/'T_R05_grouped.csv').open() as f: grouped=list(csv.DictReader(f))
    fig,axes=plt.subplots(1,3,figsize=(16,5),layout='constrained')
    for ax,metric in zip(axes,('eligible_fpr','all_attempt_recall','eligible_coverage')):
        for arm in ARMS:
            yy=[]
            for version in VERSIONS:
                values=[float(r['macro']) for r in grouped if r['metric']==metric and r['sensor']=='003' and r['arm']==arm and r['version']==version and r['macro']!='' and (r['kind']=='attack' if metric=='all_attempt_recall' else r['kind']=='clean')]
                yy.append(np.mean(values) if values else np.nan)
            ax.plot(list(VERSIONS),yy,'o-',label=arm)
        ax.set(title=metric+'; equal cell/segment means',ylabel='rate',ylim=(-.03,1.03)); ax.tick_params(axis='x',rotation=25); ax.legend(fontsize=8); ax.grid(alpha=.2)
    fig.suptitle('003: independently calibrated component / temporal arms. Missing cells stay blank; no IID intervals.')
    figure_export(fig,run,'F_R05_ablations'); plt.close(fig)


def report_run(root,run,note):
    seal=json.loads((run/'prediction_seal.json').read_text()); require_prediction_seal(run/'predictions',seal)
    protocol=json.loads((run/'protocol.json').read_text()); method=protocol['method']; grid=episode_grid(method)
    metrics=[]; coverage=[]; failures=[]; support=[]; flows=[]; outcomes=[]; paired=[]; time_rows=[]; common=[]; sessions=[]; integrity=[]
    for role in ('C0','C1','C2','C3'):
        fold='F'+role[-1]; directory=run/'predictions'/fold
        intake=json.loads((run/'intake'/f'{role}.json').read_text())
        sessions.append({'segment':role,'first_source_ns':intake.get('first_ns'),
            'last_source_ns':max((s['last_ns'] for s in intake.get('streams',[]) if s.get('last_ns') is not None),default=None),
            'events':intake.get('events',0),'group':'one conservatively grouped nearby acquisition; session identity unverified',
            'independent_session_CI':'NOT_SUPPORTED'})
        complete=json.loads((directory/'complete.json').read_text())
        if complete['status']!='PREDICTIONS_COMPLETE':
            failures.append({'segment':role,'fold':fold,'status':'FAILED_STUDY_CELLS','episodes':len(grid)})
            continue
        refs=json.loads((run/'references'/f'{fold}.json').read_text())
        for r in refs: support.append({'segment':role,'fold':fold,'support_type':'reference',**{k:v for k,v in r.items() if k!='row_ids'}})
        for r in json.loads((run/'calibration'/fold/'thresholds.json').read_text()):
            support.append({'segment':role,'fold':fold,'support_type':'calibration',**{k:v for k,v in r.items() if k not in ('calibration_record_ids','calibration_raw_ids')}})
        clean_spec=next(s for s in grid if s['kind']=='clean')
        clean=read_records(directory/clean_spec['episode']/'scores.jsonl.gz')
        clean_index={(r['cloud_id'],r['arm'],r['version']):r for r in clean}
        for spec in grid:
            pred=read_records(directory/spec['episode']/'scores.jsonl.gz')
            e_dir=run/'evaluator'/role/spec['episode']
            attempts=read_records(e_dir/'attempts.jsonl.gz') if (e_dir/'attempts.jsonl.gz').exists() else []
            flow=json.loads((e_dir/'flow.json').read_text()) if (e_dir/'flow.json').exists() else {**spec,'segment':role,'sender':'003','status':'CLEAN_CONTROL'}
            flows.append(flow); sender=flow['sender']
            intervals=method['replay']['schedules_s'].get(spec['schedule'],[])
            joined=join_episode(pred,attempts,spec,intervals,sender)
            prefix_end=intervals[0][0] if intervals else float('inf')
            untouched=[r for r in pred if r['sensor']!=sender or r['time_s']<prefix_end]
            invariant=all(operational_identity(r)==operational_identity(clean_index[(r['cloud_id'],r['arm'],r['version'])]) for r in untouched)
            integrity.append({'segment':role,**spec,'check':'honest_companions_and_pre_intervention_prefix','compared_decisions':len(untouched),'pass':invariant})
            m,c,o=summarize_episode(joined,spec,segment=role,sender=sender,intervals=intervals)
            metrics.extend(m); coverage.extend(c); outcomes.extend(o)
            tr,cs=exposure_and_common_support(joined,spec,role)
            time_rows.extend(tr); common.extend(cs)
            for a in attempts:
                if a['injection_failed'] or not a['reader_valid'] or a.get('failed_rows',0)>0 or (spec['kind']=='attack' and a['realized_changed_rows']==0):
                    failures.append({'segment':role,'fold':fold,**spec,**a})
            for c_row in c:
                if c_row['unknown_alarm']:
                    failures.append({'segment':role,'fold':fold,**spec,'sensor':c_row['sensor'],'arm':c_row['arm'],'version':c_row['version'],
                        'status':'UNKNOWN_ALARM_SUPPORT','count':c_row['unknown_alarm'],'reasons':c_row['unknown_reasons']})
            if spec['kind']=='attack':
                for sensor in method['sensors']:
                    for arm in ARMS:
                        for version in VERSIONS:
                            sample=[r for r in joined if r['sensor']==sensor and r['arm']==arm and r['version']==version and r['scheduled']]
                            for field in ('A','C','score'):
                                diffs=[r[field]-clean_index[(r['cloud_id'],arm,version)][field] for r in sample
                                    if r[field] is not None and clean_index[(r['cloud_id'],arm,version)][field] is not None]
                                paired.append({'segment':role,**spec,'sensor':sensor,'arm':arm,'version':version,'field':field,
                                    'paired_known':len(diffs),'attempts':len(sample),'unknown_pairs':len(sample)-len(diffs),
                                    'mean_attacked_minus_clean':float(np.mean(diffs)) if diffs else None})
        note('offline summaries '+role)
    for name,rows in (('T_R05_metrics',metrics),('T_R05_coverage',coverage),('T_R05_failures',failures),
        ('T_R05_clean_support',support),('T_R05_attempt_flow',flows),('T_R05_episode_outcomes',outcomes),
        ('T_R05_paired_effects',paired),('T_R05_integrity',integrity),('T_R05_sessions',sessions),('T_R05_exposure_time',time_rows),('T_R05_common_support',common),('T_R05_grouped',grouped_rates(metrics))): table(run,name,rows)
    make_figures(run,method,grid)
    failure_gallery(run,coverage,outcomes)
    severity_figures(run,grouped_rates(metrics))
    note('tables and figures exported; notebook execution and gate verification still required')


def exposure_and_common_support(rows,spec,segment):
    groups=defaultdict(list); by_event=defaultdict(list)
    for r in rows:
        groups[(r['sensor'],r['arm'],r['version'])].append(r)
        by_event[(r['sensor'],r['cloud_id'])].append(r)
    time_rows=[]
    for (sensor,arm,version),sample in groups.items():
        sample=sorted(sample,key=lambda r:r['time_s']); eligible=0.; attempted=0.
        onsets=0; quiet=None; previous=None
        for r in sample:
            if previous is not None:
                dt=r['time_s']-previous['time_s']; attempted+=dt
                if dt<=.5 and r['alarm'] is not None and previous['alarm'] is not None and not r['reset']: eligible+=dt
            contiguous=previous is not None and r['time_s']-previous['time_s']<=.5 and not r['reset']
            if not contiguous or r['alarm'] is None: quiet=None
            if r['alarm'] is False:
                if quiet is None: quiet=r['time_s']
            elif r['alarm'] is True:
                if previous is None or (quiet is not None and r['time_s']-quiet>=2): onsets+=1
                quiet=None
            previous=r
        time_rows.append({'segment':segment,**spec,'sensor':sensor,'arm':arm,'version':version,
            'eligible_seconds':eligible,'attempted_seconds':attempted,'unknown_or_gap_seconds':attempted-eligible,
            'alarm_run_onsets':onsets,'runs_per_eligible_minute':onsets*60/eligible if eligible else None,
            'time_rule':'intervals with both endpoints eligible and gap<=0.5 s; no tail extrapolation'})
    by_sensor=defaultdict(list)
    for (sensor,cloud_id),sample in by_event.items(): by_sensor[sensor].append(sample)
    common=[]
    for sensor,events in by_sensor.items():
        shared=[sample for sample in events if len(sample)==12 and all(r['alarm'] is not None for r in sample)]
        for arm in ARMS:
            for version in VERSIONS:
                scores=[r for sample in shared for r in sample if r['arm']==arm and r['version']==version]
                common.append({'segment':segment,**spec,'sensor':sensor,'arm':arm,'version':version,
                    'common_known_events':len(shared),'all_attempt_events':len(events),
                    'alarm_count':sum(r['alarm'] is True for r in scores),
                    'alarm_rate':sum(r['alarm'] is True for r in scores)/len(scores) if scores else None,
                    'support':'intersection of all three methods and four temporal versions; all-attempt coverage separately retained'})
    return time_rows,common


def failure_gallery(run,coverage,outcomes):
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(15,6),layout='constrained')
    reasons=Counter()
    for row in coverage: reasons.update(row['unknown_reasons'])
    top=reasons.most_common(12)
    axes[0].barh([k[:65] for k,v in top],[v for k,v in top]); axes[0].invert_yaxis()
    axes[0].set(title='All-attempt unknown alarm reasons',xlabel='event × method × temporal attempts')
    statuses=Counter(r['delay']['status'] for r in outcomes)
    axes[1].barh(list(statuses),list(statuses.values())); axes[1].set(title='Delay outcomes; no censoring dropped',xlabel='episode intervals × methods × temporal versions')
    fig.suptitle('Failure / censoring gallery. Repeated variants are not independent scene samples.')
    figure_export(fig,run,'F_R05_failures'); plt.close(fig)


def finalize_run(root,run,note):
    """Validate complete artifacts, fresh notebooks, source and input immutability."""
    import os, sys, subprocess, resource, shutil
    import nbformat
    from nbclient import NotebookClient
    from valid_point.evaluation.real import verify_freeze
    verify_freeze(root)
    seal=json.loads((run/'prediction_seal.json').read_text()); require_prediction_seal(run/'predictions',seal)
    method=json.loads((run/'protocol.json').read_text())['method']; grid=episode_grid(method)
    checks=[]
    with (run/'T_R05_integrity.csv').open() as f: integrity=list(csv.DictReader(f))
    checks.append({'check':'all_real_prefixes_and_honest_companion_predictions','pass':all(r['pass']=='True' for r in integrity),'episodes':len(integrity)})
    roles=json.loads((run/'protocol.json').read_text())['roles']
    for entry in roles['comparison']:
        archive=root/'data/mixed_signals'/roles['revision']/'archives'/entry['archive']
        checks.append({'check':entry['id']+'_archive_still_pinned','pass':digest(archive)==entry['published_lfs_sha256']})
    for role in ('C0','C1','C2','C3'):
        fold='F'+role[-1]; directory=run/'predictions'/fold
        actual={p.name for p in directory.iterdir() if p.is_dir()}
        checks.append({'check':role+'_complete_grid','pass':actual=={s['episode'] for s in grid},'observed':len(actual),'expected':62})
        hashes=json.loads((run/'intake'/f'{role}_file_hashes.json').read_text())
        unchanged=all(digest(root/r['path'])==r['sha256'] for r in hashes)
        checks.append({'check':role+'_all_source_files_unchanged','pass':unchanged,'files':len(hashes)})
        for spec in grid:
            raw_path=directory/spec['episode']/'raw.jsonl.gz'
            if not raw_path.exists(): continue
            raw=read_records(raw_path)
            streams=Counter(r['stream'] for r in raw)
            checks.append({'check':role+'_'+spec['episode']+'_companions','pass':set(streams)==set(method['sensors']),'counts':dict(streams)})
    rerun=list((run/'evaluator/C0').glob('*/deterministic_rerun.json'))
    checks.append({'check':'bounded_actual_deterministic_rerun','pass':bool(rerun) and all(all(json.loads(p.read_text())[k] for k in ('raw_prefix_equal','regenerated_PCD_hash_equal')) for p in rerun)})
    test=subprocess.run([sys.executable,'-m','pytest','-q','tests','--junitxml='+str(run/'test_results_final.xml')],
        cwd=root,env={**os.environ,'PYTHONPATH':str(root/'src')},capture_output=True,text=True)
    (run/'test_final.log').write_text(test.stdout+test.stderr)
    checks.append({'check':'full_tests','pass':test.returncode==0})
    write_json(run/'technical_validation.json',checks)
    (run/'gate.md').write_text('# GR5 — R05 comparison disposition\n\n'
        'Technical checks: '+('PASS' if all(c['pass'] for c in checks) else 'INCOMPLETE / FAILED CHECKS')+'. '
        'Fresh notebook execution is recorded in notebook_execution.json and required for final completion.\n\n'
        'Scientific interpretation: descriptive frozen four-segment replay only. Nulls, no-power calibration, '
        'false alarms and adverse effects are retained. Target alpha=1% is not a achieved-FPR guarantee. '
        'Sessions are not verified independent and fold fits share training data; no between-session confidence interval. '
        'Ideal receipt and causal availability of recorded odometry are modeled assumptions. '
        'H/mini_14 remains unopened. Stop at R05; no next stage or publication promise.\n')
    kernel_dir=run/'jupyter/kernels/r05'
    write_json(kernel_dir/'kernel.json',{'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'R05 frozen environment','language':'python'})
    old_jupyter_path=os.environ.get('JUPYTER_PATH','')
    os.environ['JUPYTER_PATH']=str(run/'jupyter')+(os.pathsep+old_jupyter_path if old_jupyter_path else '')
    notebooks=[]
    for segment in ('C0','C1','C2','C3',None):
        name='R05_grouped_evaluation' if segment is None else 'R05_segment_timelines'
        nb=nbformat.read(root/'notebooks'/f'{name}.ipynb',as_version=4)
        os.environ['VP_RUN_DIR']=str(run)
        if segment: os.environ['VP_SEGMENT']=segment
        status='PASS'; error=None
        try:
            NotebookClient(nb,timeout=600,kernel_name='r05',resources={'metadata':{'path':str(root)}}).execute()
        except Exception as exc: status='FAIL'; error=repr(exc)
        dest=run/(name+('' if segment is None else '_'+segment)+'.executed.ipynb')
        nbformat.write(nb,dest)
        notebooks.append({'path':dest.name,'segment':segment,'status':status,'error':error})
        note('fresh notebook '+dest.name+' '+status)
    if old_jupyter_path: os.environ['JUPYTER_PATH']=old_jupyter_path
    else: os.environ.pop('JUPYTER_PATH',None)
    write_json(run/'notebook_execution.json',notebooks)
    status='PASS' if all(c['pass'] for c in checks) and all(n['status']=='PASS' for n in notebooks) else 'INCOMPLETE'
    # Preserve the pre-notebook gate as part of execution history.
    shutil.copyfile(run/'gate.md',run/'gate_before_notebooks.md')
    with (run/'gate.md').open('a') as f: f.write('\nFinal GR5 technical status: **'+status+'**. See technical_validation.json and notebook_execution.json.\n')
    require_prediction_seal(run/'predictions',seal)
    write_json(run/'environment_final.json',{'python':sys.version,'numpy':np.__version__,
        'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'free_disk_bytes':shutil.disk_usage(run).free,
        'run_bytes':sum(p.stat().st_size for p in run.rglob('*') if p.is_file())})
    write_json(run/'manifest.json',{'stage':'R05','run':run.name,'technical_status':status,'H_opened':False,
        'freeze_sha256':json.loads((run/'protocol.json').read_text())['freeze_sha256'],
        'sealed_utc':datetime.now(timezone.utc).isoformat(),
        'prediction_implementation_snapshots':[str(p.relative_to(run)) for p in sorted(run.glob('implementation_predict_*'))],
        'source_sha256':{str(p.relative_to(root)):digest(p) for p in [*root.glob('src/valid_point/**/*.py'),root/'scripts/evaluate_replay.py',root/'tests/test_evaluation.py']},
        'output_sha256':{str(p.relative_to(run)):digest(p) for p in run.rglob('*') if p.is_file() and p.name!='manifest.json'}})


def final_recovery(sample, intervals):
    """Recovery after the LAST intervention, even when only an earlier burst alarmed."""
    last=intervals[-1][1]
    alarmed=any(r['alarm'] is True and r['reader_valid'] and r['realized_changed_rows']>0
        and not r['injection_failed'] and any(a<=r['time_s']<b for a,b in intervals) for r in sample)
    if not alarmed: return {'value_s':None,'status':'NOT_APPLICABLE_NEVER_ALARMED','last_offset_s':last}
    start=None; previous=None; interrupted=False
    for r in sorted((r for r in sample if r['time_s']>=last),key=lambda r:r['time_s']):
        valid=r['alarm'] is False and not r.get('reset',False)
        gap=previous is not None and r['time_s']-previous>.5
        if not valid or gap:
            start=None; interrupted|=r['alarm'] is None or r.get('reset',False) or gap
        if valid and start is None: start=r['time_s']
        if start is not None and r['time_s']-start>=2:
            return {'value_s':r['time_s']-last,'status':'RECOVERED','last_offset_s':last}
        previous=r['time_s'] if valid else None
    return {'value_s':None,'status':'UNDEFINED_INTERRUPTED_SUPPORT' if interrupted else 'RIGHT_CENSORED_NO_PERSISTENCE','last_offset_s':last}


def severity_figures(run,grouped):
    import matplotlib.pyplot as plt
    families=('random_removal','localized_removal','displacement','rearrangement','addition')
    fig,axes=plt.subplots(5,2,figsize=(14,19),layout='constrained')
    for i,family in enumerate(families):
        for j,schedule in enumerate(('sustained','burst')):
            ax=axes[i,j]
            for arm in ARMS:
                for version in ('memoryless','EWMA'):
                    sample=sorted((r for r in grouped if r['sensor']=='003' and r['family']==family and r['schedule']==schedule
                        and r['arm']==arm and r['version']==version and r['metric']=='all_attempt_recall'),key=lambda r:r['severity'])
                    ax.plot([r['severity'] for r in sample],[np.nan if r['macro'] is None else r['macro'] for r in sample],
                        marker='o',linestyle='-' if version=='memoryless' else '--',label=arm+' '+version)
            ax.set(title=family+' / '+schedule,ylabel='macro all-attempt event recall',xlabel='severity (m)' if family in ('displacement','rearrangement') else 'severity (fraction)',ylim=(-.03,1.03)); ax.grid(alpha=.2)
            if i==0: ax.legend(fontsize=7)
    fig.suptitle('Frozen severity grid; failed injections and abstentions remain undetected attempts\nEqual-weight segment macro; full micro denominators and omissions in T_R05_grouped')
    figure_export(fig,run,'F_R05_severity'); plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(17,6),layout='constrained')
    for arm in ARMS:
        for version in ('memoryless','EWMA'):
            values=[]
            sensors=('003','004','laser','top','dome')
            for sensor in sensors:
                r=next((r for r in grouped if r['sensor']==sensor and r['kind']=='clean' and r['arm']==arm and r['version']==version and r['metric']=='eligible_fpr'),None)
                values.append(np.nan if r is None or r['macro'] is None else r['macro'])
            axes[0].plot(sensors,values,'o-',label=arm+' '+version)
    axes[0].set(title='Achieved clean eligible false-alarm rate',ylabel='macro FPR'); axes[0].axhline(.01,ls=':',color='black',label='target only'); axes[0].legend(fontsize=7)
    stresses=sorted({(r['family'],r['severity']) for r in grouped if r['kind']=='benign'})
    for arm in ARMS:
        for version in ('memoryless','EWMA'):
            values=[]
            for family,severity in stresses:
                rates=[r['macro'] for r in grouped if r['sensor']=='003' and r['family']==family and r['severity']==severity and r['arm']==arm and r['version']==version and r['metric']=='eligible_fpr' and r['macro'] is not None]
                values.append(float(np.mean(rates)) if rates else np.nan)
            axes[1].plot(range(len(stresses)),values,'o-',label=arm+' '+version)
    axes[1].set_xticks(range(len(stresses)),[f'{f.replace("assumed_adapter_", "").replace("modeled_source_", "")} {s:g}' for f,s in stresses],rotation=75,ha='right',fontsize=7)
    axes[1].set(title='003 benign stress FPR; equal schedule/segment means',ylabel='macro FPR')
    for ax in axes: ax.set_ylim(-.03,1.03); ax.grid(alpha=.2)
    fig.suptitle('Separately calibrated arms; unavailable thresholds yield gaps, not zero false alarms')
    figure_export(fig,run,'F_R05_false_alarms'); plt.close(fig)


def operational_identity(row):
    """Exclude opaque episode identity when comparing matched operational traces."""
    row=dict(row); row.pop('episode',None)
    if row.get('state') is not None:
        row['state']=dict(row['state']); row['state'].pop('episode',None)
    return row
