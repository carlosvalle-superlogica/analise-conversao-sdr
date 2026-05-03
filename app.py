import streamlit as st
import pandas as pd

# 1. Configuração de Layout e Estilo Refinado
st.set_page_config(page_title="Análise SDR", layout="wide")

st.markdown("""
    <style>
    /* fundo da página */
    .stApp { background-color: #F0F8FF; }
    
    /* CORRIGINDO A LATERAL: Troca o vermelho de seleção por Azul */
    span[data-baseweb="tag"] {
        background-color: #1565C0 !important;
        color: white !important;
    }
    div[role="listbox"] ul li[aria-selected="true"] {
        background-color: #E3F2FD !important;
    }
    
    /* Estilo dos Cards Superiores */
    div[data-testid="stMetricValue"] {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #90CAF9;
        color: #0D47A1;
    }
    
    /* Indicadores das métricas em Azul */
    [data-testid="stMetricDelta"] > div {
        background-color: #1565C0 !important;
        color: white !important;
        border-radius: 5px;
        padding: 2px 8px;
        font-weight: bold;
    }
    
    /* Remove setas e ajusta títulos */
    [data-testid="stMetricDelta"] svg { display: none; }
    h1, h2, h3 { color: #0D47A1 !important; }
    </style>
    """, unsafe_allow_html=True)

try:
    # Carregando os dados
    df = pd.read_csv('bd-teste-sistema.csv')
    df.columns = df.columns.str.strip()

    # Tratamento de Datas
    df['Data de criação'] = pd.to_datetime(df['Data de criação'], errors='coerce')
    
    # Barra Lateral
    st.sidebar.header("Filtros")
    data_min = df['Data de criação'].min().date()
    data_max = df['Data de criação'].max().date()
    periodo = st.sidebar.date_input("Data de criação", [data_min, data_max])

    tipos = df["[IS] Tipo de lead"].dropna().unique().tolist()
    filtro_tipo = st.sidebar.multiselect("Tipo de Lead", tipos, default=tipos)

    origens = df["[IS] Origem do lead"].dropna().unique().tolist()
    filtro_origem = st.sidebar.multiselect("Origem do Lead", origens, default=origens)

    # Lógica de Filtro
    if isinstance(periodo, list) and len(periodo) == 2:
        mask = (df['Data de criação'].dt.date >= periodo[0]) & (df['Data de criação'].dt.date <= periodo[1]) & \
               (df["[IS] Tipo de lead"].isin(filtro_tipo)) & (df["[IS] Origem do lead"].isin(filtro_origem))
        df_f = df[mask].copy()
    else:
        df_f = df.copy()

    # Cálculos
    L = len(df_f)
    C = df_f['Contato Realizado '].notna().sum() if 'Contato Realizado ' in df_f.columns else df_f['Contato Realizado'].notna().sum()
    A = df_f['[IS/SDR] Data do Agendamento'].notna().sum()
    R = df_f['[IS/Closer] Reunião Ocorrida '].notna().sum() if '[IS/Closer] Reunião Ocorrida ' in df_f.columns else df_f['[IS/Closer] Reunião Ocorrida'].notna().sum()
    F = df_f[df_f['Etapa do negócio'].isin(['Fechado', 'Pago'])].shape[0]

    st.title("📊 Dashboard de Conversão Comercial")

    # Métricas Superiores
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Leads", L)
    col2.metric("Contatos", C, f"{(C/L*100):.1f}%" if L>0 else "0%")
    col3.metric("Agendados", A, f"{(A/C*100):.1f}%" if C>0 else "0%")
    col4.metric("Reuniões", R, f"{(R/L*100):.1f}%" if L>0 else "0%")
    col5.metric("Fechados", F, f"{(F/L*100):.1f}%" if L>0 else "0%")

    st.divider()

    # 2. SEÇÃO DE CONVERSÃO COM PORCENTAGEM VISÍVEL
    st.subheader("📈 Taxas de Conversão do Funil")
    c_graf1, c_graf2 = st.columns(2)
    
    with c_graf1:
        perc_r = (R/L*100) if L>0 else 0
        st.write(f"**Lead x Reunião Ocorrida: {perc_r:.1f}%**")
        st.progress(perc_r / 100)

    with c_graf2:
        perc_f = (F/L*100) if L>0 else 0
        st.write(f"**Lead x Fechado / Pago: {perc_f:.1f}%**")
        st.progress(perc_f / 100)

except Exception as e:
    st.error(f"Erro no processamento: {e}")
