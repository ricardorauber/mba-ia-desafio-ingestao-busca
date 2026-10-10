# 0003 - Default OpenAI chat model is gpt-6-luna

- Date: 2026-10-10
- Spec: 0001-project-setup-and-config
- Status: accepted

## Context
The spec sets `OPENAI_LLM_MODEL=gpt-5-nano` and asks for the model names to be confirmed against the official documentation at build time. OpenAI's deprecations page lists the `gpt-5-nano-2025-08-07` snapshot for shutdown on 2026-12-11. The other defaults (`text-embedding-3-small`, `gemini-embedding-001`, `gemini-3.1-flash-lite`) are current.

## Options considered
- A: `gpt-6-luna` — OpenAI's current most efficient model ($0.10 input / $0.50 output per 1M tokens).
- B: `gpt-5.6-luna` — the replacement the deprecations page names for `gpt-5-nano`.
- C: Keep `gpt-5-nano` — matches the spec but stops working after 2026-12-11.

## Decision
"gpt-6-luna" — option A.

## Consequences
`.env.example` and `src/config.py` default `OPENAI_LLM_MODEL` to `gpt-6-luna` instead of the value written in the spec. The spec text should be updated with `update-spec` if the spec is reused.
