"""Entry-point CLI para realizar uma busca semantica avulsa (sem loop de chat).

Execucao: python src/search.py "Qual o faturamento da empresa?"
"""

import logging
import sys
import warnings
from pathlib import Path

# Garante que a raiz do projeto esteja no sys.path quando executado diretamente
_project_root = str(Path(__file__).parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

warnings.filterwarnings("ignore", module="urllib3")

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

from src.infrastructure.config.container import Container


def main() -> None:
    """Executa uma busca semantica para a pergunta passada como argumento."""
    if len(sys.argv) < 2:
        print("Uso: python src/search.py \"sua pergunta aqui\"")
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    container = Container()
    use_case = container.search_context_use_case()

    response = use_case.execute(question)
    print(f"\nPERGUNTA: {question}")
    print(f"RESPOSTA: {response}\n")


if __name__ == "__main__":
    main()
