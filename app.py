import streamlit as st
import pandas as pd

# 1. Configuração de Layout e Estilo (Inalterado)
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
    
    # Tratamento de Datas (Lógica de Evento validada)
    df['Data de criação'] = pd.to_datetime(df['Data de criação'], errors='coerce')
    
    col_contato = 'Contato Realizado' if 'Contato Realizado' in df.columns else df.columns[df.columns.str.contains('Contato Realizado')].tolist()[0]
    df['Data Contato'] = pd.to_datetime(df[col_contato], errors='coerce')
    
    df['Data Agendamento'] = pd.to_datetime(df['[IS/SDR] Data do Agendamento'], errors='coerce')
    
    col_reuniao = '[IS/Closer] Reunião Ocorrida' if '[IS/Closer] Reunião Ocorrida' in df.columns else df.columns[df.columns.str.contains('Reunião Ocorrida')].tolist()[0]
    df['Data Reuniao'] = pd.to_datetime(df[col_reuniao], errors='coerce')
    
    df['Data Fechamento'] = pd.to_datetime(df['Data de fechamento'], errors='coerce')

    # Responsáveis
    col_sdr = '[IS/SDR] SDR Responsável'
    col_closer = '[IS/SDR] Closer Responsável'

    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("Filtros")
    data_min, data_max = df['Data de criação'].dropna().min().date(), df['Data de criação'].dropna().max().date()
    periodo = st.sidebar.date_input("Período do Evento", [data_min, data_max])
    
    filtro_tipo = st.sidebar.multiselect("Tipo de Lead", sorted(df["[IS] Tipo de lead"].dropna().unique()), default=df["[IS] Tipo de lead"].dropna().unique())
    filtro_origem = st.sidebar.multiselect("Origem do Lead", sorted(df["[IS] Origem do lead"].dropna().unique()), default=df["[IS] Origem do lead"].dropna().unique())

    lista_sdr = sorted(df[col_sdr].dropna().unique())
    filtro_sdr = st.sidebar.multiselect("SDR Responsável", lista_sdr, default=lista_sdr)

    lista_closer = sorted(df[col_closer].dropna().unique())
    filtro_closer = st.sidebar.multiselect("Closer Responsável", lista_closer, default=lista_closer)

    # --- LÓGICA DE FILTRAGEM (SEGURA) ---
    # Filtro de atributos base
    mask_base = (df["[IS] Tipo de lead"].isin(filtro_tipo)) & \
                (df["[IS] Origem do lead"].isin(filtro_origem)) & \
                (df[col_sdr].fillna('Vazio').isin(filtro_sdr if filtro_sdr else ['Vazio'])) & \
                (df[col_closer].fillna('Vazio').isin(filtro_closer if filtro_closer else ['Vazio']))
    
    df_f = df[mask_base].copy()

    if isinstance(periodo, (list, tuple)) and len(periodo) == 2:
        p_s, p_e = periodo[0], periodo[1]
        
        mask_L = (df_f['Data de criação'].dt.date >= p_s) & (df_f['Data de criação'].dt.date <= p_e)
        mask_C = (df_f['Data Contato'].dt.date >= p_s) & (df_f['Data Contato'].dt.date <= p_e)
        mask_A = (df_f['Data Agendamento'].dt.date >= p_s) & (df_f['Data Agendamento'].dt.date <= p_e)
        mask_R = (df_f['Data Reuniao'].dt.date >= p_s) & (df_f['Data Reuniao'].dt.date <= p_e)
        mask_F = (df_f['Data Fechamento'].dt.date >= p_s) & (df_f['Data Fechamento'].dt.date <= p_e) & (df_f['Etapa do negócio'].isin(['Fechado', 'Pago']))
        
        L, C, A, R, F = mask_L.sum(), mask_C.sum(), mask_A.sum(), mask_R.sum(), mask_F.sum()

    st.title("📊 Dashboard Comercial")

    # Topo
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Leads", L)
    m2.metric("Contato", C, f"{(C/L*100):.1f}% s/ Lead" if L>0 else "0%")
    m3.metric("Agendado", A, f"{(A/C*100):.1f}% s/ Contato" if C>0 else "0%")
    m4.metric("Ocorrido", R, f"{(R/A*100):.1f}% s/ Agend." if A>0 else "0%")
    m5.metric("Fechado", F, f"{(F/R*100):.1f}% s/ Ocorr." if R>0 else "0%")

    st.divider()

    # Tabelas (Origem e Tipo)
    def criar_tabela(coluna):
        l_cat = df_f[mask_L].groupby(coluna).size().reset_index(name='Leads')
        r_cat = df_f[mask_R].groupby(coluna).size().reset_index(name='Reunioes')
        f_cat = df_f[mask_F].groupby(coluna).size().reset_index(name='Fechados')
        
        t = l_cat.merge(r_cat, on=coluna, how='outer').merge(f_cat, on=coluna, how='outer').fillna(0)
        t['Lead x Reunião (%)'] = t.apply(lambda row: f"{(row['Reunioes']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
        t['Lead x Fechado (%)'] = t.apply(lambda row: f"{(row['Fechados']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
        return t[[coluna, 'Leads', 'Lead x Reunião (%)', 'Lead x Fechado (%)']].sort_values(by='Leads', ascending=False)

    ca, cb = st.columns(2)
    with ca:
        st.subheader("📍 Por Origem")
        st.dataframe(criar_tabela("[IS] Origem do lead"), use_container_width=True, hide_index=True)
    with cb:
        st.subheader("🏷️ Por Tipo")
        st.dataframe(criar_tabela("[IS] Tipo de lead"), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Erro Crítico: {e}")
