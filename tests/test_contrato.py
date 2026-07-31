"""
test_contrato.py — pytest-compatible tests (also runnable via run_tests.py).

Uses only assert + plain functions, so `pytest` OR a manual run both work. The
contract, the bank's teeth, and the mutation score are all pinned here.
"""
from guardianes import banco, mutador
from guardianes import guardian_hook as gh
from guardianes import salud_minima as sm


def test_contract_blocks_violation_and_allows_clean():
    assert gh.evaluate("password=hunter2", gh.SECRET_PATTERNS_V2) == gh.EXIT_VIOLATION
    assert gh.evaluate("a normal line", gh.SECRET_PATTERNS_V2) == gh.EXIT_OK


def test_empty_checks_are_unhealthy():
    assert sm.veredicto_global([]) == sm.ENFERMO


def test_green_bank_is_all_green():
    assert all(c.passed for c in banco.run_bank())


def test_every_injected_bug_is_caught():
    for name, caught in banco.prove_red():
        assert caught, f"bank did not catch: {name}"


def test_source_mutants_all_killed():
    src = mutador.source()
    survivors = [r.name for r in src if not r.killed]
    assert not survivors and len(src) >= 4, f"surviving source mutants: {survivors}"


def test_main_is_covered_and_its_mutant_is_killed():
    # the function that materialises the exit-code contract must be tested
    assert any(r.name == "source:main-return-0" and r.killed for r in mutador.source())


def test_no_mutant_survives_overall():
    survivors = [r.name for r in mutador.ejecutar() if not r.killed]
    assert not survivors, f"surviving mutants: {survivors}"


def _run_standalone() -> int:
    """Run every test_* in this module without pytest, and report the count.

    The docstring at the top has always claimed `pytest` OR a manual run both
    work. Until now the manual run did nothing at all: no `__main__` block meant
    `python tests/test_contrato.py` imported the module, defined the functions
    and exited 0 without asserting anything. A file that exits green having run
    zero tests is worse than one that fails, because the zero is invisible.
    """
    tests = sorted((name, fn) for name, fn in globals().items()
                   if name.startswith("test_") and callable(fn))
    failed = []
    for name, fn in tests:
        try:
            fn()
            print(f"  [PASS] {name}")
        except AssertionError as e:
            failed.append(name)
            print(f"  [FAIL] {name}: {e}")
    print("-" * 60)
    if failed:
        print(f"FAILURES PRESENT ({len(failed)} of {len(tests)} checks)")
        return 1
    print(f"{len(tests)}/{len(tests)} checks PASS - ALL GREEN")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(_run_standalone())
