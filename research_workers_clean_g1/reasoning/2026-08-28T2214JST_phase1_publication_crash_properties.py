from dataclasses import dataclass, replace

@dataclass(frozen=True)
class PubState:
    checkpoint: str | None = None
    checkpoint_digest: str | None = None
    verified: bool = False
    pointer: str = "P0"
    preread_pointer: str = "P0"
    cas_outcome: str | None = None
    postread_pointer: str | None = None
    receipt: tuple | None = None

def step(st, event):
    if event == "create":
        if st.checkpoint is None:
            return replace(st, checkpoint="C", checkpoint_digest="D")
        assert (st.checkpoint, st.checkpoint_digest) == ("C", "D")
        return st
    if event == "verify":
        if st.checkpoint == "C" and st.checkpoint_digest == "D":
            return replace(st, verified=True)
        return st
    if event == "cas":
        if not st.verified:
            return st
        if st.pointer == "C":
            return replace(st, cas_outcome="already_current")
        if st.pointer == st.preread_pointer:
            return replace(st, pointer="C", cas_outcome="success")
        return replace(st, cas_outcome="failure")
    if event == "postread":
        if st.cas_outcome is None:
            return st
        return replace(st, postread_pointer=st.pointer)
    if event == "receipt":
        if st.postread_pointer is None or not st.verified:
            return st
        return replace(
            st,
            receipt=(st.checkpoint, st.checkpoint_digest, st.cas_outcome, st.postread_pointer),
        )
    if event == "other":
        return replace(st, pointer="P2")
    raise ValueError(event)

def recover(st):
    s = replace(
        st,
        verified=False,
        preread_pointer=st.pointer,
        cas_outcome=None,
        postread_pointer=None,
        receipt=None,
    )
    s = step(s, "create")
    s = step(s, "verify")
    if s.pointer == "P2":
        s = replace(s, cas_outcome="blocked_by_newer_pointer")
    else:
        s = step(s, "cas")
    s = step(s, "postread")
    s = step(s, "receipt")
    return s

def main():
    protocol = ["create", "verify", "cas", "postread", "receipt"]
    cases = 0
    for other_pos in [None, 0, 1, 2, 3, 4, 5]:
        sequence = protocol.copy()
        if other_pos is not None:
            sequence = protocol[:other_pos] + ["other"] + protocol[other_pos:]
        for crash_cut in range(len(sequence) + 1):
            st = PubState()
            for event in sequence[:crash_cut]:
                st = step(st, event)

            if st.receipt is not None:
                checkpoint, digest, _, postread = st.receipt
                assert (checkpoint, digest) == ("C", "D")
                assert st.verified
                assert postread == st.postread_pointer

            recovered = recover(st)
            if st.checkpoint == "C":
                assert recovered.checkpoint == "C"
                assert recovered.checkpoint_digest == "D"
            if st.pointer == "P2":
                assert recovered.pointer == "P2"
                assert recovered.cas_outcome == "blocked_by_newer_pointer"
            assert recovered.receipt is not None
            assert recovered.receipt[3] == recovered.postread_pointer == recovered.pointer
            cases += 1

    print({"publication_crash_interleavings": cases})

if __name__ == "__main__":
    main()
