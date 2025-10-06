"""
Página de Transferências entre UNEs
Permite solicitar transferências de produtos entre lojas/depósitos
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import json

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuração da página
st.set_page_config(
    page_title="Transferências entre UNEs",
    page_icon="📦",
    layout="wide"
)

# Verificar autenticação
if not st.session_state.get("authenticated"):
    st.warning("⚠️ Por favor, faça login na página principal")
    st.stop()

# Importar backend
from core.connectivity.hybrid_adapter import HybridDataAdapter

# Inicializar adapter se não existir
if 'transfer_adapter' not in st.session_state:
    st.session_state.transfer_adapter = HybridDataAdapter()

adapter = st.session_state.transfer_adapter

# Título
st.title("📦 Transferências entre UNEs")
st.markdown("Solicite transferências de produtos entre lojas e depósito central")

# --- FUNÇÃO: Carregar UNEs disponíveis ---
@st.cache_data(ttl=300)
def get_unes_disponiveis():
    """Retorna lista de UNEs disponíveis"""
    try:
        result = adapter.execute_query({})
        if result:
            df = pd.DataFrame(result)
            if 'une' in df.columns and 'une_nome' in df.columns:
                unes = df[['une', 'une_nome']].drop_duplicates().sort_values('une')
                return unes.to_dict('records')
    except Exception as e:
        st.error(f"Erro ao carregar UNEs: {e}")
    return []

# --- FUNÇÃO: Carregar produtos da UNE ---
@st.cache_data(ttl=300)
def get_produtos_une(une_id):
    """Retorna produtos disponíveis em uma UNE"""
    try:
        result = adapter.execute_query({'une': une_id})
        if result:
            df = pd.DataFrame(result)

            # Selecionar colunas relevantes
            cols_relevantes = ['codigo', 'nome_produto', 'estoque_atual', 'venda_30_d',
                             'preco_38_percent', 'nomesegmento', 'NOMEFABRICANTE']
            cols_existentes = [c for c in cols_relevantes if c in df.columns]

            if cols_existentes:
                df_produtos = df[cols_existentes].copy()

                # Garantir que estoque_atual existe e é numérico
                if 'estoque_atual' not in df_produtos.columns:
                    df_produtos['estoque_atual'] = 0
                else:
                    df_produtos['estoque_atual'] = pd.to_numeric(df_produtos['estoque_atual'], errors='coerce').fillna(0)

                # Filtrar apenas produtos com estoque > 0
                df_produtos = df_produtos[df_produtos['estoque_atual'] > 0]

                return df_produtos.to_dict('records')
    except Exception as e:
        st.error(f"Erro ao carregar produtos: {e}")
    return []

# --- SIDEBAR: Configuração da Transferência ---
st.sidebar.header("🔧 Configuração")

# Carregar UNEs
unes = get_unes_disponiveis()

if not unes:
    st.error("❌ Nenhuma UNE encontrada. Verifique a conexão com o banco de dados.")
    st.stop()

# Criar dicionário UNE -> Nome
une_map = {u['une']: f"UNE {u['une']} - {u['une_nome']}" for u in unes}
une_ids = list(une_map.keys())

# MODO DE TRANSFERÊNCIA
st.sidebar.subheader("🔀 Modo de Transferência")
modo_transferencia = st.sidebar.radio(
    "Selecione o modo",
    ["1 → 1 (Uma origem, um destino)",
     "1 → N (Uma origem, múltiplos destinos)",
     "N → N (Múltiplas origens, múltiplos destinos)"],
    key='modo_transferencia'
)

st.sidebar.markdown("---")

# Seleção de UNE(s) Origem
st.sidebar.subheader("📍 Origem")

if "N → N" in modo_transferencia:
    # Modo N→N: múltiplas origens
    unes_origem = st.sidebar.multiselect(
        "Selecione UNEs de origem",
        une_ids,
        format_func=lambda x: une_map[x],
        key='unes_origem_multi'
    )
    if not unes_origem:
        st.sidebar.warning("⚠️ Selecione pelo menos uma UNE de origem")
else:
    # Modo 1→1 ou 1→N: uma origem
    une_origem_single = st.sidebar.selectbox(
        "Selecione a UNE de origem",
        une_ids,
        format_func=lambda x: une_map[x],
        key='une_origem_single'
    )
    unes_origem = [une_origem_single]

# Seleção de UNE(s) Destino
st.sidebar.subheader("📍 Destino")

if "1 → 1" in modo_transferencia:
    # Modo 1→1: um destino
    unes_destino_disponiveis = [u for u in une_ids if u not in unes_origem]
    if unes_destino_disponiveis:
        une_destino_single = st.sidebar.selectbox(
            "Selecione a UNE de destino",
            unes_destino_disponiveis,
            format_func=lambda x: une_map[x],
            key='une_destino_single'
        )
        unes_destino = [une_destino_single]
    else:
        st.sidebar.error("❌ Nenhuma UNE disponível para destino")
        unes_destino = []
else:
    # Modo 1→N ou N→N: múltiplos destinos
    unes_destino_disponiveis = [u for u in une_ids if u not in unes_origem]
    unes_destino = st.sidebar.multiselect(
        "Selecione UNEs de destino",
        unes_destino_disponiveis,
        format_func=lambda x: une_map[x],
        key='unes_destino_multi'
    )
    if not unes_destino:
        st.sidebar.warning("⚠️ Selecione pelo menos uma UNE de destino")

st.sidebar.markdown("---")

# Informações da transferência
if unes_origem and unes_destino:
    origem_str = ", ".join([f"UNE {u}" for u in unes_origem])
    destino_str = ", ".join([f"UNE {u}" for u in unes_destino])

    st.sidebar.info(f"""
