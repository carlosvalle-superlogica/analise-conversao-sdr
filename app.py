import streamlit as st
import pandas as pd

# 1. Configuração de Layout e Estilo
st.set_page_config(page_title="Análise Comercial", layout="wide")

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
    # Carregando dados
    df = pd.read_csv('bd-teste-sistema.csv')
    df.columns = df.columns.str.strip()
    
    # -------------------------------------------------------------
    # CORREÇÃO CRÍTICA: LENDO A DATA EXATA DE CADA EVENTO
    # -------------------------------------------------------------
    df['Data de criação'] = pd.to_datetime(df['Data de criação'], errors='coerce')
    
    col_contato = 'Contato Realizado' if 'Contato Realizado' in df.columns else df.columns[df.columns.str.contains('Contato Realizado')].tolist()[0]
    df['Data Contato'] = pd.to_datetime(df[col_contato], errors='coerce')
    
    df['Data Agendamento'] = pd.to_datetime(df['[IS/SDR] Data do Agendamento'], errors='coerce')
    
    col_reuniao = '[IS/Closer] Reunião Ocorrida' if '[IS/Closer] Reunião Ocorrida' in df.columns else df.columns[df.columns.str.contains('Reunião Ocorrida')].tolist()[0]
    df['Data Reuniao'] = pd.to_datetime(df[col_reuniao], errors='coerce')
    
    df['Data Fechamento'] = pd.to_datetime(df['Data de fechamento'], errors='coerce')
    # -------------------------------------------------------------

    # Barra Lateral
    st.sidebar.header("Filtros")
    data_min, data_max = df['Data de criação'].dropna().min().date(), df['Data de criação'].dropna().max().date()
    periodo = st.sidebar.date_input("Período do Evento", [data_min, data_max])
    
    tipos = sorted(df["[IS] Tipo de lead"].dropna().unique().tolist())
    filtro_tipo = st.sidebar.multiselect("Tipo de Lead", tipos, default=tipos)
    
    origens = sorted(df["[IS] Origem do lead"].dropna().unique().tolist())
    filtro_origem = st.sidebar.multiselect("Origem do Lead", origens, default=origens)

    # Aplicação do Filtro de Atributos (Origem e Tipo)
    mask_atributos = (df["[IS] Tipo de lead"].isin(filtro_tipo)) & (df["[IS] Origem do lead"].isin(filtro_origem))
    df_base = df[mask_atributos].copy()

    # Aplicação do Filtro TEMPORAL (Igual ao HubSpot: Conta o evento dentro do mês)
    if isinstance(periodo, (list, tuple)) and len(periodo) == 2:
        p_start, p_end = periodo[0], periodo[1]
        
        mask_L = (df_base['Data de criação'].dt.date >= p_start) & (df_base['Data de criação'].dt.date <= p_end)
        mask_C = (df_base['Data Contato'].dt.date >= p_start) & (df_base['Data Contato'].dt.date <= p_end)
        mask_A = (df_base['Data Agendamento'].dt.date >= p_start) & (df_base['Data Agendamento'].dt.date <= p_end)
        mask_R = (df_base['Data Reuniao'].dt.date >= p_start) & (df_base['Data Reuniao'].dt.date <= p_end)
        mask_F = (df_base['Data Fechamento'].dt.date >= p_start) & (df_base['Data Fechamento'].dt.date <= p_end) & (df_base['Etapa do negócio'].isin(['Fechado', 'Pago']))
    else:
        # Fallback de segurança se nenhuma data for selecionada
        mask_L = df_base['Data de criação'].notna()
        mask_C = df_base['Data Contato'].notna()
        mask_A = df_base['Data Agendamento'].notna()
        mask_R = df_base['Data Reuniao'].notna()
        mask_F = df_base['Etapa do negócio'].isin(['Fechado', 'Pago'])

    # CÁLCULOS DO TOPO (Resultados cruzados com o seu CRM)
    L = mask_L.sum()
    C = mask_C.sum()
    A = mask_A.sum()
    R = mask_R.sum()
    F = mask_F.sum()

    st.title("📊 Dashboard de Conversão Comercial")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Leads", L)
    m2.metric("Contato", C, f"{(C/L*100):.1f}% s/ Lead" if L>0 else "0%")
    m3.metric("Agendado", A, f"{(A/C*100):.1f}% s/ Contato" if C>0 else "0%")
    m4.metric("Ocorrido", R, f"{(R/A*100):.1f}% s/ Agend." if A>0 else "0%")
    m5.metric("Fechado", F, f"{(F/R*100):.1f}% s/ Ocorr." if R>0 else "0%")

    st.divider()

    # TABELAS ABAIXO (Ajustadas para respeitar a mesma matemática de Evento)
    def criar_tabela_evento(coluna_nome):
        leads_cat = df_base[mask_L].groupby(coluna_nome).size().reset_index(name='Leads')
        reunioes_cat = df_base[mask_R].groupby(coluna_nome).size().reset_index(name='Reunioes')
        fechados_cat = df_base[mask_F].groupby(coluna_nome).size().reset_index(name='Fechados')
        
        # Junta tudo, inclusive leads antigos que geraram reunião no mês atual
        tabela = leads_cat.merge(reunioes_cat, on=coluna_nome, how='outer').merge(fechados_cat, on=coluna_nome, how='outer').fillna(0)
        
        # Proteção matemática caso a categoria tenha 0 leads novos mas gerou reunião
        tabela['Lead x Reunião (%)'] = tabela.apply(lambda row: f"{(row['Reunioes']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
        tabela['Lead x Fechado (%)'] = tabela.apply(lambda row: f"{(row['Fechados']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
        
        return tabela[[coluna_nome, 'Leads', 'Lead x Reunião (%)', 'Lead x Fechado (%)']].sort_values(by='Leads', ascending=False)

    c_a, c_b = st.columns(2)
    with c_a:
        st.subheader("📍 Por Origem")
        st.dataframe(criar_tabela_evento("[IS] Origem do lead"), use_container_width=True, hide_index=True)
    with c_b:
        st.subheader("🏷️ Por Tipo")
        st.dataframe(criar_tabela_evento("[IS] Tipo de lead"), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Erro no processamento de dados: {e}")
