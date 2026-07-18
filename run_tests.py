"""
run_tests.py — tiny stdlib test runner (dogfoods the exit-code contract).

    python run_tests.py

Runs the green bank AND `prove_red()` (each known bug injected must be caught).
Exits 0 only if every green case passes and every injected bug is caught.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tests"))

import banco_guardianes as banco  # noqa: E402


def main() -> int:
    ok = True

    print("== green bank ==")
    for c in banco.run_bank():
        mark = "PASS" if c.passed else "FAIL"
        if not c.passed:
            ok = False
        print(f"  [{mark}] {c.name} {('- ' + c.detail) if c.detail and not c.passed else ''}")

    print("== red proofs (each injected bug must be caught) ==")
    for name, caught in banco.prove_red():
        mark = "PASS" if caught else "FAIL"
        if not caught:
            ok = False
        print(f"  [{mark}] {name}: bank turned red = {caught}")

    print("-" * 60)
    print("ALL GREEN" if ok else "FAILURES PRESENT")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
