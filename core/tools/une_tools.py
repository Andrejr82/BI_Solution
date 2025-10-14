"""
Ferramentas LangChain para operações UNE.
Implementa regras de abastecimento, MC e política de preços.

Este módulo fornece ferramentas para:
- Cálculo de necessidades de abastecimento por UNE
- Consulta de MC (Média Comum) de produtos
- Cálculo de preços finais aplicando política de preços UNE
"""

from langchain_core.tools import tool
import pandas as pd
import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Path do arquivo Parquet com dados estendidos
PARQUET_PATH = os.path.join(os.getcwd(), "data", "parquet", "admmat_extended.parquet")


@tool
def calcular_abastecimento_une(une_id: int, segmento: str = None) -> Dict[str, Any]:
    """
    Calcula produtos que precisam de abastecimento em uma UNE.

    Regra aplicada: ESTOQUE_UNE <= 50% LINHA_VERDE

    Args:
        une_id: ID da UNE (1-10)
        segmento: Filtro opcional por segmento (ex: "TECIDOS", "PAPELARIA")

    Returns:
        dict com:
        - total_produtos: int (total de produtos que precisam abastecimento)
        - produtos: list[dict] (top 20 produtos ordenados por qtd_a_abastecer DESC)
        - regra_aplicada: str (descrição da regra de abastecimento)
        - une_id: int
        - segmento: str (se aplicado)

    Example:
        >>> result = calcular_abastecimento_une(une_id=1, segmento="TECIDOS")
        >>> print(f"Total produtos: {result['total_produtos']}")
    """
    try:
        # Validação de inputs
        if not isinstance(une_id, int) or une_id <= 0:
            return {"error": "une_id deve ser um inteiro positivo"}

        if not os.path.exists(PARQUET_PATH):
            return {"error": f"Arquivo não encontrado: {PARQUET_PATH}"}

        # Carregar dados do Parquet
        logger.info(f"Carregando dados de abastecimento para UNE {une_id}")
        df = pd.read_parquet(PARQUET_PATH)

        # Filtrar por UNE
        df_une = df[df['une'] == une_id].copy()

        if df_une.empty:
            return {
                "error": f"Nenhum produto encontrado para UNE {une_id}",
                "une_id": une_id
            }

        # Filtrar por segmento (se fornecido)
        if segmento:
            if 'nomesegmento' in df_une.columns:
                df_une = df_une[
                    df_une['nomesegmento'].str.contains(segmento, case=False, na=False)
                ]
                if df_une.empty:
                    return {
                        "error": f"Nenhum produto encontrado para segmento '{segmento}' na UNE {une_id}",
                        "une_id": une_id,
                        "segmento": segmento
                    }
            else:
                logger.warning("Coluna 'nomesegmento' não encontrada no dataset")

        # Filtrar produtos que precisam abastecimento
        if 'precisa_abastecimento' not in df_une.columns:
            return {"error": "Coluna 'precisa_abastecimento' não encontrada no dataset"}

        df_abastecer = df_une[df_une['precisa_abastecimento'] == True].copy()

        total_produtos = len(df_abastecer)

        if total_produtos == 0:
            return {
                "total_produtos": 0,
                "produtos": [],
                "regra_aplicada": "ESTOQUE_UNE <= 50% LINHA_VERDE",
                "une_id": une_id,
                "segmento": segmento if segmento else "Todos",
                "mensagem": "Nenhum produto precisa de abastecimento no momento"
            }

        # Ordenar por qtd_a_abastecer DESC e pegar top 20
        df_abastecer = df_abastecer.sort_values('qtd_a_abastecer', ascending=False)
        top_20 = df_abastecer.head(20)

        # Preparar lista de produtos
        produtos = []
        for _, row in top_20.iterrows():
            produto = {
                "codigo": int(row['codigo']) if pd.notna(row['codigo']) else None,
                "nome_produto": str(row['nome_produto']) if pd.notna(row['nome_produto']) else "N/A",
                "segmento": str(row['nomesegmento']) if 'nomesegmento' in row and pd.notna(row['nomesegmento']) else "N/A",
                "estoque_atual": float(row['estoque_atual']) if pd.notna(row['estoque_atual']) else 0.0,
                "linha_verde": float(row['linha_verde']) if pd.notna(row['linha_verde']) else 0.0,
                "qtd_a_abastecer": float(row['qtd_a_abastecer']) if pd.notna(row['qtd_a_abastecer']) else 0.0,
                "percentual_estoque": round((float(row['estoque_atual']) / float(row['linha_verde']) * 100), 2) if pd.notna(row['linha_verde']) and row['linha_verde'] > 0 else 0.0
            }
            produtos.append(produto)

        logger.info(f"Encontrados {total_produtos} produtos para abastecimento na UNE {une_id}")

        return {
            "total_produtos": total_produtos,
            "produtos": produtos,
            "regra_aplicada": "ESTOQUE_UNE <= 50% LINHA_VERDE",
            "une_id": une_id,
            "segmento": segmento if segmento else "Todos"
        }

    except Exception as e:
        logger.error(f"Erro em calcular_abastecimento_une: {e}", exc_info=True)
        return {"error": f"Erro ao calcular abastecimento: {str(e)}"}


