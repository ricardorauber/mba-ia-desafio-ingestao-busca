from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres import PGVector

from config import Settings


def get_embeddings(settings: Settings) -> Embeddings:
    if settings.llm_provider == "gemini":
        return GoogleGenerativeAIEmbeddings(
            model=settings.google_embedding_model,
            google_api_key=settings.google_api_key,
        )
    return OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        api_key=settings.openai_api_key,
    )


def get_llm(settings: Settings) -> BaseChatModel:
    if settings.llm_provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=settings.google_llm_model,
            google_api_key=settings.google_api_key,
        )
    return ChatOpenAI(
        model=settings.openai_llm_model,
        api_key=settings.openai_api_key,
    )


def get_vector_store(
    settings: Settings,
    embeddings: Embeddings,
    pre_delete_collection: bool = False,
) -> PGVector:
    return PGVector(
        embeddings=embeddings,
        connection=settings.database_url,
        collection_name=settings.collection_name,
        use_jsonb=True,
        pre_delete_collection=pre_delete_collection,
    )
