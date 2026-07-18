"""
guardian_hook.py — a guardrail as a hook, with an exit-code contract.

The contract (the whole point of this repo):
    exit 0  -> input is clean, let it through
    exit 2  -> a violation was found, BLOCK it

A guardrail that can only *print* "violation" but always exits 0 protects
nothing: the surrounding harness reads the exit code, not the prose. This
module is deliberately tiny so the *contract* — not the detector — is the star.

The example detector scans text for hardcoded-secret patterns. It ships with a
known HOLE (see `SECRET_PATTERNS_V1`) so the bank can be proven in red.
"""
from __future__ import annotations

import re
import sys

EXIT_OK = 0
EXIT_VIOLATION = 2

# v1 has a hole on purpose: it catches `password=` but misses `passwd=`/`pwd=`.
# A bank written *from this list* would be circular and pass while the hole
# stays open. See tests/banco_guardianes.py for the independent bank that
# catches it.
SECRET_PATTERNS_V1 = [
    re.compile(r"password\s*=\s*\S+", re.IGNORECASE),
    re.compile(r"AKIA[0-9A-Z]{16}"),  # AWS-access-key shape
]

# v2 closes the hole.
SECRET_PATTERNS_V2 = SECRET_PATTERNS_V1 + [
    re.compile(r"\b(passwd|pwd)\s*=\s*\S+", re.IGNORECASE),
]


def scan(text: str, patterns=SECRET_PATTERNS_V1) -> bool:
    """Return True if a forbidden pattern is present."""
    return any(p.search(text) for p in patterns)


def evaluate(text: str, patterns=SECRET_PATTERNS_V1) -> int:
    """Pure core: text -> exit code. No I/O, so it is trivially testable."""
    return EXIT_VIOLATION if scan(text, patterns) else EXIT_OK


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    text = " ".join(argv) if argv else sys.stdin.read()
    code = evaluate(text)
    if code == EXIT_VIOLATION:
        sys.stderr.write("BLOCK: possible hardcoded secret\n")
    return code


if __name__ == "__main__":
    sys.exit(main())
