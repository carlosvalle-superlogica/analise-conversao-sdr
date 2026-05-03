import streamlit as st
import pandas as pd

# 1. Configuração de Layout e Estilo
st.set_page_config(page_title="Análise SDR", layout="wide")

st.markdown("""
    <style>
    /* Fundo da página */
    .stApp { background-color: #F0F8FF; }
    
    /* Estilo dos Cards Principais */
    div[data-testid="stMetricValue"] {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #90CAF9;
        color: #0D47A1;
    }
    
    /* Indicadores em Azul (substituindo o vermelho) */
    [data-testid="stMetricDelta"] > div {
        background-color: #1565C0 !important;
        color: white !important;
        border-radius: 5px;
        padding: 2px 8px;
        font-weight: bold;
    }
    
    /* Ocultar setas de variação */
    [data-testid="stMetricDelta"] svg { display: none; }
    
    h1, h2, h3 { color: #0D47A1 !important; }
    </style>
    """, unsafe_allow_html=True)

try:
    # Carregando os dados
    df = pd.read_csv('bd-teste-sistema.csv')
    df.columns = df.columns.str.strip()

    # 2. Tratamento de Datas para o Formato Brasil
    df['Data de criação'] = pd.to_datetime(df['Data de criação'], errors='coerce')
    
    # Barra Lateral
    st.sidebar.header("Filtros")
    
    data_min = df['Data de criação'].min().date()
    data_max = df['Data de criação'].max().date()
    
    # Filtro de Data com formato de exibição BR
    periodo = st.sidebar.date_input(
        "Data de criação", 
        [data_min, data_max],
        format="DD/MM/YYYY"  # Define o formato visual no seletor
    )

    # Filtros de Seleção
    tipos = df["[IS] Tipo de lead"].dropna().unique().tolist()
    filtro_tipo = st.sidebar.multiselect("Tipo de Lead", tipos, default=tipos)

    origens = df["[IS] Origem do lead"].dropna().unique().tolist()
    filtro_origem = st.sidebar.multiselect("Origem do Lead", origens, default=origens)

    # Lógica de Filtro
    mask = (df['Data de criação'].dt.date >= periodo[0]) & (df['Data de criação'].dt.date <= periodo[1]) & \
           (df["[IS] Tipo de lead"].isin(filtro_tipo)) & (df["[IS] Origem do lead"].isin(filtro_origem))
    df_f = df[mask].copy()

    # 3. Cálculos
    L = len(df_f)
    C = df_f['Contato Realizado '].notna().sum()
    A = df_f['[IS/SDR] Data do Agendamento'].notna().sum()
    R = df_f['[IS/Closer] Reunião Ocorrida '].notna().sum()
    F = df_f[df_f['Etapa do negócio'].isin(['Fechado', 'Pago'])].shape[0]

    st.title("📊 Dashboard de Conversão Comercial")

    # Exibição das Métricas
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Leads", L)
    col2.metric("Contatos", C, f"{(C/L*100):.1f}%")
    col3.metric("Agendados", A, f"{(A/C*100):.1f}%")
    col4.metric("Reuniões", R, f"{(R/L*100):.1f}%")
    col5.metric("Fechados", F, f"{(F/L*100):.1f}%")

    st.divider()

    # Tabela com datas formatadas para PT-BR
    st.subheader("Visualização dos Dados")
    
    # Criando uma cópia para exibição com datas formatadas
    df_display = df_f[['Data de criação', '[IS] Tipo de lead', '[IS] Origem do lead', 'Etapa do negócio']].head(10).copy()
    df_display['Data de criação'] = df_display['Data de criação'].dt.strftime('%d/%m/%Y')
    
    st.dataframe(df_display, use_container_width=True)

except Exception as e:
    st.error(f"Erro: {e}")
