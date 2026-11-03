# Architecture of the Drone Shield prototype

## 1. Pipeline (what exists)

```
.bio specification --(bio_subset.py: parse, reject unknown syntax)--> AST
   |-- verify_spec.py   : Z3 check of the invariants against the state machine (exact reals)
   |-- verify_float.py  : Z3 proofs about the float32 step function (NaN, infinity, distance guards)
   `-- gen_gate.py      : generate a no_std Rust gate (IEEE-754 f32, no heap, no loops)
          `-- build_gates.py -> RISC-V RV32IMC ELF -> measure_gate.py (emulator: differential test, instruction counts)
```
Everything is software. There is no FPGA/VHDL generation, no hardware synthesis, and no hardware test in this repository. Earlier statements about "< 10 ns on FPGA", "logic-as-hardware" and "immune to buffer overflow" described intentions, not implemented or measured results.

## 2. Determinism

The generated gate is a straight-line function with a small `match`: no loops, no recursion, no heap, no system calls. Its instruction count per tick therefore has a small fixed maximum; measured on the RISC-V build with soft-float arithmetic: 144 minimum, 348 median, 467 maximum (the path through the state machine and the soft-float routines cause the spread). That is bounded and small, but it is not "constant": the count varies with the inputs.
"Deterministic" here means: same inputs and state give the same outputs, and the execution time is bounded. It does not mean immune to hardware faults, memory corruption or a compromised flight controller.

## 3. Divergence guard

1. Inputs: GNSS and INS positions (2D), RF power.
2. The gate compares the squared GNSS-INS distance with 400 m² (20 m) and 2500 m² (50 m) and the RF power with -125 dBm. States: `Normal` -> `Suspect` (alarm) -> `Isolated` (alarm, latched).
3. Invalid values (NaN, infinity) fail safe because the guards are written in the negated form `NOT (x <= limit)`.
4. Limits: the check detects *divergence* between two position sources. It does not know which source is correct, cannot detect a spoof that keeps both sources consistent, and a slow drift below the threshold passes. INS drift grows with time; a fixed 50 m threshold does not remain meaningful over a long GNSS outage.

## 4. Where the gate sits (design intention, not implemented here)

The earlier claim that the gate "cannot be bypassed by an exploit in the flight controller (e.g. PX4) because it is synthesised into hardware" is true only for a separate hardware implementation, which does not exist in this repository. A software gate on the same processor as the flight controller shares its failure modes.

## 5. Cellular-automata self-healing

The earlier text about a cellular-automata layer that restores bit flips by neighbour consensus has no implementation in this repository and is withdrawn.
