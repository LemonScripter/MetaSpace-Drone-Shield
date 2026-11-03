"""
measure_gate: runs a GENERATED gate (RISC-V RV32IMC, no FPU, soft-float) in the Unicorn emulator and
  (A) compares every result with an independent numpy float32 model of the same specification (exact match required),
  (B) compares the v2 gate with the real-valued specification semantics (bio_subset.step, float64) outside the 1e-6 rounding band,
  (C) shows the NaN / infinity behaviour (fail-open for v1, fail-safe for v2),
  (D) counts executed instructions per tick (by class) and converts them to a time ESTIMATE at 160 MHz with stated cycle assumptions.
Usage: python measure_gate.py build/gate_v2.elf v2 [n_random]      (the second argument selects the numpy model: v1 | v2)
"""
import struct, sys, math
import numpy as np
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_RISCV, UC_MODE_RISCV32, UC_HOOK_CODE
from unicorn.riscv_const import UC_RISCV_REG_A0, UC_RISCV_REG_A1, UC_RISCV_REG_A2, UC_RISCV_REG_A3, UC_RISCV_REG_A4, UC_RISCV_REG_A5, UC_RISCV_REG_SP, UC_RISCV_REG_RA
from bio_subset import parse, step as spec_step

ELF, VER = sys.argv[1], sys.argv[2]
NRAND = int(sys.argv[3]) if len(sys.argv) > 3 else 60000
FLASH, FLASH_SZ, RAM, RAM_SZ = 0x42000000, 4 * 1024 * 1024, 0x3FC80000, 384 * 1024
HALT = FLASH + FLASH_SZ - 0x1000
f2i = lambda x: struct.unpack("<I", struct.pack("<f", x))[0]

elf = ELFFile(open(ELF, "rb")); sym = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols() if s.name}
img = bytearray(FLASH_SZ); uc = Uc(UC_ARCH_RISCV, UC_MODE_RISCV32); uc.mem_map(FLASH, FLASH_SZ); uc.mem_map(RAM, RAM_SZ)
for seg in elf.iter_segments():
    if seg["p_type"] == "PT_LOAD" and seg["p_filesz"]:
        d = seg.data(); uc.mem_write(seg["p_vaddr"], d)
        if FLASH <= seg["p_vaddr"] < FLASH + FLASH_SZ: img[seg["p_vaddr"] - FLASH:seg["p_vaddr"] - FLASH + len(d)] = d
code_size = {s.name: s["sh_size"] for s in elf.iter_sections()}.get(".text", 0)
uc.mem_write(HALT, b"\x01\x00" * 4)


def classify(addr):
    off = addr - FLASH; h = img[off] | (img[off + 1] << 8)
    if (h & 3) != 3:
        quad, f3 = h & 3, h >> 13
        if quad == 0: return ("load" if f3 == 2 else "store" if f3 == 6 else "alu"), 2
        if quad == 1: return ("jump" if f3 in (1, 5) else "branch" if f3 in (6, 7) else "alu"), 2
        if f3 == 2: return "load", 2
        if f3 == 6: return "store", 2
        if f3 == 4:
            rs2 = (h >> 2) & 31; rs1 = (h >> 7) & 31; b12 = (h >> 12) & 1
            if (b12 == 0 and rs2 == 0) or (b12 == 1 and rs2 == 0 and rs1 != 0): return "jump", 2
        return "alu", 2
    w = h | (img[off + 2] << 16) | (img[off + 3] << 24); op = w & 0x7F
    if op == 0x03: return "load", 4
    if op == 0x23: return "store", 4
    if op == 0x63: return "branch", 4
    if op in (0x6F, 0x67): return "jump", 4
    if op == 0x33 and (w >> 25) == 1: return ("mul" if ((w >> 12) & 7) < 4 else "div"), 4
    return "alu", 4


cls_cache = {}; cnt = {k: 0 for k in ("alu", "load", "store", "branch", "branch_taken", "jump", "mul", "div")}; st = {"prev": None, "on": False}


