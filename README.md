# guardianes-verificados-ia
### Who tests the guardrails? / ¿Quién vigila a los guardianes?

> A guardrail that has never blocked anything has never been shown to protect
> anything. This is a tiny, dependency-free harness that puts **guardrails
> themselves** under test: an exit-code contract, banks proven in red, a
> non-vacuity check, and three real incidents you can reproduce.
>
> Un guardarraíl que nunca ha bloqueado nada no ha demostrado que proteja nada.
> Este es un harness mínimo, sin dependencias, que pone a examen **a los propios
> guardianes**: un contrato de códigos de salida, bancos probados en rojo, un
> control de no-vacuidad, y tres incidentes reales que puedes reproducir.

---

## EN

Most "guardrail" projects check the *output* of a model. This one checks the
*guardrails*. The idea is one level up (meta): a detector that can only *print*
"violation" but always exits 0 protects nothing, because the harness around it
reads the **exit code**, not the prose.

**Run the heart of the repo:**

```bash
python demo_rojo_verde.py
```

It reproduces three incidents, each shown failing (RED) *before* it passes
(GREEN):

1. **The guardrail that never braked** — a shell wrapper swallowed the child
   exit code, so a detector that correctly found a violation was reported as
   "passed". Only an end-to-end check (wrapper included) catches it.
2. **The toothless verdict** — a health check printed `ENFERMO` (unhealthy) and
   still exited 0, because the verdict was never wired to the process exit code.
3. **The bank that lied** — a test bank whose cases were lifted from the
   detector's own rules stays green while the detector's hole stays open; an
   independent bank bites.

### What's inside

| File | Role |
|---|---|
| `src/guardian_hook.py` | a guardrail as a hook, with the `exit 0 / exit 2` contract |
| `src/salud_minima.py` | a health orchestrator whose global verdict has teeth |
| `src/verificador_guardianes.py` | the meta-level: runs each guardrail against a known violation and demands the contract |
| `demo_rojo_verde.py` | the three incidents, red before green |

_Standard library only. No network, no secrets, no third-party dependencies._

### Prior art / genealogy

This stands on: deterministic hooks (control by code, not by an LLM), and
**mutation testing** — the 40-year-old idea that *a test that never fails proves
nothing*. The closest relatives validate with an LLM; here the validator is
plain code.

---

## ES

La mayoría de los proyectos de "guardarraíles" comprueban la *salida* de un
modelo. Este comprueba **los guardarraíles**. La idea está un nivel por encima:
un detector que solo *imprime* "violación" pero siempre sale con código 0 no
protege nada, porque el harness que lo rodea lee el **código de salida**, no el
texto.

**Ejecuta el corazón del repo:**

```bash
python demo_rojo_verde.py
```

Reproduce tres incidentes, cada uno mostrado fallando (ROJO) *antes* de pasar
(VERDE):

1. **El guardián que no frenaba** — un envoltorio de shell se tragaba el código
   de salida del proceso hijo, así que un detector que sí encontraba la
   violación se reportaba como "pasado". Solo una comprobación de punta a punta
   (envoltorio incluido) lo caza.
2. **El veredicto sin dientes** — una comprobación de salud imprimía `ENFERMO` y
   aun así salía con 0, porque el veredicto nunca se cableó al código de salida.
3. **El banco que mentía** — un banco de pruebas cuyos casos se copiaron de las
   propias reglas del detector se queda verde mientras el agujero del detector
   sigue abierto; un banco independiente lo caza.

_Solo biblioteca estándar. Sin red, sin secretos, sin dependencias de terceros._

---

<!-- TODO (pendiente antes de publicar / before publishing):
     - componentes 4 (banco reutilizable) y 5 (vigilancia diaria)
     - LICENSE (decisión de licencia)
     - checklist de seguridad completo (grep rutas/credenciales/nombres) -->
