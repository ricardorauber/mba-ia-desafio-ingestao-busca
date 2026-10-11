# 0004 - Semantic search and answer generation

## Goal
Answer a question using only the 10 most similar chunks from the vector store and the challenge's fixed prompt.

## Scope
- In: `src/search.py` (`PROMPT_TEMPLATE`, `build_context`, `search_prompt`).
- Out: terminal loop and input handling (0005).

## Requirements
- R1: The system SHALL keep `PROMPT_TEMPLATE` exactly as provided in the template repository, with placeholders `{contexto}` and `{pergunta}`.
- R2: For each question, the system SHALL call `similarity_search_with_score(question, k=10)` on the vector store (which embeds the question).
- R3: `build_context` SHALL concatenate the `page_content` of the returned documents, in the returned order, separated by a blank line.
- R4: The system SHALL fill the prompt with the context and the question, invoke the LLM from `get_llm(settings)`, and return the response text stripped of surrounding whitespace.
- R5: `search_prompt()` SHALL return a callable `ask(question: str) -> str` that reuses one settings object, one embeddings client, one vector store and one LLM across questions.
- R6: WHEN initialization fails (`ConfigError` or unreachable database), `search_prompt()` SHALL print a short Brazilian Portuguese message and return `None`.
- R7: WHEN the collection has no documents, `ask` SHALL return `Não tenho informações necessárias para responder sua pergunta.` without calling the LLM.

## Acceptance criteria
- [x] AC1: `PROMPT_TEMPLATE` is byte-identical to the template repository version. (R1)
- [x] AC2: `ask` calls `similarity_search_with_score` with `k=10`. (R2)
- [x] AC3: The prompt sent to the LLM contains every retrieved chunk in order, separated by blank lines, and the user question. (R3, R4)
- [x] AC4: With `document.pdf` ingested, asking for the revenue of a company listed in the PDF returns the value from the PDF. (R4)
- [x] AC5: With `document.pdf` ingested, `Qual é a capital da França?` returns `Não tenho informações necessárias para responder sua pergunta.` (R4)
- [x] AC6: Two calls to `ask` construct the LLM and vector store once. (R5)
- [x] AC7: Missing API key → `search_prompt()` prints a message and returns `None`. (R6)
- [x] AC8: Empty search result returns the fixed fallback and the LLM is not invoked. (R7)

## Unit tests
- T1: `build_context` joins three documents in order with blank lines (AC3).
- T2: `ask` with patched vector store and fake LLM: `k=10` used, prompt contains chunks and question, returns stripped LLM text (AC2, AC3).
- T3: factories called once across two `ask` calls (AC6).
- T4: `ConfigError` during init → `None` returned, message printed (AC7).
- T5: empty search result → fallback text, fake LLM never invoked (AC8).
- T6: `PROMPT_TEMPLATE` contains `{contexto}`, `{pergunta}` and the fallback sentence verbatim (AC1).
