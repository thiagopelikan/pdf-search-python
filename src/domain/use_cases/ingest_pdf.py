"""Caso de uso responsavel pela ingestion de um PDF no banco vetorial."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from src.domain.entities.document_chunk import DocumentChunk
from src.domain.repositories.vector_repository import VectorRepository

logger = logging.getLogger(__name__)

CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "150"))


class IngestPDF:
    """Le um PDF, divide em chunks e armazena os vetores no repositorio."""

    def __init__(self, vector_repository: VectorRepository) -> None:
        self._vector_repository = vector_repository

    def execute(self, pdf_path: str) -> int:
        """Executa a ingestion completa do PDF e retorna o numero de chunks armazenados."""
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF nao encontrado: {pdf_path}")

        logger.info(f"Iniciando ingestion de {pdf_path}")

        # Imports lazy para evitar dependencia de langchain em tempo de coleta de testes
        from langchain_community.document_loaders import PyPDFLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        # Carregar paginas do PDF
        loader = PyPDFLoader(str(path))
        pages = loader.load()
        logger.info(f"PDF carregado: {len(pages)} paginas")

        # Dividir em chunks conforme parametros do enunciado
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        raw_chunks = splitter.split_documents(pages)
        logger.info(f"Texto dividido em {len(raw_chunks)} chunks")

        # Converter para entidades de dominio
        chunks = [
            DocumentChunk(
                content=doc.page_content,
                page=doc.metadata.get("page", 0) + 1,  # PyPDFLoader usa base 0
                source=str(path),
            )
            for doc in raw_chunks
        ]

        # Armazenar no repositorio vetorial
        stored = self._vector_repository.store(chunks)
        logger.info(f"Ingestion concluida: {stored} chunks armazenados")

        return stored
