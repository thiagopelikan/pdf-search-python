"""Container de Dependency Injection — seleciona implementacoes conforme APP_ENV."""

import logging
import os

from src.domain.repositories.llm_repository import LLMRepository
from src.domain.repositories.vector_repository import VectorRepository
from src.domain.use_cases.ingest_pdf import IngestPDF
from src.domain.use_cases.search_context import SearchContext

logger = logging.getLogger(__name__)


def _build_embeddings_model():
    """Instancia o modelo de embeddings conforme o provider configurado."""
    provider = os.environ.get("LLM_PROVIDER", "openai").lower()
    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.environ["OPENAI_API_KEY"],
        )
    elif provider == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.environ["GOOGLE_API_KEY"],
        )
    else:
        raise ValueError(f"LLM_PROVIDER invalido: '{provider}'. Use 'openai' ou 'gemini'.")


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
            embeddings = _build_embeddings_model()
            return PGVectorRepository(embeddings_model=embeddings)
        else:
            from src.infrastructure.repositories.mock.mock_vector_repository import MockVectorRepository
            return MockVectorRepository()

    def llm_repository(self) -> LLMRepository:
        """Retorna a implementacao de LLMRepository para o ambiente atual."""
        if self._env == "production":
            provider = os.environ.get("LLM_PROVIDER", "openai").lower()
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
