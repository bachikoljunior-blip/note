#!/usr/bin/env python3
"""Semantic validator for cached scientific phase pass replay.

A persisted PASS may be reused only when the exact approval context is still
current. File-path existence and stored PASS labels are insufficient: the
current plan step, verifier revision, artifact membership, and artifact bytes
must still match the approved snapshot.

A conservative rerun is always allowed; this validator only gates reuse.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import jsonschema


def _artifact_map(items: List[Dict[str, Any]]) -> Tuple[Dict[Tuple[str, str], str], List[str]]:
    out: Dict[Tuple[str, str], str] = {}
    issues: List[str] = []
    for item in items:
        key = (str(item["artifact_id"]), str(item["path"]))
        if key in out:
            issues.append(f"duplicate checked artifact identity: {key[0]} @ {key[1]}")
        out[key] = str(item["sha256"])
    return out, issues


def semantic_issues(packet: Dict[str, Any]) -> List[str]:
    issues: List[str] = []
    approval = packet["approval"]
    current = packet["current"]
    decision = packet["decision"]

    if decision["action"] == "reuse" and decision["reuse_cached_pass"] is not True:
        issues.append("reuse action must set reuse_cached_pass=true")
    if decision["action"] == "rerun" and decision["reuse_cached_pass"] is not False:
        issues.append("rerun action must set reuse_cached_pass=false")

    if decision["action"] != "reuse":
        return issues

    for field in ("hook_status", "review_status", "prefinish_contract_status"):
        if approval[field] != "PASS":
            issues.append(f"cached reuse requires approval.{field}=PASS")

    if approval["plan_step_sha256"] != current["plan_step_sha256"]:
        issues.append("plan step digest changed since approval")
    if approval["verifier_revision"] != current["verifier_revision"]:
        issues.append("verifier revision changed since approval")

    approved, dup_a = _artifact_map(approval["checked_artifacts"])
    current_map, dup_c = _artifact_map(current["checked_artifacts"])
    issues.extend(dup_a)
    issues.extend(dup_c)

    approved_keys = set(approved)
    current_keys = set(current_map)
    for key in sorted(approved_keys - current_keys):
        issues.append(f"approved checked artifact missing from current context: {key[0]} @ {key[1]}")
    for key in sorted(current_keys - approved_keys):
        issues.append(f"current checked-artifact membership changed: unexpected {key[0]} @ {key[1]}")
    for key in sorted(approved_keys & current_keys):
        if approved[key] != current_map[key]:
            issues.append(f"checked artifact digest changed: {key[0]} @ {key[1]}")

    return issues


def validate_packet(packet: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    structural: List[str] = []
    for error in sorted(jsonschema.Draft202012Validator(schema).iter_errors(packet), key=lambda e: list(e.path)):
        structural.append("schema: " + error.message)
    if structural:
        return structural
    return semantic_issues(packet)


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print("usage: cached_phase_replay_validator_v1.py SCHEMA.json PACKET.json", file=sys.stderr)
        return 2
    schema = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    packet = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    issues = validate_packet(packet, schema)
    print(json.dumps({"valid": not issues, "issues": issues}, indent=2, sort_keys=True))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
