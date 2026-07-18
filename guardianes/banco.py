"""
banco.py — a reusable bank that is proven in RED.

A bank that always passes proves nothing (mutation-testing lineage). Every wire
of every guardrail is an injection point, so `prove_red()` (and mutador.py) can
break one wire at a time and assert the bank turns red. A guardrail suite you
cannot make fail on demand has no demonstrated teeth.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from . import guardian_hook as gh
from . import salud_minima as sm
from . import verificador_guardianes as vg
from . import guardian_recurso as gr
from . import guardian_frescura as gf


@dataclass(frozen=True)
class Case:
    name: str
    passed: bool
    detail: str = ""


def _bare_runner(text: str) -> int:
    return gh.evaluate(text, gh.SECRET_PATTERNS_V2)


def _buggy_wrapper(text: str) -> int:
    gh.evaluate(text, gh.SECRET_PATTERNS_V2)  # exit code swallowed
    return 0


def run_bank(*, salud_teeth: bool = True, guardian_patterns=gh.SECRET_PATTERNS_V2,
             runner=_bare_runner, veredicto_fn=sm.veredicto_global,
             recurso_fn=gr.guard_by_resource, frescura_fn=gf.fresh_by_disk) -> list[Case]:
    """Green when everything is wired correctly. Every parameter is an injection
    point so a mutant can break one wire and turn the matching case red."""
    cases: list[Case] = []

    def check(name, cond, detail=""):
        cases.append(Case(name, bool(cond), detail))

    # 1-3 · secret-scan guardrail contract
    check("guardian_blocks_violation",
          gh.evaluate("password=hunter2", guardian_patterns) == gh.EXIT_VIOLATION)
    check("guardian_allows_clean",
          gh.evaluate("a normal line", guardian_patterns) == gh.EXIT_OK)
    check("guardian_catches_passwd_hole",   # independent case a circular bank misses
          gh.evaluate("passwd=hunter2", guardian_patterns) == gh.EXIT_VIOLATION)

    # 4-5 · health verdict has teeth + non-vacuity (verbose off: library call)
    failing = [sm.Check("cuadre", True), sm.Check("banco", False)]
    check("salud_enfermo_exits_2",
          sm.run(failing, with_teeth=salud_teeth, verbose=False) == sm.EXIT_UNHEALTHY)
    check("salud_empty_is_enfermo", veredicto_fn([]) == sm.ENFERMO)

    # 6 · verifier catches a swallowed exit code end to end
    res = vg.verify_contract("secret-scan", runner,
                             clean="a normal line", violation="password=hunter2")
    check("verificador_contract_end_to_end", res.ok, res.detail)

    # 7 · guard the RESOURCE, not the name (an alias must still be blocked)
    check("recurso_guards_the_room",
          recurso_fn("b.txt") == gr.EXIT_VIOLATION and recurso_fn("clean.txt") == gr.EXIT_OK)

    # 8 · freshness against an INDEPENDENT source (drift must be caught)
    check("frescura_catches_drift",
          frescura_fn(4476, 4766) == gf.EXIT_VIOLATION and frescura_fn(4766, 4766) == gf.EXIT_OK)

    # 9 · main() actually translates the verdict into the process exit code
    #     (the function that MATERIALISES the contract — must be covered too)
    check("main_translates_verdict",
          gh.main(["password=hunter2"]) == gh.EXIT_VIOLATION and gh.main(["a normal line"]) == gh.EXIT_OK)

    return cases


# --- mutant wires, used only to prove the bank has teeth --------------------- #
_MATCH_EVERYTHING = [re.compile(r".")]     # paranoid: flags even clean text
_MATCH_NOTHING: list = []                  # blind: flags nothing


def _veredicto_ciego(checks):
    """Broken verdict: reports SANO on an empty check list (vacuity bug)."""
    return sm.SANO if not checks else sm.veredicto_global(checks)


def _frescura_ciega(indexed, disk):
    """Broken freshness: compares the value against itself (manifest bug)."""
    return gf.fresh_by_manifest(indexed, indexed)


def prove_red() -> list[tuple[str, bool]]:
    """Inject one bug per case and assert the bank catches it (that case goes
    red). Covers ALL eight cases — a suite you cannot make fail on demand has
    no demonstrated teeth."""
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
        ("inject guard-by-name (wrong door)",
         caught({"recurso_fn": gr.guard_by_name}, "recurso_guards_the_room")),
        ("inject blind-freshness (self-compare)",
         caught({"frescura_fn": _frescura_ciega}, "frescura_catches_drift")),
    ]
