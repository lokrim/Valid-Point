from dataclasses import replace
from io import BytesIO
from pathlib import Path
import json
import numpy as np
import pytest
from valid_point.replay import AllowedSource, CloudEvent, PoseEvent, ReplayConfig, replay
from valid_point.io.mixed_signals import STREAM_PRINCIPAL


def fixture(tmp_path):
    clouds=tmp_path/"PointClouds"; clouds.mkdir()
    poses=tmp_path/"Odometry"; poses.mkdir()
    xyz=np.array([(x,y,0) for x in range(12) for y in range(12)],float)
    events=[]
    for k in range(3):
        name=f"003_{k}_1.{k*100000000:09d}.pcd"
        path=clouds/name
        lines=["VERSION .7","FIELDS x y z intensity","SIZE 4 4 4 4","TYPE F F F F","COUNT 1 1 1 1",f"WIDTH {len(xyz)}","HEIGHT 1",f"POINTS {len(xyz)}","DATA ascii"]
        path.write_text("\n".join(lines)+"\n"+"\n".join(f"{x} {y} {z} 1" for x,y,z in xyz)+"\n")
        ns=1_000_000_000+k*100_000_000
        events.append(CloudEvent(name,"003","003",k,ns,ns,ns,path))
    mat=np.eye(4)
    pose=[PoseEvent(f"pose{k}","003",e.source_ns,e.source_ns,mat,True) for k,e in enumerate(events)]
    return AllowedSource(clouds,poses),events,pose


def test_actual_entrypoint_causality_and_unknowns(tmp_path):
    source,events,pose=fixture(tmp_path)
    cfg=ReplayConfig(min_voxels=100)
    result=replay(events,source,config=cfg,poses={"003":pose})
    assert [r.pose_id for r in result]==[f"pose{k}" for k in range(3)]
    assert result[0].geometry.reason=="NO_CAUSAL_HISTORY"
    assert all(r.density.status=="known" and len(r.density.counts)==32 for r in result)
    assert result[1].geometry.previous_cloud_id==events[0].cloud_id
    assert result[1].geometry.status=="known"
    late=replace(events[1],arrival_ns=events[1].deadline_ns+1)
    assert replay([late],source,config=cfg,poses={"003":pose})[0].density.counts is None
    future=replace(events[1],source_ns=events[1].deadline_ns+1)
    assert replay([future],source,config=cfg,poses={"003":pose})[0].geometry.distance_m is None
    stale=replay([events[1]],source,config=cfg,poses={"003":[pose[0]]})[0]
    assert stale.pose_id=="pose0"  # 100 ms past remains causal
    too_stale=replay([events[2]],source,config=cfg,poses={"003":[pose[0]]})[0]
    assert too_stale.pose_id is None and too_stale.density.status=="known" and too_stale.geometry.distance_m is None
    future_pose=replay([events[0]],source,config=cfg,poses={"003":[pose[1]]})[0]
    assert future_pose.pose_id is None and future_pose.geometry.distance_m is None
    bad=replace(pose[0],matrix=np.diag([2,1,1,1]),valid=False)
    assert replay([events[0]],source,config=cfg,poses={"003":[bad]})[0].geometry.distance_m is None
    nonrigid=replace(pose[1],matrix=np.diag([2,1,1,1]),valid=True)
    broken=replay(events[:2],source,config=cfg,poses={"003":[pose[0],nonrigid]})[1]
    assert broken.density.status=="known" and broken.geometry.reason=="INVALID_TRANSFORM"
    absent=replace(events[0],path=None,state="absent")
    assert replay([absent],source,config=cfg,poses={"003":pose})[0].density.counts is None


def test_present_empty_and_future_prefix(tmp_path):
    source,events,pose=fixture(tmp_path)
    empty=source.clouds_dir/events[2].cloud_id
    empty.write_text("VERSION .7\nFIELDS x y z intensity\nSIZE 4 4 4 4\nTYPE F F F F\nCOUNT 1 1 1 1\nWIDTH 0\nHEIGHT 1\nPOINTS 0\nDATA ascii\n")
    baseline=replay(events,source,poses={"003":pose})
    assert baseline[2].density.counts==(0,)*32
    # Change only a later event and its pose: every earlier record is identical,
    # including selected IDs, raw cells, history, and source hashes.
    empty.write_text(empty.read_text()+"\n")
    changed=replay(events,source,poses={"003":pose[:2]+[replace(pose[2],valid=False)]})
    assert [r.as_dict() for r in baseline[:2]]==[r.as_dict() for r in changed[:2]]


