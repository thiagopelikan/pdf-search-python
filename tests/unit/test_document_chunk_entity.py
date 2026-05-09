"""Testes unitarios da entidade DocumentChunk."""

import pytest

from src.domain.entities.document_chunk import DocumentChunk


class TestDocumentChunk:
    """Testes para a entidade de dominio DocumentChunk."""

    def test_creates_chunk_with_all_fields(self):
        """Deve criar um chunk com todos os campos corretamente."""
        chunk = DocumentChunk(content="texto do chunk", page=3, source="arquivo.pdf")
        assert chunk.content == "texto do chunk"
        assert chunk.page == 3
        assert chunk.source == "arquivo.pdf"

    def test_equality_by_value(self):
        """Dois chunks com os mesmos valores devem ser iguais (dataclass)."""
        chunk1 = DocumentChunk(content="texto", page=1, source="doc.pdf")
        chunk2 = DocumentChunk(content="texto", page=1, source="doc.pdf")
        assert chunk1 == chunk2

    def test_inequality_on_different_content(self):
        """Chunks com conteudo diferente nao devem ser iguais."""
        chunk1 = DocumentChunk(content="texto A", page=1, source="doc.pdf")
        chunk2 = DocumentChunk(content="texto B", page=1, source="doc.pdf")
        assert chunk1 != chunk2

    def test_accepts_empty_content(self):
        """Deve aceitar content vazio sem lancar excecao."""
        chunk = DocumentChunk(content="", page=1, source="doc.pdf")
        assert chunk.content == ""

    def test_page_is_integer(self):
        """O campo page deve ser um inteiro."""
        chunk = DocumentChunk(content="texto", page=5, source="doc.pdf")
        assert isinstance(chunk.page, int)
