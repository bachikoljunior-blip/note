import json


class Relay:
    def __init__(self):
        self.next_id = 1
        self.outbox = []
        self.delivered = []

    def enqueue(self, logical_effect):
        transport_id = f"msg-{self.next_id}"
        self.next_id += 1
        self.outbox.append({"transport_id": transport_id, "logical_effect": logical_effect})
        return transport_id

    def drain(self):
        while self.outbox:
            self.delivered.append(self.outbox.pop(0))

    def count(self, logical_effect):
        return sum(1 for item in self.delivered if item["logical_effect"] == logical_effect)

    def has_effect(self, logical_effect):
        return any(item["logical_effect"] == logical_effect for item in self.delivered)


def run_probe():
    effect = "effect-42"

    # Arm A: the effect becomes deliverable before a later gate reports failure.
    bad = Relay()
    first_id = bad.enqueue(effect)
    bad.drain()
    first = {"status": "failed_to_start", "transport_id": first_id}
    retry_id = bad.enqueue(effect)
    bad.drain()
    retry = {"status": "accepted", "transport_id": retry_id}
    bad_result = {
        "first": first,
        "retry": retry,
        "delivered_count": bad.count(effect),
        "delivered_transport_ids": [item["transport_id"] for item in bad.delivered],
    }

    # Arm B: gate before enqueue; a failed start leaves no deliverable effect.
    gate_first = Relay()
    first = {"status": "failed_to_start", "transport_id": None}
    retry_id = gate_first.enqueue(effect)
    gate_first.drain()
    retry = {"status": "accepted", "transport_id": retry_id}
    gate_first_result = {
        "first": first,
        "retry": retry,
        "delivered_count": gate_first.count(effect),
        "delivered_transport_ids": [item["transport_id"] for item in gate_first.delivered],
    }

    # Arm C: authoritative effect readback prevents retry after a misleading local failure.
    reconcile = Relay()
    first_id = reconcile.enqueue(effect)
    reconcile.drain()
    if reconcile.has_effect(effect):
        first = {"status": "accepted_via_readback", "transport_id": first_id, "created": True}
        retry = {"status": "skipped", "reason": "logical_effect_already_delivered"}
    else:
        first = {"status": "failed_to_start", "transport_id": first_id, "created": True}
        retry_id = reconcile.enqueue(effect)
        reconcile.drain()
        retry = {"status": "accepted", "transport_id": retry_id}
    reconcile_result = {
        "first": first,
        "retry": retry,
        "delivered_count": reconcile.count(effect),
        "delivered_transport_ids": [item["transport_id"] for item in reconcile.delivered],
    }

    result = {
        "schema_version": 1,
        "probe": "false_failure_after_effect_then_retry",
        "logical_effect": effect,
        "arms": {
            "bad_enqueue_before_gate": bad_result,
            "gate_before_enqueue": gate_first_result,
            "keyed_reconcile": reconcile_result,
        },
        "assertions": {
            "bad_duplicates": bad_result["delivered_count"] == 2,
            "gate_first_single_effect": gate_first_result["delivered_count"] == 1,
            "readback_single_effect": reconcile_result["delivered_count"] == 1,
        },
        "scope": "single-process deterministic simulation; not production network or relay evidence",
    }
    assert all(result["assertions"].values())
    return result


if __name__ == "__main__":
    print(json.dumps(run_probe(), indent=2, sort_keys=True))
