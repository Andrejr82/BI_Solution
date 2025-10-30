#!/bin/bash

# Agent Solution BI - Launcher
# Para Linux e Mac

echo "===================================================================="
echo "🤖 Agent Solution BI - Launcher"
echo "===================================================================="
echo ""

echo "[1/2] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python não encontrado! Instale Python 3.11+"
    exit 1
fi
echo "✓ Python OK"

echo ""
echo "[2/2] Iniciando launcher..."
echo ""

python3 start_all.py
