from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document
from sqlalchemy.exc import OperationalError

import ingest
from config import ConfigError
from conftest import build_settings


@pytest.fixture
def pdf_settings(tmp_path):
    pdf = tmp_path / "document.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    return build_settings(PDF_PATH=str(pdf))


def test_split_respects_chunk_size_and_overlap():
    words = [f"palavra{index:04d}" for index in range(250)]
    text = " ".join(words)
    assert len(text) >= 2500

    chunks = ingest.split_documents([Document(page_content=text, metadata={"page": 0})])

    assert len(chunks) >= 3
    assert all(len(chunk.page_content) <= 1000 for chunk in chunks)
    for previous, current in zip(chunks, chunks[1:]):
        overlap = set(previous.page_content.split()) & set(current.page_content.split())
        overlap_length = len(" ".join(sorted(overlap)))
        assert 0 < overlap_length <= 150


def test_split_drops_blank_chunks():
    documents = [
        Document(page_content="   \n\t  ", metadata={"page": 0}),
        Document(page_content="Conteúdo real", metadata={"page": 1}),
    ]

    chunks = ingest.split_documents(documents)

    assert [chunk.page_content for chunk in chunks] == ["Conteúdo real"]


def test_ingest_recreates_collection_and_stores_all_chunks(pdf_settings, capsys):
    pages = [Document(page_content="Alfa Energia S.A. R$ 722.875.391,46 1972", metadata={"page": 0})]

    with (
        patch.object(ingest, "load_documents", return_value=pages),
        patch.object(ingest, "get_embeddings") as get_embeddings,
        patch.object(ingest, "get_vector_store") as get_vector_store,
    ):
        ingest.ingest_pdf(pdf_settings)

    get_vector_store.assert_called_once_with(
        pdf_settings, get_embeddings.return_value, pre_delete_collection=True
    )
    stored = get_vector_store.return_value.add_documents.call_args.args[0]
    assert [chunk.page_content for chunk in stored] == [pages[0].page_content]
    output = capsys.readouterr().out
    assert "1 páginas" in output
    assert "1 chunks" in output
    assert "documents" in output


def test_missing_pdf_exits_without_touching_database(tmp_path, capsys):
    missing = tmp_path / "missing.pdf"
    settings = build_settings(PDF_PATH=str(missing))

    with (
        patch.object(ingest, "load_settings", return_value=settings),
        patch.object(ingest, "get_vector_store") as get_vector_store,
    ):
        exit_code = ingest.main()

    assert exit_code == 1
    assert f"Arquivo PDF não encontrado: {missing}" in capsys.readouterr().out
    get_vector_store.assert_not_called()


def test_config_error_exits_with_message(capsys):
    with patch.object(ingest, "load_settings", side_effect=ConfigError("Variável DATABASE_URL não definida.")):
        exit_code = ingest.main()

    assert exit_code == 1
    assert "DATABASE_URL" in capsys.readouterr().out


def wrapped_connection_error():
    try:
        raise OperationalError("connect", {}, Exception("connection refused"))
    except OperationalError as cause:
        try:
            raise Exception("Failed to create vector extension") from cause
        except Exception as wrapped:
            return wrapped


@pytest.mark.parametrize(
    "error",
    [OperationalError("connect", {}, Exception("connection refused")), wrapped_connection_error()],
    ids=["direct", "wrapped-by-pgvector"],
)
def test_unreachable_database_exits_with_docker_hint(pdf_settings, capsys, error):

    with (
        patch.object(ingest, "load_settings", return_value=pdf_settings),
        patch.object(ingest, "load_documents", return_value=[Document(page_content="texto")]),
        patch.object(ingest, "get_embeddings", return_value=MagicMock()),
        patch.object(ingest, "get_vector_store", side_effect=error),
    ):
        exit_code = ingest.main()

    output = capsys.readouterr().out
    assert exit_code == 1
    assert "docker compose up -d" in output
    assert "Traceback" not in output
