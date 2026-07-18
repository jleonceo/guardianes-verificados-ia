"""
vigilancia_diaria.py — the unattended daily watch (log + marker + notice).

A guardrail suite only helps if something runs it while nobody is looking and
makes noise when it turns red. This is the minimal loop: run the bank, drop a
marker file with the verdict and a timestamp, and exit non-zero (and print a
notice) when unhealthy — so a scheduler and the next session both find out.

No network, no secrets. Marker path defaults next to this file.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tests"))

import banco_guardianes as banco  # noqa: E402

EXIT_HEALTHY = 0
EXIT_UNHEALTHY = 2
DEFAULT_MARKER = os.path.join(os.path.dirname(__file__), "..", "ULTIMO_ESTADO.json")


def vigilar(marker_path: str = DEFAULT_MARKER) -> int:
    cases = banco.run_bank()
    failed = [c.name for c in cases if not c.passed]
    verdict = "ENFERMO" if failed else "SANO"

    marker = {
        "verdict": verdict,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total": len(cases),
        "failed": failed,
    }
    with open(marker_path, "w", encoding="utf-8") as fh:
        json.dump(marker, fh, ensure_ascii=False, indent=2)

    if verdict == "ENFERMO":
        sys.stderr.write(f"AVISO: guardianes ENFERMO -> {failed}\n")
        return EXIT_UNHEALTHY
    sys.stdout.write(f"guardianes SANO ({len(cases)}/{len(cases)})\n")
    return EXIT_HEALTHY


if __name__ == "__main__":
    sys.exit(vigilar())
