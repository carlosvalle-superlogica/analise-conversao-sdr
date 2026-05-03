import streamlit as st
import pandas as pd

# 1. Configuração de Layout e Cor Azul Clara (Reforçada)
st.set_page_config(page_title="Análise SDR", layout="wide")

st.markdown("""
    <style>
    /* Cor de fundo da página inteira */
    .stApp {
        background-color: #E3F2FD;
    }
    /* Estilo dos Cards de Métricas */
    div[data-testid="stMetricValue"] {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #90CAF9;
    }
    /* Títulos em azul escuro */
    h1, h2, h3 {
        color: #0D47A1 !important;
    }
    </style>
    """, unsafe_allow_html=True)

try:
    # Carregando o arquivo
    df = pd.read_csv('bd-teste-sistema.csv')
    df.columns = df.columns.str.strip()

    # Barra Lateral
    st.sidebar.header("Filtros")
    
    df['Data de criação'] = pd.to_datetime(df['Data de criação'], errors='coerce')
    data_min = df['Data de criação'].min().date()
    data_max = df['Data de criação'].max().date()
    
    # Filtro de Data
    periodo = st.sidebar.date_input("Data de criação", [data_min, data_max])

    # Filtro de Tipo de Lead
    tipos = df["[IS] Tipo de lead"].dropna().unique().tolist()
    filtro_tipo = st.sidebar.multiselect("Tipo de Lead", tipos, default=tipos)

    # Filtro de Origem do Lead
    origens = df["[IS] Origem do lead"].dropna().unique().tolist()
    filtro_origem = st.sidebar.multiselect("Origem do Lead", origens, default=origens)

    # Lógica do Filtro
    mask = (df['Data de criação'].dt.date >= periodo[0]) & (df['Data de criação'].dt.date <= periodo[1]) & \
           (df["[IS] Tipo de lead"].isin(filtro_tipo)) & (df["[IS] Origem do lead"].isin(filtro_origem))
    df_f = df[mask]

    # Cálculos
    L = len(df_f)
    C = df_f['Contato Realizado'].notna().sum()
    A = df_f['[IS/SDR] Data do Agendamento'].notna().sum()
    R = df_f['[IS/Closer] Reunião Ocorrida'].notna().sum()
    F = df_f[df_f['Etapa do negócio'].isin(['Fechado', 'Pago'])].shape[0]

    # Dashboard
    st.title("📊 Dashboard de Conversão Comercial")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Leads", L)
    col2.metric("Contatos", C, f"{(C/L*100):.1f}%" if L>0 else "0%")
    col3.metric("Agendados", A, f"{(A/C*100):.1f}%" if C>0 else "0%")
    col4.metric("Reuniões", R, f"{(R/L*100):.1f}% Total" if L>0 else "0%")
    col5.metric("Fechados", F, f"{(F/L*100):.1f}% Total" if L>0 else "0%")

    st.divider()

    # Gráficos de Conversão (Estilo Barra de Progresso do Sheets)
    st.subheader("📈 Taxas de Conversão")
    c1, c2 = st.columns(2)
    
    with c1:
        st.write("**Lead x Reunião Ocorrida**")
        taxa_r = (R/L) if L>0 else 0
        st.progress(taxa_r)
        st.write(f"{taxa_r*100:.1f}%")

    with c2:
        st.write("**Lead x Fechado / Pago**")
        taxa_f = (F/L) if L>0 else 0
        st.progress(taxa_f)
        st.write(f"{taxa_f*100:.1f}%")

except Exception as e:
    st.error(f"Aguardando dados ou erro no arquivo: {e}")
