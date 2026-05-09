PYTHON = venv/bin/python
PYTEST = PYTHONWARNINGS=ignore $(PYTHON) -m pytest

test:
	APP_ENV=development $(PYTEST) tests/unit tests/integration -v

test-e2e-openai:
	APP_ENV=production LLM_PROVIDER=openai $(PYTEST) tests/e2e/ -m e2e -v

test-e2e-gemini:
	APP_ENV=production LLM_PROVIDER=gemini $(PYTEST) tests/e2e/ -m e2e -v

ingest:
	$(PYTHON) src/ingest.py

chat:
	$(PYTHON) src/chat.py
