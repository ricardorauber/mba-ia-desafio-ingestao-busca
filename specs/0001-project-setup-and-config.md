# 0001 - Project setup and configuration

## Goal
Give the project up-to-date dependencies, a complete environment template, and one validated configuration module that every script reuses.

## Scope
- In: `requirements.txt` refresh, `.env.example`, `src/config.py`, pytest setup, `tests/` folder.
- Out: provider clients (0002), ingestion (0003), search (0004), chat loop (0005), README (0006).

## Requirements
- R1: The system SHALL pin dependency versions in `requirements.txt` that install on Python 3.12, 3.13 and 3.14, including `langchain`, `langchain-community`, `langchain-text-splitters`, `langchain-openai`, `langchain-google-genai`, `langchain-postgres`, `pypdf`, `psycopg[binary]`, `python-dotenv` and `pytest`.
- R2: The system SHALL provide `.env.example` with these variables and defaults: `LLM_PROVIDER=openrouter` (allowed: `openai`, `gemini`, `openrouter`), `OPENROUTER_API_KEY=`, `OPENROUTER_EMBEDDING_MODEL=openai/text-embedding-3-small`, `OPENROUTER_LLM_MODEL=openai/gpt-6-luna`, `OPENAI_API_KEY=`, `OPENAI_EMBEDDING_MODEL=text-embedding-3-small`, `OPENAI_LLM_MODEL=gpt-6-luna`, `GOOGLE_API_KEY=`, `GOOGLE_EMBEDDING_MODEL=models/gemini-embedding-001`, `GOOGLE_LLM_MODEL=gemini-3.1-flash-lite`, `DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag`, `PG_VECTOR_COLLECTION_NAME=documents`, `PDF_PATH=document.pdf`. Model names SHALL be confirmed against the provider's official documentation at build time.
- R3: The system SHALL expose `load_settings()` in `src/config.py` that reads the environment (after `load_dotenv()`) and returns an immutable settings object with the fields above.
- R4: WHEN `LLM_PROVIDER` is not `openai`, `gemini` or `openrouter`, `load_settings()` SHALL raise a `ConfigError` whose message, in Brazilian Portuguese, names the variable and the allowed values.
- R5: WHEN the API key of the selected provider (`OPENAI_API_KEY` for `openai`, `GOOGLE_API_KEY` for `gemini`, `OPENROUTER_API_KEY` for `openrouter`) is missing or blank, `load_settings()` SHALL raise a `ConfigError` whose message, in Brazilian Portuguese, names the missing variable.
- R6: WHEN `DATABASE_URL` or `PG_VECTOR_COLLECTION_NAME` is missing or blank, `load_settings()` SHALL raise a `ConfigError` naming the missing variable.
- R7: The system SHALL never print or log API key values.

## Acceptance criteria
- [x] AC1: `pip install -r requirements.txt` succeeds in a fresh Python 3.14 venv. (R1)
- [ ] AC2: `.env.example` contains exactly the variables and defaults listed in R2, with empty key values. (R2)
- [x] AC3: With a valid environment, `load_settings()` returns an object whose fields match the environment and cannot be reassigned. (R3)
- [ ] AC4: `LLM_PROVIDER=anthropic` raises `ConfigError` mentioning `LLM_PROVIDER`, `openai`, `gemini` and `openrouter`. (R4)
- [x] AC5: `LLM_PROVIDER=gemini` with blank `GOOGLE_API_KEY` raises `ConfigError` mentioning `GOOGLE_API_KEY`; `OPENAI_API_KEY` is not required in that case. (R5)
- [x] AC6: Blank `DATABASE_URL` raises `ConfigError` mentioning `DATABASE_URL`. (R6)
- [x] AC7: No `ConfigError` message and no `repr()` of the settings object contains an API key value. (R7)
- [x] AC8: `pytest` runs from the repository root and discovers `tests/`. (R1)
- [ ] AC9: `LLM_PROVIDER=openrouter` with blank `OPENROUTER_API_KEY` raises `ConfigError` mentioning `OPENROUTER_API_KEY`; neither `OPENAI_API_KEY` nor `GOOGLE_API_KEY` is required in that case. (R5)

## Unit tests
- T1: valid OpenAI environment returns settings with the expected field values (AC3).
- T2: settings object is frozen — assigning a field raises (AC3).
- T3: invalid `LLM_PROVIDER` raises `ConfigError` with variable name and the three allowed values (AC4).
- T4: `openai` provider without `OPENAI_API_KEY` raises naming `OPENAI_API_KEY` (R5).
- T5: `gemini` provider without `GOOGLE_API_KEY` raises naming `GOOGLE_API_KEY`, and does not require `OPENAI_API_KEY` (AC5).
- T6: blank `DATABASE_URL` and blank `PG_VECTOR_COLLECTION_NAME` each raise naming the variable (AC6).
- T7: `repr(settings)` does not contain the API key value (AC7).
- T8: `openrouter` provider without `OPENROUTER_API_KEY` raises naming `OPENROUTER_API_KEY`, and with it set loads without `OPENAI_API_KEY` or `GOOGLE_API_KEY` (AC9).
