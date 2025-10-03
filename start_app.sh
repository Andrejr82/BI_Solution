#!/bin/bash
# ========================================
#   Agent_BI - Inicializador para Linux/macOS
#   Inicia Backend (FastAPI) e Frontend (Streamlit)
# ========================================

echo ""
echo "========================================"
echo "   AGENT_BI - AGENTE DE NEGÓCIOS"
echo "   Inicializando aplicação..."
echo "========================================"
echo ""

# Verificar se está na pasta correta
if [ ! -f "streamlit_app.py" ]; then
    echo "[ERRO] Arquivo streamlit_app.py não encontrado!"
    echo "Execute este script na raiz do projeto."
    exit 1
fi

# Verificar se ambiente virtual existe
if [ ! -d ".venv" ]; then
    echo "[ERRO] Ambiente virtual não encontrado!"
    echo "Execute: python -m venv .venv"
    exit 1
fi

# Ativar ambiente virtual
echo "[1/4] Ativando ambiente virtual..."
source .venv/bin/activate

# Verificar se backend existe
if [ ! -f "main.py" ]; then
    echo "[AVISO] Backend FastAPI não encontrado. Pulando..."
    echo "[3/4] Iniciando Frontend Streamlit..."
    streamlit run streamlit_app.py &
    FRONTEND_PID=$!

    echo ""
    echo "========================================"
    echo "   APLICAÇÃO INICIADA COM SUCESSO!"
    echo "   Frontend: http://localhost:8501"
    echo "========================================"
    echo ""
    echo "Pressione Ctrl+C para encerrar..."

    trap "kill $FRONTEND_PID 2>/dev/null; exit" INT TERM
    wait $FRONTEND_PID
    exit 0
fi

# Iniciar Backend FastAPI em segundo plano
echo "[2/4] Iniciando Backend FastAPI..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Aguardar backend estar pronto
echo "[3/4] Aguardando Backend inicializar..."
sleep 3

for i in {1..30}; do
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo "   - Backend pronto! [OK]"
        break
    fi
    echo -ne "   - Tentativa $i/30...\r"
    sleep 2
done

# Iniciar Frontend Streamlit
echo "[4/4] Iniciando Frontend Streamlit..."
sleep 1
streamlit run streamlit_app.py &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "   APLICAÇÃO INICIADA COM SUCESSO!"
echo ""
echo "   Backend:  http://localhost:8000"
echo "   Docs API: http://localhost:8000/docs"
echo "   Frontend: http://localhost:8501"
echo ""
echo "   Para encerrar: Ctrl+C neste terminal"
echo "========================================"
echo ""

# Capturar Ctrl+C e encerrar processos
trap "echo '\n\nEncerrando aplicação...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Aplicação encerrada com sucesso!'; exit" INT TERM

# Manter script rodando
echo "Pressione Ctrl+C para encerrar a aplicação..."
wait
