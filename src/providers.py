from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres import PGVector
from psycopg import OperationalError as PsycopgOperationalError
from sqlalchemy.exc import OperationalError as SQLAlchemyOperationalError

from config import Settings

DATABASE_ERRORS = (SQLAlchemyOperationalError, PsycopgOperationalError)

DATABASE_UNAVAILABLE_MESSAGE = (
    "Não foi possível conectar ao banco de dados. "
    "Verifique se ele está em execução com: docker compose up -d"
)


def is_database_unavailable(error: BaseException) -> bool:
    """Tell whether ``error`` was caused by a failed database connection.

    PGVector wraps connection failures in a generic ``Exception``, so the
    whole cause chain is inspected.
    """
    current: BaseException | None = error
    while current is not None:
        if isinstance(current, DATABASE_ERRORS):
            return True
        current = current.__cause__ or current.__context__
    return False


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
