"""
bio_subset: a parser for the subset of the .bio language used by the Drone Shield examples, plus an executable reference semantics.

Supported: CELL / INTERFACE (INPUT, OUTPUT; types FLOAT, BINARY, VECTOR2D) / INVARIANTS (RULE name: expr;) / STATES (STATE name [TYPE t] { out = expr; TRANSITION TO s IF expr; }).
Expressions: numbers, identifiers, DISTANCE(a, b) on VECTOR2D, + - * /, comparisons (> < >= <= == !=), NOT, AND, OR, IMPLIES.
Everything else is rejected with an error (no silent acceptance, unlike the previous tokenizer that returned a fixed AST).

Reference semantics ("transition-first", Mealy-style), one tick:
  1. in the current state, the transitions are tried in source order; the first whose guard is true is taken (state changes),
  2. the assignments of the (possibly new) state are executed; the outputs are those assignments.
The alternative "output-first" (Moore-style) semantics emits the outputs of the current state and moves afterwards; the verifier checks both.
"""
import re

TOKEN = re.compile(r"\s*(?:(//[^\n]*)|(/\*.*?\*/)|(\d+\.\d*|\d+)|([A-Za-z_][A-Za-z0-9_]*)|(>=|<=|==|!=|[><{}();:,=+\-*/]))", re.S)
KEYWORDS = {"CELL", "INTERFACE", "INPUT", "OUTPUT", "INVARIANTS", "RULE", "STATES", "STATE", "TYPE", "TRANSITION", "TO", "IF", "IMPLIES", "AND", "OR", "NOT"}


class BioError(Exception):
    pass


def tokenize(src):
    pos, out = 0, []
    src = src.rstrip()
    while pos < len(src):
        m = TOKEN.match(src, pos)
        if not m or m.end() == pos:
            raise BioError(f"unexpected character at offset {pos}: {src[pos:pos+20]!r}")
        pos = m.end()
        if m.group(1) or m.group(2):
            continue
        if m.group(3):
            out.append(("NUM", float(m.group(3))))
        elif m.group(4):
            w = m.group(4)
            out.append(("KW" if w in KEYWORDS else "ID", w))
        else:
            out.append(("OP", m.group(5)))
    return out


class Parser:
    def __init__(self, toks):
        self.t, self.i = toks, 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else ("EOF", None)

    def next(self):
        tok = self.peek(); self.i += 1; return tok

    def expect(self, kind, val=None):
        tok = self.next()
        if tok[0] != kind or (val is not None and tok[1] != val):
            raise BioError(f"expected {val or kind}, found {tok[1]!r} (token {self.i})")
        return tok[1]

    def accept(self, kind, val):
        if self.peek() == (kind, val):
            self.i += 1; return True
        return False

    # ---- expressions
    def expr(self):
        a = self.or_()
        if self.accept("KW", "IMPLIES"):
            return ("bin", "IMPLIES", a, self.expr())
        return a

    def or_(self):
        a = self.and_()
        while self.accept("KW", "OR"): a = ("bin", "OR", a, self.and_())
        return a

    def and_(self):
        a = self.not_()
        while self.accept("KW", "AND"): a = ("bin", "AND", a, self.not_())
        return a

    def not_(self):
        if self.accept("KW", "NOT"): return ("not", self.not_())
        return self.cmp_()

    def cmp_(self):
        a = self.arith()
        if self.peek()[0] == "OP" and self.peek()[1] in (">", "<", ">=", "<=", "==", "!="):
            op = self.next()[1]
            return ("bin", op, a, self.arith())
        return a

    def arith(self):
        a = self.term()
        while self.peek()[0] == "OP" and self.peek()[1] in ("+", "-"):
            op = self.next()[1]; a = ("bin", op, a, self.term())
        return a

    def term(self):
        a = self.factor()
        while self.peek()[0] == "OP" and self.peek()[1] in ("*", "/"):
            op = self.next()[1]; a = ("bin", op, a, self.factor())
        return a

    def factor(self):
        k, v = self.next()
        if k == "NUM": return ("num", v)
        if k == "OP" and v == "-": return ("neg", self.factor())
        if k == "OP" and v == "(":
            e = self.expr(); self.expect("OP", ")"); return e
        if k == "ID":
            if self.accept("OP", "("):
                args = []
                if not self.accept("OP", ")"):
                    args.append(self.expr())
                    while self.accept("OP", ","): args.append(self.expr())
                    self.expect("OP", ")")
                return ("call", v, args)
            return ("id", v)
        raise BioError(f"unexpected token {v!r} in expression")

    # ---- structure
    def cell(self):
        self.expect("KW", "CELL"); name = self.expect("ID"); self.expect("OP", "{")
        cell = dict(name=name, inputs={}, outputs={}, rules=[], states=[])
        while not self.accept("OP", "}"):
            sec = self.next()
            if sec == ("KW", "INTERFACE"):
                self.expect("OP", "{")
                while not self.accept("OP", "}"):
                    d = self.expect("KW")
                    if d not in ("INPUT", "OUTPUT"): raise BioError(f"INTERFACE expects INPUT/OUTPUT, found {d}")
                    nm = self.expect("ID"); self.expect("OP", ":"); ty = self.expect("ID"); self.expect("OP", ";")
                    if ty not in ("FLOAT", "BINARY", "VECTOR2D"): raise BioError(f"unsupported type {ty}")
                    (cell["inputs"] if d == "INPUT" else cell["outputs"])[nm] = ty
            elif sec == ("KW", "INVARIANTS"):
                self.expect("OP", "{")
                while not self.accept("OP", "}"):
                    self.expect("KW", "RULE"); nm = self.expect("ID"); self.expect("OP", ":")
                    cell["rules"].append((nm, self.expr())); self.expect("OP", ";")
            elif sec == ("KW", "STATES"):
                self.expect("OP", "{")
                while not self.accept("OP", "}"):
                    self.expect("KW", "STATE"); nm = self.expect("ID"); ty = None
                    if self.accept("KW", "TYPE"): ty = self.expect("ID")
                    self.expect("OP", "{"); st = dict(name=nm, type=ty, assigns=[], trans=[])
                    while not self.accept("OP", "}"):
                        if self.accept("KW", "TRANSITION"):
                            self.expect("KW", "TO"); tgt = self.expect("ID"); self.expect("KW", "IF")
                            st["trans"].append((tgt, self.expr())); self.expect("OP", ";")
                        else:
                            v = self.expect("ID"); self.expect("OP", "="); st["assigns"].append((v, self.expr())); self.expect("OP", ";")
                    cell["states"].append(st)
            else:
                raise BioError(f"unknown section {sec[1]!r}")
        names = [s["name"] for s in cell["states"]]
        for s in cell["states"]:
            for tgt, _ in s["trans"]:
                if tgt not in names: raise BioError(f"transition to undefined state {tgt}")
        return cell


