"""
Ferramentas de Metadados e Introspecção
Permite ao Agente "conhecer" os dados antes de consultá-los.
FIX 2026-01-17: Migrado para usar column_mapping.py expandido (97 colunas) dinamicamente.
"""

from langchain_core.tools import tool
import logging
from typing import Dict, Any, List, Optional
from app.core.data_source_manager import get_data_manager

logger = logging.getLogger(__name__)


def _get_column_dictionary() -> Dict[str, str]:
    """
    Carrega o dicionário de colunas dinamicamente do column_mapping.py.
    Garante que sempre use a versão mais atualizada (97 colunas).
    """
    from app.infrastructure.data.config.column_mapping import list_all_columns
    
    all_columns = list_all_columns()
    return {name: desc for name, desc in all_columns}


@tool
def consultar_dicionario_dados(termo_busca: Optional[str] = None) -> Dict[str, Any]:
    """
    Consulta o dicionário de dados completo do Data Lake.
    Use SEMPRE que precisar saber quais colunas existem e o que significam.
    
    IMPORTANTE: Use esta ferramenta ANTES de fazer consultas complexas!
    
    Args:
        termo_busca: (Opcional) Palavra-chave para filtrar colunas.
                     Exemplos: "venda", "estoque", "mes", "custo", "abc", "logistica"
                     Se vazio, retorna categorias principais.
                      
    Returns:
        Lista de colunas com descrições semânticas.
        
    Exemplos de uso:
        - consultar_dicionario_dados("mes") -> Retorna colunas de histórico mensal
        - consultar_dicionario_dados("venda") -> Retorna colunas de vendas
        - consultar_dicionario_dados("estoque") -> Retorna colunas de estoque
        - consultar_dicionario_dados("picklist") -> Retorna colunas de logística
    """
    try:
        # Carregar dicionário atualizado dinamicamente
        COLUMN_DICTIONARY = _get_column_dictionary()
        
        manager = get_data_manager()
        info = manager.get_source_info()
        
        if "status" in info and info["status"] == "sem_dados":
            return {"erro": "Não foi possível acessar os metadados."}
            
        all_columns = info.get("columns", [])
        
        # Se não tem termo de busca, retornar colunas por categoria
        if not termo_busca:
            categorias = {
                "📊 VENDAS MENSAIS (para previsões e tendências)": [
                    "MES_12", "MES_11", "MES_10", "MES_09", "MES_08", "MES_07", 
                    "MES_06", "MES_05", "MES_04", "MES_03", "MES_02", "MES_01", "MES_PARCIAL"
                ],
                "📈 VENDAS SEMANAIS": [
                    "SEMANA_ANTERIOR_5", "SEMANA_ANTERIOR_4", "SEMANA_ANTERIOR_3", 
                    "SEMANA_ANTERIOR_2", "SEMANA_ATUAL", "VENDA_30DD"
                ],
                "📦 ESTOQUE (detalhado)": [
                    "ESTOQUE_CD", "ESTOQUE_UNE", "ESTOQUE_LV", "ESTOQUE_GONDOLA_LV", 
                    "ESTOQUE_ILHA_LV", "EXPOSICAO_MINIMA_UNE", "EXPOSICAO_MAXIMA_UNE"
                ],
                "💰 PREÇOS E CUSTOS": [
                    "LIQUIDO_38", "ULTIMA_ENTRADA_CUSTO_CD", "QTDE_EMB_MASTER", "QTDE_EMB_MULTIPLO"
                ],
                "🏷️ CLASSIFICAÇÃO": [
                    "NOMESEGMENTO", "NOMECATEGORIA", "NOMEGRUPO", "NOMESUBGRUPO", 
                    "NOMEFABRICANTE", "ABC_UNE_30DD", "ABC_CACULA_90DD"
                ],
                "🚚 LOGÍSTICA (movimentação)": [
                    "SOLICITACAO_PENDENTE", "PICKLIST", "ROMANEIO_SOLICITACAO", 
                    "NOTA", "ULTIMA_ENTRADA_DATA_CD", "ULTIMA_VENDA_DATA_UNE"
                ],
                "📍 IDENTIFICAÇÃO": [
                    "UNE", "UNE_NOME", "PRODUTO", "NOME", "EAN"
                ]
            }
            
            resultado = {
                "total_colunas": len(all_columns),
                "total_documentadas": len(COLUMN_DICTIONARY),
                "categorias": categorias,
                "instrucoes": (
                    "Para análises de previsão, use as colunas MES_* (histórico de 12 meses). "
                    "Para vendas recentes, use VENDA_30DD. "
                    "Para logística, consulte PICKLIST, ROMANEIO, SOLICITACAO_PENDENTE."
                )
            }
            return resultado
            
        # Filtragem com descrições semânticas
        termo = termo_busca.lower()
        matches = []
        
        for col in all_columns:
            descricao = COLUMN_DICTIONARY.get(col, "")
            if termo in col.lower() or termo in descricao.lower():
                matches.append({
                    "coluna": col,
                    "descricao": COLUMN_DICTIONARY.get(col, "Sem descrição disponível")
                })
                
        if not matches:
            return {
                "mensagem": f"Nenhuma coluna encontrada contendo '{termo_busca}'.",
                "sugestao": "Tente: 'venda', 'estoque', 'mes', 'custo', 'abc', 'preco', 'logistica', 'picklist'"
            }
            
        return {
            "termo_buscado": termo_busca,
            "total_encontrado": len(matches),
            "resultados": matches[:20]  # Limitar a 20 resultados para evitar overflow
        }

    except Exception as e:
        logger.error(f"Erro ao consultar dicionário: {e}", exc_info=True)
        return {"erro": str(e)}


