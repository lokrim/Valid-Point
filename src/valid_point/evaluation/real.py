"""R05 local-only orchestration primitives and fold-specific operational scoring.

No acquisition or extraction is implemented. Evaluator metadata is never an
argument to normalize/score; the caller owns clean split selection and joins.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from hashlib import sha256
import gzip
import json
from math import ceil
from pathlib import Path
import numpy as np

from valid_point.development_scores import NormalizedFactors, decide, _gap_context
from valid_point.evaluation.splits import canonical_hash, validate_roles
from valid_point.evidence.density import CELL_IDS, DensityRaw
from valid_point.evidence.temporal_geometry import GeometryRaw
from valid_point.replay import RawFactorRecord
from valid_point.temporal import TemporalEWMA

FREEZE = '80694538e8549256934b3a314301cc8ca821efe0bf36ff4071eab9681f2c039c'
ARMS = ('D-only', 'G-only', 'max(D,G)')
VERSIONS = {'memoryless': None, 'EWMA': 1., 'EWMA_tau_0.25': .25, 'EWMA_tau_2': 2.}


def digest(path: Path) -> str:
    h = sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4*1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n')


def write_records(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as f, gzip.GzipFile(fileobj=f, mode='wb', mtime=0, filename='') as z:
        for row in rows:
            z.write((json.dumps(row, sort_keys=True, allow_nan=False)+'\n').encode())


def read_records(path: Path) -> list[dict]:
    with gzip.open(path, 'rt') as f:
        return [json.loads(line) for line in f]


def raw_from_dict(row: dict) -> RawFactorRecord:
    row = dict(row)
    row['density'] = DensityRaw(**row['density'])
    row['geometry'] = GeometryRaw(**row['geometry'])
    return RawFactorRecord(**row)


def verify_freeze(root: Path) -> dict:
    frozen = root/'artifacts/20261010T211551Z-R04-80694538e854'
    payload = json.loads((frozen/'freeze_payload.json').read_text())
    actual = canonical_hash(payload)
    sources = [{'path': p, 'expected': h, 'actual': digest(root/p)}
               for p, h in payload['source_sha256'].items()]
    manifest = json.loads((frozen/'manifest.json').read_text())
    outputs = [{'path': p, 'expected': h, 'actual': digest(frozen/p)}
               for p, h in manifest['output_sha256'].items()]
    if actual != FREEZE or any(r['expected'] != r['actual'] for r in sources+outputs):
        raise ValueError('FROZEN_HASH_MISMATCH: amendment required before outcomes')
    validate_roles(payload['roles'])
    return {'freeze_sha256': actual, 'sources': sources, 'GR4_outputs': outputs}


def local_inventory(root: Path, roles: dict) -> dict:
    """Stat only authorized explicit paths; never traverse final H directories."""
    data = root/'data/mixed_signals'/roles['revision']
    rows, partials = [], []
    for entry in [roles['development'], *roles['comparison']]:
        archive = data/'archives'/entry['archive']
        partial = archive.with_suffix('.tar.partial')
        if partial.exists():
            partials.append({'path': str(partial), 'bytes': partial.stat().st_size,
                             'disposition': 'REDUNDANT_DUPLICATE_DO_NOT_RESUME'})
        rows.append({'role': entry['id'], 'path': str(archive),
                     'bytes': archive.stat().st_size if archive.exists() else None,
                     'expected_bytes': entry['bytes']})
        for kind in ('PointClouds', 'Odometry'):
            directory = data/'raw'/kind/entry['segment']
            files = sorted(p for p in directory.iterdir() if p.is_file()) if directory.exists() else []
            rows.append({'role': entry['id'], 'path': str(directory),
                         'files': len(files), 'bytes': sum(p.stat().st_size for p in files)})
    return {'files': rows, 'redundant_partials': partials, 'H_opened': False}


def require_prediction_seal(directory: Path, seal: dict) -> None:
    expected = seal['files']
    if not all(f'{fold}/complete.json' in expected for fold in ('F0','F1','F2','F3')):
        raise ValueError('MISSING_FOLD_COMPLETION')
    actual = {str(p.relative_to(directory)): digest(p) for p in directory.rglob('*') if p.is_file()}
    if actual != expected or seal.get('folds') != ['F0','F1','F2','F3']:
        raise ValueError('INCOMPLETE_OR_CHANGED_PREDICTION_SEAL')


@dataclass(frozen=True)
class Reference:
    sensor: str
    factor: str
    context: str
    u: float | None
    b: float | None
    q50: float | None
    observations: int
    distinct_clouds: int
    segments: tuple[str, ...]
    segment_counts: dict
    row_ids: tuple[str, ...]
    status: str
    reference_id: str


def fit_references(records: dict[str, list[RawFactorRecord]], fold) -> dict:
    if set(records) != set(fold.reference):
        raise ValueError('exact frozen reference segments required')
    groups = defaultdict(list)
    for segment, rows in records.items():
        seen = set()
        for r in rows:
            key = (r.stream, r.cloud_id)
            if key in seen or not r.input_sha256:
                if key in seen: raise ValueError('duplicate clean raw input')
                continue
            seen.add(key)
            identity = f'{segment}:{r.stream}:{r.cloud_id}:{r.input_sha256}'
            if r.density.counts is not None:
                if len(r.density.counts) != 32: raise ValueError('incomplete D universe')
                for cell, value in zip(CELL_IDS, r.density.counts):
                    for ctx in (cell, 'range:'+cell.split(':')[0]):
                        groups[(r.stream,'D',ctx)].append((segment,identity,float(value)))
            if r.geometry.distance_m is not None:
                for ctx in ('all', _gap_context(r.geometry.gap_s)):
                    if ctx: groups[(r.stream,'G',ctx)].append((segment,identity,r.geometry.distance_m))
    reference_id = canonical_hash({'fold':fold.id, 'raw':{s:[r.as_dict() for r in rows] for s,rows in records.items()}})
    refs = {}
    for sensor in ('003','004','laser','top','dome'):
        for factor, contexts in (('D', (*CELL_IDS, *(f'range:r{i}' for i in range(4)))),
                                 ('G', ('g0','g1','g2','all'))):
            for ctx in contexts:
                values = groups[(sensor,factor,ctx)]
                ids = tuple(sorted({v[1] for v in values}))
                segments = tuple(sorted({v[0] for v in values}))
                counts = {s:len({i for seg,i,_ in values if seg==s}) for s in fold.reference}
                q50,u = map(float,np.quantile([v[2] for v in values],[.5,.95])) if values else (None,None)
                b = None if u is None else 4*(u-q50)
                status = 'LOW_SUPPORT' if len(ids)<200 or len(segments)<2 else 'ZERO_SCALE' if b<=0 else 'SUPPORTED'
                refs[(sensor,factor,ctx)] = Reference(sensor,factor,ctx,u,b,q50,len(values),len(ids),segments,counts,ids,status,reference_id)
    return refs


def normalize(row: RawFactorRecord, refs: dict) -> NormalizedFactors:
    reference_id = next(iter(refs.values())).reference_id
    ds, contexts = [], []
    reason = row.density.reason
    if row.density.counts is not None:
        if len(row.density.counts)!=32: raise ValueError('incomplete D universe')
        for cell, count in zip(CELL_IDS,row.density.counts):
            ref = refs.get((row.stream,'D',cell))
            if ref is None or ref.status!='SUPPORTED': ref=refs.get((row.stream,'D','range:'+cell.split(':')[0]))
            if ref is None or ref.status!='SUPPORTED':
                reason='UNSUPPORTED_CELL:'+cell; break
            ds.append(float(np.clip((count-ref.u)/ref.b,0,1))); contexts.append(ref.context)
        else: reason='VALID'
    d = max(ds) if len(ds)==32 and reason=='VALID' else None
    g, gc, gr = None,None,row.geometry.reason
    if row.geometry.distance_m is not None:
        ref=refs.get((row.stream,'G',_gap_context(row.geometry.gap_s)))
        if ref is None or ref.status!='SUPPORTED': ref=refs.get((row.stream,'G','all'))
        if ref is None or ref.status!='SUPPORTED': gr='UNSUPPORTED_G_REFERENCE'
        else:
            g=float(np.clip((row.geometry.distance_m-ref.u)/ref.b,0,1)); gc=ref.context; gr='VALID'
    return NormalizedFactors(row.cloud_id,row.stream,row.source_ns,d,g,reason,gr,tuple(contexts),gc,reference_id)


def score_records(records, refs: dict, *, episode: str, first_ns: int, thresholds=None):
    """Typed raw-only path: no evaluator inputs or filesystem access."""
    states={v:TemporalEWMA(tau) for v,tau in VERSIONS.items() if tau is not None}
    rows=[]
    for raw in records:
        normalized=normalize(raw,refs)
        for arm in ARMS:
            inst=decide(raw,normalized,arm)
            for version,tau in VERSIONS.items():
                state=None if tau is None else states[version].update(episode=episode,principal=raw.principal,
                    sensor=raw.stream,method_arm=arm,reference_version=inst.reference_id,
                    source_ns=raw.source_ns,A=inst.A,reason=inst.reason)
                score=inst.A if state is None else state.Z if state.ready else None
                threshold=None if thresholds is None else thresholds[(raw.stream,arm,version)]
                c=None if threshold is None else threshold['threshold']
                why=(inst.reason if inst.A is None else 'VALID') if state is None else state.reason
                if score is not None and c is None: why='UNAVAILABLE_CALIBRATION'
                rows.append({'episode':episode,'cloud_id':raw.cloud_id,'sensor':raw.stream,'principal':raw.principal,
                    'source_ns':raw.source_ns,'time_s':(raw.source_ns-first_ns)/1e9,'cloud_sha256':raw.input_sha256,
                    'raw_record_id':canonical_hash(raw.as_dict()),'arm':arm,'version':version,
                    'normalized':normalized.as_dict(),'A':inst.A,'C':inst.C,
                    'state':None if state is None else state.as_dict(), 'score':score,
                    'threshold':c,'threshold_id':None if threshold is None else threshold['threshold_id'],
                    'alarm':None if c is None or score is None else bool(score>c),'reason':why,
                    'reference_id':inst.reference_id})
    return rows,{v:s.checkpoint() for v,s in states.items()}


def calibrate(rows: list[dict], fold, refs: dict) -> dict:
    result={}
    for sensor in ('003','004','laser','top','dome'):
        for arm in ARMS:
            for version in VERSIONS:
                sample=[r for r in rows if (r['sensor'],r['arm'],r['version'])==(sensor,arm,version)]
                values=sorted(r['score'] for r in sample if r['score'] is not None)
                n=len(values); k=ceil((n+1)*.99)
                c=None if n<200 else 1. if k>n else values[k-1]
                lineage={'fold':fold.id,'sensor':sensor,'arm':arm,'version':version,
                    'reference_segments':list(fold.reference),'calibration_segment':fold.calibration,'test_segment':fold.test,
                    'reference_id':next(iter(refs.values())).reference_id,
                    'calibration_raw_ids':[r['raw_record_id'] for r in sample],
                    'calibration_record_ids':[canonical_hash(r) for r in sample]}
                result[(sensor,arm,version)]={**lineage,'threshold_id':canonical_hash(lineage),
                    'threshold':c,'known':n,'attempts':len(sample),'order_index':k,
                    'status':'INSUFFICIENT_KNOWN' if c is None else 'NO_POWER' if c>=1 or len(set(values))==1 else 'AVAILABLE'}
    return result


def episode_grid(method: dict) -> list[dict]:
    aliases={'displacement_m':'displacement','rearrangement_m':'rearrangement','addition_fraction':'addition'}
    specs=[{'kind':'clean','family':'clean','severity':0.,'schedule':'none'}]
    for family,severities in method['replay']['families'].items():
        family=aliases.get(family,family)
        specs.append({'kind':'identity','family':family,'severity':0.,'schedule':'sustained'})
        for severity in severities:
            for schedule in ('sustained','burst'):
                specs.append({'kind':'attack','family':family,'severity':severity,'schedule':schedule})
    for name,values in method['benign'].items():
        if not isinstance(values,list): continue
        for severity in values:
            for schedule in ('sustained','burst'):
                specs.append({'kind':'benign','family':name,'severity':severity,'schedule':schedule})
    for i,spec in enumerate(specs): spec['episode']='e'+canonical_hash([i,spec])[:16]
    return specs


def intake_segment(root: Path, run: Path, roles: dict, entry: dict) -> dict:
    """Read-only pinned archive/extract verification; no label bodies or H."""
    from valid_point.io.mixed_signals import safe_members, read_pcd_header, raw_to_top
    from valid_point.replay import AllowedSource
    if entry not in roles['comparison']: raise ValueError('comparison role only')
    data=root/'data/mixed_signals'/roles['revision']; segment=entry['segment']
    archive=data/'archives'/entry['archive']
    if archive.stat().st_size!=entry['bytes'] or digest(archive)!=entry['published_lfs_sha256']:
        raise ValueError('ARCHIVE_HASH_MISMATCH')
    inventory=safe_members(archive)
    write_json(run/'intake'/f"{entry['id']}_members.json",inventory)
    manifest=json.loads((data/'manifests'/f'{segment}_extracted_files.json').read_text())
    checks=[]
    for item in manifest['files']:
        path=(root/item['path']).resolve()
        allowed=[(data/'raw'/kind/segment).resolve() for kind in ('PointClouds','Odometry')]
        if path.parent not in allowed or path.suffix not in ('.pcd','.csv'):
            raise ValueError('unauthorized extracted manifest path')
        actual=digest(path)
        checks.append({'path':item['path'],'bytes':path.stat().st_size,'sha256':actual,
                       'matches':actual==item['sha256'] and path.stat().st_size==item['bytes']})
    write_json(run/'intake'/f"{entry['id']}_file_hashes.json",checks)
    if not all(c['matches'] for c in checks): raise ValueError('EXTRACT_HASH_MISMATCH')
    source=AllowedSource(data/'raw/PointClouds'/segment,data/'raw/Odometry'/segment)
    events=source.events(first_seconds=25)
    poses={s:source.read_poses(s) for s in ('003','004','laser')}
    schemas=[]
    for sensor in ('003','004','laser','top','dome'):
        sample=[e for e in events if e.stream==sensor]
        times=[e.source_ns for e in sample]; gaps=np.diff(times)/1e9
        headers=set()
        for e in sample:
            with e.path.open('rb') as f: headers.add(str(asdict(read_pcd_header(f))))
        matrix=raw_to_top(sensor, next((p.matrix for p in poses.get(sensor,[]) if p.valid),None))
        schemas.append({'sensor':sensor,'events':len(sample),'first_ns':min(times) if times else None,
            'last_ns':max(times) if times else None,'duplicate_times':len(times)-len(set(times)),
            'gap_s_min':float(gaps.min()) if len(gaps) else None,'gap_s_max':float(gaps.max()) if len(gaps) else None,
            'header_variants':sorted(headers),'valid_poses':sum(p.valid for p in poses.get(sensor,[])),
            'frame_roundtrip_error':None if matrix is None else float(np.max(np.abs(np.linalg.inv(matrix)@matrix-np.eye(4)))),
            'frame_assumption':'frozen published RSU map / vehicle native convention; not independent physical calibration'})
    result={'role':entry['id'],'segment':segment,'archive_sha256':entry['published_lfs_sha256'],
        'inventory_members':len(inventory),'verified_files':len(checks),'events':len(events),
        'first_ns':min(e.source_ns for e in events),'streams':schemas,'labels_read':False,'H_opened':False,
        'clock':'ideal receipt=source; latest past available pose; seconds from earliest event',
        'status':'USABLE' if all(s['events'] and not s['duplicate_times'] for s in schemas) else 'INCOMPLETE_STREAMS'}
    write_json(run/'intake'/f"{entry['id']}.json",result)
    return result


def source_for(root: Path, roles: dict, role: str, extra=None):
    from valid_point.replay import AllowedSource
    entry=next(x for x in roles['comparison'] if x['id']==role)
    data=root/'data/mixed_signals'/roles['revision']/'raw'
    return AllowedSource(data/'PointClouds'/entry['segment'],data/'Odometry'/entry['segment'],extra)


def read_values(path: Path):
    from valid_point.io.mixed_signals import read_pcd
    with path.open('rb') as f: header,values=read_pcd(f)
    return values[:,[header.fields.index(x) for x in ('x','y','z','intensity')]].astype(np.float32)


def replay_episode(root, run, roles, role, spec, method, clean, memo=None):
    """Generator boundary followed by production replay. Only raw records leave it.

    Companion factors are parameter-independent clean caches, checked against
    fresh production reads for every episode. All sender records are recomputed.
    """
    from dataclasses import replace
    import shutil
    from valid_point.attacks.overlays import apply_overlay, seed_key, freeze_target, cell_index
    from valid_point.io.mixed_signals import write_pcd
    from valid_point.replay import replay, PoseEvent
    source=source_for(root,roles,role)
    events=source.events(first_seconds=25)
    first=min(e.source_ns for e in events)
    sender=next((s for s in ('003','004','laser') if any(e.stream==s for e in events)),None)
    if sender is None: raise ValueError('NO_SENDER')
    poses={s:source.read_poses(s) for s in ('003','004','laser')}
    entry=next(x for x in roles['comparison'] if x['id']==role)
    episode=spec['episode']; active=run/'active_derived'
    active.mkdir(exist_ok=False)
    target_path=run/'evaluator'/role/'target.json'
    if not target_path.exists():
        prefix=[(e.cloud_id,read_values(e.path)) for e in events if e.stream==sender and (e.source_ns-first)/1e9<3]
        target=freeze_target(prefix)
        write_json(target_path,asdict(target))
    else:
        from valid_point.attacks.overlays import Target
        target=Target(**json.loads(target_path.read_text()))
    intervals=method['replay']['schedules_s'].get(spec['schedule'],[])
    scheduled=lambda ns:any(a<=(ns-first)/1e9<b for a,b in intervals)
    selected=[]; attempts=[]; geometry=[]
    ledger_dir=run/'evaluator'/role/episode
    ledger_dir.mkdir(parents=True,exist_ok=False)
    index={r.cloud_id:r for r in clean}
    companions=0
    for event in events:
        if event.stream!=sender:
            _,h=source.read_cloud(event)
            if h!=index[event.cloud_id].input_sha256: raise ValueError('COMPANION_HASH_CHANGED')
            companions+=1
            continue
        family=spec['family']; severity=spec['severity']
        affect=scheduled(event.source_ns) and spec['kind']!='clean'
        pose_only=family in ('assumed_adapter_translation_m','assumed_adapter_yaw_deg','modeled_source_clock_skew_ms')
        if not affect or pose_only:
            selected.append(event)
            if affect:
                attempts.append({'cloud_id':event.cloud_id,'reader_valid':True,'realized_changed_rows':0,
                    'injection_failed':False,'status':'MODELED_ALIGNMENT_ONLY','key':None})
            continue
        path=active/event.cloud_id
        original=read_values(event.path)
        key=seed_key(entry['segment'],sender,event.cloud_id,
            family if spec['kind']!='benign' else 'random_removal' if family=='raw_downsampling_fraction' else 'displacement',abs(severity))
        attempt={'cloud_id':event.cloud_id,'base_sha256':index[event.cloud_id].input_sha256,'key':key,
                 'reader_valid':False,'realized_changed_rows':0,'injection_failed':False}
        try:
            if family=='coordinate_noise_sigma_m':
                values=original.copy(); rng=np.random.default_rng(int(key[:16],16))
                values[:,:3]+=rng.normal(0,severity,(len(values),3)).astype('f4')
                ids=np.arange(len(values)); failed=[]; intended=len(values)
            else:
                overlay=apply_overlay(original,family='random_removal' if family=='raw_downsampling_fraction' else family,
                    severity=severity,key=key,target=target)
                values=overlay.values; ids=np.asarray(overlay.changed_ids,dtype=np.int32)
                failed=overlay.failed_ids; intended=overlay.intended_count
                attempt['generator_reason']=overlay.reason
                attempt['selected_rows']=len(overlay.selected_ids)
            write_pcd(path,values)
            reread=read_values(path)
            # Reload must match the intended float32 values, including retained intensity.
            error=float(np.max(np.abs(reread-values))) if reread.shape==values.shape and len(values) else 0.
            if reread.shape!=values.shape or error>1e-6: raise ValueError('ROUNDTRIP_MISMATCH')
            changed=len(ids) if spec['kind']!='identity' else 0
            if family in ('displacement','rearrangement','coordinate_noise_sigma_m'):
                changed=int(np.count_nonzero(np.any(reread!=original,axis=1)))
            before=np.bincount(cell_index(original[:,:3],(0,0))+1,minlength=33)
            after=np.bincount(cell_index(reread[:,:3],(0,0))+1,minlength=33)
            if family=='rearrangement' and not np.array_equal(before,after): raise ValueError('CELL_CONSTRAINT_FAILED')
            np.savez_compressed(ledger_dir/(event.cloud_id+'.npz'),changed_ids=np.asarray(ids,dtype=np.int32),
                failed_ids=np.asarray(failed,dtype=np.int32),
                assigned_additions=values[len(original):] if family=='addition' else np.empty((0,4),dtype='f4'))
            attempt.update(reader_valid=True,realized_changed_rows=changed,derived_sha256=digest(path),
                derived_bytes=path.stat().st_size,intended_rows=intended,failed_rows=len(failed),
                base_points=len(original),realized_points=len(reread),max_roundtrip_error=error,
                changed_cell_count_l1=int(np.abs(before-after).sum()),status='ACCEPTED')
            # Predeclared geometry: first, middle and last scheduled sender cloud.
            geometry.append(event.cloud_id)
            selected.append(replace(event,path=path))
        except (OSError,ValueError,UnicodeError) as exc:
            attempt.update(injection_failed=True,status=type(exc).__name__+':'+str(exc))
            selected.append(replace(event,path=path if path.exists() else None,state='present' if path.exists() else 'absent'))
        attempts.append(attempt)
    # Model alignment uncertainty only in sender poses. Cloud filename/source
    # identity remains honest. Shift the pose association clock, not actual arrival.
    if spec['kind']=='benign' and spec['family'] in ('assumed_adapter_translation_m','assumed_adapter_yaw_deg','modeled_source_clock_skew_ms'):
        poses[sender]=alignment_poses(poses[sender],family=spec['family'],severity=spec['severity'],first_ns=first,intervals=intervals)
    active_source=source_for(root,roles,role,active)
    sender_raw=replay(selected,active_source,poses=poses) if memo is None else memo.replay(selected,active_source,poses)
    if memo is not None:
        write_json(ledger_dir/'raw_memo.json',{'hits_cumulative':memo.hits,'misses_cumulative':memo.misses,'entries':len(memo.rows),'fresh_reader_before_lookup':True})
    attacked={r.cloud_id:r for r in sender_raw}
    raw=[attacked[r.cloud_id] if r.stream==sender else r for r in clean]
    if geometry:
        for position in sorted({0,len(geometry)//2,len(geometry)-1}):
            cloud_id=geometry[position]
            if not (active/cloud_id).exists(): continue
            e=next(e for e in events if e.cloud_id==cloud_id)
            # Deterministic spatial display subsample; full geometry remains regenerable.
            base=read_values(e.path); derived=read_values(active/cloud_id)
            pose=next((p.matrix for p in reversed(poses[sender]) if p.source_ns<=e.source_ns and p.available_ns<=e.deadline_ns and p.valid),None)
            np.savez_compressed(ledger_dir/f'geometry_{position}.npz',
                clean=base[::max(1,len(base)//12000)],derived=derived[::max(1,len(derived)//12000)],
                cloud_id=cloud_id,pose=np.eye(4) if pose is None else pose)
    if role=='C0' and spec['family']=='displacement' and spec['severity']==1. and spec['schedule']=='burst':
        repeated=list(replay(selected[:65],source_for(root,roles,role,active),poses=poses))
        invariant=[r.as_dict() for r in repeated]==[r.as_dict() for r in sender_raw[:65]]
        first_changed=next(a for a in attempts if a.get('derived_sha256'))
        event=next(e for e in events if e.cloud_id==first_changed['cloud_id'])
        original=read_values(event.path)
        regenerated=apply_overlay(original,family='displacement',severity=1.,key=first_changed['key'],target=target)
        check=ledger_dir/'bounded_rerun.pcd'
        write_pcd(check,regenerated.values)
        same_hash=digest(check)==first_changed['derived_sha256']
        # This compact bounded derived file is retained as deterministic evidence.
        write_json(ledger_dir/'deterministic_rerun.json',{'prefix_events':len(repeated),
            'raw_prefix_equal':invariant,'regenerated_PCD_hash_equal':same_hash,
            'derived_sha256':digest(check)})
        if not invariant or not same_hash: raise ValueError('DETERMINISTIC_RERUN_FAILED')
    write_records(ledger_dir/'attempts.jsonl.gz',attempts)
    write_json(ledger_dir/'flow.json',{**spec,'segment':role,'sender':sender,'sender_events':len(sender_raw),
        'companion_events':companions,'scheduled_events':sum(scheduled(e.source_ns) for e in events if e.stream==sender),
        'attempts':len(attempts),'reader_valid':sum(a['reader_valid'] for a in attempts),
        'injection_failed':sum(a['injection_failed'] for a in attempts),'production_reload':True,
        'companion_raw_reuse':'independent of references and peer inputs; fresh production read + hash each episode'})
    write_json(ledger_dir/'access.json',source.access_log+active_source.access_log)
    # Only regenerable derived scratch in this run is removed, after ledgers.
    shutil.rmtree(active)
    return raw


def alignment_poses(poses, *, family, severity, first_ns, intervals):
    """Upstream benign stress; metadata skew cannot move actual availability earlier."""
    from dataclasses import replace
    transformed=[]
    for p in poses:
        matrix=None if p.matrix is None else p.matrix.copy()
        stamp=p.source_ns
        if any(a<=(stamp-first_ns)/1e9<b for a,b in intervals):
            if family=='modeled_source_clock_skew_ms': stamp+=int(severity*1e6)
            elif matrix is not None:
                delta=np.eye(4)
                if family=='assumed_adapter_translation_m': delta[0,3]=severity
                elif family=='assumed_adapter_yaw_deg':
                    angle=np.deg2rad(severity)
                    delta[:2,:2]=[[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]]
                else: raise ValueError('unknown alignment stress')
                matrix=matrix@delta
        transformed.append(replace(p,source_ns=stamp,matrix=matrix))
    return sorted(transformed,key=lambda p:(p.source_ns,p.pose_id))


def run_stage(root: Path, run: Path | None, phase: str) -> Path:
    from datetime import datetime, timezone
    import os, platform, resource, shutil, subprocess, sys, time
    from valid_point.replay import replay
    roles=json.loads((root/'configs/segment_roles.json').read_text())
    method=json.loads((root/'configs/replay_evaluation.json').read_text())
    folds=validate_roles(roles)[:4]
    if run is None:
        run=root/'artifacts'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-R05')
        run.mkdir(exist_ok=False)
    run=run.resolve()
    if run.parent!=root/'artifacts' or (run/'manifest.json').exists(): raise ValueError('new unsealed project run required')
    def note(message):
        line=datetime.now(timezone.utc).isoformat()+' '+message
        print(line,flush=True)
        with (run/'execution.log').open('a') as f: f.write(line+'\n')
    started=time.monotonic()
    note('R05 '+phase+'; existing local data only; no H access')
    try:
        verification=verify_freeze(root)
        if not (run/'protocol.json').exists():
            write_json(run/'protocol.json',{'freeze_sha256':FREEZE,'method':method,'roles':roles,'seed':20261008,
                'implementation_choices':{'identity_schedule':'sustained; five full identity replay episodes',
                'benign_grid':'each individual frozen scalar stress, both schedules; no undeclared Cartesian pairing',
                'clock_skew':'shift modeled sender odometry association stamp; preserve original pose availability so negative skew cannot expose a future input; source cloud clock stays fixed',
                'caching':'parameter-independent companion raw reuse only after fresh production read/hash in each episode'},
                'retention':'existing data immutable; cap run plus single active derived scratch at 4,000,000,000 bytes'})
            write_json(run/'freeze_verification.json',verification)
            inventory=local_inventory(root,roles); write_json(run/'local_inventory.json',inventory)
            if inventory['redundant_partials']:
                (run/'gate.md').write_text('# GR5 — STOPPED\n\nRedundant partial archive found. No download resumed; no data changed. R05 incomplete.\n')
                return run
            write_json(run/'resource_amendment.json',json.loads((root/'artifacts/20261012T130403Z-R05-preparation/resource_amendment.json').read_text()))
            paths=[*root.glob('src/valid_point/**/*.py'),root/'scripts/evaluate_replay.py',root/'tests/test_evaluation.py',
                   root/'notebooks/R05_segment_timelines.ipynb',root/'notebooks/R05_grouped_evaluation.ipynb',*root.glob('configs/*.json')]
            for path in paths:
                if path.exists():
                    dest=run/'source_snapshot'/path.relative_to(root); dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(path,dest)
            write_json(run/'environment_start.json',{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,
                'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
                'git_status':subprocess.check_output(['git','status','--short'],cwd=root,text=True),
                'free_bytes':shutil.disk_usage(root).free})
        snapshot=run/('implementation_'+phase+'_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
        for path in (root/'src/valid_point/evaluation/real.py',root/'src/valid_point/evaluation/statistics.py',
                     root/'scripts/evaluate_replay.py',root/'tests/test_evaluation.py'):
            if path.exists():
                dest=snapshot/path.relative_to(root); dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(path,dest)
        if phase in ('all','intake'):
            for entry in roles['comparison']:
                path=run/'intake'/f"{entry['id']}.json"
                if path.exists(): continue
                note('verify local archive and extracted hashes '+entry['id'])
                try:
                    result=intake_segment(root,run,roles,entry)
                    note('intake '+entry['id']+' '+result['status'])
                except Exception as exc:
                    write_json(path,{'role':entry['id'],'segment':entry['segment'],'status':'FAILED','reason':repr(exc)})
                    note('intake failure '+entry['id']+' '+repr(exc))
        if phase in ('all','predict'):
            clean={}
            for entry in roles['comparison']:
                role=entry['id']; intake=json.loads((run/'intake'/f'{role}.json').read_text())
                path=run/'clean_raw'/f'{role}.jsonl.gz'
                if intake['status']!='USABLE': clean[role]=[]; continue
                if path.exists(): clean[role]=[raw_from_dict(r) for r in read_records(path)]; continue
                note('clean production raw replay '+role)
                source=source_for(root,roles,role)
                clean[role]=list(replay(source.events(first_seconds=25),source))
                write_records(path,(r.as_dict() for r in clean[role]))
                write_json(run/'clean_raw'/f'{role}_access.json',source.access_log)
                note('clean raw complete '+role+' events='+str(len(clean[role])))
            for fold in folds:
                fold_dir=run/'predictions'/fold.id
                if (fold_dir/'complete.json').exists(): continue
                fold_dir.mkdir(parents=True,exist_ok=True)
                if any(not clean.get(role) for role in (*fold.reference,fold.calibration,fold.test)):
                    write_json(fold_dir/'failed_cells.json',{'fold':fold.id,'status':'UNUSABLE_INPUT_SEGMENT','episodes':episode_grid(method)})
                    write_json(fold_dir/'complete.json',{'status':'FAILED_STUDY_CELLS','fold':fold.id}); continue
                refs=fit_references({s:clean[s] for s in fold.reference},fold)
                ref_path=run/'references'/f'{fold.id}.json'
                if not ref_path.exists(): write_json(ref_path,[asdict(v) for v in refs.values()])
                cal_path=run/'calibration'/fold.id/'raw.jsonl.gz'
                if not cal_path.exists():
                    note('fresh clean calibration replay '+fold.id+' '+fold.calibration)
                    source=source_for(root,roles,fold.calibration)
                    calraw=list(replay(source.events(first_seconds=25),source))
                    write_records(cal_path,(r.as_dict() for r in calraw))
                    write_json(cal_path.parent/'access.json',source.access_log)
                else: calraw=[raw_from_dict(r) for r in read_records(cal_path)]
                ref_ids={f'{s}:{r.cloud_id}:{r.input_sha256}' for s in fold.reference for r in clean[s]}
                cal_ids={f'{fold.calibration}:{r.cloud_id}:{r.input_sha256}' for r in calraw}
                test_ids={f'{fold.test}:{r.cloud_id}:{r.input_sha256}' for r in clean[fold.test]}
                if ref_ids&cal_ids or ref_ids&test_ids or cal_ids&test_ids: raise ValueError('LINEAGE_OVERLAP')
                lineage_path=cal_path.parent/'lineage.json'
                if not lineage_path.exists(): write_json(lineage_path,{'fold':asdict(fold),
                    'reference_ids':sorted(ref_ids),'calibration_ids':sorted(cal_ids),'test_ids':sorted(test_ids),
                    'disjoint':True,'calibration_fresh_production_replay':True})
                first=min(r.source_ns for r in calraw)
                calibration_rows,state=score_records(calraw,refs,episode='calibration',first_ns=first)
                thresholds=calibrate(calibration_rows,fold,refs)
                if not (cal_path.parent/'thresholds.json').exists():
                    write_json(cal_path.parent/'thresholds.json',list(thresholds.values()))
                    write_records(cal_path.parent/'scores.jsonl.gz',calibration_rows)
                    write_json(cal_path.parent/'state.json',state)
                first=min(r.source_ns for r in clean[fold.test])
                memo=CausalRawMemo()
                memo_source=source_for(root,roles,fold.test)
                memo_poses={s:memo_source.read_poses(s) for s in ('003','004','laser')}
                memo.seed(memo_source.events(first_seconds=25),clean[fold.test],memo_poses)
                for i,spec in enumerate(episode_grid(method)):
                    ep_dir=fold_dir/spec['episode']
                    if (ep_dir/'state.json').exists(): continue
                    usage=sum(p.stat().st_size for p in run.rglob('*') if p.is_file())
                    if usage>2_000_000_000: raise RuntimeError('run compact evidence exceeds 2 GB; preserving 2 GB for one derived episode within cap')
                    note(f"{fold.id} episode {i+1}/62 {spec['kind']} {spec['family']} {spec['severity']} {spec['schedule']}")
                    t=time.monotonic()
                    if spec['kind']=='clean': raw=clean[fold.test]
                    else: raw=replay_episode(root,run,roles,fold.test,spec,method,clean[fold.test],memo)
                    pred,state=score_records(raw,refs,episode=spec['episode'],first_ns=first,thresholds=thresholds)
                    write_records(ep_dir/'raw.jsonl.gz',(r.as_dict() for r in raw))
                    write_records(ep_dir/'scores.jsonl.gz',pred)
                    write_json(ep_dir/'state.json',state)
                    note(f"{fold.id} episode complete events={len(raw)} wall_s={time.monotonic()-t:.2f}")
                write_json(fold_dir/'complete.json',{'fold':fold.id,'episodes':len(episode_grid(method)),'status':'PREDICTIONS_COMPLETE'})
            if not (run/'prediction_seal.json').exists():
                write_json(run/'prediction_seal.json',{'folds':[f.id for f in folds],
                    'created_utc':datetime.now(timezone.utc).isoformat(),
                    'files':{str(p.relative_to(run/'predictions')):digest(p) for p in (run/'predictions').rglob('*') if p.is_file()}})
            require_prediction_seal(run/'predictions',json.loads((run/'prediction_seal.json').read_text()))
            note('ALL FOUR FOLD PREDICTIONS SEALED; evaluator joins now permitted')
        if phase in ('all','report'):
            from valid_point.evaluation.statistics import report_run
            report_run(root,run,note)
        note('phase completed wall_s='+str(round(time.monotonic()-started,2)))
        if phase=='finalize':
            from valid_point.evaluation.statistics import finalize_run
            finalize_run(root,run,note)
        return run
    except Exception as exc:
        note('FAILED '+repr(exc))
        stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        write_json(run/f'failure_{stamp}.json',{'phase':phase,'error':repr(exc)})
        raise


class CausalRawMemo:
    """Memoize frozen raw computation only for identical current/past inputs.

    Every cache lookup follows a fresh production cloud read and causal pose
    selection. No references, scores, labels, schedule or future input is a key.
    Misses call the unchanged production replay on the current and last eligible
    event. This is parameter-independent raw reuse permitted by the split contract.
    """
    def __init__(self):
        self.rows={}
        self.hits=0
        self.misses=0

    @staticmethod
    def pose_key(event,poses):
        from valid_point.replay import _select_pose
        if event.stream not in ('003','004','laser'): return 'STATIC_RSU'
        p,reason=_select_pose(poses.get(event.stream,[]),event.source_ns,event.deadline_ns,150_000_000)
        return [reason,None if p is None else [p.pose_id,p.source_ns,p.available_ns,p.matrix.tolist()]]

    @staticmethod
    def event_key(event,digest_value,pose):
        return [event.cloud_id,event.stream,event.principal,event.sync_id,event.source_ns,event.arrival_ns,event.deadline_ns,event.state,digest_value,pose]

    @staticmethod
    def admitted(event,row,prior):
        return row.reason=='VALID' and row.input_sha256 is not None and (prior is None or event.source_ns>prior[0].source_ns)

    def seed(self,events,records,poses):
        by_id={r.cloud_id:r for r in records}; history={}
        for event in events:
            row=by_id[event.cloud_id]; prior=history.get(event.stream)
            pose=self.pose_key(event,poses)
            current=self.event_key(event,row.input_sha256,pose)
            key=canonical_hash([current,None if prior is None else prior[1]])
            if row.history_id != (None if prior is None else prior[0].cloud_id): raise ValueError('seed history differs from causal admission')
            self.rows[key]=row
            if self.admitted(event,row,prior): history[event.stream]=(event,current)

    def replay(self,events,source,poses):
        from valid_point.replay import replay
        history={}; output=[]
        for event in events:
            prior=history.get(event.stream); pose=self.pose_key(event,poses)
            eligible=(event.state=='present' and event.source_ns<=event.arrival_ns<=event.deadline_ns
                      and event.deadline_ns-event.source_ns<=150_000_000)
            h=None
            if eligible:
                try: _,h=source.read_cloud(event)
                except (ValueError,OSError,UnicodeError): pass
            current=self.event_key(event,h,pose)
            key=canonical_hash([current,None if prior is None else prior[1]])
            if key in self.rows:
                row=self.rows[key]; self.hits+=1
            else:
                pair=[event] if prior is None else [prior[0],event]
                computed=replay(pair,source,poses=poses)
                if prior is not None and computed[0].input_sha256!=prior[1][8]: raise ValueError('past input changed during replay')
                row=computed[-1]; self.rows[key]=row; self.misses+=1
            output.append(row)
            if self.admitted(event,row,prior): history[event.stream]=(event,current)
        return tuple(output)
