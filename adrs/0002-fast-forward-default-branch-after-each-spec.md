# 0002 - Fast-forward the default branch after each spec

- Date: 2026-10-10
- Spec: 0001-project-setup-and-config
- Status: accepted

## Context
The build process never commits to the default branch, but spec 0006 requires the default branch of the public fork to contain the final code.

## Options considered
- A: Open one pull request per spec and merge them in order at the end.
- B: Open pull requests and let the user merge them.
- C: Push the spec branches only.

## Decision
"Eu permito que pode ir fazendo commit na main" (I allow committing to main as we go).

## Consequences
Each spec is still built in its own worktree and branch. Once a spec is green, committed and pushed, `main` is fast-forwarded to that spec branch and pushed, and the next spec branches from the updated `main`.