# Nova ferramenta para análise de histórico de vendas
@tool 
def analisar_historico_vendas(
    codigo_produto: Optional[int] = None,
    codigo_une: Optional[int] = None
) -> Dict[str, Any]:
    """
    Analisa o histórico de vendas de um produto para previsões.
    
    Use esta ferramenta para:
    - Calcular tendência de vendas
    - Fazer previsão para próximos 30 dias
    - Identificar sazonalidade
    
    Args:
        codigo_produto: Código SKU do produto (obrigatório para análise específica)
        codigo_une: Código da loja (opcional, se vazio analisa todas as lojas)
        
    Returns:
        Análise com histórico, tendência, média e previsão estimada.
    """
    try:
        import pandas as pd
        import numpy as np
        
        manager = get_data_manager()
        df = manager.get_data()
        
        if hasattr(df, 'to_pandas'):
            df = df.to_pandas()
        elif hasattr(df, 'df'):
            df = df.df()
        
        if df is None or df.empty:
            return {"erro": "Dados não disponíveis"}
        
        # Aplicar filtros
        if codigo_produto:
            df['PRODUTO'] = pd.to_numeric(df['PRODUTO'], errors='coerce')
            df = df[df['PRODUTO'] == codigo_produto]
            
        if codigo_une:
            df['UNE'] = pd.to_numeric(df['UNE'], errors='coerce')
            df = df[df['UNE'] == codigo_une]
            
        if df.empty:
            return {
                "erro": f"Produto {codigo_produto} não encontrado" + (f" na UNE {codigo_une}" if codigo_une else ""),
                "sugestao": "Verifique se o código do produto está correto"
            }
        
        # Extrair histórico mensal
        meses = ['MES_12', 'MES_11', 'MES_10', 'MES_09', 'MES_08', 'MES_07', 
                 'MES_06', 'MES_05', 'MES_04', 'MES_03', 'MES_02', 'MES_01']
        
        historico = {}
        for i, mes in enumerate(meses):
            if mes in df.columns:
                valor = pd.to_numeric(df[mes], errors='coerce').sum()
                historico[f"mes_{12-i}"] = int(valor) if not pd.isna(valor) else 0
        
        # Calcular métricas
        valores = list(historico.values())
        
        if not valores or all(v == 0 for v in valores):
            return {
                "produto": codigo_produto,
                "une": codigo_une,
                "historico": historico,
                "analise": "Sem vendas no período analisado (12 meses)",
                "previsao_30_dias": 0
            }
        
        media_mensal = sum(valores) / len(valores) if valores else 0
        media_ultimos_3 = sum(valores[-3:]) / 3 if len(valores) >= 3 else media_mensal
        
        # Tendência simples (últimos 3 meses vs 3 meses anteriores)
        if len(valores) >= 6:
            media_recente = sum(valores[-3:]) / 3
            media_anterior = sum(valores[-6:-3]) / 3
            if media_anterior > 0:
                tendencia_pct = ((media_recente - media_anterior) / media_anterior) * 100
            else:
                tendencia_pct = 0
        else:
            tendencia_pct = 0
        
        # Previsão para próximos 30 dias (média ponderada dos últimos 3 meses)
        previsao = int(media_ultimos_3)
        
        # Venda atual (30 dias)
        venda_30dd = 0
        if 'VENDA_30DD' in df.columns:
            venda_30dd = int(pd.to_numeric(df['VENDA_30DD'], errors='coerce').sum())
        
        # Nome do produto
        nome = df['NOME'].iloc[0] if 'NOME' in df.columns else "Produto"
        
        # Determinar tendência textual
        if tendencia_pct > 10:
            tendencia_texto = "📈 Crescimento"
        elif tendencia_pct < -10:
            tendencia_texto = "📉 Queda"
        else:
            tendencia_texto = "➡️ Estável"
        
        return {
            "produto": {
                "codigo": codigo_produto,
                "nome": nome,
                "une": codigo_une if codigo_une else "Todas"
            },
            "historico_mensal": historico,
            "metricas": {
                "media_mensal_12m": round(media_mensal, 1),
                "media_ultimos_3m": round(media_ultimos_3, 1),
                "venda_atual_30dd": venda_30dd,
                "tendencia_percentual": round(tendencia_pct, 1),
                "tendencia": tendencia_texto
            },
            "previsao": {
                "proximos_30_dias": previsao,
                "metodo": "Média móvel ponderada (últimos 3 meses)",
                "confianca": "Média" if len([v for v in valores if v > 0]) >= 6 else "Baixa (histórico insuficiente)"
            },
            "recomendacao": f"Baseado no histórico, o produto deve vender aproximadamente {previsao} unidades nos próximos 30 dias."
        }
        
    except Exception as e:
        logger.error(f"Erro ao analisar histórico: {e}", exc_info=True)
        return {"erro": str(e)}
