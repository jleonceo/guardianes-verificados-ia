"""
demo_rojo_verde.py — five real incidents, each reproduced as red-before-green.

Run it:  python demo_rojo_verde.py

Each demo prints the RED state (the bug in place, the guardrail asleep) BEFORE
the GREEN state (the fix, the guardrail biting). A guardrail that has never
blocked anything has never been shown to protect anything — so here every
guardrail is shown failing first, on purpose.

No third-party deps, no network, no secrets. Pure standard library.
"""
from __future__ import annotations

import sys

from guardianes import guardian_hook as gh
from guardianes import salud_minima as sm
from guardianes import verificador_guardianes as vg
from guardianes import guardian_recurso as gr
from guardianes import guardian_frescura as gf


def _banner(n: int, title: str) -> None:
    print("\n" + "=" * 70)
    print(f"INCIDENT {n} - {title}")
    print("=" * 70)


def incident_1_swallowed_exit_code() -> None:
    _banner(1, "the guardrail that never braked")
    violation, clean = "password = hunter2", "just a normal line of text"

    def buggy_wrapper(text: str) -> int:
        gh.evaluate(text)          # result discarded — the classic shell-wrapper bug
        return 0

    red = vg.verify_contract("secret-scan (buggy wrapper)", buggy_wrapper,
                             clean=clean, violation=violation)
    print(f"  RED   -> contract_ok={red.ok}: {red.detail}")
    green = vg.verify_contract("secret-scan (bare)", gh.evaluate,
                               clean=clean, violation=violation)
    print(f"  GREEN -> contract_ok={green.ok}: {green.detail}")
    assert red.ok is False and green.ok is True


def incident_2_toothless_verdict() -> None:
    _banner(2, "the toothless verdict")
    checks = [sm.Check("cuadre", True), sm.Check("banco", False)]
    red = sm.run(checks, with_teeth=False)
    print(f"  RED   -> exit_code={red} (printed ENFERMO but exits 0)")
    green = sm.run(checks, with_teeth=True)
    print(f"  GREEN -> exit_code={green} (ENFERMO now translates to exit 2)")
    assert red == 0 and green == 2


def incident_3_lying_bank() -> None:
    _banner(3, "the bank that lied")
    hole = "passwd=hunter2"
    bank_v1 = ["password=x", "AKIA0000000000000000"]           # cases lifted FROM the rules
    v1_pass = all(gh.evaluate(c) == gh.EXIT_VIOLATION for c in bank_v1)
    v1_hole = gh.evaluate(hole) == gh.EXIT_VIOLATION
    print(f"  RED   -> bank_v1 all-green={v1_pass}, hole caught={v1_hole} (green bank, open hole)")
    bank_v2 = bank_v1 + [hole, "pwd = hunter2"]                 # independent cases
    v2_pass = all(gh.evaluate(c, gh.SECRET_PATTERNS_V2) == gh.EXIT_VIOLATION for c in bank_v2)
    v2_hole = gh.evaluate(hole, gh.SECRET_PATTERNS_V2) == gh.EXIT_VIOLATION
    print(f"  GREEN -> bank_v2 all-green={v2_pass}, hole caught={v2_hole}")
    assert v1_pass and not v1_hole and v2_pass and v2_hole


def incident_4_wrong_door() -> None:
    _banner(4, "the guardrail on the wrong door (we counted 5 doors, there were 6)")
    alias = "b.txt"    # an alias to the protected resource the name-matcher never listed
    red = gr.guard_by_name(alias)
    print(f"  RED   -> guard_by_name('{alias}')={red} (alias to the resource slips through)")
    green = gr.guard_by_resource(alias)
    print(f"  GREEN -> guard_by_resource('{alias}')={green} (canonical resource is guarded)")
    assert red == gr.EXIT_OK and green == gr.EXIT_VIOLATION


def incident_5_green_but_blind() -> None:
    _banner(5, "the green-but-blind verdict (checking a value against itself)")
    indexed, manifest, disk = 4476, 4476, 4766     # manifest built in the same pass -> agrees
    red = gf.fresh_by_manifest(indexed, manifest)
    print(f"  RED   -> fresh_by_manifest({indexed},{manifest})={red} (green while disk has {disk})")
    green = gf.fresh_by_disk(indexed, disk)
    print(f"  GREEN -> fresh_by_disk({indexed},{disk})={green} (independent source catches the drift)")
    assert red == gf.EXIT_OK and green == gf.EXIT_VIOLATION


def main() -> int:
    incident_1_swallowed_exit_code()
    incident_2_toothless_verdict()
    incident_3_lying_bank()
    incident_4_wrong_door()
    incident_5_green_but_blind()
    print("\n" + "-" * 70)
    print("Five incidents reproduced: each guardrail failed BEFORE it passed.")
    print("-" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
