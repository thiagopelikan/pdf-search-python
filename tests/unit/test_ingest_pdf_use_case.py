"""Testes unitarios do use case IngestPDF."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.domain.entities.document_chunk import DocumentChunk
from src.domain.use_cases.ingest_pdf import IngestPDF


class TestIngestPDF:
    """Testes para o use case IngestPDF."""

    def _make_use_case(self, stored_count: int = 3):
        """Cria um IngestPDF com repositorio mock configurado."""
        mock_repo = MagicMock()
        mock_repo.store.return_value = stored_count
        return IngestPDF(vector_repository=mock_repo), mock_repo

    def test_raises_file_not_found_for_missing_pdf(self):
        """Deve lancar FileNotFoundError quando o PDF nao existe."""
        use_case, _ = self._make_use_case()
        with pytest.raises(FileNotFoundError, match="PDF nao encontrado"):
            use_case.execute("/caminho/inexistente/arquivo.pdf")

    @patch("langchain_community.document_loaders.PyPDFLoader")
    @patch("langchain_text_splitters.RecursiveCharacterTextSplitter")
    def test_returns_stored_count(self, mock_splitter_cls, mock_loader_cls, tmp_path):
        """Deve retornar o numero de chunks armazenados pelo repositorio."""
        # Criar PDF temporario para satisfazer a verificacao de existencia
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 fake content")

        # Configurar mocks da cadeia LangChain
        mock_doc = MagicMock()
        mock_doc.page_content = "conteudo de teste"
        mock_doc.metadata = {"page": 0}

        mock_loader = MagicMock()
        mock_loader.load.return_value = [mock_doc]
        mock_loader_cls.return_value = mock_loader

        mock_splitter = MagicMock()
        mock_splitter.split_documents.return_value = [mock_doc, mock_doc]
        mock_splitter_cls.return_value = mock_splitter

        use_case, mock_repo = self._make_use_case(stored_count=2)
        result = use_case.execute(str(pdf_file))

        assert result == 2

    @patch("langchain_community.document_loaders.PyPDFLoader")
    @patch("langchain_text_splitters.RecursiveCharacterTextSplitter")
    def test_calls_store_with_document_chunks(self, mock_splitter_cls, mock_loader_cls, tmp_path):
        """Deve chamar store() com instancias de DocumentChunk."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 fake content")

        mock_doc = MagicMock()
        mock_doc.page_content = "texto do chunk"
        mock_doc.metadata = {"page": 1}

        mock_loader = MagicMock()
        mock_loader.load.return_value = [mock_doc]
        mock_loader_cls.return_value = mock_loader

        mock_splitter = MagicMock()
        mock_splitter.split_documents.return_value = [mock_doc]
        mock_splitter_cls.return_value = mock_splitter

        use_case, mock_repo = self._make_use_case(stored_count=1)
        use_case.execute(str(pdf_file))

        # Verificar que store foi chamado com uma lista de DocumentChunk
        mock_repo.store.assert_called_once()
        chunks_arg = mock_repo.store.call_args[0][0]
        assert len(chunks_arg) == 1
        assert isinstance(chunks_arg[0], DocumentChunk)
        assert chunks_arg[0].content == "texto do chunk"

    @patch("langchain_community.document_loaders.PyPDFLoader")
    @patch("langchain_text_splitters.RecursiveCharacterTextSplitter")
    def test_uses_correct_chunk_parameters(self, mock_splitter_cls, mock_loader_cls, tmp_path):
        """Deve usar chunk_size=1000 e chunk_overlap=150 conforme o enunciado."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 fake content")

        mock_loader = MagicMock()
        mock_loader.load.return_value = []
        mock_loader_cls.return_value = mock_loader

        mock_splitter = MagicMock()
        mock_splitter.split_documents.return_value = []
        mock_splitter_cls.return_value = mock_splitter

        use_case, _ = self._make_use_case(stored_count=0)
        use_case.execute(str(pdf_file))

        # Verificar parametros do splitter
        mock_splitter_cls.assert_called_once_with(chunk_size=1000, chunk_overlap=150)
