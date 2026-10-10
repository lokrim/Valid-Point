import math
import pytest

from valid_point.temporal import TemporalEWMA
from valid_point.evidence.temporal_geometry import _directed_distances
from valid_point.development_scores import AlarmDecision
import numpy as np


def put(state,t,a,**kwargs):
    return state.update(episode=kwargs.get("episode","e"),principal=kwargs.get("principal","003"),
                        sensor=kwargs.get("sensor","003"),method_arm=kwargs.get("arm","D-only"),
                        reference_version=kwargs.get("version","v1"),source_ns=round(t*1e9),A=a,
                        reason="MISSING" if a is None else "VALID")


def test_irregular_recurrence_and_boundedness():
    state=TemporalEWMA(tau_s=1,g_reset_s=3,min_updates=1)
    assert put(state,0,0).Z==0
    r=put(state,.3,1)
    assert r.Z==pytest.approx(1-math.exp(-.3))
    r=put(state,1.1,.5)
    expected=math.exp(-.8)*(1-math.exp(-.3))+(1-math.exp(-.8))*.5
    assert r.Z==pytest.approx(expected) and 0<=r.Z<=1


def test_initialization_warmup_missing_hold_short_and_long_gap():
    state=TemporalEWMA(tau_s=.1,g_reset_s=.5,min_updates=4)
    first=put(state,0,.8)
    assert first.Z==.8 and not first.ready and first.reason=="WARM_UP"
    put(state,.1,.8); missing=put(state,.2,None)
    assert missing.Z is None and missing.C_time is None and missing.held_Z==pytest.approx(.8)
    assert missing.held_age_s==pytest.approx(.1)
    short=put(state,.3,.2)
    assert short.eligible_updates==3 and not short.reset
    ready=put(state,.4,.2)
    assert ready.ready and ready.eligible_updates==4
    long=put(state,1.1,.4)
    assert long.reset and long.Z==.4 and not long.ready and long.eligible_updates==1


def test_duplicate_reverse_no_mutation_checkpoint_resume():
    s=TemporalEWMA(.2,.5)
    put(s,0,.2); put(s,.1,.8)
    checkpoint=s.checkpoint()
    assert put(s,.1,1).reason=="DUPLICATE_TIME"
    assert put(s,.05,1).reason=="REVERSED_TIME"
    assert s.checkpoint()==checkpoint
    resumed=TemporalEWMA.resume(checkpoint)
    assert put(s,.2,.4)==put(resumed,.2,.4)
    assert s.checkpoint()==resumed.checkpoint()


def test_no_cross_agent_arm_episode_or_reference_and_prefix():
    s=TemporalEWMA(.1,.5,min_updates=1)
    base=put(s,0,.9)
    assert put(s,0,.1,principal="004").Z==.1
    assert put(s,0,.2,arm="G-only").Z==.2
    assert put(s,0,.3,episode="other").Z==.3
    assert put(s,.1,.4,version="v2").Z==.4
    assert all(x['key'][-1]!='v1' for x in s.checkpoint()['states'] if x['key'][:4]==['e','003','003','D-only'])
    a=TemporalEWMA(.1,.5,min_updates=1); b=TemporalEWMA(.1,.5,min_updates=1)
    prefix=[(0,.2),(.1,.4),(.3,.8)]
    one=[put(a,t,v) for t,v in prefix]
    two=[put(b,t,v) for t,v in prefix]
    put(a,.4,1); put(b,.4,0)
    assert one==two and base.Z==.9


def test_deterministic_geometry_work_exhaustion_is_unknown():
    points=np.array([[.1,.1,.1],[.2,.2,.2],[.3,.3,.3]])
    distances, reason=_directed_distances(points,points,max_pair_evaluations=1)
    assert distances is None and reason=="NEIGHBOR_WORK_BUDGET"


def test_constant_dense_and_sparse_updates_share_elapsed_time_result():
    sparse=TemporalEWMA(1.,g_reset_s=2,min_updates=1)
    dense=TemporalEWMA(1.,g_reset_s=2,min_updates=1)
    put(sparse,0,.2); put(dense,0,.2)
    expected=put(sparse,1,.8).Z
    for t in (.25,.5,.75,1.): actual=put(dense,t,.8).Z
    assert actual==pytest.approx(expected)


def test_uncalibrated_alarm_is_a_distinct_unknown_record():
    alarm=AlarmDecision('cloud','003','003',100_000_000,'D-only','unknown',None,None,None,
                        'DIAGNOSTIC_CALIBRATION_UNAVAILABLE','reference-v1')
    assert alarm.instant_alarm is None and alarm.temporal_alarm is None
    assert alarm.status=='unknown' and alarm.threshold_id is None
