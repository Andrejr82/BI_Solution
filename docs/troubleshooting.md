# 🛠️ Guia de Solução de Problemas - Agent_Solution_BI

**Versão:** 3.0
**Data de Atualização:** 21 de setembro de 2025
**Público-Alvo:** Usuários, Desenvolvedores, Administradores

---

## 🎯 **Visão Geral**

Este guia oferece soluções para os problemas mais comuns encontrados no Agent_Solution_BI, organizados por categoria e nível de severidade. Use o índice para localizar rapidamente a solução do seu problema.

### **🚨 Níveis de Severidade**
- 🔴 **Crítico**: Sistema não funciona
- 🟡 **Alto**: Funcionalidade limitada
- 🟢 **Baixo**: Inconveniente menor

---

## 📋 **Índice de Problemas**

### **🖥️ [Problemas de Interface](#interface)**
- [Sistema não carrega](#sistema-nao-carrega)
- [Página em branco](#pagina-branco)
- [Login não funciona](#login-nao-funciona)
- [Gráficos não aparecem](#graficos-nao-aparecem)

### **💬 [Problemas de Consulta](#consulta)**
- [Respostas incorretas](#respostas-incorretas)
- [Sistema muito lento](#sistema-lento)
- [Erro "Não encontrei dados"](#nao-encontrei-dados)
- [Consulta trava](#consulta-trava)

### **🔧 [Problemas Técnicos](#tecnicos)**
- [Erro de conexão](#erro-conexao)
- [Problemas de performance](#performance)
- [Erros de API](#erros-api)
- [Problemas de dados](#problemas-dados)

### **🛡️ [Problemas de Configuração](#configuracao)**
- [Variáveis de ambiente](#variaveis-ambiente)
- [Problemas de permissão](#permissoes)
- [Configuração de banco](#config-banco)

---

## 🖥️ **Problemas de Interface** {#interface}

### **Sistema não carrega** {#sistema-nao-carrega}
**Severidade:** 🔴 Crítico

#### **Sintomas:**
- Página não abre no navegador
- Erro de conexão recusada
- Timeout na conexão

#### **Possíveis Causas e Soluções:**

**1. Servidor não está rodando**
```bash
# Verificar se o processo está ativo
ps aux | grep streamlit
ps aux | grep python

# Iniciar o servidor
streamlit run streamlit_app.py
```

**2. Porta já está em uso**
```bash
# Verificar porta 8501
netstat -tulpn | grep 8501
lsof -i :8501

# Matar processo na porta
kill -9 <PID>

# Ou usar porta diferente
streamlit run streamlit_app.py --server.port 8502
```

**3. Problemas de firewall**
```bash
# Linux - liberar porta
sudo ufw allow 8501

# Windows - verificar Windows Defender
# Adicionar exceção para Python/Streamlit
```

**4. Problemas de DNS/rede**
```bash
# Testar localhost
curl http://localhost:8501

# Testar IP específico
curl http://127.0.0.1:8501

# Verificar conectividade
ping localhost
```

### **Página em branco** {#pagina-branco}
**Severidade:** 🟡 Alto

#### **Sintomas:**
- Página carrega mas fica em branco
- Spinning wheel infinito
- Console do browser mostra erros

#### **Soluções:**

**1. Limpar cache do navegador**
```
# Chrome/Edge
Ctrl + Shift + Delete → Limpar dados

# Firefox
Ctrl + Shift + Delete → Limpar tudo
```

**2. Verificar console do navegador**
```javascript
// Abrir console (F12) e procurar por:
// - Erros 404 (arquivos não encontrados)
// - Erros CORS (política de mesma origem)
// - Erros JavaScript
```

**3. Recarregar aplicação**
```bash
# Parar aplicação (Ctrl+C)
# Limpar cache do Streamlit
rm -rf ~/.streamlit/

# Reiniciar aplicação
streamlit run streamlit_app.py --server.enableCORS false
```

**4. Verificar logs da aplicação**
```bash
# Verificar logs no terminal
# Procurar por stack traces ou erros
tail -f logs/app.log
```

### **Login não funciona** {#login-nao-funciona}
**Severidade:** 🟡 Alto

#### **Sintomas:**
- Credenciais rejeitadas
- Página de login não responde
- Erro de autenticação

#### **Soluções:**

**1. Verificar credenciais padrão**
```python
# Credenciais padrão (se não configurado)
Usuário: admin
Senha: admin123

# Ou verificar em core/auth.py
ADMIN_CREDENTIALS = {
    "admin": "senha_secreta"
}
```

**2. Reset de senha**
```bash
# Executar script de reset (se disponível)
python scripts/reset_password.py

# Ou editar diretamente core/auth.py
```

**3. Verificar configuração de autenticação**
```python
# Em core/auth.py, verificar função login()
def login(username: str, password: str) -> bool:
    # Adicionar debug
    print(f"Tentativa de login: {username}")
    return verificar_credenciais(username, password)
```

**4. Problema de sessão**
```bash
# Limpar dados de sessão
rm -rf data/sessions/*

# Reiniciar aplicação
```

### **Gráficos não aparecem** {#graficos-nao-aparecem}
**Severidade:** 🟡 Alto

#### **Sintomas:**
- Consulta processa mas gráfico não carrega
- Erro "Unable to render chart"
- Espaço em branco onde deveria estar o gráfico

#### **Soluções:**

**1. Verificar dependências de visualização**
```bash
# Instalar/atualizar bibliotecas
pip install plotly==5.17.0
pip install streamlit-plotly-events

# Verificar imports
python -c "import plotly.graph_objects as go; print('OK')"
```

**2. Verificar dados do gráfico**
```python
# Debug em core/agents/code_gen_agent.py
def generate_code(self, requirements: str) -> str:
    code = self.llm_adapter.invoke(prompt).content
    print(f"Código gerado: {code}")  # Debug
    return code
```

**3. Problema de memória**
```bash
# Verificar uso de memória
htop
free -h

# Reduzir tamanho do dataset se necessário
# Usar sample em pandas
df_sample = df.sample(n=1000)
```

**4. Verificar logs de erro**
```bash
# Procurar por erros de Plotly
grep -i "plotly\|chart\|graph" logs/app.log
```

---

## 💬 **Problemas de Consulta** {#consulta}

### **Respostas incorretas** {#respostas-incorretas}
**Severidade:** 🟡 Alto

#### **Sintomas:**
- Sistema responde com dados errados
- Interpretação incorreta da pergunta
- Gráficos com dados irrelevantes

#### **Soluções:**

**1. Melhorar a pergunta**
```
❌ Ruim: "Mostre vendas"
✅ Bom: "Mostre a evolução das vendas mensais dos últimos 6 meses"

❌ Ruim: "Produtos"
✅ Bom: "Quais são os 10 produtos mais vendidos em agosto de 2025?"
```

**2. Verificar catálogo de dados**
```bash
# Acessar "Gerenciar Catálogo" na interface
# Ou verificar data/catalog_cleaned.json
cat data/catalog_cleaned.json | jq '.codigo'
```

**3. Verificar dados disponíveis**
```python
# Testar consulta simples primeiro
"Quantos produtos temos no total?"
"Qual é o período dos dados disponíveis?"
```

**4. Debug do processo de classificação**
```python
# Em core/agents/bi_agent_nodes.py
def classify_intent(state: AgentState, llm_adapter: BaseLLMAdapter) -> Dict[str, Any]:
    user_query = state['messages'][-1].content
    print(f"Query: {user_query}")  # Debug
    # ... resto da função
    print(f"Intent classificado: {intent}")  # Debug
```

### **Sistema muito lento** {#sistema-lento}
**Severidade:** 🟡 Alto

#### **Sintomas:**
- Respostas demoram mais de 10 segundos
- Interface trava durante processamento
- Timeout nas consultas

#### **Soluções:**

**1. Otimizar consultas**
```
❌ Evitar: "Analise todos os dados de vendas de todos os anos"
✅ Preferir: "Vendas dos últimos 3 meses"

❌ Evitar: Múltiplas perguntas complexas simultâneas
✅ Preferir: Uma pergunta específica por vez
```

**2. Verificar recursos do sistema**
```bash
# CPU e memória
htop
free -h

# Espaço em disco
df -h

# Processos pesados
ps aux --sort=-%cpu | head -10
```

**3. Otimizar configuração**
```python
# Em core/config/settings.py
class Settings(BaseSettings):
    LLM_TIMEOUT: int = 30  # Aumentar se necessário
    MAX_TOKENS: int = 1000  # Reduzir para respostas mais rápidas
    CACHE_ENABLED: bool = True  # Habilitar cache
```

**4. Verificar conexão de rede**
```bash
# Testar latência para OpenAI
ping api.openai.com

# Testar velocidade de download
curl -o /dev/null -s -w '%{time_total}\n' https://api.openai.com
```

### **Erro "Não encontrei dados"** {#nao-encontrei-dados}
**Severidade:** 🟢 Baixo

#### **Sintomas:**
- Sistema responde que não encontrou informações
- Dados existem mas não são localizados
- Filtros muito restritivos

#### **Soluções:**

**1. Verificar se dados existem**
```python
# Testar no Python
import pandas as pd
df = pd.read_parquet('data/parquet/admmat.parquet')
print(f"Total de registros: {len(df)}")
print(f"Colunas disponíveis: {df.columns.tolist()}")
print(f"Periodo dos dados: {df['data_ultima_venda'].min()} até {df['data_ultima_venda'].max()}")
```

**2. Usar termos mais genéricos**
```
❌ Específico demais: "Produto código 999999999"
✅ Mais genérico: "Produtos da categoria eletrônicos"

❌ Data muito específica: "Vendas do dia 15/03/2025"
✅ Período mais amplo: "Vendas de março de 2025"
```

**3. Verificar filtros aplicados**
```python
# Debug em core/connectivity/parquet_adapter.py
def query_data(self, filters: Dict[str, Any]) -> pd.DataFrame:
    df = self.load_data()
    print(f"Dataset original: {len(df)} registros")

    for column, value in filters.items():
        if column in df.columns:
            df_before = len(df)
            df = df[df[column] == value]
            print(f"Filtro {column}={value}: {df_before} → {len(df)} registros")

    return df
```

**4. Verificar formato dos dados**
```python
# Verificar tipos de dados
df.dtypes
df.describe()

# Valores únicos em colunas categóricas
df['categoria'].value_counts()
df['fornecedor'].value_counts()
```

### **Consulta trava** {#consulta-trava}
**Severidade:** 🔴 Crítico

#### **Sintomas:**
- Interface para de responder
- Consulta não termina nunca
- Necessário recarregar página

#### **Soluções:**

**1. Verificar loops infinitos**
```python
# Em core/graph/graph_builder.py
# Adicionar logs para debug do fluxo
def _decide_after_intent_classification(self, state: AgentState) -> str:
    intent = state.get("intent")
    print(f"DEBUG: Roteando intent: {intent}")  # Debug
    # ... resto da função
```

**2. Configurar timeouts**
```python
# Em core/config/settings.py
LLM_TIMEOUT = 30  # segundos
QUERY_TIMEOUT = 60  # segundos

# Em código que chama LLM
response = llm_adapter.invoke(prompt, timeout=30)
```

**3. Verificar estado da sessão**
```python
# Limpar estado corrompido
if 'agent_graph' in st.session_state:
    del st.session_state.agent_graph
st.experimental_rerun()
```

**4. Monitorar recursos**
```bash
# Memory leak ou CPU 100%
watch -n 1 'ps aux | grep python'

# Matar processo se necessário
pkill -f streamlit
pkill -f "python main.py"
```

---

## 🔧 **Problemas Técnicos** {#tecnicos}

### **Erro de conexão** {#erro-conexao}
**Severidade:** 🔴 Crítico

#### **Sintomas:**
- "Connection refused"
- "Network unreachable"
- "Timeout error"

#### **Soluções:**

**1. Verificar conectividade básica**
```bash
# Internet
ping 8.8.8.8

# DNS
nslookup api.openai.com

# Porta específica
telnet api.openai.com 443
```

**2. Verificar proxy/firewall**
```bash
# Configurar proxy se necessário
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# Ou no código Python
import os
os.environ['HTTP_PROXY'] = 'http://proxy.company.com:8080'
```

**3. Verificar certificados SSL**
```bash
# Testar SSL
openssl s_client -connect api.openai.com:443

# Verificar certificados do sistema
python -c "import ssl; print(ssl.get_default_verify_paths())"
```

**4. Configurar retry e timeout**
```python
# Em core/llm_adapter.py
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)
```

### **Problemas de performance** {#performance}
**Severidade:** 🟡 Alto

#### **Sintomas:**
- Sistema lento em geral
- Alto uso de CPU/memória
- Aplicação trava frequentemente

#### **Soluções:**

**1. Monitorar recursos**
```bash
# Monitoramento contínuo
htop
iotop  # I/O disk
nethogs  # Network usage

# Profiling da aplicação Python
pip install py-spy
py-spy top --pid <python_pid>
```

**2. Otimizar carregamento de dados**
```python
# Em core/connectivity/parquet_adapter.py
class ParquetAdapter:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._dataframe = None  # Lazy loading

    def load_data(self) -> pd.DataFrame:
        if self._dataframe is None:
            # Carregar apenas colunas necessárias
            self._dataframe = pd.read_parquet(
                self.file_path,
                columns=['codigo', 'descricao', 'preco', 'estoque']  # Especificar colunas
            )
        return self._dataframe
```

**3. Implementar cache**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_query(query_hash: str, filters: str) -> pd.DataFrame:
    # Cache de consultas frequentes
    return execute_query(filters)
```

**4. Configurar garbage collection**
```python
import gc

# Forçar limpeza de memória periodicamente
gc.collect()

# Monitorar uso de memória
import psutil
process = psutil.Process()
print(f"Memória: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

### **Erros de API** {#erros-api}
**Severidade:** 🟡 Alto

#### **Sintomas:**
- Erro 401, 403, 429, 500 da API
- "API key invalid"
- "Rate limit exceeded"

#### **Soluções:**

**1. Verificar chave da API**
```bash
# Verificar variável de ambiente
echo $OPENAI_API_KEY

# Testar chave manualmente
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**2. Problemas de rate limit**
```python
# Implementar backoff exponencial
import time
import random

def api_call_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
                continue
            raise e
```

**3. Verificar quota da API**
```bash
# Verificar uso atual da OpenAI
curl https://api.openai.com/v1/usage \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**4. Configurar fallback**
```python
# Em core/llm_adapter.py
class OpenAILLMAdapter:
    def invoke(self, prompt: str) -> str:
        try:
            return self._call_openai(prompt)
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            # Fallback para resposta padrão
            return "Desculpe, não foi possível processar sua consulta no momento."
```

### **Problemas de dados** {#problemas-dados}
**Severidade:** 🟡 Alto

#### **Sintomas:**
- Dados corrompidos
- Arquivo Parquet não abre
- Erro de schema

#### **Soluções:**

**1. Verificar integridade do arquivo**
```bash
# Verificar se arquivo existe e tem tamanho
ls -la data/parquet/admmat.parquet

# Verificar integridade do Parquet
python -c "
import pandas as pd
try:
    df = pd.read_parquet('data/parquet/admmat.parquet')
    print(f'OK: {len(df)} registros carregados')
    print(f'Colunas: {df.columns.tolist()}')
except Exception as e:
    print(f'Erro: {e}')
"
```

**2. Backup e recuperação**
```bash
# Verificar backups disponíveis
ls -la data/parquet/

# Usar arquivo de backup se disponível
cp data/parquet/admatao_full.parquet data/parquet/admmat.parquet
```

**3. Regenerar dados se necessário**
```bash
# Se houver script de ETL
python scripts/generate_parquet.py

# Ou conectar diretamente ao banco
python scripts/export_to_parquet.py
```

**4. Verificar schema compatibility**
```python
# Verificar mudanças no schema
import pandas as pd
import pyarrow.parquet as pq

schema = pq.read_schema('data/parquet/admmat.parquet')
print(schema)

# Verificar tipos incompatíveis
df = pd.read_parquet('data/parquet/admmat.parquet')
print(df.dtypes)
```

---

## 🛡️ **Problemas de Configuração** {#configuracao}

### **Variáveis de ambiente** {#variaveis-ambiente}
**Severidade:** 🔴 Crítico

#### **Sintomas:**
- "Environment variable not found"
- Configurações não carregam
- API keys não funcionam

#### **Soluções:**

**1. Verificar arquivo .env**
```bash
# Verificar se existe
ls -la .env

# Verificar conteúdo (sem mostrar senhas)
grep -v "PASSWORD\|KEY" .env

# Criar se não existir
cp .env.example .env
```

**2. Formato correto do .env**
```bash
# Formato correto (sem espaços ao redor do =)
OPENAI_API_KEY=sk-1234567890abcdef
MSSQL_SERVER=servidor.exemplo.com
MSSQL_DATABASE=nome_banco

# Formato incorreto (com espaços)
OPENAI_API_KEY = sk-1234567890abcdef  # ❌
```

**3. Verificar carregamento**
```python
# Debug em core/config/settings.py
from dotenv import load_dotenv
import os

load_dotenv()
print(f"OPENAI_API_KEY definida: {'OPENAI_API_KEY' in os.environ}")
print(f"MSSQL_SERVER: {os.getenv('MSSQL_SERVER', 'NÃO DEFINIDO')}")
```

**4. Permissões do arquivo**
```bash
# Verificar permissões
ls -la .env

# Corrigir se necessário
chmod 600 .env  # Apenas owner pode ler/escrever
```

### **Problemas de permissão** {#permissoes}
**Severidade:** 🟡 Alto

#### **Sintomas:**
- "Permission denied"
- Não consegue escrever logs
- Não consegue acessar arquivos

#### **Soluções:**

**1. Verificar permissões de diretórios**
```bash
# Verificar permissões principais
ls -la logs/
ls -la data/
ls -la data/parquet/

# Corrigir permissões se necessário
chmod 755 logs/ data/
chmod 644 data/parquet/*.parquet
```

**2. Criar diretórios necessários**
```bash
# Criar se não existirem
mkdir -p logs data/sessions data/cache

# Definir permissões adequadas
chmod 755 logs data
chmod 700 data/sessions  # Dados sensíveis
```

**3. Verificar usuário e grupo**
```bash
# Verificar proprietário dos arquivos
ls -la data/

# Alterar proprietário se necessário
chown -R $USER:$USER data/ logs/
```

**4. SELinux/AppArmor (Linux)**
```bash
# Verificar se SELinux está causando problemas
getenforce
sestatus

# Verificar logs do SELinux
ausearch -m avc -ts recent

# Desabilitar temporariamente se necessário
sudo setenforce 0
```

### **Configuração de banco** {#config-banco}
**Severidade:** 🟡 Alto

#### **Sintomas:**
- Não conecta com SQL Server
- Timeout de conexão
- Erro de autenticação

#### **Soluções:**

**1. Testar conectividade básica**
```bash
# Testar se porta está aberta
telnet servidor.exemplo.com 1433

# Ping básico
ping servidor.exemplo.com
```

**2. Verificar string de conexão**
```python
# Testar conexão manualmente
import pyodbc

connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=servidor.exemplo.com;"
    "DATABASE=nome_banco;"
    "UID=usuario;"
    "PWD=senha;"
)

try:
    conn = pyodbc.connect(connection_string)
    print("Conexão OK!")
    conn.close()
except Exception as e:
    print(f"Erro: {e}")
```

**3. Verificar driver ODBC**
```bash
# Listar drivers instalados
odbcinst -q -d

# Instalar driver se necessário (Ubuntu/Debian)
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/msprod.list
sudo apt-get update
sudo apt-get install msodbcsql17
```

**4. Configurar firewall do SQL Server**
```sql
-- No SQL Server, verificar se TCP/IP está habilitado
-- SQL Server Configuration Manager → Protocols → TCP/IP → Enabled

-- Verificar porta (padrão 1433)
-- SQL Server Configuration Manager → TCP/IP → Properties → IP Addresses
```

---

## 🚨 **Problemas Críticos de Sistema**

### **Sistema totalmente inoperante**
**Severidade:** 🔴 Crítico

#### **Lista de Verificação Rápida:**
```bash
# 1. Verificar processos
ps aux | grep -E "(streamlit|python)"

# 2. Verificar portas
netstat -tulpn | grep -E "(8501|8000)"

# 3. Verificar logs
tail -f logs/app.log

# 4. Verificar espaço em disco
df -h

# 5. Verificar memória
free -h

# 6. Reiniciar completo
pkill -f streamlit
pkill -f python
streamlit run streamlit_app.py
```

### **Recuperação de emergência**
```bash
#!/bin/bash
# Script de recuperação de emergência

echo "=== RECUPERAÇÃO DE EMERGÊNCIA AGENT_BI ==="

# Parar tudo
pkill -f streamlit
pkill -f python
sleep 5

# Verificar dependências críticas
python -c "import streamlit, pandas, plotly" || {
    echo "ERRO: Dependências não encontradas"
    pip install -r requirements.txt
}

# Verificar arquivos críticos
test -f "data/parquet/admmat.parquet" || {
    echo "ERRO: Arquivo de dados não encontrado"
    exit 1
}

test -f ".env" || {
    echo "AVISO: Arquivo .env não encontrado"
    cp .env.example .env
}

# Criar diretórios necessários
mkdir -p logs data/sessions data/cache

# Limpar cache corrompido
rm -rf ~/.streamlit/

# Reiniciar aplicação
echo "Iniciando aplicação..."
streamlit run streamlit_app.py --server.port 8501 &

echo "Sistema reiniciado. Aguarde 30 segundos e acesse http://localhost:8501"
```

---

## 📊 **Monitoramento Preventivo**

### **Script de health check**
```bash
#!/bin/bash
# health_check.sh - Executar a cada 5 minutos

LOG_FILE="logs/health_check.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Verificar se aplicação responde
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501)

if [ "$HTTP_STATUS" -eq "200" ]; then
    echo "$TIMESTAMP [OK] Sistema operacional" >> $LOG_FILE
else
    echo "$TIMESTAMP [ERRO] Sistema não responde (HTTP $HTTP_STATUS)" >> $LOG_FILE
    # Reiniciar automaticamente
    pkill -f streamlit
    streamlit run streamlit_app.py &
fi

# Verificar uso de memória
MEM_USAGE=$(ps aux --no-headers -C python3 | awk '{sum+=$4} END {print sum}')
if (( $(echo "$MEM_USAGE > 80" | bc -l) )); then
    echo "$TIMESTAMP [AVISO] Alto uso de memória: ${MEM_USAGE}%" >> $LOG_FILE
fi

# Verificar espaço em disco
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo "$TIMESTAMP [AVISO] Pouco espaço em disco: ${DISK_USAGE}%" >> $LOG_FILE
fi
```

### **Cron job para monitoramento**
```bash
# Adicionar ao crontab
crontab -e

# Executar health check a cada 5 minutos
*/5 * * * * /path/to/agent_bi/health_check.sh

# Backup diário dos dados
0 2 * * * cp /path/to/agent_bi/data/parquet/admmat.parquet /backup/admmat_$(date +\%Y\%m\%d).parquet
```

---

## 📞 **Contatos de Suporte**

### **Suporte por Nível**

**🆘 Suporte Urgente (24/7)**
- **Problemas Críticos**: Sistema completamente inoperante
- **Contato**: emergency@company.com
- **WhatsApp**: +55 11 9999-9999
- **Slack**: #emergency-support

**🔧 Suporte Técnico (8h-18h)**
- **Problemas de Configuração**: Banco, API, Performance
- **Contato**: tech-support@company.com
- **Teams**: Agent BI Tech Support
- **Ticket**: https://support.company.com

**👥 Suporte de Usuário (8h-18h)**
- **Dúvidas de Uso**: Como fazer perguntas, interpretar resultados
- **Contato**: user-support@company.com
- **Chat**: Disponível na interface
- **FAQ**: https://docs.company.com/faq

### **Informações para Reporte de Problema**

**Sempre incluir:**
```
1. Data/hora do problema
2. Descrição detalhada do que aconteceu
3. Passos para reproduzir
4. Mensagens de erro (screenshots)
5. Versão do sistema (disponível em /api/v1/info)
6. Navegador e versão (se problema de interface)
7. Logs relevantes (últimas 50 linhas)
```

**Template de reporte:**
```
Assunto: [URGENTE/NORMAL] Problema com Agent_BI

Data/Hora: 2025-09-21 10:30
Severidade: [Crítico/Alto/Baixo]

Descrição:
[O que aconteceu?]

Passos para reproduzir:
1. [Primeiro passo]
2. [Segundo passo]
3. [Resultado]

Erro observado:
[Mensagem de erro ou screenshot]

Ambiente:
- SO: [Windows/Linux/Mac]
- Navegador: [Chrome/Firefox/Safari]
- Versão do Agent_BI: [Verificar em /api/v1/info]

Logs:
[Colar últimas linhas relevantes dos logs]
```

---

**📝 Este guia é atualizado regularmente com base em problemas reportados.**
**🔄 Última atualização:** 21 de setembro de 2025
**📧 Sugestões de melhoria:** docs@company.com