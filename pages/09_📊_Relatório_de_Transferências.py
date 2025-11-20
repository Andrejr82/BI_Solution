"""
Módulo para pages/8_📊_Relatório_de_Transferências.py. Fornece as funções: load_transfer_data, convert_df_to_csv. Define componentes da interface de utilizador (UI).
"""


import streamlit as st
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

st.set_page_config(
    page_title="Relatório de Transferências",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Relatório de Transferências")

@st.cache_data(ttl=60)
def load_transfer_data():
    transferencias = []
    solicitacoes_path = Path(__file__).parent.parent / 'data' / 'transferencias'
    if solicitacoes_path.exists():
        for file in solicitacoes_path.glob("transferencia_*.json"):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                transferencias.append(data)
    return transferencias

transferencias = load_transfer_data()

if not transferencias:
    st.warning("Nenhuma transferência encontrada.")
    st.stop()

df = pd.DataFrame(transferencias)

if 'total_valor' not in df.columns:
    df['total_valor'] = 0

df['timestamp'] = pd.to_datetime(df['timestamp'])
df['week'] = df['timestamp'].dt.isocalendar().week

report_type = st.radio("Tipo de Relatório", ('Semanal', 'Manual'))

if report_type == 'Semanal':
    weeks = sorted(df['week'].unique(), reverse=True)
    selected_week = st.selectbox("Selecione a semana:", weeks)
    df_report = df[df['week'] == selected_week]
    report_name = f"semana_{selected_week}"
else:
    today = datetime.today()
    one_week_ago = today - pd.Timedelta(weeks=1)
    start_date = st.date_input('Data de início', one_week_ago)
    end_date = st.date_input('Data de fim', today)
    df_report = df[(df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)]
    report_name = f"{start_date.strftime('%Y%m%d')}_a_{end_date.strftime('%Y%m%d')}"

if df_report.empty:
    st.warning("Nenhuma transferência encontrada para o período selecionado.")
    st.stop()

df_report['total_valor'] = df_report['total_valor'].fillna(0)

st.header(f"Resumo do Relatório")

total_transferencias = len(df_report)
total_produtos = df_report['total_produtos'].sum()
total_itens = df_report['total_itens'].sum()
total_valor = df_report['total_valor'].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Transferências", total_transferencias)
col2.metric("Total de Produtos", total_produtos)
col3.metric("Total de Itens", total_itens)
col4.metric("Valor Total", f"R$ {total_valor:,.2f}")

st.header("Detalhes das Transferências")

for index, row in df_report.iterrows():
    with st.expander(f"Transferência {row['timestamp'].strftime('%Y-%m-%d %H:%M')} - Status: {row['status']}"):
        st.write(f"**Origem:** {row['unes_origem']}")
        st.write(f"**Destino:** {row['unes_destino']}")
        st.write(f"**Total de Produtos:** {row['total_produtos']}")
        st.write(f"**Total de Itens:** {row['total_itens']}")
        st.write(f"**Valor Total:** R$ {row.get('total_valor', 0):,.2f}")

        produtos = []
        for chave, item in row['produtos'].items():
            produto = item['produto']
            produtos.append({
                'Código': produto.get('codigo'),
                'Produto': produto.get('nome_produto'),
                'Quantidade': item.get('total'),
                'Preço': f"R$ {pd.to_numeric(item.get('preco', 0), errors='coerce'):.2f}",
                'Valor Total': f"R$ {item.get('valor_total_item', 0):.2f}"
            })
        
        st.dataframe(pd.DataFrame(produtos), use_container_width=True)


@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df_to_csv(df_report)

st.download_button(
   "Download do Relatório (CSV)",
   csv,
   f"relatorio_transferencias_{report_name}.csv",
   "text/csv",
   key='download-csv'
)
