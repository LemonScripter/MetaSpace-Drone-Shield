# SMT verification report (replaces "SMT_CERTIFICATE.md")

This is a report of what the solver established, with its limits. It is not a certificate. Logs: `results/verify_spec.txt`, `results/verify_float.txt`. Tools: `src/verify_spec.py`, `src/verify_float.py`. Solver: Z3 4.15.

## 1. Specification level (exact real arithmetic) — `verify_spec.py`

Model: the state machine of the `.bio` file; inputs are free real variables (no sensor model); `DISTANCE(a, b)` is a real variable `d >= 0` with `d·d =` squared distance. For every reachable state and every input the solver looks for a violation of each `RULE`; no counter-example (`unsat`) means the rule holds in that state for all inputs.

| Specification | Semantics | spatial_integrity | rf_integrity | SAFETY_LOCK absorbing |
|---|---|---|---|---|
| v1 (original) | transition-first | proved in all states | **violated in `Normal`** (RF -124 dBm, alarm stays 0) | proved |
| v1 (original) | output-first | **violated in `Normal`** (distance 51 m, alarm stays 0 for one tick) | **violated in `Normal`** | proved |
| v2 | transition-first | proved | proved | proved |
| v2 | output-first | **violated in `Normal`** (one-tick lag) | **violated in `Normal`** | proved |

Meaning: the defect of v1 is real. v2 is correct **only** if the implementation evaluates the guards on the current inputs before emitting the outputs (transition-first); an output-first implementation would have a one-tick lag. The generated gate (`gen_gate.py`) is transition-first.
What this does not show: nothing about sensors, thresholds, timing or the physical world.

## 2. Float32 step function (IEEE-754) — `verify_float.py`

The model is the exact operation order of the generated code: `dx = gx - ix; dy = gy - iy; d2 = dx·dx + dy·dy` in float32 with round-to-nearest-even; guards `!(d2 <= 400 && rf <= -125)` and `!(d2 <= 2500)`.

| Property | Claim | Status |
|---|---|---|
| F1a | any NaN input, any infinite coordinate, or rf = +inf makes the `Normal` guard fire | **PROVED** for all float32 inputs |
| F1b | any NaN or infinite coordinate makes the `Suspect` guard fire (escalation) | **PROVED** for all float32 inputs |
| F4 | rf > -125 (not NaN) makes the `Normal` guard fire | **PROVED** for all float32 inputs |
| F2, F3 | the distance guards agree with the exact distance outside a relative band of 2^-20 around the limit (no missed alarm above, no false alarm below) | see section 3 |

An invalid rf alone does not escalate `Suspect`, but `Suspect` already has `alarm = 1`, so the alarm output is 1 for every invalid input.

## 3. Distance guards near the limit (F2, F3)

Z3 cannot decide the mixed float/real formulation directly (first attempt: `unknown`, which is not a proof). Two approaches were tried; the outcome of each check is in `results/verify_float.txt`.

1. **From the standard rounding model** (`fl(z) = z(1+e) + d`, |e| <= 2^-24, |d| <= 2^-100, Higham, *Accuracy and Stability of Numerical Algorithms*, Thm 2.2). Over the reals Z3 checks that an exact squared distance above the limit by a relative margin of 2^-20 gives a computed value above the limit, and the mirror statement below the limit. **All four checks PROVED** (about 22-30 s each). The result is conditional on that standard model (and, for the "above the limit" direction, on a squared distance up to 1e9 m²; larger values overflow to infinity and fall under F1-type handling). It does not inspect the processor's arithmetic bit by bit.
2. **Bit-level on a bounded domain** (every float32 with 2^-8 <= |x| <= 2^8 or zero, exact reference distance in a 70-bit-mantissa format). All four checks ended with `UNKNOWN` (solver timeout after 300 s). **This is not a proof and no claim is made from it.** The code stays in `verify_float.py` behind the `--bitlevel` option for anyone who wants to retry with more time or a different solver.

So for the distance limits the repository has: (a) a proof conditional on the standard rounding model, (b) differential testing of the compiled gate on boundary vectors around 20 m and 50 m (0 mismatches against an independent float32 model, `results/measure_gate_v2.txt`), and (c) no bit-level proof.

## 4. What the proofs do not cover

* The compiled binary: it is checked by differential testing (`src/measure_gate.py`, 100,803 vectors, 0 mismatches against an independent float32 model, 0 differences against the real-valued specification outside the rounding band), which is evidence, not proof.
* The generator and the parser are not qualified tools.
* Sensor faults, spoofing that keeps GNSS and INS consistent, INS drift, threshold choice, timing on hardware, the flight controller.