def hook(uc_, addr, size, _):
    if not st["on"]: return
    c = cls_cache.get(addr)
    if c is None: c = classify(addr)[0]; cls_cache[addr] = c
    p = st["prev"]
    if p is not None and p[0] == "branch" and addr != p[1]: cnt["branch_taken"] += 1
    cnt[c] += 1; st["prev"] = (c, addr + size)


uc.hook_add(UC_HOOK_CODE, hook, begin=FLASH, end=FLASH + FLASH_SZ - 0x2000)
REGS = (UC_RISCV_REG_A0, UC_RISCV_REG_A1, UC_RISCV_REG_A2, UC_RISCV_REG_A3, UC_RISCV_REG_A4, UC_RISCV_REG_A5)


def gate(state, gx, gy, ix, iy, rf, count=False):
    for k in cnt: cnt[k] = 0
    st["prev"] = None; st["on"] = count
    vals = [state & 0xFFFFFFFF] + [f2i(v) for v in (gx, gy, ix, iy, rf)]
    for r, v in zip(REGS, vals): uc.reg_write(r, v)
    uc.reg_write(UC_RISCV_REG_SP, RAM + RAM_SZ); uc.reg_write(UC_RISCV_REG_RA, HALT)
    uc.emu_start(sym["gate_step"], HALT)
    r = uc.reg_read(UC_RISCV_REG_A0)
    return r & 0xFF, (r >> 8) & 0xFF, (dict(cnt) if count else None)


# ---------------------------------------------------------------- independent numpy f32 model (written by hand, not generated)
f = np.float32


def model(ver, state, gx, gy, ix, iy, rf):
    with np.errstate(all="ignore"):
        gx, gy, ix, iy, rf = f(gx), f(gy), f(ix), f(iy), f(rf)
        dx = gx - ix; dy = gy - iy; d2 = dx * dx + dy * dy
        nxt = state
        if ver == "v2":
            if state == 0 and not (d2 <= f(400.0) and rf <= f(-125.0)): nxt = 1
            elif state == 1 and not (d2 <= f(2500.0)): nxt = 2
        else:
            if state == 0 and (d2 > f(400.0)): nxt = 1
            elif state == 1 and (d2 > f(2500.0)): nxt = 2
        if state > 2: nxt = 2
        return nxt, (0 if nxt == 0 else 1)


rng = np.random.default_rng(20261103)
vecs = []
for _ in range(NRAND):   # (1) random, mostly near the interesting range
    vecs.append((int(rng.integers(3)), *rng.uniform(-60, 60, 4), rng.uniform(-140, -110)))
for L in (20.0, 50.0):   # (2) boundary: distance around L, several angles, rf around -125
    for ang in np.linspace(0, 2 * math.pi, 40, endpoint=False):
        for rel in (-1e-3, -1e-5, -1e-6, -1e-7, 0.0, 1e-7, 1e-6, 1e-5, 1e-3):
            d = L * (1 + rel); gx_, gy_ = 7.5 + d * math.cos(ang), -3.25 + d * math.sin(ang)
            for s in range(3):
                for rf in (-130.0, -125.0, float(np.nextafter(np.float32(-125.0), np.float32(0))), float(np.nextafter(np.float32(-125.0), np.float32(-200))), -124.99):
                    vecs.append((s, gx_, gy_, 7.5, -3.25, rf))
special = [0.0, -0.0, 1.0, -1.0, 1e30, -1e30, 3.4e38, float("inf"), float("-inf"), float("nan"), 1e-40, -125.0, 20.0, 50.0]
for _ in range(30000):   # (3) special values incl. NaN / inf / subnormal
    vecs.append((int(rng.integers(3)), *[special[int(rng.integers(len(special)))] for _ in range(5)]))
for v in (3, 7, 255): vecs.append((v, 0.0, 0.0, 0.0, 0.0, -130.0))   # invalid state values

first = None
print(f"gate {ELF} | numpy model {VER} | .text {code_size} bytes | {len(vecs)} test vectors")
bad = 0
for v in vecs:
    ns, al, _ = gate(*v)
    ms, ma = model(VER, v[0], *v[1:])
    if (ns, al) != (ms, ma):
        bad += 1
        if first is None: first = (v, (ns, al), (ms, ma))
