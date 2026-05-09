# Backlog — pdf-search-python

Todas as features derivadas de `docs/requirements.txt`. Marque o checkbox e registre a data ao implementar cada item.

| Status | Feature | Data |
|--------|---------|------|
| **Infraestrutura** | | |
| [x] | Docker Compose (PostgreSQL + pgVector) | 2026-05-09 |
| [x] | Virtual environment + requirements.txt (dependencias Python) | 2026-05-09 |
| [x] | .env.example com variaveis OPENAI_API_KEY e GOOGLE_API_KEY | 2026-05-09 |
| **Arquitetura Clean** | | |
| [x] | Estrutura de diretorios (domain / infrastructure / src entry-points) | 2026-05-09 |
| [x] | Interface abstrata VectorRepository em `src/domain/repositories/vector_repository.py` | 2026-05-09 |
| [x] | Interface abstrata LLMRepository em `src/domain/repositories/llm_repository.py` | 2026-05-09 |
| [x] | Entidade DocumentChunk em `src/domain/entities/document_chunk.py` | 2026-05-09 |
| [x] | Use case IngestPDF em `src/domain/use_cases/ingest_pdf.py` | 2026-05-09 |
| [x] | Use case SearchContext em `src/domain/use_cases/search_context.py` | 2026-05-09 |
| [x] | Implementacao mock VectorRepository em `src/infrastructure/repositories/mock/` | 2026-05-09 |
| [x] | Implementacao mock LLMRepository em `src/infrastructure/repositories/mock/` | 2026-05-09 |
| [x] | Implementacao real pgVector em `src/infrastructure/repositories/real/pgvector_repository.py` | 2026-05-09 |
| [x] | Implementacao real OpenAI LLM em `src/infrastructure/repositories/real/openai_llm_repository.py` | 2026-05-09 |
| [x] | Implementacao real Gemini LLM em `src/infrastructure/repositories/real/gemini_llm_repository.py` | 2026-05-09 |
| [x] | Container de DI em `src/infrastructure/config/container.py` | 2026-05-09 |
| **Features Principais** | | |
| [x] | Ingestion de PDF — chunking 1000 chars / overlap 150 | 2026-05-09 |
| [x] | Geracao de embeddings OpenAI (text-embedding-3-small) | 2026-05-09 |
| [x] | Geracao de embeddings Gemini (models/gemini-embedding-001) | 2026-05-09 |
| [x] | Armazenamento vetorial no pgVector | 2026-05-09 |
| [x] | Busca semantica k=10 via similarity_search_with_score | 2026-05-09 |
| [x] | CLI de chat interativo (`src/chat.py`) | 2026-05-09 |
| [x] | Resposta contextual via LLM (gpt-5-nano / gemini-2.5-flash-lite) | 2026-05-09 |
| [x] | Recusa de perguntas fora do contexto | 2026-05-09 |
| **Prompts** | | |
| [x] | Arquivo `prompts/search_prompt.txt` com template exato do enunciado | 2026-05-09 |
| **Testes** | | |
| [x] | Testes unitarios do use case IngestPDF | 2026-05-09 |
| [x] | Testes unitarios do use case SearchContext | 2026-05-09 |
| [x] | Testes unitarios das entidades de dominio | 2026-05-09 |
| [x] | Testes de integracao dos repositorios mock | 2026-05-09 |
| [x] | Testes de integracao end-to-end (banco real via docker-compose) | 2026-05-09 |
| **CI/CD** | | |
| [x] | GitHub Actions — workflow ci-homolog.yml (tests + deploy) | 2026-05-09 |
| [x] | GitHub Actions — workflow ci-main.yml (tests + deploy) | 2026-05-09 |
| [x] | Branch develop criada no remote | 2026-05-09 |
| [x] | Branch homolog criada no remote | 2026-05-09 |
| [x] | Branch main configurada no remote | 2026-05-09 |
| [x] | Documentacao de branch strategy no README | 2026-05-09 |
| **Documentacao** | | |
| [x] | README.md com instrucoes de execucao | 2026-05-09 |
| [x] | GUIDELINES.md com boas praticas Python | 2026-05-09 |
| **Subagentes Claude** | | |
| [x] | `.claude/agents/developer.md` | 2026-05-09 |
| [x] | `.claude/agents/cicd.md` | 2026-05-09 |
| [x] | `.claude/agents/quality.md` | 2026-05-09 |
| [x] | `.claude/agents/techlead.md` | 2026-05-09 |

---

## Sequencia de Implementacao Recomendada

1. Scaffolding — backlog, guidelines, subagentes, estrutura de diretorios
2. Infraestrutura — docker-compose, .env.example, requirements.txt
3. Dominio — entidades, interfaces de repositorio, use cases
4. Implementacoes mock — todos os repositorios
5. Testes unitarios e de integracao (com mocks)
6. Implementacoes reais — pgVector, OpenAI, Gemini
7. Entry-points CLI — ingest.py, search.py, chat.py
8. CI/CD — GitHub Actions, configuracao de branches
9. Testes de integracao end-to-end
10. README final + revisao completa
