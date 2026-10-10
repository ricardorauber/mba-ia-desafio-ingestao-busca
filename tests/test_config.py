import dataclasses

import pytest

from config import ROOT_DIR, ConfigError, load_settings

OPENAI_KEY = "sk-test-openai-secret"
GOOGLE_KEY = "google-test-secret"


def make_env(**overrides):
    env = {
        "LLM_PROVIDER": "openai",
        "OPENAI_API_KEY": OPENAI_KEY,
        "OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
        "OPENAI_LLM_MODEL": "gpt-6-luna",
        "GOOGLE_API_KEY": "",
        "GOOGLE_EMBEDDING_MODEL": "models/gemini-embedding-001",
        "GOOGLE_LLM_MODEL": "gemini-3.1-flash-lite",
        "DATABASE_URL": "postgresql+psycopg://postgres:postgres@localhost:5432/rag",
        "PG_VECTOR_COLLECTION_NAME": "documents",
        "PDF_PATH": "document.pdf",
    }
    env.update(overrides)
    return env


def test_valid_openai_environment_returns_expected_settings():
    settings = load_settings(make_env())

    assert settings.llm_provider == "openai"
    assert settings.openai_api_key == OPENAI_KEY
    assert settings.openai_embedding_model == "text-embedding-3-small"
    assert settings.openai_llm_model == "gpt-6-luna"
    assert settings.google_embedding_model == "models/gemini-embedding-001"
    assert settings.google_llm_model == "gemini-3.1-flash-lite"
    assert settings.database_url == "postgresql+psycopg://postgres:postgres@localhost:5432/rag"
    assert settings.collection_name == "documents"
    assert settings.pdf_path == ROOT_DIR / "document.pdf"


def test_settings_are_immutable():
    settings = load_settings(make_env())

    with pytest.raises(dataclasses.FrozenInstanceError):
        settings.collection_name = "other"


def test_invalid_provider_names_variable_and_allowed_values():
    with pytest.raises(ConfigError) as error:
        load_settings(make_env(LLM_PROVIDER="anthropic"))

    message = str(error.value)
    assert "LLM_PROVIDER" in message
    assert "openai" in message
    assert "gemini" in message


def test_openai_provider_requires_openai_api_key():
    with pytest.raises(ConfigError, match="OPENAI_API_KEY"):
        load_settings(make_env(OPENAI_API_KEY="  "))


def test_gemini_provider_requires_only_google_api_key():
    with pytest.raises(ConfigError, match="GOOGLE_API_KEY"):
        load_settings(make_env(LLM_PROVIDER="gemini", GOOGLE_API_KEY=""))

    settings = load_settings(make_env(LLM_PROVIDER="gemini", GOOGLE_API_KEY=GOOGLE_KEY, OPENAI_API_KEY=""))
    assert settings.llm_provider == "gemini"
    assert settings.google_api_key == GOOGLE_KEY


@pytest.mark.parametrize("variable", ["DATABASE_URL", "PG_VECTOR_COLLECTION_NAME"])
def test_blank_database_variables_are_rejected(variable):
    with pytest.raises(ConfigError, match=variable):
        load_settings(make_env(**{variable: ""}))


def test_repr_and_errors_do_not_leak_api_keys():
    settings = load_settings(make_env(GOOGLE_API_KEY=GOOGLE_KEY))
    text = repr(settings)
    assert OPENAI_KEY not in text
    assert GOOGLE_KEY not in text

    with pytest.raises(ConfigError) as error:
        load_settings(make_env(DATABASE_URL=""))
    assert OPENAI_KEY not in str(error.value)
