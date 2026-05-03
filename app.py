import streamlit as st
import pandas as pd

# 1. Configuração visual "Clean"
st.set_page_config(page_title="Análise SDR", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F8F9FA; }
    .stMetric { border: 1px solid #E0E0E0; padding: 15px; border-radius: 8px; background-color: #FFFFFF; }
    </style>
    """, unsafe_allow_html=True)

# 2. Carregando os dados do arquivo que você subiu
try:
    df = pd.read_csv('bd-teste-sistema.csv')
    
    # Tratamento de datas (garantindo que o sistema entenda o que é data)
    colunas_data = ['Data de criação', 'Contato Realizado ', '[IS/SDR] Data do Agendamento', '[IS/Closer] Reunião Ocorrida ', 'Data de fechamento']
    for col in colunas_data:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # 3. Barra Lateral (Filtros dinâmicos)
    st.sidebar.header("Filtros de Análise")
    
    tipos = df["[IS] Tipo de lead"].dropna().unique().tolist()
    filtro_tipo = st.sidebar.multiselect("Tipo de Lead", tipos, default=tipos)

    origens = df["[IS] Origem do lead"].dropna().unique().tolist()
    filtro_origem = st.sidebar.multiselect("Origem do Lead", origens, default=origens)

    # Aplicando os filtros nos dados
    df_filtrado = df[df["[IS] Tipo de lead"].isin(filtro_tipo) & df["[IS] Origem do lead"].isin(filtro_origem)]

    # 4. Lógica do Funil (Assertividade)
    total_leads = len(df_filtrado)
    contatos = df_filtrado['Contato Realizado '].notna().sum()
    agendados = df_filtrado['[IS/SDR] Data do Agendamento'].notna().sum()
    reunioes = df_filtrado['[IS/Closer] Reunião Ocorrida '].notna().sum()
    
    # Regra de Fechamento: Etapa é Fechado/Pago E tem Data de Fechamento
    fechados = df_filtrado[
        (df_filtrado['Etapa do negócio'].isin(['Fechado', 'Pago'])) & 
        (df_filtrado['Data de fechamento'].notna())
    ].shape[0]

    # 5. Exibição dos Resultados
    st.title("📊 Painel de Conversão Comercial")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Leads", total_leads)
    col2.metric("Contatos", contatos)
    col3.metric("Agendados", agendados)
    col4.metric("Reuniões", reunioes)
    col5.metric("Fechados", fechados)

    st.divider()
    st.subheader("Base de Dados (Filtro Atual)")
    st.dataframe(df_filtrado[['ID do registro.', 'Nome do negócio', 'Etapa do negócio', 'Data de fechamento']].head(10))

except Exception as e:
    st.error(f"Erro ao carregar o arquivo: {e}")