def parse(src):
    p = Parser(tokenize(src)); c = p.cell()
    if p.peek()[0] != "EOF": raise BioError("trailing tokens after CELL")
    return c


# ---------------------------------------------------------------- reference semantics (float64, Python)
def _ev(e, env):
    k = e[0]
    if k == "num": return e[1]
    if k == "id":
        if e[1] not in env: raise BioError(f"unbound {e[1]}")
        return env[e[1]]
    if k == "neg": return -_ev(e[1], env)
    if k == "not": return not _ev(e[1], env)
    if k == "call":
        if e[1] != "DISTANCE" or len(e[2]) != 2: raise BioError(f"unsupported function {e[1]}")
        a, b = _ev(e[2][0], env), _ev(e[2][1], env)
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
    op = e[1]; a = _ev(e[2], env)
    if op == "IMPLIES": return (not a) or bool(_ev(e[3], env))
    if op == "AND": return bool(a) and bool(_ev(e[3], env))
    if op == "OR": return bool(a) or bool(_ev(e[3], env))
    b = _ev(e[3], env)
    if op == ">": return a > b
    if op == "<": return a < b
    if op == ">=": return a >= b
    if op == "<=": return a <= b
    if op == "==": return a == b
    if op == "!=": return a != b
    if op == "+": return a + b
    if op == "-": return a - b
    if op == "*": return a * b
    if op == "/": return a / b
    raise BioError(f"unknown operator {op}")


def eval_expr(e, env):
    return _ev(e, env)


def step(cell, state, inputs, semantics="transition_first"):
    """one tick; returns (next_state, outputs dict)"""
    st = {s["name"]: s for s in cell["states"]}
    env = dict(inputs)
    cur = st[state]
    if semantics == "transition_first":
        nxt = state
        for tgt, g in cur["trans"]:
            if eval_expr(g, env): nxt = tgt; break
        outs = {v: eval_expr(x, env) for v, x in st[nxt]["assigns"]}
        return nxt, outs
    outs = {v: eval_expr(x, env) for v, x in cur["assigns"]}
    nxt = state
    for tgt, g in cur["trans"]:
        if eval_expr(g, env): nxt = tgt; break
    return nxt, outs


def check_rules(cell, inputs, outs):
    env = dict(inputs); env.update(outs)
    return {nm: bool(eval_expr(e, env)) for nm, e in cell["rules"]}


if __name__ == "__main__":
    import sys
    c = parse(open(sys.argv[1], encoding="utf-8").read())
    print(c["name"], "inputs", c["inputs"], "outputs", c["outputs"], "rules", [r[0] for r in c["rules"]], "states", [s["name"] for s in c["states"]])
