"""Entry-point CLI para chat interativo com o conteudo do PDF.

Execucao: python src/chat.py
O usuario digita perguntas e recebe respostas baseadas no PDF ingerido.
Para sair, digitar 'sair' ou pressionar Ctrl+C.
"""

import logging

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
