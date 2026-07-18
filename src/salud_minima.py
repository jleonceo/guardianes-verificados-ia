"""
salud_minima.py — a minimal health orchestrator with a *global verdict*.

Incident this models (in miniature): a real health checker printed "ENFERMO"
(unhealthy) and still exited 0, because the verdict was never wired to the
process exit code. Every scheduled run went green. A green status that cannot
turn red is not a status.

`veredicto_global` is a PURE function (checks -> verdict), so it can be unit
tested without spawning anything. `run` is the thin shell that MUST translate
an unhealthy verdict into a non-zero exit code.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass

SANO = "SANO"        # healthy
ENFERMO = "ENFERMO"  # unhealthy

EXIT_HEALTHY = 0
EXIT_UNHEALTHY = 2


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool


def veredicto_global(checks: list[Check]) -> str:
    """Pure: any failing check makes the whole system ENFERMO.

    An empty check list is ENFERMO too — "nothing was checked" must never be
    reported as healthy (the non-vacuity rule).
    """
    if not checks:
        return ENFERMO
    return SANO if all(c.passed for c in checks) else ENFERMO


def run(checks: list[Check], *, with_teeth: bool = True) -> int:
    """Print the verdict and return the exit code.

    `with_teeth=False` reproduces the toothless bug: it prints ENFERMO but
    returns 0 anyway. The bank pins that this must be exit 2.
    """
    verdict = veredicto_global(checks)
    sys.stdout.write(f"veredicto_global={verdict}\n")
    if verdict == ENFERMO:
        return EXIT_UNHEALTHY if with_teeth else EXIT_HEALTHY
    return EXIT_HEALTHY
