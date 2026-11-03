# Validation status and roadmap

Status: **TRL 3-4 (laboratory prototype).** Earlier versions of this repository claimed certification ("Stage 1 CERTIFIED") and readiness for SIL-3/SIL-4/NATO audits. Those claims are withdrawn: nothing here is certified, qualified or independently audited.

## 1. Where each stage stands

| Stage | Status | Evidence / gap |
|---|---|---|
| 1. Language and logic | **partial** | a subset has a parser and a reference semantics (`src/bio_subset.py`, `docs/validation/FORMAL_SEMANTICS.md`); Z3 checks of the invariants against the state machine and of the float32 step function (`docs/validation/SMT_VERIFICATION_REPORT.md`); no machine-checked formal semantics of the full language |
| 2. Tool chain | **prototype** | a generator for the subset (`src/gen_gate.py`) with differential tests against independent models; no tool qualification (DO-330) process |
| 3. Safety V&V | **draft** | HARA and FMEA drafted by the authors, not reviewed (`HARA_REPORT.md`, `FMEA_REPORT.md`) |
| 4. System level | **not done** | no software-in-the-loop, hardware-in-the-loop, flight or field test |
| 5. Assurance case | **draft with open gaps** | `ASSURANCE_CASE.md` |

## 2. What would be needed for a stronger claim

1. **Independent review** of the specification, thresholds and tool chain by a qualified party.
2. **Thresholds from data:** GNSS error and INS drift statistics for a real platform; false-alarm and miss rates.
3. **Hardware measurement:** the gate on the target controller (and, if claimed, on an FPGA), with timing measured on the device, not estimated from instruction counts.
4. **System tests:** software-in-the-loop (e.g. ArduPilot SITL), then hardware-in-the-loop, then flight tests with injected spoofing in a controlled environment.
5. **Coverage of further invariants** (staleness, battery, altitude) that older documents mentioned but this repository does not implement.
6. **Certification-oriented work** (DO-178C / DO-333 / IEC 61508) only after the above, with an external assessor.

Professional verdict: not yet certifiable, not a "100% proof" of anything beyond the stated model.
