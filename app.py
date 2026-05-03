import streamlit as st
import pandas as pd

# 1. Configuração de Layout e Estilo (Padrão Aprovado)
st.set_page_config(page_title="Análise SDR", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F0F8FF; }
    span[data-baseweb="tag"] { background-color: #1565C0 !important; color: white !important; }
    div[data-testid="stMetricValue"] {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #90CAF9;
        color: #0D47A1;
    }
    [data-testid="stMetricDelta"] > div {
        background-color: #1565C0 !important;
        color: white !important;
        border-radius: 5px;
        padding: 2px 8px;
        font-weight: bold;
    }
    [data-testid="stMetricDelta"] svg { display: none; }
    h1, h2, h3 { color: #0D47A1 !important; }
    </style>
    """, unsafe_allow_html=True)

try:
    df = pd.read_csv('bd-teste-sistema.csv')
    df.columns = df.columns.str.strip()
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

    # Cálculos Principais
    L = len(df_f)
    R = df_f['[IS/Closer] Reunião Ocorrida '].notna().sum() if '[IS/Closer] Reunião Ocorrida ' in df_f.columns else df_f['[IS/Closer] Reunião Ocorrida'].notna().sum()
    F = df_f[df_f['Etapa do negócio'].isin(['Fechado', 'Pago'])].shape[0]

    st.title("📊 Dashboard de Conversão Comercial")

    # Métricas Superiores
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Leads", L)
    col2.metric("Conversão Reunião", f"{(R/L*100):.1f}%" if L>0 else "0%", "Lead x Reunião")
    col3.metric("Conversão Fechado", f"{(F/L*100):.1f}%" if L>0 else "0%", "Lead x Fechado")

    st.divider()

    # FUNÇÃO PARA CRIAR AS TABELAS DE SEGMENTAÇÃO
    def criar_tabela_segmentada(coluna_nome):
        # Agrupamento
        tabela = df_f.groupby(coluna_nome).agg(
            Leads=('ID do registro.', 'count'),
            Reunioes=('[IS/Closer] Reunião Ocorrida ', 'count') if '[IS/Closer] Reunião Ocorrida ' in df_f.columns else ('[IS/Closer] Reunião Ocorrida', 'count'),
        ).reset_index()
        
        # Cálculo de Fechados por categoria
        fechados_cat = df_f[df_f['Etapa do negócio'].isin(['Fechado', 'Pago'])].groupby(coluna_nome)['ID do registro.'].count().reset_index()
        fechados_cat.columns = [coluna_nome, 'Fechados']
        
        # Merge das tabelas
        tabela = tabela.merge(fechados_cat, on=coluna_nome, how='left').fillna(0)
        
        # Cálculos de % solicitados
        tabela['Lead x Reunião (%)'] = (tabela['Reunioes'] / tabela['Leads'] * 100).round(1)
        tabela['Lead x Fechado (%)'] = (tabela['Fechados'] / tabela['Leads'] * 100).round(1)
        
        return tabela[[coluna_nome, 'Leads', 'Lead x Reunião (%)', 'Lead x Fechado (%)']].sort_values(by='Leads', ascending=False)

    # Exibição lado a lado
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📍 Por Origem do Lead")
        st.dataframe(criar_tabela_segmentada("[IS] Origem do lead"), use_container_width=True, hide_index=True)

    with col_b:
        st.subheader("🏷️ Por Tipo de Lead")
        st.dataframe(criar_tabela_segmentada("[IS] Tipo de lead"), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Erro no processamento: {e}")
