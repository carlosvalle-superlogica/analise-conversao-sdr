import streamlit as st
import pandas as pd

# Configuração visual "Clean"
st.set_page_config(page_title="Análise SDR", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F8F9FA; }
    .stMetric { border: 1px solid #E0E0E0; padding: 15px; border-radius: 8px; background-color: #FFFFFF; }
    </style>
    """, unsafe_allow_html=True)

# Título e Sidebar
st.title("📊 Painel de Conversão Comercial")
st.sidebar.header("Filtros de Análise")

# Filtros que combinamos
filtro_data = st.sidebar.date_input("Filtrar por Período")
filtro_tipo = st.sidebar.multiselect("Tipo de Lead", ["Inbound", "Outbound", "Indicação", "Base"])

# Layout de Cards (Resumo)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Leads", "0")
col2.metric("Contatos Realizados", "0")
col3.metric("Reuniões Ocorridas", "0")
col4.metric("Fechados (Pagos)", "0")

st.divider()
st.warning("Próximo passo: Conectar ao Google Sheets para visualizar os dados reais.")
