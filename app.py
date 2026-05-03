import streamlit as st
import pandas as pd

# 1. Configuração de Layout e Estilo (Mantendo o padrão aprovado)
st.set_page_config(page_title="Análise SDR", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F0F8FF; }
    span[data-baseweb="tag"] { background-color: #1565C0 !important; color: white !important; }
    div[data-testid="stMetricValue"] {
        background-color: #FFFFFF; border-radius: 10px; padding: 10px; border: 1px solid #90CAF9; color: #0D47A1;
    }
    [data-testid="stMetricDelta"] > div {
        background-color: #1565C0 !important; color: white !important; border-radius: 5px; padding: 2px 8px; font-weight: bold;
    }
    [data-testid="stMetricDelta"] svg { display: none; }
    h1, h2, h3 { color: #0D47A1 !important; }
    </style>
    """, unsafe_allow_html=True)

try:
    # Carregando os dados
    df = pd.read_csv('bd-teste-sistema.csv')
    df.columns = df.columns.str.strip()

    # TRATAMENTO DE DATA CRÍTICO: Convertendo a coluna para garantir que o filtro funcione
    df['Data de criação'] = pd.to_datetime(df['Data de criação'], errors='coerce')
    # Remove linhas onde a data é inválida para não quebrar o filtro
    df = df.dropna(subset=['Data de criação'])

    # Barra Lateral
    st.sidebar.header("Filtros")
    data_min = df['Data de criação'].min().date()
    data_max = df['Data de criação'].max().date()
    periodo = st.sidebar.date_input("Data de criação", [data_min, data_max])

    tipos = sorted(df["[IS] Tipo de lead"].dropna().unique().tolist())
    filtro_tipo = st.sidebar.multiselect("Tipo de Lead", tipos, default=tipos)

    origens = sorted(df["[IS] Origem do lead"].dropna().unique().tolist())
    filtro_origem = st.sidebar.multiselect("Origem do Lead", origens, default=origens)

    # APLICANDO O FILTRO REAL (df_f será usado em TUDO a partir daqui)
    if isinstance(periodo, list) or isinstance(periodo, tuple):
        if len(periodo) == 2:
            mask = (df['Data de criação'].dt.date >= periodo[0]) & \
                   (df['Data de criação'].dt.date <= periodo[1]) & \
                   (df["[IS] Tipo de lead"].isin(filtro_tipo)) & \
                   (df["[IS] Origem do lead"].isin(filtro_origem))
            df_f = df[mask].copy()
        else:
            df_f = df[df["[IS] Tipo de lead"].isin(filtro_tipo) & df["[IS] Origem do lead"].isin(filtro_origem)].copy()
    else:
        df_f = df.copy()

    # Cálculos Principais baseados no Filtro
    L = len(df_f)
    # Buscando colunas com ou sem espaço no final (flexibilidade)
    col_reuniao = '[IS/Closer] Reunião Ocorrida ' if '[IS/Closer] Reunião Ocorrida ' in df_f.columns else '[IS/Closer] Reunião Ocorrida'
    
    R = df_f[col_reuniao].notna().sum()
    F = df_f[df_f['Etapa do negócio'].isin(['Fechado', 'Pago'])].shape[0]

    st.title("📊 Dashboard de Conversão Comercial")

    # Métricas Superiores
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Leads", L)
    col2.metric("Conv. Reunião", f"{(R/L*100):.1f}%" if L>0 else "0%", "Lead x Reunião")
    col3.metric("Conv. Fechado", f"{(F/L*100):.1f}%" if L>0 else "0%", "Lead x Fechado")

    st.divider()

    # FUNÇÃO CORRIGIDA: Agora ela usa explicitamente o df_f (filtrado)
    def criar_tabela_segmentada(df_filtrado, coluna_nome):
        # Agrupamento sobre os dados já filtrados
        tabela = df_filtrado.groupby(coluna_nome).agg(
            Leads=('ID do registro.', 'count'),
        ).reset_index()
        
        # Reuniões por categoria
        reunioes_cat = df_filtrado[df_filtrado[col_reuniao].notna()].groupby(coluna_nome)['ID do registro.'].count().reset_index()
        reunioes_cat.columns = [coluna_nome, 'Reunioes']
        
        # Fechados por categoria
        fechados_cat = df_filtrado[df_filtrado['Etapa do negócio'].isin(['Fechado', 'Pago'])].groupby(coluna_nome)['ID do registro.'].count().reset_index()
        fechados_cat.columns = [coluna_nome, 'Fechados']
        
        # Merge
        tabela = tabela.merge(reunioes_cat, on=coluna_nome, how='left')
        tabela = tabela.merge(fechados_cat, on=coluna_nome, how='left').fillna(0)
        
        # % sobre os leads daquela categoria
        tabela['Lead x Reunião (%)'] = (tabela['Reunioes'] / tabela['Leads'] * 100).round(1).astype(str) + '%'
        tabela['Lead x Fechado (%)'] = (tabela['Fechados'] / tabela['Leads'] * 100).round(1).astype(str) + '%'
        
        return tabela[[coluna_nome, 'Leads', 'Lead x Reunião (%)', 'Lead x Fechado (%)']].sort_values(by='Leads', ascending=False)

    # Exibição
    c_a, c_b = st.columns(2)
    with c_a:
        st.subheader("📍 Por Origem")
        st.dataframe(criar_tabela_segmentada(df_f, "[IS] Origem do lead"), use_container_width=True, hide_index=True)
    with c_b:
        st.subheader("🏷️ Por Tipo")
        st.dataframe(criar_tabela_segmentada(df_f, "[IS] Tipo de lead"), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Ocorreu um erro: {e}")
