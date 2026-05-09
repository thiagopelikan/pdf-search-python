"""Implementacao real do LLMRepository usando OpenAI (gpt-5-nano)."""

import logging
import os

from langchain_openai import ChatOpenAI

from src.domain.repositories.llm_repository import LLMRepository

logger = logging.getLogger(__name__)

# Modelo fixado pelo enunciado (docs/requirements.txt)
OPENAI_LLM_MODEL = "gpt-5-nano"


class OpenAILLMRepository(LLMRepository):
    """Repositorio LLM usando a API da OpenAI.

    Requer OPENAI_API_KEY configurada no .env.
    """

    def __init__(self) -> None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY nao configurada no ambiente")
        self._llm = ChatOpenAI(model=OPENAI_LLM_MODEL, api_key=api_key)
        logger.info(f"OpenAILLMRepository inicializado com modelo {OPENAI_LLM_MODEL}")

    def generate(self, prompt: str) -> str:
        """Envia o prompt ao modelo OpenAI e retorna o texto da resposta."""
        response = self._llm.invoke(prompt)
        return response.content
