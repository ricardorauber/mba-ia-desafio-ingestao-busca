from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from config import ConfigError, load_settings
from providers import (
    DATABASE_UNAVAILABLE_MESSAGE,
    get_embeddings,
    get_llm,
    get_vector_store,
    is_database_unavailable,
)

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""


FALLBACK_ANSWER = "Não tenho informações necessárias para responder sua pergunta."

TOP_K = 10


def build_context(documents: list[Document]) -> str:
    return "\n\n".join(document.page_content for document in documents)


def search_prompt():
    """Build the question-answering function, or return None when setup fails."""
    try:
        settings = load_settings()
        embeddings = get_embeddings(settings)
        store = get_vector_store(settings, embeddings)
        llm = get_llm(settings)
    except ConfigError as error:
        print(error)
        return None
    except Exception as error:
        if not is_database_unavailable(error):
            raise
        print(DATABASE_UNAVAILABLE_MESSAGE)
        return None

    chain = PromptTemplate.from_template(PROMPT_TEMPLATE) | llm | StrOutputParser()

    def ask(question: str) -> str:
        results = store.similarity_search_with_score(question, k=TOP_K)
        if not results:
            return FALLBACK_ANSWER
        context = build_context([document for document, _score in results])
        answer = chain.invoke({"contexto": context, "pergunta": question})
        return answer.strip()

    return ask
