from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

import search
from config import ConfigError
from conftest import build_settings


class RecordingLLM:
    """Runnable stand-in for a chat model that records every prompt it receives."""

    def __init__(self, answer="  O faturamento foi de R$ 722.875.391,46.  "):
        self.answer = answer
        self.prompts = []
        self.runnable = RunnableLambda(self._respond)

    def _respond(self, prompt_value):
        self.prompts.append(prompt_value.to_string())
        return AIMessage(content=self.answer)


def results_for(*texts):
    return [(Document(page_content=text), 0.1 * index) for index, text in enumerate(texts)]


@pytest.fixture
def wiring():
    llm = RecordingLLM()
    store = MagicMock()
    with (
        patch.object(search, "load_settings", return_value=build_settings()) as load_settings,
        patch.object(search, "get_embeddings") as get_embeddings,
        patch.object(search, "get_vector_store", return_value=store) as get_vector_store,
        patch.object(search, "get_llm", return_value=llm.runnable) as get_llm,
    ):
        yield {
            "llm": llm,
            "store": store,
            "load_settings": load_settings,
            "get_embeddings": get_embeddings,
            "get_vector_store": get_vector_store,
            "get_llm": get_llm,
        }


def test_build_context_joins_documents_in_order():
    documents = [Document(page_content=text) for text in ("primeiro", "segundo", "terceiro")]

    assert search.build_context(documents) == "primeiro\n\nsegundo\n\nterceiro"


def test_ask_uses_top_ten_and_sends_chunks_and_question(wiring):
    wiring["store"].similarity_search_with_score.return_value = results_for("chunk A", "chunk B")
    question = "Qual o faturamento da Alfa Energia S.A.?"

    answer = search.search_prompt()(question)

    wiring["store"].similarity_search_with_score.assert_called_once_with(question, k=10)
    prompt = wiring["llm"].prompts[0]
    assert "chunk A\n\nchunk B" in prompt
    assert question in prompt
    assert answer == "O faturamento foi de R$ 722.875.391,46."


def test_clients_are_built_once_across_questions(wiring):
    wiring["store"].similarity_search_with_score.return_value = results_for("chunk")

    ask = search.search_prompt()
    ask("primeira pergunta")
    ask("segunda pergunta")

    wiring["load_settings"].assert_called_once()
    wiring["get_embeddings"].assert_called_once()
    wiring["get_vector_store"].assert_called_once()
    wiring["get_llm"].assert_called_once()
    assert len(wiring["llm"].prompts) == 2


def test_config_error_returns_none(capsys):
    with patch.object(search, "load_settings", side_effect=ConfigError("Variável OPENAI_API_KEY não definida.")):
        assert search.search_prompt() is None

    assert "OPENAI_API_KEY" in capsys.readouterr().out


def test_empty_search_returns_fallback_without_calling_llm(wiring):
    wiring["store"].similarity_search_with_score.return_value = []

    answer = search.search_prompt()("Qual é a capital da França?")

    assert answer == "Não tenho informações necessárias para responder sua pergunta."
    assert wiring["llm"].prompts == []


def test_prompt_template_keeps_placeholders_and_fallback_sentence():
    assert "{contexto}" in search.PROMPT_TEMPLATE
    assert "{pergunta}" in search.PROMPT_TEMPLATE
    assert '"Não tenho informações necessárias para responder sua pergunta."' in search.PROMPT_TEMPLATE
