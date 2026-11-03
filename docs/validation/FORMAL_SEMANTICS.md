# Formal semantics of the `.bio` subset used here

Implemented in `src/bio_subset.py` (parser and reference semantics). This document describes what the tools implement; it is not a full definition of the `.bio` language.

## Subset

```
CELL name { INTERFACE { INPUT x: T; ... OUTPUT y: T; }
            INVARIANTS { RULE r: expr; ... }
            STATES { STATE s [TYPE t] { out = expr; TRANSITION TO s2 IF expr; ... } ... } }
```
Types: `FLOAT`, `BINARY`, `VECTOR2D`. Expressions: numbers, identifiers, `DISTANCE(a, b)` on `VECTOR2D`, `+ - * /`, comparisons, `NOT`, `AND`, `OR`, `IMPLIES`. The parser rejects everything else (unknown sections, types such as `INTEGER`, malformed input).

## One tick (transition-first)

1. In the current state the `TRANSITION` clauses are tried in source order; the first whose guard is true is taken.
2. The assignments of the resulting state are executed; they are the outputs of the tick.

A state of `TYPE SAFETY_LOCK` has no outgoing transition and therefore keeps the system there. An out-of-range state value in the generated code moves to the lock state (fail-safe).
The alternative output-first semantics (emit the outputs of the current state, then move) is evaluated by the verifier; the result differs (see `SMT_VERIFICATION_REPORT.md`). A specification must say which one is meant; this repository uses transition-first.

## Invariants

Each `RULE` is a Boolean expression over the inputs and outputs of the same tick. "The rule holds" means: for every reachable state and every input, evaluating the rule on the inputs and on the outputs of the tick gives true.

## Numbers

The reference semantics uses exact reals (the Z3 check) or float64 (the Python evaluator). The generated code uses IEEE-754 float32. `DISTANCE(a, b) <op> T` compiles to `d2 <op> T·T` with `d2 = (ax-bx)² + (ay-by)²` (no square root). A comparison with NaN is false. To make a missing or invalid value fail safe, guards are written as `NOT (x <= limit)`, not `x > limit`.

## What is not defined here

Timing (clock, jitter, hardware synthesis), the `STALENESS`, `RATE_OF_CHANGE` and fuzzy-logic constructs, temporal properties beyond one tick, and the proprietary compiler. Statements in earlier versions about "100% state-space coverage", "every logic gate evaluated every 500 ns" and "exactly one valid output proven by Z3" referred to none of this and are withdrawn.
