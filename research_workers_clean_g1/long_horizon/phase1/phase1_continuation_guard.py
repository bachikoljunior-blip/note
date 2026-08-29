from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

SCHEMA = 1


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(obj) -> str:
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


@dataclass
class Checkpoint:
    schema_version: int
    task_id: str
    seq: int
    plan_generation: int
    predecessor_hash: str
    plan_id: str
    alternative_plan_id: Optional[str]
    budget_remaining_min: int
    forecast_p90_remaining_min: int
    retry_reserve_min: int
    rate_limit_not_before_min: Optional[int]
    retry_attempt: int
    max_retry_attempts: int
    completed_effect_ids: list[str]
    status: str
    switch_reason: Optional[str]
    checkpoint_hash: str = ""

    def payload(self):
        d = asdict(self)
        d.pop("checkpoint_hash", None)
        return d

    def seal(self):
        self.checkpoint_hash = digest(self.payload())
        return self

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


def initial_checkpoint(**overrides):
    d = dict(
        schema_version=SCHEMA,
        task_id="phase1-clean-long-horizon-overrun-recovery",
        seq=4,
        plan_generation=2,
        predecessor_hash="pred-003",
        plan_id="deep-public-audit",
        alternative_plan_id="bounded-direct-probe",
        budget_remaining_min=50,
        forecast_p90_remaining_min=24,
        retry_reserve_min=8,
        rate_limit_not_before_min=None,
        retry_attempt=0,
        max_retry_attempts=2,
        completed_effect_ids=["audit-public-sources"],
        status="READY",
        switch_reason=None,
    )
    d.update(overrides)
    return Checkpoint(**d).seal()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json_atomic(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def load_cp(path):
    cp = Checkpoint.from_dict(load_json(path))
    if cp.schema_version != SCHEMA:
        raise ValueError("unsupported schema")
    if digest(cp.payload()) != cp.checkpoint_hash:
        raise ValueError("checkpoint integrity mismatch")
    return cp


def load_ledger(path):
    p = Path(path)
    if not p.exists():
        return {"schema_version": 1, "consumed_resume_ids": []}
    d = load_json(path)
    if d.get("schema_version") != 1 or not isinstance(d.get("consumed_resume_ids"), list):
        raise ValueError("invalid ledger")
    return d


def resume_id(cp: Checkpoint, invocation_id: str):
    return digest({
        "task_id": cp.task_id,
        "checkpoint_hash": cp.checkpoint_hash,
        "plan_generation": cp.plan_generation,
        "invocation_id": invocation_id,
    })[:24]


def advance(cp: Checkpoint, *, status: str, switch_reason=None):
    n = copy.deepcopy(cp)
    n.predecessor_hash = cp.checkpoint_hash
    n.seq += 1
    n.status = status
    n.switch_reason = switch_reason
    return n


def switch_plan(cp: Checkpoint, reason: str):
    if not cp.alternative_plan_id:
        n = advance(cp, status="DEFERRED", switch_reason=reason)
        return n.seal(), "DEFER_NO_ALTERNATIVE"
    old = cp.plan_id
    n = advance(cp, status="SWITCHED", switch_reason=f"{reason}:{old}->{cp.alternative_plan_id}")
    n.plan_generation += 1
    n.plan_id = cp.alternative_plan_id
    n.alternative_plan_id = None
    n.rate_limit_not_before_min = None
    n.retry_attempt = 0
    return n.seal(), "SWITCH_PLAN"


def decide(head: Checkpoint, candidate: Checkpoint, ledger: dict, invocation_id: str, now_min: int):
    # 1) Reconstruction/integrity already happened on load.  Freshness is exact-head + generation.
    if candidate.checkpoint_hash != head.checkpoint_hash:
        return head, ledger, {"accepted": False, "decision": "REJECT_STALE_CHECKPOINT"}
    if candidate.plan_generation != head.plan_generation:
        return head, ledger, {"accepted": False, "decision": "REJECT_STALE_GENERATION"}

    rid = resume_id(candidate, invocation_id)
    if rid in ledger["consumed_resume_ids"]:
        return head, ledger, {"accepted": False, "decision": "REJECT_DUPLICATE_RESUME", "resume_id": rid}

    # 2) Forecast/rate-limit policy runs before authorizing work.
    if head.rate_limit_not_before_min is not None:
        wait = max(0, head.rate_limit_not_before_min - now_min)
        feasible = (
            wait + head.forecast_p90_remaining_min + head.retry_reserve_min
            <= head.budget_remaining_min
        ) and head.retry_attempt < head.max_retry_attempts
        if not feasible:
            new_head, decision = switch_plan(head, "RATE_LIMIT_OVERRUN")
            return new_head, ledger, {
                "accepted": True,
                "decision": decision,
                "reason": new_head.switch_reason,
                "not_before_min": head.rate_limit_not_before_min,
            }
        if wait > 0:
            # Durable defer: do not consume an execution claim and do not spin-retry before not_before.
            return head, ledger, {
                "accepted": False,
                "decision": "DEFER_RATE_LIMIT",
                "not_before_min": head.rate_limit_not_before_min,
                "wait_min": wait,
            }
        # Eligible again; actual retry is authorized below.  A future 429 writes a new checkpoint.

    usable = head.budget_remaining_min - head.retry_reserve_min
    if head.forecast_p90_remaining_min > usable:
        new_head, decision = switch_plan(head, "FORECAST_OVERRUN")
        return new_head, ledger, {
            "accepted": True,
            "decision": decision,
            "reason": new_head.switch_reason,
        }

    # 3) Work authorization consumes a resume identity in a ledger separate from checkpoint identity.
    new_ledger = copy.deepcopy(ledger)
    new_ledger["consumed_resume_ids"] = sorted(set(new_ledger["consumed_resume_ids"] + [rid]))
    return head, new_ledger, {"accepted": True, "decision": "CONTINUE", "resume_id": rid}


def cmd_step(args):
    head = load_cp(args.head)
    candidate = load_cp(args.candidate)
    ledger = load_ledger(args.ledger)
    new_head, new_ledger, decision = decide(head, candidate, ledger, args.invocation_id, args.now_min)
    write_json_atomic(args.head, asdict(new_head))
    write_json_atomic(args.ledger, new_ledger)
    out = {
        "decision": decision,
        "head_hash": new_head.checkpoint_hash,
        "head_seq": new_head.seq,
        "plan_generation": new_head.plan_generation,
        "plan_id": new_head.plan_id,
        "ledger_count": len(new_ledger["consumed_resume_ids"]),
    }
    print(json.dumps(out, sort_keys=True))


def invoke_step(script, head, candidate, ledger, invocation, now_min):
    cp = subprocess.run(
        [sys.executable, str(script), "step", "--head", str(head), "--candidate", str(candidate),
         "--ledger", str(ledger), "--invocation-id", invocation, "--now-min", str(now_min)],
        check=True, capture_output=True, text=True,
    )
    return json.loads(cp.stdout)


def cmd_suite(_args):
    script = Path(__file__).resolve()
    report = {"process_boundary": True, "cases": {}}
    with tempfile.TemporaryDirectory(prefix="lh-guard-") as td:
        td = Path(td)

        def setup(name, cp):
            d = td / name
            d.mkdir()
            head, cand, ledger = d / "head.json", d / "candidate.json", d / "resume_ledger.json"
            write_json_atomic(head, asdict(cp))
            write_json_atomic(cand, asdict(cp))
            write_json_atomic(ledger, {"schema_version": 1, "consumed_resume_ids": []})
            return head, cand, ledger

        # Valid + exact duplicate across two separate child processes.
        head, cand, ledger = setup("valid_duplicate", initial_checkpoint())
        r1 = invoke_step(script, head, cand, ledger, "invocation-A", 10)
        r2 = invoke_step(script, head, cand, ledger, "invocation-A", 10)
        report["cases"]["valid_then_duplicate"] = {"first": r1, "second": r2}

        # Stale checkpoint is structurally valid but not current.
        current = initial_checkpoint()
        head, cand, ledger = setup("stale", current)
        stale = initial_checkpoint(seq=3, predecessor_hash="pred-002")
        write_json_atomic(cand, asdict(stale))
        report["cases"]["stale"] = invoke_step(script, head, cand, ledger, "invocation-stale", 10)

        # Corrupt checkpoint cannot be reconstructed: payload/hash mismatch is rejected before policy.
        corrupt = initial_checkpoint()
        head, cand, ledger = setup("corrupt", corrupt)
        corrupt_dict = load_json(cand)
        corrupt_dict["plan_id"] = "tampered-plan"  # deliberately retain old checkpoint_hash
        write_json_atomic(cand, corrupt_dict)
        bad = subprocess.run(
            [sys.executable, str(script), "step", "--head", str(head), "--candidate", str(cand),
             "--ledger", str(ledger), "--invocation-id", "invocation-corrupt", "--now-min", "10"],
            check=False, capture_output=True, text=True,
        )
        report["cases"]["corrupt_checkpoint"] = {
            "returncode": bad.returncode,
            "integrity_rejected": bad.returncode != 0 and "checkpoint integrity mismatch" in bad.stderr,
        }

        # Forecast overrun switches plans; replaying the old candidate is then stale.
        over = initial_checkpoint(budget_remaining_min=30, forecast_p90_remaining_min=28, retry_reserve_min=6)
        head, cand, ledger = setup("forecast", over)
        s1 = invoke_step(script, head, cand, ledger, "invocation-overrun", 10)
        s2 = invoke_step(script, head, cand, ledger, "invocation-old-plan", 10)
        report["cases"]["forecast_overrun"] = {"switch": s1, "old_replay": s2, "new_head": load_json(head)}

        # Rate limit still feasible: persist not-before and defer without consuming a retry claim.
        rl = initial_checkpoint(
            budget_remaining_min=50, forecast_p90_remaining_min=20, retry_reserve_min=8,
            rate_limit_not_before_min=18, retry_attempt=1,
        )
        head, cand, ledger = setup("rate_defer", rl)
        d1 = invoke_step(script, head, cand, ledger, "invocation-rate-early", 10)
        d2 = invoke_step(script, head, cand, ledger, "invocation-rate-eligible", 18)
        report["cases"]["rate_limit_defer_then_resume"] = {"early": d1, "eligible": d2}

        # Rate-limit delay consumes slack: switch now instead of waiting for a doomed retry.
        rl2 = initial_checkpoint(
            budget_remaining_min=30, forecast_p90_remaining_min=18, retry_reserve_min=8,
            rate_limit_not_before_min=20, retry_attempt=1,
        )
        head, cand, ledger = setup("rate_switch", rl2)
        rs1 = invoke_step(script, head, cand, ledger, "invocation-rate-overrun", 10)
        rs2 = invoke_step(script, head, cand, ledger, "invocation-rate-old", 10)
        report["cases"]["rate_limit_switch"] = {"switch": rs1, "old_replay": rs2, "new_head": load_json(head)}

        # Same overrun but no alternate plan: durable deferral, not blind retry.
        rl3 = initial_checkpoint(
            alternative_plan_id=None, budget_remaining_min=25, forecast_p90_remaining_min=18,
            retry_reserve_min=8, rate_limit_not_before_min=20, retry_attempt=1,
        )
        head, cand, ledger = setup("rate_no_alt", rl3)
        report["cases"]["rate_limit_no_alternative"] = invoke_step(
            script, head, cand, ledger, "invocation-rate-no-alt", 10
        )

    actual = {
        "valid": report["cases"]["valid_then_duplicate"]["first"]["decision"]["decision"],
        "duplicate": report["cases"]["valid_then_duplicate"]["second"]["decision"]["decision"],
        "stale": report["cases"]["stale"]["decision"]["decision"],
        "corrupt": "REJECT_INTEGRITY" if report["cases"]["corrupt_checkpoint"]["integrity_rejected"] else "FAILED",
        "forecast_switch": report["cases"]["forecast_overrun"]["switch"]["decision"]["decision"],
        "forecast_old_replay": report["cases"]["forecast_overrun"]["old_replay"]["decision"]["decision"],
        "rate_early": report["cases"]["rate_limit_defer_then_resume"]["early"]["decision"]["decision"],
        "rate_eligible": report["cases"]["rate_limit_defer_then_resume"]["eligible"]["decision"]["decision"],
        "rate_switch": report["cases"]["rate_limit_switch"]["switch"]["decision"]["decision"],
        "rate_old_replay": report["cases"]["rate_limit_switch"]["old_replay"]["decision"]["decision"],
        "rate_no_alt": report["cases"]["rate_limit_no_alternative"]["decision"]["decision"],
    }
    expected = {
        "valid": "CONTINUE",
        "duplicate": "REJECT_DUPLICATE_RESUME",
        "stale": "REJECT_STALE_CHECKPOINT",
        "corrupt": "REJECT_INTEGRITY",
        "forecast_switch": "SWITCH_PLAN",
        "forecast_old_replay": "REJECT_STALE_CHECKPOINT",
        "rate_early": "DEFER_RATE_LIMIT",
        "rate_eligible": "CONTINUE",
        "rate_switch": "SWITCH_PLAN",
        "rate_old_replay": "REJECT_STALE_CHECKPOINT",
        "rate_no_alt": "DEFER_NO_ALTERNATIVE",
    }
    report["expected"] = expected
    report["actual"] = actual
    report["passed"] = actual == expected
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["passed"] else 1)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("step")
    s.add_argument("--head", required=True)
    s.add_argument("--candidate", required=True)
    s.add_argument("--ledger", required=True)
    s.add_argument("--invocation-id", required=True)
    s.add_argument("--now-min", type=int, required=True)
    s.set_defaults(func=cmd_step)
    t = sub.add_parser("suite")
    t.set_defaults(func=cmd_suite)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