@tool
def calcular_mc_produto(produto_id: int, une_id: int) -> Dict[str, Any]:
    """
    Retorna informações de MC (Média Comum) de um produto em uma UNE específica.

    A MC representa a média de vendas do produto, usada para dimensionar
    o estoque adequado em gôndola.

    Args:
        produto_id: Código do produto
        une_id: ID da UNE (1-10)

    Returns:
        dict com:
        - produto_id: int
        - nome: str
        - segmento: str
        - mc_calculada: float (Média Comum)
        - estoque_atual: float
        - linha_verde: float (estoque máximo)
        - estoque_gondola: float (se existir na base)
        - percentual_linha_verde: float (% do estoque em relação à linha verde)
        - recomendacao: str (orientação de abastecimento)

    Example:
        >>> result = calcular_mc_produto(produto_id=12345, une_id=1)
        >>> print(f"MC: {result['mc_calculada']}, Recomendação: {result['recomendacao']}")
    """
    try:
        # Validação de inputs
        if not isinstance(produto_id, int) or produto_id <= 0:
            return {"error": "produto_id deve ser um inteiro positivo"}

        if not isinstance(une_id, int) or une_id <= 0:
            return {"error": "une_id deve ser um inteiro positivo"}

        if not os.path.exists(PARQUET_PATH):
            return {"error": f"Arquivo não encontrado: {PARQUET_PATH}"}

        # Carregar dados do Parquet
        logger.info(f"Buscando MC do produto {produto_id} na UNE {une_id}")
        df = pd.read_parquet(PARQUET_PATH)

        # Filtrar por produto e UNE
        produto_df = df[(df['codigo'] == produto_id) & (df['une'] == une_id)]

        if produto_df.empty:
            return {
                "error": f"Produto {produto_id} não encontrado na UNE {une_id}",
                "produto_id": produto_id,
                "une_id": une_id
            }

        # Pegar primeira linha (deve ser única)
        row = produto_df.iloc[0]

        # Extrair dados
        mc_calculada = float(row['mc']) if pd.notna(row['mc']) else 0.0
        estoque_atual = float(row['estoque_atual']) if pd.notna(row['estoque_atual']) else 0.0
        linha_verde = float(row['linha_verde']) if pd.notna(row['linha_verde']) else 0.0

        # Estoque gôndola (se existir)
        estoque_gondola = None
        if 'ESTOQUE_GONDOLA' in row:
            estoque_gondola = float(row['ESTOQUE_GONDOLA']) if pd.notna(row['ESTOQUE_GONDOLA']) else 0.0
        elif 'estoque_gondola' in row:
            estoque_gondola = float(row['estoque_gondola']) if pd.notna(row['estoque_gondola']) else 0.0

        # Calcular percentual da linha verde
        percentual_linha_verde = 0.0
        if linha_verde > 0:
            percentual_linha_verde = round((estoque_atual / linha_verde) * 100, 2)

        # Gerar recomendação
        recomendacao = "Manter estoque atual"

        if estoque_gondola is not None and mc_calculada > estoque_gondola:
            recomendacao = "Aumentar ESTOQUE em gôndola - MC superior ao estoque atual"
        elif percentual_linha_verde < 50:
            recomendacao = "URGENTE: Abastecer produto - Estoque abaixo de 50% da linha verde"
        elif percentual_linha_verde < 75:
            recomendacao = "ATENÇÃO: Planejar abastecimento - Estoque entre 50% e 75% da linha verde"
        elif percentual_linha_verde > 100:
            recomendacao = "ALERTA: Estoque acima da linha verde - Verificar dimensionamento"

        resultado = {
            "produto_id": int(produto_id),
            "une_id": int(une_id),
            "nome": str(row['nome_produto']) if pd.notna(row['nome_produto']) else "N/A",
            "segmento": str(row['nomesegmento']) if 'nomesegmento' in row and pd.notna(row['nomesegmento']) else "N/A",
            "mc_calculada": mc_calculada,
            "estoque_atual": estoque_atual,
            "linha_verde": linha_verde,
            "percentual_linha_verde": percentual_linha_verde,
            "recomendacao": recomendacao
        }

        # Adicionar estoque_gondola se existir
        if estoque_gondola is not None:
            resultado["estoque_gondola"] = estoque_gondola

        logger.info(f"MC calculada para produto {produto_id}: {mc_calculada}")

        return resultado

    except Exception as e:
        logger.error(f"Erro em calcular_mc_produto: {e}", exc_info=True)
        return {"error": f"Erro ao calcular MC do produto: {str(e)}"}


