import pytest
from valid_point.ablations import clean_fixture_rows
from valid_point.references import fit_references, select_reference, normalize


def test_training_only_and_split_lineage():
    rows = clean_fixture_rows([100,101,102,103,104,105,106,107,108,109], 'reference')
    bundle = fit_references(rows, allowed_seeds=set(range(100,110)))
    assert bundle['S:vehicle:C_far_sparse'].status == 'low_support'
    assert bundle['S:vehicle:B_constant'].status == 'zero_scale'
    ref, reason = select_reference(bundle,'S','vehicle','C_far_sparse')
    assert ref.context == 'S:vehicle' and reason == 'fallback'
    ref, reason = select_reference(bundle,'S','vehicle','B_constant')
    assert ref.context == 'S:vehicle' and reason == 'fallback'
    assert select_reference(bundle,'S','radar','near')[0] is None
    assert normalize(ref.u + ref.b * 10, ref) == 1
    assert normalize(0, ref) == 0
    with pytest.raises(ValueError):
        fit_references(rows + clean_fixture_rows([200],'calibration'))
    with pytest.raises(ValueError):
        fit_references(rows,allowed_seeds={100})
    with pytest.raises(ValueError):
        fit_references([{**rows[0], 'clean':False}])


def test_support_across_segments_and_pooled_opt_in():
    rows = clean_fixture_rows([100], 'reference')
    bundle = fit_references(rows,min_rows=20)
    assert bundle['K:vehicle:dt_0p5s'].status == 'low_support'
    assert select_reference(bundle,'K','vehicle','dt_0p5s')[0] is None
    assert 'K:pooled' not in bundle
