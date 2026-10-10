# 0002 - Embeddings, LLM and vector store factory

## Goal
Build the embeddings model, the chat model and the PGVector store from the settings in one place, so ingestion and search share identical wiring.

## Scope
- In: `src/providers.py` with `get_embeddings(settings)`, `get_llm(settings)` and `get_vector_store(settings, embeddings)`.
- Out: settings loading (0001), ingestion flow (0003), retrieval and prompting (0004).

## Requirements
- R1: WHEN `settings.llm_provider` is `openai`, `get_embeddings` SHALL return `OpenAIEmbeddings` configured with `OPENAI_EMBEDDING_MODEL` and `OPENAI_API_KEY`.
- R2: WHEN `settings.llm_provider` is `gemini`, `get_embeddings` SHALL return `GoogleGenerativeAIEmbeddings` configured with `GOOGLE_EMBEDDING_MODEL` and `GOOGLE_API_KEY`.
- R3: WHEN `settings.llm_provider` is `openai`, `get_llm` SHALL return `ChatOpenAI` configured with `OPENAI_LLM_MODEL`; WHEN it is `gemini`, `get_llm` SHALL return `ChatGoogleGenerativeAI` configured with `GOOGLE_LLM_MODEL`.
- R4: `get_vector_store` SHALL return a `langchain_postgres.PGVector` bound to `DATABASE_URL`, `PG_VECTOR_COLLECTION_NAME` and the given embeddings, with `use_jsonb=True`.
- R5: `get_vector_store` SHALL accept a `pre_delete_collection` flag (default `False`) and pass it to `PGVector`.
- R6: WHEN `settings.llm_provider` is `openrouter`, `get_embeddings` SHALL return `OpenAIEmbeddings` configured with `OPENROUTER_EMBEDDING_MODEL`, `OPENROUTER_API_KEY` and the base URL `https://openrouter.ai/api/v1`, sending the chunk text as plain strings (no client-side tokenization).
- R7: WHEN `settings.llm_provider` is `openrouter`, `get_llm` SHALL return `ChatOpenAI` configured with `OPENROUTER_LLM_MODEL`, `OPENROUTER_API_KEY` and the base URL `https://openrouter.ai/api/v1`.

## Acceptance criteria
- [x] AC1: OpenAI settings yield an `OpenAIEmbeddings` whose model equals `OPENAI_EMBEDDING_MODEL`. (R1)
- [x] AC2: Gemini settings yield a `GoogleGenerativeAIEmbeddings` whose model equals `GOOGLE_EMBEDDING_MODEL`. (R2)
- [x] AC3: OpenAI settings yield a `ChatOpenAI` with `OPENAI_LLM_MODEL`; Gemini settings yield a `ChatGoogleGenerativeAI` with `GOOGLE_LLM_MODEL`. (R3)
- [x] AC4: `PGVector` is constructed with the configured connection, collection name, embeddings and `use_jsonb=True`. (R4)
- [x] AC5: `pre_delete_collection=True` reaches the `PGVector` constructor; omitted, it is `False`. (R5)
- [ ] AC6: OpenRouter settings yield an `OpenAIEmbeddings` whose model equals `OPENROUTER_EMBEDDING_MODEL`, whose base URL is `https://openrouter.ai/api/v1` and that does not tokenize input client-side. (R6)
- [ ] AC7: OpenRouter settings yield a `ChatOpenAI` whose model equals `OPENROUTER_LLM_MODEL` and whose base URL is `https://openrouter.ai/api/v1`. (R7)

## Unit tests
- T1: OpenAI embeddings class and model name (AC1) — no network call.
- T2: Gemini embeddings class and model name (AC2) — no network call.
- T3: chat model class and model name for each provider (AC3).
- T4: `PGVector` is patched; constructor receives connection, collection name, embeddings, `use_jsonb=True` (AC4).
- T5: `pre_delete_collection` forwarded as given and defaults to `False` (AC5).
- T6: OpenRouter embeddings class, model name, base URL and plain-text input setting (AC6) — no network call.
- T7: OpenRouter chat model class, model name and base URL (AC7) — no network call.
