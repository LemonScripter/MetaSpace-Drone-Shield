# Correction notice (2026-11-03)

An earlier version of this repository presented tools and documents as a certified and mathematically proven safety layer. On review, the code did not do what the documents said. This version replaces them. The old files stay in the git history.

## What was wrong

* **`src/verification/smt_solver.py` proved nothing.** It printed `PROVED_DETERMINISTIC` and `Confidence: 1.0 (Mathematical Certainty)` and returned `True` without any logic.
* **`src/compiler/parser.py` ignored its input.** It tokenised the file and then returned a fixed result (`"cell": "DroneShield_V1"`).
* **`metaspace_smt_engine.py` was a tautology.** It asserted the rule, asserted that the rule's antecedent holds and that the lock is off, and found that to be unsatisfiable. That only shows that the rule agrees with itself, not that the state machine or any implementation enforces it. The "proof hash" was a fixed string and the text called the result "bulletproof".
* **`metaspace_auditor.py` certified itself.** It evaluated four hand-written test inputs with `eval` and then wrote `"overall_status": "CERTIFIED"`. Its "latency determinism" test timed the expression `2**20`, which says nothing about a gate.
* **`metaspace_compiler_v2.py` carried a fixed "Z3-VERIFIED" hash as an input parameter** and printed "Stage 2 Tool Qualified" into the generated header. The VHDL it produced always contained the single comparison `dist_raw < 50`, independent of the specification (a second invariant such as `speed < 20` never reached the hardware).
* **`metaspace_core_engine.py` could not read the repository's own `.bio` files.** It searched for `INVARIANT:` and `STATE:`, while the examples use `RULE name:` and `STATE Name {`.
* **The example specification had a real defect** (see README, result 1), and nobody had noticed because nothing checked it.
* **The documents claimed more than any evidence supports:** "CERTIFIED (Audit #MS-001)", "PROVED (Audit #001)", "100% mathematical integrity", "ready for NATO / DoD / SIL-4 audits", "a MetaSpace-equipped machine CANNOT crash", "99% of failures", residual risk "NEGLIGIBLE", "< 10 ns on FPGA", "0.0005 ms", "SIL-3", and "SITL simulations (ArduPilot) prove resilience". None of this exists in the repository (no certification body, no FPGA, no SITL test, no timing evidence). The thresholds also contradicted each other (20 m, 30 m, 50 m).
* **The website (`index.html`) showed a "Certified Stage 1" badge, "PROVED", "SIL-3", "ZERO jitter", and scripted audit-log lines** such as `[SUCCESS] State-Space Coverage: 100.0%` and `Timing: 0.0005 ms avg / 1M samples`, none of which was produced by a run. The "Operational Benchmarking" charts used hand-typed numbers.

## What this version contains instead

A parser that rejects what it does not understand, a Z3 check of the invariants against the state machine (it finds the v1 defect), Z3 proofs about the float32 step function including NaN and infinity, a generator that produces the gate from the specification, an emulator-based differential test and instruction count, and documents rewritten to say what is proved, measured, estimated, and not done.

## Still open (not fixed by this version)

* The distance guards near the limits (F2/F3) are proved only relative to the standard floating-point rounding model; the bit-level attempt on a bounded domain timed out (`UNKNOWN`, no claim). See `docs/validation/SMT_VERIFICATION_REPORT.md`.
* The tool chain is not qualified (no DO-330 process), nothing is certified, there is no hardware or flight testing, and no FPGA implementation.
* `examples/af447_speed_shield.bio` and `examples/financial_trading_shield.bio` are not covered by the tools; the simulations in `examples/` and `app.py` are illustrative.
* Licence text: `LICENSE` is MIT. An untracked local file (`docs/legal/INVENTION_STATEMENT.md`) states "No License Granted" and contains verification claims that do not hold; it should not be published in its current form.
