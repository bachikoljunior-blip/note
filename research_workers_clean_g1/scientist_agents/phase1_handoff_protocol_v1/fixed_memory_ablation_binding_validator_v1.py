#!/usr/bin/env python3
"""Validate a claimed fixed-memory ablation handoff.

A comparison may be labelled fixed-memory identity only when every condition is
bound to the same implementation revision, non-memory control digest, initial
memory snapshot digest and candidate universe, and every condition freezes
memory updates during evaluation. The intervention configuration may differ;
that is the intended manipulated variable.

Declining the fixed-memory identity claim is always legal. This validator does
not score experimental outcomes or establish causal efficacy.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import jsonschema


def semantic_issues(packet: Dict[str, Any]) -> List[str]:
    issues: List[str] = []
    conditions = packet["conditions"]
    ids = [str(item["condition_id"]) for item in conditions]
    if len(ids) != len(set(ids)):
        issues.append("condition_id values must be unique")

    if packet["decision"]["assert_fixed_memory_identity"] is not True:
        return issues

    matched_fields = {
        "code_revision": [item["code_revision"] for item in conditions],
        "non_memory_controls_sha256": [item["non_memory_controls_sha256"] for item in conditions],
        "initial_snapshot_sha256": [item["memory"]["initial_snapshot_sha256"] for item in conditions],
        "candidate_universe_sha256": [item["memory"]["candidate_universe_sha256"] for item in conditions],
    }
    for field, values in matched_fields.items():
        if len(set(values)) != 1:
            issues.append(f"{field} differs across conditions")

    online = [
        str(item["condition_id"])
        for item in conditions
        if item["memory"]["update_policy"] != "frozen"
    ]
    if online:
        issues.append(
            "fixed-memory identity requires update_policy=frozen for every condition: "
            + ", ".join(online)
        )
    return issues


def validate_packet(packet: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    structural: List[str] = []
    for error in sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(packet),
        key=lambda item: list(item.path),
    ):
        structural.append("schema: " + error.message)
    if structural:
        return structural
    return semantic_issues(packet)


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print("usage: fixed_memory_ablation_binding_validator_v1.py SCHEMA.json PACKET.json", file=sys.stderr)
        return 2
    schema = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    packet = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    issues = validate_packet(packet, schema)
    print(json.dumps({"valid": not issues, "issues": issues}, indent=2, sort_keys=True))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
