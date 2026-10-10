# 0005 - Chat CLI

## Goal
Let the user ask questions in the terminal and read the answers, in the format shown in the challenge.

## Scope
- In: `src/chat.py` (`run_chat(ask, input_fn, output_fn)`, `main`).
- Out: retrieval and prompting (0004).

## Requirements
- R1: WHEN `search_prompt()` returns `None`, `main` SHALL print `Não foi possível iniciar o chat. Verifique os erros de inicialização.` and exit with code 1.
- R2: On start, the system SHALL print `Faça sua pergunta:` followed by a hint that `sair`, `exit` or `quit` end the chat.
- R3: The system SHALL read each question with the prompt `PERGUNTA: ` and print the answer as `RESPOSTA: <text>`, followed by a blank line.
- R4: WHEN the input, trimmed, is empty, the system SHALL not call `ask` and SHALL prompt again.
- R5: WHEN the input, trimmed and case-insensitive, is `sair`, `exit` or `quit`, the system SHALL print `Até logo!` and end with code 0.
- R6: WHEN the user presses Ctrl+C or Ctrl+D, the system SHALL print `Até logo!` and end with code 0, with no stack trace.
- R7: WHEN `ask` raises during a question, the system SHALL print `RESPOSTA: Erro ao processar a pergunta: <short reason>` and keep the chat running.

## Acceptance criteria
- [ ] AC1: Initialization failure prints the fixed message and exits 1. (R1)
- [ ] AC2: Start-up output shows `Faça sua pergunta:` and the exit hint. (R2)
- [ ] AC3: Typing a question prints `RESPOSTA: ` plus the answer. (R3)
- [ ] AC4: Pressing Enter on an empty line asks again without calling `ask`. (R4)
- [ ] AC5: `SAIR`, `exit` and ` quit ` all end the chat with `Até logo!`. (R5)
- [ ] AC6: Ctrl+C and Ctrl+D end the chat with `Até logo!` and no traceback. (R6)
- [ ] AC7: An exception in `ask` is reported and the next question is still accepted. (R7)

## Unit tests
- T1: scripted inputs `["Pergunta 1", "sair"]` with fake `ask` → output contains `RESPOSTA: <fake answer>` and `Até logo!` (AC3, AC5).
- T2: `["", "   ", "sair"]` → `ask` never called (AC4).
- T3: each of `SAIR`, `exit`, ` quit ` ends the loop (AC5).
- T4: `input_fn` raising `KeyboardInterrupt`, and separately `EOFError`, ends with `Até logo!` (AC6).
- T5: `ask` raising once then succeeding → error line printed, second answer printed (AC7).
- T6: `main` with `search_prompt` patched to return `None` → fixed message, exit code 1 (AC1).
