@echo off
echo ============================================================
echo DIAGNOSTICO: Sistema de Transferencias
echo ============================================================
echo.

echo [1/3] Testando carregamento de produtos (UNE 1)...
python -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path.cwd())); from core.connectivity.hybrid_adapter import HybridDataAdapter; import pandas as pd; adapter = HybridDataAdapter(); result = adapter.execute_query({'une': 1}); df = pd.DataFrame(result); df['estoque_atual'] = pd.to_numeric(df['estoque_atual'], errors='coerce').fillna(0); com_estoque = (df['estoque_atual'] > 0).sum(); print(f'\n✓ UNE 1: {com_estoque} produtos com estoque\n')"

echo.
echo [2/3] Testando carregamento de produtos (UNE 3)...
python -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path.cwd())); from core.connectivity.hybrid_adapter import HybridDataAdapter; import pandas as pd; adapter = HybridDataAdapter(); result = adapter.execute_query({'une': 3}); df = pd.DataFrame(result); df['estoque_atual'] = pd.to_numeric(df['estoque_atual'], errors='coerce').fillna(0); com_estoque = (df['estoque_atual'] > 0).sum(); print(f'\n✓ UNE 3: {com_estoque} produtos com estoque\n')"

echo.
echo [3/3] Verificando funcao get_produtos_une()...
python -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path.cwd())); from core.connectivity.hybrid_adapter import HybridDataAdapter; import pandas as pd; adapter = HybridDataAdapter(); result = adapter.execute_query({'une': 1}); df = pd.DataFrame(result); cols_relevantes = ['codigo', 'nome_produto', 'estoque_atual', 'venda_30_d', 'preco_38_percent', 'nomesegmento', 'NOMEFABRICANTE']; cols_existentes = [c for c in cols_relevantes if c in df.columns]; df_produtos = df[cols_existentes].copy(); colunas_numericas = ['estoque_atual', 'venda_30_d', 'preco_38_percent']; [df_produtos.__setitem__(col, pd.to_numeric(df_produtos[col], errors='coerce').fillna(0)) for col in colunas_numericas if col in df_produtos.columns]; df_produtos = df_produtos[df_produtos['estoque_atual'] > 0]; print(f'\n✓ Funcao get_produtos_une(): {len(df_produtos)} produtos retornados\n')"

echo.
echo ============================================================
echo RESULTADO:
echo ============================================================
echo.
echo Se voce ver numeros de produtos acima (ex: 41460, 20745),
echo o codigo esta funcionando!
echo.
echo PROXIMOS PASSOS:
echo 1. Parar o Streamlit (Ctrl+C no terminal)
echo 2. Executar: streamlit run streamlit_app.py
echo 3. Limpar cache do navegador (Ctrl+Shift+R)
echo 4. No Streamlit, clicar em "Clear cache" no menu (C)
echo.
pause
