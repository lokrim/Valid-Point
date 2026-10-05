"""Execute only S02: tests, three fresh kernels and an immutable evidence bundle."""
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from valid_point.evidence import LIMITATIONS, load_raw_config
from valid_point.provenance import execute_notebook, git_revision, sha256_file, utc_now, write_json_new

NOTEBOOKS = ('02_kinematics', '02_spatial_surplus', '02_availability')


def main():
    config_path = ROOT / 'configs/raw_evidence.json'
    config = load_raw_config(config_path)
    sources = sorted(set(
        [p for folder in ('src', 'tests', 'configs', 'scripts')
         for p in (ROOT/folder).rglob('*') if p.suffix in ('.py','.json')]
        + [ROOT/'notebooks'/(name+'.ipynb') for name in NOTEBOOKS]
        + [ROOT/'.gitignore', ROOT/'pyproject.toml', ROOT/'requirements.lock', ROOT/'planning/03_phase1_evidence.md',
           ROOT/'planning/08_notebooks.md']))
    source_hashes = {str(p.relative_to(ROOT)):sha256_file(p) for p in sources}
    digest = hashlib.sha256()
    for path in sources:
        digest.update(str(path.relative_to(ROOT)).encode()+b'\0'+path.read_bytes()+b'\0')
    source_hash = digest.hexdigest()
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+secrets.token_hex(4)
    run = ROOT/'artifacts'/run_id
    run.mkdir(parents=True,exist_ok=False)
    started = utc_now()
    for path in sources:
        destination = run/'source'/path.relative_to(ROOT)
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(path.read_bytes())
    (run/'config.json').write_bytes(config_path.read_bytes())
    write_json_new(run/'seeds.json',{'seed':config['seed'],'rng_scheme':config['rng_scheme']})
    env = {**os.environ, 'PYTHONPATH':str(ROOT/'src'), 'MPLCONFIGDIR':str(run/'matplotlib_cache')}
    command = [sys.executable,'-m','pytest','-q','tests','--junitxml='+str(run/'tests.xml')]
    test = subprocess.run(command,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    write_json_new(run/'test_results.json',{'command':command,'exit_code':test.returncode,'output':test.stdout})
    failures = [] if test.returncode == 0 else ['test suite failed']
    log = [f'start: {started}',f'command: {sys.executable} scripts/measure_synthetic.py',test.stdout]
    notebooks = []
    previous = {k:os.environ.get(k) for k in ('PYTHONPATH','MPLCONFIGDIR')}
    try:
        for key in previous:
            os.environ[key] = env[key]
        for name in NOTEBOOKS:
            destination = run/(name+'.executed.ipynb')
            log.append(f'{utc_now()} fresh kernel start: {name}')
            try:
                execute_notebook(ROOT/'notebooks'/(name+'.ipynb'),destination,ROOT,
                                 {'VP_REPO_ROOT':str(ROOT),'VP_RUN_DIR':str(run),'VP_SOURCE_SHA256':source_hash})
                notebooks.append(destination.name)
                log.append(f'{utc_now()} notebook PASS: {name}')
            except Exception as exc:
                failures.append(f'{name}: {type(exc).__name__}: {exc}')
                log.append(f'{utc_now()} notebook FAIL: {failures[-1]}')
    finally:
        for key,value in previous.items():
            if value is None:
                os.environ.pop(key,None)
            else:
                os.environ[key] = value
    for section in ('kinematics','spatial','availability'):
        gate = run/(section+'_gate.json')
        if not gate.exists() or json.loads(gate.read_text())['status'] != 'PASS':
            failures.append(section+' visible hand-case gate did not pass')
    # Prevent a concurrently edited source from masquerading as the frozen snapshot.
    if any(sha256_file(ROOT/name) != h for name,h in source_hashes.items()):
        failures.append('source changed during execution')
    ignored = subprocess.run(['git','check-ignore','-q',str(run/'source')],cwd=ROOT)
    if ignored.returncode != 0:
        failures.append('source snapshot is not Git-ignored')
    status = 'FAIL' if failures else 'PASS'
    evidence_links = '\n'.join(
        f'- [{name}](./{name}.executed.ipynb)' for name in NOTEBOOKS)
    for table, figure in (('T02_kinematic_raw','F02_motion'), ('T02_region_counts','F02_regions'),
                          ('T02_eligibility','F02_deadlines')):
        suffix = '_S02_gt_free_hand_cases_'+run_id
        evidence_links += (f'\n- [{table}](../../reports/tables/{table}{suffix}.md) / '
                           f'[{figure}](../../reports/figures/{figure}{suffix}.png)')
    (run/'gate.md').write_text(
        f'# S02 raw evidence gate\n\n**{status}** — raw contracts and strict unknown states only.\n\n'
        f'Tests exit code: {test.returncode}; fresh kernels completed: {len(notebooks)}/3. '
        'Each notebook has 12 complete hand cases, named tables/figures and explicit expectations.\n\n'
        +LIMITATIONS+'\n\n'
        'S02 passing permits review for a separately invoked S03; it does not execute fitting. '
        'G2 as a whole is BLOCKED pending S03. No data download or other stage executed.\n\n'
        f'Execution failures: {failures or "none"}.\n\n'
        'Evidence: [manifest](manifest.json), [tests](test_results.json), [execution log](execution.log).\n\n'
        + evidence_links + '\n')
    finished = utc_now()
    log += [f'finish: {finished}',f'S02 gate: {status}',LIMITATIONS]
    (run/'execution.log').write_text('\n'.join(log)+'\n')
    reports = sorted(p for folder in ('tables','figures') for p in (ROOT/'reports'/folder).glob('*'+run_id+'*'))
    outputs = sorted(p for p in run.rglob('*') if p.is_file())+reports
    manifest = {
        'manifest_schema_version':'s02.manifest.v1','stage':'S02','stage_version':'1',
        'run_id':run_id,'started_utc':started,'finished_utc':finished,
        'exact_command':f'{sys.executable} scripts/measure_synthetic.py',
        'configuration':{'source':'configs/raw_evidence.json','sha256':sha256_file(run/'config.json'),'value':config},
        'seeds':{'file':'seeds.json','sha256':sha256_file(run/'seeds.json'),'value':config['seed'],'rng_scheme':config['rng_scheme']},
        'source':{**git_revision(ROOT),'snapshot_sha256':source_hash,'files':source_hashes,
                  'snapshot_path':'source','source_url':'local literal hand fixtures; no external data',
                  'source_revision':'s02.raw.v1','license':'project source; no third-party dataset'},
        'environment':{'python':sys.version,'platform':platform.platform(),'executable':sys.executable,
                       'packages':{n:importlib.metadata.version(n) for n in ('numpy','matplotlib','pytest','nbformat','nbclient','ipykernel')}},
        'decision_context':{k:config[k] for k in ('track','segment','split_role','anchor_ns','deadline_ns','frame_id','time_mapping')},
        'data_lineage':{'reference':config['reference_lineage'],'calibration':config['calibration_lineage'],
                        'input_fixture_config_sha256':sha256_file(run/'config.json'),
                        'archive':'not applicable','policy':'not run','attack_framework':'not run'},
        'inputs':{str(p.relative_to(run)):sha256_file(p) for p in run.glob('*_inputs.json')},
        'outputs':{str(p.relative_to(ROOT)):sha256_file(p) for p in outputs},
        'failures':failures,'scientific_limitations':LIMITATIONS,
        'tests':{'exit_code':test.returncode,'report':'test_results.json','junit':'tests.xml'},
        'executed_notebooks':notebooks,'gate':'gate.md',
        'research_status':{'raw_contracts':status,'references':'not run','score':'not run','calibration':'not run','alarm':'not run'}}
    write_json_new(run/'manifest.json',manifest)
    for name, expected in manifest['outputs'].items():
        if sha256_file(ROOT/name) != expected:
            raise RuntimeError('output hash mismatch: '+name)
    for path in outputs+[run/'manifest.json']:
        path.chmod(0o444)
    for path in sorted((p for p in run.rglob('*') if p.is_dir()),reverse=True):
        path.chmod(0o555)
    run.chmod(0o555)
    print(run)
    print((run/'gate.md').read_text())
    return 0 if status == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
