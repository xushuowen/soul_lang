# SOUL_LANG

**A formal computational model for spontaneity, continuous memory, and irreducible randomness.**

> *Does thinking precede soul, or does soul precede thinking?*
> — *The Empire of Corpses* (2015)

SOUL_LANG is a programming language specification and Python runtime prototype designed to probe the **computational boundary of soul** — defined operationally through three simultaneous conditions: spontaneity (S1), shadow self-organization (S2), and ε irreducibility (S3).

---

## Paper

The full academic paper is available in this repository:

- [`soul_lang_paper_v1.md`](soul_lang_paper_v1.md) — Markdown source
- [`soul_lang_paper_v1.html`](soul_lang_paper_v1.html) — Rendered HTML (open in browser)

**Title:** SOUL_LANG: Toward a Formal Computational Model for Spontaneity, Continuous Memory, and Irreducible Randomness
**Author:** Shuo-Wen Hsu (許碩文), Independent Researcher
**Date:** March 2026

### Phase 1 Results (n = 20 measurements)

| Outcome | Mean ± SD | Min | Max |
|---------|-----------|-----|-----|
| Φ (integrated information) | 0.508 ± 0.662 | 0.000 | 1.913 |
| ρ_ε (ε unpredictability rate) | 0.505 ± 0.072 | 0.320 | 0.640 |
| H_shadow (self-organization entropy) | 1.460 ± 0.702 | 0.000 | 2.641 |

All four failure conditions were never simultaneously met. The system **passed** Phase 1 verification.

---

## Repository Structure

```
soul_lang/
├── runtime/                  # Phase 1 Python runtime
│   ├── epsilon.py            # Quantum ε source (NIST Randomness Beacon)
│   ├── shadow_bit.py         # ShadowBit: visible + shadow + ε
│   ├── shadow_engine.py      # ODE engine (SciPy RK45)
│   ├── state.py              # State: dual-layer semantic unit
│   ├── phi.py                # Φ computation (IIT, mutual information)
│   ├── experiment.py         # Verification experiment framework (SQLite)
│   └── repl.py               # Interactive REPL
├── figures/
│   ├── fig1_shadowbit.png    # ShadowBit structure diagram
│   ├── fig2_dual_time.png    # Dual-layer time structure
│   ├── fig3_system_flow.png  # System architecture and verification flow
│   └── generate_figures.py   # Figure generation script (matplotlib)
├── soul_lang_paper_v1.md     # Academic paper (Markdown)
├── soul_lang_paper_v1.html   # Academic paper (HTML, self-contained)
├── soul_lang_whitepaper.md   # Technical white paper (Traditional Chinese)
├── soul_lang_whitepaper.html # Technical white paper (HTML)
├── references.bib            # BibTeX references
└── style.css                 # Paper stylesheet
```

---

## Quick Start

**Requirements:** Python 3.10+, `numpy`, `scipy`

```bash
pip install numpy scipy
```

```python
from runtime import State, VerificationExperiment

# Create a SoulCore state
state = State("SoulCore", use_ode=True)
state.define_shadow("resonance", 0.5)
state.define_shadow("depth", 0.4)
state.define_shadow("memory", 0.3)
state.define_visible("mood", "calm")
state.define_visible("active", False)

# Run a verification experiment
exp = VerificationExperiment(state, session_id="my_experiment")
exp.run(n_steps=20, measure_interval=5)
print(exp.report())
```

---

## Core Concepts

### ShadowBit
The basic computational unit. Each ShadowBit has three components:
- **visible** (`b_visible ∈ {0, 1}`) — discrete, fully observable
- **shadow** (`f_shadow ∈ [0.0, 1.0]`) — continuous, self-organizing, partially observable
- **ε** — quantum random injection (NIST Randomness Beacon, fallback: `os.urandom`)

### Shadow Evolution ODE
$$\frac{dS_i}{dt} = -\alpha(S_i - 0.5) + \beta \cdot \varepsilon_i(t) + \gamma \sum_{j \neq i} C_{ij}(S_j - S_i)$$

Parameters: α = 0.1, β = 0.3, γ = 0.05. Solved via SciPy `solve_ivp` (RK45).

### Failure Conditions (all four must hold simultaneously to declare failure)
| | Condition |
|-|-----------|
| F1 | Φ < 0.01 (system fully partitionable) |
| F2 | H_shadow variance < 0.01 over 5 steps (shadow halted) |
| F3 | ρ_ε < 0.05 (ε fully predictable) |
| F4 | Memory continuity cannot be re-established |

---

## Roadmap

- **Phase 1 (complete):** ShadowBit, State, ε source, ODE engine, Φ computation, verification experiment framework
- **Phase 2 (planned):** 1,000-step trajectories, n = 200 measurements, multiple SoulCore configurations, confirmed quantum ε
- **Phase 3 (planned):** Cross-system comparison, Φ threshold calibration, language compiler

---

## License

© 2026 Shuo-Wen Hsu (許碩文). All rights reserved.
For academic use and review. Contact via GitHub Issues.
