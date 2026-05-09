"""Implementacao real do VectorRepository usando PostgreSQL + pgVector via LangChain."""

import logging
import os
import time

from langchain_postgres import PGVector

from src.domain.entities.document_chunk import DocumentChunk
from src.domain.repositories.vector_repository import VectorRepository

logger = logging.getLogger(__name__)

COLLECTION_BASE = "pdf_search_chunks"


class PGVectorRepository(VectorRepository):
    """Repositorio vetorial usando PostgreSQL com extensao pgVector.

    Requer APP_ENV=production e POSTGRES_CONNECTION_STRING configurados no .env.
    O embeddings_model e injetado pelo container de DI (OpenAI ou Gemini).
    Cada provider usa sua propria colecao para evitar mistura de dimensoes de vetores.
    """

    def __init__(self, embeddings_model, collection_name: str) -> None:
        connection_string = os.environ["POSTGRES_CONNECTION_STRING"]
        self._store = PGVector(
            embeddings=embeddings_model,
            collection_name=collection_name,
            connection=connection_string,
            use_jsonb=True,
        )
        logger.info(f"PGVectorRepository inicializado com colecao '{collection_name}'")

    _BATCH_SIZE = 10

    def _add_batch_with_retry(self, batch: list, batch_num: int, total_batches: int) -> None:
        import re
        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            try:
                self._store.add_documents(batch)
                return
            except Exception as exc:
                msg = str(exc)
                match = re.search(r"retry in (\d+)", msg, re.IGNORECASE)
                wait = int(match.group(1)) + 2 if match else 65
                if attempt < max_attempts and ("429" in msg or "quota" in msg.lower() or "exhausted" in msg.lower()):
                    logger.warning(f"Rate limit no batch {batch_num}/{total_batches}, aguardando {wait}s (tentativa {attempt}/{max_attempts})")
                    time.sleep(wait)
                else:
                    raise

    def store(self, chunks: list[DocumentChunk]) -> int:
        """Converte chunks em documentos LangChain e armazena no pgVector em batches com retry."""
        from langchain_core.documents import Document

        documents = [
            Document(
                page_content=chunk.content,
                metadata={"page": chunk.page, "source": chunk.source},
            )
            for chunk in chunks
        ]
        total_batches = (len(documents) + self._BATCH_SIZE - 1) // self._BATCH_SIZE
        total = 0
        for i in range(0, len(documents), self._BATCH_SIZE):
            batch = documents[i : i + self._BATCH_SIZE]
            batch_num = i // self._BATCH_SIZE + 1
            self._add_batch_with_retry(batch, batch_num, total_batches)
            total += len(batch)
            logger.info(f"PGVectorRepository: batch {batch_num}/{total_batches} — {total}/{len(documents)} chunks armazenados")
            if i + self._BATCH_SIZE < len(documents):
                time.sleep(1)
        return total

    def search(self, query: str, k: int) -> list[tuple[DocumentChunk, float]]:
        """Busca os k chunks mais similares usando similarity_search_with_score.

        O score retornado e cosine similarity normalizado para [0, 1] (1 = identico),
        convertido a partir da cosine distance retornada pelo pgVector (distance = 1 - similarity).
        """
        raw_results = self._store.similarity_search_with_score(query, k=k)
        results = [
            (
                DocumentChunk(
                    content=doc.page_content,
                    page=doc.metadata.get("page", 0),
                    source=doc.metadata.get("source", ""),
                ),
                # pgVector retorna cosine distance (0=identico, 2=oposto); converte para similarity
                max(0.0, 1.0 - float(score)),
            )
            for doc, score in raw_results
        ]
        logger.info(f"PGVectorRepository: {len(results)} resultados encontrados para query")
        return results

    def clear(self) -> None:
        """Remove todos os documentos da colecao no pgVector."""
        self._store.delete_collection()
        logger.info("PGVectorRepository: colecao removida")
