"""
Script de Exportação: SQL Server → Parquet
Exporta tabela ADMMATAO completa com todas as 95 colunas.

ATENÇÃO: Este script sobrescreve o Parquet atual!
Backup automático criado antes da execução.
"""
import os
import sys
import pyodbc
import pandas as pd
from datetime import datetime
from pathlib import Path
import shutil

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def load_env():
    """Carrega variáveis do .env"""
    env_path = Path(__file__).parent.parent / '.env'
    env_vars = {}

    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"')

    return env_vars

def create_backup(parquet_path: Path):
    """Cria backup do Parquet atual antes de sobrescrever."""
    if parquet_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = parquet_path.parent / f"admmat_backup_{timestamp}.parquet"

        print(f"Criando backup: {backup_path.name}")
        shutil.copy2(parquet_path, backup_path)
        print(f"[OK] Backup criado com sucesso!")
        return backup_path
    else:
        print("Parquet atual nao existe, criando novo arquivo...")
        return None

def export_sqlserver_to_parquet():
    """Exporta tabela ADMMATAO do SQL Server para Parquet."""

    print("\n" + "="*70)
    print("EXPORTACAO SQL SERVER -> PARQUET")
    print("="*70 + "\n")

    # 1. Carregar credenciais do .env
    print("1. Carregando credenciais do .env...")
    env_vars = load_env()

    required_vars = ['MSSQL_SERVER', 'MSSQL_DATABASE', 'MSSQL_USER', 'MSSQL_PASSWORD', 'DB_DRIVER']
    missing = [v for v in required_vars if v not in env_vars]

    if missing:
        print(f"[ERRO] Variaveis faltando no .env: {missing}")
        return False

    print(f"[OK] Credenciais carregadas")
    print(f"   Servidor: {env_vars['MSSQL_SERVER']}")
    print(f"   Database: {env_vars['MSSQL_DATABASE']}")
    print(f"   User: {env_vars['MSSQL_USER']}")

    # 2. Criar string de conexão
    trust_cert = env_vars.get('DB_TRUST_SERVER_CERTIFICATE', 'yes')
    conn_str = (
        f"DRIVER={{{env_vars['DB_DRIVER']}}};"
        f"SERVER={env_vars['MSSQL_SERVER']};"
        f"DATABASE={env_vars['MSSQL_DATABASE']};"
        f"UID={env_vars['MSSQL_USER']};"
        f"PWD={env_vars['MSSQL_PASSWORD']};"
        f"TrustServerCertificate={trust_cert};"
    )

    # 3. Conectar ao SQL Server
    print("\n2. Conectando ao SQL Server...")
    try:
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        print("[OK] Conexao estabelecida com sucesso!")
    except Exception as e:
        print(f"[ERRO] ao conectar: {e}")
        print("\nVerifique:")
        print("   - SQL Server esta rodando?")
        print("   - Credenciais estao corretas?")
        print("   - Firewall liberado?")
        return False

    # 4. Verificar tabela ADMMATAO
    print("\n3. Verificando tabela ADMMATAO...")
    try:
        cursor.execute("SELECT COUNT(*) FROM ADMMATAO")
        total_rows = cursor.fetchone()[0]
        print(f"[OK] Tabela encontrada: {total_rows:,} registros")
    except Exception as e:
        print(f"[ERRO] Tabela ADMMATAO nao encontrada: {e}")
        conn.close()
        return False

    # 5. Exportar dados com SQLAlchemy + chunking (OTIMIZADO)
    print("\n4. Exportando dados (modo otimizado com chunking)...")
    try:
        from sqlalchemy import create_engine
        from urllib.parse import quote_plus

        # Criar engine SQLAlchemy
        connection_string = (
            f"mssql+pyodbc://{env_vars['MSSQL_USER']}:{quote_plus(env_vars['MSSQL_PASSWORD'])}"
            f"@{env_vars['MSSQL_SERVER']}/{env_vars['MSSQL_DATABASE']}"
            f"?driver={quote_plus(env_vars['DB_DRIVER'])}"
            f"&TrustServerCertificate={trust_cert}"
        )

        engine = create_engine(connection_string, fast_executemany=True)

        # Query para buscar TODOS os dados
        query = "SELECT * FROM ADMMATAO"

        print("   Lendo dados em chunks (100k registros por vez)...")

        chunks = []
        chunk_size = 100000
        total_rows = 0

        for i, chunk in enumerate(pd.read_sql(query, engine, chunksize=chunk_size)):
            total_rows += len(chunk)
            chunks.append(chunk)
            print(f"   Chunk {i+1}: {len(chunk):,} linhas (total: {total_rows:,})")

        # Combinar chunks
        print("   Combinando chunks...")
        df = pd.concat(chunks, ignore_index=True)

        print(f"   [OK] Dados lidos: {len(df):,} linhas x {len(df.columns)} colunas")
        print(f"   Tamanho em memoria: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

        engine.dispose()

        # Mapear nomes das colunas (SQL Server MAIÚSCULO → parquet minúsculo)
        column_mapping = {
            'UNE': 'une',
            'PRODUTO': 'codigo',
            'TIPO': 'tipo',
            'UNE_NOME': 'une_nome',
            'NOME': 'nome_produto',
            'EMBALAGEM': 'embalagem',
            'NOMESEGMENTO': 'nomesegmento',
            'NomeCategoria': 'nome_categoria',
            'NOMEGRUPO': 'nomegrupo',
            'NomeSUBGRUPO': 'nome_subgrupo',
            'NomeFabricante': 'nome_fabricante',
            'EAN': 'ean',
            'PROMOCIONAL': 'promocional',
            'FORALINHA': 'foralinha',
            'LIQUIDO_38': 'preco_38_percent',
            'QTDE_EMB_MASTER': 'qtde_emb_master',
            'QTDE_EMB_MULTIPLO': 'qtde_emb_multiplo',
            'ABC_UNE_MES_04': 'abc_une_mes_04',
            'ABC_UNE_MES_03': 'abc_une_mes_03',
            'ABC_UNE_MES_02': 'abc_une_mes_02',
            'ABC_UNE_MES_01': 'abc_une_mes_01',
            'ABC_UNE_30DD': 'abc_une_30_dd',
            'ABC_CACULA_90DD': 'abc_cacula_90_dd',
            'ABC_UNE_30XABC_CACULA_90DD': 'abc_une_30_xabc_cacula_90_dd',
            'MES_12': 'mes_12',
            'MES_11': 'mes_11',
            'MES_10': 'mes_10',
            'MES_09': 'mes_09',
            'MES_08': 'mes_08',
            'MES_07': 'mes_07',
            'MES_06': 'mes_06',
            'MES_05': 'mes_05',
            'MES_04': 'mes_04',
            'MES_03': 'mes_03',
            'MES_02': 'mes_02',
            'MES_01': 'mes_01',
            'MES_PARCIAL': 'mes_parcial',
            'SEMANA_ANTERIOR_5': 'semana_anterior_5',
            'FREQ_SEMANA_ANTERIOR_5': 'freq_semana_anterior_5',
            'QTDE_SEMANA_ANTERIOR_5': 'qtde_semana_anterior_5',
            'MEDIA_SEMANA_ANTERIOR_5': 'media_semana_anterior_5',
            'SEMANA_ANTERIOR_4': 'semana_anterior_4',
            'FREQ_SEMANA_ANTERIOR_4': 'freq_semana_anterior_4',
            'QTDE_SEMANA_ANTERIOR_4': 'qtde_semana_anterior_4',
            'MEDIA_SEMANA_ANTERIOR_4': 'media_semana_anterior_4',
            'SEMANA_ANTERIOR_3': 'semana_anterior_3',
            'FREQ_SEMANA_ANTERIOR_3': 'freq_semana_anterior_3',
            'QTDE_SEMANA_ANTERIOR_3': 'qtde_semana_anterior_3',
            'MEDIA_SEMANA_ANTERIOR_3': 'media_semana_anterior_3',
            'SEMANA_ANTERIOR_2': 'semana_anterior_2',
            'FREQ_SEMANA_ANTERIOR_2': 'freq_semana_anterior_2',
            'QTDE_SEMANA_ANTERIOR_2': 'qtde_semana_anterior_2',
            'MEDIA_SEMANA_ANTERIOR_2': 'media_semana_anterior_2',
            'SEMANA_ATUAL': 'semana_atual',
            'FREQ_SEMANA_ATUAL': 'freq_semana_atual',
            'QTDE_SEMANA_ATUAL': 'qtde_semana_atual',
            'MEDIA_SEMANA_ATUAL': 'media_semana_atual',
            'VENDA_30DD': 'venda_30_d',
            'MEDIA_CONSIDERADA_LV': 'media_considerada_lv',
            'ESTOQUE_CD': 'estoque_cd',
            'ULTIMA_ENTRADA_DATA_CD': 'ultima_entrada_data_cd',
            'ULTIMA_ENTRADA_QTDE_CD': 'ultima_entrada_qtde_cd',
            'ULTIMA_ENTRADA_CUSTO_CD': 'ultima_entrada_custo_cd',
            'ESTOQUE_UNE': 'estoque_atual',
            'ULTIMO_INVENTARIO_UNE': 'ultimo_inventario_une',
            'ULTIMA_ENTRADA_DATA_UNE': 'ultima_entrada_data_une',
            'ULTIMA_ENTRADA_QTDE_UNE': 'ultima_entrada_qtde_une',
            'ESTOQUE_LV': 'estoque_lv',
            'ESTOQUE_GONDOLA_LV': 'estoque_gondola_lv',
            'ESTOQUE_ILHA_LV': 'estoque_ilha_lv',
            'EXPOSICAO_MINIMA': 'exposicao_minima',
            'EXPOSICAO_MINIMA_UNE': 'exposicao_minima_une',
            'EXPOSICAO_MAXIMA_UNE': 'exposicao_maxima_une',
            'LEADTIME_LV': 'leadtime_lv',
            'PONTO_PEDIDO_LV': 'ponto_pedido_lv',
            'MEDIA_TRAVADA': 'media_travada',
            'ENDERECO_RESERVA': 'endereco_reserva',
            'ENDERECO_LINHA': 'endereco_linha',
            'SOLICITACAO_PENDENTE': 'solicitacao_pendente',
            'SOLICITACAO_PENDENTE_DATA': 'solicitacao_pendente_data',
            'SOLICITACAO_PENDENTE_QTDE': 'solicitacao_pendente_qtde',
            'SOLICITACAO_PENDENTE_SITUACAO': 'solicitacao_pendente_situacao',
            'ULTIMA_VENDA_DATA_UNE': 'ultima_venda_data_une',
            'PICKLIST': 'picklist',
            'PICKLIST_SITUACAO': 'picklist_situacao',
            'PICKLIST_CONFERENCIA': 'picklist_conferencia',
            'ULTIMO_VOLUME': 'ultimo_volume',
            'VOLUME_QTDE': 'volume_qtde',
            'ROMANEIO_SOLICITACAO': 'romaneio_solicitacao',
            'ROMANEIO_ENVIO': 'romaneio_envio',
            'NOTA': 'nota',
            'SERIE': 'serie',
            'NOTA_EMISSAO': 'nota_emissao',
            'FREQ_ULT_SEM': 'freq_ult_sem',
            'COMPRADOR': 'comprador'
        }

        # Renomear colunas
        df_renamed = df.rename(columns=column_mapping)
        print(f"   [OK] Colunas renomeadas para formato padrao")

    except Exception as e:
        print(f"[ERRO] ao exportar: {e}")
        conn.close()
        return False

    finally:
        conn.close()
        print("   Conexao SQL Server fechada")

    # 6. Criar backup do Parquet atual
    parquet_path = Path(__file__).parent.parent / 'data' / 'parquet' / 'admmat.parquet'
    backup_path = create_backup(parquet_path)

    # 7. Salvar novo Parquet
    print("\n5. Salvando Parquet...")
    try:
        parquet_path.parent.mkdir(parents=True, exist_ok=True)

        # Salvar com compressão
        df_renamed.to_parquet(
            parquet_path,
            engine='pyarrow',
            compression='snappy',
            index=False
        )

        file_size_mb = parquet_path.stat().st_size / 1024**2

        print(f"   [OK] Parquet salvo com sucesso!")
        print(f"   Arquivo: {parquet_path}")
        print(f"   Tamanho: {file_size_mb:.2f} MB")

    except Exception as e:
        print(f"[ERRO] ao salvar Parquet: {e}")

        # Restaurar backup se falhou
        if backup_path and backup_path.exists():
            print("   Restaurando backup...")
            shutil.copy2(backup_path, parquet_path)
            print("   [OK] Backup restaurado")

        return False

    # 8. Validar Parquet gerado
    print("\n6. Validando Parquet gerado...")
    try:
        df_test = pd.read_parquet(parquet_path)

        print(f"   [OK] Validacao OK!")
        print(f"   Linhas: {len(df_test):,}")
        print(f"   Colunas: {len(df_test.columns)}")
        print(f"   Primeiras colunas: {list(df_test.columns[:5])}")

        # Verificar coluna vendas_total
        vendas_cols = [f'mes_{i:02d}' for i in range(1, 13)]
        vendas_existentes = [c for c in vendas_cols if c in df_test.columns]

        if vendas_existentes:
            df_test['vendas_total'] = df_test[vendas_existentes].fillna(0).sum(axis=1)
            print(f"   [OK] Coluna vendas_total criada automaticamente")

    except Exception as e:
        print(f"[ERRO] na validacao: {e}")
        return False

    # Resumo final
    print("\n" + "="*70)
    print("EXPORTACAO CONCLUIDA COM SUCESSO!")
    print("="*70)
    print(f"\nResumo:")
    print(f"   Registros exportados: {len(df_renamed):,}")
    print(f"   Colunas: {len(df_renamed.columns)}")
    print(f"   Arquivo: {parquet_path}")
    print(f"   Tamanho: {file_size_mb:.2f} MB")
    if backup_path:
        print(f"   Backup: {backup_path.name}")
    print(f"\nProximos passos:")
    print(f"   1. Executar: python scripts/test_hybrid_connection.py")
    print(f"   2. Testar app: streamlit run streamlit_app.py")
    print(f"\n")

    return True

if __name__ == "__main__":
    success = export_sqlserver_to_parquet()
    sys.exit(0 if success else 1)
