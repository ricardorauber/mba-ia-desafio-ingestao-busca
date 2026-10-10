# 0001 - User-facing text stays in Brazilian Portuguese; everything else is in English

- Date: 2026-10-10
- Spec: 0001-project-setup-and-config
- Status: accepted

## Context
The build process requires every produced file to be in American English, but specs 0001, 0003, 0004, 0005 and 0006 require CLI messages and the README in Brazilian Portuguese, matching the challenge statement and its sample session.

## Options considered
- A: User-facing text (CLI messages, error messages, README) in Brazilian Portuguese; code, identifiers, comments, tests and commits in English — follows the specs and the challenge.
- B: Everything in English — requires updating the specs and diverges from the challenge's sample output.

## Decision
"Textos ao usuário em PT-BR" (User-facing text in Brazilian Portuguese) — option A.

## Consequences
Strings printed to the terminal and the README are written in Brazilian Portuguese. Source code, identifiers, comments, tests, ADRs and commit messages remain in American English.
