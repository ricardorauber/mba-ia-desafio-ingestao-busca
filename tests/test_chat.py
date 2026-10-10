from unittest.mock import MagicMock, patch

import pytest

import chat


def scripted(*entries):
    """Return an input function that yields each entry, raising it when it is an exception."""
    queue = list(entries)

    def input_fn(_prompt):
        entry = queue.pop(0)
        if isinstance(entry, BaseException):
            raise entry
        return entry

    return input_fn


def run(ask, *entries):
    lines = []
    exit_code = chat.run_chat(ask, scripted(*entries), lambda *args: lines.append(" ".join(map(str, args))))
    return exit_code, "\n".join(lines)


def test_answers_question_then_exits():
    ask = MagicMock(return_value="O faturamento foi de 10 milhões de reais.")

    exit_code, output = run(ask, "Pergunta 1", "sair")

    assert exit_code == 0
    ask.assert_called_once_with("Pergunta 1")
    assert "Faça sua pergunta:" in output
    assert "RESPOSTA: O faturamento foi de 10 milhões de reais." in output
    assert output.endswith("Até logo!")


def test_blank_input_is_ignored():
    ask = MagicMock()

    exit_code, _ = run(ask, "", "   ", "sair")

    assert exit_code == 0
    ask.assert_not_called()


@pytest.mark.parametrize("command", ["SAIR", "exit", " quit "])
def test_exit_commands_end_the_chat(command):
    exit_code, output = run(MagicMock(), command)

    assert exit_code == 0
    assert output.endswith("Até logo!")


@pytest.mark.parametrize("interruption", [KeyboardInterrupt(), EOFError()], ids=["ctrl-c", "ctrl-d"])
def test_interruptions_end_the_chat(interruption):
    exit_code, output = run(MagicMock(), interruption)

    assert exit_code == 0
    assert output.endswith("Até logo!")
    assert "Traceback" not in output


def test_error_in_ask_keeps_chat_running():
    ask = MagicMock(side_effect=[RuntimeError("limite de requisições atingido"), "Segunda resposta"])

    exit_code, output = run(ask, "Primeira", "Segunda", "sair")

    assert exit_code == 0
    assert "RESPOSTA: Erro ao processar a pergunta: limite de requisições atingido" in output
    assert "RESPOSTA: Segunda resposta" in output


def test_main_reports_initialization_failure(capsys):
    with patch.object(chat, "search_prompt", return_value=None):
        exit_code = chat.main()

    assert exit_code == 1
    assert "Não foi possível iniciar o chat. Verifique os erros de inicialização." in capsys.readouterr().out
