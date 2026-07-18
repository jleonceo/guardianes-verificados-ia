"""
guardian_recurso.py — guard the RESOURCE, not the name.

Incident (real, dated): a hook was wired to a `matcher` (a path/name) and was
believed to protect a resource. But the same resource was reachable by another
path the matcher didn't list — the guard protected the door, not the room.
"We counted 5 doors; there were 6." A guardrail keyed on a name is only as good
as the enumeration of names; miss one alias and it is silently bypassed.

The fix: resolve the input to the CANONICAL resource and guard that.
"""
from __future__ import annotations

EXIT_OK = 0
EXIT_VIOLATION = 2

# The protected resource is reachable by several aliases (paths, links, ...).
_ALIASES = {
    "a.txt": "secret",
    "./a.txt": "secret",
    "b.txt": "secret",        # a 6th door the name-matcher never listed
    "link_to_a": "secret",
}
_PROTECTED = "secret"


def guard_by_name(path: str, blocked_names=("a.txt",)) -> int:
    """BUGGY: blocks by name/matcher only. Any alias to the same resource slips."""
    return EXIT_VIOLATION if path in blocked_names else EXIT_OK


def canonical(path: str) -> str:
    """Resolve an input path to the resource it actually reaches."""
    return _ALIASES.get(path, path)


def guard_by_resource(path: str, protected: str = _PROTECTED) -> int:
    """FIXED: guard the canonical resource, so every alias is covered."""
    return EXIT_VIOLATION if canonical(path) == protected else EXIT_OK
