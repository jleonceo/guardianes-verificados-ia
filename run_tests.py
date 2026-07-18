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

    print("== green bank ==")
    for c in banco.run_bank():
        if not c.passed:
            ok = False
        print(f"  [{'PASS' if c.passed else 'FAIL'}] {c.name}"
              f"{(' - ' + c.detail) if c.detail and not c.passed else ''}")

    print("== red proofs - fault injection (each injected bug must be caught) ==")
    for name, caught in banco.prove_red():
        if not caught:
            ok = False
        print(f"  [{'PASS' if caught else 'FAIL'}] {name}: bank turned red = {caught}")

    # Source-level mutation (AST) is the evidence BEYOND the fault-injection
    # proofs above: it rewrites guardian_hook.py and re-execs it. Reported on
    # its own so the number is not inflated by re-counting the red proofs.
    print("== source-level mutation (AST rewrite of guardian_hook.py) ==")
    src_mutants = mutador.source()
    for r in src_mutants:
        if not r.killed:
            ok = False
        print(f"  [{'KILLED' if r.killed else 'SURVIVED'}] {r.name}")
    killed = sum(1 for r in src_mutants if r.killed)
    print(f"  source mutation score: {killed}/{len(src_mutants)}")

    print("-" * 60)
    print("ALL GREEN" if ok else "FAILURES PRESENT")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