def test_forbidden_evaluator_isolation_and_positive_control(tmp_path,monkeypatch):
    source,events,pose=fixture(tmp_path)
    forbidden=tmp_path/"evaluator"; forbidden.mkdir()
    for name in ("labels.txt","boxes.json","masks.bin","schedules.json","clean_counterpart.pcd","outcomes.json"):
        (forbidden/name).write_text("version 1")
    original_read=Path.read_bytes
    original_open=Path.open
    def guarded_read(path,*args,**kwargs):
        if forbidden in path.parents: raise AssertionError("forbidden evaluator read")
        return original_read(path,*args,**kwargs)
    def guarded_open(path,*args,**kwargs):
        if forbidden in path.parents and not str(kwargs.get("mode",args[0] if args else "r")).startswith(("w","a","x")):
            raise AssertionError("forbidden evaluator read")
        return original_open(path,*args,**kwargs)
    monkeypatch.setattr(Path,"read_bytes",guarded_read)
    monkeypatch.setattr(Path,"open",guarded_open)
    first=replay(events,source,poses={"003":pose})
    log1=tuple(source.access_log)
    for path in forbidden.iterdir():
        # Write is allowed; any read by the operational path is trapped.
        path.write_text("version 2")
    source.access_log.clear()
    second=replay(events,source,poses={"003":pose})
    assert [r.as_dict() for r in first]==[r.as_dict() for r in second]
    assert log1==tuple(source.access_log)
    with pytest.raises(AssertionError,match="forbidden evaluator read"):
        (forbidden/"labels.txt").read_bytes()  # deliberate failing positive control


def test_static_native_frame_and_invalid_origin(tmp_path):
    from valid_point.replay import _frame
    top_map,top_origin,_=_frame("top",None)
    assert np.array_equal(top_map,np.eye(4)) and top_origin==(-41.551,-51.878)
    source,events,pose=fixture(tmp_path)
    top_name="top_0_1.000000000.pcd"
    top_path=source.clouds_dir/top_name
    top_path.write_bytes((source.clouds_dir/events[0].cloud_id).read_bytes())
    top=CloudEvent(top_name,"top",STREAM_PRINCIPAL["top"],0,1_000_000_000,1_000_000_000,1_000_000_000,top_path)
    record=replay([top],source,poses={})[0]
    assert record.pose_id is None and record.density.status=="known"
    assert record.density.origin_id=="top:published_map_origin"
    blocked=replay([top],source,config=ReplayConfig(validated_origins=()),poses={})[0]
    assert blocked.density.counts is None and blocked.geometry.distance_m is None


def test_wrapper_zero_support_and_every_required_cell(tmp_path):
    from valid_point.operational import DCellReference, measure_operational
    from valid_point.evidence.density import CELL_IDS
    source,events,pose=fixture(tmp_path)
    refs=tuple(DCellReference(c,0.,1.,0,0,"fixture") for c in CELL_IDS)
    record=measure_operational([events[0]],source,poses={"003":pose},reference=refs)[0]
    assert record.raw.density.status=="known" and record.d_anomaly is None
    assert record.d_reason=="ZERO_OR_INSUFFICIENT_REFERENCE_SUPPORT"
    missing=measure_operational([events[0]],source,poses={"003":pose},reference=refs[:-1])[0]
    assert missing.d_reason=="REQUIRED_CELL_COVERAGE" and missing.d_anomaly is None
    good=tuple(DCellReference(c,0.,1.,200,2,"fixture") for c in CELL_IDS)
    normalized=measure_operational([events[0]],source,poses={"003":pose},reference=good)[0]
    assert normalized.d_status=="known" and normalized.d_anomaly==1.


def test_overlap_diagnostic_never_selects_future_top(tmp_path):
    from scripts.inspect_causal_factors import overlap_diagnostic
    source,events,pose=fixture(tmp_path)
    top_path=source.clouds_dir/'top_0_1.050000000.pcd'
    top_path.write_bytes((source.clouds_dir/events[0].cloud_id).read_bytes())
    top=CloudEvent(top_path.name,'top','RSU',0,1_050_000_000,1_050_000_000,1_050_000_000,top_path)
    rows=overlap_diagnostic(source,[events[0],top],{'003':pose,'004':[],'laser':[]},tmp_path)
    assert len(rows)==1 and rows[0]['reason']=='NO_CAUSAL_TOP'
    assert rows[0]['top_id'] is None and source.access_log==[]
