"""S03 diagnostic ablations and deterministic illustrative observations."""
from __future__ import annotations
from .scoring import score


def clean_fixture_rows(seeds: list[int], role: str) -> list[dict]:
    """Deterministic clean raw fixtures; no LiDAR replay or empirical distribution claim."""
    rows = []
    for seed in seeds:
        segment = f'illustrative_scene_{seed}'
        for frame in range(40):
            # Each sender/frame has one K residual and three frozen 5 m tile counts.
            k = round(.02 + .01*((seed*7 + frame*3) % 19), 4)
            for factor, region, value, bin_id, units in (
                ('K', 'motion', k, 'dt_0p5s', 'm'),
                ('S', 'gt_free:A', float(4 + (seed + frame*3) % 9), 'A_near', 'points'),
                ('S', 'gt_free:B', float(5 if frame < 20 else 2 + (seed*3 + frame) % 7), 'B_constant' if frame < 20 else 'B_near', 'points'),
                ('S', 'gt_free:C', float(1 + (seed + frame) % 5), 'C_far_sparse' if seed % 10 < 4 else 'C_near', 'points')):
                rows.append({'split_role':role,'clean':True,'seed':seed,'segment':segment,
                             'frame':frame,'factor':factor,'region_id':region,'sensor_class':'vehicle',
                             'bin_id':bin_id,'value':value,'units':units,
                             'deadline_ns':1550000000+frame*100000000,'track':'gt_free'})
    return rows


def ablation_row(K: float | None, S: float | None, *, role: str = 'vehicle') -> dict:
    k = score('vehicle', K, None)
    s = score('static_rsu', None, S)
    combined = score(role, K, S)
    return {'K_only_T':None if K is None else 1-K,
            'S_only_T':s.T,'max_T':combined.T,
            'K_only_status':'known' if K is not None else 'unknown',
            'S_only_status':s.status,'max_status':combined.status,
            'strongest':combined.strongest_factor,'interval':[combined.lower,combined.upper]}


def point_count_sweep(base_count: int, additions: range, u: float, b: float,
                      fixed_k: float) -> list[dict]:
    from .references import Reference, normalize
    ref = Reference('S','S:vehicle:near','specific',200,('a','b'),0,u,b,'points','supported')
    rows = []
    for addition in additions:
        if addition < 0:
            raise ValueError('sweep additions must be nonnegative')
        s = normalize(base_count+addition,ref)
        result = score('vehicle',fixed_k,s,region='gt_free:A')
        rows.append({'injected_points':addition,'region_count':base_count+addition,
                     'K':fixed_k,'S':s,'T':result.T,'strongest':result.strongest_factor})
    return rows


def score_clean_rows(raw_rows: list[dict], bundle: dict) -> list[dict]:
    """Score all illustrative clean sender/frame decisions; retain unsupported regions."""
    from collections import defaultdict
    from .references import select_reference, normalize
    from .scoring import spatial_penalty
    grouped = defaultdict(list)
    for row in raw_rows:
        grouped[(row['seed'], row['frame'])].append(row)
    decisions = []
    for (seed, frame), observations in sorted(grouped.items()):
        motion = next(r for r in observations if r['factor'] == 'K')
        k_ref, k_lineage = select_reference(bundle,'K','vehicle',motion['bin_id'])
        K = normalize(motion['value'],k_ref)
        spatial = {}
        ref_ids = []
        fallback = []
        for row in observations:
            if row['factor'] != 'S': continue
            ref, lineage = select_reference(bundle,'S','vehicle',row['bin_id'])
            spatial[row['region_id']] = (row['value'],ref)
            ref_ids.append(ref.context if ref else 'unsupported')
            if lineage == 'fallback': fallback.append(row['region_id'])
        S, region, spatial_reasons = spatial_penalty(spatial,('gt_free:A','gt_free:B','gt_free:C'))
        result = score('vehicle',K,S,region=region,reasons=spatial_reasons)
        decisions.append({'split_role':motion['split_role'],'clean':True,'seed':seed,
                          'segment':motion['segment'],'frame':frame,'deadline_ns':motion['deadline_ns'],
                          'track':'gt_free','raw_K_m':motion['value'],
                          'raw_A_points':spatial['gt_free:A'][0],
                          'raw_B_points':spatial['gt_free:B'][0],
                          'raw_C_points':spatial['gt_free:C'][0],
                          'K':K,'S':S,'A':None if result.T is None else 1-result.T,
                          'T':result.T,'status':result.status,'lower':result.lower,
                          'upper':result.upper,'strongest':result.strongest_factor,
                          'strongest_region':result.strongest_region,
                          'reason':';'.join(result.reasons),
                          'K_reference':k_ref.context if k_ref else 'unsupported',
                          'S_references':';'.join(ref_ids),'fallback_regions':';'.join(fallback)})
    return decisions


