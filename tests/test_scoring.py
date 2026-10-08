import pytest
from valid_point.scoring import score, spatial_penalty, spatial_diagnostic
from valid_point.references import Reference
from valid_point.ablations import point_count_sweep


def test_hand_contract_and_strict_unknowns():
    assert (score('vehicle',.2,.7).T,score('vehicle',.2,.7).strongest_factor) == (.30000000000000004,'S')
    assert score('vehicle',.8,.1).strongest_factor == 'K'
    missing=score('vehicle',None,.2,reasons=('KINEMATICS_MISSING',))
    assert missing.T is None and missing.lower == 0 and missing.upper == .8
    static=score('static_rsu',None,.2)
    assert static.T == .8 and 'NOT_APPLICABLE_STATIC' in static.reasons
    assert score('vehicle',.1,0).T == .9
    absent=score('vehicle',.1,None,reasons=('CLOUD_ABSENT',))
    assert absent.T is None and absent.upper == .9
    assert score('vehicle',.4,.4).strongest_factor == 'K+S'
    assert score('vehicle',None,None).upper == 1
    with pytest.raises(ValueError):
        score('vehicle',1.01,0)


def test_fixed_region_full_coverage_and_monotonic_addition():
    ref=Reference('S','S:vehicle:near','specific',200,('a','b'),4,10,8,'points','supported')
    s,region,reasons=spatial_penalty({'A':(10,ref),'B':(0,ref)},('A','B'))
    assert s == 0 and not reasons
    partial=spatial_penalty({'A':(14,ref)},('A','B'))
    assert partial[0] is None and 'SCORE_PARTIAL' in partial[2]
    details=spatial_diagnostic({'A':(14,ref)},('A','B'))
    assert details['S'] is None and details['partial_max']==.5 and not details['coverage_known']
    sweep=point_count_sweep(10,range(12),10,8,.2)
    assert sweep[0]['T'] == .8 and sweep[4]['T'] == .5
    assert all(a['T'] >= b['T'] for a,b in zip(sweep,sweep[1:]))
    assert sweep[-1]['T'] == 0
