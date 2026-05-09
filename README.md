# pdf-search-python

Busca semantica em PDFs usando LangChain, PostgreSQL e pgVector.

## Requisitos

- Python 3.11+
- Docker e Docker Compose
- API Key da OpenAI ou Google (Gemini)

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

Editar `.env` com suas chaves:

```env
APP_ENV=production
LLM_PROVIDER=openai
OPENAI_API_KEY=sua_chave_aqui
POSTGRES_CONNECTION_STRING=postgresql+psycopg2://postgres:postgres@localhost:5432/pdf_search
```

### 3. Adicionar o PDF

Copiar o PDF que deseja consultar para a raiz do projeto com o nome `document.pdf`.

## Execucao

### 1. Subir o banco de dados

```bash
docker compose up -d
```

### 2. Executar a ingestion do PDF

```bash
python src/ingest.py
```

Para usar um PDF especifico:

```bash
python src/ingest.py caminho/para/outro.pdf
```

### 3. Rodar o chat

```bash
python src/chat.py
```

Exemplo de interacao:

```
Chat iniciado. Digite 'sair' para encerrar.

PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhoes de reais.

PERGUNTA: Qual a capital da Franca?
RESPOSTA: Nao tenho informacoes necessarias para responder sua pergunta.
```

Para sair, digitar `sair` ou pressionar `Ctrl+C`.

## Busca avulsa

```bash
python src/search.py "Qual o faturamento da empresa?"
```

## Rodando os testes

```bash
APP_ENV=development pytest tests/ -v
```

Com relatorio de cobertura:

```bash
APP_ENV=development pytest tests/ --cov=src --cov-report=term-missing
```

## Branch strategy

| Branch | Ambiente | Implementacao |
|--------|---------|--------------|
| `develop` | development | Mock (sem banco, sem APIs) |
| `homolog` | production | Real (pgVector + OpenAI/Gemini) |
| `main` | production | Real (pgVector + OpenAI/Gemini) |

Push em `homolog` ou `main` dispara o pipeline de CI/CD que roda todos os testes antes de finalizar o deploy.

## Modelos suportados

**OpenAI** (LLM_PROVIDER=openai):
- Embeddings: text-embedding-3-small
- LLM: gpt-5-nano

**Gemini** (LLM_PROVIDER=gemini):
- Embeddings: models/embedding-001
- LLM: gemini-2.5-flash-lite

## Estrutura do projeto

```
src/
  domain/          <- regras de negocio (sem dependencias externas)
    entities/      <- DocumentChunk
    repositories/  <- interfaces VectorRepository, LLMRepository
    use_cases/     <- IngestPDF, SearchContext
  infrastructure/  <- implementacoes concretas
    repositories/
      mock/        <- sem banco, sem APIs (ambiente development)
      real/        <- pgVector, OpenAI, Gemini (ambiente production)
    config/
      container.py <- factory de DI
  ingest.py        <- entry-point de ingestion
  search.py        <- entry-point de busca avulsa
  chat.py          <- entry-point de chat interativo
prompts/
  search_prompt.txt <- template do prompt de busca
tests/
  unit/            <- testes sem dependencias externas
  integration/     <- testes com implementacoes mock
```