def hand_cases() -> list[dict]:
    cases = [
      ('S strongest','vehicle',.2,.7,'',.3),
      ('K strongest','vehicle',.8,.1,'',.2),
      ('kinematics missing','vehicle',None,.2,'KINEMATICS_MISSING',None),
      ('static S only','static_rsu',None,.2,'',.8),
      ('present empty valid','vehicle',.1,0,'VISIBILITY_UNKNOWN',.9),
      ('cloud absent','vehicle',.1,None,'CLOUD_ABSENT',None),
      ('count base 10','vehicle',.2,0,'',.8),
      ('count plus four','vehicle',.2,.5,'',.5),
      ('rearranged unchanged','vehicle',.2,.5,'COUNT_UNCHANGED',.5),
      ('no region','vehicle',.2,None,'NO_REGION',None),
      ('unsupported reference','vehicle',.2,None,'REFERENCE_UNSUPPORTED',None),
      ('tied factors','vehicle',.4,.4,'',.6),
    ]
    rows=[]
    for name,role,k,s,reason,expected in cases:
        result=score(role,k,s,reasons=(reason,) if reason else ())
        rows.append({'case':name,'sensor_role':role,'K':k,'S':s,'T':result.T,
                     'expected_T':expected,'pass':(result.T is None and expected is None) or
                     (result.T is not None and abs(result.T-expected)<1e-12),
                     'lower':result.lower,'upper':result.upper,'status':result.status,
                     'strongest':result.strongest_factor,'reasons':';'.join(result.reasons)})
    return rows


def _save_figure(fig, name, report_dir, provenance):
    from pathlib import Path
    from .provenance import output_stem, write_json_new, sha256_file
    stem=output_stem(name,provenance)
    paths=[report_dir/f'{stem}.{ext}' for ext in ('pdf','svg','png')]
    if any(p.exists() for p in paths): raise FileExistsError(stem)
    report_dir.mkdir(parents=True,exist_ok=True)
    for path in paths: fig.savefig(path,bbox_inches='tight')
    write_json_new(report_dir/f'{stem}.provenance.json',
                   {**provenance,'name':name,'outputs':{p.name:sha256_file(p) for p in paths}})
    return paths


def reference_notebook_outputs(root, run, config, provenance):
    """Compute and export S03 reference evidence; invoked by the source notebook."""
    from pathlib import Path
    import json
    from matplotlib.figure import Figure
    from .references import fit_references, reference_rows, select_reference
    from .provenance import export_table, write_json_new
    raw=clean_fixture_rows(config['reference_seeds'],'reference')
    fit=config['fitted_ranges']
    bundle=fit_references(raw,min_rows=fit['min_rows'],min_segments=fit['min_segments'],
                          allowed_seeds=set(config['reference_seeds']),pooled_compatible=fit['pooled_compatible'])
    write_json_new(run/'reference_bundle.json',{k:vars(v) for k,v in bundle.items()})
    write_json_new(run/'reference_raw.json',raw)
    support=[]
    for row in reference_rows(bundle):
        row={**row,'segments':';'.join(row['segments'])}
        selected,lineage=select_reference(bundle,row['factor'],'vehicle',row['context'].split(':')[-1]) if row['level']=='specific' else (None,'not_applicable')
        row['selected_context']=selected.context if selected else 'not_applicable'
        row['lineage']=lineage
        support.append({k:str(v) for k,v in row.items()})
    export_table(support,'T03_reference_support',root/'reports/tables',provenance)
    fig=Figure(figsize=(11,6),dpi=150)
    axes=fig.subplots(1,2)
    for ax,factor,unit in zip(axes,('K','S'),('m','points')):
        values=[r['value'] for r in raw if r['factor']==factor]
        ax.hist(values,bins=18 if factor=='K' else 14,color='#377c9c',alpha=.8)
        ax.set(xlabel=f'raw clean {factor} ({unit})',ylabel='observations',
               title=f'{factor}: n={len(values)}; illustrative reference seeds')
        ax.grid(alpha=.2)
    fig.suptitle('F03_clean_distributions — raw deterministic clean fixtures; no LiDAR replay')
    _save_figure(fig,'F03_clean_distributions',root/'reports/figures',provenance)
    summary={'raw_rows':len(raw),'contexts':len(bundle),'supported':sum(v.status=='supported' for v in bundle.values()),
             'zero_scale':[k for k,v in bundle.items() if v.status=='zero_scale'],
             'low_support':[k for k,v in bundle.items() if v.status=='low_support'],
             'unsupported_example':select_reference(bundle,'S','radar','near')[1],
             'range_rule':fit,'engineering_validity':config['engineering_validity'],
             'policy_parameters':config['future_policy_parameters']}
    write_json_new(run/'reference_summary.json',summary)
    return summary,support[:]


