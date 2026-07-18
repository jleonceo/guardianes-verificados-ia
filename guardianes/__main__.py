"""
Command-line entry point:  python -m guardianes <command>

  verificar "<text>"   run the secret-scan guardrail on text (exit 0 clean / 2 violation)
  banco                run the bank of guardrail contracts (exit 0 green / 2 red)
  mutar                run mutation testing on the guardrails (exit 0 iff score 100%)
  vigilar              the unattended daily watch (writes a marker, exit 0/2)

Every command honours the exit-code contract, so a scheduler or CI reads the
result from the exit code — not from the text.
"""
from __future__ import annotations

import argparse
import sys

from . import banco, guardian_hook, mutador, vigilancia_diaria


def _cmd_verificar(args) -> int:
    return guardian_hook.evaluate(args.text, guardian_hook.SECRET_PATTERNS_V2)


def _cmd_banco(args) -> int:
    cases = banco.run_bank()
    for c in cases:
        print(f"  [{'PASS' if c.passed else 'FAIL'}] {c.name}")
    red = [c for c in cases if not c.passed]
    print(f"{'ALL GREEN' if not red else 'FAILURES: ' + str(len(red))}")
    return 0 if not red else 2


def _cmd_mutar(args) -> int:
    resultados = mutador.ejecutar()
    for r in resultados:
        mark = "KILLED" if r.killed else "SURVIVED"
        print(f"  [{mark:8}] ({r.kind}) {r.name}")
    killed, total = mutador.mutation_score(resultados)
    survivors = [r.name for r in resultados if not r.killed]
    print(f"mutation score: {killed}/{total}")
    if survivors:
        print("SURVIVING MUTANTS (bank holes): " + ", ".join(survivors))
    return 0 if killed == total else 2


def _cmd_vigilar(args) -> int:
    return vigilancia_diaria.vigilar()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="guardianes", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verificar", help="run the secret-scan guardrail on text")
    v.add_argument("text")
    v.set_defaults(fn=_cmd_verificar)
    sub.add_parser("banco", help="run the bank of guardrail contracts").set_defaults(fn=_cmd_banco)
    sub.add_parser("mutar", help="run mutation testing on the guardrails").set_defaults(fn=_cmd_mutar)
    sub.add_parser("vigilar", help="the unattended daily watch").set_defaults(fn=_cmd_vigilar)
    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
