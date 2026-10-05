"""S02 raw measurements and literal demonstration fixtures. No fitting or scoring.

The notebook adapters below only construct frozen inputs, call measurement
functions, check hand expectations, and export/display complete small results.
"""
from dataclasses import asdict
import json
from pathlib import Path

import numpy as np

from valid_point.contracts import DecisionInput, DecisionKey, MessageState, RigidTransform
from valid_point.io.pointcloud import PointCloud
from valid_point.provenance import (export_table, json_bytes, output_stem,
                                    sha256_bytes, sha256_file, write_json_new)
from .availability import ReceiverContext, measure_availability
from .kinematics import MotionSample, measure_motion
from .spatial import FixedRegion, RegionSet, count_regions


LIMITATIONS = (
    "Motion self-consistency has no independent motion observation: jointly consistent "
    "spoofed pose/velocity has zero residual, while legitimate acceleration has nonzero residual. "
    "Counts do not identify intent: dense legitimate returns are large, within-region "
    "rearrangement preserves counts, and removal lowers counts. Unknown visibility forbids "
    "zero-return/deficit accusations. No normalized evidence, trust probability, conformity "
    "score, alarm, reference fit or calibration is produced. G2 remains incomplete until S03."
)


def load_raw_config(path: Path) -> dict:
    config = json.loads(path.read_text())
    if (config['schema_version'] != 's02.raw.v1' or config['stage'] != 'S02'
            or config['track'] != 'gt_free' or config['seed'] is not None
            or not 0 <= config['region_frozen_ns'] <= config['anchor_ns'] <= config['deadline_ns']):
        raise ValueError('unsupported S02 configuration')
    return config


def fixture_key(config, case):
    return DecisionKey(config['segment'], case, config['frame_id'], config['deadline_ns'])


def fixed_regions(config):
    return RegionSet(tuple(FixedRegion(r['region_id'], tuple(r['lower_m']), tuple(r['upper_m']))
                           for r in config['regions']), 'gt_free', 'receiver',
                     config['region_provenance'], config['region_frozen_ns'])


def cloud_fixture(config, case):
    """Only literal hand cases; no perturbation/attack generator or evaluator input."""
    points = case.get('points', [[1, 1, 0, 1]])
    state = MessageState(case.get('state', 'present_nonempty' if points else 'present_empty'))
    cloud = (PointCloud('sensor', tuple(tuple(p) for p in points))
             if points is not None and state in (MessageState.PRESENT_NONEMPTY, MessageState.PRESENT_EMPTY)
             else None)
    source = case.get('source_ns', config['anchor_ns'])
    arrival = (None if state == MessageState.ABSENT else
               config['deadline_ns'] + 10000000 if state == MessageState.LATE else source + 10000000)
    transform = RigidTransform('receiver_from_sensor', 'sensor',
                               'unsupported' if case.get('transform') == 'unsupported' else 'receiver',
                               tuple(tuple(r) for r in np.eye(4)), 0,
                               source - 1 if case.get('transform') == 'expired' else 2000000000,
                               'independent receiver calibration; hand-defined identity')
    cloud_id = 'sha256:' + sha256_bytes(json_bytes(asdict(cloud))) if cloud else None
    row = DecisionInput(fixture_key(config, case['case']), 'hand_sensor', 'hand_principal',
                        'vehicle', config['anchor_ns'], None if state == MessageState.ABSENT else source, arrival, state, cloud_id,
                        cloud.count if cloud is not None else None, transform.transform_id)
    context = ReceiverContext('receiver_context:' + case['case'],
                              case.get('context_available_ns', 0),
                              'trusted hand-fixture receiver context; no sender health inference',
                              case.get('clock_verified', True), case.get('membership_verified', True),
                              case.get('health', 'healthy'), transform, 0)
    return row, cloud, context


def motion_demo(config):
    rows, inputs, checks, results = [], [], [], []
    for case in config['motion_cases']:
        samples = tuple(MotionSample(**s) for s in case['samples'])
        result = measure_motion(fixture_key(config, case['case']), samples,
                                anchor_ns=config['anchor_ns'], sensor_role=case.get('sensor_role', 'vehicle'),
                                **config['motion'])
        results.append((case, result))
        for s in samples:
            inputs.append({'case': case['case'], **asdict(s)})
        m = result.residual
        expected = case.get('expected_m')
        passed = (m.status.value == 'known' and np.isclose(m.value, expected, rtol=0, atol=1e-12)
                  if expected is not None else m.reason == case['expected_reason'] and m.value is None)
        checks.append({'case': case['case'], 'expected': expected if expected is not None else case['expected_reason'],
                       'observed': m.value if m.value is not None else m.reason, 'pass': bool(passed)})
        prior = next((s for s in samples if result.selected_ids and s.sample_id == result.selected_ids[0]), None)
        rows.append({'case': case['case'], 'sender': m.key.sender, 'frame': m.key.frame_id,
                     'deadline_ns': m.key.deadline_ns, 'dt_s': result.dt_s,
                     'displacement_m': result.displacement_m, 'predicted_m': result.predicted_displacement_m,
                     'residual_vector_m': result.residual_vector_m, 'residual_m': m.value,
                     'position_frame': prior.position_frame if prior else None,
                     'position_unit': prior.position_unit if prior else None,
                     'velocity_frame': prior.velocity_frame if prior else None,
                     'velocity_unit': prior.velocity_unit if prior else None,
                     'status': m.status.value, 'reason': m.reason, 'source_ids': m.source_ids,
                     'available_ns': m.available_ns, 'excluded': result.excluded})
    return rows, inputs, checks, results


