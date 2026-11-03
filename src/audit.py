"""
audit: regression checks of this repository's own tooling (no eval, no hard-coded verdicts). Exit code 0 only if every check holds.
It does NOT certify anything: it checks that the tools still find what they are known to find.
  1. the parser accepts the two example specifications and REJECTS malformed input
  2. the Z3 spec check finds the known defect in v1 (rule rf_integrity in state Normal) and proves v2 (transition-first semantics)
  3. the reference semantics behaves as documented on hand-computed cases
Usage (from src/):  python audit.py
"""
import io, sys, contextlib
import z3
from bio_subset import parse, step, BioError
import verify_spec

fails = []


def check(name, cond):
    print(("PASS  " if cond else "FAIL  ") + name)
    if not cond: fails.append(name)


v1 = open("../examples/drone_shield_v1.bio", encoding="utf-8").read(); v2 = open("../examples/drone_shield_v2.bio", encoding="utf-8").read()
c1, c2 = parse(v1), parse(v2)
check("parser: v1 and v2 parse, three states each", len(c1["states"]) == 3 and len(c2["states"]) == 3)
for bad in ("CELL X { INTERFACE { INPUT a: FLOAT } }", "CELL X { STATES { STATE A { TRANSITION TO B IF 1 > 0; } } }", "CELL X { INTERFACE { INPUT a: INTEGER; } }", "garbage"):
    try:
        parse(bad); check(f"parser rejects {bad[:30]!r}", False)
    except BioError:
        check(f"parser rejects {bad[:30]!r}", True)

with contextlib.redirect_stdout(io.StringIO()):
    r1 = verify_spec.check("../examples/drone_shield_v1.bio", "transition_first")
    r2 = verify_spec.check("../examples/drone_shield_v2.bio", "transition_first")
check("z3: v1 is NOT proved (known defect: RF alarm not raised in state Normal)", not r1)
check("z3: v2 is proved under transition-first semantics", r2)

# hand-computed reference cases (v2): state, gps, ins, rf -> (next state, alarm)
cases = [("Normal", (0, 0), (0, 0), -130.0, "Normal", 0), ("Normal", (0, 0), (0, 25), -130.0, "Suspect", 1), ("Normal", (0, 0), (0, 0), -120.0, "Suspect", 1),
         ("Suspect", (0, 0), (0, 25), -130.0, "Suspect", 1), ("Suspect", (0, 0), (0, 60), -130.0, "Isolated", 1), ("Isolated", (0, 0), (0, 0), -130.0, "Isolated", 1)]
for s, g, i, rf, ns, al in cases:
    n, o = step(c2, s, dict(gps_coord=g, ins_coord=i, rf_power=rf))
    check(f"semantics v2: {s} gps={g} ins={i} rf={rf} -> {ns}, alarm {al}", n == ns and int(o["alarm"]) == al)
print("\nALL CHECKS PASSED" if not fails else f"\n{len(fails)} CHECK(S) FAILED")
sys.exit(1 if fails else 0)
