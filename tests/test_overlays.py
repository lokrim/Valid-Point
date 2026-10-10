from io import BytesIO
import numpy as np
import pytest

from valid_point.attacks.overlays import apply_overlay, cell_index, freeze_target, seed_key, selected_ids
from valid_point.io.mixed_signals import read_pcd, write_pcd


def cloud(n=1000):
    x=np.linspace(12,20,n,dtype=np.float32)
    return np.column_stack((x,np.ones(n,dtype=np.float32),np.zeros(n,dtype=np.float32),
                            np.arange(n,dtype=np.float32))).astype(np.float32)


def key(family,severity): return seed_key("mini_7","003","003_1_1.1.pcd",family,severity)


def test_row_counts_and_retained_fields():
    values=cloud()
    removed=apply_overlay(values,family="random_removal",severity=.3,key=key("random_removal",.3))
    assert len(removed.values)==700 and len(removed.changed_ids)==300
    assert np.array_equal(removed.values[:,3],np.delete(values[:,3],removed.selected_ids))
    added=apply_overlay(values,family="addition",severity=.05,key=key("addition",.05),
                        target=freeze_target([("prefix",values)]))
    assert len(added.values)==1050 and np.array_equal(added.values[:1000],values)
    displaced=apply_overlay(values,family="displacement",severity=1,key=key("displacement",1))
    assert len(displaced.values)==1000 and len(displaced.selected_ids)==250
    assert np.array_equal(displaced.values[:,1:],values[:,1:])


def test_rearrangement_preserves_each_cell_count_and_failure_ids():
    values=cloud()
    values[:100,0]=100  # Outside the frozen D crop has no original D cell.
    moved=apply_overlay(values,family="rearrangement",severity=1.,key=key("rearrangement",1.))
    assert len(moved.values)==len(values)
    original_cells=cell_index(values[:,:3],(0,0))
    moved_cells=cell_index(moved.values[:,:3],(0,0))
    assert np.array_equal(np.bincount(original_cells[original_cells>=0],minlength=32),
                          np.bincount(moved_cells[moved_cells>=0],minlength=32))
    assert len(moved.changed_ids)+len(moved.failed_ids)==len(moved.selected_ids)
    assert not any(cell_index(values[:,:3],(0,0))[list(moved.changed_ids)]<0)


def test_selection_independent_of_traversal_and_zero_controls():
    values=cloud()
    ids=selected_ids(len(values),.25,key("displacement",1.))
    assert np.array_equal(ids,selected_ids(len(values),.25,key("displacement",1.)))
    files=['003_1_1.1.pcd','003_2_1.2.pcd','003_3_1.3.pcd']
    def selections(order):
        return {name:tuple(selected_ids(1000,.25,seed_key('mini_7','003',name,'displacement',1.))) for name in order}
    assert selections(files)==selections(list(reversed(files)))
    for family in ("random_removal","localized_removal","displacement","rearrangement","addition"):
        identity=apply_overlay(values,family=family,severity=0,key=key(family,0))
        assert np.array_equal(identity.values,values) and identity.reason=="IDENTITY"


def test_identity_pcd_roundtrip_and_malformed_rejected(tmp_path):
    values=cloud(25)
    path=tmp_path/"003_1_1.1.pcd"
    write_pcd(path,values)
    with path.open("rb") as f: header,reread=read_pcd(f)
    assert header.points==25 and np.allclose(reread,values,atol=1e-6)
    with pytest.raises(FileExistsError): write_pcd(path,values)
    malformed=path.read_bytes().replace(b"DATA ascii\n",b"DATA ascii\nnot-a-number ",1)
    with pytest.raises(ValueError): read_pcd(BytesIO(malformed))
    with pytest.raises(ValueError): read_pcd(BytesIO(path.read_bytes().replace(b"POINTS 25",b"POINTS 26")))


def test_zero_target_is_failed_attempt_not_resampled():
    values=cloud()
    target=freeze_target([])
    result=apply_overlay(values,family="localized_removal",severity=.5,key=key("localized_removal",.5),target=target)
    assert result.reason=="NO_TARGET" and not result.changed_ids and np.array_equal(result.values,values)