def score_notebook_outputs(root, run, config, provenance):
    """Score separate clean fixtures, calibrate, export hand and ablation evidence."""
    import json
    from matplotlib.figure import Figure
    from .references import Reference
    from .calibration import calibrate, alarm
    from .provenance import export_table, write_json_new
    data=json.loads((run/'reference_bundle.json').read_text())
    bundle={key:Reference(**value) for key,value in data.items()}
    calibration_rows=score_clean_rows(clean_fixture_rows(config['calibration_seeds'],'calibration'),bundle)
    test_rows=score_clean_rows(clean_fixture_rows(config['test_seeds'],'test'),bundle)
    cal=calibrate(calibration_rows,alpha=config['operating_calibration']['alpha'],
                  min_known=config['operating_calibration']['min_known'],
                  allowed_seeds=set(config['calibration_seeds']))
    write_json_new(run/'calibration.json',vars(cal))
    write_json_new(run/'calibration_decisions.json',calibration_rows)
    write_json_new(run/'test_decisions.json',test_rows)
    cases=hand_cases()
    if not all(r['pass'] for r in cases): raise AssertionError('hand score contract failed')
    comparison=[]
    for label,subset in [('calibration',calibration_rows),('test',test_rows)]:
        for mode in ('K_only','S_only','max'):
            known=0; alarms=0; strengths={'K':0,'S':0,'K+S':0,None:0}; values=[]
            for decision in subset:
                K,S=decision['K'],decision['S']
                value={'K_only':K,'S_only':S,'max':None if K is None or S is None else max(K,S)}[mode]
                if value is None: continue
                known+=1; values.append(value)
                alarms+=alarm(value,cal) is True
                strengths[decision['strongest']]+=1
            comparison.append({'population':label,'mode':mode,'all_decisions':len(subset),
                               'known':known,'unknown':len(subset)-known,
                               'known_fraction':known/len(subset),'common_support_n':sum(r['K'] is not None and r['S'] is not None for r in subset),
                               'mean_A_common_or_known':sum(values)/known if known else None,
                               'alarms_at_frozen_max_threshold':alarms,
                               'alarm_rate_known':alarms/known if known else None,
                               'strongest_K':strengths['K'] if mode=='max' else 'not_applicable',
                               'strongest_S':strengths['S'] if mode=='max' else 'not_applicable',
                               'strongest_tie':strengths['K+S'] if mode=='max' else 'not_applicable'})
    # All hand decisions remain in the denominator for every component ablation.
    for mode in ('K_only','S_only','max'):
        values=[]
        for case in cases:
            K,S=case['K'],case['S']
            value={'K_only':K,'S_only':S,'max':None if case['T'] is None else 1-case['T']}[mode]
            if value is not None: values.append(value)
        comparison.append({'population':'illustrative_hand_cases','mode':mode,'all_decisions':len(cases),
                           'known':len(values),'unknown':len(cases)-len(values),
                           'known_fraction':len(values)/len(cases),
                           'common_support_n':sum(r['K'] is not None and r['S'] is not None for r in cases),
                           'mean_A_common_or_known':sum(values)/len(values) if values else None,
                           'alarms_at_frozen_max_threshold':sum(alarm(v,cal) is True for v in values),
                           'alarm_rate_known':sum(alarm(v,cal) is True for v in values)/len(values) if values else None,
                           'strongest_K':sum(r['strongest']=='K' for r in cases) if mode=='max' else 'not_applicable',
                           'strongest_S':sum(r['strongest']=='S' for r in cases) if mode=='max' else 'not_applicable',
                           'strongest_tie':sum(r['strongest']=='K+S' for r in cases) if mode=='max' else 'not_applicable'})
    unknown=score('vehicle',None,.2,reasons=('KINEMATICS_MISSING',))
    export_table([{k:str(v) for k,v in row.items()} for row in comparison],
                 'T03_ablations',root/'reports/tables',provenance)
    export_table([{k:str(v) for k,v in row.items()} for row in cases],
                 'T03_hand_cases',root/'reports/tables',provenance)
    sweep=point_count_sweep(10,range(13),10,8,.2)
    write_json_new(run/'point_count_sweep.json',sweep)
    export_table([{k:str(v) for k,v in row.items()} for row in sweep],
                 'T03_point_count_sweep',root/'reports/tables',provenance)
    no_power_rows=[{'split_role':'calibration','clean':True,'seed':200+i%2,
                    'segment':f'no_power_fixture_{i%2}','status':'known','A':1.0} for i in range(200)]
    no_power=calibrate(no_power_rows,alpha=cal.alpha,min_known=200,allowed_seeds={200,201})
    fig=Figure(figsize=(12,8),dpi=150); axes=fig.subplots(2,2)
    for mode,color in [('K_only','#ad6b23'),('S_only','#3971a1'),('max','#8b3b76')]:
        vals=[{'K_only':r['K'],'S_only':r['S'],'max':r['A']}[mode] for r in test_rows]
        axes[0,0].hist([v for v in vals if v is not None],bins=12,alpha=.4,label=mode,color=color)
    axes[0,0].axvline(cal.threshold if cal.threshold is not None else 1,color='black',ls='--',label='frozen max c')
    axes[0,0].set(xlabel='anomaly A (dimensionless)',ylabel='decisions',title=f'Test common support n={len(test_rows)}')
    axes[0,0].set_xlim(-.02,1.02)
    axes[0,0].text(.55,.75,'All illustrative clean A=0',transform=axes[0,0].transAxes,fontsize=10)
    axes[0,0].legend(fontsize=8)
    axes[0,1].bar([r['mode'] for r in comparison[:3]],[r['alarm_rate_known'] or 0 for r in comparison[:3]],color=['#ad6b23','#3971a1','#8b3b76'])
    axes[0,1].axhline(cal.alpha,color='black',ls=':',label='target 1%')
    axes[0,1].set(ylabel='calibration alarms / known',title=f'Frozen c={cal.threshold}; strict >, ties quiet')
    axes[0,1].set_ylim(0,.025)
    axes[0,1].text(.02,.8,'Observed max FPR = 0/400\nA separate all-one fixture gives c=1, no power',
                   transform=axes[0,1].transAxes,fontsize=9)
    axes[0,1].legend(fontsize=8)
    identities={factor:sum(r['strongest']==factor for r in test_rows) for factor in ('K','S','K+S')}
    axes[1,0].bar(list(identities),list(identities.values()),color=['#ad6b23','#3971a1','#777777'])
    axes[1,0].set(ylabel='test decisions',title='Strongest anomaly identity; ties explicit')
    hand_known=sum(r['status']=='known' for r in cases)
    axes[1,1].bar(['clean test','hand cases'],[1,hand_known/len(cases)],color='#2d8a6a',label='known')
    axes[1,1].bar(['clean test','hand cases'],[0,1-hand_known/len(cases)],
                  bottom=[1,hand_known/len(cases)],color='#9a5b5b',label='unknown')
    axes[1,1].set(ylim=(0,1.1),ylabel='share of all decisions',
                  title=f'Strict unknown: test 0/{len(test_rows)}, hand {len(cases)-hand_known}/{len(cases)}')
    axes[1,1].legend(fontsize=8)
    fig.tight_layout()
    _save_figure(fig,'F03_threshold_ablation',root/'reports/figures',provenance)
    fig2=Figure(figsize=(8,5),dpi=150); ax=fig2.subplots()
    ax.plot([r['injected_points'] for r in sweep],[r['T'] for r in sweep],marker='o',label='T=1-max(K,S)')
    ax.plot([r['injected_points'] for r in sweep],[r['S'] for r in sweep],marker='x',label='S')
    ax.set(xlabel='literal points added in fixed region A',ylabel='dimensionless score / penalty',ylim=(-.03,1.03),
           title='F03_trust_point_count — illustrative fixture, K=.2, u=10, b=8')
    ax.legend(); ax.grid(alpha=.2)
    _save_figure(fig2,'F03_trust_point_count',root/'reports/figures',provenance)
    grouped={}
    for row in calibration_rows:
        grouped.setdefault(row['segment'],[]).append(row)
    group_rates={segment:sum(alarm(r['A'],cal) is True for r in rows)/max(1,sum(r['status']=='known' for r in rows))
                 for segment,rows in grouped.items()}
    summary={'calibration':vars(cal),'no_power_negative_fixture':vars(no_power),'calibration_group_rates':group_rates,
             'test_decisions':len(test_rows),'test_known':sum(r['status']=='known' for r in test_rows),
             'test_unknown':sum(r['status']=='unknown' for r in test_rows),
             'test_clean_alarm_rate_known':sum(alarm(r['A'],cal) is True for r in test_rows)/max(1,sum(r['status']=='known' for r in test_rows)),
             'hand_cases_passed':len(cases),'unknown_fixture_interval':[unknown.lower,unknown.upper],
             'strongest_identity':identities,
             'sweep_nonincreasing':all(a['T']>=b['T'] for a,b in zip(sweep,sweep[1:])),
             'limitations':'Deterministic illustrative clean fixtures; no empirical sensor calibration or attack power. Wilson interval ignores frame clustering; group rates expose variation.'}
    write_json_new(run/'score_summary.json',summary)
    return summary,comparison,cases,sweep
