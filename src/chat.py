"""Entry-point CLI para chat interativo com o conteudo do PDF.

Execucao: python -m src.chat  (da raiz do projeto)
O usuario digita perguntas e recebe respostas baseadas no PDF ingerido.
Para sair, digitar 'sair' ou pressionar Ctrl+C.
"""

import logging
import sys
import warnings
from pathlib import Path

# Garante que a raiz do projeto esteja no sys.path quando executado diretamente
_project_root = str(Path(__file__).parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

warnings.filterwarnings("ignore", category=Warning, module="urllib3")

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.WARNING,  # Reduzir verbosidade no modo chat para melhor UX
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

from src.infrastructure.config.container import Container


def main() -> None:
    """Loop principal do chat interativo."""
    container = Container()
    use_case = container.search_context_use_case()

    print("Chat iniciado. Digite 'sair' para encerrar.\n")

    while True:
        try:
            question = input("PERGUNTA: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nChat encerrado.")
            break

        if not question:
            continue

        if question.lower() in {"sair", "exit", "quit"}:
            print("Chat encerrado.")
            break

        response = use_case.execute(question)
        print(f"RESPOSTA: {response}\n")


if __name__ == "__main__":
    main()
