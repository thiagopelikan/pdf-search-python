"""Implementacao real do LLMRepository usando Google Gemini."""

import logging
import os

from langchain_google_genai import ChatGoogleGenerativeAI

from src.domain.repositories.llm_repository import LLMRepository

logger = logging.getLogger(__name__)

GEMINI_LLM_MODEL = os.environ.get("GEMINI_LLM_MODEL", "gemini-2.5-flash-lite")


class GeminiLLMRepository(LLMRepository):
    """Repositorio LLM usando a API do Google Gemini.

    Requer GOOGLE_API_KEY configurada no .env.
    """

    def __init__(self) -> None:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError("GOOGLE_API_KEY nao configurada no ambiente")
        self._llm = ChatGoogleGenerativeAI(model=GEMINI_LLM_MODEL, google_api_key=api_key)
        logger.info(f"GeminiLLMRepository inicializado com modelo {GEMINI_LLM_MODEL}")

    def generate(self, prompt: str) -> str:
        """Envia o prompt ao modelo Gemini e retorna o texto da resposta."""
        response = self._llm.invoke(prompt)
        return response.content
