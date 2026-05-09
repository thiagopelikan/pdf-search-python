"""Entry-point CLI para realizar uma busca semantica avulsa (sem loop de chat).

Execucao: python src/search.py "Qual o faturamento da empresa?"
"""

import logging
import sys

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
