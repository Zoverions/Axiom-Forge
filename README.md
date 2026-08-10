# Axiom Forge

Axiom Forge is an experimental ethical-reflection workspace for recording personal axioms and testing them against structured dilemmas. The repository also preserves a later **ZWA Lite** generated-tool experiment, but ZWA Lite is not the repository's product identity or an AXIOM authority boundary.

## Status

This repository contains research prototypes, not production systems.

| Surface | Current purpose | Current boundary |
|---|---|---|
| `frontend/` + `backend/` | Axiom Forge ethical-reflection prototype | Local prototype only. User identity is a placeholder, dilemmas are mock/generated templates, and the Flask entry point is not production hardened. |
| `zwa_lite.py` | Historical generated-tool / self-expanding-agent experiment | **Quarantined and non-executing by default.** Model-generated Python may be proposed, but legacy in-process execution requires explicit unsafe opt-in and is not a sandbox. |

Externally effective agent/tool execution should converge on the separately governed AXIOM capability and policy boundary rather than being granted by this prototype.

## Axiom Forge prototype

The original product surface remains in `frontend/` and `backend/`.

### Run locally

```bash
python -m venv .venv
# activate .venv for your shell
pip install -r backend/requirements.txt
python -m backend.create_db
python -m backend.app
```

The prototype supports:

- adding and deleting personal axioms;
- a collaborative dilemma mode for exploring one axiom;
- a personal red-team mode that places two selected axioms in conflict; and
- explicit consent before entering the red-team UI.

### Non-claims

- There is no production authentication or authorization model. The backend currently uses a placeholder local user.
- The dilemma engine is a mock/template implementation, not a validated moral reasoner.
- The Flask development server/debug path is not a deployment boundary.
- Nothing in this repository is authorized to override AXIOM policy, capability, or execution controls.

## ZWA Lite research artifact

`zwa_lite.py` preserves the Zero-Weight Architecture experiment: a local language model proposes small Python tools and can store successful tools in `constellation.json`.

The historical implementation executed model-generated Python in-process after regex/import checks. Those checks are useful linting but **cannot provide a secure Python sandbox**. The current boundary therefore defaults to proposal-only behavior.

### Proposal-only mode — default

```bash
pip install -r requirements.txt
python zwa_lite.py
```

Generated code is shown for inspection but is not executed or persisted as a successful skill.

### Legacy unsafe execution — research only

The legacy execution path requires both:

```bash
export AXIOM_FORGE_UNSAFE_LOCAL_EXEC=I_UNDERSTAND_THIS_IS_NOT_A_SANDBOX
python zwa_lite.py --unsafe-local-exec
```

Do not use that mode with secrets, sensitive files, privileged credentials, valuable local data, or on a trusted network. Model-generated code is untrusted code. The opt-in mode is preserved only for controlled local research and backward study; it is not a security boundary and should not be used for production agents.

## Verification

Repository contract checks are intentionally offline and do not claim model, moral, deployment, or sandbox correctness:

```bash
python -m unittest discover -s tests -v
python -m compileall -q backend zwa_lite.py
```

The checks verify the documented identity/safety boundary and that default ZWA execution remains fail-closed.

## Licensing

No repository-level `LICENSE` file is currently present. Do not infer an MIT or other reuse grant from historical README text. A license should be added only after an explicit owner licensing decision.
