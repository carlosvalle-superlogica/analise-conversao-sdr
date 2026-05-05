import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO DE LAYOUT E ESTILO (Padrão Original Validado)
st.set_page_config(page_title="Sistema de Gestão Comercial", layout="wide")

st.markdown("""
    <style>
    /* Estilo para manter o padrão Azul e remover o vermelho */
    .stApp { background-color: #F0F8FF; }
    span[data-baseweb="tag"] { background-color: #1565C0 !important; color: white !important; }
    
    div[data-testid="stMetricValue"] {
        background-color: #FFFFFF; border-radius: 10px; padding: 10px; border: 1px solid #90CAF9; color: #0D47A1;
    }
    [data-testid="stMetricDelta"] > div {
        background-color: #1565C0 !important; color: white !important; border-radius: 5px; padding: 2px 8px; font-weight: bold;
    }
    [data-testid="stMetricDelta"] svg { display: none; }
    h1, h2, h3, h4 { color: #1565C0 !important; font-weight: 700 !important; }
    
    /* Forçar azul nos textos de multiselect para evitar vermelho */
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
    if st.button("Acessar Sistema"):
        # LOGIN MASTER (100% Liberado)
        if u == "aquisições" and s == "1987":
            st.session_state.update({'autenticado': True, 'perfil': 'master'})
            st.rerun()
        # LOGIN MKT (Visão Restrita)
        elif u == "mkt" and s == "123":
            st.session_state.update({'autenticado': True, 'perfil': 'operador'})
            st.rerun()
        else:
            st.error("Dados de acesso incorretos.")

if not st.session_state['autenticado']:
    login()
else:
    # --- BARRA LATERAL ---
    if st.sidebar.button("Encerrar Sessão"):
        st.session_state['autenticado'] = False
        st.rerun()

    try:
        # CARREGAMENTO DE DADOS
        df = pd.read_csv('bd-teste-sistema.csv')
        df.columns = df.columns.str.strip()

        # Tratamento de Datas (Motor Original Imutável)
        df['Data de criação'] = pd.to_datetime(df['Data de criação'], errors='coerce')
        col_cont = 'Contato Realizado' if 'Contato Realizado' in df.columns else df.columns[df.columns.str.contains('Contato Realizado')].tolist()[0]
        df['Data Contato'] = pd.to_datetime(df[col_cont], errors='coerce')
        df['Data Agendamento'] = pd.to_datetime(df['[IS/SDR] Data do Agendamento'], errors='coerce')
        col_reun = '[IS/Closer] Reunião Ocorrida' if '[IS/Closer] Reunião Ocorrida' in df.columns else df.columns[df.columns.str.contains('Reunião Ocorrida')].tolist()[0]
        df['Data Reuniao'] = pd.to_datetime(df[col_reun], errors='coerce')
        df['Data Fechamento'] = pd.to_datetime(df['Data de fechamento'], errors='coerce')

        # Preparação de nomes de equipe
        df['Filtro_SDR'] = df['[IS/SDR] SDR Responsável'].fillna('Sem SDR')
        df['Filtro_Closer'] = df['[IS/SDR] Closer Responsável'].fillna('Sem Closer')

        # --- FILTROS LATERAIS ---
        st.sidebar.header(f"Perfil: {st.session_state['perfil'].upper()}")
        
        data_min, data_max = df['Data de criação'].dropna().min().date(), df['Data de criação'].dropna().max().date()
        periodo = st.sidebar.date_input("Período do Evento", [data_min, data_max])

        lista_origens = sorted(df["[IS] Origem do lead"].dropna().unique().tolist())
        origens_sel = st.sidebar.multiselect("Origem do Lead", lista_origens, default=lista_origens)

        lista_tipos = sorted(df["[IS] Tipo de lead"].dropna().unique().tolist())
        tipos_sel = st.sidebar.multiselect("Tipo de Lead", lista_tipos, default=lista_tipos)

        # Filtros de SDR e Closer (SÓ APARECEM NO MASTER)
        if st.session_state['perfil'] == "master":
            lista_sdrs = sorted(df['Filtro_SDR'].unique().tolist())
            sdrs_sel = st.sidebar.multiselect("SDR Responsável", lista_sdrs, default=lista_sdrs)
            
            lista_closers = sorted(df['Filtro_Closer'].unique().tolist())
            closers_sel = st.sidebar.multiselect("Closer Responsável", lista_closers, default=lista_closers)
        else:
            sdrs_sel = df['Filtro_SDR'].unique().tolist()
            closers_sel = df['Filtro_Closer'].unique().tolist()

        # --- PROCESSAMENTO DOS DADOS ---
        mask_attr = (
            (df["[IS] Origem do lead"].isin(origens_sel)) &
            (df["[IS] Tipo de lead"].isin(tipos_sel)) &
            (df['Filtro_SDR'].isin(sdrs_sel)) &
            (df['Filtro_Closer'].isin(closers_sel))
        )
        df_base = df[mask_attr].copy()

        if len(periodo) == 2:
            p_start, p_end = periodo[0], periodo[1]
            mL = (df_base['Data de criação'].dt.date >= p_start) & (df_base['Data de criação'].dt.date <= p_end)
            mC = (df_base['Data Contato'].dt.date >= p_start) & (df_base['Data Contato'].dt.date <= p_end)
            mA = (df_base['Data Agendamento'].dt.date >= p_start) & (df_base['Data Agendamento'].dt.date <= p_end)
            mR = (df_base['Data Reuniao'].dt.date >= p_start) & (df_base['Data Reuniao'].dt.date <= p_end)
            mF = (df_base['Data Fechamento'].dt.date >= p_start) & (df_base['Data Fechamento'].dt.date <= p_end) & (df_base['Etapa do negócio'].isin(['Fechado', 'Pago']))
            ano_ref = p_end.year
        else:
            mL = df_base['Data de criação'].notna(); mC = df_base['Data Contato'].notna(); mA = df_base['Data Agendamento'].notna(); mR = df_base['Data Reuniao'].notna(); mF = df_base['Etapa do negócio'].isin(['Fechado', 'Pago'])
            ano_ref = 2026

        # --- INTERFACE ---
        st.title("📊 Dashboard Comercial")
        
        # 1. FUNIL DO PERÍODO (Para todos)
        L, C, A, R, F = mL.sum(), mC.sum(), mA.sum(), mR.sum(), mF.sum()
        st.subheader("📅 Resultados do Período")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Leads", f"{L}")
        c2.metric("Contato", f"{C}", f"{(C/L*100):.1f}%" if L>0 else "0%")
        c3.metric("Agendado", f"{A}", f"{(A/C*100):.1f}%" if C>0 else "0%")
        c4.metric("Ocorrido", f"{R}", f"{(R/A*100):.1f}%" if A>0 else "0%")
        c5.metric("Fechado", f"{F}", f"{(F/R*100):.1f}%" if R>0 else "0%")

        st.divider()

        # 2. TABELAS DE APOIO (Para todos)
        def criar_tabela_evento(coluna_nome):
            l_cat = df_base[mL].groupby(coluna_nome).size().reset_index(name='Leads')
            r_cat = df_base[mR].groupby(coluna_nome).size().reset_index(name='Reunioes')
            f_cat = df_base[mF].groupby(coluna_nome).size().reset_index(name='Fechados')
            t = l_cat.merge(r_cat, on=coluna_nome, how='outer').merge(f_cat, on=coluna_nome, how='outer').fillna(0)
            t['Lead x Fechado (%)'] = t.apply(lambda row: f"{(row['Fechados']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
            return t[[coluna_nome, 'Leads', 'Reunioes', 'Fechados', 'Lead x Fechado (%)']].sort_values(by='Leads', ascending=False)

        col_a, col_b = st.columns(2)
        with col_a: 
            st.subheader("📍 Por Origem")
            st.dataframe(criar_tabela_evento("[IS] Origem do lead"), use_container_width=True, hide_index=True)
        with col_b: 
            st.subheader("🏷️ Por Tipo")
            st.dataframe(criar_tabela_evento("[IS] Tipo de lead"), use_container_width=True, hide_index=True)

        # --- BLOCO MASTER (LIBERAÇÃO TOTAL) ---
        if st.session_state['perfil'] == "master":
            st.divider()
            
            # 3. ACUMULADO DO ANO
            st.subheader(f"📈 Acumulado do Ano ({ano_ref})")
            mY_L = df_base['Data de criação'].dt.year == ano_ref
            mY_C = df_base['Data Contato'].dt.year == ano_ref
            mY_A = df_base['Data Agendamento'].dt.year == ano_ref
            mY_R = df_base['Data Reuniao'].dt.year == ano_ref
            mY_F = (df_base['Data Fechamento'].dt.year == ano_ref) & (df_base['Etapa do negócio'].isin(['Fechado', 'Pago']))
            
            L_y, C_y, A_y, R_y, F_y = mY_L.sum(), mY_C.sum(), mY_A.sum(), mY_R.sum(), mY_F.sum()
            cy1, cy2, cy3, cy4, cy5 = st.columns(5)
            cy1.metric("Leads (Ano)", f"{L_y}")
            cy2.metric("Contatos (Ano)", f"{C_y}", f"{(C_y/L_y*100):.1f}%" if L_y>0 else "0%")
            cy3.metric("Agendados (Ano)", f"{A_y}", f"{(A_y/C_y*100):.1f}%" if C_y>0 else "0%")
            cy4.metric("Reuniões (Ano)", f"{R_y}", f"{(R_y/A_y*100):.1f}%" if A_y>0 else "0%")
            cy5.metric("Fechados (Ano)", f"{F_y}", f"{(F_y/R_y*100):.1f}%" if R_y>0 else "0%")

            st.divider()

            # 4. PERFORMANCE VENDEDORES (O que estava no código original "bom")
            st.subheader("🏆 Performance por SDR")
            sdr_l = df_base[mL].groupby('Filtro_SDR').size().reset_index(name='Leads')
            sdr_c = df_base[mC].groupby('Filtro_SDR').size().reset_index(name='Contatos')
            sdr_r = df_base[mR].groupby('Filtro_SDR').size().reset_index(name='Ocorridos')
            df_sdr = sdr_l.merge(sdr_c, on='Filtro_SDR', how='outer').merge(sdr_r, on='Filtro_SDR', how='outer').fillna(0).rename(columns={'Filtro_SDR': 'SDR Responsável'})
            df_sdr['Ocorr/Lead (%)'] = df_sdr.apply(lambda row: f"{(row['Ocorridos']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
            st.dataframe(df_sdr.sort_values(by='Leads', ascending=False), use_container_width=True, hide_index=True)

            st.write("")
            st.subheader("🎯 Eficiência Closer")
            cl_ef_r = df_base[mR & (df_base['Filtro_Closer'] != 'Sem Closer')].groupby('Filtro_Closer').size().reset_index(name='Ocorridos')
            cl_ef_f = df_base[mF & (df_base['Filtro_Closer'] != 'Sem Closer')].groupby('Filtro_Closer').size().reset_index(name='Fechados')
            ef_cl = cl_ef_r.merge(cl_ef_f, on='Filtro_Closer', how='outer').fillna(0).rename(columns={'Filtro_Closer': 'Closer Responsável'})
            ef_cl['Taxa de Fecho (%)'] = ef_cl.apply(lambda row: f"{(row['Fechados']/row['Ocorridos']*100):.1f}%" if row['Ocorridos'] > 0 else "-", axis=1)
            st.dataframe(ef_cl.sort_values(by='Ocorridos', ascending=False), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
