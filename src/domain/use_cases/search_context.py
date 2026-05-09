"""Caso de uso responsavel pela busca semantica e geracao de resposta."""

import logging
import os
from pathlib import Path

from src.domain.repositories.llm_repository import LLMRepository
from src.domain.repositories.vector_repository import VectorRepository

logger = logging.getLogger(__name__)

SEARCH_K = int(os.environ.get("SEARCH_K", "10"))
SEARCH_MIN_SCORE = float(os.environ.get("SEARCH_MIN_SCORE", "0.5"))

_NO_CONTEXT_RESPONSE = "Nao tenho informacoes necessarias para responder sua pergunta."

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
        raw_results = self._vector_repository.search(question, k=SEARCH_K)
        logger.info(f"Encontrados {len(raw_results)} resultados brutos")

        for i, (chunk, score) in enumerate(raw_results):
            logger.info(
                f"  chunk[{i}] score={score:.4f} page={chunk.page} "
                f"preview={chunk.content[:80].replace(chr(10), ' ')!r}"
            )

        # Filtrar chunks abaixo do limiar de similaridade para evitar contexto irrelevante
        results = [(chunk, score) for chunk, score in raw_results if score >= SEARCH_MIN_SCORE]
        logger.info(
            f"{len(results)}/{len(raw_results)} chunks passaram no filtro "
            f"(min_score={SEARCH_MIN_SCORE})"
        )

        # Se nenhum chunk for suficientemente relevante, responde sem chamar o LLM
        if not results:
            logger.info("Nenhum chunk relevante encontrado; retornando resposta padrao")
            return _NO_CONTEXT_RESPONSE

        # Concatenar o conteudo dos chunks como contexto para o LLM
        context = "\n\n".join(chunk.content for chunk, _score in results)

        # Montar o prompt substituindo as variaveis do template
        prompt = self._prompt_template.format(context=context, question=question)

        # Gerar resposta via LLM
        response = self._llm_repository.generate(prompt)
        logger.info("Resposta gerada com sucesso")

        return response
