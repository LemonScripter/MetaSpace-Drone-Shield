# Assurance case (draft, Goal Structuring Notation style)

Status: **draft with open gaps.** This is not a completed or certified assurance case. Each evidence item names what exists in the repository; each gap is listed.

## G1 Goal
When GNSS and INS positions diverge by more than a configured limit, or the RF power exceeds a limit, the shield raises an alarm within one control tick, and an invalid sensor value never silences the alarm.

Scope: the gate's decision logic only. It is not a claim about the safety of the whole drone.

| Strategy / sub-goal | Evidence in this repository | Gap |
|---|---|---|
| S1 The specification enforces its own invariants | `verify_spec.py`: v2 proved under transition-first semantics, v1's defect found (`results/verify_spec.txt`) | proofs cover the model, not a hardware or flight context |
| S2 Invalid input fails safe | `verify_float.py`: F1a, F1b, F4 proved for all float32 inputs | sensor-level plausibility (stuck values, slow drift) is not addressed |
| S3 The distance guard is accurate up to rounding | `verify_float.py` F2, F3: PROVED relative to the standard rounding model; the bit-level attempt timed out (`results/verify_float.txt`) | conditional on the model, no bit-level proof; outside the 2^-20 relative band the result may go either way |
| S4 The code matches the specification | `measure_gate.py`: 0 mismatches / 100,803 vectors against an independent float32 model; 0 differences against the real-valued spec outside the band | differential testing, not a proof; generator and parser are unqualified tools |
| S5 The gate is fast enough | emulator instruction counts: 144 / 348 / 467 per tick; time ESTIMATED at 2-4 µs on a 160 MHz RISC-V core without FPU | no hardware timing; interrupt and bus effects not measured |
| S6 The thresholds are suitable | none | the 20 m / 50 m / -125 dBm values were chosen by the authors; no analysis of GNSS error statistics or INS drift for a real platform |
| S7 The hazards are identified | draft HARA and FMEA (`HARA_REPORT.md`, `FMEA_REPORT.md`) | prepared by the authors, no independent review, no field data |

## Gaps that block any certification claim
* No independent assessment of any kind; no tool qualification; no requirements-based test coverage measurement (MC/DC).
* No hardware-in-the-loop, flight or field test; no ArduPilot/PX4 integration.
* No evidence for spoofing scenarios in which GNSS and INS stay consistent, or in which the INS itself is wrong.
* No analysis of false-alarm rate against real GNSS error behaviour.

## Operational feedback
The earlier claim of "continuous self-certification" and "automated invariant boundary tightening" has no implementation here and is withdrawn.
