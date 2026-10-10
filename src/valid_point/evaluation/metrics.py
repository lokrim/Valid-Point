"""Offline attempted-event metrics. Inputs here are sealed evaluator joins, never scorer inputs."""
from __future__ import annotations

from collections import defaultdict
from math import isfinite
import random


def ratio(numerator: int, denominator: int, *, empty_reason: str = "EMPTY_DENOMINATOR") -> dict:
    if denominator < 0 or numerator < 0 or numerator > denominator:
        raise ValueError("invalid metric counts")
    return {"numerator": numerator, "denominator": denominator,
            "value": None if denominator == 0 else numerator / denominator,
            "status": empty_reason if denominator == 0 else "defined"}


def threshold_power(scores: list[float], threshold: float | None, *, min_known: int = 200) -> str:
    """Describe calibration support/power without requiring favorable alarms."""
    if len(scores) < min_known or threshold is None:
        return "INSUFFICIENT_KNOWN"
    if not 0 <= threshold <= 1 or any(not isfinite(x) or not 0 <= x <= 1 for x in scores):
        raise ValueError("invalid calibration scores")
    return "NO_POWER" if threshold >= 1 or max(scores) <= threshold else "AVAILABLE"


def event_metrics(rows: list[dict]) -> dict:
    """One row per scheduled attempted event, including failures and unknowns."""
    keys = [(r["segment"], r["episode"], r["principal"], r["sensor"], r["cloud_id"]) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate attempted event")
    for r in rows:
        if r["alarm"] not in (True, False, None):
            raise ValueError("invalid alarm")
        if r["alarm"] is not None and r.get("score") is None:
            raise ValueError("known alarm without score")
        if r.get("score") is not None and (not isfinite(r["score"]) or not 0 <= r["score"] <= 1):
            raise ValueError("invalid score")
    eligible = [r for r in rows if r["alarm"] is not None]
    realized = [r for r in rows if r.get("reader_valid") is True and r.get("realized_changed_rows", 0) > 0]
    alarmed = lambda sample: sum(r["alarm"] is True and r.get("reader_valid") is True
                                 and r.get("realized_changed_rows", 0) > 0
                                 and not r.get("injection_failed", False) for r in sample)
    return {"all_attempt_recall": ratio(alarmed(rows), len(rows)),
            "eligible_recall": ratio(alarmed(eligible), len(eligible), empty_reason="NO_ELIGIBLE_SCORES"),
            "realized_recall": ratio(alarmed(realized), len(realized), empty_reason="NO_REALIZED_CHANGE"),
            "eligible_coverage": ratio(len(eligible), len(rows)),
            "failed_injection_count": sum(r.get("injection_failed", False) for r in rows),
            "reader_rejected_count": sum(r.get("reader_valid") is False for r in rows),
            "missing_score_count": sum(r.get("score") is None for r in rows)}


def false_alarm_metrics(rows: list[dict]) -> dict:
    known = [r for r in rows if r["alarm"] is not None]
    count = sum(r["alarm"] is True for r in rows)
    return {"eligible_fpr": ratio(count, len(known), empty_reason="NO_ELIGIBLE_CLEAN"),
            "all_attempt_alarm_rate": ratio(count, len(rows)),
            "eligible_coverage": ratio(len(known), len(rows))}


def episode_metrics(rows: list[dict], *, onset_s: float, offset_s: float,
                    end_s: float, g_reset_s: float = .5, recovery_hold_s: float = 2.) -> dict:
    if onset_s >= offset_s or end_s < offset_s:
        raise ValueError("invalid episode times")
    sample = sorted(rows, key=lambda r: r["time_s"])
    if any(a["time_s"] == b["time_s"] for a, b in zip(sample, sample[1:])):
        raise ValueError("duplicate event time")
    inside = [r for r in sample if onset_s <= r["time_s"] < offset_s]
    before = [r for r in sample if r["time_s"] < onset_s]
    preexisting = bool(before and before[-1]["alarm"] is True)
    realized = [r for r in inside if r.get("reader_valid") is True and r.get("realized_changed_rows", 0) > 0]
    exposure = bool(realized)
    alarms = [r for r in inside if r["alarm"] is True and r.get("reader_valid") is True
              and r.get("realized_changed_rows", 0) > 0 and not r.get("injection_failed", False)]
    new_alarms = [r for r in alarms if not preexisting]
    if preexisting:
        delay = {"value_s": None, "status": "PREEXISTING_ALARM", "censor_s": None}
    elif not exposure:
        delay = {"value_s": None, "status": "NO_REALIZED_EXPOSURE", "censor_s": offset_s - onset_s}
    elif not any(r["alarm"] is not None for r in inside):
        delay = {"value_s": None, "status": "NO_ELIGIBLE_ALARM", "censor_s": offset_s - onset_s}
    elif not new_alarms:
        delay = {"value_s": None, "status": "RIGHT_CENSORED_NO_DETECTION", "censor_s": offset_s - onset_s}
    else:
        delay = {"value_s": new_alarms[0]["time_s"] - onset_s, "status": "DETECTED", "censor_s": None}
    first_realized = realized[0]["time_s"] if realized else None
    delay["first_realized_onset_s"] = first_realized
    delay["from_first_realized_s"] = None if first_realized is None or not new_alarms else new_alarms[0]["time_s"] - first_realized
    recovery = {"value_s": None, "status": "NOT_APPLICABLE_NEVER_ALARMED"}
    if alarms:
        recovery = {"value_s": None, "status": "RIGHT_CENSORED_NO_PERSISTENCE"}
        after = [r for r in sample if offset_s <= r["time_s"] <= end_s]
        start = None; previous = None
        for r in after:
            valid = r["alarm"] is False and not r.get("reset", False)
            gap = previous is not None and r["time_s"] - previous > g_reset_s
            if not valid or gap:
                start = None
            if valid and start is None:
                start = r["time_s"]
            if start is not None and r["time_s"] - start >= recovery_hold_s:
                recovery = {"value_s": r["time_s"] - offset_s, "status": "RECOVERED"}
                break
            previous = r["time_s"] if valid else None
        if recovery["value_s"] is None and any(r["alarm"] is None or r.get("reset", False) for r in after):
            recovery["status"] = "UNDEFINED_INTERRUPTED_SUPPORT"
    return {"attempted_episode": True, "realized_nonzero_episode": exposure,
            "alarm_in_window": bool(alarms), "preexisting_alarm": preexisting,
            "delay": delay, "recovery": recovery}


def episode_recall(episodes: list[dict]) -> dict:
    """Each attempted episode counts once, regardless of its frame count."""
    return {"all_attempted": ratio(sum(e["alarm_in_window"] for e in episodes), len(episodes)),
            "realized_nonzero": ratio(sum(e["alarm_in_window"] for e in episodes if e["realized_nonzero_episode"]),
                                      sum(e["realized_nonzero_episode"] for e in episodes),
                                      empty_reason="NO_REALIZED_EPISODES"),
            "preexisting_count": sum(e["preexisting_alarm"] for e in episodes)}


def clean_alarm_runs(rows: list[dict], *, eligible_seconds: float, attempted_seconds: float,
                     separation_s: float = 2.) -> dict:
    """Count clean alarm-run onsets after two seconds of continuous eligible quiet."""
    if eligible_seconds < 0 or attempted_seconds < eligible_seconds or separation_s <= 0:
        raise ValueError("invalid observed time")
    sample = sorted(rows, key=lambda r: r["time_s"])
    previous = None; quiet_start = None; onsets = 0
    for row in sample:
        alarm = row["alarm"]
        if alarm is None:
            quiet_start = None
        elif alarm is False:
            if previous is None or previous["alarm"] is not False:
                quiet_start = row["time_s"]
        elif previous is None or previous["alarm"] is not True:
            if previous is None or (quiet_start is not None and row["time_s"]-quiet_start >= separation_s):
                onsets += 1
        previous = row
    return {"alarm_run_onsets": onsets, "eligible_agent_minutes": eligible_seconds/60,
            "attempted_agent_minutes": attempted_seconds/60,
            "rate_per_eligible_minute": None if eligible_seconds == 0 else onsets/(eligible_seconds/60),
            "status": "NO_ELIGIBLE_TIME" if eligible_seconds == 0 else "defined"}


def grouped_summary(rows: list[dict], *, metric: str) -> dict:
    """Equal-weight segment mean and leave-one-segment values; rows may be paired variants."""
    groups = defaultdict(list)
    for row in rows:
        groups[row["segment"]].append(row)
    values = {}
    for segment, sample in sorted(groups.items()):
        pairs = defaultdict(dict)
        for row in sample:
            key = (row.get("_resample_copy", 0), row["episode"], row["cloud_id"])
            variant = row["variant"]
            if variant in pairs[key]:
                raise ValueError("duplicate paired variant")
            pairs[key][variant] = row.get(metric)
        diffs = [v["attacked"] - v["clean"] for v in pairs.values()
                 if v.get("attacked") is not None and v.get("clean") is not None]
        values[segment] = {"paired_n": len(diffs), "value": sum(diffs)/len(diffs) if diffs else None,
                           "unpaired_or_unknown": len(pairs)-len(diffs)}
    defined = {s: v["value"] for s, v in values.items() if v["value"] is not None}
    macro = sum(defined.values())/len(defined) if defined else None
    leave_one = {s: sum(v for k, v in defined.items() if k != s)/(len(defined)-1)
                 for s in defined if len(defined) > 1}
    return {"segments": values, "macro": macro, "contributing_segments": len(defined),
            "omitted_segments": sorted(set(values)-set(defined)), "range": None if not defined else [min(defined.values()), max(defined.values())],
            "leave_one_segment": leave_one}


def paired_group_resample(rows: list[dict], *, group_key: str, draws: int = 2000, seed: int = 20261008) -> list[list[dict]]:
    """Resample whole acquisition groups, keeping every episode and clean/attacked pair together."""
    groups = defaultdict(list)
    for row in rows:
        if group_key not in row:
            raise ValueError("missing acquisition group")
        groups[row[group_key]].append(row)
    keys = sorted(groups)
    if len(keys) < 2:
        raise ValueError("no between-group resampling with one identifiable group")
    rng = random.Random(seed)
    return [[dict(row, _resample_copy=i) for i, key in enumerate(rng.choices(keys, k=len(keys)))
             for row in groups[key]] for _ in range(draws)]
