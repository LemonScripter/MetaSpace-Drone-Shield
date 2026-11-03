"""
build_gates: generate the Rust gate from each example specification and build it for RISC-V RV32IMC (ESP32-C3 class core, no FPU).
Needs: rustup target add riscv32imc-unknown-none-elf. Run from this directory:  python build_gates.py
Output: ../build/gate_v1.elf, ../build/gate_v2.elf
"""
import os, shutil, subprocess, sys
from bio_subset import parse
from gen_gate import generate

here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
crate = os.path.join(root, "gate_rv32"); out = os.path.join(root, "build"); os.makedirs(out, exist_ok=True)
os.makedirs(os.path.join(crate, "src"), exist_ok=True)
for v in ("v1", "v2"):
    cell = parse(open(os.path.join(root, "examples", f"drone_shield_{v}.bio"), encoding="utf-8").read())
    open(os.path.join(crate, "src", "main.rs"), "w", encoding="utf-8").write(generate(cell))
    r = subprocess.run(["cargo", "build", "--release"], cwd=crate, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout, r.stderr); sys.exit(1)
    shutil.copy(os.path.join(crate, "target", "riscv32imc-unknown-none-elf", "release", "gate"), os.path.join(out, f"gate_{v}.elf"))
    print("built", f"gate_{v}.elf", "from", cell["name"])
