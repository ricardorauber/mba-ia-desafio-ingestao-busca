import sys
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import ConfigError, Settings, load_settings
from providers import DATABASE_UNAVAILABLE_MESSAGE, get_embeddings, get_vector_store, is_database_unavailable

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def load_documents(pdf_path: Path) -> list[Document]:
    return PyPDFLoader(str(pdf_path)).load()


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.split_documents(documents)
    return [chunk for chunk in chunks if chunk.page_content.strip()]


def ingest_pdf(settings: Settings) -> None:
    pages = load_documents(settings.pdf_path)
    chunks = split_documents(pages)

    embeddings = get_embeddings(settings)
    store = get_vector_store(settings, embeddings, pre_delete_collection=True)
    store.add_documents(chunks)

    print(
        f"Ingestão concluída: {len(pages)} páginas carregadas, "
        f"{len(chunks)} chunks armazenados na collection '{settings.collection_name}'."
    )


def main() -> int:
    try:
        settings = load_settings()
    except ConfigError as error:
        print(error)
        return 1

    if not settings.pdf_path.is_file():
        print(f"Arquivo PDF não encontrado: {settings.pdf_path}")
        return 1

    try:
        ingest_pdf(settings)
    except Exception as error:
        if not is_database_unavailable(error):
            raise
        print(DATABASE_UNAVAILABLE_MESSAGE)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
