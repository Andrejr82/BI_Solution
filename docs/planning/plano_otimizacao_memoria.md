# Plano de Otimização de Memória para o Streamlit Cloud

**Objetivo:** Reduzir drasticamente o consumo de memória da aplicação para garantir sua estabilidade no Streamlit Cloud e evitar que seja encerrada por excesso de recursos.

**Estratégia:** Mudar a forma como a aplicação lê e gerencia o arquivo de dados (`admmat.parquet`), que é a principal fonte do alto consumo de memória. A ideia é: **ler menos e reutilizar mais**.

---

### **Passos de Execução:**

**Passo 1: Otimizar a Validação Inicial (Arquivo: `streamlit_app.py`)**

*   **O que faremos:** Vamos substituir a validação inicial que hoje lê o arquivo de dados inteiro usando `pandas.read_parquet()`.
*   **Como faremos:** Usaremos a biblioteca `pyarrow` para ler apenas os metadados do arquivo (nomes das colunas e número de linhas), sem carregar nenhum dado em memória.
*   **Benefício Imediato:** Uma redução massiva no uso de memória durante a inicialização do aplicativo.

**Passo 2: Centralizar o Carregamento de Dados (Arquivo: `streamlit_app.py`)**

*   **O que faremos:** Garantiremos que o `ParquetAdapter` (o componente que lê os dados) seja criado **apenas uma vez** por sessão de usuário.
*   **Como faremos:** Vamos inicializá-lo dentro da função `initialize_backend`, que já possui o cache (`@st.cache_resource`), e o manteremos disponível no estado da sessão (`st.session_state`).
*   **Benefício Imediato:** O arquivo de dados será lido do disco e carregado na memória apenas uma única vez, não a cada nova pergunta.

**Passo 3: Reutilizar os Dados Carregados (Arquivo: `streamlit_app.py`)**

*   **O que faremos:** Modificaremos a função `query_backend` (que processa as perguntas do usuário).
*   **Como faremos:** Em vez de criar um novo `ParquetAdapter` a cada chamada, ela passará a usar a instância única que foi criada e armazenada no Passo 2.
*   **Benefício Imediato:** As consultas serão mais rápidas e o consumo de memória se manterá estável, pois não haverá mais recarregamento de dados.

**Passo 4 (Opcional, mas recomendado): Limitar o Histórico de Conversa**

*   **O que faremos:** Podemos limitar o número de mensagens antigas que ficam armazenadas na memória.
*   **Como faremos:** Manteremos, por exemplo, apenas as últimas 20 trocas de mensagens na sessão.
*   **Benefício Imediato:** Evita que o uso de memória cresça indefinidamente em conversas muito longas.

---

**Resultado Final Esperado:**

Uma aplicação muito mais leve, rápida e, o mais importante, **estável** no Streamlit Cloud, eliminando as quedas por excesso de memória.
