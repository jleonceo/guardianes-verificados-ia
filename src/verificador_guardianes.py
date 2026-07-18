"""
verificador_guardianes.py — the meta-level: who tests the guardrails?

A guardrail is only trustworthy if, when handed a KNOWN violation, it actually
returns the blocking exit code — through the very wrapper the harness uses to
call it. This module runs each guardrail against a fixed pair of inputs and
demands the contract:

    known-clean     input -> exit 0
    known-violation input -> exit 2

Incident this models: a shell wrapper (a double `powershell.exe ... ; ...`
construct) swallowed the child's exit code and returned 0, so a guardrail that
correctly detected a violation was reported as "passed". The guardrail was
fine; the *plumbing around it* was blind. Only a check that runs the guardrail
END TO END, wrapper included, catches that.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

# A "runner" is however the harness actually invokes a guardrail: it takes the
# input text and returns the exit code the harness observes (wrapper included).
Runner = Callable[[str], int]

EXIT_OK = 0
EXIT_VIOLATION = 2


@dataclass(frozen=True)
class ContractResult:
    name: str
    ok: bool
    detail: str


def verify_contract(name: str, runner: Runner, *, clean: str, violation: str) -> ContractResult:
    """Demand exit 0 on clean input and exit 2 on the known violation."""
    code_clean = runner(clean)
    code_violation = runner(violation)

    if code_clean != EXIT_OK:
        return ContractResult(name, False, f"clean input returned {code_clean}, expected {EXIT_OK}")
    if code_violation != EXIT_VIOLATION:
        return ContractResult(
            name, False,
            f"KNOWN VIOLATION returned {code_violation}, expected {EXIT_VIOLATION} "
            "(guardrail did not block — check the wrapper)",
        )
    return ContractResult(name, True, "contract satisfied end to end")
