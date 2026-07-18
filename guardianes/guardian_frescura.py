"""
guardian_frescura.py — compare against an INDEPENDENT source, not yourself.

Incident (real, dated): a freshness metric compared the search index against a
manifest — but the manifest was written in the SAME build pass as the index, so
the two always agreed. Green by construction, even with ~288 stale documents on
disk. A guardrail that checks a value against a copy of itself cannot fail.

The fix: compare against the DISK (an independent source of truth).
"""
from __future__ import annotations

EXIT_OK = 0
EXIT_VIOLATION = 2


def fresh_by_manifest(indexed: int, manifest: int) -> int:
    """BUGGY: manifest comes from the same build pass -> it always agrees."""
    return EXIT_OK if indexed == manifest else EXIT_VIOLATION


def fresh_by_disk(indexed: int, disk: int) -> int:
    """FIXED: disk is independent -> it catches the drift the manifest hides."""
    return EXIT_OK if indexed == disk else EXIT_VIOLATION
