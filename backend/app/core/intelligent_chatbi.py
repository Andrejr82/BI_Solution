"""
Chat BI - Sistema Inteligente com Gemini
Solução definitiva para processar perguntas em linguagem natural
"""

import google.generativeai as genai
import polars as pl
from pathlib import Path
import json
import re
from typing import Dict, Any, Optional
import os


class IntelligentChatBI:
    """
    Sistema inteligente de Chat BI usando Gemini para NL2SQL
    """
    
    def __init__(self, parquet_path: Path):
        self.parquet_path = parquet_path
        
        # Configurar Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não configurada")
        
        genai.configure(api_key=api_key)
        
        # Usar modelo ESTÁVEL (não experimental)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Carregar schema do Parquet
        self.schema = self._load_schema()
    
    def _load_schema(self) -> Dict[str, str]:
        """Carrega schema do Parquet para contexto"""
        lf = pl.scan_parquet(self.parquet_path)
        schema = lf.collect_schema()
        
        return {
            "columns": list(schema.names()),
            "description": {
                "PRODUTO": "Código do produto",
                "NOME": "Nome do produto",
                "UNE": "Unidade de Negócio (loja)",
                "MES_01": "Vendas/Preço do mês 1",
                "MES_02": "Vendas/Preço do mês 2",
                "MES_03": "Vendas/Preço do mês 3",
                # Adicionar mais conforme necessário
            }
        }
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Processa pergunta do usuário usando Gemini
        Retorna resposta estruturada com dados e texto
        """
        
        # Detecção rápida de saudações (sem usar Gemini)
        query_lower = user_query.lower()
        saudacoes = ["olá", "oi", "ola", "hello", "boa tarde", "bom dia", "boa noite"]
        
        if any(saudacao in query_lower for saudacao in saudacoes):
            return {
                "success": True,
                "text": "👋 Olá! Sou seu assistente de BI.\n\nPosso ajudar com:\n• Consultas de preços\n• Análise de vendas\n• Informações de produtos\n\nFaça uma pergunta!",
                "data": None
            }
        
        # Criar prompt SIMPLIFICADO para Gemini (evitar erro 400)
        prompt = f"""Analise esta pergunta sobre dados de vendas e retorne JSON:

Pergunta: "{user_query}"

Colunas disponíveis: PRODUTO, NOME, UNE, MES_01, MES_02, MES_03

Retorne JSON:
{{
  "produto": "código ou null",
  "une": "código ou null",
  "meses": ["MES_01", "MES_02", "MES_03"],
  "operacao": "sum|filter|count"
}}

Exemplo: "vendas produto 59294 une 261 últimos 3 meses"
{{
  "produto": "59294",
  "une": "261",
  "meses": ["MES_01", "MES_02", "MES_03"],
  "operacao": "sum"
}}
"""
        
        try:
            # Chamar Gemini
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extrair JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                return self._fallback_response(user_query)
            
            query_plan = json.loads(json_match.group())
            
            # Executar consulta Polars
            lf = pl.scan_parquet(self.parquet_path)
            
            produto = query_plan.get("produto")
            une = query_plan.get("une")
            meses = query_plan.get("meses", ["MES_01", "MES_02", "MES_03"])
            
            # Construir filtro
            filters = []
            if produto:
                filters.append(pl.col("PRODUTO") == produto)
            if une:
                filters.append(pl.col("UNE") == une)
            
            # Aplicar filtros
            if filters:
                result = lf.filter(pl.all_horizontal(filters)).select(["PRODUTO", "NOME", "UNE"] + meses).head(1).collect()
            else:
                result = lf.select(meses).sum().collect()
            
            # Formatar resposta
            if len(result) > 0:
                row = result.row(0, named=True)
                
                if produto and une:
                    nome = row.get("NOME", "Produto")
                    valores = [row.get(m, 0) for m in meses]
                    total = sum(valores)
                    
                    response_text = f"📊 **Produto {produto}** na UNE {une}:\n\n**Nome:** {nome}\n"
                    for i, mes in enumerate(meses, 1):
                        response_text += f"**Mês {i}:** {row.get(mes, 0):,.0f}\n"
                    response_text += f"\n**Total:** {total:,.0f}"
                else:
                    total = sum([row.get(m, 0) for m in meses])
                    response_text = f"📈 **Total de Vendas:** {total:,.0f}"
                
                return {
                    "success": True,
                    "text": response_text,
                    "data": row
                }
            
            return self._fallback_response(user_query)
            
        except Exception as e:
            print(f"Erro ao processar com Gemini: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_response(user_query)
    
    def _format_response(self, plan: Dict, result: Any) -> Dict[str, Any]:
        """Formata resposta baseado no template"""
        
        template = plan.get("response_template", "")
        
        # Extrair dados do resultado Polars
        if isinstance(result, pl.DataFrame):
            if len(result) > 0:
                row = result.row(0, named=True)
                
                # Calcular total se houver múltiplos meses
                total = sum([v for k, v in row.items() if k.startswith("MES_")])
                
                # Substituir placeholders
                text = template.format(
                    produto=plan.get("produto", ""),
                    une=plan.get("une", ""),
                    mes_01=row.get("MES_01", 0),
                    mes_02=row.get("MES_02", 0),
                    mes_03=row.get("MES_03", 0),
                    total=total
                )
                
                return {
                    "text": text,
                    "data": row
                }
        
        return {"text": str(result)}
    
    def _fallback_response(self, query: str) -> Dict[str, Any]:
        """Resposta de fallback quando Gemini falha"""
        return {
            "success": False,
            "text": f"🤔 Desculpe, não consegui processar sua pergunta: '{query}'\n\nTente reformular ou use perguntas mais simples como:\n• 'Qual o preço do produto X?'\n• 'Vendas do produto X na UNE Y'",
            "data": None
        }
