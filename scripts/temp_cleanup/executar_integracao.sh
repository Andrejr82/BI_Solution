#!/bin/bash

echo "================================================================================"
echo "INTEGRACAO DynamicPrompt no CodeGenAgent"
echo "TAREFA 5 - PLANO_PILAR_4_EXECUCAO.md"
echo "================================================================================"
echo ""

echo "[1/2] Executando integracao..."
python3 integrate_dynamic_prompt.py
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERRO] Integracao falhou!"
    exit 1
fi

echo ""
echo "[2/2] Validando integracao..."
python3 validate_integration.py
if [ $? -ne 0 ]; then
    echo ""
    echo "[AVISO] Validacao encontrou problemas. Verifique os logs acima."
    exit 1
fi

echo ""
echo "================================================================================"
echo "INTEGRACAO CONCLUIDA COM SUCESSO!"
echo "================================================================================"
echo ""
echo "Proximos passos:"
echo "  1. Testar com queries reais"
echo "  2. Monitorar logs de execucao"
echo "  3. Continuar para TAREFA 6 - FeedbackCollector"
echo ""
echo "Documentacao: INTEGRACAO_DYNAMIC_PROMPT.md"
echo ""
