# Ingestão e Busca Semântica com LangChain e Postgres

Software que lê um PDF, armazena seus trechos como vetores no PostgreSQL com pgVector e responde perguntas pelo terminal **usando apenas o conteúdo do PDF**.

- **Ingestão** (`src/ingest.py`): carrega o `document.pdf`, divide em chunks de 1000 caracteres com overlap de 150, gera os embeddings e grava no Postgres.
- **Busca** (`src/search.py`): vetoriza a pergunta, busca os 10 trechos mais relevantes (`k=10`), monta o prompt e chama a LLM.
- **Chat** (`src/chat.py`): CLI interativa de perguntas e respostas.

Funciona com **OpenRouter** (padrão), **OpenAI** ou **Google Gemini**, escolhidos pela variável `LLM_PROVIDER`.

## Pré-requisitos

- Python 3.12 ou superior (testado no 3.14)
- Docker com Docker Compose
- Uma API key da [OpenRouter](https://openrouter.ai/keys) (padrão), da [OpenAI](https://platform.openai.com/api-keys) **ou** do [Google AI Studio](https://aistudio.google.com/apikey)

## Como executar

### 1. Criar e ativar o ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar as variáveis de ambiente

```bash
cp .env.example .env
```

Abra o `.env` e preencha a API key do provedor escolhido: `OPENROUTER_API_KEY` (padrão), `OPENAI_API_KEY` ou `GOOGLE_API_KEY`. O `.env` está no `.gitignore` e nunca deve ser commitado.

### 4. Subir o banco de dados

```bash
docker compose up -d
```

Isso sobe o PostgreSQL 17 com a extensão pgVector na porta `5432`.

### 5. Executar a ingestão do PDF

```bash
python src/ingest.py
```

Saída esperada:

```
Ingestão concluída: 34 páginas carregadas, 67 chunks armazenados na collection 'documents'.
```

Cada execução **apaga a collection e refaz a ingestão do zero**, então rodar mais de uma vez não duplica dados.

### 6. Rodar o chat

```bash
python src/chat.py
```

### 7. Rodar os testes (opcional)

```bash
pytest
```

Os testes unitários não precisam de banco nem de API key.

## Exemplo de uso

```
Faça sua pergunta:
(digite 'sair', 'exit' ou 'quit' para encerrar)

PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento da SuperTechIABrazil é R$ 10.000.000,00.

PERGUNTA: Em que ano foi fundada a Alfa Energia S.A.?
RESPOSTA: 1972

PERGUNTA: Quantos clientes temos em 2024?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.

PERGUNTA: sair
Até logo!
```

Para encerrar o chat, digite `sair`, `exit` ou `quit`, ou pressione `Ctrl+C` / `Ctrl+D`. Pressionar Enter sem texto apenas pede a pergunta novamente.

## Variáveis de ambiente

| Variável | Padrão no `.env.example` | Para que serve |
| --- | --- | --- |
| `LLM_PROVIDER` | `openrouter` | Provedor de embeddings e LLM: `openrouter`, `openai` ou `gemini`. |
| `OPENROUTER_API_KEY` | _(vazio)_ | API key da OpenRouter. Obrigatória quando `LLM_PROVIDER=openrouter`. |
| `OPENROUTER_EMBEDDING_MODEL` | `openai/text-embedding-3-small` | Modelo de embeddings usado via OpenRouter. |
| `OPENROUTER_LLM_MODEL` | `openai/gpt-6-luna` | Modelo de chat usado via OpenRouter para gerar a resposta. |
| `OPENAI_API_KEY` | _(vazio)_ | API key da OpenAI. Obrigatória quando `LLM_PROVIDER=openai`. |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Modelo de embeddings da OpenAI. |
| `OPENAI_LLM_MODEL` | `gpt-6-luna` | Modelo de chat da OpenAI que gera a resposta. |
| `GOOGLE_API_KEY` | _(vazio)_ | API key do Google. Obrigatória quando `LLM_PROVIDER=gemini`. |
| `GOOGLE_EMBEDDING_MODEL` | `models/gemini-embedding-001` | Modelo de embeddings do Gemini. |
| `GOOGLE_LLM_MODEL` | `gemini-3.1-flash-lite` | Modelo de chat do Gemini que gera a resposta. |
| `DATABASE_URL` | `postgresql+psycopg://postgres:postgres@localhost:5432/rag` | Conexão com o Postgres do `docker-compose.yml`. |
| `PG_VECTOR_COLLECTION_NAME` | `documents` | Nome da collection onde os vetores são gravados. |
| `PDF_PATH` | `document.pdf` | Caminho do PDF a ingerir (relativo à raiz do projeto ou absoluto). |

### Alternando entre OpenRouter, OpenAI e Gemini

Basta mudar `LLM_PROVIDER` no `.env` (`openrouter`, `openai` ou `gemini`) e preencher a API key correspondente. A OpenRouter é acessada pela API compatível com a OpenAI em `https://openrouter.ai/api/v1`, tanto para embeddings quanto para o chat; qualquer modelo do catálogo dela pode ser usado nas variáveis `OPENROUTER_*`. Somente a key do provedor selecionado é exigida.

### Modelos padrão

Os padrões são os modelos mais leves e baratos de cada provedor, conferidos na documentação oficial em outubro de 2026:

- **OpenRouter:** `openai/text-embedding-3-small` (embeddings, 1536 dimensões) e `openai/gpt-6-luna` (chat).
- **OpenAI:** `text-embedding-3-small` (embeddings, 1536 dimensões) e `gpt-6-luna` (chat).
- **Gemini:** `gemini-embedding-001` (embeddings, 3072 dimensões) e `gemini-3.1-flash-lite` (chat, com camada gratuita).

Nomes de modelos mudam com frequência; se algum for descontinuado, troque pelo equivalente atual nas variáveis acima.

## Trocando o modelo de embeddings

Modelos de embeddings diferentes geram vetores de dimensões diferentes, e a tabela é criada com a dimensão do modelo usado na primeira ingestão. Ao trocar o modelo ou o provedor:

1. Atualize o `.env`.
2. Rode a ingestão de novo — ela apaga a collection e recria tudo com o novo modelo:

   ```bash
   python src/ingest.py
   ```

Se ainda assim houver erro de dimensão, apague o volume do banco e recomece do zero:

```bash
docker compose down -v
```

```bash
docker compose up -d
```

```bash
python src/ingest.py
```

## Mensagens de erro comuns

- `Variável OPENROUTER_API_KEY não definida.` — preencha a key do provedor escolhido no `.env` (`OPENROUTER_API_KEY`, `OPENAI_API_KEY` ou `GOOGLE_API_KEY`).
- `Não foi possível conectar ao banco de dados. Verifique se ele está em execução com: docker compose up -d` — o Postgres não está rodando.
- `Arquivo PDF não encontrado: ...` — confira o `PDF_PATH`.

## Estrutura do projeto

```
├── docker-compose.yml    # PostgreSQL + pgVector
├── requirements.txt      # Dependências
├── .env.example          # Template das variáveis de ambiente
├── pytest.ini            # Configuração dos testes
├── src/
│   ├── config.py         # Leitura e validação do .env
│   ├── providers.py      # Embeddings, LLM e vector store (OpenRouter, OpenAI ou Gemini)
│   ├── ingest.py         # Script de ingestão do PDF
│   ├── search.py         # Busca semântica e chamada à LLM
│   └── chat.py           # CLI para interação com o usuário
├── tests/                # Testes unitários (pytest)
├── specs/                # Especificações (SDD) de cada etapa
├── adrs/                 # Registros de decisões de arquitetura
├── document.pdf          # PDF para ingestão
└── README.md
```
