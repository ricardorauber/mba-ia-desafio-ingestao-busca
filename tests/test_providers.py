from unittest.mock import patch

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

import providers


def test_openai_embeddings(openai_settings):
    embeddings = providers.get_embeddings(openai_settings)

    assert isinstance(embeddings, OpenAIEmbeddings)
    assert embeddings.model == "text-embedding-3-small"


def test_gemini_embeddings(gemini_settings):
    embeddings = providers.get_embeddings(gemini_settings)

    assert isinstance(embeddings, GoogleGenerativeAIEmbeddings)
    assert embeddings.model == "models/gemini-embedding-001"


def test_chat_model_per_provider(openai_settings, gemini_settings):
    openai_llm = providers.get_llm(openai_settings)
    gemini_llm = providers.get_llm(gemini_settings)

    assert isinstance(openai_llm, ChatOpenAI)
    assert openai_llm.model_name == "gpt-6-luna"
    assert isinstance(gemini_llm, ChatGoogleGenerativeAI)
    assert gemini_llm.model == "gemini-3.1-flash-lite"


def test_vector_store_wiring(openai_settings):
    embeddings = object()

    with patch.object(providers, "PGVector") as pgvector:
        store = providers.get_vector_store(openai_settings, embeddings)

    assert store is pgvector.return_value
    pgvector.assert_called_once_with(
        embeddings=embeddings,
        connection=openai_settings.database_url,
        collection_name="documents",
        use_jsonb=True,
        pre_delete_collection=False,
    )


def test_pre_delete_collection_is_forwarded(openai_settings):
    with patch.object(providers, "PGVector") as pgvector:
        providers.get_vector_store(openai_settings, object(), pre_delete_collection=True)

    assert pgvector.call_args.kwargs["pre_delete_collection"] is True