**Transferência:**
- **Modo:** {modo_transferencia.split(' ')[0]}
- **Origem:** {origem_str}
- **Destino:** {destino_str}
""")
else:
    st.sidebar.warning("⚠️ Configure origem e destino")

# Validar configuração
if not unes_origem or not unes_destino:
    st.warning("⚠️ Configure origem e destino na barra lateral")
    st.stop()

# --- ÁREA PRINCIPAL: Seleção de Produtos ---
if "N → N" in modo_transferencia:
    st.subheader(f"🔍 Produtos disponíveis - {len(unes_origem)} UNEs de origem")
else:
    st.subheader(f"🔍 Produtos disponíveis na UNE {unes_origem[0]}")

# Carregar produtos de todas as UNEs de origem
produtos_por_une = {}
with st.spinner("Carregando produtos..."):
    for une in unes_origem:
        prods = get_produtos_une(une)
        if prods:
            produtos_por_une[une] = prods

if not produtos_por_une:
    st.warning(f"⚠️ Nenhum produto com estoque encontrado nas UNEs selecionadas")
    st.stop()

# Combinar produtos de todas as origens
produtos_todos = []
for une, prods in produtos_por_une.items():
    for p in prods:
        p['une_origem'] = une  # Adicionar UNE de origem
        produtos_todos.append(p)

produtos = produtos_todos

# Filtros
col1, col2, col3, col4 = st.columns(4)

with col1:
    busca = st.text_input("🔎 Buscar (ex: tnt, 25., 123)", "",
                          help="Digite código/nome. Use ponto final (25.) para busca exata")

with col2:
    segmentos = list(set([p.get('nomesegmento', 'N/A') for p in produtos if p.get('nomesegmento')]))
    segmento_filtro = st.selectbox("Segmento", ["Todos"] + sorted(segmentos))

with col3:
    fabricantes = list(set([p.get('NOMEFABRICANTE', 'N/A') for p in produtos if p.get('NOMEFABRICANTE')]))
    fabricante_filtro = st.selectbox("Fabricante", ["Todos"] + sorted(fabricantes))

with col4:
    min_estoque = st.number_input("Estoque mín.", min_value=0, value=0)

# Aplicar filtros
produtos_filtrados = produtos.copy()

if busca:
    busca_norm = busca.strip().replace('%', '')

    # Busca exata se terminar com ponto
    if busca_norm.endswith('.'):
        busca_exata = busca_norm[:-1]  # Remove o ponto
        produtos_filtrados = [
            p for p in produtos_filtrados
            if str(p.get('codigo', '')).replace('.0', '').strip() == busca_exata
            or p.get('nome_produto', '').strip().lower() == busca_exata.lower()
        ]
    else:
        # Busca parcial
        produtos_filtrados = [
            p for p in produtos_filtrados
            if busca_norm.lower() in str(p.get('codigo', '')).replace('.0', '').strip().lower()
            or busca_norm.lower() in str(p.get('nome_produto', '')).strip().lower()
        ]

if segmento_filtro != "Todos":
    produtos_filtrados = [p for p in produtos_filtrados if p.get('nomesegmento') == segmento_filtro]

if fabricante_filtro != "Todos":
    produtos_filtrados = [p for p in produtos_filtrados if p.get('NOMEFABRICANTE') == fabricante_filtro]

if min_estoque > 0:
    produtos_filtrados = [p for p in produtos_filtrados if p.get('estoque_atual', 0) >= min_estoque]

st.info(f"📊 **{len(produtos_filtrados)}** produtos encontrados (de {len(produtos)} total)")

# --- TABELA DE SELEÇÃO ---
if produtos_filtrados:
    st.markdown("### ✅ Selecione os produtos para transferir")

    # Inicializar carrinho se não existir
    if 'carrinho_transferencia' not in st.session_state:
        st.session_state.carrinho_transferencia = {}

    # Mostrar produtos
    df_produtos = pd.DataFrame(produtos_filtrados)

    # Formatação
    if 'preco_38_percent' in df_produtos.columns:
        df_produtos['preco_38_percent'] = pd.to_numeric(df_produtos['preco_38_percent'], errors='coerce')
        df_produtos['preco_38_percent'] = df_produtos['preco_38_percent'].apply(
            lambda x: f"R$ {x:.2f}" if pd.notna(x) else "N/A"
        )

    # Exibir tabela (paginação manual)
    items_per_page = 10
    total_pages = (len(df_produtos) - 1) // items_per_page + 1

    page = st.number_input("Página", min_value=1, max_value=total_pages, value=1, step=1)

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    df_page = df_produtos.iloc[start_idx:end_idx]

    # Colunas a exibir (incluir une_origem se houver múltiplas origens)
    cols_display = ['codigo', 'nome_produto', 'estoque_atual', 'venda_30_d', 'preco_38_percent', 'nomesegmento', 'NOMEFABRICANTE']
    if 'une_origem' in df_page.columns and len(unes_origem) > 1:
        cols_display.insert(0, 'une_origem')

    st.dataframe(
        df_page[[c for c in cols_display if c in df_page.columns]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown(f"Mostrando {start_idx+1}-{min(end_idx, len(df_produtos))} de {len(df_produtos)} produtos")

    # --- ADICIONAR AO CARRINHO ---
    st.markdown("---")
    st.subheader("🛒 Adicionar ao Carrinho")

    # Modo 1→N ou N→N: permitir distribuição de quantidade por destino
    if len(unes_destino) > 1:
        st.info(f"💡 **Modo distribuição:** Defina quantidades para cada UNE de destino")

        codigo_add = st.text_input("Código do produto", key='codigo_add_multi')

        if codigo_add:
            # Verificar se produto existe
            produto = next((p for p in produtos_filtrados if str(p.get('codigo')) == str(codigo_add)), None)

            if produto:
                estoque_total = produto.get('estoque_atual', 0)
                une_origem_prod = produto.get('une_origem', unes_origem[0])

                st.write(f"**Produto:** {produto.get('nome_produto')} | **Estoque UNE {une_origem_prod}:** {estoque_total}")

                # Input de quantidade por destino
                st.write("**Distribuição por destino:**")
                distribuicao = {}
                total_distribuido = 0

                cols = st.columns(min(len(unes_destino), 4))
                for idx, une_dest in enumerate(unes_destino):
                    with cols[idx % 4]:
                        qtd = st.number_input(
                            f"UNE {une_dest}",
                            min_value=0,
                            value=0,
                            key=f'dist_{codigo_add}_{une_dest}'
                        )
                        distribuicao[une_dest] = qtd
                        total_distribuido += qtd

                st.write(f"**Total:** {total_distribuido} / {estoque_total}")

                if st.button("➕ Adicionar com distribuição", use_container_width=True):
                    if total_distribuido > estoque_total:
                        st.error(f"❌ Total distribuído ({total_distribuido}) > estoque ({estoque_total})")
                    elif total_distribuido == 0:
                        st.warning("⚠️ Defina pelo menos uma quantidade")
                    else:
                        # Criar chave única: codigo_une_origem
                        chave = f"{codigo_add}_UNE{une_origem_prod}"
                        st.session_state.carrinho_transferencia[chave] = {
                            'produto': produto,
                            'une_origem': une_origem_prod,
                            'distribuicao': distribuicao,
                            'total': total_distribuido,
                            'preco': produto.get('preco_38_percent', 0),
                            'valor_total_item': total_distribuido * pd.to_numeric(produto.get('preco_38_percent', 0), errors='coerce')
                        }
                        st.success(f"✅ Produto adicionado com {total_distribuido} unidades distribuídas!")
                        st.rerun()
            else:
                st.error(f"❌ Produto {codigo_add} não encontrado")

    else:
        # Modo 1→1: quantidade única
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            codigo_add = st.text_input("Código do produto", key='codigo_add_single')

        with col2:
            qtd_add = st.number_input("Quantidade", min_value=1, value=1, key='qtd_add_single')

        with col3:
            st.write("")  # Espaço
            st.write("")  # Espaço
            if st.button("➕ Adicionar", use_container_width=True):
                if codigo_add:
                    produto = next((p for p in produtos_filtrados if str(p.get('codigo')) == str(codigo_add)), None)

                    if produto:
                        estoque = produto.get('estoque_atual', 0)
                        une_origem_prod = produto.get('une_origem', unes_origem[0])

                        if qtd_add > estoque:
                            st.error(f"❌ Quantidade ({qtd_add}) > estoque ({estoque})")
                        else:
                            chave = f"{codigo_add}_UNE{une_origem_prod}"
                            st.session_state.carrinho_transferencia[chave] = {
                                'produto': produto,
                                'une_origem': une_origem_prod,
                                'distribuicao': {unes_destino[0]: qtd_add},
                                'total': qtd_add,
                                'preco': produto.get('preco_38_percent', 0),
                                'valor_total_item': qtd_add * pd.to_numeric(produto.get('preco_38_percent', 0), errors='coerce')
                            }
                            st.success(f"✅ Produto {codigo_add} adicionado!")
                            st.rerun()
                    else:
                        st.error(f"❌ Produto {codigo_add} não encontrado")
                else:
                    st.warning("⚠️ Digite o código do produto")

# --- CARRINHO DE TRANSFERÊNCIA ---
if st.session_state.carrinho_transferencia:
    st.markdown("---")
    st.subheader("🛒 Carrinho de Transferência")

    carrinho_items = []
    total_itens = 0
    total_valor = 0

    for chave, item in st.session_state.carrinho_transferencia.items():
        produto = item['produto']
        une_origem_item = item.get('une_origem', 'N/A')
        distribuicao = item.get('distribuicao', {})
        total_prod = item.get('total', 0)
        valor_total_item = item.get('valor_total_item', 0)

        # Criar string de distribuição
        dist_str = ", ".join([f"UNE {dest}: {qtd}" for dest, qtd in distribuicao.items() if qtd > 0])

        carrinho_items.append({
            'Código': produto.get('codigo'),
            'Produto': produto.get('nome_produto', 'N/A')[:30],
            'Origem': f"UNE {une_origem_item}",
            'Distribuição': dist_str,
            'Total': total_prod,
            'Valor Total': f"R$ {valor_total_item:,.2f}",
            'Estoque': produto.get('estoque_atual', 0)
        })
        total_itens += total_prod
        total_valor += valor_total_item

    df_carrinho = pd.DataFrame(carrinho_items)
    st.dataframe(df_carrinho, use_container_width=True, hide_index=True)

    st.info(f"📦 **{len(carrinho_items)}** produtos | **{total_itens}** unidades | **Valor Total: R$ {total_valor:,.2f}**")

    # Ações do carrinho
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🗑️ Limpar Carrinho", use_container_width=True):
            st.session_state.carrinho_transferencia = {}
            st.rerun()

    with col2:
        codigo_remover = st.text_input("Remover produto (código)", key='codigo_remover')
        if st.button("➖ Remover", use_container_width=True) and codigo_remover:
            # Encontrar chave que contém o código
            chave_encontrada = None
            for chave in st.session_state.carrinho_transferencia.keys():
                if chave.startswith(str(codigo_remover)):
                    chave_encontrada = chave
                    break

            if chave_encontrada:
                del st.session_state.carrinho_transferencia[chave_encontrada]
                st.success(f"✅ Produto {codigo_remover} removido")
                st.rerun()
            else:
                st.error(f"❌ Produto {codigo_remover} não encontrado no carrinho")

    with col3:
        st.write("")  # Espaço

    # --- GERAR SOLICITAÇÃO ---
    st.markdown("---")
    st.subheader("📝 Finalizar Solicitação de Transferência")

    observacoes = st.text_area("Observações (opcional)", "", height=100)

    col1, col2 = st.columns(2)

    with col1:
        prioridade = st.selectbox("Prioridade", ["Normal", "Alta", "Urgente"])

    with col2:
        st.write("")  # Espaço
        st.write("")  # Espaço
        if st.button("✅ Gerar Solicitação", type="primary", use_container_width=True):
            # Gerar solicitação
            solicitacao = {
                'timestamp': datetime.now().isoformat(),
                'usuario': st.session_state.get('username', 'user'),
                'modo': modo_transferencia.split(' ')[0],
                'unes_origem': unes_origem,
                'unes_destino': unes_destino,
                'produtos': st.session_state.carrinho_transferencia,
                'total_produtos': len(carrinho_items),
                'total_itens': total_itens,
                'total_valor': total_valor,
                'prioridade': prioridade,
                'observacoes': observacoes,
                'status': 'PENDENTE'
            }

            # Salvar solicitação
            solicitacao_path = Path(__file__).parent.parent / 'data' / 'transferencias'
            solicitacao_path.mkdir(exist_ok=True)

            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transferencia_{timestamp_str}.json"

            with open(solicitacao_path / filename, 'w', encoding='utf-8') as f:
                json.dump(solicitacao, f, indent=2, ensure_ascii=False)

            origem_str = ", ".join([f"UNE {u}" for u in unes_origem])
            destino_str = ", ".join([f"UNE {u}" for u in unes_destino])

            st.success(f"""
            ✅ **Solicitação gerada com sucesso!**

            **Número:** {timestamp_str}
            **Modo:** {modo_transferencia.split(' ')[0]}
            **Origem:** {origem_str}
            **Destino:** {destino_str}
            **Total de produtos:** {len(carrinho_items)}
            **Total de unidades:** {total_itens}
            **Prioridade:** {prioridade}

            Arquivo salvo: `{filename}`
            """)

            # Limpar carrinho
            st.session_state.carrinho_transferencia = {}

            st.balloons()

else:
    st.info("🛒 Carrinho vazio. Adicione produtos para criar uma solicitação de transferência.")

# --- HISTÓRICO DE TRANSFERÊNCIAS ---
st.markdown("---")
st.subheader("📋 Histórico de Solicitações")

solicitacoes_path = Path(__file__).parent.parent / 'data' / 'transferencias'

if solicitacoes_path.exists():
    solicitacoes_files = sorted(solicitacoes_path.glob("transferencia_*.json"), reverse=True)

    if solicitacoes_files:
        st.info(f"📊 **{len(solicitacoes_files)}** solicitações encontradas")

        # Mostrar últimas 10
        for i, file in enumerate(solicitacoes_files[:10]):
            with open(file, 'r', encoding='utf-8') as f:
                sol = json.load(f)

            # Compatibilidade com formato antigo e novo
            unes_origem_sol = sol.get('unes_origem', [sol.get('une_origem')])
            unes_destino_sol = sol.get('unes_destino', [sol.get('une_destino')])

            origem_str = ", ".join([f"UNE {u}" for u in unes_origem_sol])
            destino_str = ", ".join([f"UNE {u}" for u in unes_destino_sol])
            modo_str = sol.get('modo', '1→1')

            with st.expander(f"📦 {file.stem} - {origem_str} → {destino_str} ({sol['status']})"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.write(f"**Data:** {sol['timestamp'][:16]}")
                    st.write(f"**Usuário:** {sol['usuario']}")
                    st.write(f"**Modo:** {modo_str}")

                with col2:
                    st.write(f"**Prioridade:** {sol['prioridade']}")
                    st.write(f"**Status:** {sol['status']}")

                with col3:
                    st.write(f"**Produtos:** {sol.get('total_produtos', len(sol['produtos']))}")
                    st.write(f"**Total unidades:** {sol['total_itens']}")
                    st.write(f"**Valor Total:** R$ {sol.get('total_valor', 0):,.2f}")

                if sol.get('observacoes'):
                    st.write(f"**Observações:** {sol['observacoes']}")

                # Detalhes dos produtos
                if st.checkbox(f"Ver produtos", key=f"ver_produtos_{i}"):
                    produtos_sol = []
                    for chave, item in sol['produtos'].items():
                        produto = item['produto']
                        une_origem_item = item.get('une_origem', 'N/A')
                        distribuicao = item.get('distribuicao', {item.get('une_destino', 'N/A'): item.get('quantidade', 0)})

                        dist_str = ", ".join([f"UNE {dest}: {qtd}" for dest, qtd in distribuicao.items() if qtd > 0])

                        produtos_sol.append({
                            'Código': produto.get('codigo'),
                            'Produto': produto.get('nome_produto', 'N/A')[:40],
                            'Origem': f"UNE {une_origem_item}",
                            'Distribuição': dist_str,
                            'Total': item.get('total', item.get('quantidade', 0))
                        })
                    st.dataframe(pd.DataFrame(produtos_sol), hide_index=True, use_container_width=True)
    else:
        st.info("📭 Nenhuma solicitação encontrada")
else:
    st.info("📭 Nenhuma solicitação encontrada")

# Footer
st.markdown("---")
st.caption(f"Agent_BI - Sistema de Transferências | Usuário: {st.session_state.get('username', 'N/A')} | Fonte: {adapter.get_status()['current_source'].upper()}")
