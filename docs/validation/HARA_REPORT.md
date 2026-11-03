# Hazard and risk analysis (draft, not independently reviewed)

Prepared by the authors in the style of IEC 61508 / ISO 26262 hazard analysis. **No safety integrity level has been assessed or achieved.** "SIL-3" in earlier versions was a target, and no evidence for it exists in this repository.

## Hazards (considered)

| ID | Hazard | Cause considered | Detection by the shield | Status of the mitigation |
|---|---|---|---|---|
| H1 | Fly-away | GNSS spoofing that moves the reported position while the INS remains correct | alarm when GNSS-INS distance exceeds 20 m (Suspect) and latch at 50 m (Isolated) | rule specified, spec and float32 gate checked (see `SMT_VERIFICATION_REPORT.md`); the reaction of the vehicle to the alarm (failsafe, return, landing) is **not** part of this repository |
| H2 | Alarm silenced by invalid data | NaN or infinity from a failed sensor | v2 guards fail safe (alarm) | proved for float32 inputs (F1a, F1b) |
| H3 | RF-based indication ignored | RF power above -125 dBm | alarm (Suspect) | proved at the specification and float32 level (F4) |
| H4 | Spurious alarm / nuisance isolation | noisy GNSS near the limits, thresholds too tight | none | **not analysed**; `Isolated` is latched, so a false alarm is not recoverable inside the gate |
| H5 | Spoof invisible to the gate | both GNSS and INS wrong or consistent; slow spoof below the drift of the INS | none | **not covered**; outside the capability of a divergence check |
| H6 | Unintended altitude loss | faulty altimeter | **no rule exists** for altitude in the shipped specification | not mitigated; an earlier "barometric vs GPS altitude" invariant was never implemented |

## Requirements traceability (honest status)

| Requirement | Implementation | Verification status |
|---|---|---|
| REQ-1 Alarm when GNSS-INS distance > 50 m, within the same tick | rule `spatial_integrity`, v2 | proved at specification level (transition-first); float32 distance guard see F2/F3 |
| REQ-2 Alarm when RF power > -125 dBm | rule `rf_integrity`, v2 | proved (specification, F4) |
| REQ-3 Isolated state is latched | `STATE Isolated TYPE SAFETY_LOCK` | proved absorbing |
| REQ-4 Invalid sensor values never suppress the alarm | negated guards | proved for float32 (F1a, F1b) |
| REQ-5 Reaction within 100 ms | not specified in the `.bio` | **no verification**; the gate step takes microseconds (estimated), the end-to-end latency (sensor, bus, flight controller) is unknown |
| REQ-6 Battery-aware landing, temporal guard, replay protection | mentioned in older documents | **not implemented** in this repository |
