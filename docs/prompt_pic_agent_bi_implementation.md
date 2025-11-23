# Plano de Implementação Cirúrgica (PIC) - Agent_BI Refactoring

**Versão:** 1.0
**Data de Criação:** 21 de Novembro de 2025
**Escopo:** Refatoração completa do projeto `Agents_Solution_BI` para implementar Governança de Prompts (CO-STAR), Segurança de Dados (PII Masking) e Experiência de Usuário (Streaming)
**Nível de Precisão:** Cirúrgico (Instruções linha por linha)

---

## 📋 ÍNDICE

1. [Visão Geral e Contexto](#visão-geral-e-contexto)
2. [Estrutura de Arquivos Esperada](#estrutura-de-arquivos-esperada)
3. [Pilar 1: Governança de Prompts (CO-STAR)](#pilar-1-governança-de-prompts-co-star)
4. [Pilar 2: Segurança de Dados (PII Masking)](#pilar-2-segurança-de-dados-pii-masking)
5. [Pilar 3: Experiência de Usuário (Streaming)](#pilar-3-experiência-de-usuário-streaming)
6. [Testes e Validação](#testes-e-validação)
7. [Critério de Sucesso](#critério-de-sucesso)

---

## Visão Geral e Contexto

### Objetivo Geral
Refatorar o projeto `Agent_BI` (localizado em `/home/ubuntu/Agents_Solution_BI`) para implementar três pilares de melhoria:
1. **Governança de Prompts:** Estruturação robusta usando o paradigma CO-STAR
2. **Segurança de Dados:** Mascaramento de PII antes/depois da chamada ao LLM
3. **Experiência de Usuário:** Streaming de respostas sem indicadores de carregamento bloqueantes

### Restrições Críticas
- **Não quebrar a funcionalidade existente:** Todas as alterações devem ser retrocompatíveis
- **Não remover código:** Apenas adicionar, refatorar ou estender
- **Não alterar dependências:** Usar apenas bibliotecas já presentes no projeto
- **Manter a arquitetura atual:** Streamlit como frontend, Python como backend

### Arquitetura de Alto Nível
```
Agents_Solution_BI/
├── streamlit_app.py (FRONTEND - Será modificado)
├── core/
│   ├── agents/
│   │   └── prompt_loader.py (Será modificado)
│   ├── prompts/
│   │   ├── prompt_analise.md (Será modificado)
│   │   ├── prompt_desambiguacao.md (NOVO - Será criado)
│   │   └── [outros prompts]
│   ├── llm_service.py (Assumido - Será criado/modificado)
│   ├── security/
│   │   └── data_masking.py (NOVO - Será criado)
│   └── config/
│       └── logging_config.py (Existente - Não modificar)
└── [outros diretórios]
```

---

## Estrutura de Arquivos Esperada

Antes de iniciar a implementação, verifique se os seguintes arquivos existem:

```json
{
  "arquivos_esperados": [
    {
      "caminho": "/home/ubuntu/Agents_Solution_BI/streamlit_app.py",
      "tipo": "Python",
      "status": "DEVE EXISTIR",
      "descrição": "Arquivo principal do Streamlit"
    },
    {
      "caminho": "/home/ubuntu/Agents_Solution_BI/core/agents/prompt_loader.py",
      "tipo": "Python",
      "status": "DEVE EXISTIR",
      "descrição": "Carregador de prompts"
    },
    {
      "caminho": "/home/ubuntu/Agents_Solution_BI/core/prompts/",
      "tipo": "Diretório",
      "status": "DEVE EXISTIR",
      "descrição": "Diretório de templates de prompts"
    },
    {
      "caminho": "/home/ubuntu/Agents_Solution_BI/core/llm_service.py",
      "tipo": "Python",
      "status": "PODE NÃO EXISTIR",
      "descrição": "Serviço de LLM (será criado se não existir)"
    },
    {
      "caminho": "/home/ubuntu/Agents_Solution_BI/core/security/",
      "tipo": "Diretório",
      "status": "SERÁ CRIADO",
      "descrição": "Diretório de módulos de segurança"
    }
  ]
}
```

**Ação Prévia:** Se algum arquivo não existir, criar com conteúdo mínimo viável.

---

## PILAR 1: Governança de Prompts (CO-STAR)

### 1.1. Modificação: `core/agents/prompt_loader.py`

**Objetivo:** Estender a classe `PromptLoader` para suportar templates Markdown com injeção dinâmica de contexto.

**Arquivo:** `/home/ubuntu/Agents_Solution_BI/core/agents/prompt_loader.py`

**Ações:**

#### 1.1.1. Adicionar Método de Carregamento de Template Markdown

**Localização:** Após a linha 136 (final da classe `PromptLoader`)

**Código a Adicionar:**

```python
    def load_prompt_template(self, prompt_name: str) -> Optional[str]:
        """
        Carrega um template de prompt em formato Markdown (.md)
        
        Args:
            prompt_name (str): Nome do arquivo de prompt (com ou sem extensão .md)
            
        Returns:
            str: Conteúdo do template ou None se ocorrer erro
        """
        # Adiciona a extensão .md se não estiver presente
        if not prompt_name.endswith(".md"):
            prompt_file = f"{prompt_name}.md"
        else:
            prompt_file = prompt_name
        
        # Constrói o caminho completo do arquivo
        prompt_path = os.path.join(self.prompts_dir, prompt_file)
        
        # Verifica se o arquivo existe
        if not os.path.exists(prompt_path):
            logger.error(f"Template de prompt não encontrado: {prompt_path}")
            return None
        
        # Carrega o arquivo Markdown
        try:
            with open(prompt_path, "r", encoding="utf-8") as file:
                template_content = file.read()
                logger.info(f"Template de prompt carregado com sucesso: {prompt_name}")
                return template_content
        except Exception as e:
            logger.error(f"Erro ao carregar template de prompt {prompt_name}: {e}")
            return None
    
    def inject_context_into_template(self, template: str, context: Dict[str, Any]) -> str:
        """
        Injeta contexto dinâmico em um template de prompt usando placeholders.
        
        Placeholders esperados no template:
        - [CONTEXTO_DADOS]: Será substituído pelo esquema de banco de dados
        - [OBJETIVO_ATÔMICO]: Será substituído pelo objetivo da tarefa
        - [FORMATO_RESPOSTA]: Será substituído pelas instruções de formato
        
        Args:
            template (str): Conteúdo do template com placeholders
            context (Dict[str, Any]): Dicionário com valores para substituição
            
        Returns:
            str: Template com contexto injetado
        """
        result = template
        
        # Substitui placeholders por valores do contexto
        for placeholder, value in context.items():
            placeholder_key = f"[{placeholder}]"
            if isinstance(value, dict):
                # Se o valor é um dicionário, converte para string formatada
                value_str = json.dumps(value, ensure_ascii=False, indent=2)
            else:
                value_str = str(value)
            
            result = result.replace(placeholder_key, value_str)
            logger.debug(f"Placeholder {placeholder_key} substituído com sucesso")
        
        return result
```

**Justificativa:**
- Permite carregar templates Markdown em vez de apenas JSON
- Suporta injeção dinâmica de contexto (esquema de dados, objetivos)
- Mantém compatibilidade com o método `load_prompt` existente

---

### 1.2. Criação: `core/prompts/prompt_desambiguacao.md`

**Objetivo:** Criar um prompt focado em desambiguar perguntas vagas do usuário.

**Arquivo:** `/home/ubuntu/Agents_Solution_BI/core/prompts/prompt_desambiguacao.md` (NOVO)

**Conteúdo:**

```markdown
# PROMPT DE DESAMBIGUAÇÃO - Agent_BI

## PERSONA E PAPEL

**QUEM VOCÊ É:**
Você é um Analista de Dados Interativo e especialista em Business Intelligence. Sua função é clarificar perguntas vagas de usuários finais, ajudando-os a refinar suas consultas de dados.

## CONTEXTO

O usuário fez uma pergunta que é potencialmente ambígua ou vaga. Sua tarefa é fazer perguntas de esclarecimento para entender melhor a intenção do usuário, permitindo que o agente de BI gere uma consulta mais precisa e relevante.

**Esquema de Dados Disponível:**
[CONTEXTO_DADOS]

## OBJETIVO ATÔMICO

Formular entre 2 e 3 perguntas de esclarecimento que ajudem a refinar a consulta do usuário. As perguntas devem ser:
- Específicas e focadas
- Baseadas no esquema de dados disponível
- Apresentadas em formato de múltipla escolha ou aberta
- Sem gerar código SQL ou resposta final

## TAREFA

Analise a pergunta do usuário abaixo e formule perguntas de esclarecimento:

**Pergunta do Usuário:**
[PERGUNTA_USUARIO]

## INSTRUÇÕES DE FORMATO DE SAÍDA

Retorne **apenas** um objeto JSON válido, sem texto introdutório ou conclusivo, com a seguinte estrutura:

```json
{
  "pergunta_original": "A pergunta exata do usuário",
  "ambiguidades_detectadas": [
    "Descrição da primeira ambiguidade",
    "Descrição da segunda ambiguidade"
  ],
  "perguntas_esclarecimento": [
    {
      "numero": 1,
      "pergunta": "Qual é o período de tempo que você deseja analisar?",
      "opcoes": ["Últimos 7 dias", "Últimos 30 dias", "Últimos 90 dias", "Personalizado"]
    },
    {
      "numero": 2,
      "pergunta": "Qual dimensão de análise você prefere?",
      "opcoes": ["Por Produto", "Por Região", "Por Cliente", "Todas"]
    }
  ],
  "sugestao_proxima_etapa": "Após o usuário responder, o agente poderá gerar uma consulta SQL precisa."
}
```

## RESTRIÇÕES

- **NÃO** gere código SQL
- **NÃO** retorne dados ou resultados
- **NÃO** faça suposições sobre a intenção do usuário
- **SEMPRE** use apenas as tabelas e colunas disponíveis no esquema de dados
- **SEMPRE** retorne um JSON válido

## TOM E ESTILO

Mantenha um tom consultivo, profissional e focado em clareza. Seja conciso e direto.
```

**Justificativa:**
- Reduz erros de interpretação de consultas vagas
- Melhora a precisão das respostas do agente
- Alinha-se com a Feature 4.1.1 (PLN) do PRD

---

### 1.3. Modificação: `core/prompts/prompt_analise.md`

**Objetivo:** Atualizar o prompt principal para incluir o formato CO-STAR e exigir saída JSON estruturada.

**Arquivo:** `/home/ubuntu/Agents_Solution_BI/core/prompts/prompt_analise.md`

**Ações:**

#### 1.3.1. Substituir Conteúdo Completo

**Localização:** Linhas 1-26 (todo o arquivo)

**Novo Conteúdo:**

```markdown
# PROMPT PRINCIPAL DE ANÁLISE - Agent_BI (CO-STAR)

## CONTEXTO (C)

**Esquema de Banco de Dados:**
[CONTEXTO_DADOS]

O usuário está consultando este banco de dados através de uma interface conversacional. Você tem acesso a todas as tabelas e colunas listadas acima.

## OBJETIVO ATÔMICO (O)

Sua tarefa é traduzir a pergunta do usuário em uma consulta SQL otimizada, executá-la (simuladamente), analisar os resultados e formular uma resposta em linguagem natural que seja clara, acionável e relevante para o contexto de negócio.

**Tarefas Específicas:**
1. Interpretar a intenção da pergunta do usuário
2. Gerar uma consulta SQL otimizada
3. Simular a execução (ou indicar que será executada)
4. Analisar os dados resultantes
5. Formular uma resposta em português claro
6. Sugerir um tipo de gráfico apropriado

## ESTILO (S)

Mantenha um estilo de comunicação:
- **Conciso:** Sem floreios desnecessários
- **Profissional:** Focado em fatos e dados
- **Analítico:** Baseado em evidências
- **Formatado:** Use Markdown para tabelas e listas quando apropriado

## TOM (T)

Adote um tom **consultivo e técnico**. Se a pergunta for ambígua, **não faça suposições**. Em vez disso, indique a ambiguidade na resposta JSON (campo `ambiguidades_detectadas`).

## PÚBLICO-ALVO (A)

O público é composto por:
- Diretores e Gestores (necessitam de resumos executivos)
- Analistas de Negócios (necessitam de detalhes técnicos)
- Compradores e Operações (necessitam de dados específicos)

Adapte o nível de detalhe conforme apropriado.

## FORMATO DE RESPOSTA (R)

**SAÍDA OBRIGATÓRIA:** Retorne **apenas** um objeto JSON válido, sem texto introdutório ou conclusivo, com a seguinte estrutura:

```json
{
  "interpretacao_pergunta": "Resumo da intenção do usuário",
  "ambiguidades_detectadas": [
    "Se houver ambiguidades, liste aqui"
  ],
  "sql_query": "SELECT ... FROM ... WHERE ...",
  "sql_explicacao": "Explicação breve da lógica SQL",
  "data_summary": {
    "total_registros": 0,
    "colunas_retornadas": ["col1", "col2"],
    "resumo_estatistico": "Descrição dos dados"
  },
  "natural_language_response": "Resposta em português claro e profissional",
  "suggested_chart_type": "bar|line|pie|scatter|table",
  "chart_config": {
    "titulo": "Título do gráfico",
    "eixo_x": "Nome da dimensão",
    "eixo_y": "Nome da métrica",
    "filtros_aplicados": ["filtro1", "filtro2"]
  }
}
```

## RESTRIÇÕES CRÍTICAS

- Use **apenas** as tabelas e colunas fornecidas no CONTEXTO_DADOS
- **NÃO** invente dados ou colunas
- **NÃO** execute queries perigosas (DROP, DELETE sem WHERE)
- **NÃO** retorne dados sensíveis sem indicação de mascaramento
- **SEMPRE** retorne um JSON válido e bem formatado

## EXEMPLOS DE ENTRADA E SAÍDA

### Exemplo 1: Pergunta Clara
**Entrada:** "Qual foi o faturamento total do último trimestre?"
**Saída:** JSON com SQL, resumo e gráfico de barras

### Exemplo 2: Pergunta Ambígua
**Entrada:** "Me mostre as vendas"
**Saída:** JSON com `ambiguidades_detectadas` preenchido, sugerindo refinamento

## INSTRUÇÕES FINAIS

1. Sempre priorize a **precisão** sobre a velocidade
2. Se não tiver certeza, indique a ambiguidade
3. Retorne **sempre** um JSON válido
4. Inclua explicações técnicas no campo `sql_explicacao`
5. Sugira gráficos apropriados para o tipo de dado
```

**Justificativa:**
- Implementa o paradigma CO-STAR completo
- Garante saída estruturada em JSON
- Reduz ambiguidades e erros de interpretação

---

## PILAR 2: Segurança de Dados (PII Masking)

### 2.1. Criação: `core/security/data_masking.py`

**Objetivo:** Implementar funções de mascaramento de PII (Informações Pessoais Identificáveis).

**Arquivo:** `/home/ubuntu/Agents_Solution_BI/core/security/data_masking.py` (NOVO)

**Conteúdo:**

```python
"""
Módulo de Segurança: Mascaramento de PII (Informações Pessoais Identificáveis)
Fornece funções para identificar e mascarar dados sensíveis antes de enviar ao LLM.
"""

import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger("data_masking")

# Padrões de regex para identificar PII
PII_PATTERNS = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "cpf": r"\d{3}\.\d{3}\.\d{3}-\d{2}",
    "telefone": r"\(\d{2}\)\s?\d{4,5}-\d{4}",
    "cartao_credito": r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}",
    "nome_proprio": r"\b[A-Z][a-z]+\s[A-Z][a-z]+\b",  # Heurístico básico
}

# Mapeamento de padrão para token de mascaramento
PII_MASKS = {
    "email": "[EMAIL_MASKED]",
    "cpf": "[CPF_MASKED]",
    "telefone": "[TELEFONE_MASKED]",
    "cartao_credito": "[CARTAO_MASKED]",
    "nome_proprio": "[NOME_MASKED]",
}


class PIIMasker:
    """
    Classe responsável por mascarar dados sensíveis em textos.
    """
    
    def __init__(self, patterns: Dict[str, str] = None, masks: Dict[str, str] = None):
        """
        Inicializa o mascarador de PII.
        
        Args:
            patterns (Dict[str, str]): Dicionário de padrões regex customizados
            masks (Dict[str, str]): Dicionário de máscaras customizadas
        """
        self.patterns = patterns or PII_PATTERNS
        self.masks = masks or PII_MASKS
        self.masked_items: List[Tuple[str, str]] = []  # Histórico de mascaramentos
    
    def mask_text(self, text: str) -> str:
        """
        Mascara todos os padrões de PII em um texto.
        
        Args:
            text (str): Texto a ser mascarado
            
        Returns:
            str: Texto com PII mascarado
        """
        if not text:
            return text
        
        masked_text = text
        self.masked_items = []
        
        for pii_type, pattern in self.patterns.items():
            mask = self.masks.get(pii_type, "[MASKED]")
            
            # Encontra todas as ocorrências do padrão
            matches = re.finditer(pattern, masked_text)
            
            for match in matches:
                original_value = match.group(0)
                # Registra o mascaramento
                self.masked_items.append((pii_type, original_value))
                logger.debug(f"PII detectado ({pii_type}): {original_value[:10]}...")
            
            # Substitui todas as ocorrências
            masked_text = re.sub(pattern, mask, masked_text)
        
        logger.info(f"Mascaramento concluído: {len(self.masked_items)} itens de PII mascarados")
        return masked_text
    
    def mask_dict(self, data: Dict) -> Dict:
        """
        Mascara valores de PII em um dicionário.
        
        Args:
            data (Dict): Dicionário com dados potencialmente sensíveis
            
        Returns:
            Dict: Dicionário com PII mascarado
        """
        masked_data = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                masked_data[key] = self.mask_text(value)
            elif isinstance(value, dict):
                masked_data[key] = self.mask_dict(value)
            elif isinstance(value, list):
                masked_data[key] = [
                    self.mask_text(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                masked_data[key] = value
        
        return masked_data
    
    def get_masked_items_summary(self) -> Dict:
        """
        Retorna um resumo dos itens mascarados.
        
        Returns:
            Dict: Resumo com contagem por tipo de PII
        """
        summary = {}
        for pii_type, _ in self.masked_items:
            summary[pii_type] = summary.get(pii_type, 0) + 1
        
        return summary


# Instância global do mascarador
_global_masker = PIIMasker()


def mask_pii(text: str) -> str:
    """
    Função utilitária para mascarar PII em um texto.
    
    Args:
        text (str): Texto a ser mascarado
        
    Returns:
        str: Texto com PII mascarado
    """
    return _global_masker.mask_text(text)


def mask_pii_dict(data: Dict) -> Dict:
    """
    Função utilitária para mascarar PII em um dicionário.
    
    Args:
        data (Dict): Dicionário com dados potencialmente sensíveis
        
    Returns:
        Dict: Dicionário com PII mascarado
    """
    return _global_masker.mask_dict(data)


def get_pii_summary() -> Dict:
    """
    Retorna um resumo dos itens mascarados na sessão atual.
    
    Returns:
        Dict: Resumo com contagem por tipo de PII
    """
    return _global_masker.get_masked_items_summary()
```

**Justificativa:**
- Centraliza a lógica de mascaramento de PII
- Suporta múltiplos padrões de dados sensíveis
- Registra histórico de mascaramentos para auditoria
- Fácil de estender com novos padrões

---

### 2.2. Criação: `core/security/__init__.py`

**Objetivo:** Tornar o módulo `security` um pacote Python.

**Arquivo:** `/home/ubuntu/Agents_Solution_BI/core/security/__init__.py` (NOVO)

**Conteúdo:**

```python
"""
Pacote de Segurança do Agent_BI
Fornece módulos para proteção de dados, mascaramento de PII e validação.
"""

from .data_masking import mask_pii, mask_pii_dict, get_pii_summary, PIIMasker

__all__ = [
    "mask_pii",
    "mask_pii_dict",
    "get_pii_summary",
    "PIIMasker",
]
```

---

### 2.3. Modificação: `streamlit_app.py`

**Objetivo:** Integrar o mascaramento de PII no fluxo de entrada/saída do usuário.

**Arquivo:** `/home/ubuntu/Agents_Solution_BI/streamlit_app.py`

**Ações:**

#### 2.3.1. Adicionar Import do Módulo de Segurança

**Localização:** Após as linhas de import (aproximadamente linha 20)

**Código a Adicionar:**

```python
# Importar módulo de segurança
from core.security import mask_pii, mask_pii_dict, get_pii_summary
```

#### 2.3.2. Mascarar Input do Usuário

**Localização:** Onde a entrada do usuário é recebida (procure por `st.chat_input` ou similar)

**Padrão de Código Existente (Exemplo):**
```python
user_input = st.chat_input("Digite sua pergunta...")
```

**Código Modificado:**
```python
user_input = st.chat_input("Digite sua pergunta...")

if user_input:
    # Mascarar PII antes de processar
    masked_input = mask_pii(user_input)
    logger.info(f"Input mascarado: PII removido")
    
    # Usar masked_input para o resto do processamento
    user_input_for_llm = masked_input
else:
    user_input_for_llm = None
```

#### 2.3.3. Mascarar Output do LLM

**Localização:** Onde a resposta do LLM é exibida (procure por `st.write` ou similar)

**Padrão de Código Existente (Exemplo):**
```python
llm_response = call_llm(user_input_for_llm)
st.write(llm_response)
```

**Código Modificado:**
```python
llm_response = call_llm(user_input_for_llm)

# Mascarar PII na resposta do LLM (camada extra de proteção)
masked_response = mask_pii(llm_response)

# Exibir resposta mascarada
st.write(masked_response)

# Log de segurança
pii_summary = get_pii_summary()
if pii_summary:
    logger.warning(f"PII detectado e mascarado: {pii_summary}")
```

---

## PILAR 3: Experiência de Usuário (Streaming)

### 3.1. Criação: `core/llm_service.py`

**Objetivo:** Centralizar a lógica de chamada ao LLM com suporte a streaming.

**Arquivo:** `/home/ubuntu/Agents_Solution_BI/core/llm_service.py` (NOVO)

**Conteúdo:**

```python
"""
Módulo de Serviço LLM: Encapsula a lógica de chamada ao Large Language Model
Fornece suporte a streaming e tratamento de erros.
"""

import logging
import json
from typing import Generator, Optional, Dict, Any
from core.agents.prompt_loader import PromptLoader

logger = logging.getLogger("llm_service")

# Importar a biblioteca do LLM (ajustar conforme o LLM utilizado)
# Exemplo: OpenAI, Anthropic, Google Gemini, etc.
# Para este exemplo, assumimos que existe um módulo de LLM configurado
try:
    from core.llm_client import get_llm_client
except ImportError:
    logger.warning("LLM client não encontrado. Usando mock para testes.")
    def get_llm_client():
        return None


class LLMService:
    """
    Serviço centralizado para chamadas ao LLM com suporte a streaming.
    """
    
    def __init__(self):
        """Inicializa o serviço LLM."""
        self.client = get_llm_client()
        self.prompt_loader = PromptLoader()
        self.model_name = "gpt-4"  # Ajustar conforme o modelo utilizado
    
    def get_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Obtém uma resposta completa do LLM (não-streaming).
        
        Args:
            prompt (str): Prompt ou template de prompt
            context (Dict): Contexto para injeção dinâmica (opcional)
            
        Returns:
            str: Resposta completa do LLM
        """
        try:
            # Se o prompt é um template, carregar e injetar contexto
            if context:
                full_prompt = self.prompt_loader.inject_context_into_template(prompt, context)
            else:
                full_prompt = prompt
            
            # Chamada ao LLM (ajustar conforme a biblioteca utilizada)
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            logger.info("Resposta do LLM obtida com sucesso (não-streaming)")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter resposta do LLM: {e}")
            return f"Erro ao processar sua pergunta: {str(e)}"
    
    def get_response_stream(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Generator[str, None, None]:
        """
        Obtém uma resposta do LLM em modo streaming (chunks).
        
        Args:
            prompt (str): Prompt ou template de prompt
            context (Dict): Contexto para injeção dinâmica (opcional)
            
        Yields:
            str: Chunks de texto da resposta
        """
        try:
            # Se o prompt é um template, carregar e injetar contexto
            if context:
                full_prompt = self.prompt_loader.inject_context_into_template(prompt, context)
            else:
                full_prompt = prompt
            
            # Chamada ao LLM com streaming (ajustar conforme a biblioteca utilizada)
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.7,
                max_tokens=2000,
                stream=True  # Ativar streaming
            )
            
            logger.info("Streaming de resposta do LLM iniciado")
            
            # Iterar sobre os chunks
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            
            logger.info("Streaming de resposta do LLM concluído")
            
        except Exception as e:
            logger.error(f"Erro ao fazer streaming da resposta do LLM: {e}")
            yield f"Erro ao processar sua pergunta: {str(e)}"
    
    def parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Tenta fazer parse de uma resposta JSON do LLM.
        
        Args:
            response (str): Resposta do LLM (esperado ser JSON)
            
        Returns:
            Dict: Dicionário parseado ou None se falhar
        """
        try:
            # Tenta fazer parse direto
            return json.loads(response)
        except json.JSONDecodeError:
            # Se falhar, tenta remover caracteres de escape ou formatação
            try:
                # Remove markdown code blocks se presentes
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0]
                
                return json.loads(response)
            except Exception as e:
                logger.error(f"Erro ao fazer parse de JSON: {e}")
                return None


# Instância global do serviço LLM
_global_llm_service = LLMService()


def get_llm_service() -> LLMService:
    """
    Retorna a instância global do serviço LLM.
    
    Returns:
        LLMService: Instância do serviço
    """
    return _global_llm_service


def get_llm_response(prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Função utilitária para obter resposta do LLM (não-streaming).
    
    Args:
        prompt (str): Prompt
        context (Dict): Contexto (opcional)
        
    Returns:
        str: Resposta do LLM
    """
    return _global_llm_service.get_response(prompt, context)


def get_llm_response_stream(prompt: str, context: Optional[Dict[str, Any]] = None) -> Generator[str, None, None]:
    """
    Função utilitária para obter resposta do LLM em streaming.
    
    Args:
        prompt (str): Prompt
        context (Dict): Contexto (opcional)
        
    Yields:
        str: Chunks de texto
    """
    yield from _global_llm_service.get_response_stream(prompt, context)
```

**Justificativa:**
- Centraliza a lógica de LLM em um único módulo
- Suporta tanto streaming quanto não-streaming
- Facilita testes e manutenção
- Separa a lógica de LLM da interface Streamlit

---

### 3.2. Modificação: `streamlit_app.py` (Streaming)

**Objetivo:** Integrar o streaming de resposta do LLM no frontend.

**Arquivo:** `/home/ubuntu/Agents_Solution_BI/streamlit_app.py`

**Ações:**

#### 3.2.1. Adicionar Import do Serviço LLM

**Localização:** Após as linhas de import (aproximadamente linha 25)

**Código a Adicionar:**

```python
# Importar serviço LLM
from core.llm_service import get_llm_response_stream, get_llm_service
```

#### 3.2.2. Implementar Streaming na Exibição de Resposta

**Localização:** Onde a resposta do LLM é exibida (procure por `st.write` ou similar)

**Padrão de Código Existente (Exemplo):**
```python
if user_input:
    with st.spinner("Processando sua pergunta..."):
        llm_response = call_llm(user_input)
    st.write(llm_response)
```

**Código Modificado:**
```python
if user_input:
    # Criar um placeholder para a resposta
    response_placeholder = st.empty()
    
    # Criar um placeholder para status intermediário
    status_placeholder = st.empty()
    
    # Atualizar status
    status_placeholder.text("⏳ Analisando a intenção...")
    
    try:
        # Usar streaming para exibir a resposta em tempo real
        with response_placeholder.container():
            st.write_stream(get_llm_response_stream(user_input_for_llm))
        
        # Limpar status após conclusão
        status_placeholder.empty()
        
        logger.info("Resposta exibida com sucesso via streaming")
        
    except Exception as e:
        status_placeholder.error(f"Erro ao processar: {str(e)}")
        logger.error(f"Erro durante streaming: {e}")
```

#### 3.2.3. Adicionar Feedback Intermediário (Sub-status)

**Localização:** Antes da chamada ao LLM

**Código a Adicionar:**

```python
# Criar colunas para layout do status
col1, col2 = st.columns([3, 1])

with col1:
    status_messages = [
        "⏳ Analisando a intenção...",
        "🔍 Gerando consulta SQL...",
        "💾 Consultando a base de dados...",
        "📊 Formatando a resposta..."
    ]
    
    # Simular progresso (ajustar conforme a lógica real)
    import time
    for i, msg in enumerate(status_messages):
        with st.spinner(msg):
            time.sleep(0.5)  # Simulação - remover em produção
```

**Observação:** Este é um exemplo simplificado. A implementação real deve integrar o feedback com as etapas reais do agente.

---

## Testes e Validação

### 4.1. Teste de Mascaramento de PII

**Arquivo de Teste:** `/home/ubuntu/Agents_Solution_BI/tests/test_data_masking.py` (NOVO)

**Conteúdo:**

```python
"""
Testes para o módulo de mascaramento de PII
"""

import unittest
from core.security import mask_pii, mask_pii_dict


class TestDataMasking(unittest.TestCase):
    """Testes para a classe PIIMasker"""
    
    def test_mask_email(self):
        """Testa mascaramento de e-mail"""
        text = "Contato: joao@example.com"
        masked = mask_pii(text)
        self.assertNotIn("joao@example.com", masked)
        self.assertIn("[EMAIL_MASKED]", masked)
    
    def test_mask_cpf(self):
        """Testa mascaramento de CPF"""
        text = "CPF: 123.456.789-10"
        masked = mask_pii(text)
        self.assertNotIn("123.456.789-10", masked)
        self.assertIn("[CPF_MASKED]", masked)
    
    def test_mask_dict(self):
        """Testa mascaramento em dicionário"""
        data = {
            "nome": "João Silva",
            "email": "joao@example.com",
            "cpf": "123.456.789-10"
        }
        masked = mask_pii_dict(data)
        self.assertNotIn("joao@example.com", masked["email"])
        self.assertIn("[EMAIL_MASKED]", masked["email"])
    
    def test_no_false_positives(self):
        """Testa que não há falsos positivos"""
        text = "O produto custa R$ 123.45"
        masked = mask_pii(text)
        # Não deve mascarar valores monetários
        self.assertIn("123.45", masked)


if __name__ == "__main__":
    unittest.main()
```

**Execução:**
```bash
cd /home/ubuntu/Agents_Solution_BI
python -m pytest tests/test_data_masking.py -v
```

---

### 4.2. Teste de Streaming

**Arquivo de Teste:** `/home/ubuntu/Agents_Solution_BI/tests/test_llm_streaming.py` (NOVO)

**Conteúdo:**

```python
"""
Testes para o módulo de streaming de LLM
"""

import unittest
from core.llm_service import get_llm_service


class TestLLMStreaming(unittest.TestCase):
    """Testes para o serviço LLM com streaming"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.llm_service = get_llm_service()
    
    def test_stream_generator(self):
        """Testa se o streaming retorna um generator"""
        prompt = "Olá, como você está?"
        stream = self.llm_service.get_response_stream(prompt)
        
        # Verificar se é um generator
        self.assertTrue(hasattr(stream, '__iter__'))
        self.assertTrue(hasattr(stream, '__next__'))
    
    def test_stream_yields_strings(self):
        """Testa se o streaming retorna strings"""
        prompt = "Teste de streaming"
        stream = self.llm_service.get_response_stream(prompt)
        
        for chunk in stream:
            self.assertIsInstance(chunk, str)
            break  # Apenas verificar o primeiro chunk


if __name__ == "__main__":
    unittest.main()
```

**Execução:**
```bash
cd /home/ubuntu/Agents_Solution_BI
python -m pytest tests/test_llm_streaming.py -v
```

---

## Critério de Sucesso

A implementação será considerada bem-sucedida quando **TODOS** os critérios abaixo forem atendidos:

### ✅ Critério 1: Governança de Prompts (CO-STAR)

```json
{
  "criterio": "Governança de Prompts",
  "validacoes": [
    {
      "item": "Prompt de Desambiguação",
      "validacao": "Arquivo /home/ubuntu/Agents_Solution_BI/core/prompts/prompt_desambiguacao.md existe e contém estrutura JSON",
      "teste": "Verificar se arquivo existe e contém 'CONTEXTO_DADOS' e 'PERGUNTA_USUARIO'"
    },
    {
      "item": "Prompt Principal Atualizado",
      "validacao": "Arquivo /home/ubuntu/Agents_Solution_BI/core/prompts/prompt_analise.md contém seções CO-STAR",
      "teste": "Verificar se arquivo contém 'CONTEXTO', 'OBJETIVO', 'ESTILO', 'TOM', 'PÚBLICO', 'FORMATO'"
    },
    {
      "item": "Método de Injeção de Contexto",
      "validacao": "Função inject_context_into_template() existe em prompt_loader.py",
      "teste": "Chamar função com template e contexto, verificar se placeholders foram substituídos"
    },
    {
      "item": "Saída JSON Estruturada",
      "validacao": "Resposta do agente é um JSON válido com chaves obrigatórias",
      "teste": "Fazer pergunta, verificar se resposta é JSON com 'sql_query', 'natural_language_response', 'suggested_chart_type'"
    }
  ]
}
```

### ✅ Critério 2: Segurança de Dados (PII Masking)

```json
{
  "criterio": "Segurança de Dados",
  "validacoes": [
    {
      "item": "Módulo de Mascaramento",
      "validacao": "Arquivo /home/ubuntu/Agents_Solution_BI/core/security/data_masking.py existe",
      "teste": "Importar módulo: from core.security import mask_pii"
    },
    {
      "item": "Mascaramento de E-mail",
      "validacao": "Função mask_pii() mascara e-mails corretamente",
      "teste": "mask_pii('contato@example.com') retorna '[EMAIL_MASKED]'"
    },
    {
      "item": "Mascaramento de CPF",
      "validacao": "Função mask_pii() mascara CPFs corretamente",
      "teste": "mask_pii('123.456.789-10') retorna '[CPF_MASKED]'"
    },
    {
      "item": "Integração no Streamlit",
      "validacao": "Input do usuário é mascarado antes de enviar ao LLM",
      "teste": "Verificar logs: 'Input mascarado: PII removido' aparece após entrada do usuário"
    },
    {
      "item": "Proteção de Saída",
      "validacao": "Output do LLM é mascarado antes de exibir",
      "teste": "Verificar logs: 'PII detectado e mascarado' aparece após resposta do LLM"
    }
  ]
}
```

### ✅ Critério 3: Experiência de Usuário (Streaming)

```json
{
  "criterio": "Experiência de Usuário",
  "validacoes": [
    {
      "item": "Serviço LLM com Streaming",
      "validacao": "Arquivo /home/ubuntu/Agents_Solution_BI/core/llm_service.py existe",
      "teste": "Importar módulo: from core.llm_service import get_llm_response_stream"
    },
    {
      "item": "Método get_response_stream()",
      "validacao": "Função retorna um generator de strings",
      "teste": "Chamar função, verificar se retorna generator com chunks de texto"
    },
    {
      "item": "Integração com st.write_stream()",
      "validacao": "Resposta do LLM é exibida via st.write_stream() no Streamlit",
      "teste": "Fazer pergunta no Streamlit, verificar se resposta aparece gradualmente (não de uma vez)"
    },
    {
      "item": "Sem Spinner Bloqueante",
      "validacao": "Não há st.spinner() bloqueante durante o streaming",
      "teste": "Fazer pergunta, verificar que a interface não fica congelada com 'lupa rodando'"
    },
    {
      "item": "Feedback Intermediário",
      "validacao": "Mensagens de status aparecem durante o processamento",
      "teste": "Fazer pergunta, verificar se aparecem mensagens como '⏳ Analisando...' ou '🔍 Gerando SQL...'"
    }
  ]
}
```

### 🎯 Teste de Integração Final

**Cenário:** Um usuário faz uma pergunta vaga no Streamlit.

**Fluxo Esperado:**
1. ✅ Input do usuário é mascarado (PII removido)
2. ✅ Sistema detecta ambiguidade e usa prompt_desambiguacao.md
3. ✅ Resposta é gerada em JSON estruturado
4. ✅ Resposta é mascarada (proteção extra)
5. ✅ Resposta é exibida via streaming (sem spinner bloqueante)
6. ✅ Usuário vê a resposta aparecer gradualmente

**Comando de Teste:**
```bash
cd /home/ubuntu/Agents_Solution_BI
streamlit run streamlit_app.py
# Fazer pergunta: "Me mostre as vendas"
# Verificar: Resposta aparece gradualmente, sem "lupa rodando"
```

---

## Checklist de Implementação

Utilize este checklist para rastrear o progresso:

```
PILAR 1: Governança de Prompts (CO-STAR)
- [ ] Modificar core/agents/prompt_loader.py (adicionar load_prompt_template e inject_context_into_template)
- [ ] Criar core/prompts/prompt_desambiguacao.md
- [ ] Modificar core/prompts/prompt_analise.md (adicionar estrutura CO-STAR)

PILAR 2: Segurança de Dados (PII Masking)
- [ ] Criar core/security/__init__.py
- [ ] Criar core/security/data_masking.py (classe PIIMasker)
- [ ] Modificar streamlit_app.py (adicionar imports de segurança)
- [ ] Modificar streamlit_app.py (mascarar input do usuário)
- [ ] Modificar streamlit_app.py (mascarar output do LLM)

PILAR 3: Experiência de Usuário (Streaming)
- [ ] Criar core/llm_service.py (classe LLMService com streaming)
- [ ] Modificar streamlit_app.py (adicionar imports de LLM)
- [ ] Modificar streamlit_app.py (implementar st.write_stream)
- [ ] Modificar streamlit_app.py (remover st.spinner bloqueante)
- [ ] Modificar streamlit_app.py (adicionar feedback intermediário)

TESTES E VALIDAÇÃO
- [ ] Criar tests/test_data_masking.py
- [ ] Criar tests/test_llm_streaming.py
- [ ] Executar testes de mascaramento
- [ ] Executar testes de streaming
- [ ] Teste manual no Streamlit (pergunta vaga)
- [ ] Verificar logs de segurança

FINALIZAÇÃO
- [ ] Todos os critérios de sucesso atendidos
- [ ] Documentação atualizada
- [ ] Código commitado no Git
```

---

## Notas Importantes

1. **Retrocompatibilidade:** Todas as alterações devem ser retrocompatíveis. Não remova código existente, apenas estenda.
2. **Logging:** Adicione logs em pontos críticos para facilitar debugging e auditoria.
3. **Tratamento de Erros:** Sempre use try/except para evitar que erros de segurança ou streaming quebrem a aplicação.
4. **Testes:** Execute os testes após cada pilar implementado.
5. **Git:** Faça commits frequentes com mensagens descritivas.

---

## Referências de Arquivos

| Arquivo | Tipo | Status | Descrição |
| :--- | :--- | :--- | :--- |
| `/home/ubuntu/Agents_Solution_BI/streamlit_app.py` | Python | Modificar | Frontend Streamlit |
| `/home/ubuntu/Agents_Solution_BI/core/agents/prompt_loader.py` | Python | Modificar | Carregador de prompts |
| `/home/ubuntu/Agents_Solution_BI/core/prompts/prompt_analise.md` | Markdown | Modificar | Prompt principal |
| `/home/ubuntu/Agents_Solution_BI/core/prompts/prompt_desambiguacao.md` | Markdown | Criar | Prompt de desambiguação |
| `/home/ubuntu/Agents_Solution_BI/core/security/__init__.py` | Python | Criar | Pacote de segurança |
| `/home/ubuntu/Agents_Solution_BI/core/security/data_masking.py` | Python | Criar | Módulo de mascaramento PII |
| `/home/ubuntu/Agents_Solution_BI/core/llm_service.py` | Python | Criar | Serviço LLM com streaming |
| `/home/ubuntu/Agents_Solution_BI/tests/test_data_masking.py` | Python | Criar | Testes de mascaramento |
| `/home/ubuntu/Agents_Solution_BI/tests/test_llm_streaming.py` | Python | Criar | Testes de streaming |

---

## Conclusão

Este **Plano de Implementação Cirúrgica (PIC)** fornece instruções detalhadas e precisas para implementar as três melhorias propostas no Agent_BI. Cada ação é localizada, especificada e testável, minimizando o risco de introduzir bugs ou quebrar a funcionalidade existente.

**Próximas Etapas:**
1. Revisar este documento com a equipe de desenvolvimento
2. Executar as ações na ordem especificada
3. Testar após cada pilar
4. Documentar qualquer desvio ou ajuste necessário
5. Fazer commit no Git com mensagens descritivas
