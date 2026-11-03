"""
verify_spec: a REAL Z3 check of a .bio specification against its own state machine (exact real arithmetic).

What is checked, for a given semantics (transition_first | output_first):
  P1  for every reachable state and EVERY input, each INVARIANT rule holds on the outputs emitted in that tick
      (the solver searches for a counter-example: inputs and state where a rule is violated; unsat = proved)
  P2  states of TYPE SAFETY_LOCK are absorbing (no outgoing transition can leave them)
  P3  determinism/totality of the step function is by construction (first matching guard wins), so it is not a proof obligation
Reachability: a state is reachable if it is the first state or some guard into it is satisfiable from a reachable state.

What this does NOT show: that a compiled binary implements the specification (see verify_float.py and the differential tests),
nor anything about the physical world (the sensor values are the solver's free variables).
Usage: python verify_spec.py examples/drone_shield_v1.bio [examples/drone_shield_v2.bio ...]
"""
import sys
import z3
from bio_subset import parse


def encode(cell):
    """Z3 variables for the inputs; DISTANCE(a, b) as a real variable d with d >= 0 and d*d = squared distance."""
    V = {}
    for nm, ty in cell["inputs"].items():
        if ty == "VECTOR2D": V[nm] = (z3.Real(nm + "_x"), z3.Real(nm + "_y"))
        else: V[nm] = z3.Real(nm)
    return V


class Enc:
    def __init__(self, cell):
        self.cell, self.V, self.side = cell, encode(cell), []
        self.n = 0

    def e(self, ex, env):
        k = ex[0]
        if k == "num": return z3.RealVal(str(ex[1]))
        if k == "id": return env[ex[1]]
        if k == "neg": return -self.e(ex[1], env)
        if k == "not": return z3.Not(self.e(ex[1], env))
        if k == "call":
            a, b = self.e(ex[2][0], env), self.e(ex[2][1], env)
            self.n += 1; d = z3.Real(f"dist{self.n}")
            self.side += [d >= 0, d * d == (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2]
            return d
        op = ex[1]; a = self.e(ex[2], env); b = self.e(ex[3], env)
        if op == "IMPLIES": return z3.Implies(a, b)
        if op == "AND": return z3.And(a, b)
        if op == "OR": return z3.Or(a, b)
        if op in ("==", "!="):
            a = self._num(a); b = self._num(b)
        ops = {">": lambda: a > b, "<": lambda: a < b, ">=": lambda: a >= b, "<=": lambda: a <= b, "==": lambda: a == b, "!=": lambda: a != b,
               "+": lambda: a + b, "-": lambda: a - b, "*": lambda: a * b, "/": lambda: a / b}
        return ops[op]()

    @staticmethod
    def _num(x):
        return x


def step_expr(enc, state_name, semantics):
    """returns (next-state index as a Z3 expression, outputs dict of Z3 reals) for a CONCRETE current state"""
    cell = enc.cell; names = [s["name"] for s in cell["states"]]; st = {s["name"]: s for s in cell["states"]}
    env = dict(enc.V)

    def outs_of(sname): return {v: enc.e(x, env) for v, x in st[sname]["assigns"]}
    cur = st[state_name]
    # next state: first true guard wins
    nxt = z3.IntVal(names.index(state_name))
    for tgt, g in reversed(cur["trans"]):
        nxt = z3.If(enc.e(g, env), z3.IntVal(names.index(tgt)), nxt)
    if semantics == "output_first":
        return nxt, outs_of(state_name)
    # transition_first: the outputs of the resulting state
    outs = {}
    for ov in cell["outputs"]:
        val = None
        for i in reversed(range(len(names))):
            sv = dict((v, enc.e(x, env)) for v, x in st[names[i]]["assigns"]).get(ov)
            if sv is None: continue
            val = sv if val is None else z3.If(nxt == i, sv, val)
        outs[ov] = val
    return nxt, outs


def reachable(cell, semantics):
    names = [s["name"] for s in cell["states"]]; st = {s["name"]: s for s in cell["states"]}
    reach = {names[0]}; todo = [names[0]]
    while todo:
        s = todo.pop(); enc = Enc(cell)
        env = dict(enc.V)
        prior = []
        for tgt, g in st[s]["trans"]:
            slv = z3.Solver(); gexp = enc.e(g, env)
            slv.add(enc.side); slv.add(gexp)
            for p in prior: slv.add(z3.Not(p))
            if slv.check() == z3.sat and tgt not in reach: reach.add(tgt); todo.append(tgt)
            prior.append(gexp)
    return [n for n in names if n in reach]


def check(path, semantics):
    cell = parse(open(path, encoding="utf-8").read()); names = [s["name"] for s in cell["states"]]
    print(f"\n== {cell['name']} ({path}) | semantics: {semantics}")
    reach = reachable(cell, semantics); print("reachable states:", reach, "| unreachable:", [n for n in names if n not in reach])
    ok_all = True
    for sname in reach:
        for rname, rexp in cell["rules"]:
            enc = Enc(cell); nxt, outs = step_expr(enc, sname, semantics)
            env = dict(enc.V); env.update({ov: val for ov, val in outs.items()})
            # BINARY outputs are compared with 1: outputs are real-valued here
            rule = enc.e(rexp, env)          # encode first: the rule may introduce its own DISTANCE variables
            s = z3.Solver(); s.add(enc.side)
            s.add(z3.Not(rule))
            r = s.check()
            if r == z3.unsat:
                print(f"  P1 [{sname:9s}] {rname:18s}: PROVED (no input violates it)")
            else:
                ok_all = False
                m = s.model()
                vals = {str(d): (float(m[d].as_fraction()) if m[d] is not None else None) for d in m.decls() if not str(d).startswith("dist")}
                print(f"  P1 [{sname:9s}] {rname:18s}: VIOLATED, counter-example {vals}  (z3: {r})")
    for st in cell["states"]:
        if st["type"] == "SAFETY_LOCK":
            enc = Enc(cell); nxt, _ = step_expr(enc, st["name"], semantics)
            s = z3.Solver(); s.add(enc.side); s.add(nxt != names.index(st["name"]))
            res = s.check()
            print(f"  P2 [{st['name']:9s}] absorbing (SAFETY_LOCK): {'PROVED' if res == z3.unsat else 'VIOLATED'}")
            ok_all &= res == z3.unsat
    return ok_all


if __name__ == "__main__":
    paths = sys.argv[1:] or ["../examples/drone_shield_v1.bio", "../examples/drone_shield_v2.bio"]
    summary = {}
    for p in paths:
        for sem in ("transition_first", "output_first"):
            summary[(p, sem)] = check(p, sem)
    print("\nSUMMARY (all properties proved?):")
    for (p, sem), v in summary.items(): print(f"  {p:38s} {sem:17s} {'yes' if v else 'NO'}")
