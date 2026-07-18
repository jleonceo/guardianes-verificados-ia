"""
banco_guardianes.py — a reusable bank that is proven in RED.

A bank that always passes proves nothing (mutation-testing lineage). So this
bank ships with `prove_red()`: it injects each bug back into the guardrails and
asserts the bank actually turns red. A guardrail suite you cannot make fail on
demand has no demonstrated teeth.
"""
from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import guardian_hook as gh          # noqa: E402
import salud_minima as sm           # noqa: E402
import verificador_guardianes as vg  # noqa: E402


@dataclass(frozen=True)
class Case:
    name: str
    passed: bool
    detail: str


def _bare_runner(text: str) -> int:
    return gh.evaluate(text, gh.SECRET_PATTERNS_V2)


def _buggy_wrapper(text: str) -> int:
    gh.evaluate(text, gh.SECRET_PATTERNS_V2)  # exit code swallowed
    return 0


def run_bank(*, salud_teeth: bool = True, guardian_patterns=gh.SECRET_PATTERNS_V2,
             runner=_bare_runner, veredicto_fn=sm.veredicto_global) -> list[Case]:
    """Green when everything is wired correctly. Every parameter is an
    injection point so `prove_red()` can mutate one wire at a time and assert
    the corresponding case turns red."""
    cases: list[Case] = []

    def check(name, cond, detail=""):
        cases.append(Case(name, bool(cond), detail))

    # guardrail contract
    check("guardian_blocks_violation",
          gh.evaluate("password=hunter2", guardian_patterns) == gh.EXIT_VIOLATION)
    check("guardian_allows_clean",
          gh.evaluate("a normal line", guardian_patterns) == gh.EXIT_OK)
    # independent case that a circular bank would have missed
    check("guardian_catches_passwd_hole",
          gh.evaluate("passwd=hunter2", guardian_patterns) == gh.EXIT_VIOLATION)

    # health verdict has teeth (verbose off: this is a library call)
    failing = [sm.Check("cuadre", True), sm.Check("banco", False)]
    check("salud_enfermo_exits_2",
          sm.run(failing, with_teeth=salud_teeth, verbose=False) == sm.EXIT_UNHEALTHY)
    # non-vacuity: empty checks must not read as healthy
    check("salud_empty_is_enfermo",
          veredicto_fn([]) == sm.ENFERMO)

    # verifier catches a swallowed exit code end to end
    res = vg.verify_contract("secret-scan", runner,
                             clean="a normal line", violation="password=hunter2")
    check("verificador_contract_end_to_end", res.ok, res.detail)

    return cases


# --- mutant guardrails / verdicts, used only to prove the bank has teeth --- #
_MATCH_EVERYTHING = [re.compile(r".")]          # paranoid: flags even clean text
_MATCH_NOTHING: list = []                       # blind: flags nothing


def _veredicto_ciego(checks):
    """Broken verdict: reports SANO on an empty check list (vacuity bug)."""
    return sm.SANO if not checks else sm.veredicto_global(checks)


def prove_red() -> list[tuple[str, bool]]:
    """Inject one bug per case and assert the bank catches it (that case goes
    red). Covers ALL six cases — a suite you cannot make fail on demand has no
    demonstrated teeth."""
    def caught(injection_kwargs, case_name):
        red = run_bank(**injection_kwargs)
        return any(not c.passed and c.name == case_name for c in red)

    return [
        ("inject swallowed-exit-code",
         caught({"runner": _buggy_wrapper}, "verificador_contract_end_to_end")),
        ("inject toothless-verdict",
         caught({"salud_teeth": False}, "salud_enfermo_exits_2")),
        ("inject holed-guardrail",
         caught({"guardian_patterns": gh.SECRET_PATTERNS_V1}, "guardian_catches_passwd_hole")),
        ("inject blind-guardrail",
         caught({"guardian_patterns": _MATCH_NOTHING}, "guardian_blocks_violation")),
        ("inject paranoid-guardrail",
         caught({"guardian_patterns": _MATCH_EVERYTHING}, "guardian_allows_clean")),
        ("inject vacuous-verdict",
         caught({"veredicto_fn": _veredicto_ciego}, "salud_empty_is_enfermo")),
    ]
