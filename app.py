import streamlit as st
import pandas as pd

# 1. Configuração visual Azul Claro
st.set_page_config(page_title="Análise SDR", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #E3F2FD; } /* Fundo Azul Claro */
    .stMetric { 
        border: 1px solid #90CAF9; 
        padding: 15px; 
        border-radius: 10px; 
        background-color: #FFFFFF;
    }
    h1, h2, h3 { color: #1565C0; }
    </style>
    """, unsafe_allow_html=True)

try:
    # Carregando o arquivo que você subiu
    df = pd.read_csv('bd-teste-sistema.csv')
    df.columns = df.columns.str.strip()

    # Filtros na Lateral
    st.sidebar.header("Filtros")
    
    # Filtro de Data
    df['Data de criação'] = pd.to_datetime(df['Data de criação'], errors='coerce')
    data_min = df['Data de criação'].min().date()
    data_max = df['Data de criação'].max().date()
    periodo = st.sidebar.date_input("Data de criação", [data_min, data_max])

    # Filtros de Lead e Origem
    tipos = df["[IS] Tipo de lead"].dropna().unique().tolist()
    filtro_tipo = st.sidebar.multiselect("Tipo de Lead", tipos, default=tipos)

    origens = df["[IS] Origem do lead"].dropna().unique().tolist()
    filtro_origem = st.sidebar.multiselect("Origem do Lead", origens, default=origens)

    # Lógica de Filtro
    mask = (df['Data de criação'].dt.date >= periodo[0]) & (df['Data de criação'].dt.date <= periodo[1]) & \
           (df["[IS] Tipo de lead"].isin(filtro_tipo)) & (df["[IS] Origem do lead"].isin(filtro_origem))
    df_f = df[mask]

    # Cálculos de Métricas
    L = len(df_f)
    C = df_f['Contato Realizado'].notna().sum()
    A = df_f['[IS/SDR] Data do Agendamento'].notna().sum()
    R = df_f['[IS/Closer] Reunião Ocorrida'].notna().sum()
    F = df_f[df_f['Etapa do negócio'].isin(['Fechado', 'Pago'])].shape[0]

    # Exibição do Título
    st.title("📊 Dashboard de Conversão Comercial")

    # Primeira Linha: Números e Conversões (%)
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Leads", L)
    col2.metric("Contatos", C, f"{(C/L*100):.1f}%" if L>0 else "0%")
    col3.metric("Agendados", A, f"{(A/C*100):.1f}%" if C>0 else "0%")
    col4.metric("Reuniões", R, f"{(R/L*100):.1f}% do Total" if L>0 else "0%")
    col5.metric("Fechados", F, f"{(F/L*100):.1f}% do Total" if L>0 else "0%")

    st.divider()

    # Gráficos de Conversão solicitados
    st.subheader("📈 Taxas de Conversão Críticas")
    c_graf1, c_graf2 = st.columns(2)
    
    with c_graf1:
        st.write("**Lead x Reunião Ocorrida**")
        conv_r = (R/L*100) if L>0 else 0
        st.progress(conv_r / 100)
        st.write(f"{conv_r:.1f}%")

    with c_graf2:
        st.write("**Lead x Fechado / Pago**")
        conv_f = (F/L*100) if L>0 else 0
        st.progress(conv_f / 100)
        st.write(f"{conv_f:.1f}%")

except Exception as e:
    st.error(f"Erro: {e}")
