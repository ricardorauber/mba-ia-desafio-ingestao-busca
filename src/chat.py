import sys
from collections.abc import Callable

from search import search_prompt

EXIT_COMMANDS = {"sair", "exit", "quit"}
GOODBYE_MESSAGE = "Até logo!"
MAX_ERROR_LENGTH = 200


def short_reason(error: Exception) -> str:
    lines = str(error).strip().splitlines()
    reason = lines[0] if lines else type(error).__name__
    return reason[:MAX_ERROR_LENGTH]


def run_chat(
    ask: Callable[[str], str],
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[..., None] = print,
) -> int:
    output_fn("Faça sua pergunta:")
    output_fn("(digite 'sair', 'exit' ou 'quit' para encerrar)")
    output_fn()

    while True:
        try:
            question = input_fn("PERGUNTA: ").strip()
            if not question:
                continue
            if question.lower() in EXIT_COMMANDS:
                output_fn(GOODBYE_MESSAGE)
                return 0
            try:
                answer = ask(question)
            except Exception as error:
                answer = f"Erro ao processar a pergunta: {short_reason(error)}"
        except (KeyboardInterrupt, EOFError):
            output_fn()
            output_fn(GOODBYE_MESSAGE)
            return 0

        output_fn(f"RESPOSTA: {answer}")
        output_fn()


def main() -> int:
    ask = search_prompt()

    if not ask:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return 1

    return run_chat(ask)


if __name__ == "__main__":
    sys.exit(main())
