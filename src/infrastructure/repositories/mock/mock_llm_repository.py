"""Implementacao mock do LLMRepository — respostas fixas para testes sem API key."""

from __future__ import annotations

import logging
from typing import Optional

from src.domain.repositories.llm_repository import LLMRepository

logger = logging.getLogger(__name__)

# Resposta padrao retornada quando o contexto esta vazio
_NO_CONTEXT_RESPONSE = "Nao tenho informacoes necessarias para responder sua pergunta."


class MockLLMRepository(LLMRepository):
    """Repositorio LLM simulado para testes e ambiente de desenvolvimento.

    Retorna uma resposta configuravel sem chamar nenhuma API externa.
    Util para testar o fluxo completo sem necessidade de API keys.
    """

    def __init__(self, fixed_response: Optional[str] = None) -> None:
        # Permite configurar a resposta retornada para testes especificos
        self._fixed_response = fixed_response or _NO_CONTEXT_RESPONSE

    def generate(self, prompt: str) -> str:
        """Retorna a resposta configurada sem chamar API externa."""
        logger.debug(f"MockLLMRepository: gerando resposta para prompt de {len(prompt)} chars")
        return self._fixed_response
