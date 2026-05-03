import streamlit as st
import pandas as pd

# 1. Configuração visual "Clean"
st.set_page_config(page_title="Análise SDR", layout="wide")

# Estilização para cartões brancos e fundo cinza claro
st.markdown("""
    <style>
    .main { background-color: #F8F9FA; }
    .stMetric { border: 1px solid #E0E0E0; padding: 15px; border-radius: 8px; background-color: #FFFFFF; }
    </style>
    """, unsafe_allow_html=True)

# 2. Barra Lateral (Filtros)
st.sidebar.header("Filtros de Análise")

# Filtro de Data
filtro_data = st.sidebar.date_input("Filtrar por Período")

# Filtro de Tipo de Lead
filtro_tipo = st.sidebar.multiselect(
    "Tipo de Lead", 
    ["Inbound", "Outbound", "Indicação", "Base"]
)

# Filtro de Origem do Lead
filtro_origem = st.sidebar.multiselect(
    "Origem do Lead", 
    ["MKT", "Outbound", "Indicação", "Prospecção Ativa"]
)

# 3. Corpo Principal
st.title("📊 Painel de Conversão Comercial")

# Cards de métricas no topo (Agora com 5 colunas para seguir o seu funil)
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Leads", "0")
col2.metric("Contatos Realizados", "0")
col3.metric("Agendamentos", "0")
col4.metric("Reuniões Ocorridas", "0")
col5.metric("Fechados (Pagos)", "0")

st.divider()

# Mensagem de status
st.info("Layout atualizado com as 5 etapas do funil. Pronto para conectar os dados.")
