# Verification record

Axiom Forge uses `.github/workflows/repository-contract.yml` as an offline repository-boundary check.

The workflow intentionally verifies only:

- Python syntax/compilation for `backend/`, `zwa_lite.py`, and repository tests;
- ZWA model dependencies are not loaded merely by importing the module;
- generated-code execution is denied by default;
- the legacy unsafe execution path requires the exact environment acknowledgment in addition to the explicit execution path;
- stored skills remain proposal-only under the default `run()` behavior; and
- repository documentation does not claim a secure Python sandbox or an unsupported MIT license grant.

It does **not** verify production authentication/authorization, dilemma quality or moral validity, model safety, secure generated-code sandboxing, dependency reproducibility, hardware behavior, external services, or deployment readiness.

## Bootstrap history

Security-boundary PR #4 introduced the workflow and merged as `4cd90ad9e0bd6913c03dfc03299689c223c9833d` after exact five-file review. Because a new `pull_request` workflow cannot provide ordinary base-branch PR evidence until it exists on the base branch, this verification-record PR is the first normal pull-request execution of that contract over the merged boundary.

A successful run on this PR establishes repository-contract evidence only; it does not expand the non-claims above.
