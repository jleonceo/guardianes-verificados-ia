"""
demo_rojo_verde.py — three real incidents, each reproduced as red-before-green.

Run it:  python demo_rojo_verde.py

Each demo prints the RED state (the bug in place, the guardrail asleep) BEFORE
the GREEN state (the fix, the guardrail biting). A guardrail that has never
blocked anything has never been shown to protect anything — so here every
guardrail is shown failing first, on purpose.

No third-party deps, no network, no secrets. Pure standard library.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import guardian_hook as gh          # noqa: E402
import salud_minima as sm           # noqa: E402
import verificador_guardianes as vg  # noqa: E402


def _banner(n: int, title: str) -> None:
    print("\n" + "=" * 68)
    print(f"INCIDENT {n} - {title}")
    print("=" * 68)


# --------------------------------------------------------------------------- #
# Incident 1 — the guardrail that never braked (exit code swallowed by a wrapper)
# --------------------------------------------------------------------------- #
def incident_1_swallowed_exit_code() -> None:
    _banner(1, "the guardrail that never braked")
    violation = "password = hunter2"
    clean = "just a normal line of text"

    # The guardrail itself is correct: violation -> 2, clean -> 0.
    def bare_runner(text: str) -> int:
        return gh.evaluate(text)

    # BUG: a wrapper that swallows the child exit code and always returns 0.
    def buggy_wrapper(text: str) -> int:
        gh.evaluate(text)  # result discarded — the classic shell-wrapper bug
        return 0

    red = vg.verify_contract("secret-scan (buggy wrapper)", buggy_wrapper,
                             clean=clean, violation=violation)
    print(f"  RED   -> contract_ok={red.ok}: {red.detail}")

    green = vg.verify_contract("secret-scan (bare)", bare_runner,
                               clean=clean, violation=violation)
    print(f"  GREEN -> contract_ok={green.ok}: {green.detail}")

    assert red.ok is False and green.ok is True


# --------------------------------------------------------------------------- #
# Incident 2 — the toothless verdict (prints ENFERMO, exits 0)
# --------------------------------------------------------------------------- #
def incident_2_toothless_verdict() -> None:
    _banner(2, "the toothless verdict")
    checks = [sm.Check("cuadre", True), sm.Check("banco", False)]  # one failing

    red = sm.run(checks, with_teeth=False)
    print(f"  RED   -> exit_code={red} (printed ENFERMO but exits 0)")

    green = sm.run(checks, with_teeth=True)
    print(f"  GREEN -> exit_code={green} (ENFERMO now translates to exit 2)")

    assert red == 0 and green == 2


# --------------------------------------------------------------------------- #
# Incident 3 — the bank that lied (circular cases hide the guardrail's hole)
# --------------------------------------------------------------------------- #
def incident_3_lying_bank() -> None:
    _banner(3, "the bank that lied")
    # The guardrail (v1) has a hole: it misses `passwd=`.
    hole_input = "passwd=hunter2"

    # Bank v1 — cases lifted FROM the guardrail's own patterns (circular).
    bank_v1 = ["password=x", "AKIA0000000000000000"]
    v1_pass = all(gh.evaluate(c) == gh.EXIT_VIOLATION for c in bank_v1)
    v1_catches_hole = gh.evaluate(hole_input) == gh.EXIT_VIOLATION
    print(f"  RED   -> bank_v1 all-green={v1_pass}, but hole caught={v1_catches_hole} "
          "(green bank, open hole)")

    # Bank v2 — independent cases, including the hole. Run against fixed v2.
    bank_v2 = bank_v1 + [hole_input, "pwd = hunter2"]
    v2_pass = all(gh.evaluate(c, gh.SECRET_PATTERNS_V2) == gh.EXIT_VIOLATION for c in bank_v2)
    v2_catches_hole = gh.evaluate(hole_input, gh.SECRET_PATTERNS_V2) == gh.EXIT_VIOLATION
    print(f"  GREEN -> bank_v2 all-green={v2_pass}, hole caught={v2_catches_hole}")

    assert v1_pass and not v1_catches_hole      # the lie: green while holed
    assert v2_pass and v2_catches_hole          # the fix: independent case bites


def main() -> int:
    incident_1_swallowed_exit_code()
    incident_2_toothless_verdict()
    incident_3_lying_bank()
    print("\n" + "-" * 68)
    print("All three incidents reproduced: each guardrail failed BEFORE it passed.")
    print("-" * 68)
    return 0


if __name__ == "__main__":
    sys.exit(main())
