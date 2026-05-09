# Guidelines de Desenvolvimento Python — pdf-search-python

Este documento define as boas praticas obrigatorias para todo o codigo do projeto.
Todos os subagentes e desenvolvedores devem seguir estas regras sem excecao.

---

## 1. Arquitetura Clean

O projeto segue Clean Architecture com tres camadas. Dependencias sempre apontam para dentro (domain nao conhece infrastructure).

```
src/
  domain/          <- regras de negocio puras, sem dependencias externas
    entities/      <- objetos de dominio (dataclasses ou Pydantic)
    repositories/  <- interfaces abstratas (ABC)
    use_cases/     <- casos de uso, orquestram entidades e repositorios
  infrastructure/  <- implementacoes concretas de repositorios, config, DI
    repositories/
      mock/        <- implementacoes em memoria para testes e ambiente develop
      real/        <- implementacoes reais (pgVector, OpenAI, Gemini)
    config/
      container.py <- factory de DI, seleciona implementacao por APP_ENV
  ingest.py        <- entry-point CLI para ingestion
  search.py        <- entry-point CLI para busca avulsa
  chat.py          <- entry-point CLI para chat interativo
```

**Regras de dependencia:**
- `domain` nao importa nada de `infrastructure`
- `use_cases` recebem repositorios via injecao de dependencia (nunca instanciam)
- `infrastructure` conhece `domain` mas `domain` nunca conhece `infrastructure`

---

## 2. Dependency Injection

- Todas as dependencias externas (repositorios, LLMs, embeddings) sao injetadas via construtor
- O container DI fica em `src/infrastructure/config/container.py`
- A variavel de ambiente `APP_ENV` controla qual implementacao e injetada:
  - `development` -> repositorios mock (sem banco de dados, sem APIs externas)
  - `production` -> implementacoes reais (pgVector, OpenAI ou Gemini)
- Os entry-points (`ingest.py`, `chat.py`, `search.py`) chamam o container para montar as dependencias

```python
# Exemplo de uso correto
from src.infrastructure.config.container import Container

container = Container()
use_case = container.ingest_pdf_use_case()
use_case.execute(pdf_path="document.pdf")
```

---

## 3. Use Cases

- Uma classe por caso de uso
- Metodo principal sempre chamado `execute()`
- Recebem todas as dependencias via construtor
- Nao contem logica de infraestrutura (sem SQL, sem HTTP, sem I/O de arquivo)
- Nao conhecem detalhes de framework (sem LangChain diretamente, apenas via interface)

```python
# Exemplo correto
class IngestPDF:
    def __init__(self, vector_repository: VectorRepository) -> None:
        self._vector_repository = vector_repository

    def execute(self, pdf_path: str) -> int:
        # retorna numero de chunks armazenados
        ...
```

---

## 4. Repositorios

Para cada acesso externo (banco de dados, API, sistema de arquivos), criar:

1. **Interface abstrata** em `src/domain/repositories/` usando `ABC` e `abstractmethod`
2. **Implementacao mock** em `src/infrastructure/repositories/mock/` — em memoria, sem dependencias externas
3. **Implementacao real** em `src/infrastructure/repositories/real/` — usa bibliotecas externas (LangChain, pgVector, OpenAI, Gemini)

```python
# Interface (domain)
from abc import ABC, abstractmethod

class VectorRepository(ABC):
    @abstractmethod
    def store(self, chunks: list[DocumentChunk]) -> int: ...

    @abstractmethod
    def search(self, query: str, k: int) -> list[tuple[DocumentChunk, float]]: ...
```

---

## 5. Prompts e Textos

- **Todo** texto de prompt, mensagem de sistema, template de resposta e string exibida ao usuario deve estar em arquivo `.txt` dentro de `prompts/`
- O codigo Python carrega o arquivo com `pathlib.Path` e substitui variaveis com `.format()` ou f-string
- Nunca hardcode prompts ou mensagens longas no codigo Python
- Isso garante versionamento separado dos prompts

