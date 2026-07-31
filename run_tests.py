"""
run_tests.py — tiny stdlib test runner (dogfoods the exit-code contract).

    python run_tests.py

Runs the green bank, `prove_red()` (each known bug injected must be caught), and
the mutation runner (every mutant must be killed). Exits 0 only if all three are
fully green.
"""
from __future__ import annotations

import sys

from guardianes import banco, mutador


def main() -> int:
    ok = True
    ran = 0

    print("== green bank ==")
    for c in banco.run_bank():
        ran += 1
        if not c.passed:
            ok = False
        print(f"  [{'PASS' if c.passed else 'FAIL'}] {c.name}"
              f"{(' - ' + c.detail) if c.detail and not c.passed else ''}")

    print("== red proofs - fault injection (each injected bug must be caught) ==")
    for name, caught in banco.prove_red():
        ran += 1
        if not caught:
            ok = False
        print(f"  [{'PASS' if caught else 'FAIL'}] {name}: bank turned red = {caught}")

    # Source-level mutation (AST) is the evidence BEYOND the fault-injection
    # proofs above: it rewrites guardian_hook.py and re-execs it. Reported on
    # its own so the number is not inflated by re-counting the red proofs.
    print("== source-level mutation (AST rewrite of guardian_hook.py) ==")
    src_mutants = mutador.source()
    for r in src_mutants:
        ran += 1
        if not r.killed:
            ok = False
        print(f"  [{'KILLED' if r.killed else 'SURVIVED'}] {r.name}")
    killed = sum(1 for r in src_mutants if r.killed)
    print(f"  source mutation score: {killed}/{len(src_mutants)}")

    print("-" * 60)
    # The count goes on the verdict line on purpose. A runner that only says GREEN
    # tells you nothing about how much it ran: "all green" over zero checks reads
    # exactly like "all green" over forty, and that is the shape of a bank that
    # quietly stops running and nobody notices.
    print(f"{ran}/{ran} checks PASS - ALL GREEN" if ok
          else f"FAILURES PRESENT ({ran} checks ran)")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
