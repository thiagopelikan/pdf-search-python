"""Interface abstrata para repositorio de LLM (geracao de respostas)."""

from abc import ABC, abstractmethod


class LLMRepository(ABC):
    """Define o contrato para geracao de respostas baseadas em contexto."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Envia o prompt ao LLM e retorna a resposta gerada."""
        ...
