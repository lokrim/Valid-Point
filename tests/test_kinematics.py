"""Hand calculations and causal selection; no fitted scale or penalty."""
from dataclasses import replace

import numpy as np
import pytest

from valid_point.contracts import DecisionKey, EvidenceStatus as S
from valid_point.evidence.kinematics import MotionSample, measure_motion

KEY = DecisionKey('hand', 'vehicle', 1, 1_550_000_000)
I = ((1,0,0),(0,1,0),(0,0,1))
A = MotionSample('a',1_000_000_000,1_010_000_000,(0,0,0),(2,0,0),I)
B = MotionSample('b',1_500_000_000,1_510_000_000,(1,0,0),(3,0,0),I)


def measure(samples=(A,B), **kw):
    return measure_motion(KEY, samples, anchor_ns=1_500_000_000,max_age_ns=1_000_000_000,
                          min_dt_s=.01,max_dt_s=1,**kw)


def test_hand_residual_vector_norm_actual_dt_and_prior_velocity():
    r = measure((A,replace(B,position=(4,4,0),velocity=(999,0,0))))
    assert r.dt_s == .5
    assert r.displacement_m == (4,4,0)
    assert r.predicted_displacement_m == (1,0,0)
    assert r.residual_vector_m == (3,4,0)
    assert r.residual.value == 5 and r.residual.unit == 'm'
    assert r.residual.available_ns == B.available_ns


def test_acceleration_and_consistent_spoof_are_identifiability_limits():
    assert measure((A,replace(B,position=(1.25,0,0)))).residual.value == .25
    spoof = (replace(A,position=(100,0,0),velocity=(6,0,0)),replace(B,position=(103,0,0)))
    assert measure(spoof).residual.value == measure().residual.value == 0


def test_body_rotation_and_explicit_receiver_velocity():
    quarter_turn = ((0,-1,0),(1,0,0),(0,0,1))
    assert measure((replace(A,rotation=quarter_turn),replace(B,position=(0,1,0)))).residual.value == 0
    assert measure((replace(A,velocity_frame='receiver',rotation=None),B)).residual.value == 0


def test_latest_causal_pair_ignores_future_late_stale_and_order():
    future = replace(B,sample_id='future',source_ns=1_600_000_000,available_ns=1_601_000_000,position=(999,0,0))
    late = replace(B,sample_id='late',source_ns=1_400_000_000,available_ns=1_551_000_000,position=(999,0,0))
    stale = replace(A,sample_id='stale',source_ns=0,available_ns=1)
    r = measure((future,B,stale,late,A))
    assert r.selected_ids == ('a','b') and r.residual.value == 0
    assert dict(r.excluded) == {'future':'FUTURE_SAMPLE','late':'LATE','stale':'STALE_SAMPLE'}


def test_missing_selected_velocity_never_falls_back_or_becomes_zero():
    older = replace(A,sample_id='older',source_ns=750_000_000)
    r = measure((older,replace(A,velocity=None),B))
    assert r.selected_ids == ('a','b')
    assert r.residual.status == S.UNKNOWN and r.residual.value is None
    assert r.residual.reason == 'VELOCITY_MISSING'


@pytest.mark.parametrize('change,reason',[
    ({'position':None},'POSITION_MISSING'),({'rotation':None},'ORIENTATION_MISSING'),
    ({'velocity_unit':'km/h'},'UNSUPPORTED_VELOCITY_CONVENTION'),
    ({'position_unit':'cm'},'UNSUPPORTED_POSITION_CONVENTION'),
    ({'position_frame':'world'},'UNSUPPORTED_POSITION_CONVENTION'),
    ({'velocity':(np.nan,0,0)},'MALFORMED_MOTION_VECTOR'),
    ({'position':(1,2)},'MALFORMED_MOTION_VECTOR'),
    ({'rotation':((2,0,0),(0,1,0),(0,0,1))},'ORIENTATION_INVALID'),
    ({'rotation':((-1,0,0),(0,1,0),(0,0,1))},'ORIENTATION_INVALID'),
])
def test_missing_malformed_and_units_are_not_measurements(change,reason):
    r = measure((replace(A,**change),B))
    assert r.residual.value is None and r.residual.reason == reason


@pytest.mark.parametrize('source_ns',[1_500_000_000,1_499_000_000])
def test_zero_or_below_minimum_dt_invalid(source_ns):
    r=measure((replace(A,source_ns=source_ns,available_ns=1_510_000_000),B))
    assert r.residual.status == S.INVALID and r.residual.reason == 'INVALID_DT'


def test_large_gap_invalid_and_stale_missing_unknown():
    r=measure_motion(KEY,(replace(A,source_ns=0),B),anchor_ns=1_500_000_000,
                     max_age_ns=2_000_000_000,min_dt_s=.01,max_dt_s=1)
    assert r.residual.reason == 'INVALID_DT'
    assert measure((replace(A,source_ns=0),B)).residual.status == S.UNKNOWN
    assert measure(sensor_role='static_rsu').residual.status == S.NOT_APPLICABLE
    assert measure(clock_verified=False).residual.reason == 'CLOCK_UNVERIFIED'


def test_bad_clock_and_duplicate_samples_rejected():
    assert measure((replace(A,available_ns=0),B)).residual.reason == 'MALFORMED_SAMPLE_CLOCK'
    assert measure((A,A)).residual.reason == 'DUPLICATE_SAMPLE_ID'