@tool
def calcular_preco_final_une(valor_compra: float, ranking: int, forma_pagamento: str) -> Dict[str, Any]:
    """
    Calcula preço final aplicando política de preços UNE.

    Regras de Tipo de Preço:
    - Valor >= R$ 750,00 → Preço Atacado
    - Valor < R$ 750,00 → Preço Varejo

    Política por Ranking:
    - Ranking 0: Atacado 38%, Varejo 30%
    - Ranking 1: Preço único 38% (independente do valor)
    - Ranking 2: Atacado 38%, Varejo 30%
    - Ranking 3: Sem desconto (preço tabela)
    - Ranking 4: Atacado 38%, Varejo 24%

    Desconto por Forma de Pagamento:
    - 'vista': 38%
    - '30d': 36%
    - '90d': 34%
    - '120d': 30%

    Args:
        valor_compra: Valor total da compra em reais
        ranking: Classificação do produto (0-4)
        forma_pagamento: Tipo de pagamento ('vista', '30d', '90d', '120d')

    Returns:
        dict com:
        - valor_original: float
        - tipo: str ("Atacado" ou "Varejo")
        - ranking: int
        - desconto_ranking: str (percentual aplicado pelo ranking)
        - forma_pagamento: str
        - desconto_pagamento: str (percentual por forma de pagamento)
        - preco_final: float
        - economia: float (valor economizado)
        - detalhamento: str (explicação do cálculo)

    Example:
        >>> result = calcular_preco_final_une(valor_compra=1000.0, ranking=0, forma_pagamento='vista')
        >>> print(f"Preço final: R$ {result['preco_final']:.2f}")
    """
    try:
        # Validação de inputs
        if not isinstance(valor_compra, (int, float)) or valor_compra <= 0:
            return {"error": "valor_compra deve ser um número positivo"}

        if not isinstance(ranking, int) or ranking < 0 or ranking > 4:
            return {"error": "ranking deve ser um inteiro entre 0 e 4"}

        formas_validas = ['vista', '30d', '90d', '120d']
        if forma_pagamento not in formas_validas:
            return {"error": f"forma_pagamento deve ser uma das opções: {', '.join(formas_validas)}"}

        valor_original = float(valor_compra)

        # Determinar tipo de preço (Atacado ou Varejo)
        tipo_preco = "Atacado" if valor_compra >= 750.0 else "Varejo"

        # Definir desconto por ranking
        desconto_ranking_percent = 0.0

        if ranking == 0:
            desconto_ranking_percent = 38.0 if tipo_preco == "Atacado" else 30.0
        elif ranking == 1:
            desconto_ranking_percent = 38.0  # Preço único
            tipo_preco = "Único"  # Override para ranking 1
        elif ranking == 2:
            desconto_ranking_percent = 38.0 if tipo_preco == "Atacado" else 30.0
        elif ranking == 3:
            desconto_ranking_percent = 0.0  # Sem desconto
        elif ranking == 4:
            desconto_ranking_percent = 38.0 if tipo_preco == "Atacado" else 24.0

        # Aplicar desconto do ranking
        valor_apos_ranking = valor_original * (1 - desconto_ranking_percent / 100)

        # Definir desconto por forma de pagamento
        descontos_pagamento = {
            'vista': 38.0,
            '30d': 36.0,
            '90d': 34.0,
            '120d': 30.0
        }

        desconto_pagamento_percent = descontos_pagamento[forma_pagamento]

        # Aplicar desconto de forma de pagamento sobre o valor após desconto de ranking
        valor_final = valor_apos_ranking * (1 - desconto_pagamento_percent / 100)

        # Calcular economia total
        economia = valor_original - valor_final

        # Gerar detalhamento do cálculo
        detalhamento_partes = [
            f"Valor original: R$ {valor_original:.2f}",
            f"Tipo de preço: {tipo_preco} (valor {'>=' if valor_compra >= 750 else '<'} R$ 750,00)"
        ]

        if desconto_ranking_percent > 0:
            detalhamento_partes.append(
                f"Desconto ranking {ranking}: {desconto_ranking_percent}% -> R$ {valor_apos_ranking:.2f}"
            )
        else:
            detalhamento_partes.append(
                f"Ranking {ranking}: Sem desconto (preço tabela)"
            )

        detalhamento_partes.append(
            f"Desconto pagamento ({forma_pagamento}): {desconto_pagamento_percent}% -> R$ {valor_final:.2f}"
        )
        detalhamento_partes.append(
            f"Economia total: R$ {economia:.2f} ({(economia/valor_original)*100:.2f}%)"
        )

        detalhamento = " | ".join(detalhamento_partes)

        logger.info(
            f"Preço calculado: R$ {valor_original:.2f} -> R$ {valor_final:.2f} "
            f"(Ranking {ranking}, {forma_pagamento})"
        )

        return {
            "valor_original": round(valor_original, 2),
            "tipo": tipo_preco,
            "ranking": ranking,
            "desconto_ranking": f"{desconto_ranking_percent}%" if desconto_ranking_percent > 0 else "Sem desconto",
            "forma_pagamento": forma_pagamento,
            "desconto_pagamento": f"{desconto_pagamento_percent}%",
            "preco_final": round(valor_final, 2),
            "economia": round(economia, 2),
            "percentual_economia": round((economia / valor_original) * 100, 2),
            "detalhamento": detalhamento
        }

    except Exception as e:
        logger.error(f"Erro em calcular_preco_final_une: {e}", exc_info=True)
        return {"error": f"Erro ao calcular preço final: {str(e)}"}


# Lista de ferramentas disponíveis para exportação
__all__ = [
    'calcular_abastecimento_une',
    'calcular_mc_produto',
    'calcular_preco_final_une'
]
