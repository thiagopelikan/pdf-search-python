#!/usr/bin/env bash
# Smoke test end-to-end: valida o pipeline completo com Docker e API real.
#
# Uso:
#   LLM_PROVIDER=openai ./scripts/smoke_test.sh
#   LLM_PROVIDER=gemini  ./scripts/smoke_test.sh [caminho/para/arquivo.pdf]
#
# Requisitos:
#   - Docker instalado e rodando
#   - .env com APP_ENV=production e API keys configuradas
#   - venv ativado ou dependencias instaladas globalmente

set -euo pipefail

PDF_PATH="${1:-Docs/document.pdf}"
PASS=0
FAIL=0

_ok()   { echo "[OK]  $1"; PASS=$((PASS + 1)); }
_fail() { echo "[FAIL] $1"; FAIL=$((FAIL + 1)); }
_info() { echo "---  $1"; }

_info "Iniciando smoke test (provider=${LLM_PROVIDER:-openai})"

# 1. Docker acessivel
if docker info > /dev/null 2>&1; then
    _ok "Docker acessivel"
else
    _fail "Docker nao esta rodando"
    exit 1
fi

# 2. Subir banco (idempotente)
docker compose up -d > /dev/null 2>&1
sleep 2

# 3. Verificar conectividade com o PostgreSQL
if docker exec pdf-search-postgres pg_isready -U postgres > /dev/null 2>&1; then
    _ok "PostgreSQL acessivel"
else
    _fail "PostgreSQL nao responde"
    exit 1
fi

# 4. PDF existe
if [ -f "$PDF_PATH" ]; then
    _ok "PDF encontrado: $PDF_PATH"
else
    _fail "PDF nao encontrado: $PDF_PATH"
    exit 1
fi

# 5. Ingestion
_info "Rodando ingestion..."
INGEST_OUTPUT=$(APP_ENV=production PYTHONPATH=. python src/ingest.py "$PDF_PATH" 2>&1)
if echo "$INGEST_OUTPUT" | grep -q "Ingestion concluida"; then
    CHUNKS=$(echo "$INGEST_OUTPUT" | grep -oE '[0-9]+ chunks' | tail -1)
    _ok "Ingestion concluida: $CHUNKS armazenados"
else
    _fail "Ingestion falhou"
    echo "$INGEST_OUTPUT" | tail -5
    exit 1
fi

# 6. Busca com pergunta relevante
_info "Testando busca semantica..."
SEARCH_OUTPUT=$(APP_ENV=production PYTHONPATH=. python src/search.py "O que e Domain Driven Design?" 2>&1)
if echo "$SEARCH_OUTPUT" | grep -q "RESPOSTA:"; then
    RESPOSTA=$(echo "$SEARCH_OUTPUT" | grep "RESPOSTA:" | head -1)
    if echo "$RESPOSTA" | grep -qi "nao tenho informacoes"; then
        _fail "Busca retornou resposta generica para pergunta relevante"
    else
        _ok "Busca semantica retornou resposta relevante"
    fi
else
    _fail "Busca semantica falhou"
    echo "$SEARCH_OUTPUT" | tail -5
fi

# 7. Busca com pergunta fora de contexto
_info "Testando recusa de pergunta fora de contexto..."
OUT_OF_CTX=$(APP_ENV=production PYTHONPATH=. python src/search.py "Qual e a capital da Franca?" 2>&1)
if echo "$OUT_OF_CTX" | grep -qi "nao tenho informacoes\|não tenho informações"; then
    _ok "Pergunta fora de contexto recusada corretamente"
else
    _fail "Pergunta fora de contexto nao foi recusada"
    echo "$OUT_OF_CTX" | grep "RESPOSTA:"
fi

# Resultado final
echo ""
echo "Resultado: ${PASS} ok, ${FAIL} falhas"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
