"""Elapsed-time, per-stream EWMA with explicit unknown and warm-up states."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import exp, isfinite


@dataclass(frozen=True)
class TemporalRecord:
    episode: str
    principal: str
    sensor: str
    method_arm: str
    reference_version: str
    source_ns: int
    status: str
    reason: str
    Z: float | None
    C_time: float | None
    held_Z: float | None
    held_age_s: float | None
    eligible_updates: int
    contiguous_s: float
    ready: bool
    reset: bool

    def as_dict(self) -> dict:
        return asdict(self)


class TemporalEWMA:
    def __init__(self, tau_s: float = 1., g_reset_s: float = .5,
                 min_updates: int = 10):
        if not isfinite(tau_s) or tau_s <= 0 or not isfinite(g_reset_s) or g_reset_s <= 0 or min_updates < 1:
            raise ValueError("invalid temporal settings")
        self.tau_s=tau_s; self.g_reset_s=g_reset_s; self.min_updates=min_updates
        self._states: dict[tuple, dict] = {}
        self._versions: dict[tuple, str] = {}

    def update(self, *, episode: str, principal: str, sensor: str,
               method_arm: str, reference_version: str, source_ns: int,
               A: float | None, reason: str = "VALID") -> TemporalRecord:
        if type(source_ns) is not int or not all((episode,principal,sensor,method_arm,reference_version)):
            raise ValueError("invalid temporal identity/time")
        if A is not None and (not isfinite(A) or not 0 <= A <= 1):
            raise ValueError("A outside [0,1]")
        base=(episode,principal,sensor,method_arm)
        old_version=self._versions.get(base)
        version_reset=old_version is not None and old_version != reference_version
        if version_reset:
            self._states.pop(base+(old_version,),None)
        self._versions[base]=reference_version
        key=base+(reference_version,)
        state=self._states.get(key)
        if state is not None and source_ns <= state["last_event_ns"]:
            why="DUPLICATE_TIME" if source_ns == state["last_event_ns"] else "REVERSED_TIME"
            return self._record(key,source_ns,"unknown",why,state,None,False)
        if state is not None:
            state["last_event_ns"]=source_ns
        if A is None:
            return self._record(key,source_ns,"unknown",reason,state,None,False)
        reset=version_reset
        if state is None or (source_ns-state["last_eligible_ns"])/1e9 > self.g_reset_s:
            reset=reset or state is not None
            state={"Z":float(A),"first_ns":source_ns,"last_eligible_ns":source_ns,
                   "last_event_ns":source_ns,"updates":1}
            self._states[key]=state
        else:
            dt=(source_ns-state["last_eligible_ns"])/1e9
            rho=exp(-dt/self.tau_s)
            state["Z"]=rho*state["Z"]+(1-rho)*A
            state["last_eligible_ns"]=source_ns
            state["updates"]+=1
        ready=state["updates"]>=self.min_updates and (source_ns-state["first_ns"])/1e9 >= 3*self.tau_s
        return self._record(key,source_ns,"known","VALID" if ready else "WARM_UP",state,state["Z"],reset)

    def _record(self,key,source_ns,status,reason,state,public_z,reset):
        age=None if state is None else max(0.,(source_ns-state["last_eligible_ns"])/1e9)
        duration=0. if state is None else (state["last_eligible_ns"]-state["first_ns"])/1e9
        ready=public_z is not None and state["updates"]>=self.min_updates and duration>=3*self.tau_s
        return TemporalRecord(*key,source_ns,status,reason,public_z,
                              None if public_z is None else 1-public_z,
                              None if state is None else state["Z"],age,
                              0 if state is None else state["updates"],duration,ready,reset)

    def checkpoint(self) -> dict:
        return {"tau_s":self.tau_s,"g_reset_s":self.g_reset_s,"min_updates":self.min_updates,
                "states":[{"key":list(key),**state} for key,state in sorted(self._states.items())],
                "versions":[{"key":list(key),"version":value} for key,value in sorted(self._versions.items())]}

    @classmethod
    def resume(cls, checkpoint: dict) -> "TemporalEWMA":
        result=cls(checkpoint["tau_s"],checkpoint["g_reset_s"],checkpoint["min_updates"])
        result._states={tuple(row["key"]):{k:v for k,v in row.items() if k!="key"} for row in checkpoint["states"]}
        result._versions={tuple(row["key"]):row["version"] for row in checkpoint["versions"]}
        return result
