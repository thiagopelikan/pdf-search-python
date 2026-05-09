"""Testes de integracao do MockVectorRepository."""

import pytest

from src.domain.entities.document_chunk import DocumentChunk
from src.infrastructure.repositories.mock.mock_vector_repository import MockVectorRepository


def _make_chunk(content: str, page: int = 1) -> DocumentChunk:
    """Helper para criar DocumentChunk de teste."""
    return DocumentChunk(content=content, page=page, source="test.pdf")


class TestMockVectorRepository:
    """Testes para a implementacao mock do VectorRepository."""

    def setup_method(self):
        """Cria um repositorio limpo antes de cada teste."""
        self.repo = MockVectorRepository()

    def test_store_returns_count_of_stored_chunks(self):
        """Deve retornar o numero de chunks armazenados."""
        chunks = [_make_chunk("texto 1"), _make_chunk("texto 2")]
        result = self.repo.store(chunks)
        assert result == 2

    def test_store_empty_list_returns_zero(self):
        """Deve retornar 0 ao armazenar lista vazia."""
        result = self.repo.store([])
        assert result == 0

    def test_search_returns_empty_when_no_chunks_stored(self):
        """Deve retornar lista vazia quando nao ha chunks armazenados."""
        results = self.repo.search("alguma pergunta", k=10)
        assert results == []

    def test_search_returns_at_most_k_results(self):
        """Deve retornar no maximo k resultados."""
        chunks = [_make_chunk(f"chunk numero {i}") for i in range(20)]
        self.repo.store(chunks)
        results = self.repo.search("chunk numero", k=5)
        assert len(results) <= 5

    def test_search_returns_tuples_of_chunk_and_float(self):
        """Cada resultado deve ser uma tupla (DocumentChunk, float)."""
        self.repo.store([_make_chunk("texto relevante")])
        results = self.repo.search("texto", k=10)
        assert len(results) > 0
        for item in results:
            assert len(item) == 2
            chunk, score = item
            assert isinstance(chunk, DocumentChunk)
            assert isinstance(score, float)

    def test_search_ranks_relevant_chunk_higher(self):
        """Chunk com maior sobreposicao de palavras deve ter maior score."""
        relevant = _make_chunk("faturamento empresa SuperTechIABrazil dez milhoes")
        irrelevant = _make_chunk("clima previsao temperatura umidade pressao")
        self.repo.store([irrelevant, relevant])

        results = self.repo.search("faturamento empresa", k=10)
        assert len(results) >= 2
        # O chunk relevante deve ter score maior
        top_chunk, top_score = results[0]
        assert top_chunk.content == relevant.content

    def test_clear_removes_all_chunks(self):
        """Apos clear(), busca deve retornar lista vazia."""
        self.repo.store([_make_chunk("texto qualquer")])
        self.repo.clear()
        results = self.repo.search("texto", k=10)
        assert results == []

    def test_accumulates_chunks_across_multiple_stores(self):
        """Multiplas chamadas a store() devem acumular os chunks."""
        self.repo.store([_make_chunk("primeiro batch")])
        self.repo.store([_make_chunk("segundo batch")])
        results = self.repo.search("batch", k=10)
        assert len(results) == 2
