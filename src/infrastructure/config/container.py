"""Container de Dependency Injection — seleciona implementacoes conforme APP_ENV."""

import logging
import os

from src.domain.repositories.llm_repository import LLMRepository
from src.domain.repositories.vector_repository import VectorRepository
from src.domain.use_cases.ingest_pdf import IngestPDF
from src.domain.use_cases.search_context import SearchContext

logger = logging.getLogger(__name__)


_COLLECTION_NAMES = {
    "openai": "pdf_search_chunks_openai",
    "gemini": "pdf_search_chunks_gemini",
}


def _get_provider() -> str:
    provider = os.environ.get("LLM_PROVIDER", "openai").lower()
    if provider not in _COLLECTION_NAMES:
        raise ValueError(f"LLM_PROVIDER invalido: '{provider}'. Use 'openai' ou 'gemini'.")
    return provider


def _build_embeddings_model(provider: str):
    """Instancia o modelo de embeddings conforme o provider configurado."""
    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model=os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            api_key=os.environ["OPENAI_API_KEY"],
        )
    else:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            model=os.environ.get("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001"),
            google_api_key=os.environ["GOOGLE_API_KEY"],
        )


class Container:
    """Factory que resolve dependencias conforme APP_ENV.

    APP_ENV=development -> repositorios mock (sem banco, sem APIs)
    APP_ENV=production  -> repositorios reais (pgVector + OpenAI/Gemini)
    """

    def __init__(self) -> None:
        self._env = os.environ.get("APP_ENV", "development").lower()
        logger.info(f"Container inicializado com APP_ENV={self._env}")

    def vector_repository(self) -> VectorRepository:
        """Retorna a implementacao de VectorRepository para o ambiente atual."""
        if self._env == "production":
            from src.infrastructure.repositories.real.pgvector_repository import PGVectorRepository
            provider = _get_provider()
            embeddings = _build_embeddings_model(provider)
            collection_name = _COLLECTION_NAMES[provider]
            return PGVectorRepository(embeddings_model=embeddings, collection_name=collection_name)
        else:
            from src.infrastructure.repositories.mock.mock_vector_repository import MockVectorRepository
            return MockVectorRepository()

    def llm_repository(self) -> LLMRepository:
        """Retorna a implementacao de LLMRepository para o ambiente atual."""
        if self._env == "production":
            provider = _get_provider()
            if provider == "openai":
                from src.infrastructure.repositories.real.openai_llm_repository import OpenAILLMRepository
                return OpenAILLMRepository()
            else:
                from src.infrastructure.repositories.real.gemini_llm_repository import GeminiLLMRepository
                return GeminiLLMRepository()
        else:
            from src.infrastructure.repositories.mock.mock_llm_repository import MockLLMRepository
            return MockLLMRepository()

    def ingest_pdf_use_case(self) -> IngestPDF:
        """Monta e retorna o use case de ingestion com as dependencias corretas."""
        return IngestPDF(vector_repository=self.vector_repository())

    def search_context_use_case(self) -> SearchContext:
        """Monta e retorna o use case de busca com as dependencias corretas."""
        return SearchContext(
            vector_repository=self.vector_repository(),
            llm_repository=self.llm_repository(),
        )