def spatial_demo(config):
    regions = fixed_regions(config)
    rows, inputs, checks, results = [], [], [], []
    for case in config['spatial_cases']:
        row, cloud, context = cloud_fixture(config, case)
        result = count_regions(row, cloud, regions, context, max_cloud_age_ns=config['max_cloud_age_ns'])
        results.append((case, result))
        inputs.append({'case': case['case'], 'decision': asdict(row), 'cloud': asdict(cloud) if cloud else None,
                       'receiver_context': asdict(context)})
        values = [m.value for m in result.counts]
        passed = (values == case['expected'] and result.outside_regions.value == case['outside']
                  if 'expected' in case else result.reason == case['expected_reason'] and all(v is None for v in values))
        checks.append({'case': case['case'], 'expected': case.get('expected', case.get('expected_reason')),
                       'observed': values if result.coverage_status.value == 'known' else result.reason, 'pass': passed})
        for region, m in zip(regions.regions, result.counts):
            rows.append({'case': case['case'], 'sender': row.key.sender, 'frame': row.key.frame_id,
                         'deadline_ns': row.key.deadline_ns, 'region': region.region_id,
                         'bounds_m': [region.lower_m, region.upper_m], 'volume_m3': region.volume_m3,
                         'count_points': m.value, 'outside_union_points': result.outside_regions.value,
                         'status': m.status.value, 'reason': m.reason, 'visibility': result.visibility,
                         'deficit_inference': result.deficit_inference, 'track': result.track,
                         'region_provenance': result.region_provenance, 'source_ids': m.source_ids,
                         'available_ns': m.available_ns})
    return rows, inputs, checks, results


def availability_demo(config):
    rows, inputs, checks, results = [], [], [], []
    for case in config['availability_cases']:
        row, cloud, context = cloud_fixture(config, case)
        result = measure_availability(row, cloud, context, max_cloud_age_ns=config['max_cloud_age_ns'])
        results.append((case, result))
        inputs.append({'case': case['case'], 'decision': asdict(row), 'cloud': asdict(cloud) if cloud else None,
                       'receiver_context': asdict(context)})
        checks.append({'case': case['case'], 'expected': case['expected'], 'observed': result.eligible.reason,
                       'pass': result.eligible.reason == case['expected']})
        rows.append({'case': case['case'], 'sender': row.key.sender, 'frame': row.key.frame_id,
                     'source_ns': row.source_ns, 'arrival_ns': row.arrival_ns, 'deadline_ns': row.key.deadline_ns,
                     'message_state': result.message_state, 'source_age_s': result.freshness.value,
                     'freshness_status': result.freshness.status.value, 'freshness_reason': result.freshness.reason,
                     **{f'{name}_{field}': getattr(getattr(result, name), field).value
                        if field == 'status' else getattr(getattr(result, name), field)
                        for name in ('payload', 'transform', 'health', 'membership', 'eligible')
                        for field in ('status', 'reason')},
                     'provenance': result.provenance, 'context_id': result.context_id,
                     'intent': 'not inferred'})
    return rows, inputs, checks, results


