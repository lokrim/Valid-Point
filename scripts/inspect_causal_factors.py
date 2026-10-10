"""Execute R02 only on the already extracted, bounded mini_7 window."""
from __future__ import annotations
import csv
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
import time
from collections import Counter
from dataclasses import asdict

ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/mpl-valid-point')
sys.path.insert(0,str(ROOT/'src'))
from valid_point.replay import AllowedSource,ReplayConfig
from valid_point.operational import measure_operational


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def save_table(run,name,rows):
    rows=list(rows)
    keys=list(dict.fromkeys(k for row in rows for k in row))
    path=run/(name+'.csv')
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,keys); w.writeheader(); w.writerows(rows)
    md=run/(name+'.md')
    with md.open('w') as f:
        f.write('| '+' | '.join(keys)+' |\n| '+' | '.join('---' for _ in keys)+' |\n')
        for row in rows:
            f.write('| '+' | '.join(str(row.get(k,'' )).replace('|','/').replace('\n',' ') for k in keys)+' |\n')
    return path


def isolation_check(events,raw,poses,config,run):
    from unittest.mock import patch
    from valid_point.replay import AllowedSource
    forbidden=run/'evaluator_fixture'; forbidden.mkdir(exist_ok=True)
    names=('labels.txt','boxes.json','masks.bin','schedules.json','clean_counterparts.pcd','outcomes.json')
    for name in names: (forbidden/name).write_text('version 1')
    original_read=Path.read_bytes; original_open=Path.open
    def guard_read(path,*a,**kw):
        if forbidden in path.parents: raise AssertionError('forbidden evaluator read')
        return original_read(path,*a,**kw)
    def guard_open(path,*a,**kw):
        mode=kw.get('mode',a[0] if a else 'r')
        if forbidden in path.parents and not str(mode).startswith(('w','a','x')):
            raise AssertionError('forbidden evaluator read')
        return original_open(path,*a,**kw)
    with patch.object(Path,'read_bytes',guard_read),patch.object(Path,'open',guard_open):
        first_source=AllowedSource(raw/'PointClouds/mini_7',raw/'Odometry/mini_7')
        first=measure_operational(events,first_source,config=config)
        for name in names: (forbidden/name).write_text('version 2')
        second_source=AllowedSource(raw/'PointClouds/mini_7',raw/'Odometry/mini_7')
        second=measure_operational(events,second_source,config=config)
        same=[x.as_dict() for x in first]==[x.as_dict() for x in second]
        same_log=first_source.access_log==second_source.access_log
        trapped=False
        try: (forbidden/'labels.txt').read_bytes()
        except AssertionError: trapped=True
    return {'events':len(events),'operational_output_identical':same,'access_log_identical':same_log,
            'positive_control_trapped':trapped,'allowed_input_sha256_identical':
            [x.raw.input_sha256 for x in first]==[x.raw.input_sha256 for x in second],
            'forbidden_categories':list(names),'access_log':first_source.access_log}


