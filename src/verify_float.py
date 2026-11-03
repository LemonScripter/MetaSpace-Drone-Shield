"""
verify_float: Z3 proofs about the float32 (IEEE-754) step function that the generated gate implements (v2 spec).
The model below is the exact operation order of the generated Rust code (gen_gate.py):
    dx = gx - ix; dy = gy - iy; d2 = dx*dx + dy*dy                      (all f32, round-to-nearest-even)
    Normal : next = Suspect  if !(d2 <= 400.0  && rf <= -125.0) else Normal
    Suspect: next = Isolated if !(d2 <= 2500.0)                  else Suspect
    Isolated: stays;  alarm = (state after the transition) != Normal
Comparisons with NaN are false, hence the negated guard form fails safe.

Properties (unsat of the negated claim = proved; UNKNOWN = the solver gave up, NOT a proof):
  F1a invalid input (any NaN, infinite coordinate, rf = +inf)  -> the Normal guard fires (alarm = 1 after one tick)          [bit-level, all f32]
  F1b invalid coordinate (NaN / infinity)                      -> the Suspect guard fires (escalation to Isolated)          [bit-level, all f32]
  F4  rf > -125                                                -> the Normal guard fires                                    [bit-level, all f32]
  F2  exact squared distance above the limit by a relative margin EPS -> the guard fires
  F3  exact squared distance below the limit by EPS (and rf <= -125 for the Normal guard) -> the guard does not fire (no false alarm)
      F2/F3 are shown in two ways: (step 1) from the standard rounding model fl(z) = z(1+e)+d over the reals (conditional on that model),
      (step 2) bit-level on a bounded domain (every f32 with 2^-8 <= |x| <= 2^8, or zero), exact reference distance in a wide FP format.
EPS = 2^-20 (about 1e-6). The rounding error of d2 stays below 4 * 2^-24, so the guard decides correctly outside a relative band of 1e-6 around the limit;
inside the band the result may go either way (that is the honest meaning of "the compiled gate implements the real-valued rule").
Usage: python verify_float.py [timeout_seconds] [--bitlevel]
"""
import sys, time
import z3

F32 = z3.FPSort(8, 24)
RNE = z3.RNE()
fp = lambda v: z3.FPVal(v, F32)
EPS = z3.RealVal(1) / (2 ** 20)


def model():
    gx, gy, ix, iy, rf = [z3.FP(n, F32) for n in ("gx", "gy", "ix", "iy", "rf")]
    dx = z3.fpSub(RNE, gx, ix); dy = z3.fpSub(RNE, gy, iy)
    d2 = z3.fpAdd(RNE, z3.fpMul(RNE, dx, dx), z3.fpMul(RNE, dy, dy))
    g20 = z3.Not(z3.And(z3.fpLEQ(d2, fp(400.0)), z3.fpLEQ(rf, fp(-125.0))))
    g50 = z3.Not(z3.fpLEQ(d2, fp(2500.0)))
    return (gx, gy, ix, iy, rf), d2, g20, g50


def finite(x): return z3.And(z3.Not(z3.fpIsNaN(x)), z3.Not(z3.fpIsInf(x)))


def prove(name, claim, hyp, tmo):
    s = z3.Solver(); s.set("timeout", int(tmo * 1000)); s.add(hyp); s.add(z3.Not(claim))
    t0 = time.time(); r = s.check(); dt = time.time() - t0
    if r == z3.unsat: print(f"  {name:72s} PROVED   ({dt:.1f} s)", flush=True)
    elif r == z3.sat: print(f"  {name:72s} VIOLATED ({dt:.1f} s) counter-example: {s.model()}", flush=True)
    else: print(f"  {name:72s} UNKNOWN  ({dt:.1f} s, solver: {s.reason_unknown()})", flush=True)
    return r == z3.unsat


