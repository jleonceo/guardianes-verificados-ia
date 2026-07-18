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


def test_mutation_score_is_perfect():
    killed, total = mutador.mutation_score()
    assert killed == total and total >= 8, f"surviving mutants: score {killed}/{total}"
