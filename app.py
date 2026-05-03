import streamlit as st
import pandas as pd

# 1. Configuração de Layout
st.set_page_config(page_title="Análise SDR", layout="wide")

st.markdown("""
    <style>
    /* Fundo da página */
    .stApp { background-color: #F0F8FF; }
    
    /* Estilo dos Cards */
    div[data-testid="stMetricValue"] {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #90CAF9;
        color: #0D47A1;
    }
    
    /* REMOVENDO O VERMELHO: Forçando os indicadores (deltas) a serem azuis ou cinzas */
    [data-testid="stMetricDelta"] svg {
        display: none; /* Remove a setinha de subida/descida se quiser */
    }
    div[data-testid="stMetricDelta"] > div {
        color: #4682B4 !important; /* Transforma o texto de baixo em Azul Marinho */
    }
    
    h1, h2, h3 { color: #0D47A1 !important; }
    </style>
    """, unsafe_allow_html=True)

try:
    df = pd.read_csv('bd-teste-sistema.csv')
    df.columns = df.columns.str.strip()

    # Filtros Laterais
    st.sidebar.header("Filtros")
    df['Data de criação'] = pd.to_datetime(df['Data de criação'], errors='coerce')
    data_min = df['Data de criação'].min().date()
    data_max = df['Data de criação'].max().date()
    periodo = st.sidebar.date_input("Data de criação", [data_min, data_max])

    tipos = df["[IS] Tipo de lead"].dropna().unique().tolist()
    filtro_tipo = st.sidebar.multiselect("Tipo de Lead", tipos, default=tipos)

    origens = df["[IS] Origem do lead"].dropna().unique().tolist()
    filtro_origem = st.sidebar.multiselect("Origem do Lead", origens, default=origens)

    # Lógica de Filtro
    mask = (df['Data de criação'].dt.date >= periodo[0]) & (df['Data de criação'].dt.date <= periodo[1]) & \
           (df["[IS] Tipo de lead"].isin(filtro_tipo)) & (df["[IS] Origem do lead"].isin(filtro_origem))
    df_f = df[mask]

    # Cálculos
    L = len(df_f)
    C = df_f['Contato Realizado'].notna().sum()
    A = df_f['[IS/SDR] Data do Agendamento'].notna().sum()
    R = df_f['[IS/Closer] Reunião Ocorrida'].notna().sum()
    F = df_f[df_f['Etapa do negócio'].isin(['Fechado', 'Pago'])].shape[0]

    st.title("📊 Dashboard de Conversão Comercial")

    # Exibição das Métricas - Usando delta_color="off" para não ficar vermelho/verde
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric("Leads", L)
    
    # delta_color="off" deixa o texto cinza/azul padrão, sem o alerta de perigo
    col2.metric("Contatos", C, f"{(C/L*100):.1f}% de conversão", delta_color="off")
    col3.metric("Agendados", A, f"{(A/C*100):.1f}% de conversão", delta_color="off")
    col4.metric("Reuniões", R, f"{(R/L*100):.1f}% sobre total", delta_color="off")
    col5.metric("Fechados", F, f"{(F/L*100):.1f}% sobre total", delta_color="off")

    st.divider()

    # Gráficos
    st.subheader("📈 Taxas de Conversão")
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Lead x Reunião Ocorrida**")
        st.progress((R/L) if L>0 else 0)
        st.write(f"{(R/L*100):.1f}%")
    with c2:
        st.write("**Lead x Fechado / Pago**")
        st.progress((F/L) if L>0 else 0)
        st.write(f"{(F/L*100):.1f}%")

except Exception as e:
    st.error(f"Erro: {e}")
