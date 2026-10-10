# 0003 - PDF ingestion

## Goal
Load the PDF, split it into 1000-character chunks with 150 overlap, embed each chunk and store the vectors in PostgreSQL with pgVector, replacing any previous ingestion.

## Scope
- In: `src/ingest.py` (`load_documents`, `split_documents`, `ingest_pdf`, `main`).
- Out: search and chat (0004, 0005).

## Requirements
- R1: The system SHALL load the file at `PDF_PATH` with `PyPDFLoader`; a relative path SHALL be resolved from the repository root.
- R2: The system SHALL split the documents with `RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)`.
- R3: The system SHALL drop chunks whose text is empty or whitespace only.
- R4: The system SHALL store every chunk in the vector store built by `get_vector_store(settings, embeddings, pre_delete_collection=True)`, so each run deletes the existing collection and re-ingests from scratch.
- R5: WHEN ingestion finishes, the system SHALL print, in Brazilian Portuguese, the number of pages loaded, chunks stored and the collection name.
- R6: WHEN `PDF_PATH` does not exist, the system SHALL print `Arquivo PDF não encontrado: <path>` and exit with code 1 without touching the database.
- R7: WHEN settings are invalid (`ConfigError`) or the database is unreachable, the system SHALL print a short Brazilian Portuguese message (for the database: tell the user to run `docker compose up -d`), with no stack trace, and exit with code 1.

## Acceptance criteria
- [ ] AC1: `python src/ingest.py` with the database up stores the chunks of `document.pdf` and prints pages, chunks and collection name. (R1, R4, R5)
- [ ] AC2: Running it twice leaves the same number of rows in the collection as running it once. (R4)
- [ ] AC3: Every stored chunk has at most 1000 characters and consecutive chunks of the same page share overlap. (R2)
- [ ] AC4: No stored chunk is blank. (R3)
- [ ] AC5: A missing PDF prints the not-found message, exits 1 and never builds the vector store. (R6)
- [ ] AC6: With the database down, the script prints the `docker compose up -d` hint, no traceback, exit code 1. (R7)

## Unit tests
- T1: `split_documents` on a synthetic 2500-character document returns chunks of ≤1000 characters with 150-character overlap (AC3).
- T2: `split_documents` drops whitespace-only chunks (AC4).
- T3: `ingest_pdf` with patched loader and vector store calls `get_vector_store(..., pre_delete_collection=True)` and `add_documents` with all chunks (AC1, AC2).
- T4: missing PDF path → exit code 1, message printed, vector store factory not called (AC5).
- T5: `ConfigError` → message printed, exit code 1 (R7).
- T6: database `OperationalError` → message with `docker compose up -d`, exit code 1 (AC6).
