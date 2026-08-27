from __future__ import annotations
import importlib.util
import json
import random
from pathlib import Path

MODULE = Path(__file__).with_name("atomic_dual_channel_journal_2026-08-27T2107_JST.py")
spec = importlib.util.spec_from_file_location("atomic_journal", MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)
J = mod.AtomicDualChannelJournal
encode = mod.encode_frame


def validate(seed: int = 8272026) -> dict:
    rng = random.Random(seed)
    admit = J.admit_event("b0", ["s0", "s1", "s2"], 100.0, 110.0, 8)
    s0 = J.slot_event("b0", "s0", 0.0, 104.0)
    s1 = J.slot_event("b0", "s1", 0.5, 106.0)
    close = J.close_event("b0", 111.0)
    events = [admit, s0, s1, close]
    frames = [encode(e) for e in events]
    full = b"".join(frames)
    ref, _, _ = J.recover(full)
    expected = ref.closed_rows[0]
    assert expected["block_score"] == 0.5

    prefix = b""
    cuts = failures = 0
    for idx, frame in enumerate(frames):
        for cut in range(len(frame)):
            torn = prefix + frame[:cut]
            state, valid_len, _ = J.recover(torn)
            if idx == 0:
                failures += int(state.active is not None or bool(state.closed_rows))
            elif idx < 3:
                failures += int(state.active is None or bool(state.closed_rows))
            else:
                failures += int(state.active is None or bool(state.closed_rows))
                recovery_close = state.deterministic_recovery_close(112.0)
                assert recovery_close is not None
                recovered, _, _ = J.recover(torn[:valid_len] + encode(recovery_close))
                failures += int(recovered.closed_rows != [expected])
            cuts += 1
        prefix += frame

    duplicate_blob = b"".join([frames[0], frames[0], frames[1], frames[1], frames[2], frames[2], frames[3], frames[3]])
    duplicate_state, _, _ = J.recover(duplicate_blob)
    assert duplicate_state.closed_rows == [expected]
    assert len(duplicate_state.replay_channels()[0]) == 1
    assert len(duplicate_state.replay_channels()[1]) == 1

    conflicting = J.slot_event("b0", "s0", 1.0, 105.0)
    late = J.slot_event("b0", "s2", 0.0, 112.0)
    conflict_blob = b"".join([frames[0], frames[1], encode(conflicting), frames[2], frames[3], encode(late)])
    conflict_state, _, _ = J.recover(conflict_blob)
    assert conflict_state.closed_rows == [expected]
    assert any(x["type"] == "event_id_conflict" for x in conflict_state.anomalies)
    assert any(x["type"] == "slot_after_close" for x in conflict_state.anomalies)

    campaigns = 1000
    blocks = campaign_failures = partial_recoveries = duplicate_retries = conflicting_overwrites = 0
    for campaign in range(campaigns):
        journal = b""
        expected_rows = []
        for bi in range(rng.randint(1, 5)):
            blocks += 1
            bid = f"c{campaign}b{bi}"
            n = rng.randint(1, 8)
            slots = [f"s{j}" for j in range(n)]
            admission = J.admit_event(bid, slots, 1000 + 20 * bi, 1010 + 20 * bi, 8)
            frame = encode(admission)
            if rng.random() < 0.35:
                cut = rng.randrange(len(frame))
                torn = journal + frame[:cut]
                _, valid_len, _ = J.recover(torn)
                partial_recoveries += 1
                journal = torn[:valid_len] + frame
            else:
                journal += frame
            state, _, _ = J.recover(journal)
            if state.active is None or state.active.block_id != bid:
                campaign_failures += 1
                break

            accepted = {}
            for sid in slots:
                if rng.random() < 0.72:
                    score = rng.choice([0.0, 0.25, 0.5, 0.75, 1.0])
                    event = J.slot_event(bid, sid, score, 1001 + 20 * bi + 8 * rng.random())
                    frame = encode(event)
                    if rng.random() < 0.25:
                        cut = rng.randrange(len(frame))
                        torn = journal + frame[:cut]
                        _, valid_len, _ = J.recover(torn)
                        partial_recoveries += 1
                        journal = torn[:valid_len] + frame
                    else:
                        journal += frame
                    accepted[sid] = score
                    if rng.random() < 0.15:
                        journal += frame
                        duplicate_retries += 1
                    if rng.random() < 0.08:
                        journal += encode(J.slot_event(bid, sid, 1.0 - score, 1009 + 20 * bi))
                        conflicting_overwrites += 1

            vals = [accepted.get(s, 1.0) for s in slots]
            expected_rows.append({
                "block_id": bid,
                "planned_size": n,
                "completed_canonical": len(accepted),
                "missing_or_failed": n - len(accepted),
                "block_score": sum(vals) / n,
                "exposure_weight": n / 8,
            })

            close_event = J.close_event(bid, 1011 + 20 * bi)
            frame = encode(close_event)
            if rng.random() < 0.35:
                cut = rng.randrange(len(frame))
                torn = journal + frame[:cut]
                state, valid_len, _ = J.recover(torn)
                partial_recoveries += 1
                journal = torn[:valid_len] + encode(state.deterministic_recovery_close(1012 + 20 * bi))
            else:
                journal += frame
            if rng.random() < 0.2:
                journal += frame
                duplicate_retries += 1
            state, _, _ = J.recover(journal)
            if state.closed_rows != expected_rows:
                campaign_failures += 1
                break
        if campaign_failures:
            break

    return {
        "seed": seed,
        "exhaustive_partial_frame_cut_checks": cuts,
        "exhaustive_partial_frame_failures": failures,
        "random_campaigns": campaigns,
        "random_blocks": blocks,
        "random_campaign_failures": campaign_failures,
        "partial_tail_recoveries": partial_recoveries,
        "duplicate_retries": duplicate_retries,
        "conflicting_overwrite_rejections_exercised": conflicting_overwrites,
        "reference_closed_rows": 1,
        "reference_process_replay_rows": 1,
        "reference_exposure_replay_rows": 1,
        "reference_block_score": expected["block_score"],
        "reference_exposure_weight": expected["exposure_weight"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2, sort_keys=True))
