import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO DE LAYOUT (Fiel ao Original)
st.set_page_config(page_title="Sistema de Gestão", layout="wide")

st.markdown("""
    <style>
    /* Estilo validado e idêntico ao layout original */
    .stApp { background-color: #F0F8FF; }
    span[data-baseweb="tag"] { background-color: #1565C0 !important; color: white !important; }
    div[data-testid="stMetricValue"] {
        background-color: #FFFFFF; border-radius: 10px; padding: 10px; border: 1px solid #90CAF9; color: #0D47A1;
    }
    [data-testid="stMetricDelta"] > div {
        background-color: #1565C0 !important; color: white !important; border-radius: 5px; padding: 2px 8px; font-weight: bold;
    }
    [data-testid="stMetricDelta"] svg { display: none; }
    h1, h2, h3, h4 { color: #0D47A1 !important; }
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
    # --- LOGOUT ---
    if st.sidebar.button("Sair"):
        st.session_state['autenticado'] = False
        st.rerun()

    # CARREGAMENTO DE DADOS E MOTOR MATEMÁTICO INTACTO
    try:
        df = pd.read_csv('bd-teste-sistema.csv')
        df.columns = df.columns.str.strip()

        df['Data de criação'] = pd.to_datetime(df['Data de criação'], errors='coerce')
        col_cont = 'Contato Realizado' if 'Contato Realizado' in df.columns else df.columns[df.columns.str.contains('Contato Realizado')].tolist()[0]
        df['Data Contato'] = pd.to_datetime(df[col_cont], errors='coerce')
        df['Data Agendamento'] = pd.to_datetime(df['[IS/SDR] Data do Agendamento'], errors='coerce')
        col_reun = '[IS/Closer] Reunião Ocorrida' if '[IS/Closer] Reunião Ocorrida' in df.columns else df.columns[df.columns.str.contains('Reunião Ocorrida')].tolist()[0]
        df['Data Reuniao'] = pd.to_datetime(df[col_reun], errors='coerce')
        df['Data Fechamento'] = pd.to_datetime(df['Data de fechamento'], errors='coerce')

        # Garantia contra erros de dados em branco
        df['Filtro_SDR'] = df['[IS/SDR] SDR Responsável'].fillna('Sem SDR')
        df['Filtro_Closer'] = df['[IS/SDR] Closer Responsável'].fillna('Sem Closer')

        # --- BARRA LATERAL (IDÊNTICA À ORIGINAL) ---
        st.sidebar.header("Filtros")
        
        data_min, data_max = df['Data de criação'].dropna().min().date(), df['Data de criação'].dropna().max().date()
        periodo = st.sidebar.date_input("Período do Evento", [data_min, data_max])

        lista_origens = sorted(df["[IS] Origem do lead"].dropna().unique().tolist())
        origens_sel = st.sidebar.multiselect("Origem do Lead", lista_origens, default=lista_origens)

        # CORREÇÃO DO ERRO APLICADA AQUI (Tipo de lead com "l" minúsculo)
        lista_tipos = sorted(df["[IS] Tipo de lead"].dropna().unique().tolist())
        tipos_sel = st.sidebar.multiselect("Tipo de Lead", lista_tipos, default=lista_tipos)

        # Filtro de SDR e Closer - SÓ APARECE PARA ADMIN
        if st.session_state['perfil'] == "admin":
            lista_sdrs = sorted(df['Filtro_SDR'].unique().tolist())
            sdrs_sel = st.sidebar.multiselect("SDR Responsável", lista_sdrs, default=lista_sdrs)
            
            lista_closers = sorted(df['Filtro_Closer'].unique().tolist())
            closers_sel = st.sidebar.multiselect("Closer Responsável", lista_closers, default=lista_closers)
        else:
            # Se for MKT, carrega todas as opções de equipe internamente para não quebrar a conta
            sdrs_sel = df['Filtro_SDR'].unique().tolist()
            closers_sel = df['Filtro_Closer'].unique().tolist()

        # --- APLICAÇÃO DOS FILTROS ---
        df_base = df[
            (df["[IS] Origem do lead"].isin(origens_sel)) &
            (df["[IS] Tipo de lead"].isin(tipos_sel)) &
            (df['Filtro_SDR'].isin(sdrs_sel)) &
            (df['Filtro_Closer'].isin(closers_sel))
        ].copy()

        if isinstance(periodo, (list, tuple)) and len(periodo) == 2:
            p_start, p_end = periodo[0], periodo[1]
            
            mL = (df_base['Data de criação'].dt.date >= p_start) & (df_base['Data de criação'].dt.date <= p_end)
            mC = (df_base['Data Contato'].dt.date >= p_start) & (df_base['Data Contato'].dt.date <= p_end)
            mA = (df_base['Data Agendamento'].dt.date >= p_start) & (df_base['Data Agendamento'].dt.date <= p_end)
            mR = (df_base['Data Reuniao'].dt.date >= p_start) & (df_base['Data Reuniao'].dt.date <= p_end)
            mF = (df_base['Data Fechamento'].dt.date >= p_start) & (df_base['Data Fechamento'].dt.date <= p_end) & (df_base['Etapa do negócio'].isin(['Fechado', 'Pago']))
        else:
            mL = df_base['Data de criação'].notna(); mC = df_base['Data Contato'].notna(); mA = df_base['Data Agendamento'].notna(); mR = df_base['Data Reuniao'].notna(); mF = df_base['Etapa do negócio'].isin(['Fechado', 'Pago'])

        # DASHBOARD PRINCIPAL
        st.title("📊 Dashboard Comercial")
        
        L, C, A, R, F = mL.sum(), mC.sum(), mA.sum(), mR.sum(), mF.sum()
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Leads", f"{L}")
        col2.metric("Contato", f"{C}", f"{(C/L*100):.1f}% s/ Lead" if L>0 else "0%")
        col3.metric("Agendado", f"{A}", f"{(A/C*100):.1f}% s/ Contato" if C>0 else "0%")
        col4.metric("Ocorrido", f"{R}", f"{(R/A*100):.1f}% s/ Agend." if A>0 else "0%")
        col5.metric("Fechado", f"{F}", f"{(F/R*100):.1f}% s/ Ocorr." if R>0 else "0%")

        st.divider()

        # Tabelas de Origem e Tipo
        def criar_tabela_evento(coluna_nome):
            leads_cat = df_base[mL].groupby(coluna_nome).size().reset_index(name='Leads')
            reunioes_cat = df_base[mR].groupby(coluna_nome).size().reset_index(name='Reunioes')
            fechados_cat = df_base[mF].groupby(coluna_nome).size().reset_index(name='Fechados')
            tabela = leads_cat.merge(reunioes_cat, on=coluna_nome, how='outer').merge(fechados_cat, on=coluna_nome, how='outer').fillna(0)
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

        # SE O USUÁRIO FOR ADMIN, ELE VÊ O RESTANTE
        if st.session_state['perfil'] == "admin":
            st.divider()
            
            st.subheader("🏆 Performance por SDR")
            sdr_l = df_base[mL].groupby('Filtro_SDR').size().reset_index(name='Leads')
            sdr_c = df_base[mC].groupby('Filtro_SDR').size().reset_index(name='Contatos')
            sdr_a = df_base[mA].groupby('Filtro_SDR').size().reset_index(name='Agendados')
            sdr_r = df_base[mR].groupby('Filtro_SDR').size().reset_index(name='Ocorridos')
            df_sdr = sdr_l.merge(sdr_c, on='Filtro_SDR', how='outer').merge(sdr_a, on='Filtro_SDR', how='outer').merge(sdr_r, on='Filtro_SDR', how='outer').fillna(0).rename(columns={'Filtro_SDR': 'SDR Responsável'})
            df_sdr['Cont/Lead (%)'] = df_sdr.apply(lambda row: f"{(row['Contatos']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
            df_sdr['Agend/Cont (%)'] = df_sdr.apply(lambda row: f"{(row['Agendados']/row['Contatos']*100):.1f}%" if row['Contatos'] > 0 else "-", axis=1)
            df_sdr['Ocorr/Agend (%)'] = df_sdr.apply(lambda row: f"{(row['Ocorridos']/row['Agendados']*100):.1f}%" if row['Agendados'] > 0 else "-", axis=1)
            col_sdr = ['SDR Responsável', 'Leads', 'Contatos', 'Agendados', 'Ocorridos', 'Cont/Lead (%)', 'Agend/Cont (%)', 'Ocorr/Agend (%)']
            st.dataframe(df_sdr[col_sdr].sort_values(by='Leads', ascending=False), use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("🎯 Eficiência Geral de Fechamento")
            
            col_ef1, col_ef2 = st.columns(2)
            with col_ef1:
                st.write("**SDR: Lead x Ocorrido e Fechado**")
                sdr_ef_l = df_base[mL].groupby('Filtro_SDR').size().reset_index(name='Leads')
                sdr_ef_r = df_base[mR].groupby('Filtro_SDR').size().reset_index(name='Ocorridos')
                sdr_ef_f = df_base[mF].groupby('Filtro_SDR').size().reset_index(name='Fechados')
                ef_sdr = sdr_ef_l.merge(sdr_ef_r, on='Filtro_SDR', how='outer').merge(sdr_ef_f, on='Filtro_SDR', how='outer').fillna(0).rename(columns={'Filtro_SDR': 'SDR Responsável'})
                ef_sdr['Lead x Ocorrido (%)'] = ef_sdr.apply(lambda row: f"{(row['Ocorridos']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
                ef_sdr['Lead x Fechado (%)'] = ef_sdr.apply(lambda row: f"{(row['Fechados']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
                st.dataframe(ef_sdr[['SDR Responsável', 'Leads', 'Ocorridos', 'Fechados', 'Lead x Ocorrido (%)', 'Lead x Fechado (%)']].sort_values(by='Leads', ascending=False), use_container_width=True, hide_index=True)

            with col_ef2:
                st.write("**Closer: Ocorrido x Fechado**")
                mask_has_closer = df_base['Filtro_Closer'] != 'Sem Closer'
                cl_ef_r = df_base[mR & mask_has_closer].groupby('Filtro_Closer').size().reset_index(name='Ocorridos')
                cl_ef_f = df_base[mF & mask_has_closer].groupby('Filtro_Closer').size().reset_index(name='Fechados')
                ef_cl = cl_ef_r.merge(cl_ef_f, on='Filtro_Closer', how='outer').fillna(0).rename(columns={'Filtro_Closer': 'Closer Responsável'})
                ef_cl['Ocorrido x Fechado (%)'] = ef_cl.apply(lambda row: f"{(row['Fechados']/row['Ocorridos']*100):.1f}%" if row['Ocorridos'] > 0 else "-", axis=1)
                st.dataframe(ef_cl[['Closer Responsável', 'Ocorridos', 'Fechados', 'Ocorrido x Fechado (%)']].sort_values(by='Ocorridos', ascending=False), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
