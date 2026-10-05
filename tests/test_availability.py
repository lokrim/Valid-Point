"""Freshness, health, transform and membership are independent of intent."""
from dataclasses import replace
from pathlib import Path

import pytest

from valid_point.contracts import EvidenceStatus as S
from valid_point.evidence import cloud_fixture, fixed_regions, load_raw_config
from valid_point.evidence.availability import measure_availability
from valid_point.evidence.spatial import count_regions

CONFIG=load_raw_config(Path(__file__).resolve().parents[1]/'configs/raw_evidence.json')


def fixture(**kw):
    return cloud_fixture(CONFIG,dict(case='test',**kw))


def measure(row,cloud,context):
    return measure_availability(row,cloud,context,max_cloud_age_ns=200000000)


def test_deadline_age_and_exact_freshness_boundary():
    r=measure(*fixture(source_ns=1350000000))
    assert r.freshness.value==.2 and r.eligible.status==S.KNOWN
    assert measure(*fixture(source_ns=1349999999)).payload.reason=='STALE'


def test_receipt_at_deadline_is_causal_one_ns_after_is_late_contract():
    row,cloud,context=fixture()
    assert measure(replace(row,arrival_ns=row.key.deadline_ns),cloud,context).payload.status==S.KNOWN
    with pytest.raises(ValueError):
        replace(row,arrival_ns=row.key.deadline_ns+1)


def test_absent_empty_malformed_late_distinct():
    assert measure(*fixture(points=[])).message_state=='present_empty'
    assert measure(*fixture(points=[])).payload.status==S.KNOWN
    for state,reason in [('absent','CLOUD_ABSENT'),('malformed','MALFORMED'),('late','LATE')]:
        r=measure(*fixture(state=state))
        assert r.message_state==state and r.payload.reason==reason
        assert r.eligible.status!=S.KNOWN


def test_health_independent_of_content_counts_and_freshness():
    row,cloud,context=fixture(health='unknown')
    r=measure(row,cloud,context)
    assert r.freshness.value==.05 and r.payload.status==S.KNOWN and r.transform.status==S.KNOWN
    assert r.health.status==S.UNKNOWN and r.eligible.status==S.UNKNOWN
    assert count_regions(row,cloud,fixed_regions(CONFIG),context,max_cloud_age_ns=200000000).counts[0].value==1
    assert measure(*fixture(health='fault')).health.status==S.INVALID
    assert measure(*fixture(points=[])).health==measure(*fixture(points=[[1,1,0,1]]*100)).health


def test_transform_missing_late_expired_units_and_frame():
    row,cloud,context=fixture()
    for modified,reason in [(replace(context,transform=None),'TRANSFORM_UNAVAILABLE'),
                           (replace(context,transform_available_ns=row.key.deadline_ns+1),'TRANSFORM_UNAVAILABLE'),
                           (replace(context,transform=replace(context.transform,valid_until_ns=row.source_ns-1)),'TRANSFORM_INVALID'),
                           (replace(context,transform=replace(context.transform,units='cm')),'TRANSFORM_UNSUPPORTED'),
                           (replace(context,transform=replace(context.transform,source_frame='other')),'TRANSFORM_UNSUPPORTED')]:
        r=measure(row,cloud,modified)
        assert r.transform.reason==reason and r.freshness.status==S.KNOWN


def test_unverified_clock_membership_and_future_context_unknown():
    assert measure(*fixture(clock_verified=False)).freshness.value is None
    assert measure(*fixture(membership_verified=False)).membership.status==S.UNKNOWN
    r=measure(*fixture(context_available_ns=1600000000))
    assert r.health.status==r.transform.status==r.membership.status==r.freshness.status==S.UNKNOWN


def test_missing_source_count_mismatch_future_source_and_reversed_clock():
    row,cloud,context=fixture()
    assert measure(replace(row,source_ns=None),cloud,context).payload.reason=='SOURCE_TIME_MISSING'
    assert measure(replace(row,point_count=2),cloud,context).payload.reason=='COUNT_MISMATCH'
    assert measure(replace(row,source_ns=row.anchor_ns+1),cloud,context).payload.reason=='FUTURE_SAMPLE'
    assert measure(replace(row,arrival_ns=row.source_ns-1),cloud,context).payload.reason=='ARRIVAL_BEFORE_SOURCE'


def test_late_packet_metadata_cannot_supply_freshness_or_transform_time():
    row,cloud,context=fixture(state='late')
    r=measure(row,cloud,context)
    assert r.freshness.value is None and r.freshness.status==S.UNKNOWN
    assert r.transform.reason=='TRANSFORM_TIME_UNKNOWN'
    assert r.health.status==S.KNOWN  # independent receiver context remains available
    with pytest.raises(ValueError):
        replace(context,clock_verified='unknown')