print(f"(A) emulated RISC-V gate vs independent f32 model: {bad} mismatches in {len(vecs)}" + (f"  first: {first}" if bad else "  -> exact match"))

# ---------------------------------------------------------------- (B) real-valued specification
spec = parse(open(f"../examples/drone_shield_{VER}.bio", encoding="utf-8").read()); names = [s["name"] for s in spec["states"]]
checked = diff = 0; ex = None
for v in vecs:
    s, gx, gy, ix, iy, rf = v
    if s > 2 or not all(math.isfinite(float(f(x))) for x in (gx, gy, ix, iy, rf)): continue
    gx, gy, ix, iy, rf = [float(f(x)) for x in (gx, gy, ix, iy, rf)]
    d2 = (gx - ix) ** 2 + (gy - iy) ** 2
    if any(abs(d2 - L * L) <= 2e-6 * L * L for L in (20.0, 50.0)): continue          # inside the 1e-6 rounding band: either result is allowed
    if abs(rf + 125.0) == 0.0 and False: continue
    nxt, outs = spec_step(spec, names[s], dict(gps_coord=(gx, gy), ins_coord=(ix, iy), rf_power=rf))
    ns, al, _ = gate(s, *[float(x) for x in (gx, gy, ix, iy, rf)])
    checked += 1
    if (names[ns], al) != (nxt, int(outs["alarm"])):
        diff += 1
        if ex is None: ex = (names[s], gx, gy, ix, iy, rf, "gate", names[ns], al, "spec", nxt, outs["alarm"])
print(f"(B) gate vs real-valued spec semantics (float64), outside the 2e-6 band around 20 m and 50 m: {diff} differences in {checked} finite vectors" + (f"  first: {ex}" if diff else "  -> agree"))

# ---------------------------------------------------------------- (C) NaN / inf behaviour from the Normal state with an otherwise harmless input
print("(C) from state Normal, harmless inputs except one invalid value:")
for name, vec in [("gps_x = NaN", (0, float("nan"), 0, 0, 0, -130.0)), ("gps_x = +inf", (0, float("inf"), 0, 0, 0, -130.0)), ("ins_y = NaN", (0, 0, 0, 0, float("nan"), -130.0)),
                  ("rf = NaN", (0, 0, 0, 0, 0, float("nan"))), ("rf = +inf", (0, 0, 0, 0, 0, float("inf")))]:
    ns, al, _ = gate(*vec); print(f"      {name:14s} -> next state {ns}, alarm {al}   ({'ALARM' if al else 'NO ALARM (fail-open)'})")

# ---------------------------------------------------------------- (D) instruction counts
sample = [v for v in vecs if v[0] <= 2][:: max(1, len(vecs) // 4000)]
tot = []; comp = {k: [] for k in cnt}
for v in sample:
    _, _, c = gate(*v, count=True); tot.append(sum(c[k] for k in ("alu", "load", "store", "branch", "jump", "mul", "div"))); [comp[k].append(c[k]) for k in cnt]
tot = np.array(tot)
OPT = dict(alu=1, load=1, store=1, branch=1, branch_taken=0, jump=1, mul=1, div=20); PES = dict(alu=1, load=2, store=1, branch=1, branch_taken=2, jump=2, mul=4, div=35)
worst_i = int(np.argmax(tot)); wc = {k: comp[k][worst_i] for k in cnt}; med_i = int(np.argsort(tot)[len(tot) // 2]); mc = {k: comp[k][med_i] for k in cnt}
cyc = lambda c, m: sum(c[k] * m[k] for k in m)
print(f"(D) instructions per tick over {len(tot)} vectors: min {tot.min()}, median {int(np.median(tot))}, max {tot.max()}  (MEASURED, emulator)")
for nm, c in (("median", mc), ("worst", wc)):
    lo, hi = cyc(c, OPT), cyc(c, PES)
    print(f"    {nm:6s} tick: {lo} - {hi} cycles = {lo / 160e6 * 1e6:.1f} - {hi / 160e6 * 1e6:.1f} microseconds at 160 MHz  (ESTIMATED: cycles/instruction assumed, see TECHNICAL notes)")
