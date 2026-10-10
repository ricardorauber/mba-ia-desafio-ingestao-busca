import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent

PROVIDERS = ("openai", "gemini", "openrouter")

DEFAULTS = {
    "OPENROUTER_EMBEDDING_MODEL": "openai/text-embedding-3-small",
    "OPENROUTER_LLM_MODEL": "openai/gpt-6-luna",
    "OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
    "OPENAI_LLM_MODEL": "gpt-6-luna",
    "GOOGLE_EMBEDDING_MODEL": "models/gemini-embedding-001",
    "GOOGLE_LLM_MODEL": "gemini-3.1-flash-lite",
    "PDF_PATH": "document.pdf",
}

API_KEY_VARIABLES = {
    "openai": "OPENAI_API_KEY",
    "gemini": "GOOGLE_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}


class ConfigError(Exception):
    """Raised when the environment does not hold a usable configuration."""


@dataclass(frozen=True)
class Settings:
    llm_provider: str
    openrouter_api_key: str = field(repr=False)
    openrouter_embedding_model: str
    openrouter_llm_model: str
    openai_api_key: str = field(repr=False)
    openai_embedding_model: str
    openai_llm_model: str
    google_api_key: str = field(repr=False)
    google_embedding_model: str
    google_llm_model: str
    database_url: str = field(repr=False)
    collection_name: str
    pdf_path: Path


def _read(environ: Mapping[str, str], name: str) -> str:
    value = environ.get(name)
    if value is None or not value.strip():
        return DEFAULTS.get(name, "")
    return value.strip()


def _require(environ: Mapping[str, str], name: str) -> str:
    value = _read(environ, name)
    if not value:
        raise ConfigError(f"Variável {name} não definida. Preencha-a no arquivo .env.")
    return value


def _resolve_path(raw: str) -> Path:
    path = Path(raw).expanduser()
    return path if path.is_absolute() else ROOT_DIR / path


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    """Read and validate the configuration.

    When ``environ`` is omitted, the ``.env`` file at the repository root is
    loaded into the process environment first.
    """
    if environ is None:
        load_dotenv(ROOT_DIR / ".env")
        environ = os.environ

    provider = _read(environ, "LLM_PROVIDER").lower()
    if provider not in PROVIDERS:
        allowed = ", ".join(PROVIDERS[:-1]) + " ou " + PROVIDERS[-1]
        raise ConfigError(f"Variável LLM_PROVIDER inválida. Valores permitidos: {allowed}.")

    _require(environ, API_KEY_VARIABLES[provider])

    return Settings(
        llm_provider=provider,
        openrouter_api_key=_read(environ, "OPENROUTER_API_KEY"),
        openrouter_embedding_model=_read(environ, "OPENROUTER_EMBEDDING_MODEL"),
        openrouter_llm_model=_read(environ, "OPENROUTER_LLM_MODEL"),
        openai_api_key=_read(environ, "OPENAI_API_KEY"),
        openai_embedding_model=_read(environ, "OPENAI_EMBEDDING_MODEL"),
        openai_llm_model=_read(environ, "OPENAI_LLM_MODEL"),
        google_api_key=_read(environ, "GOOGLE_API_KEY"),
        google_embedding_model=_read(environ, "GOOGLE_EMBEDDING_MODEL"),
        google_llm_model=_read(environ, "GOOGLE_LLM_MODEL"),
        database_url=_require(environ, "DATABASE_URL"),
        collection_name=_require(environ, "PG_VECTOR_COLLECTION_NAME"),
        pdf_path=_resolve_path(_read(environ, "PDF_PATH")),
    )
