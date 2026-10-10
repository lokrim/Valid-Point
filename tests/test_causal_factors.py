import numpy as np
from valid_point.evidence.density import CELL_IDS, count_cells, occupancy_change
from valid_point.evidence.temporal_geometry import directed_novelty


def test_half_open_cells_and_full_coverage():
    xyz=np.array([[0,0,0],[9.999,0,2],[10,0,0],[0,25,0],[-80,0,0],[81,0,0]],float)
    d=count_cells(xyz,origin_xy_m=(0,0),origin_id="sensor",valid_origin=True)
    assert len(CELL_IDS)==len(d.counts)==32
    assert d.counts[0]==2 and d.counts[8]==1 and d.counts[2*8+2]==1
    assert sum(d.counts)==4 and d.excluded_points==2
    empty=count_cells(np.empty((0,3)),origin_xy_m=(0,0),origin_id="sensor",valid_origin=True)
    assert empty.status=="known" and empty.counts==(0,)*32
    assert sum(occupancy_change(empty,d))==-3
    assert count_cells(xyz,origin_xy_m=None,origin_id=None,valid_origin=False).counts is None


def test_static_translation_and_moving_confounder():
    grid=np.array([(x*.8,y*.8,z*.8) for x in range(12) for y in range(12) for z in range(2)],float)
    p=np.eye(4); p[0,3]=1
    current=grid.copy(); current[:,0]-=1
    kw=dict(current_origin_xy=(0,0),previous_origin_xy=(0,0),map_from_current=p,
            map_from_previous=np.eye(4),gap_s=.1,previous_cloud_id="old",
            current_pose_id="newpose",previous_pose_id="oldpose")
    result=directed_novelty(current,grid,**kw)
    assert result.status=="known" and result.distance_m<1e-10
    moved=current.copy(); moved[::2,1]+=4
    confounded=directed_novelty(moved,grid,**kw)
    assert confounded.status=="known" and confounded.distance_m>result.distance_m
    invalid=p.copy(); invalid[0,0]=2
    assert directed_novelty(current,grid,**{**kw,"map_from_current":invalid}).distance_m is None
    assert directed_novelty(current,grid,**{**kw,"gap_s":.6}).distance_m is None
    assert directed_novelty(current[:2],grid,**kw).reason=="INSUFFICIENT_VOXEL_SUPPORT"
