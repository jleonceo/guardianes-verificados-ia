"""
banco_guardianes.py — a reusable bank that is proven in RED.

A bank that always passes proves nothing (mutation-testing lineage). So this
bank ships with `prove_red()`: it injects each bug back into the guardrails and
asserts the bank actually turns red. A guardrail suite you cannot make fail on
demand has no demonstrated teeth.
"""
from __future__ import annotations

import os
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
             runner=_bare_runner) -> list[Case]:
    """Green when everything is wired correctly. Parameters let the caller
    inject each known bug to prove the bank turns red."""
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

    # health verdict has teeth
    failing = [sm.Check("cuadre", True), sm.Check("banco", False)]
    check("salud_enfermo_exits_2",
          sm.run(failing, with_teeth=salud_teeth) == sm.EXIT_UNHEALTHY)
    # non-vacuity: empty checks must not read as healthy
    check("salud_empty_is_enfermo",
          sm.veredicto_global([]) == sm.ENFERMO)

    # verifier catches a swallowed exit code end to end
    res = vg.verify_contract("secret-scan", runner,
                             clean="a normal line", violation="password=hunter2")
    check("verificador_contract_end_to_end", res.ok, res.detail)

    return cases


def prove_red() -> list[tuple[str, bool]]:
    """Inject each bug and assert the bank catches it (goes red)."""
    proofs = []

    # bug 1: swallowed exit code -> verificador case must fail
    red = run_bank(runner=_buggy_wrapper)
    proofs.append(("inject swallowed-exit-code",
                   any(not c.passed and c.name == "verificador_contract_end_to_end" for c in red)))

    # bug 2: toothless salud -> salud case must fail
    red = run_bank(salud_teeth=False)
    proofs.append(("inject toothless-verdict",
                   any(not c.passed and c.name == "salud_enfermo_exits_2" for c in red)))

    # bug 3: holed guardrail (v1) -> the passwd hole case must fail
    red = run_bank(guardian_patterns=gh.SECRET_PATTERNS_V1)
    proofs.append(("inject holed-guardrail",
                   any(not c.passed and c.name == "guardian_catches_passwd_hole" for c in red)))

    return proofs
