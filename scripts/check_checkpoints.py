#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = json.loads((ROOT / "state/current.json").read_text(encoding="utf-8"))
NOW = datetime.now(timezone.utc)


def parse(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


due_48h = NOW >= parse(STATE["checkpoints"]["after_48h_utc"])
due_7d = NOW >= parse(STATE["checkpoints"]["after_7d_utc"])
payload = {
    "checked_at_utc": NOW.isoformat(),
    "due_48h": due_48h,
    "due_7d": due_7d,
    "article_url": STATE["publication"]["article_url"],
}
out = ROOT / "reports" / "checkpoints.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, ensure_ascii=False))
if output := os.environ.get("GITHUB_OUTPUT"):
    with open(output, "a", encoding="utf-8") as fh:
        fh.write(f"due_48h={str(due_48h).lower()}\n")
        fh.write(f"due_7d={str(due_7d).lower()}\n")
