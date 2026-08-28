from dataclasses import dataclass, replace
from itertools import product

@dataclass(frozen=True)
class HState:
    offer_id: str | None = None
    owner: str = "S"
    generation: int = 7
    committed_handoff: str | None = None
    local_status: str = "ACTIVE"
    accepted_effects: tuple = ()

def step(st, event):
    effects = list(st.accepted_effects)
    if event == "offer":
        return replace(st, offer_id="H1")
    if event == "accept":
        if st.offer_id != "H1":
            return st
        if st.owner == "S" and st.generation == 7:
            return replace(st, owner="T", generation=8, committed_handoff="H1")
        if st.owner == "T" and st.generation == 8 and st.committed_handoff == "H1":
            return st
        return st
    if event == "accept_foreign":
        return st
    if event == "observe":
        if st.owner == "T" and st.generation == 8 and st.committed_handoff == "H1":
            return replace(st, local_status="HANDED_OFF")
        return st
    if event == "stale_ack":
        return st
    if event == "source_effect":
        if st.owner == "S" and st.generation == 7:
            effects.append(("S", 7))
        return replace(st, accepted_effects=tuple(effects))
    if event == "target_effect":
        if st.owner == "T" and st.generation == 8:
            effects.append(("T", 8))
        return replace(st, accepted_effects=tuple(effects))
    if event == "crash":
        return st
    raise ValueError(event)

def main():
    events = [
        "offer", "accept", "accept_foreign", "observe", "stale_ack",
        "source_effect", "target_effect", "crash",
    ]
    cases = 0
    for length in range(7):
        for sequence in product(events, repeat=length):
            st = HState()
            transfer_count = 0
            previous_generation = st.generation
            for event in sequence:
                old = st
                st = step(st, event)
                if st.generation > previous_generation:
                    transfer_count += 1
                assert st.generation >= previous_generation
                assert transfer_count <= 1
                previous_generation = st.generation

                if st.local_status == "HANDED_OFF":
                    assert st.owner == "T"
                    assert st.generation == 8
                    assert st.committed_handoff == "H1"

                if old.owner == "T" and event == "source_effect":
                    assert st.accepted_effects == old.accepted_effects

                if event in ("accept_foreign", "stale_ack", "crash"):
                    assert (st.owner, st.generation, st.committed_handoff) == (
                        old.owner, old.generation, old.committed_handoff
                    )

            if st.owner == "T":
                assert step(st, "accept") == st
            cases += 1

    print({"handoff_event_sequences_len_le_6": cases})

if __name__ == "__main__":
    main()
