import pytest
from valid_point.calibration import calibrate, alarm


def rows(values,role='calibration'):
    return [{'split_role':role,'clean':True,'seed':200+i%2,'segment':f's{i%2}',
             'status':'known' if v is not None else 'unknown','A':v} for i,v in enumerate(values)]


def test_order_statistic_ties_and_unknowns():
    c=calibrate(rows([i/200 for i in range(200)]+[None]*10), allowed_seeds={200,201})
    assert c.order_index == 199 and c.threshold == 198/200
    assert c.achieved_fpr == 1/200 and c.abstention == pytest.approx(10/210)
    assert alarm(c.threshold,c) is False and alarm(None,c) is None
    assert alarm(199/200,c) is True
    assert c.wilson_low <= c.achieved_fpr <= c.wilson_high
    tied=calibrate(rows([.1]*199+[1]))
    assert tied.threshold == .1 and tied.achieved_fpr == 1/200
    no_power=calibrate(rows([1]*200))
    assert no_power.no_power and no_power.achieved_fpr == 0 and alarm(1,no_power) is False


def test_separate_calibration_and_insufficient_support():
    assert calibrate(rows([.1]*199)).status == 'unavailable'
    with pytest.raises(ValueError): calibrate(rows([.1]*200,'reference'))
    with pytest.raises(ValueError): calibrate(rows([.1]*200),allowed_seeds={100})
