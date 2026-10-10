# 0006 - README and GitHub delivery

## Goal
Document how to run the project and publish it as a public fork on the user's personal GitHub account.

## Scope
- In: `README.md` rewrite (Brazilian Portuguese), fork of `devfullcycle/mba-ia-desafio-ingestao-busca` under the personal account `ricardorauber`, push of the work.
- Out: code changes.

## Requirements
- R1: The README SHALL describe, in Brazilian Portuguese: prerequisites (Python ≥ 3.12, Docker with Compose, an OpenRouter, OpenAI or Google API key), venv creation and activation, `pip install -r requirements.txt`, copying `.env.example` to `.env` and filling it, `docker compose up -d`, `python src/ingest.py`, `python src/chat.py`, and `pytest`.
- R2: The README SHALL document every variable of `.env.example`, how `LLM_PROVIDER` switches between OpenRouter, OpenAI and Gemini, and the default models.
- R3: The README SHALL explain that changing the embeddings model or provider requires re-running `python src/ingest.py` (which recreates the collection), and how to wipe the database volume with `docker compose down -v` if needed.
- R4: The README SHALL show a sample chat session with one in-context and one out-of-context question, and how to exit the chat.
- R5: The repository SHALL be a public fork of `devfullcycle/mba-ia-desafio-ingestao-busca` owned by the GitHub account `ricardorauber`, containing all source code, specs and tests.
- R6: `.env` SHALL never be committed.

## Acceptance criteria
- [ ] AC1: Following the README step by step on a clean machine runs ingestion and the chat. (R1)
- [ ] AC2: Every variable in `.env.example` appears in the README with its purpose. (R2)
- [x] AC3: The README has a section on switching embeddings models. (R3)
- [x] AC4: The README has a sample session and the exit commands. (R4)
- [ ] AC5: `https://github.com/ricardorauber/mba-ia-desafio-ingestao-busca` is public, is a fork of the template, and its default branch contains the final code. (R5)
- [x] AC6: `git ls-files` does not list `.env`. (R6)

## Unit tests
- T1: none — documentation and delivery only; verified by AC1–AC6.
