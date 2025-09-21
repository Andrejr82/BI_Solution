"""
Agente de Sincronização de Dados SQL Server para Parquet
Responsável por manter os dados atualizados entre SQL Server e arquivos Parquet
"""

import pandas as pd
import pyodbc
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import schedule
import time
from pathlib import Path

# Settings e conexão importadas com lazy loading
from core.utils.db_connection import get_db_connection

logger = logging.getLogger(__name__)

def get_settings():
    """Obtém settings de forma lazy"""
    try:
        from core.config.safe_settings import get_safe_settings
        return get_safe_settings()
    except Exception:
        return None

class DataSyncAgent:
    """
    Agente responsável pela sincronização automática de dados entre SQL Server e Parquet
    """

    def __init__(self):
        self.data_dir = Path("data")
        self.parquet_dir = self.data_dir / "parquet"
        self.backup_dir = self.data_dir / "backup_parquet"
        self.log_file = self.data_dir / "sync_log.txt"

        # Criar diretórios se não existirem
        self.parquet_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Tabelas para sincronizar (adicione mais conforme necessário)
        self.tables_to_sync = [
            "Vendas",
            "Produtos",
            "Clientes",
            "Fornecedores",
            "Estoque",
            "Categorias"
        ]

    def log_operation(self, message: str):
        """Registra operação no log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_message)

        logger.info(message)

    def backup_existing_parquet(self):
        """Faz backup dos arquivos Parquet existentes"""
        try:
            backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_folder = self.backup_dir / f"backup_{backup_timestamp}"
            backup_folder.mkdir(exist_ok=True)

            # Copiar arquivos existentes
            for parquet_file in self.parquet_dir.glob("*.parquet"):
                backup_file = backup_folder / parquet_file.name
                import shutil
                shutil.copy2(parquet_file, backup_file)

            self.log_operation(f"Backup criado: {backup_folder}")
            return str(backup_folder)

        except Exception as e:
            self.log_operation(f"Erro ao criar backup: {e}")
            return None

    def get_table_data(self, table_name: str) -> Optional[pd.DataFrame]:
        """Extrai dados de uma tabela do SQL Server"""
        try:
            conn = get_db_connection()
            if conn is None:
                self.log_operation("Sem conexão de banco disponível")
                return None

            # Query para extrair todos os dados da tabela
            query = f"SELECT * FROM [{table_name}]"

            with conn:
                df = pd.read_sql(query, conn)
                self.log_operation(f"Extraídos {len(df)} registros da tabela {table_name}")
                return df

        except Exception as e:
            self.log_operation(f"Erro ao extrair dados da tabela {table_name}: {e}")
            return None

    def clean_dataframe(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Limpa e padroniza o DataFrame"""
        try:
            # Limpar nomes das colunas
            df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]

            # Remover linhas completamente vazias
            df = df.dropna(how='all')

            # Converter tipos de dados apropriados
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Tentar converter strings que são números
                    try:
                        if df[col].str.replace('.', '').str.replace(',', '').str.isdigit().all():
                            df[col] = pd.to_numeric(df[col].str.replace(',', '.'), errors='coerce')
                    except:
                        pass

            self.log_operation(f"DataFrame {table_name} limpo: {len(df)} registros, {len(df.columns)} colunas")
            return df

        except Exception as e:
            self.log_operation(f"Erro ao limpar DataFrame {table_name}: {e}")
            return df

    def save_to_parquet(self, df: pd.DataFrame, table_name: str) -> bool:
        """Salva DataFrame como arquivo Parquet"""
        try:
            parquet_file = self.parquet_dir / f"{table_name.lower()}.parquet"

            # Salvar com compressão
            df.to_parquet(
                parquet_file,
                compression='snappy',
                index=False,
                engine='pyarrow'
            )

            file_size = os.path.getsize(parquet_file) / 1024 / 1024  # MB
            self.log_operation(f"Arquivo salvo: {parquet_file} ({file_size:.2f} MB)")
            return True

        except Exception as e:
            self.log_operation(f"Erro ao salvar Parquet {table_name}: {e}")
            return False

    def sync_single_table(self, table_name: str) -> bool:
        """Sincroniza uma única tabela"""
        try:
            self.log_operation(f"Iniciando sincronização da tabela: {table_name}")

            # 1. Extrair dados do SQL Server
            df = self.get_table_data(table_name)
            if df is None or df.empty:
                self.log_operation(f"Nenhum dado encontrado para a tabela {table_name}")
                return False

            # 2. Limpar e padronizar dados
            df_clean = self.clean_dataframe(df, table_name)

            # 3. Salvar como Parquet
            success = self.save_to_parquet(df_clean, table_name)

            if success:
                self.log_operation(f"Sincronização concluída: {table_name}")

            return success

        except Exception as e:
            self.log_operation(f"Erro na sincronização da tabela {table_name}: {e}")
            return False

    def sync_all_tables(self) -> Dict[str, bool]:
        """Sincroniza todas as tabelas configuradas"""
        self.log_operation("=== INICIANDO SINCRONIZAÇÃO COMPLETA ===")

        # Criar backup antes da sincronização
        backup_path = self.backup_existing_parquet()

        results = {}
        total_success = 0

        for table in self.tables_to_sync:
            success = self.sync_single_table(table)
            results[table] = success
            if success:
                total_success += 1

        # Log de resultado final
        self.log_operation(f"Sincronização concluída: {total_success}/{len(self.tables_to_sync)} tabelas")
        self.log_operation("=== FIM DA SINCRONIZAÇÃO ===")

        return results

    def get_last_sync_info(self) -> Optional[Dict]:
        """Retorna informações sobre a última sincronização"""
        try:
            if not self.log_file.exists():
                return None

            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if not lines:
                return None

            # Procurar última sincronização completa
            last_sync = None
            for line in reversed(lines):
                if "INICIANDO SINCRONIZAÇÃO COMPLETA" in line:
                    timestamp_str = line.split("]")[0].split("[")[1]
                    last_sync = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    break

            if last_sync:
                return {
                    "last_sync": last_sync,
                    "time_ago": datetime.now() - last_sync,
                    "formatted": last_sync.strftime("%d/%m/%Y às %H:%M:%S")
                }

            return None

        except Exception as e:
            logger.error(f"Erro ao obter informações de sincronização: {e}")
            return None

    def schedule_automatic_sync(self, interval_hours: int = 24):
        """Agenda sincronização automática"""
        self.log_operation(f"Agendando sincronização automática a cada {interval_hours} horas")

        schedule.every(interval_hours).hours.do(self.sync_all_tables)

        # Loop de execução
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar a cada minuto

    def manual_sync(self) -> Dict[str, bool]:
        """Executa sincronização manual"""
        return self.sync_all_tables()

    def get_parquet_files_info(self) -> List[Dict]:
        """Retorna informações sobre os arquivos Parquet existentes"""
        files_info = []

        for parquet_file in self.parquet_dir.glob("*.parquet"):
            try:
                # Ler informações do arquivo
                df = pd.read_parquet(parquet_file)
                file_size = os.path.getsize(parquet_file) / 1024 / 1024  # MB
                mod_time = datetime.fromtimestamp(os.path.getmtime(parquet_file))

                files_info.append({
                    "filename": parquet_file.name,
                    "table_name": parquet_file.stem.title(),
                    "records": len(df),
                    "columns": len(df.columns),
                    "size_mb": round(file_size, 2),
                    "last_modified": mod_time,
                    "formatted_time": mod_time.strftime("%d/%m/%Y às %H:%M:%S")
                })

            except Exception as e:
                logger.error(f"Erro ao ler arquivo {parquet_file}: {e}")

        return sorted(files_info, key=lambda x: x["last_modified"], reverse=True)

# Instância global do agente
data_sync_agent = DataSyncAgent()