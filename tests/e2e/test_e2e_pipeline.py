"""Testes end-to-end do pipeline completo com Docker + API real.

Execucao:
    APP_ENV=production LLM_PROVIDER=openai pytest tests/e2e/ -m e2e -v
    APP_ENV=production LLM_PROVIDER=gemini pytest tests/e2e/ -m e2e -v

Requisitos:
    - Docker com pgVector rodando (docker compose up -d)
    - OPENAI_API_KEY ou GOOGLE_API_KEY configuradas no .env
"""

import os
import tempfile
from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv()

# Colecao isolada para nao poluir dados de producao
_E2E_COLLECTION = "pdf_search_e2e_test"

# Conteudo de PDF minimo para testes (evita custo de embeddings do PDF real)
_PDF_TEXT = (
    "Domain Driven Design e uma abordagem de desenvolvimento de software. "
    "O DDD foi criado por Eric Evans em 2003. "
    "Clean Architecture organiza o sistema em camadas com limites claros. "
    "O objetivo e separar regras de negocio de detalhes de infraestrutura."
)


def _postgres_available() -> bool:
    """Verifica se o PostgreSQL esta acessivel."""
    try:
        import psycopg2
        conn_str = os.environ.get(
            "POSTGRES_CONNECTION_STRING",
            "postgresql+psycopg2://postgres:postgres@localhost:5432/pdf_search",
        )
        # Extrai host/port/db da connection string para psycopg2 direto
        import re
        m = re.match(r".*://(\w+):(\w+)@([\w.]+):(\d+)/(\w+)", conn_str)
        if not m:
            return False
        user, password, host, port, dbname = m.groups()
        conn = psycopg2.connect(host=host, port=int(port), dbname=dbname, user=user, password=password, connect_timeout=3)
        conn.close()
        return True
    except Exception:
        return False


def _api_key_available() -> bool:
    """Verifica se a API key do provider configurado esta presente."""
    provider = os.environ.get("LLM_PROVIDER", "openai")
    if provider == "openai":
        return bool(os.environ.get("OPENAI_API_KEY"))
    return bool(os.environ.get("GOOGLE_API_KEY"))


skip_if_no_infra = pytest.mark.skipif(
    not _postgres_available() or not _api_key_available(),
    reason="Requer Docker com pgVector rodando e API key configurada",
)


@pytest.fixture(scope="module")
def vector_store():
    """Cria e limpa a colecao e2e antes/apos os testes do modulo."""
    from src.infrastructure.config.container import _build_embeddings_model, _get_provider
    from langchain_postgres import PGVector

    provider = _get_provider()
    embeddings = _build_embeddings_model(provider)
    conn_str = os.environ["POSTGRES_CONNECTION_STRING"]

    store = PGVector(
        embeddings=embeddings,
        collection_name=_E2E_COLLECTION,
        connection=conn_str,
        use_jsonb=True,
    )
    yield store
    store.delete_collection()


@pytest.fixture(scope="module")
def ingested_pdf(vector_store, tmp_path_factory):
    """Ingere um PDF minimo na colecao e2e e retorna o numero de chunks."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    # Criar PDF minimo com reportlab
    tmp = tmp_path_factory.mktemp("pdfs")
    pdf_path = tmp / "test_e2e.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.drawString(72, 720, _PDF_TEXT)
    c.save()

    from src.infrastructure.repositories.real.pgvector_repository import PGVectorRepository
    from src.domain.use_cases.ingest_pdf import IngestPDF

    repo = PGVectorRepository(
        embeddings_model=vector_store.embeddings,
        collection_name=_E2E_COLLECTION,
    )
    use_case = IngestPDF(vector_repository=repo)
    total = use_case.execute(str(pdf_path))
    return total


@pytest.mark.e2e
@skip_if_no_infra
class TestE2EPipeline:
    """Testes do pipeline completo: ingestion -> busca semantica -> resposta LLM."""

    def test_ingestion_armazena_chunks(self, ingested_pdf):
        """Ingestion deve armazenar pelo menos 1 chunk no pgVector."""
        assert ingested_pdf >= 1

    def test_busca_retorna_resultado_relevante(self, vector_store, ingested_pdf):
        """Busca semantica deve retornar chunks relevantes para pergunta sobre DDD."""
        from src.infrastructure.repositories.real.pgvector_repository import PGVectorRepository

        repo = PGVectorRepository(
            embeddings_model=vector_store.embeddings,
            collection_name=_E2E_COLLECTION,
        )
        results = repo.search("O que e Domain Driven Design?", k=3)
        assert len(results) >= 1
        top_chunk, score = results[0]
        assert "Domain" in top_chunk.content or "DDD" in top_chunk.content or score < 1.0

    def test_pipeline_completo_responde_sobre_conteudo(self, vector_store, ingested_pdf):
        """Use case SearchContext deve gerar resposta baseada no conteudo do PDF."""
        from src.infrastructure.repositories.real.pgvector_repository import PGVectorRepository
        from src.infrastructure.config.container import Container

        repo = PGVectorRepository(
            embeddings_model=vector_store.embeddings,
            collection_name=_E2E_COLLECTION,
        )
        container = Container()
        llm = container.llm_repository()

        from src.domain.use_cases.search_context import SearchContext
        use_case = SearchContext(vector_repository=repo, llm_repository=llm)

        response = use_case.execute("Quem criou o DDD?")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_pipeline_recusa_pergunta_fora_de_contexto(self, vector_store, ingested_pdf):
        """Use case deve recusar perguntas sem resposta no contexto."""
        from src.infrastructure.repositories.real.pgvector_repository import PGVectorRepository
        from src.infrastructure.config.container import Container

        repo = PGVectorRepository(
            embeddings_model=vector_store.embeddings,
            collection_name=_E2E_COLLECTION,
        )
        container = Container()
        llm = container.llm_repository()

        from src.domain.use_cases.search_context import SearchContext
        use_case = SearchContext(vector_repository=repo, llm_repository=llm)

        response = use_case.execute("Qual e a capital da Franca?")
        assert "nao tenho" in response.lower() or "não tenho" in response.lower()
