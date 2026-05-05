import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO DE LAYOUT (Fiel ao Original)
st.set_page_config(page_title="Sistema de Gestão - Marketing", layout="wide")

# Estilo para manter o padrão Azul e remover o vermelho de avisos
st.markdown("""
    <style>
    [data-testid="stMetricLabel"] { color: #1565C0 !important; font-weight: bold; }
    h1, h2, h3 { color: #1565C0 !important; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    /* Remove o vermelho padrão de seleções vazias se houver */
    .stMultiSelect span { color: #1565C0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE ACESSO ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
    st.session_state['perfil'] = None

def login():
    st.title("🔐 Login de Acesso")
    u = st.text_input("Login")
    s = st.text_input("Senha", type="password")
    if st.button("Acessar"):
        if u == "aquisições" and s == "1987":
            st.session_state.update({'autenticado': True, 'perfil': 'admin'})
            st.rerun()
        elif u == "mkt" and s == "123":
            st.session_state.update({'autenticado': True, 'perfil': 'operador'})
            st.rerun()
        else:
            st.error("Dados incorretos")

if not st.session_state['autenticado']:
    login()
else:
    # --- LOGOUT E TÍTULO ---
    if st.sidebar.button("Sair"):
        st.session_state['autenticado'] = False
        st.rerun()

    # CARREGAMENTO DE DADOS
    try:
        df = pd.read_csv('bd-teste-sistema.csv')
        df.columns = df.columns.str.strip()

        # Tratamento de Datas (Motor Original)
        df['Data de criação'] = pd.to_datetime(df['Data de criação'], errors='coerce')
        col_cont = 'Contato Realizado' if 'Contato Realizado' in df.columns else df.columns[df.columns.str.contains('Contato Realizado')].tolist()[0]
        df['Data Contato'] = pd.to_datetime(df[col_cont], errors='coerce')
        df['Data Agendamento'] = pd.to_datetime(df['[IS/SDR] Data do Agendamento'], errors='coerce')
        col_reun = '[IS/Closer] Reunião Ocorrida' if '[IS/Closer] Reunião Ocorrida' in df.columns else df.columns[df.columns.str.contains('Reunião Ocorrida')].tolist()[0]
        df['Data Reuniao'] = pd.to_datetime(df[col_reun], errors='coerce')
        df['Data Fechamento'] = pd.to_datetime(df['Data de fechamento'], errors='coerce')

        # --- BARRA LATERAL (IDÊNTICA À ORIGINAL) ---
        st.sidebar.image("https://logodownload.org/wp-content/uploads/2014/04/hubspot-logo.png", width=150) # Opcional: logo do hubspot ou sua
        
        # Filtro de Data
        data_min, data_max = df['Data de criação'].dropna().min().date(), df['Data de criação'].dropna().max().date()
        periodo = st.sidebar.date_input("Selecione o Período", [data_min, data_max])

        # FILTROS DE ORIGEM E TIPO (Mantidos como na visão original)
        lista_origens = sorted(df["[IS] Origem do lead"].dropna().unique().tolist())
        origens_sel = st.sidebar.multiselect("Origem do Lead", lista_origens, default=lista_origens)

        lista_tipos = sorted(df["[IS] Tipo de Lead"].dropna().unique().tolist())
        tipos_sel = st.sidebar.multiselect("Tipo de Lead", lista_tipos, default=lista_tipos)

        # Filtro de SDR e Closer - SÓ APARECE PARA ADMIN
        if st.session_state['perfil'] == "admin":
            lista_sdrs = sorted(df["[IS/SDR] SDR Responsável"].dropna().unique().tolist())
            sdrs_sel = st.sidebar.multiselect("SDR Responsável", lista_sdrs, default=lista_sdrs)
            
            lista_closers = sorted(df["[IS/SDR] Closer Responsável"].dropna().unique().tolist())
            closers_sel = st.sidebar.multiselect("Closer Responsável", lista_closers, default=lista_closers)
        else:
            # Se for marketing, ele "seleciona" todos internamente para não quebrar o cálculo
            sdrs_sel = df["[IS/SDR] SDR Responsável"].unique().tolist()
            closers_sel = df["[IS/SDR] Closer Responsável"].unique().tolist()

        # --- APLICAÇÃO DOS FILTROS ---
        df_base = df[
            (df["[IS] Origem do lead"].isin(origens_sel)) &
            (df["[IS] Tipo de Lead"].isin(tipos_sel)) &
            (df["[IS/SDR] SDR Responsável"].fillna('Vazio').isin(sdrs_sel)) &
            (df["[IS/SDR] Closer Responsável"].fillna('Vazio').isin(closers_sel))
        ].copy()

        if len(periodo) == 2:
            p_start, p_end = periodo[0], periodo[1]
            
            # Filtros de Funil por Período
            mL = (df_base['Data de criação'].dt.date >= p_start) & (df_base['Data de criação'].dt.date <= p_end)
            mC = (df_base['Data Contato'].dt.date >= p_start) & (df_base['Data Contato'].dt.date <= p_end)
            mA = (df_base['Data Agendamento'].dt.date >= p_start) & (df_base['Data Agendamento'].dt.date <= p_end)
            mR = (df_base['Data Reuniao'].dt.date >= p_start) & (df_base['Data Reuniao'].dt.date <= p_end)
            mF = (df_base['Data Fechamento'].dt.date >= p_start) & (df_base['Data Fechamento'].dt.date <= p_end) & (df_base['Etapa do negócio'].isin(['Fechado', 'Pago']))

            # DASHBOARD PRINCIPAL
            st.title("🚀 Dashboard de Performance")
            
            # Linha de Métricas (Igual ao Print)
            L, C, A, R, F = mL.sum(), mC.sum(), mA.sum(), mR.sum(), mF.sum()
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Leads", f"{L}")
            col2.metric("Contatos", f"{C}", f"{(C/L*100):.1f}%" if L>0 else "0%")
            col3.metric("Agendados", f"{A}", f"{(A/C*100):.1f}%" if C>0 else "0%")
            col4.metric("Reuniões", f"{R}", f"{(R/A*100):.1f}%" if A>0 else "0%")
            col5.metric("Fechados", f"{F}", f"{(F/R*100):.1f}%" if R>0 else "0%")

            st.write("---")

            # Tabelas de Apoio
            st.subheader("📊 Conversão por Origem do Lead")
            leads_orig = df_base[mL].groupby("[IS] Origem do lead").size().reset_index(name='Leads')
            fechados_orig = df_base[mF].groupby("[IS] Origem do lead").size().reset_index(name='Vendas')
            tab_orig = leads_orig.merge(fechados_orig, on="[IS] Origem do lead", how="left").fillna(0)
            tab_orig['% Conv'] = (tab_orig['Vendas']/tab_orig['Leads']*100).map('{:.1f}%'.format)
            st.dataframe(tab_orig.sort_values("Leads", ascending=False), use_container_width=True, hide_index=True)

            # ACUMULADO ANUAL - SÓ APARECE PARA ADMIN
            if st.session_state['perfil'] == "admin":
                st.write("---")
                st.subheader(f"📈 Acumulado do Ano ({p_end.year})")
                mY_L = df_base['Data de criação'].dt.year == p_end.year
                mY_F = (df_base['Data Fechamento'].dt.year == p_end.year) & (df_base['Etapa do negócio'].isin(['Fechado', 'Pago']))
                ca1, ca2 = st.columns(2)
                ca1.metric("Total Leads YTD", f"{mY_L.sum()}")
                ca2.metric("Total Fechados YTD", f"{mY_F.sum()}")

    except Exception as e:
        st.error(f"Erro ao processar: {e}")
