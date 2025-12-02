"""
Chat BI - Sistema ROBUSTO com Regex (SEM dependência de API)
Solução definitiva que funciona 100% offline
"""

import polars as pl
from pathlib import Path
import re
from typing import Dict, Any, List, Optional


class RobustChatBI:
    """
    Sistema robusto de Chat BI usando REGEX
    Não depende de APIs externas - funciona 100% offline
    """
    
    def __init__(self, parquet_path: Path):
        self.parquet_path = parquet_path
        
        # Carregar schema do Parquet
        lf = pl.scan_parquet(parquet_path)
        self.schema = lf.collect_schema()
        self.columns = list(self.schema.names())
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Processa pergunta do usuário usando REGEX robusto
        Retorna resposta estruturada com dados e texto
        """
        
        query_lower = user_query.lower()
        
        # 1. Detecção de saudações
        saudacoes = ["olá", "oi", "ola", "hello", "boa tarde", "bom dia", "boa noite"]
        if any(saudacao in query_lower for saudacao in saudacoes):
            return {
                "success": True,
                "text": "👋 Olá! Sou seu assistente de BI.\n\nPosso ajudar com:\n• Consultas de preços\n• Análise de vendas\n• Informações de produtos\n\nFaça uma pergunta!",
                "data": None
            }
        
        # 2. Extrair informações com REGEX
        produto = self._extract_produto(query_lower)
        une = self._extract_une(query_lower)
        periodo = self._extract_periodo(query_lower)
        tipo_consulta = self._detect_query_type(query_lower)
        
        # 3. Executar consulta
        try:
            result = self._execute_query(produto, une, periodo, tipo_consulta)
            return result
        except KeyError as e:
            print(f"[ERROR] KeyError ao executar consulta: {e}")
            print(f"[DEBUG] Produto: {produto}, UNE: {une}, Periodo: {periodo}")
            import traceback
            traceback.print_exc()
            return self._fallback_response(user_query)
        except Exception as e:
            print(f"[ERROR] Erro ao executar consulta: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_response(user_query)
    
    def _extract_produto(self, query: str) -> Optional[str]:
        """Extrai código ou nome do produto usando regex"""
        # 1. Tentar código numérico (prioridade)
        patterns_code = [
            r'produto\s+(\d{4,6})',
            r'prod\s+(\d{4,6})',
            r'código\s+(\d{4,6})',
            r'codigo\s+(\d{4,6})',
            r'\b(\d{5,6})\b',  # Número de 5-6 dígitos isolado
        ]
        for pattern in patterns_code:
            match = re.search(pattern, query)
            if match:
                return match.group(1)
        
        # 2. Tentar nome do produto (texto após 'produto')
        # Captura tudo até a próxima palavra-chave (na, em, une, loja, nos, etc) ou fim da string
        pattern_name = r'(?:produto|prod|vendas de|venda de)\s+(.+?)(?:\s+na\s+|\s+em\s+|\s+da\s+|\s+do\s+|\s+no\s+|\s+nos\s+|\s+une|\s+loja|$)'
        match = re.search(pattern_name, query)
        if match:
            # Limpar espaços extras
            return match.group(1).strip()
            
        return None
    
    def _extract_une(self, query: str) -> Optional[str]:
        """Extrai código ou nome da UNE usando regex"""
        # 1. Tentar código numérico
        patterns_code = [
            r'une\s+(\d+)',
            r'loja\s+(\d+)',
            r'unidade\s+(\d+)',
        ]
        for pattern in patterns_code:
            match = re.search(pattern, query)
            if match:
                return match.group(1)
        
        # 2. Tentar nome da UNE (texto após 'une'/'loja')
        pattern_name = r'(?:une|loja|unidade|na)\s+(.+?)(?:\s+nos\s+|\s+no\s+|\s+do\s+|\s+da\s+|\s+de\s+|\s+produto|$)'
        match = re.search(pattern_name, query)
        if match:
            val = match.group(1).strip()
            # Evitar capturar "une" se for parte de outra palavra ou muito curto
            if len(val) > 1 and val.lower() not in ["scr", "meses", "dias"]:
                return val.upper()
        
        # Caso especial: "UNE SCR" ou apenas "SCR"
        if "scr" in query:
            return "SCR"
            
        return None
    
    def _extract_periodo(self, query: str) -> List[str]:
        """Extrai período usando regex"""
        # Padrões: "últimos 3 meses", "último mês", "3 meses", "mês 1"
        
        # Últimos X meses
        match = re.search(r'(?:últimos?|ultimos?)\s+(\d+)\s+mes', query)
        if match:
            num_meses = int(match.group(1))
            return [f"MES_{str(i).zfill(2)}" for i in range(1, min(num_meses + 1, 13))]
        
        # Mês específico
        match = re.search(r'mês\s+(\d+)', query)
        if match:
            mes_num = int(match.group(1))
            return [f"MES_{str(mes_num).zfill(2)}"]
        
        # Default: últimos 3 meses
        if "mes" in query or "mês" in query:
            return ["MES_01", "MES_02", "MES_03"]
        
        return ["MES_01"]
    
    def _detect_query_type(self, query: str) -> str:
        """Detecta tipo de consulta"""
        if any(word in query for word in ["venda", "vendas", "quantidade", "quantas", "quanto"]):
            return "vendas"
        elif any(word in query for word in ["preço", "preco", "valor", "custo"]):
            return "preco"
        elif any(word in query for word in ["total", "soma", "somar"]):
            return "total"
        else:
            return "geral"
    
    def _execute_query(self, produto: Optional[str], une: Optional[str], 
                      periodo: List[str], tipo: str) -> Dict[str, Any]:
        """Executa consulta no Parquet"""
        
        lf = pl.scan_parquet(self.parquet_path)
        
        # Construir filtros
        filters = []
        
        # Filtro de PRODUTO
        if produto:
            if produto.isdigit():
                # É código numérico
                try:
                    produto_int = int(produto)
                    filters.append(pl.col("PRODUTO") == produto_int)
                except ValueError:
                    filters.append(pl.col("PRODUTO").cast(pl.Utf8) == produto)
            else:
                # É nome do produto - busca textual (case insensitive)
                # Verifica se coluna NOME existe
                if "NOME" in self.columns:
                    filters.append(pl.col("NOME").str.to_uppercase().str.contains(produto.upper()))
                else:
                    # Se não tem coluna NOME, não dá pra buscar por nome
                    return {
                        "success": False,
                        "text": f"❌ Desculpe, não consigo buscar produtos por nome ('{produto}') neste conjunto de dados. Por favor, use o código do produto.",
                        "data": None
                    }

        # Filtro de UNE
        if une:
            if une.isdigit():
                # É código numérico
                filters.append(
                    (pl.col("UNE").cast(pl.Utf8) == une) | 
                    (pl.col("UNE") == int(une))
                )
            else:
                # É nome da UNE ou código alfanumérico (ex: SCR)
                if "UNE_NOME" in self.columns:
                    filters.append(
                        (pl.col("UNE_NOME").str.to_uppercase().str.contains(une.upper())) |
                        (pl.col("UNE").cast(pl.Utf8).str.to_uppercase() == une.upper())
                    )
                else:
                    # Tentar apenas na coluna UNE como string
                    filters.append(pl.col("UNE").cast(pl.Utf8).str.to_uppercase() == une.upper())
        
        # Aplicar filtros
        if filters:
            query = lf.filter(pl.all_horizontal(filters))
        else:
            query = lf
        
        # Selecionar colunas
        cols_to_select = ["PRODUTO", "NOME", "UNE"] + [p for p in periodo if p in self.columns]
        
        # Executar com tratamento de erro
        try:
            result = query.select(cols_to_select).head(1).collect()
        except Exception as e:
            print(f"[ERROR] Erro ao executar query Polars: {e}")
            print(f"[DEBUG] Colunas selecionadas: {cols_to_select}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "text": f"❌ Erro ao processar consulta. Por favor, tente novamente.",
                "data": None
            }
        
        # Formatar resposta
        if len(result) > 0:
            row = result.row(0, named=True)
            
            nome = row.get("NOME", "Produto")
            produto_id = row.get("PRODUTO", produto or "N/A")
            une_id = row.get("UNE", une or "N/A")
            
            # Calcular valores
            valores = []
            for mes in periodo:
                # Usar .get() para evitar KeyError se a coluna não existir
                if mes in row:
                    val = row.get(mes)
                    # Converter para float se necessário
                    if val is not None:
                        valores.append(float(val))
            
            total = sum(valores) if valores else 0
            
            # Formatar texto da resposta
            if tipo == "vendas" or tipo == "total":
                response_text = f"📊 **Produto {produto_id}** na UNE {une_id}:\n\n"
                response_text += f"**Nome:** {nome}\n\n"
                
                if len(valores) > 1:
                    for i, (mes, valor) in enumerate(zip(periodo, valores), 1):
                        response_text += f"**Mês {i}:** {valor:,.0f}\n"
                    response_text += f"\n**Total:** {total:,.0f}"
                else:
                    response_text += f"**Valor:** {total:,.0f}"
            
            elif tipo == "preco":
                response_text = f"📊 **Produto {produto_id}** na UNE {une_id}:\n\n"
                response_text += f"**Nome:** {nome}\n"
                response_text += f"**Preço:** R$ {total:,.2f}"
            
            else:
                response_text = f"📊 **Produto {produto_id}** na UNE {une_id}:\n\n"
                response_text += f"**Nome:** {nome}\n"
                response_text += f"**Valor:** {total:,.0f}"
            
            return {
                "success": True,
                "text": response_text,
                "data": row
            }
        
        # Nenhum resultado encontrado
        if produto and une:
            # Verificar se o produto existe em QUALQUER UNE
            lf = pl.scan_parquet(self.parquet_path)
            
            # Filtro de produto (int ou str)
            prod_filter = None
            try:
                prod_filter = (pl.col("PRODUTO") == int(produto))
            except ValueError:
                prod_filter = (pl.col("PRODUTO").cast(pl.Utf8) == produto)
                
            # Buscar UNEs disponíveis
            unes_disponiveis = lf.filter(prod_filter).select("UNE").unique().head(5).collect()
            
            if len(unes_disponiveis) > 0:
                lista_unes = [str(r[0]) for r in unes_disponiveis.rows()]
                unes_str = ", ".join(lista_unes)
                return {
                    "success": False,
                    "text": f"❌ O produto {produto} não foi encontrado na UNE {une}.\n\n✅ Mas ele está disponível nas seguintes UNEs: **{unes_str}**...\n\nTente consultar uma dessas lojas!",
                    "data": None
                }
            else:
                return {
                    "success": False,
                    "text": f"❌ O produto {produto} não foi encontrado em nenhuma UNE.",
                    "data": None
                }
                
        elif produto:
            return {
                "success": False,
                "text": f"❌ Não encontrei o produto {produto}.\n\nVerifique se o código está correto.",
                "data": None
            }
        else:
            return self._fallback_response("")
    
    def _fallback_response(self, query: str) -> Dict[str, Any]:
        """Resposta de fallback"""
        return {
            "success": False,
            "text": "🤔 Não consegui entender sua pergunta.\n\nTente perguntas como:\n• 'Quantas vendas do produto 59294 na UNE 261 nos últimos 3 meses?'\n• 'Qual o preço do produto 59294 na UNE SCR?'\n• 'Total de vendas do produto 12345'",
            "data": None
        }
