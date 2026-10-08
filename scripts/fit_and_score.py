"""Execute only S03 tests and two fresh notebooks; seal immutable evidence."""
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import secrets
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from valid_point.provenance import execute_notebook, git_revision, sha256_file, utc_now, write_json_new

NOTEBOOKS=('03_clean_references','03_score_and_ablations')


def main():
    config_path=ROOT/'configs/reference_protocol.json'
    config=json.loads(config_path.read_text())
    ref=set(config['reference_seeds']); cal=set(config['calibration_seeds']); test=set(config['test_seeds'])
    if ref & cal or ref & test or cal & test or not all(len(s)>=2 for s in (ref,cal,test)):
        raise ValueError('split lineage is not disjoint')
    sources=sorted(set([p for folder in ('src','tests','configs','scripts') for p in (ROOT/folder).rglob('*') if p.suffix in ('.py','.json')]
                       +[ROOT/'notebooks'/(name+'.ipynb') for name in NOTEBOOKS]
                       +[ROOT/'planning/03_phase1_evidence.md',ROOT/'planning/07_validation.md',ROOT/'planning/08_notebooks.md',ROOT/'pyproject.toml',ROOT/'requirements.lock',ROOT/'.gitignore']))
    source_hashes={str(p.relative_to(ROOT)):sha256_file(p) for p in sources}
    digest=hashlib.sha256()
    for p in sources: digest.update(str(p.relative_to(ROOT)).encode()+b'\0'+p.read_bytes()+b'\0')
    source_hash=digest.hexdigest()
    run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+secrets.token_hex(4)
    run=ROOT/'artifacts'/run_id; run.mkdir(parents=True,exist_ok=False)
    started=utc_now(); failures=[]; log=[f'start: {started}',f'command: {sys.executable} scripts/fit_and_score.py']
    for p in sources:
        dest=run/'source'/p.relative_to(ROOT); dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(p.read_bytes())
    (run/'config.json').write_bytes(config_path.read_bytes())
    write_json_new(run/'seeds.json',{'reference':sorted(ref),'calibration':sorted(cal),'test':sorted(test),
                                    'rng_scheme':config['rng_scheme']})
    env={**os.environ,'PYTHONPATH':str(ROOT/'src'),'MPLCONFIGDIR':str(run/'matplotlib_cache')}
    command=[sys.executable,'-m','pytest','-q','tests','--junitxml='+str(run/'tests.xml')]
    test_result=subprocess.run(command,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    write_json_new(run/'test_results.json',{'command':command,'exit_code':test_result.returncode,'output':test_result.stdout})
    log += ['tests:',test_result.stdout]
    if test_result.returncode: failures.append('test suite failed')
    notebooks=[]; old={k:os.environ.get(k) for k in ('PYTHONPATH','MPLCONFIGDIR')}
    try:
        os.environ['PYTHONPATH']=env['PYTHONPATH'];os.environ['MPLCONFIGDIR']=env['MPLCONFIGDIR']
        for name in NOTEBOOKS:
            log.append(f'{utc_now()} fresh kernel start: {name}')
            try:
                execute_notebook(ROOT/'notebooks'/(name+'.ipynb'),run/(name+'.executed.ipynb'),ROOT,
                                 {'VP_REPO_ROOT':str(ROOT),'VP_RUN_DIR':str(run),'VP_SOURCE_SHA256':source_hash})
                notebooks.append(name+'.executed.ipynb'); log.append(f'{utc_now()} notebook PASS: {name}')
            except Exception as exc:
                failures.append(f'{name}: {type(exc).__name__}: {exc}')
                log.append(f'{utc_now()} notebook FAIL: {failures[-1]}')
    finally:
        for k,v in old.items():
            if v is None: os.environ.pop(k,None)
            else: os.environ[k]=v
    score_path=run/'score_summary.json'
    if score_path.exists():
        score=json.loads(score_path.read_text())
        if score['hand_cases_passed']!=12 or not score['sweep_nonincreasing']:
            failures.append('hand contract or point sweep failed')
        if score['calibration']['status']!='available': failures.append('calibration unavailable')
    else: failures.append('score evidence missing')
    if any(sha256_file(ROOT/p)!=h for p,h in source_hashes.items()): failures.append('source changed during execution')
    if subprocess.run(['git','check-ignore','-q',str(run/'source')],cwd=ROOT).returncode:
        failures.append('source snapshot not Git-ignored')
    status='PASS' if not failures else 'FAIL'
    suffix='_S03_gt_free_illustrative_clean_fixtures_'+run_id
    links='\n'.join(f'- [{name}](./{name})' for name in notebooks)
    for table in ('T03_reference_support','T03_ablations','T03_hand_cases','T03_point_count_sweep'):
        links+=f'\n- [{table}](../../reports/tables/{table}{suffix}.md)'
    for figure in ('F03_clean_distributions','F03_threshold_ablation','F03_trust_point_count'):
        links+=f'\n- [{figure}](../../reports/figures/{figure}{suffix}.png)'
    calibration=json.loads((run/'calibration.json').read_text()) if (run/'calibration.json').exists() else None
    score=json.loads(score_path.read_text()) if score_path.exists() else None
    gate=(f'# S03 G2 score/calibration gate\n\n**{status}** — reproducible illustrative semantics only.\n\n'
          f'Tests exit: {test_result.returncode}; fresh notebooks: {len(notebooks)}/2. '
          f'Separate reference/calibration/test seeds: {len(ref)}/{len(cal)}/{len(test)}.\n\n'
          f'Calibration: {calibration}; score summary: {score}.\n\n'
          'The clean distributions are deterministic illustrative raw fixtures, not replayed LiDAR. '
          'The frozen 1% threshold and its achieved rate do not establish sensor FPR or attack power. '
          'Frame correlation limits the Wilson interval; segment rates are displayed. '
          'Static S-only and strict unknown states are contract cases. Future policy parameters remain unset. '
          'No attack tuning, learned weights, external data or next stage executed.\n\n'
          f'Failures: {failures or "none"}.\n\nEvidence: [manifest](manifest.json), '
          '[tests](test_results.json), [execution log](execution.log), '
          '[reference summary](reference_summary.json), [score summary](score_summary.json).\n\n'+links+'\n')
    (run/'gate.md').write_text(gate)
    finished=utc_now();log += [f'finish: {finished}',f'gate: {status}']
    (run/'execution.log').write_text('\n'.join(log)+'\n')
    reports=sorted(p for folder in ('tables','figures') for p in (ROOT/'reports'/folder).glob('*'+run_id+'*'))
    outputs=sorted(p for p in run.rglob('*') if p.is_file())+reports
    manifest={'manifest_schema_version':'s03.manifest.v1','stage':'S03','stage_version':'1',
              'run_id':run_id,'started_utc':started,'finished_utc':finished,
              'exact_command':f'{sys.executable} scripts/fit_and_score.py',
              'configuration':{'source':'configs/reference_protocol.json','sha256':sha256_file(run/'config.json'),'value':config},
              'seeds':{'file':'seeds.json','sha256':sha256_file(run/'seeds.json'),'reference':sorted(ref),
                       'calibration':sorted(cal),'test':sorted(test),'rng_scheme':config['rng_scheme']},
              'source':{**git_revision(ROOT),'snapshot_sha256':source_hash,'files':source_hashes,
                        'snapshot_path':'source','source_url':'local deterministic illustrative clean fixtures',
                        'source_revision':'s03.reference.v1','license':'project source; no external dataset'},
              'environment':{'python':sys.version,'platform':platform.platform(),'executable':sys.executable,
                             'packages':{n:importlib.metadata.version(n) for n in ('numpy','matplotlib','pytest','nbformat','nbclient','ipykernel')}},
              'decision_context':{'track':'gt_free','segment':config['segment'],'decision_unit':config['decision_unit'],
                                  'deadline_ns':config['engineering_validity']['deadline_ns'],
                                  'reference_fit':'reference seeds only','calibration':'separate calibration seeds'},
              'data_lineage':{'reference_seeds':sorted(ref),'calibration_seeds':sorted(cal),'test_seeds':sorted(test),
                              'reference_bundle':'reference_bundle.json','calibration_bundle':'calibration.json',
                              'input_fixture_config_sha256':sha256_file(run/'config.json'),'archive':'not applicable'},
              'inputs':{'config.json':sha256_file(run/'config.json'),'seeds.json':sha256_file(run/'seeds.json')},
              'outputs':{str(p.relative_to(ROOT)):sha256_file(p) for p in outputs},
              'failures':failures,'tests':{'exit_code':test_result.returncode,'report':'test_results.json','junit':'tests.xml'},
              'executed_notebooks':notebooks,'gate':'gate.md',
              'research_status':{'semantics':status,'empirical_detection':'not run','future_policy':'not run'}}
    write_json_new(run/'manifest.json',manifest)
    for name,expected in manifest['outputs'].items():
        if sha256_file(ROOT/name)!=expected: raise RuntimeError('output hash mismatch: '+name)
    for p in outputs+[run/'manifest.json']: p.chmod(0o444)
    for p in sorted((p for p in run.rglob('*') if p.is_dir()),reverse=True): p.chmod(0o555)
    run.chmod(0o555)
    print(run);print(gate)
    return 0 if status=='PASS' else 1


if __name__=='__main__': raise SystemExit(main())
