"""Hand-checked arithmetic fixtures, never empirical observations."""
import pytest
from valid_point.evaluation.metrics import (event_metrics, false_alarm_metrics,
                                            episode_metrics, episode_recall, clean_alarm_runs,
                                            grouped_summary, paired_group_resample)


def event(i, alarm, *, realized=1, valid=True, failed=False):
    return {"segment": "mini_10", "episode": "e", "principal": "003", "sensor": "003",
            "cloud_id": str(i), "alarm": alarm, "score": None if alarm is None else .8,
            "reader_valid": valid, "realized_changed_rows": realized, "injection_failed": failed,
            "time_s": float(i)}


def test_attempt_eligible_realized_denominators_and_failure():
    rows = [event(1, True), event(2, None, valid=False, realized=0, failed=True),
            event(3, False, realized=1), event(4, True, realized=0, failed=True)]
    m = event_metrics(rows)
    assert m["all_attempt_recall"]["value"] == 1/4
    assert m["eligible_recall"]["value"] == 1/3
    assert m["realized_recall"]["value"] == 1/2
    assert m["failed_injection_count"] == 2 and m["reader_rejected_count"] == 1
    assert m["missing_score_count"] == 1
    assert false_alarm_metrics([])["eligible_fpr"]["value"] is None
    assert false_alarm_metrics([event(1, None)])["eligible_fpr"]["status"] == "NO_ELIGIBLE_CLEAN"
    with pytest.raises(ValueError): event_metrics([dict(event(1, True), score=None)])


def test_preexisting_censor_recovery_and_empty_exposure():
    rows = [event(0, True), event(1, True), event(2, None), event(3, False), event(4, False), event(5, False)]
    r = episode_metrics(rows, onset_s=1, offset_s=2, end_s=5)
    assert r["preexisting_alarm"] and r["delay"]["status"] == "PREEXISTING_ALARM"
    assert r["recovery"]["status"] == "UNDEFINED_INTERRUPTED_SUPPORT"
    rows = [event(1, False), event(2, False)]
    r = episode_metrics(rows, onset_s=1, offset_s=3, end_s=3)
    assert r["delay"]["status"] == "RIGHT_CENSORED_NO_DETECTION"
    assert r["delay"]["censor_s"] == 2
    rows = [event(1, None, realized=0, valid=False, failed=True)]
    r = episode_metrics(rows, onset_s=1, offset_s=2, end_s=2)
    assert r["delay"]["status"] == "NO_REALIZED_EXPOSURE"
    assert r["recovery"]["status"] == "NOT_APPLICABLE_NEVER_ALARMED"
    assert episode_recall([r])["all_attempted"]["value"] == 0
    assert episode_recall([r])["realized_nonzero"]["value"] is None


def test_clean_alarm_episode_rate_is_time_based():
    rows = [dict(event(i, alarm), time_s=t) for i, t, alarm in
            [(0,0,False),(1,2,True),(2,2.1,True),(3,3,False),(4,5,True)]]
    result = clean_alarm_runs(rows, eligible_seconds=60, attempted_seconds=90)
    assert result["alarm_run_onsets"] == 2
    assert result["rate_per_eligible_minute"] == 2
    assert clean_alarm_runs([], eligible_seconds=0, attempted_seconds=30)["rate_per_eligible_minute"] is None


def test_grouped_pairing_not_frame_iid():
    rows = []
    for segment, shift in (("C0", .2), ("C1", -.1)):
        for frame in range(3):
            for variant, value in (("clean", .5), ("attacked", .5+shift)):
                rows.append({"segment": segment, "acquisition_group": segment, "episode": "e",
                             "cloud_id": str(frame), "variant": variant, "A": value})
    summary = grouped_summary(rows, metric="A")
    assert summary["contributing_segments"] == 2
    assert summary["macro"] == pytest.approx(.05)
    draws = paired_group_resample(rows, group_key="acquisition_group", draws=5)
    assert len(draws) == 5
    for draw in draws:
        assert len(draw) == 12
        assert grouped_summary(draw, metric="A")["macro"] is not None
        for copy in (0, 1):
            unit = [r for r in draw if r["_resample_copy"] == copy]
            assert len(unit) == 6
            assert {r["variant"] for r in unit} == {"clean", "attacked"}
            assert len({r["acquisition_group"] for r in unit}) == 1
    with pytest.raises(ValueError): paired_group_resample(rows[:6], group_key="acquisition_group")
