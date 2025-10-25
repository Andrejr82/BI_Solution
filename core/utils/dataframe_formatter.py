"""
Formatador de DataFrames para melhor exibição no Streamlit
Aplica formatação brasileira (R$, separadores de milhar, etc.)
"""

import pandas as pd
import locale
import logging

logger = logging.getLogger(__name__)

# Configurar locale brasileiro
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        logger.warning("Não foi possível configurar locale brasileiro")


def format_currency_value(value):
    """
    Formata um valor como moeda brasileira (R$)

    Args:
        value: Valor numérico

    Returns:
        String formatada como R$ X.XXX,XX
    """
    if pd.isna(value) or value is None:
        return "R$ 0,00"

    try:
        # Garantir que é float
        if isinstance(value, str):
            value = float(value.replace(',', '.'))

        value = float(value)

        # Formatar como moeda brasileira
        # Usar formatação manual para garantir consistência
        if value < 0:
            return f"-R$ {abs(value):,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
        else:
            return f"R$ {value:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

    except (ValueError, TypeError) as e:
        logger.warning(f"Erro ao formatar valor como moeda: {value} - {e}")
        return f"R$ {value}"


def format_number_value(value, decimals=2):
    """
    Formata um número com separadores de milhar brasileiros

    Args:
        value: Valor numérico
        decimals: Número de casas decimais

    Returns:
        String formatada como X.XXX,XX
    """
    if pd.isna(value) or value is None:
        return "0"

    try:
        value = float(value)

        # Formatar com separadores brasileiros
        if decimals == 0:
            return f"{value:,.0f}".replace(',', '.')
        else:
            return f"{value:,.{decimals}f}".replace(',', '_').replace('.', ',').replace('_', '.')

    except (ValueError, TypeError) as e:
        logger.warning(f"Erro ao formatar número: {value} - {e}")
        return str(value)


def detect_currency_columns(df):
    """
    Detecta colunas que provavelmente contêm valores monetários

    Args:
        df: DataFrame pandas

    Returns:
        Lista de nomes de colunas monetárias
    """
    currency_keywords = [
        'preco', 'preço', 'valor', 'custo', 'venda', 'vendas',
        'liquido', 'bruto', 'receita', 'faturamento', 'total',
        'LIQUIDO', 'VENDA', 'PRECO', 'CUSTO', 'TOTAL'
    ]

    currency_columns = []

    for col in df.columns:
        col_lower = str(col).lower()

        # Verificar se o nome da coluna contém palavras-chave
        if any(keyword in col_lower for keyword in currency_keywords):
            # Verificar se a coluna é numérica
            if pd.api.types.is_numeric_dtype(df[col]):
                currency_columns.append(col)

    return currency_columns


def detect_number_columns(df):
    """
    Detecta colunas numéricas que não são monetárias

    Args:
        df: DataFrame pandas

    Returns:
        Lista de nomes de colunas numéricas
    """
    number_columns = []
    currency_cols = detect_currency_columns(df)

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]) and col not in currency_cols:
            # Verificar se não é uma coluna de ID/código
            if not any(id_kw in str(col).lower() for id_kw in ['id', 'codigo', 'produto', 'une_id']):
                number_columns.append(col)

    return number_columns


def format_dataframe_for_display(df, auto_detect=True, currency_cols=None, number_cols=None):
    """
    Formata um DataFrame para exibição no Streamlit com formatação brasileira

    Args:
        df: DataFrame pandas
        auto_detect: Se True, detecta automaticamente colunas monetárias/numéricas
        currency_cols: Lista de colunas a formatar como moeda (sobrescreve auto-detect)
        number_cols: Lista de colunas a formatar como número (sobrescreve auto-detect)

    Returns:
        DataFrame formatado (cópia do original)
    """
    if df is None or df.empty:
        return df

    # Criar cópia para não modificar o original
    df_formatted = df.copy()

    # Detectar colunas automaticamente se necessário
    if auto_detect:
        detected_currency = detect_currency_columns(df_formatted)
        detected_numbers = detect_number_columns(df_formatted)

        # Usar colunas detectadas se não foram especificadas manualmente
        if currency_cols is None:
            currency_cols = detected_currency
        if number_cols is None:
            number_cols = detected_numbers

    # Aplicar formatação de moeda
    if currency_cols:
        for col in currency_cols:
            if col in df_formatted.columns:
                try:
                    df_formatted[col] = df_formatted[col].apply(format_currency_value)
                    logger.info(f"✅ Coluna '{col}' formatada como moeda")
                except Exception as e:
                    logger.warning(f"Erro ao formatar coluna '{col}' como moeda: {e}")

    # Aplicar formatação de número
    if number_cols:
        for col in number_cols:
            if col in df_formatted.columns:
                try:
                    df_formatted[col] = df_formatted[col].apply(lambda x: format_number_value(x, decimals=2))
                    logger.info(f"✅ Coluna '{col}' formatada como número")
                except Exception as e:
                    logger.warning(f"Erro ao formatar coluna '{col}' como número: {e}")

    return df_formatted


def create_download_csv(df, filename_prefix="export"):
    """
    Cria um CSV formatado para download

    Args:
        df: DataFrame pandas
        filename_prefix: Prefixo do nome do arquivo

    Returns:
        Tupla (dados_csv, nome_arquivo)
    """
    from datetime import datetime

    # Formatar DataFrame
    df_formatted = format_dataframe_for_display(df)

    # Gerar nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M")
    filename = f"{timestamp}_{filename_prefix}.csv"

    # Converter para CSV
    csv_data = df_formatted.to_csv(index=False, encoding='utf-8-sig')

    return csv_data, filename


# Mapeamento de colunas conhecidas para formatação
KNOWN_CURRENCY_COLUMNS = {
    'VENDA_30DD', 'LIQUIDO_38', 'PRECO', 'CUSTO', 'VALOR',
    'venda_30_d', 'preco_38_percent', 'liquido', 'bruto',
    'mes_01', 'mes_02', 'mes_03', 'mes_04', 'mes_05', 'mes_06',
    'mes_07', 'mes_08', 'mes_09', 'mes_10', 'mes_11', 'mes_12'
}

KNOWN_NUMBER_COLUMNS = {
    'ESTOQUE_UNE', 'estoque_atual', 'quantidade', 'qtd'
}


if __name__ == "__main__":
    # Teste
    import pandas as pd

    test_df = pd.DataFrame({
        'NOMESEGMENTO': ['PAPELARIA', 'TECIDOS'],
        'VENDA_30DD': [101868.644, 77328.702],
        'ESTOQUE_UNE': [1500, 2300]
    })

    print("DataFrame original:")
    print(test_df)

    print("\nDataFrame formatado:")
    formatted = format_dataframe_for_display(test_df)
    print(formatted)

    print("\nCSV gerado:")
    csv_data, filename = create_download_csv(test_df, "teste")
    print(f"Arquivo: {filename}")
    print(csv_data[:200])
