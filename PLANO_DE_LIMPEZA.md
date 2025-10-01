# Plano de Limpeza e Preparação do Projeto

**Objetivo:** Remover arquivos e pastas desnecessários para criar uma versão de produção limpa, pronta para um cliente e para deploy na Hostinger.

---

### **Fase 1: Ponto de Restauração Seguro (Backup via Git)**

Esta é a fase mais importante. Antes de apagar qualquer coisa, criaremos um backup seguro e um ambiente isolado para a limpeza.

1.  **Verificar Mudanças Atuais:** Garantir que todo o seu trabalho recente está salvo.
    *   Comando: `git status`
2.  **Salvar Todas as Mudanças:** Adicionar e "commitar" todas as alterações atuais para criar um ponto de restauração.
    *   Comandos:
        ```bash
        git add .
        git commit -m "Checkpoint: Antes da limpeza geral do projeto"
        ```
3.  **Criar um "Ramo" de Limpeza:** Isolaremos todo o processo de limpeza em um novo "ramo" (branch). Se algo der errado, podemos simplesmente apagar este ramo e voltar ao estado anterior.
    *   Comando: `git checkout -b sprint-limpeza-producao`

---

### **Fase 2: Análise e Identificação de Alvos**

Aqui, classificamos o que pode ser removido.

**A. Remoção Segura (Arquivos e Pastas Gerados ou de Cache)**
*   **Alvos:** `__pycache__/`, `cache/`, `logs/`, `tests/results/`, `*.pyc`
*   **Justificativa:** São arquivos temporários ou de cache que o Python e a aplicação criam e recriam automaticamente. Os logs não são necessários para o cliente.

**B. Remoção de Ferramentas de Desenvolvimento e Configurações de Outras Plataformas**
*   **Alvos:** `.github/`, `.claude/`, `.devcontainer/`, `.vercel/`, `dev_tools/`, `maintenance/`, `tests/` (a pasta inteira), `build.sh`, `test_*.py` (arquivos de teste individuais na raiz).
*   **Justificativa:** Estas pastas e arquivos são para o seu processo de desenvolvimento (testes, CI/CD do GitHub, configuração do VS Code, Vercel) e não são necessários para a aplicação rodar em produção na Hostinger.

**C. Arquivamento e Limpeza de Documentação**
*   **Alvo:** A pasta `docs/`.
*   **Justificativa:** Esta pasta contém muitos relatórios de desenvolvimento (`relatorio_*.md`) que não interessam ao cliente. No entanto, arquivos como `user-guide.md` podem ser úteis.
*   **Ação Proposta:** Mover os relatórios de desenvolvimento para a subpasta `docs/archive/` e manter apenas a documentação relevante para o usuário final.

**D. Análise Crítica da Pasta `data/` (NÃO APAGAR, MAS REVISAR)**
*   **Alvo:** A pasta `data/`.
*   **Justificativa:** **Esta pasta é crítica.** Contém arquivos `.json` que parecem ser catálogos de dados, configurações e templates essenciais para a aplicação. O arquivo `vector_store.pkl` é um banco de dados de vetores que pode ser caro ou demorado para recriar.
*   **Ação Proposta:** **NÃO** apagar nada desta pasta como parte da limpeza automática. A recomendação é revisá-la manualmente para garantir que apenas os dados necessários para o cliente estejam presentes. Por exemplo, `business_question_templates.json` parece essencial.

---

### **Fase 3: Plano de Execução (Comandos para Amanhã)**

Amanhã, quando estiver pronto, você executará os seguintes comandos na ordem apresentada.

```bash
# --- Início do Script de Limpeza ---

# 1. Remover pastas de cache e geradas (Seguro)
echo "Removendo caches e logs..."
rm -rf __pycache__
rm -rf cache
rm -rf logs
rm -rf tests/results

# 2. Remover ferramentas de desenvolvimento e configurações de outras plataformas
echo "Removendo ferramentas de desenvolvimento e testes..."
rm -rf .github
rm -rf .claude
rm -rf .devcontainer
rm -rf .vercel
rm -rf dev_tools
rm -rf maintenance
rm -rf tests
rm -f build.sh
rm -f test_simple_import.py
rm -f test_streamlit_cloud_simulation.py

# 3. Arquivar documentação de desenvolvimento (Requer revisão manual depois)
echo "Arquivando documentos de desenvolvimento..."
# Cria a pasta de arquivo se não existir
mkdir -p docs/archive
# Move os relatórios para a pasta de arquivo
mv docs/relatorio_*.md docs/archive/
mv docs/analise_arquitetura_logs.md docs/archive/
mv docs/sessao_correcoes_criticas_2025-09-18.md docs/archive/

echo "Limpeza concluída. Revise a pasta 'docs/' e 'data/' manualmente."
# --- Fim do Script de Limpeza ---
```

---

### **Fase 4: Finalização e Empacotamento**

Após executar os comandos e revisar manualmente as pastas `docs/` e `data/`:

1.  **Testar a Aplicação:** Rode o `streamlit_app.py` localmente para garantir que a aplicação ainda funciona perfeitamente.
2.  **Criar Pacote para o Cliente:** Crie um arquivo `.zip` limpo do projeto para enviar ao cliente ou para o deploy.
    *   Comando: `zip -r Agent_Solution_BI_Cliente.zip . -x ".git/*" "*.zip"`
3.  **Salvar o Trabalho de Limpeza:** Faça o commit final no ramo de limpeza.
    *   Comandos:
        ```bash
        git add .
        git commit -m "Feat: Limpeza geral do projeto para versão de produção"
        ```