```python
# Carregamento correto de prompt
from pathlib import Path

def _load_prompt(name: str) -> str:
    return (Path(__file__).parent.parent.parent / "prompts" / name).read_text(encoding="utf-8")
```

---

## 6. Sem Emojis

- Nenhum emoji em codigo, comentarios, logs, outputs de CLI, mensagens de erro ou qualquer string do sistema
- Isso inclui subagentes, scripts de CI/CD e documentacao tecnica gerada automaticamente

---

## 7. Comentarios

Comentar todos os locais pertinentes:
- Todas as funcoes e metodos publicos com docstring de uma linha explicando o proposito
- Logica nao-obvia com comentario inline explicando o porque (nao o que)
- Decisoes de design que nao sao evidentes no codigo
- Parametros com significado especifico (ex: `k=10` no similarity search)
- Nao comentar codigo obvio (ex: `x = 1  # atribui 1 a x`)

```python
def execute(self, query: str) -> str:
    """Executa busca semantica e retorna resposta contextualizada do LLM."""
    # k=10 conforme especificado em docs/requirements.txt
    results = self._vector_repository.search(query, k=10)
    ...
```

---

## 8. Testes

- Framework: `pytest`
- Cobertura minima: 80% por modulo
- **Testes unitarios** em `tests/unit/`: testam use cases e entidades usando mocks; sem I/O externo
- **Testes de integracao** em `tests/integration/`: testam repositorios mock e, opcionalmente, reais com Docker
- Todos os testes unitarios devem rodar sem banco de dados, sem API keys, sem internet
- Use `pytest-mock` ou `unittest.mock` para mockar dependencias nos testes unitarios
- Nome dos arquivos de teste: `test_<modulo_testado>.py`

```
tests/
  unit/
    test_ingest_pdf_use_case.py
    test_search_context_use_case.py
    test_document_chunk_entity.py
  integration/
    test_mock_vector_repository.py
    test_mock_llm_repository.py
    test_pgvector_repository.py      # requer Docker
```

---

## 9. Variaveis de Ambiente

- Carregar com `python-dotenv` no entry-point
- Template em `.env.example` com todas as variaveis necessarias e sem valores reais
- Nunca commitar `.env` com chaves reais
- `.env` esta no `.gitignore`

Variaveis obrigatorias:
```
APP_ENV=development        # development | production
OPENAI_API_KEY=            # chave da OpenAI
GOOGLE_API_KEY=            # chave da Google/Gemini
POSTGRES_CONNECTION_STRING= # string de conexao do PostgreSQL
LLM_PROVIDER=openai        # openai | gemini
```

---

## 10. Estilo de Codigo

- PEP 8 obrigatorio
- Type hints em todas as funcoes e metodos (parametros e retorno)
- F-strings para formatacao de strings (nao `.format()` nem `%`)
- `pathlib.Path` para manipulacao de caminhos de arquivo (nao `os.path`)
- Importacoes organizadas: stdlib -> terceiros -> locais, separados por linha em branco
- Sem `print()` em codigo de producao; usar `logging`

---

## 11. Logging

- Usar `logging` da stdlib; nao usar `print()` em producao
- Configurar no entry-point com nivel adequado (`INFO` por padrao, `DEBUG` para desenvolvimento)
- Formato: `%(asctime)s — %(name)s — %(levelname)s — %(message)s`
- Nunca logar API keys, senhas ou dados sensiveis

---

## 12. Branch Strategy

| Branch | Ambiente | Repositorios |
|--------|---------|-------------|
| `develop` | development | mock (sem banco, sem APIs externas) |
| `homolog` | production | reais (pgVector, OpenAI/Gemini) |
| `main` | production | reais (pgVector, OpenAI/Gemini) |

- `APP_ENV=development` na branch `develop`
- `APP_ENV=production` nas branches `homolog` e `main`
- Push em `homolog` ou `main` dispara GitHub Actions que roda todos os testes antes de fazer merge/deploy
- Se qualquer teste falhar, o pipeline aborta e nao faz deploy
