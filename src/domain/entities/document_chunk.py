"""Entidade de dominio representando um fragmento de documento PDF."""

from dataclasses import dataclass


@dataclass
class DocumentChunk:
    """Fragmento de texto extraido de um PDF com metadados de origem."""

    content: str
    # Pagina de origem dentro do PDF (base 1)
    page: int
    # Caminho do arquivo PDF de origem
    source: str
