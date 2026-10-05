"""Exact half-open geometry, literal additions, unknown states and namespaces."""
from dataclasses import replace
from pathlib import Path

import pytest

from valid_point.contracts import EvidenceStatus as S
from valid_point.evidence import cloud_fixture, fixed_regions, load_raw_config
from valid_point.evidence.spatial import FixedRegion, RegionSet, count_regions
from valid_point.io.pointcloud import PointCloud

CONFIG=load_raw_config(Path(__file__).resolve().parents[1]/'configs/raw_evidence.json')


def counts(points, **kw):
    row, cloud, context=cloud_fixture(CONFIG,dict(case='test',points=points,**kw))
    return count_regions(row,cloud,fixed_regions(CONFIG),context,max_cloud_age_ns=CONFIG['max_cloud_age_ns'])


def test_hand_counts_boundaries_and_volume():
    r=counts([[0,0,-1,1],[5,0,0,1],[0,5,0,1],[10,0,0,1],
              [1,1,1,1],[-.001,0,0,1],[4.999,4.999,.999,1]])
    assert [m.value for m in r.counts]==[2,1,1]
    assert r.outside_regions.value==3
    assert all(m.unit=='points' for m in r.counts)
    assert fixed_regions(CONFIG).regions[0].volume_m3==50


def test_literal_added_points_are_monotone_per_region_without_share_reward():
    base=[[1,1,0,1],[6,1,0,1]]
    r0=counts(base)
    r1=counts(base+[[1,1,0,1],[2,2,0,1],[6,2,0,1]])
    r2=counts(base+[[1,1,0,1],[2,2,0,1],[6,2,0,1],[50,50,0,1]])
    assert [m.value for m in r0.counts]==[1,1,0]
    assert [m.value for m in r1.counts]==[3,2,0]
    assert [m.value for m in r2.counts]==[3,2,0]
    assert all(a.value<=b.value for a,b in zip(r0.counts,r1.counts))
    assert r2.outside_regions.value==1


def test_empty_absent_and_unknown_visibility_are_distinct():
    empty=counts([])
    absent=counts(None,state='absent')
    assert [m.value for m in empty.counts]==[0,0,0]
    assert all(m.value is None for m in absent.counts)
    assert absent.reason=='CLOUD_ABSENT'
    assert empty.visibility=='unknown' and empty.deficit_inference.startswith('unknown')


def test_dense_legitimate_rearrangement_and_removal_limits():
    base=[[1,1,0,1],[2,2,0,1]]
    assert counts(base).counts[0].value==counts([[3,3,0,1],[4,4,0,1]]).counts[0].value
    assert counts(base[:1]).counts[0].value==1
    assert counts(base*10).counts[0].value==20


@pytest.mark.parametrize('kw,reason',[
    ({'state':'late'},'LATE'),({'state':'malformed'},'MALFORMED'),
    ({'transform':'unsupported'},'TRANSFORM_UNSUPPORTED'),
    ({'transform':'expired'},'TRANSFORM_INVALID'),({'clock_verified':False},'CLOCK_UNVERIFIED')])
def test_unavailable_counts_null(kw,reason):
    r=counts([[1,1,0,1]],**kw)
    assert all(m.value is None for m in r.counts) and r.reason==reason


def test_causal_frozen_regions_no_region_and_separate_namespaces():
    row,cloud,context=cloud_fixture(CONFIG,{'case':'test'})
    regions=fixed_regions(CONFIG)
    for modified,reason in [(replace(regions,regions=()),'NO_REGION'),
                            (replace(regions,frozen_ns=CONFIG['anchor_ns']+1),'REGIONS_NOT_CAUSALLY_FROZEN')]:
        assert count_regions(row,cloud,modified,context,max_cloud_age_ns=200000000).reason==reason
    with pytest.raises(ValueError):
        replace(regions,authority='evaluator')
    oracle=RegionSet((FixedRegion('oracle_box:box',(0,0,-1),(5,5,1)),),
                     'oracle_box','evaluator','explicit evaluator-only fixture',0)
    assert count_regions(row,cloud,oracle,context,max_cloud_age_ns=200000000).track=='oracle_box'


def test_supported_translation_and_receiver_frame_not_sender_geometry():
    row,cloud,context=cloud_fixture(CONFIG,{'case':'translated','points':[[0,0,0,1]]})
    transform=replace(context.transform,matrix=((1,0,0,5),(0,1,0,0),(0,0,1,0),(0,0,0,1)))
    r=count_regions(row,cloud,fixed_regions(CONFIG),replace(context,transform=transform),max_cloud_age_ns=200000000)
    assert [m.value for m in r.counts]==[0,1,0]


def test_malformed_cloud_fields_rejected_before_measurement():
    for points,fields in [(((1,2,3),),('x_m','y_m','z_m','intensity')),
                         (((1,2,float('nan'),1),),('x_m','y_m','z_m','intensity')),
                         ((),('x','y','z'))]:
        with pytest.raises(ValueError):
            PointCloud('sensor',points,fields)
