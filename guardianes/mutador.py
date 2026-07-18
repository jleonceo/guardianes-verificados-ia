"""
mutador.py — mutation testing for the guardrails (practice what we preach).

Mutation testing's core claim (Lipton 1971; DeMillo; pitest): a suite that
survives a deliberately broken program proves nothing. This repo *preaches*
that — so it *does* it. We generate MUTANTS of the guardrails and demand the
bank KILLS each one (turns red). A surviving mutant is a hole in the bank,
reported loudly. The mutation score = killed / total.

Two operator families:
  · behavioural — inject a broken wire into the bank (blind guardrail, toothless
    verdict, wrong-door guard, self-comparing freshness, ...). Fast, black-box.
  · source-level (AST) — actually rewrite `guardian_hook.py` (zero a constant,
    negate the detector) and re-exec it. The real mutation-testing move.
"""
from __future__ import annotations

import ast
import os
from dataclasses import dataclass

from . import banco
from . import guardian_hook as gh


@dataclass(frozen=True)
class MutantResult:
    name: str
    kind: str          # "behavioural" | "source"
    killed: bool
    detail: str = ""


# --------------------------------------------------------------------------- #
# behavioural mutants — reuse the bank's injection points
# --------------------------------------------------------------------------- #
def _behavioural() -> list[MutantResult]:
    out = []
    for name, killed in banco.prove_red():
        out.append(MutantResult(name, "behavioural", killed))
    return out


# --------------------------------------------------------------------------- #
# source-level mutants — rewrite guardian_hook.py via AST and re-exec it
# --------------------------------------------------------------------------- #
def _fuente_guardian() -> str:
    ruta = os.path.join(os.path.dirname(__file__), "guardian_hook.py")
    with open(ruta, encoding="utf-8") as fh:
        return fh.read()


class _MutateExitConstant(ast.NodeTransformer):
    """Mutate the value of one EXIT_* contract-constant assignment (0<->2).

    We mutate the guardrail's DECISION logic (the exit-code contract), not the
    CLI/IO plumbing — mutating `sys.argv[1:]` produces an equivalent mutant
    (prepending the program name does not flip secret detection) and equivalent
    mutants are, by definition, unkillable. Standard practice: mutate the code
    under test.
    """
    def __init__(self, target_name: str):
        self.target = target_name
        self.hit = False

    def visit_Assign(self, node):
        if (len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == self.target
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, int)):
            self.hit = True
            nuevo = 2 if node.value.value == 0 else 0
            node.value = ast.copy_location(ast.Constant(nuevo), node.value)
        return node


def _nombres_exit(src: str) -> list[str]:
    return [n.targets[0].id for n in ast.walk(ast.parse(src))
            if isinstance(n, ast.Assign) and len(n.targets) == 1
            and isinstance(n.targets[0], ast.Name) and n.targets[0].id.startswith("EXIT_")
            and isinstance(n.value, ast.Constant) and isinstance(n.value.value, int)]


def _mutar_negando_detector(src: str) -> str:
    """Negate the detector: `any(p.search...)` -> `not any(p.search...)`."""
    return src.replace("return any(p.search", "return not any(p.search", 1)


def _exec_modulo(src: str) -> dict:
    ns: dict = {}
    exec(compile(src, "<mutant>", "exec"), ns)  # noqa: S102 — mutant of our own file
    return ns


def _contrato_roto(evaluate) -> bool:
    """A healthy guardrail: violation -> 2, clean -> 0. Killed if that breaks."""
    try:
        viol = evaluate("password=hunter2") == 2
        clean = evaluate("a normal line") == 0
        return not (viol and clean)
    except Exception:
        return True  # a mutant that crashes is also caught


def _source() -> list[MutantResult]:
    src = _fuente_guardian()
    out: list[MutantResult] = []

    # one mutant per exit-code contract constant (constant mutation operator)
    for nombre in _nombres_exit(src):
        tree = _MutateExitConstant(nombre)
        mutated = ast.fix_missing_locations(tree.visit(ast.parse(src)))
        ns = _exec_modulo(ast.unparse(mutated))
        out.append(MutantResult(f"source:{nombre}-flipped", "source",
                                _contrato_roto(ns["evaluate"])))

    # negate the detector (conditional/boolean operator)
    ns = _exec_modulo(_mutar_negando_detector(src))
    out.append(MutantResult("source:negate-detector", "source",
                            _contrato_roto(ns["evaluate"])))
    return out


def ejecutar() -> list[MutantResult]:
    return _behavioural() + _source()


def mutation_score(resultados=None):
    resultados = resultados or ejecutar()
    killed = sum(1 for r in resultados if r.killed)
    return killed, len(resultados)
