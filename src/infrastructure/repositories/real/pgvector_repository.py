"""Implementacao real do VectorRepository usando PostgreSQL + pgVector via LangChain."""

import logging
import os

from langchain_postgres import PGVector

from src.domain.entities.document_chunk import DocumentChunk
from src.domain.repositories.vector_repository import VectorRepository

logger = logging.getLogger(__name__)

# Nome da colecao no pgVector — identifica o conjunto de embeddings do projeto
COLLECTION_NAME = "pdf_search_chunks"


class PGVectorRepository(VectorRepository):
    """Repositorio vetorial usando PostgreSQL com extensao pgVector.

    Requer APP_ENV=production e POSTGRES_CONNECTION_STRING configurados no .env.
    O embeddings_model e injetado pelo container de DI (OpenAI ou Gemini).
    """

    def __init__(self, embeddings_model) -> None:
        # embeddings_model pode ser OpenAIEmbeddings ou GoogleGenerativeAIEmbeddings
        connection_string = os.environ["POSTGRES_CONNECTION_STRING"]
        self._store = PGVector(
            embeddings=embeddings_model,
            collection_name=COLLECTION_NAME,
            connection=connection_string,
            use_jsonb=True,
        )
        logger.info(f"PGVectorRepository inicializado com colecao '{COLLECTION_NAME}'")

    def store(self, chunks: list[DocumentChunk]) -> int:
        """Converte chunks em documentos LangChain e armazena no pgVector."""
        from langchain_core.documents import Document

        documents = [
            Document(
                page_content=chunk.content,
                metadata={"page": chunk.page, "source": chunk.source},
            )
            for chunk in chunks
        ]
        self._store.add_documents(documents)
        logger.info(f"PGVectorRepository: {len(chunks)} chunks armazenados")
        return len(chunks)

    def search(self, query: str, k: int) -> list[tuple[DocumentChunk, float]]:
        """Busca os k chunks mais similares usando similarity_search_with_score."""
        raw_results = self._store.similarity_search_with_score(query, k=k)
        results = [
            (
                DocumentChunk(
                    content=doc.page_content,
                    page=doc.metadata.get("page", 0),
                    source=doc.metadata.get("source", ""),
                ),
                float(score),
            )
            for doc, score in raw_results
        ]
        logger.info(f"PGVectorRepository: {len(results)} resultados encontrados para query")
        return results

    def clear(self) -> None:
        """Remove todos os documentos da colecao no pgVector."""
        self._store.delete_collection()
        logger.info("PGVectorRepository: colecao removida")
