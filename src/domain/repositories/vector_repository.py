"""Interface abstrata para repositorio de vetores (embeddings)."""

from abc import ABC, abstractmethod

from src.domain.entities.document_chunk import DocumentChunk


class VectorRepository(ABC):
    """Define o contrato para armazenamento e busca de chunks vetorizados."""

    @abstractmethod
    def store(self, chunks: list[DocumentChunk]) -> int:
        """Armazena os chunks no banco vetorial e retorna a quantidade armazenada."""
        ...

    @abstractmethod
    def search(self, query: str, k: int) -> list[tuple[DocumentChunk, float]]:
        """Busca os k chunks mais similares a query e retorna pares (chunk, score)."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Remove todos os chunks armazenados (util para reingestion e testes)."""
        ...
