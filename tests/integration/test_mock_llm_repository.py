"""Testes de integracao do MockLLMRepository."""

import pytest

from src.infrastructure.repositories.mock.mock_llm_repository import MockLLMRepository


class TestMockLLMRepository:
    """Testes para a implementacao mock do LLMRepository."""

    def test_generate_returns_fixed_response(self):
        """Deve retornar a resposta configurada para qualquer prompt."""
        repo = MockLLMRepository(fixed_response="resposta de teste")
        result = repo.generate("qualquer prompt aqui")
        assert result == "resposta de teste"

    def test_generate_returns_default_no_context_response_when_not_configured(self):
        """Deve retornar a resposta padrao quando nao e configurada resposta fixa."""
        repo = MockLLMRepository()
        result = repo.generate("qualquer prompt")
        assert "Nao tenho informacoes" in result

    def test_generate_accepts_long_prompt(self):
        """Deve aceitar prompts longos sem erros."""
        repo = MockLLMRepository(fixed_response="ok")
        long_prompt = "texto longo " * 500
        result = repo.generate(long_prompt)
        assert result == "ok"

    def test_generate_accepts_empty_prompt(self):
        """Deve aceitar prompt vazio sem lancar excecao."""
        repo = MockLLMRepository(fixed_response="resposta")
        result = repo.generate("")
        assert result == "resposta"

    def test_different_instances_are_independent(self):
        """Duas instancias com respostas diferentes devem ser independentes."""
        repo1 = MockLLMRepository(fixed_response="resposta A")
        repo2 = MockLLMRepository(fixed_response="resposta B")
        assert repo1.generate("prompt") == "resposta A"
        assert repo2.generate("prompt") == "resposta B"
