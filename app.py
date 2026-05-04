import streamlit as st
import pandas as pd

# 1. Configuração de Layout e Estilo (Fundo Azul e Cards Brancos)
st.set_page_config(page_title="Análise Comercial", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F0F8FF; }
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
    
    # Tratamento de Datas (Lógica de Evento/HubSpot)
    df['Data de criação'] = pd.to_datetime(df['Data de criação'], errors='coerce')
    
    col_contato = 'Contato Realizado' if 'Contato Realizado' in df.columns else df.columns[df.columns.str.contains('Contato Realizado')].tolist()[0]
    df['Data Contato'] = pd.to_datetime(df[col_contato], errors='coerce')
    
    df['Data Agendamento'] = pd.to_datetime(df['[IS/SDR] Data do Agendamento'], errors='coerce')
    
    col_reuniao = '[IS/Closer] Reunião Ocorrida' if '[IS/Closer] Reunião Ocorrida' in df.columns else df.columns[df.columns.str.contains('Reunião Ocorrida')].tolist()[0]
    df['Data Reuniao'] = pd.to_datetime(df[col_reuniao], errors='coerce')
    
    df['Data Fechamento'] = pd.to_datetime(df['Data de fechamento'], errors='coerce')

    # Colunas de Responsáveis
    col_sdr = '[IS/SDR] SDR Responsável'
    col_closer = '[IS/SDR] Closer Responsável'

    # --- BARRA LATERAL ---
    st.sidebar.header("Filtros")
    data_min, data_max = df['Data de criação'].dropna().min().date(), df['Data de criação'].dropna().max().date()
    periodo = st.sidebar.date_input("Período do Evento", [data_min, data_max])
    
    filtro_tipo = st.sidebar.multiselect("Tipo de Lead", sorted(df["[IS] Tipo de lead"].dropna().unique()), default=df["[IS] Tipo de lead"].dropna().unique())
    filtro_origem = st.sidebar.multiselect("Origem do Lead", sorted(df["[IS] Origin do lead"].dropna().unique()), default=df["[IS] Origin do lead"].dropna().unique())

    # Filtros de Pessoas (Com opção 'Todos' embutida)
    lista_sdr = sorted(df[col_sdr].dropna().unique().tolist())
    filtro_sdr = st.sidebar.multiselect("SDR Responsável", lista_sdr, default=lista_sdr)

    lista_closer = sorted(df[col_closer].dropna().unique().tolist())
    filtro_closer = st.sidebar.multiselect("Closer Responsável", lista_closer, default=lista_closer)

    # --- LÓGICA DE FILTRAGEM NÃO BLOQUEANTE ---
    # Primeiro filtramos por Tipo e Origem
    df_base = df[(df["[IS] Tipo de lead"].isin(filtro_tipo)) & (df["[IS] Origin do lead"].isin(filtro_origem))].copy()

    # Filtro de Data (HubSpot Style)
    if isinstance(periodo, (list, tuple)) and len(periodo) == 2:
        p_start, p_end = periodo[0], periodo[1]
        
        # Criamos as máscaras de data
        m_L = (df_base['Data de criação'].dt.date >= p_start) & (df_base['Data de criação'].dt.date <= p_end)
        m_C = (df_base['Data Contato'].dt.date >= p_start) & (df_base['Data Contato'].dt.date <= p_end)
        m_A = (df_base['Data Agendamento'].dt.date >= p_start) & (df_base['Data Agendamento'].dt.date <= p_end)
        m_R = (df_base['Data Reuniao'].dt.date >= p_start) & (df_base['Data Reuniao'].dt.date <= p_end)
        m_F = (df_base['Data Fechamento'].dt.date >= p_start) & (df_base['Data Fechamento'].dt.date <= p_end) & (df_base['Etapa do negócio'].isin(['Fechado', 'Pago']))
        
        # Filtro de Pessoa: Agora ele só filtra o SDR se o SDR estiver na linha, e o Closer se o Closer estiver na linha.
        # Isso impede que selecionar um Closer suma com os Leads de um SDR que ainda não agendou.
        if filtro_sdr:
            m_L &= df_base[col_sdr].isin(filtro_sdr)
            m_C &= df_base[col_sdr].isin(filtro_sdr)
            m_A &= df_base[col_sdr].isin(filtro_sdr)
            # Para reunião e fechamento, olhamos se foi o SDR OU o Closer selecionado
            m_R &= (df_base[col_sdr].isin(filtro_sdr)) | (df_base[col_closer].isin(filtro_closer))
            m_F &= (df_base[col_sdr].isin(filtro_sdr)) | (df_base[col_closer].isin(filtro_closer))
        
        L, C, A, R, F = m_L.sum(), m_C.sum(), m_A.sum(), m_R.sum(), m_F.sum()

    st.title("📊 Dashboard Comercial")

    # Métricas do Topo
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Leads", L)
    m2.metric("Contato", C, f"{(C/L*100):.1f}% s/ Lead" if L>0 else "0%")
    m3.metric("Agendado", A, f"{(A/C*100):.1f}% s/ Contato" if C>0 else "0%")
    m4.metric("Ocorrido", R, f"{(R/A*100):.1f}% s/ Agend." if A>0 else "0%")
    m5.metric("Fechado", F, f"{(F/R*100):.1f}% s/ Ocorr." if R>0 else "0%")

    st.divider()

    # Tabelas de Apoio (Respeitando os mesmos filtros)
    def criar_tabela(coluna):
        df_l = df_base[m_L].groupby(coluna).size().reset_index(name='Leads')
        df_r = df_base[m_R].groupby(coluna).size().reset_index(name='Reunioes')
        df_f_tab = df_base[m_F].groupby(coluna).size().reset_index(name='Fechados')
        
        tab = df_l.merge(df_r, on=coluna, how='outer').merge(df_f_tab, on=coluna, how='outer').fillna(0)
        tab['Lead x Reunião (%)'] = tab.apply(lambda r: f"{(r['Reunioes']/r['Leads']*100):.1f}%" if r['Leads'] > 0 else "-", axis=1)
        tab['Lead x Fechado (%)'] = tab.apply(lambda r: f"{(r['Fechados']/r['Leads']*100):.1f}%" if r['Leads'] > 0 else "-", axis=1)
        return tab[[coluna, 'Leads', 'Lead x Reunião (%)', 'Lead x Fechado (%)']].sort_values(by='Leads', ascending=False)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📍 Por Origem")
        st.dataframe(criar_tabela("[IS] Origin do lead"), use_container_width=True, hide_index=True)
    with c2:
        st.subheader("🏷️ Por Tipo")
        st.dataframe(criar_tabela("[IS] Tipo de lead"), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Erro: {e}")
