"""Testes unitarios do use case SearchContext."""

from unittest.mock import MagicMock

import pytest

from src.domain.entities.document_chunk import DocumentChunk
from src.domain.use_cases.search_context import SearchContext


def _make_chunk(content: str, page: int = 1) -> DocumentChunk:
    """Helper para criar DocumentChunk de teste."""
    return DocumentChunk(content=content, page=page, source="test.pdf")


def _make_use_case(search_results=None, llm_response: str = "resposta gerada"):
    """Helper para criar SearchContext com mocks configurados."""
    mock_vector_repo = MagicMock()
    mock_vector_repo.search.return_value = search_results or []

    mock_llm_repo = MagicMock()
    mock_llm_repo.generate.return_value = llm_response

    use_case = SearchContext(
        vector_repository=mock_vector_repo,
        llm_repository=mock_llm_repo,
    )
    return use_case, mock_vector_repo, mock_llm_repo


class TestSearchContext:
    """Testes para o use case SearchContext."""

    def test_raises_for_empty_question(self):
        """Deve lancar ValueError para pergunta vazia."""
        use_case, _, _ = _make_use_case()
        with pytest.raises(ValueError, match="vazia"):
            use_case.execute("")

    def test_raises_for_whitespace_only_question(self):
        """Deve lancar ValueError para pergunta com apenas espacos."""
        use_case, _, _ = _make_use_case()
        with pytest.raises(ValueError, match="vazia"):
            use_case.execute("   ")

    def test_calls_search_with_k_equals_10(self):
        """Deve buscar exatamente k=10 resultados conforme o enunciado."""
        use_case, mock_vector_repo, _ = _make_use_case()
        use_case.execute("qual e o faturamento?")
        mock_vector_repo.search.assert_called_once_with("qual e o faturamento?", k=10)

    def test_returns_llm_response(self):
        """Deve retornar a resposta gerada pelo LLM."""
        chunk = _make_chunk("O faturamento foi de 10 milhoes.")
        use_case, _, _ = _make_use_case(
            search_results=[(chunk, 0.95)],
            llm_response="O faturamento foi de 10 milhoes de reais.",
        )
        result = use_case.execute("qual e o faturamento?")
        assert result == "O faturamento foi de 10 milhoes de reais."

    def test_concatenates_chunks_as_context(self):
        """Deve concatenar o conteudo dos chunks como contexto para o LLM."""
        chunks = [
            (_make_chunk("Primeiro trecho."), 0.9),
            (_make_chunk("Segundo trecho."), 0.8),
        ]
        use_case, _, mock_llm_repo = _make_use_case(search_results=chunks)
        use_case.execute("pergunta qualquer")

        # Verificar que o prompt enviado ao LLM contem o conteudo dos dois chunks
        prompt_arg = mock_llm_repo.generate.call_args[0][0]
        assert "Primeiro trecho." in prompt_arg
        assert "Segundo trecho." in prompt_arg

    def test_handles_empty_search_results(self):
        """Deve retornar resposta padrao sem chamar o LLM quando nao ha resultados relevantes."""
        use_case, _, mock_llm_repo = _make_use_case(search_results=[])
        result = use_case.execute("pergunta sem contexto")
        mock_llm_repo.generate.assert_not_called()
        assert result == "Nao tenho informacoes necessarias para responder sua pergunta."

    def test_question_included_in_prompt(self):
        """Deve incluir a pergunta do usuario no prompt enviado ao LLM."""
        chunk = _make_chunk("Informacao relevante sobre o tema.")
        use_case, _, mock_llm_repo = _make_use_case(search_results=[(chunk, 0.9)])
        use_case.execute("Qual o faturamento da empresa?")
        prompt_arg = mock_llm_repo.generate.call_args[0][0]
        assert "Qual o faturamento da empresa?" in prompt_arg
