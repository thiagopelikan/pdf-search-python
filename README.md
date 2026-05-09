# pdf-search-python

Busca semantica em PDFs usando LangChain, PostgreSQL e pgVector.

O projeto le um PDF, divide o texto em chunks, gera embeddings via OpenAI ou Gemini e armazena no banco vetorial. O usuario faz perguntas via CLI e recebe respostas baseadas apenas no conteudo do PDF.

## Requisitos

- Python 3.11+
- Docker e Docker Compose
- API Key da OpenAI **ou** Google (Gemini)

## Configuracao inicial

### 1. Clonar e criar ambiente virtual

```bash
git clone https://github.com/thiagopelikan/pdf-search-python.git
cd pdf-search-python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar variaveis de ambiente

```bash
cp .env.example .env
```

Edite `.env` com suas chaves. Os campos obrigatorios dependem do provider escolhido:

```env
APP_ENV=production
LLM_PROVIDER=openai          # ou gemini

# OpenAI (quando LLM_PROVIDER=openai)
OPENAI_API_KEY=sk-...

# Gemini (quando LLM_PROVIDER=gemini)
GOOGLE_API_KEY=AIza...

POSTGRES_CONNECTION_STRING=postgresql+psycopg2://postgres:postgres@localhost:5432/pdf_search
```

Os demais parametros ja possuem valores padrao adequados:

| Variavel | Padrao | Descricao |
|---|---|---|
| `CHUNK_SIZE` | 1000 | Tamanho de cada chunk em caracteres |
| `CHUNK_OVERLAP` | 150 | Sobreposicao entre chunks |
| `SEARCH_K` | 10 | Numero de resultados retornados na busca |
| `OPENAI_LLM_MODEL` | gpt-5-nano | Modelo LLM OpenAI |
| `OPENAI_EMBEDDING_MODEL` | text-embedding-3-small | Modelo de embeddings OpenAI |
| `GEMINI_LLM_MODEL` | gemini-2.5-flash-lite | Modelo LLM Gemini |
| `GEMINI_EMBEDDING_MODEL` | models/gemini-embedding-001 | Modelo de embeddings Gemini |

### 3. PDF para ingestion

O projeto inclui `document.pdf` de exemplo (empresa ficticia SuperTechIABrazil). Para usar um PDF proprio, substitua o arquivo `document.pdf` na raiz do projeto.

## Execucao

### 1. Subir o banco de dados

```bash
docker compose up -d
```

### 2. Ingerir o PDF

```bash
make ingest
```

Para especificar outro PDF:

```bash
venv/bin/python src/ingest.py caminho/para/arquivo.pdf
```

> **Nota:** cada provider usa sua propria colecao no pgVector (`pdf_search_chunks_openai` ou `pdf_search_chunks_gemini`). Se trocar de provider, rode a ingestion novamente.

### 3. Rodar o chat interativo

```bash
make chat
```

Exemplo de interacao:

```
Chat iniciado. Digite 'sair' para encerrar.

PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhoes de reais.

PERGUNTA: Qual a capital da Franca?
RESPOSTA: Nao tenho informacoes necessarias para responder sua pergunta.

PERGUNTA: sair
```

### 4. Busca avulsa (sem loop)

```bash
venv/bin/python src/search.py "Qual o faturamento da empresa?"
```

## Testes

### Testes unitarios e de integracao (sem dependencias externas)

```bash
make test
```

Com relatorio de cobertura:

```bash
APP_ENV=development PYTHONWARNINGS=ignore venv/bin/python -m pytest tests/unit tests/integration --cov=src --cov-report=term-missing
```

### Testes end-to-end (requerem Docker + API key)

```bash
make test-e2e-openai   # com OpenAI
make test-e2e-gemini   # com Gemini
```

### Smoke test (validacao rapida antes de release)

```bash
LLM_PROVIDER=openai ./scripts/smoke_test.sh
```

O script valida: Docker, PostgreSQL, PDF, ingestion, busca relevante e recusa de pergunta fora de contexto.

## Estrutura do projeto

```
document.pdf          <- PDF de exemplo incluido no repositorio
src/
  domain/             <- regras de negocio (sem dependencias externas)
    entities/         <- DocumentChunk
    repositories/     <- interfaces VectorRepository, LLMRepository
    use_cases/        <- IngestPDF, SearchContext
  infrastructure/     <- implementacoes concretas
    repositories/
      mock/           <- sem banco, sem APIs (APP_ENV=development)
      real/           <- pgVector, OpenAI, Gemini (APP_ENV=production)
    config/
      container.py    <- factory de DI — seleciona implementacoes por APP_ENV
  ingest.py           <- entry-point de ingestion
  search.py           <- entry-point de busca avulsa
  chat.py             <- entry-point de chat interativo
prompts/
  search_prompt.txt   <- template do prompt enviado ao LLM
tests/
  unit/               <- testes sem dependencias externas
  integration/        <- testes com repositorios mock
  e2e/                <- testes end-to-end com Docker e API real
scripts/
  smoke_test.sh       <- validacao completa do pipeline
```

## Providers suportados

**OpenAI** (`LLM_PROVIDER=openai`):
- Embeddings: `text-embedding-3-small` (1536 dimensoes)
- LLM: `gpt-5-nano`

**Gemini** (`LLM_PROVIDER=gemini`):
- Embeddings: `models/gemini-embedding-001` (768 dimensoes)
- LLM: `gemini-2.5-flash-lite`

## Branches

| Branch | Descricao |
|---|---|
| `main` | Producao — CI roda todos os testes antes de aceitar o merge |
| `homolog` | Homologacao — validacao pre-release |
| `develop` | Desenvolvimento continuo |
