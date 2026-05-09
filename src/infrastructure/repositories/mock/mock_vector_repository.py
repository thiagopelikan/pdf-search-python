"""Implementacao mock do VectorRepository — armazenamento em memoria, sem dependencias externas."""

import logging
import math

from src.domain.entities.document_chunk import DocumentChunk
from src.domain.repositories.vector_repository import VectorRepository

logger = logging.getLogger(__name__)


class MockVectorRepository(VectorRepository):
    """Repositorio vetorial em memoria para testes e ambiente de desenvolvimento.

    Calcula similaridade por sobreposicao de palavras em vez de embeddings reais.
    Nao requer banco de dados, Docker ou API keys.
    """

    def __init__(self) -> None:
        # Armazenamento em lista simples (suficiente para testes)
        self._chunks: list[DocumentChunk] = []

    def store(self, chunks: list[DocumentChunk]) -> int:
        """Armazena os chunks em memoria e retorna a quantidade armazenada."""
        self._chunks.extend(chunks)
        logger.debug(f"MockVectorRepository: {len(chunks)} chunks armazenados (total: {len(self._chunks)})")
        return len(chunks)

    def search(self, query: str, k: int) -> list[tuple[DocumentChunk, float]]:
        """Retorna os k chunks com maior sobreposicao de palavras com a query."""
        if not self._chunks:
            return []

        query_words = set(query.lower().split())

        # Calcular score de sobreposicao simples (nao e cosine similarity, mas serve para testes)
        scored = [
            (chunk, self._overlap_score(query_words, chunk.content))
            for chunk in self._chunks
        ]

        # Ordenar por score decrescente e retornar os k primeiros
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:k]

    def clear(self) -> None:
        """Remove todos os chunks em memoria."""
        self._chunks.clear()
        logger.debug("MockVectorRepository: todos os chunks removidos")

    def _overlap_score(self, query_words: set[str], content: str) -> float:
        """Calcula score de sobreposicao de palavras entre query e conteudo."""
        content_words = set(content.lower().split())
        if not content_words:
            return 0.0
        intersection = query_words & content_words
        # Jaccard similarity: intersecao / uniao
        union = query_words | content_words
        return len(intersection) / len(union) if union else 0.0