def figures(run,rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    streams=sorted({r['stream'] for r in rows})
    t0=min(r['source_ns'] for r in rows)
    fig,axes=plt.subplots(2,1,figsize=(11,7),sharex=True)
    for stream in streams:
        rs=[r for r in rows if r['stream']==stream]
        x=[(r['source_ns']-t0)/1e9 for r in rs]
        axes[0].plot(x,[r['inside_points'] if r['inside_points'] is not None else float('nan') for r in rs],label=stream)
        axes[1].plot(x,[r['G_m'] if r['G_m'] is not None else float('nan') for r in rs],label=stream,marker='.',markersize=2)
    axes[0].set_ylabel('D crop count (points/frame)')
    axes[1].set_ylabel('G directed q90 (m)')
    axes[1].set_xlabel('source elapsed time (s)')
    axes[0].legend(ncol=5); axes[1].legend(ncol=5)
    axes[0].grid(alpha=.2); axes[1].grid(alpha=.2)
    fig.suptitle('R02 mini_7 raw factors; gaps are unknown, no reference or score')
    fig.tight_layout()
    for ext in ('png','svg','pdf'): fig.savefig(run/f'F_R02_raw_timelines.{ext}',dpi=160)
    plt.close(fig)
    fig,axes=plt.subplots(2,1,figsize=(11,6),sharex=True)
    for stream in streams:
        rs=[r for r in rows if r['stream']==stream]
        axes[0].scatter([r['sync_id'] for r in rs],[(r['source_ns']-t0)/1e9 for r in rs],s=5,label=stream)
        axes[1].plot([r['sync_id'] for r in rs],[r['pose_age_s'] for r in rs],label=stream,marker='.',markersize=2)
    axes[0].set_ylabel('source elapsed time (s)')
    axes[1].set_ylabel('selected pose age (s)')
    axes[1].set_xlabel('sync index (association only)')
    axes[0].legend(ncol=5); axes[1].legend(ncol=5)
    axes[0].grid(alpha=.2); axes[1].grid(alpha=.2)
    fig.suptitle('R02 source alignment and causal pose age; sync index is not time')
    fig.tight_layout()
    for ext in ('png','svg','pdf'): fig.savefig(run/f'F_R02_alignment.{ext}',dpi=160)
    plt.close(fig)


def overlap_diagnostic(source,events,poses,run):
    """Bounded potential-overlap diagnostic; no visibility or scoring claim."""
    import numpy as np
    by_key={(e.stream,e.sync_id):e for e in events}
    top_events=sorted((e for e in events if e.stream=='top'),key=lambda e:e.source_ns)
    rows=[]
    # The published map->top inverse puts the top origin at negative map XY.
    center=np.array([-41.551,-51.878])
    for sync in (0,16,32,49):
        def cells(xyz):
            xyz=xyz[np.hypot(xyz[:,0]-center[0],xyz[:,1]-center[1])<80]
            return {tuple(x) for x in np.floor(xyz).astype(np.int32)}
        for stream in ('003','004','laser'):
            peer=by_key.get((stream,sync))
            if peer is None: continue
            available_top=[e for e in top_events if e.source_ns<=peer.deadline_ns and e.arrival_ns<=peer.deadline_ns]
            top=max(available_top,key=lambda e:e.source_ns) if available_top else None
            if top is None:
                rows.append({'sync_id':sync,'peer':stream,'top_id':None,'peer_id':peer.cloud_id,
                             'skew_s':None,'voxel_jaccard':None,'reason':'NO_CAUSAL_TOP'})
                continue
            top_xyz,_=source.read_cloud(top)
            top_cells=cells(top_xyz)
            eligible=[p for p in poses[stream] if p.source_ns<=peer.source_ns and p.available_ns<=peer.deadline_ns and p.valid]
            if not eligible:
                rows.append({'sync_id':sync,'peer':stream,'top_id':top.cloud_id,'peer_id':peer.cloud_id,
                             'skew_s':abs(top.source_ns-peer.source_ns)/1e9,'voxel_jaccard':None,
                             'crop':'map XY within 80 m of top origin (-41.551,-51.878); all heights',
                             'voxel_m':1.0,'reason':'NO_CAUSAL_POSE'})
                continue
            pose=max(eligible,key=lambda p:p.source_ns)
            xyz,_=source.read_cloud(peer)
            xyz=xyz@pose.matrix[:3,:3].T+pose.matrix[:3,3]
            peer_cells=cells(xyz)
            union=len(top_cells|peer_cells)
            rows.append({'sync_id':sync,'top_sync_id':top.sync_id,'peer':stream,'top_id':top.cloud_id,'peer_id':peer.cloud_id,
                         'skew_s':abs(top.source_ns-peer.source_ns)/1e9,
                         'voxel_jaccard':len(top_cells&peer_cells)/union if union else None,
                         'top_voxels':len(top_cells),'peer_voxels':len(peer_cells),
                         'pose_id':pose.pose_id,
                         'crop':'map XY within 80 m of top origin (-41.551,-51.878); all heights',
                         'voxel_m':1.0,'reason':'POTENTIAL_OVERLAP_ONLY'})
    save_table(run,'T_R02_overlap_diagnostic',rows)
    return rows


def main():
    cfg=json.loads((ROOT/'configs/causal_factors.json').read_text())
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run=ROOT/'artifacts'/(stamp+'-R02')
    run.mkdir(parents=True,exist_ok=False)
    try:
        (run/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
        raw=ROOT/'data/mixed_signals'/cfg['revision']/'raw'
        source=AllowedSource(raw/'PointClouds/mini_7',raw/'Odometry/mini_7')
        events=source.events(max_sync_id=cfg['max_sync_id'],first_seconds=cfg['first_seconds'])
        poses={s:source.read_poses(s) for s in ('003','004','laser')}
        rcfg=ReplayConfig(max_pose_age_ns=cfg['max_pose_age_ns'],max_cloud_age_ns=cfg['max_cloud_age_ns'],
                          max_gap_s=cfg['max_gap_s'],min_voxels=cfg['min_voxels'])
        t0=time.process_time(); w0=time.monotonic()
        records=measure_operational(events,source,config=rcfg,poses=poses)
        cpu=time.process_time()-t0; wall=time.monotonic()-w0
        input_rows=[]; eligibility=[]; timeline=[]
        for rec in records:
            r=rec.raw
            input_rows.append({'cloud_id':r.cloud_id,'stream':r.stream,'principal':r.principal,
                'sync_id':r.sync_id,'source_ns':r.source_ns,'arrival_ns':r.arrival_ns,
                'deadline_ns':r.deadline_ns,'input_sha256':r.input_sha256,'pose_id':r.pose_id,
                'history_id':r.history_id,'history_pose_id':r.history_pose_id})
            eligibility.append({'cloud_id':r.cloud_id,'stream':r.stream,'reason':r.reason,
                'D_status':r.density.status,'D_reason':r.density.reason,
                'G_status':r.geometry.status,'G_reason':r.geometry.reason,
                'pose_age_s':r.pose_age_s,'gap_s':r.geometry.gap_s,
                'current_voxels':r.geometry.current_voxels,'previous_voxels':r.geometry.previous_voxels,
                'downsampled_current':r.geometry.downsampled_current,
                'downsampled_previous':r.geometry.downsampled_previous,'D_reference_status':rec.d_reason})
            timeline.append({'cloud_id':r.cloud_id,'stream':r.stream,'principal':r.principal,
                'sync_id':r.sync_id,'source_ns':r.source_ns,'pose_id':r.pose_id,'pose_age_s':r.pose_age_s,
                'history_id':r.history_id,'inside_points':sum(r.density.counts) if r.density.counts is not None else None,
                'outside_points':r.density.excluded_points,'occupied_cells':r.density.occupied_cells,
                'occupancy_change_signed':sum(r.occupancy_change) if r.occupancy_change is not None else None,
                'D_32_cells_json':json.dumps(r.density.counts),'G_m':r.geometry.distance_m,
                'G_status':r.geometry.status,'G_reason':r.geometry.reason})
        save_table(run,'T_R02_inputs',input_rows)
        save_table(run,'T_R02_eligibility',eligibility)
        save_table(run,'F_R02_raw_timelines',timeline)
        counts=Counter((r.raw.stream,r.raw.density.status,r.raw.geometry.status) for r in records)
        component_rows=[]
        for stream in ('003','004','laser','top','dome'):
            rs=[r.raw for r in records if r.raw.stream==stream]
            component_rows.append({'stream':stream,'principal':rs[0].principal if rs else None,
                'events':len(rs),'D_known':sum(x.density.status=='known' for x in rs),
                'G_known':sum(x.geometry.status=='known' for x in rs),
                'G_unknown_reasons':json.dumps(dict(Counter(x.geometry.reason for x in rs if x.geometry.status!='known'))),
                'K':'excluded: measured velocity provenance unresolved',
                'X':'bounded overlap/skew diagnostic only; no visibility support',
                'intensity':'excluded: calibration unverified',
                'D_reference':'not fit: one development segment'})
        save_table(run,'T_R02_components',component_rows)
        figures(run,timeline)
        overlap=overlap_diagnostic(source,events,poses,run)
        isolation=isolation_check(events[:10],raw,poses,rcfg,run)
        (run/'boundary_isolation.json').write_text(json.dumps(isolation,indent=2)+'\n')
        test=subprocess.run([str(ROOT/'.venv/bin/python'),'-m','pytest','-q','tests','--junitxml='+str(run/'test_results.xml')],
            cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT/'src')},capture_output=True,text=True)
        (run/'test.log').write_text(test.stdout+test.stderr)
        env={'python':sys.version,'platform':sys.platform,'numpy':__import__('numpy').__version__,
             'cpu_s':cpu,'wall_s':wall,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
             'events':len(records),'accessed_files':len(source.access_log)}
        (run/'environment.json').write_text(json.dumps(env,indent=2)+'\n')
        (run/'access.log').write_text('\n'.join(source.access_log)+'\n')
        # Notebook is executed by this stage runner in a fresh kernel.
        import nbformat
        from nbclient import NotebookClient
        nb=nbformat.read(ROOT/'notebooks/R02_causal_factors.ipynb',as_version=4)
        nb.metadata.setdefault('kernelspec',{'display_name':'Python 3','language':'python','name':'python3'})
        notebook_error=None
        try:
            os.environ['VP_RUN_DIR']=str(run)
            nb=NotebookClient(nb,timeout=900,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
        except Exception as exc:
            notebook_error=repr(exc)
        nbformat.write(nb,run/'R02_causal_factors.executed.ipynb')
        if notebook_error: (run/'notebook_error.txt').write_text(notebook_error)
        status='PASS' if test.returncode==0 and notebook_error is None and all((isolation[k] for k in ('operational_output_identical','access_log_identical','positive_control_trapped','allowed_input_sha256_identical'))) and all(r['D_known']==r['events'] for r in component_rows) else 'BLOCKED'
        source_files=[ROOT/'src/valid_point/replay.py',ROOT/'src/valid_point/operational.py',
                      ROOT/'src/valid_point/evidence/density.py',ROOT/'src/valid_point/evidence/temporal_geometry.py',
                      ROOT/'src/valid_point/io/mixed_signals.py',ROOT/'scripts/inspect_causal_factors.py',
                      ROOT/'notebooks/R02_causal_factors.ipynb',ROOT/'configs/causal_factors.json']
        (run/'gate.md').write_text(f'# GR2 — causal raw factor gate\n\nTechnical status: **{status}**. {len(records)} events, CPU {cpu:.2f} s, wall {wall:.2f} s, peak RSS {env["peak_rss_bytes"]} bytes.\n\nD coverage: '+', '.join(f'{x["stream"]} {x["D_known"]}/{x["events"]}' for x in component_rows)+'; G coverage: '+', '.join(f'{x["stream"]} {x["G_known"]}/{x["events"]}' for x in component_rows)+f'. Bounded cross-agent overlap/skew diagnostic: {len(overlap)} pairs.\n\nNo references, calibration, score, interventions or comparison data. Proposed freeze: D-only all five streams; G-only and max(D,G) conditional on valid causal geometry. X bounded diagnostic; K and intensity excluded. mini_7 is one contiguous development segment, not independent scenes.\n\nSee manifest, full tables, figures, executed notebook, isolation check, test log and JUnit in this run.\n')
        manifest={'run_id':run.name,'stage':'R02','status':status,'source_sha256':{str(p.relative_to(ROOT)):digest(p) for p in source_files},
                  'input_sha256':{row['cloud_id']:row['input_sha256'] for row in input_rows},
                  'pose_csv_sha256':{s:digest(raw/'Odometry/mini_7'/f'odometry_{s}.csv') for s in ('003','004','laser')},
                  'archive_sha256':cfg['archive_sha256'],'revision':cfg['revision'],'license':'CC BY-NC-SA 4.0',
                  'split_lineage':cfg['split_lineage'],'reference_id':None,'calibration_id':None,
                  'git_head':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True).stdout.strip(),
                  'git_dirty':subprocess.run(['git','status','--short'],cwd=ROOT,capture_output=True,text=True).stdout,
                  'output_sha256':{str(p.relative_to(run)):digest(p) for p in run.rglob('*') if p.is_file() and p.name!='manifest.json'}}
        (run/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        print(run)
        print((run/'gate.md').read_text())
    except Exception as exc:
        (run/'failure.txt').write_text(repr(exc)+'\n')
        raise

if __name__=='__main__': main()