if __name__ == "__main__":
    nums = [x for x in sys.argv[1:] if not x.startswith('--')]
    tmo = float(nums[0]) if nums else 300
    bitlevel = '--bitlevel' in sys.argv     # the bounded-domain bit-level part is slow and may time out; it is opt-in
    (gx, gy, ix, iy, rf), d2, g20, g50 = model()
    invalid = z3.Or(z3.fpIsNaN(gx), z3.fpIsNaN(gy), z3.fpIsNaN(ix), z3.fpIsNaN(iy), z3.fpIsNaN(rf),
                    z3.fpIsInf(gx), z3.fpIsInf(gy), z3.fpIsInf(ix), z3.fpIsInf(iy), z3.And(z3.fpIsInf(rf), z3.fpIsPositive(rf)))
    bad_coord = z3.Or(z3.fpIsNaN(gx), z3.fpIsNaN(gy), z3.fpIsNaN(ix), z3.fpIsNaN(iy), z3.fpIsInf(gx), z3.fpIsInf(gy), z3.fpIsInf(ix), z3.fpIsInf(iy))
    ok = True
    print("float32 model of the generated gate (Z3 floating-point theory)")
    ok &= prove("F1a invalid input -> Normal guard fires", g20, invalid, tmo)
    ok &= prove("F1b invalid coordinate -> Suspect guard fires (escalation)", g50, bad_coord, tmo)
    ok &= prove("F4  rf > -125 (not NaN) -> Normal guard fires", g20, z3.And(z3.Not(z3.fpIsNaN(rf)), z3.fpGT(rf, fp(-125.0))), tmo)
    print("  (an invalid rf alone does not escalate Suspect, but Suspect already has alarm = 1, so alarm = 1 holds for every invalid input)")

    print("\n  -- F2/F3 step 1: algebra over the reals from the standard rounding model fl(z) = z(1+e) + d, |e| <= 2^-24, |d| <= 2^-100 (covers underflow)")
    U = z3.RealVal(1) / (2 ** 24); ETA = z3.RealVal(1) / (2 ** 100)
    X, Y = z3.Reals("X Y"); e1, e2, e3, e4, e5 = z3.Reals("e1 e2 e3 e4 e5"); k1, k2, k3, k4, k5 = z3.Reals("k1 k2 k3 k4 k5")
    bnd = z3.And(*[z3.And(e >= -U, e <= U) for e in (e1, e2, e3, e4, e5)], *[z3.And(d >= -ETA, d <= ETA) for d in (k1, k2, k3, k4, k5)])
    a = X * (1 + e1) + k1; b = Y * (1 + e2) + k2            # fl(dx), fl(dy)
    pp = a * a * (1 + e3) + k3; qq = b * b * (1 + e4) + k4    # fl(dx*dx), fl(dy*dy)
    ss = (pp + qq) * (1 + e5) + k5                            # fl(d2)
    Ex = X * X + Y * Y
    ok &= prove("F2 model: exact d2 > 2500(1+EPS) => fl(d2) > 2500   (d2 <= 1e9)", ss > z3.RealVal(2500), z3.And(bnd, Ex > z3.RealVal(2500) * (1 + EPS), Ex <= 10 ** 9), tmo)
    ok &= prove("F2 model: exact d2 > 400(1+EPS)  => fl(d2) > 400    (d2 <= 1e9)", ss > z3.RealVal(400), z3.And(bnd, Ex > z3.RealVal(400) * (1 + EPS), Ex <= 10 ** 9), tmo)
    ok &= prove("F3 model: exact d2 < 2500(1-EPS) => fl(d2) <= 2500", ss <= z3.RealVal(2500), z3.And(bnd, Ex < z3.RealVal(2500) * (1 - EPS)), tmo)
    ok &= prove("F3 model: exact d2 < 400(1-EPS)  => fl(d2) <= 400", ss <= z3.RealVal(400), z3.And(bnd, Ex < z3.RealVal(400) * (1 - EPS)), tmo)
    print("     (conditional on the rounding model, Higham, Accuracy and Stability of Numerical Algorithms, Thm 2.2; huge values overflow to infinity and are covered by F1-type handling)")

    if not bitlevel:
        print("\n  -- F2/F3 step 2 (bit-level on a bounded domain) skipped; run with --bitlevel (may time out, see docs/validation/SMT_VERIFICATION_REPORT.md)")
    else:
        print("\n  -- F2/F3 step 2: bit-level on a bounded domain: every f32 with 2^-8 <= |x| <= 2^8 or x = 0; the reference distance is computed exactly in a wide FP format")
        W = z3.FPSort(11, 70)

        def bounded(x):
            return z3.Or(z3.fpIsZero(x), z3.And(z3.fpAbs(x) >= fp(2.0 ** -8), z3.fpAbs(x) <= fp(2.0 ** 8)))
        dom = z3.And(bounded(gx), bounded(gy), bounded(ix), bounded(iy))
        ext = lambda v: z3.fpFPToFP(RNE, v, W)
        wdx = z3.fpSub(RNE, ext(gx), ext(ix)); wdy = z3.fpSub(RNE, ext(gy), ext(iy))
        wE = z3.fpAdd(RNE, z3.fpMul(RNE, wdx, wdx), z3.fpMul(RNE, wdy, wdy))
        c = lambda v: z3.FPVal(v, W)
        ok &= prove("F2b bounded: exact d2 > 2500(1+EPS) -> g50 fires", g50, z3.And(dom, z3.fpGT(wE, c(2500.0 * (1 + 2.0 ** -20)))), tmo)
        ok &= prove("F3b bounded: exact d2 < 2500(1-EPS) -> g50 silent", z3.Not(g50), z3.And(dom, z3.fpLT(wE, c(2500.0 * (1 - 2.0 ** -20)))), tmo)
        ok &= prove("F2a bounded: exact d2 > 400(1+EPS)  -> g20 fires", g20, z3.And(dom, z3.fpGT(wE, c(400.0 * (1 + 2.0 ** -20)))), tmo)
        ok &= prove("F3a bounded: exact d2 < 400(1-EPS) and rf <= -125 -> g20 silent", z3.Not(g20), z3.And(dom, finite(rf), z3.fpLEQ(rf, fp(-125.0)), z3.fpLT(wE, c(400.0 * (1 - 2.0 ** -20)))), tmo)
    print("\nALL PROVED" if ok else "\nNOT ALL PROVED (UNKNOWN means the solver gave up; it is not a proof)")
