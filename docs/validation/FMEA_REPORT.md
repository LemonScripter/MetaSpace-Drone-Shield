# Failure mode and effects analysis (draft, not independently reviewed)

Scope: the GNSS/INS divergence gate (`examples/drone_shield_v2.bio`) as a component. Severity and risk judgments are the authors' estimates; no field data. Earlier statements such as "residual risk NEGLIGIBLE" and "shifts 99% of failures" had no basis and are withdrawn.

| Component | Failure mode | Effect | What the gate does | Residual risk (authors' judgment) |
|---|---|---|---|---|
| GNSS receiver | gradual spoofing (position drifts away from the truth) | vehicle follows a false path | raises Suspect at > 20 m divergence and latches Isolated at > 50 m; a slow spoof that stays below 20 m is not detected | **medium**: depends entirely on the thresholds and on the INS drift |
| GNSS receiver | spoofing consistent with the INS (both wrong or INS aided by GNSS) | no divergence | none | **high**, not detectable by this check |
| INS | drift or fault | false divergence or hidden divergence | alarm on divergence; cannot tell which source is wrong | **medium** |
| Position sensors | NaN / infinity | comparison with NaN is false | v2 raises the alarm (proved for float32 inputs); v1 did not | low for v2 |
| RF front end | high RF power indication | possible jamming/spoofing | alarm at > -125 dBm | **not characterised**: false-alarm rate unknown |
| Gate software | wrong state value in memory | undefined behaviour | generated code moves to the lock state | low (design), not tested against memory faults |
| Gate software | defect in specification | rule not enforced | tooling now checks the rules (v1's defect was found this way) | medium: only the properties listed in the SMT report are checked |
| Flight controller | freeze, memory corruption | actuators hold the last command | **not covered**: a software gate on the same processor does not protect against its failure; an independent hardware gate is a design intention, not implemented here | not assessed |
| Telemetry link | replay of old commands | stale commands | **not covered** (no timestamp invariant implemented) | not assessed |
| Battery | voltage drop | loss of thrust | **not covered** (no battery invariant implemented) | not assessed |

Critical finding (retained): the shield does not try to repair bad data; it flags it. Its value depends on the system acting on the alarm, which is outside this repository.
