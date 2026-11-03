# MetaSpace Drone Shield: a small, checkable safety gate for GNSS-spoofing detection

**Status: research prototype (TRL 3-4). Nothing in this repository is certified, qualified or audited by an external body.**
Every result below is produced by a script in this repository (logs in `results/`) and is labelled **PROVED** (a solver established it, for the stated model), **MEASURED**, **ESTIMATED** or **NOT DONE**. See [`CHANGES.md`](CHANGES.md) for the correction of the previous version of this repository.

## What it is

A tiny state machine that raises an alarm when the GNSS position and the inertial (INS) position diverge, or when the received RF power is suspiciously high:

```
Normal  --(distance > 20 m  or  RF power > -125 dBm)-->  Suspect (alarm)  --(distance > 50 m)-->  Isolated (alarm, latched)
```

The rule is written in the `.bio` specification language (`examples/drone_shield_v2.bio`). This repository contains:

| Tool (`src/`) | What it does |
|---|---|
| `bio_subset.py` | a real parser for the `.bio` subset used here (rejects anything it does not understand) and a reference semantics |
| `verify_spec.py` | Z3 check of the invariants against the state machine, exact real arithmetic, two evaluation-order semantics |
| `verify_float.py` | Z3 proofs about the float32 (IEEE-754) step function the generated code implements, including NaN and infinity |
| `gen_gate.py`, `build_gates.py` | generate a `no_std` Rust gate from the specification and build it for RISC-V RV32IMC (ESP32-C3-class core, no FPU) |
| `measure_gate.py` | runs the gate in the Unicorn emulator, compares it with independent models, counts executed instructions |
| `audit.py` | regression checks of the tooling itself (exit code 0 only if everything holds) |

## Results

### 1. The specification shipped before had a defect (PROVED, found by the solver)
`examples/drone_shield_v1.bio` (the original) does **not** satisfy its own invariant `rf_power > -125 IMPLIES alarm == 1`: in state `Normal` the output is `alarm = 0` and the transition guard only looks at the distance, so RF power of -124 dBm raises no alarm. If outputs are emitted before the transition is taken, the spatial rule is violated too (one tick of lag, for example a 51 m jump). `examples/drone_shield_v2.bio` fixes the guard and is proved correct under the *transition-first* semantics (`results/verify_spec.txt`).

### 2. NaN and infinity: the old form fails open, the new form fails safe (PROVED and MEASURED)
A comparison with NaN is false in IEEE-754. A guard `distance > 20` is therefore false for a NaN sensor value and no alarm is raised. v2 writes the guard in the negated form `NOT (distance <= 20 AND rf <= -125)`. Z3 proves for **all** float32 inputs that any NaN or infinite input raises the alarm (F1a, F1b) and that `rf > -125` raises it (F4). In the emulator, the v1 gate stays silent for NaN coordinates and NaN RF power, the v2 gate raises the alarm (`results/measure_gate_v1.txt`, `results/measure_gate_v2.txt`). The distance-boundary guards (F2, F3) are proved only relative to the standard floating-point rounding model; a bit-level attempt timed out (`UNKNOWN`). Details: `docs/validation/SMT_VERIFICATION_REPORT.md`.

### 3. The compiled gate matches the specification (MEASURED)
The generated RISC-V gate was run on 100,803 test vectors (random, boundary values around 20 m and 50 m, NaN, infinities, subnormals, invalid state values). It agrees exactly with an independently written float32 model (0 mismatches), and with the real-valued specification semantics on 74,410 finite vectors outside a relative band of 2e-6 around the distance limits (0 differences). This is differential testing, not a proof about the binary.

### 4. Cost on a cheap controller (MEASURED instruction counts, ESTIMATED time)
Per tick, on the RV32IMC build with soft-float arithmetic: **144 / 348 / 467 instructions (minimum / median / maximum)**, code size 12.7 KB. At 160 MHz this is about **2-4 microseconds** (estimated with assumed cycles per instruction, 1 to roughly 1.3 on average; no hardware was used). The earlier claim of "0.0005 ms" (0.5 microseconds, about 80 cycles) is **not** supported on this core: the gate needs more than 80 instructions. A hardware (FPGA) implementation was never built or measured here.

## What is NOT claimed

* Not certified, not "Stage 1 certified", not audited by anyone. The documents under `docs/` are drafts.
* No claim that a drone equipped with the gate cannot crash, or is immune to spoofing or electronic warfare. The gate detects *divergence* between GNSS and INS; a slow spoof that the INS drift masks, a spoof of both, an INS fault or a threshold set too tight or too loose are outside what it can tell.
* The proofs are about the **specification model** and the **float32 step function**. They do not cover the physical world, the sensors, the flight controller, the thresholds' suitability, or a hardware implementation.
* No hardware-in-the-loop test, no flight test, no field trial, no ArduPilot/PX4 integration. The three demos under `examples/` are illustrative simulations with synthetic data.
* The `.bio` examples `af447_speed_shield.bio` and `financial_trading_shield.bio` use syntax beyond the subset the tools here understand; they are **not** covered by the tools.

## Reproduce

```
pip install -r requirements.txt           # z3-solver, numpy, unicorn, pyelftools (+ Flask for the demo server)
rustup target add riscv32imc-unknown-none-elf
cd src
python audit.py                           # tool regression checks
python verify_spec.py                     # spec-level Z3 check (v1 vs v2, two semantics)
python verify_float.py 300                # float32 proofs (about 2 minutes; add --bitlevel for the optional bit-level attempt, which times out)
python build_gates.py                     # generate + build ../build/gate_v1.elf and gate_v2.elf
python measure_gate.py ../build/gate_v2.elf v2 60000
python measure_gate.py ../build/gate_v1.elf v1 60000
```

## Licence and development

**This project is engineered by MetaSpace Technologies** *(a deep-tech division of Citrom Media Deep Tech Holdings)*.

* **Open validation core:** the verification modules and examples in this repository are licensed under **MIT** (see `LICENSE`).
* **Commercial runtime:** the MetaSpace Deterministic Engine, FPGA synthesis tools and the Pro Compiler are proprietary and are **not** part of this repository.
* Patent reference: OSIM Nr. 20251221-2230 (patent pending).

Documentation and enterprise access: <https://metaspace.bio>
