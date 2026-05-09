"""Caso de uso responsavel pela busca semantica e geracao de resposta."""

import logging
import os
from pathlib import Path

from src.domain.repositories.llm_repository import LLMRepository
from src.domain.repositories.vector_repository import VectorRepository

logger = logging.getLogger(__name__)

SEARCH_K = int(os.environ.get("SEARCH_K", "10"))

# Caminho do template de prompt (relativo a raiz do projeto)
_PROMPT_FILE = Path(__file__).parent.parent.parent.parent / "prompts" / "search_prompt.txt"


def _load_prompt_template() -> str:
    """Carrega o template de prompt do arquivo externo."""
    return _PROMPT_FILE.read_text(encoding="utf-8")


class SearchContext:
    """Vetoriza a pergunta, busca contexto relevante e gera resposta via LLM."""

    def __init__(
        self,
        vector_repository: VectorRepository,
        llm_repository: LLMRepository,
    ) -> None:
        self._vector_repository = vector_repository
        self._llm_repository = llm_repository
        # Carrega o template uma vez na inicializacao para evitar I/O repetido
        self._prompt_template = _load_prompt_template()

    def execute(self, question: str) -> str:
        """Executa a busca semantica e retorna a resposta gerada pelo LLM."""
        if not question.strip():
            raise ValueError("A pergunta nao pode ser vazia")

        logger.info(f"Buscando contexto para: {question[:80]}...")

        # Buscar os k chunks mais similares a pergunta
        results = self._vector_repository.search(question, k=SEARCH_K)
        logger.info(f"Encontrados {len(results)} resultados")

        # Concatenar o conteudo dos chunks como contexto para o LLM
        context = "\n\n".join(chunk.content for chunk, _score in results)

        # Montar o prompt substituindo as variaveis do template
        prompt = self._prompt_template.format(context=context, question=question)

        # Gerar resposta via LLM
        response = self._llm_repository.generate(prompt)
        logger.info("Resposta gerada com sucesso")

        return response
