# Security and authority boundaries

Axiom Forge is a research/prototype repository. It is **not** a production authentication service, moral authority, agent execution authority, or secure code sandbox.

## Axiom Forge web prototype

The `frontend/` + `backend/` application currently has prototype-only properties that block production use:

- `get_current_user()` uses a placeholder local user rather than a real identity/authentication flow;
- object ownership/authorization checks are incomplete;
- `backend/app.py` starts the Flask development server with debug mode enabled when run directly;
- the dilemma engine is a mock/template generator and must not be described as validated moral reasoning;
- dependencies are not yet locked to a production reproducibility contract; and
- no security review or production deployment evidence is recorded here.

Do not expose this prototype to an untrusted network or sensitive user data without a separate hardening and review effort.

## ZWA Lite generated-code experiment

`zwa_lite.py` is preserved as an experimental generated-tool artifact.

### Default boundary

Generated Python is **proposal-only by default**. It may be displayed for inspection but must not execute or be persisted as a successful skill through the default CLI path.

### Legacy unsafe path

Historical in-process execution is retained only for controlled local research. It requires both `--unsafe-local-exec` and the exact environment acknowledgment documented in the README.

The reduced builtins, import allowlist, and source linter on that path are defense-in-depth only. They are **not a secure Python sandbox**. Python object introspection, library behavior, parser gaps, implementation defects, and allowed network-capable modules can create effects not captured by source-text rules.

Never enable unsafe execution with:

- secrets or cloud credentials in the environment;
- sensitive or valuable local files;
- privileged OS/container permissions;
- production data;
- access to trusted internal networks; or
- any expectation that generated code is contained solely by this Python process.

Production tool execution should use an external, deny-by-default isolation/capability boundary. In the wider Axiom architecture, effective execution authority belongs at the governed AXIOM boundary rather than inside this prototype.

## Reporting

Do not post live credentials, private data, or exploit payloads containing sensitive material in a public issue. Use GitHub's private vulnerability reporting/security-advisory path when enabled, or contact the repository owner through a private channel.

## Licensing note

There is currently no repository-level `LICENSE` file. Security documentation does not grant reuse rights.