def evidence_figure(section, config, results, report_dir, provenance):
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib.figure import Figure
    from matplotlib.patches import Rectangle
    names = {'kinematics': 'F02_motion', 'spatial': 'F02_regions', 'availability': 'F02_deadlines'}
    name = names[section]
    fig = Figure(figsize=(12, 7), dpi=150, layout='constrained')
    if section == 'kinematics':
        ax, bars = fig.subplots(1, 2)
        for index, (case, result) in enumerate(results[:5]):
            if result.residual.value is None:
                continue
            ax.plot([0, result.predicted_displacement_m[0]], [index, index], 'o--', color='#4778a8')
            ax.plot([0, result.displacement_m[0]], [index+.15, index+.15], 's-', color='#ce7141')
        ax.set_yticks(range(5), [c['case'].replace('_', '\n') for c, r in results[:5]], fontsize=9)
        ax.set_xlabel('Receiver x displacement (m); blue predicted, orange actual')
        ax.set_title('Input pairs: dt = 0.5 s, prior velocity m/s\nRotated case moves in y (shown in table)')
        known = [(c, r) for c, r in results if r.residual.value is not None]
        bars.barh([c['case'].replace('_', ' ') for c, r in known], [r.residual.value for c, r in known], color='#4778a8')
        bars.set_xlabel('Norm of displacement − prediction (m)')
        bars.set_title('Self-consistency only; unknowns retained in table')
        bars.invert_yaxis()
    elif section == 'spatial':
        axes = fig.subplots(2, 3).flat
        for ax, (case, result) in zip(axes, results[:6]):
            for region in fixed_regions(config).regions:
                x, y, _ = region.lower_m
                ax.add_patch(Rectangle((x,y),5,5,fill=False,edgecolor='#4778a8'))
                ax.text(x+.15,y+4.4,region.region_id,fontsize=8)
            points = np.asarray(case['points'])
            ax.scatter(points[:,0],points[:,1],s=24,color='#ce7141')
            ax.set(xlim=(-.5,12),ylim=(-.5,10.5),xlabel='receiver x (m)',ylabel='receiver y (m)',aspect='equal')
            ax.set_title(case['case'].replace('_',' ')+'\ncounts: '+str([m.value for m in result.counts]),fontsize=10)
    else:
        ax = fig.subplots()
        for index, (case, result) in enumerate(results):
            row, _, _ = cloud_fixture(config, case)
            if row.source_ns is not None:
                ax.scatter(row.source_ns / 1e9,index,marker='o',color='#4778a8')
            if row.arrival_ns is not None:
                ax.scatter(row.arrival_ns / 1e9,index,marker='x',color='#ce7141')
                ax.plot([row.source_ns/1e9,row.arrival_ns/1e9],[index,index],color='gray',lw=1)
        ax.axvline(config['deadline_ns']/1e9,color='black',linestyle='--',label='deadline')
        ax.scatter([],[],marker='o',color='#4778a8',label='source time (metadata)')
        ax.scatter([],[],marker='x',color='#ce7141',label='receipt; late is diagnostic only')
        ax.set_yticks(range(len(results)), [c['case'].replace('_',' ')+' / '+r.eligible.status.value for c,r in results])
        ax.invert_yaxis()
        ax.set_xlabel('Synthetic common clock (s)')
        ax.set_xlim(.96,1.82)
        ax.legend(loc='lower right',fontsize=8)
        ax.set_title('Freshness, health and transform eligibility are separate; no intent inference')
    fig.suptitle(name+' — S02 raw hand fixtures\n'+provenance['run_id']+' / '+provenance['track']+' / '+provenance['segment'],fontsize=11)
    stem = output_stem(name, provenance)
    paths = [report_dir / (stem+'.'+ext) for ext in ('pdf','svg','png','provenance.json')]
    if any(p.exists() for p in paths):
        raise FileExistsError(stem)
    report_dir.mkdir(parents=True,exist_ok=True)
    for path in paths[:3]:
        fig.savefig(path)
    write_json_new(paths[3],{**provenance,'name':name,'outputs':{p.name:sha256_file(p) for p in paths[:3]}})
    return paths


def export_demo(section, root, run_dir, config, provenance):
    demos = {'kinematics': (motion_demo, 'T02_kinematic_raw'),
             'spatial': (spatial_demo, 'T02_region_counts'),
             'availability': (availability_demo, 'T02_eligibility')}
    demo, name = demos[section]
    rows, inputs, checks, results = demo(config)
    write_json_new(run_dir / (section+'_inputs.json'), inputs)
    write_json_new(run_dir / (section+'_checks.json'), checks)
    provenance = {**provenance, 'input_sha256': sha256_file(run_dir/(section+'_inputs.json')),
                  'region_provenance': config['region_provenance'] if section == 'spatial' else 'not applicable: no regions consumed',
                  'reference_lineage': config['reference_lineage'], 'calibration_lineage': config['calibration_lineage']}
    tables = export_table(rows, name, root/'reports/tables', provenance)
    check_paths = export_table(checks, 'T02_'+section+'_checks', root/'reports/tables', provenance)
    figures = evidence_figure(section, config, results, root/'reports/figures', provenance)
    passed = all(c['pass'] for c in checks)
    write_json_new(run_dir/(section+'_gate.json'), {'status':'PASS' if passed else 'FAIL', 'checks':len(checks), 'limitations':LIMITATIONS})
    return {'rows':rows, 'inputs':inputs, 'checks':checks, 'tables':tables, 'check_tables':check_paths,
            'figures':figures, 'status':'PASS' if passed else 'FAIL', 'limitations':LIMITATIONS}
