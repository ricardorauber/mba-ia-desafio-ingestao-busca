import pytest

from config import load_settings


def build_settings(**overrides):
    env = {
        "LLM_PROVIDER": "openai",
        "OPENAI_API_KEY": "sk-test-openai",
        "OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
        "OPENAI_LLM_MODEL": "gpt-6-luna",
        "GOOGLE_API_KEY": "google-test",
        "GOOGLE_EMBEDDING_MODEL": "models/gemini-embedding-001",
        "GOOGLE_LLM_MODEL": "gemini-3.1-flash-lite",
        "DATABASE_URL": "postgresql+psycopg://postgres:postgres@localhost:5432/rag",
        "PG_VECTOR_COLLECTION_NAME": "documents",
        "PDF_PATH": "document.pdf",
    }
    env.update(overrides)
    return load_settings(env)


@pytest.fixture
def openai_settings():
    return build_settings()


@pytest.fixture
def gemini_settings():
    return build_settings(LLM_PROVIDER="gemini")
