import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuração visual "Clean"
st.set_page_config(page_title="Análise SDR", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F8F9FA; }
    .stMetric { border: 1px solid #E0E0E0; padding: 15px; border-radius: 8px; background-color: #FFFFFF; }
    </style>
    """, unsafe_allow_html=True)

# 2. Conexão com o Google Sheets
# Substituímos o link de edição pelo link de exportação de dados
url = "https://docs.google.com/spreadsheets/d/1EkLVZp29NiaMe7JZ3Fl8ODD_wjxbN32B-RHYF4KiCEA/export?format=csv"

try:
    # Lendo os dados como CSV diretamente do Google Sheets
    df = pd.read_csv(url)
    
    # 3. Barra Lateral (Filtros baseados nos dados reais)
    st.sidebar.header("Filtros de Análise")
    
    # Criando filtros dinâmicos baseados nas suas colunas
    tipos_disponiveis = df["[IS] Tipo de lead"].unique().tolist() if "[IS] Tipo de lead" in df.columns else []
    filtro_tipo = st.sidebar.multiselect("Tipo de Lead", tipos_disponiveis)

    origens_disponiveis = df["[IS] Origem do lead"].unique().tolist() if "[IS] Origem do lead" in df.columns else []
    filtro_origem = st.sidebar.multiselect("Origem do Lead", origens_disponiveis)

    # 4. Corpo Principal
    st.title("📊 Painel de Conversão Comercial")

    # Por enquanto, vamos apenas contar o total de linhas para testar a conexão
    total_leads = len(df)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Leads", total_leads)
    col2.metric("Contatos Realizados", "0")
    col3.metric("Agendamentos", "0")
    col4.metric("Reuniões Ocorridas", "0")
    col5.metric("Fechados (Pagos)", "0")

    st.divider()
    st.success("Conexão estabelecida com sucesso!")
    
    # Exibe as primeiras linhas para confirmarmos se as colunas estão certas
    st.write("Amostra dos dados lidos:")
    st.dataframe(df.head())

except Exception as e:
    st.error(f"Erro ao conectar com a planilha: {e}")
    st.info("Verifique se o compartilhamento na Superlógica permite acesso via link.")
