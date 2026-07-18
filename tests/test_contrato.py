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
