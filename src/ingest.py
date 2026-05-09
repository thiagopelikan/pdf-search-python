"""Entry-point CLI para ingestion de PDF no banco vetorial.

Execucao: python src/ingest.py [caminho_do_pdf]
Padrao: python src/ingest.py (usa document.pdf na raiz do projeto)
"""

import logging
import os
import sys
import warnings
from pathlib import Path

# Garante que a raiz do projeto esteja no sys.path quando executado diretamente
_project_root = str(Path(__file__).parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

warnings.filterwarnings("ignore", module="urllib3")

from dotenv import load_dotenv

# Carregar variaveis de ambiente do .env antes de qualquer importacao de infraestrutura
load_dotenv()

# Configurar logging antes de importar modulos do projeto
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

from src.infrastructure.config.container import Container


def main() -> None:
    """Executa a ingestion do PDF informado como argumento (ou document.pdf por padrao)."""
    # Determinar caminho do PDF — argumento CLI ou padrao
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Padrao: document.pdf na raiz do projeto
        pdf_path = str(Path(__file__).parent.parent / "document.pdf")

    container = Container()

    print("Limpando base vetorial de todos os providers...")
    container.clear_all_vector_repositories()

    use_case = container.ingest_pdf_use_case()
    total = use_case.execute(pdf_path)
    print(f"Ingestion concluida: {total} chunks armazenados de '{pdf_path}'")


if __name__ == "__main__":
    main()
