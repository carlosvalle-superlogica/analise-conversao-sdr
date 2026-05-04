import streamlit as st
import pandas as pd

# 1. Configuração de Layout e Estilo
st.set_page_config(page_title="Hub Comercial", layout="wide", initial_sidebar_state="expanded")

# --- CSS BASEADO NO SEU TEMPLATE TAILWIND ---
st.markdown("""
    <style>
    /* Importando a fonte Inter idêntica ao seu HTML */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* 1. RESET E FUNDO PRINCIPAL */
    .stApp {
        background-color: #f8f9ff !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Textos Gerais */
    .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label {
        color: #0b1c30 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* 2. BARRA LATERAL (Slate 900) */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b !important;
    }
    
    /* 3. MENU DE NAVEGAÇÃO (Efeito Tailwind: Hover e Item Ativo com borda azul) */
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
        display: none !important; /* Esconde a bolinha do radio button */
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        padding: 10px 16px !important;
        border-radius: 6px !important;
        margin-bottom: 4px !important;
        color: #94a3b8 !important; /* text-slate-400 */
        font-weight: 500 !important;
        font-size: 14px !important;
        transition: all 0.2s ease !important;
        background-color: transparent !important;
        border-left: 4px solid transparent !important;
    }
    /* Efeito de Hover */
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: rgba(30, 41, 59, 0.5) !important; /* hover:bg-slate-800/50 */
        color: #f1f5f9 !important; /* hover:text-slate-100 */
    }
    /* Efeito de Item Selecionado (Borda Azul Tailwind) */
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #1e293b !important; /* bg-slate-800 */
        color: #ffffff !important;
        border-left: 4px solid #3b82f6 !important; /* border-blue-500 */
        border-radius: 0 6px 6px 0 !important;
    }

    /* 4. CARDS DE MÉTRICAS (Bento Grid Style) */
    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 20px !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
    }
    /* Título do KPI (Uppercase e Tracking Wider) */
    [data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    /* Valor do KPI */
    [data-testid="stMetricValue"] {
        color: #0b1c30 !important;
        font-size: 36px !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        line-height: 44px !important;
        margin-top: 8px !important;
    }
    
    /* 5. Percentagens (Tags Tailwind) */
    [data-testid="stMetricDelta"] > div {
        background-color: #eff6ff !important;
        color: #2563eb !important;
        border-radius: 4px !important;
        padding: 2px 8px !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        margin-top: 6px !important;
    }
    [data-testid="stMetricDelta"] svg { display: none !important; }

    /* 6. Expander de Filtros */
    [data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
    }
    
    /* 7. Tabelas */
    .stDataFrame {
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        background-color: #ffffff !important;
        padding: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)

try:
    # -------------------------------------------------------------
    # BASE MATEMÁTICA DEFINITIVA (INTOCÁVEL)
    # -------------------------------------------------------------
    df = pd.read_csv('bd-teste-sistema.csv')
    df.columns = df.columns.str.strip()
    
    df['Data de criação'] = pd.to_datetime(df['Data de criação'], errors='coerce')
    col_contato = 'Contato Realizado' if 'Contato Realizado' in df.columns else df.columns[df.columns.str.contains('Contato Realizado')].tolist()[0]
    df['Data Contato'] = pd.to_datetime(df[col_contato], errors='coerce')
    df['Data Agendamento'] = pd.to_datetime(df['[IS/SDR] Data do Agendamento'], errors='coerce')
    col_reuniao = '[IS/Closer] Reunião Ocorrida' if '[IS/Closer] Reunião Ocorrida' in df.columns else df.columns[df.columns.str.contains('Reunião Ocorrida')].tolist()[0]
    df['Data Reuniao'] = pd.to_datetime(df[col_reuniao], errors='coerce')
    df['Data Fechamento'] = pd.to_datetime(df['Data de fechamento'], errors='coerce')
    
    col_sdr = '[IS/SDR] SDR Responsável'
    col_closer = '[IS/SDR] Closer Responsável'
    
    df['Filtro_SDR'] = df[col_sdr].fillna('Sem SDR')
    df['Filtro_Closer'] = df[col_closer].fillna('Sem Closer')
    # -------------------------------------------------------------

    # ==========================================
    # MENU LATERAL - Estilo App Tailwind
    # ==========================================
    st.sidebar.markdown("""
        <div style="padding: 10px 0px 20px 0px; display: flex; align-items: center; gap: 10px;">
            <div style="width: 32px; height: 32px; background-color: #2563eb; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">C</div>
            <div>
                <div style="color: white; font-size: 18px; font-weight: 700; font-family: 'Inter';">ConversionCRM</div>
                <div style="color: #94a3b8; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; font-weight: 700;">Enterprise Analytics</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    menu_opcoes = [
        "Dashboard de Conversão", 
        "Comercial por Produto", 
        "Cancelamentos / Churn",
        "Configurações"
    ]
    
    pagina_selecionada = st.sidebar.radio("Navegação", menu_opcoes, label_visibility="collapsed")

    # ==========================================
    # PÁGINA 1: DASHBOARD COMERCIAL
    # ==========================================
    if pagina_selecionada == "Dashboard de Conversão":
        
        # Cabeçalho Idêntico ao HTML
        st.markdown("""
            <div style="margin-bottom: 24px;">
                <h1 style="font-size: 24px; font-weight: 600; color: #0b1c30; margin-bottom: 4px; padding: 0;">Dashboard de Conversão Geral</h1>
                <p style="font-size: 14px; color: #45464d; margin: 0;">Visão consolidada do desempenho do funil de vendas em tempo real.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Filtros dentro do Expander
        with st.expander("Filtros do Relatório", expanded=True):
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                data_min, data_max = df['Data de criação'].dropna().min().date(), df['Data de criação'].dropna().max().date()
                periodo = st.date_input("Período do Evento", [data_min, data_max])
            with col_f2:
                tipos = sorted(df["[IS] Tipo de lead"].dropna().unique().tolist())
                filtro_tipo = st.multiselect("Tipo de Lead", tipos, default=tipos)
                origens = sorted(df["[IS] Origem do lead"].dropna().unique().tolist())
                filtro_origem = st.multiselect("Origem do Lead", origens, default=origens)
            with col_f3:
                lista_sdr = sorted(df['Filtro_SDR'].unique().tolist())
                filtro_sdr = st.multiselect("SDR Responsável", lista_sdr, default=lista_sdr)
                lista_closer = sorted(df['Filtro_Closer'].unique().tolist())
                filtro_closer = st.multiselect("Closer Responsável", lista_closer, default=lista_closer)

        # Lógica de Filtro
        mask_atributos = (
            (df["[IS] Tipo de lead"].isin(filtro_tipo)) & 
            (df["[IS] Origem do lead"].isin(filtro_origem)) &
            (df['Filtro_SDR'].isin(filtro_sdr)) &
            (df['Filtro_Closer'].isin(filtro_closer))
        )
        df_base = df[mask_atributos].copy()

        if isinstance(periodo, (list, tuple)) and len(periodo) == 2:
            p_start, p_end = periodo[0], periodo[1]
            mask_L = (df_base['Data de criação'].dt.date >= p_start) & (df_base['Data de criação'].dt.date <= p_end)
            mask_C = (df_base['Data Contato'].dt.date >= p_start) & (df_base['Data Contato'].dt.date <= p_end)
            mask_A = (df_base['Data Agendamento'].dt.date >= p_start) & (df_base['Data Agendamento'].dt.date <= p_end)
            mask_R = (df_base['Data Reuniao'].dt.date >= p_start) & (df_base['Data Reuniao'].dt.date <= p_end)
            mask_F = (df_base['Data Fechamento'].dt.date >= p_start) & (df_base['Data Fechamento'].dt.date <= p_end) & (df_base['Etapa do negócio'].isin(['Fechado', 'Pago']))
        else:
            mask_L = df_base['Data de criação'].notna()
            mask_C = df_base['Data Contato'].notna()
            mask_A = df_base['Data Agendamento'].notna()
            mask_R = df_base['Data Reuniao'].notna()
            mask_F = df_base['Etapa do negócio'].isin(['Fechado', 'Pago'])

        L, C, A, R, F = mask_L.sum(), mask_C.sum(), mask_A.sum(), mask_R.sum(), mask_F.sum()

        st.write("") 
        
        # Grid de KPIs (Agora formatados com o CSS do Tailwind)
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Leads Entrantes", L)
        m2.metric("Contato", C, f"{(C/L*100):.1f}% s/ Lead" if L>0 else "0%")
        m3.metric("Agendado", A, f"{(A/C*100):.1f}% s/ Cont." if C>0 else "0%")
        m4.metric("Ocorrido", R, f"{(R/A*100):.1f}% s/ Agend." if A>0 else "0%")
        m5.metric("Fechado", F, f"{(F/R*100):.1f}% s/ Ocorr." if R>0 else "0%")

        st.divider()

        # TABELAS
        def criar_tabela_evento(coluna_nome):
            leads_cat = df_base[mask_L].groupby(coluna_nome).size().reset_index(name='Leads')
            reunioes_cat = df_base[mask_R].groupby(coluna_nome).size().reset_index(name='Reunioes')
            fechados_cat = df_base[mask_F].groupby(coluna_nome).size().reset_index(name='Fechados')
            tabela = leads_cat.merge(reunioes_cat, on=coluna_nome, how='outer').merge(fechados_cat, on=coluna_nome, how='outer').fillna(0)
            tabela['Lead x Reunião (%)'] = tabela.apply(lambda row: f"{(row['Reunioes']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
            tabela['Lead x Fechado (%)'] = tabela.apply(lambda row: f"{(row['Fechados']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
            return tabela[[coluna_nome, 'Leads', 'Lead x Reunião (%)', 'Lead x Fechado (%)']].sort_values(by='Leads', ascending=False)

        c_a, c_b = st.columns(2)
        with c_a:
            st.markdown("#### Por Origem")
            st.dataframe(criar_tabela_evento("[IS] Origem do lead"), use_container_width=True, hide_index=True)
        with c_b:
            st.markdown("#### Por Tipo")
            st.dataframe(criar_tabela_evento("[IS] Tipo de lead"), use_container_width=True, hide_index=True)

        st.divider()

        st.markdown("#### Performance por SDR")
        sdr_l = df_base[mask_L].groupby('Filtro_SDR').size().reset_index(name='Leads')
        sdr_c = df_base[mask_C].groupby('Filtro_SDR').size().reset_index(name='Contatos')
        sdr_a = df_base[mask_A].groupby('Filtro_SDR').size().reset_index(name='Agendados')
        sdr_r = df_base[mask_R].groupby('Filtro_SDR').size().reset_index(name='Ocorridos')
        df_sdr = sdr_l.merge(sdr_c, on='Filtro_SDR', how='outer').merge(sdr_a, on='Filtro_SDR', how='outer').merge(sdr_r, on='Filtro_SDR', how='outer').fillna(0)
        df_sdr = df_sdr.rename(columns={'Filtro_SDR': 'SDR Responsável'})
        df_sdr['Cont/Lead (%)'] = df_sdr.apply(lambda row: f"{(row['Contatos']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
        df_sdr['Agend/Cont (%)'] = df_sdr.apply(lambda row: f"{(row['Agendados']/row['Contatos']*100):.1f}%" if row['Contatos'] > 0 else "-", axis=1)
        df_sdr['Ocorr/Agend (%)'] = df_sdr.apply(lambda row: f"{(row['Ocorridos']/row['Agendados']*100):.1f}%" if row['Agendados'] > 0 else "-", axis=1)
        col_sdr = ['SDR Responsável', 'Leads', 'Contatos', 'Agendados', 'Ocorridos', 'Cont/Lead (%)', 'Agend/Cont (%)', 'Ocorr/Agend (%)']
        st.dataframe(df_sdr[col_sdr].sort_values(by='Leads', ascending=False), use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("#### Eficiência Geral de Fechamento")
        col_ef1, col_ef2 = st.columns(2)
        
        with col_ef1:
            st.write("**SDR: Lead x Ocorrido e Fechado**")
            sdr_ef_l = df_base[mask_L].groupby('Filtro_SDR').size().reset_index(name='Leads')
            sdr_ef_r = df_base[mask_R].groupby('Filtro_SDR').size().reset_index(name='Ocorridos')
            sdr_ef_f = df_base[mask_F].groupby('Filtro_SDR').size().reset_index(name='Fechados')
            ef_sdr = sdr_ef_l.merge(sdr_ef_r, on='Filtro_SDR', how='outer').merge(sdr_ef_f, on='Filtro_SDR', how='outer').fillna(0)
            ef_sdr = ef_sdr.rename(columns={'Filtro_SDR': 'SDR Responsável'})
            ef_sdr['Lead x Ocorrido (%)'] = ef_sdr.apply(lambda row: f"{(row['Ocorridos']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
            ef_sdr['Lead x Fechado (%)'] = ef_sdr.apply(lambda row: f"{(row['Fechados']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
            col_ef_sdr = ['SDR Responsável', 'Leads', 'Ocorridos', 'Fechados', 'Lead x Ocorrido (%)', 'Lead x Fechado (%)']
            st.dataframe(ef_sdr[col_ef_sdr].sort_values(by='Leads', ascending=False), use_container_width=True, hide_index=True)

        with col_ef2:
            st.write("**Closer: Ocorrido x Fechado**")
            mask_has_closer = df_base['Filtro_Closer'] != 'Sem Closer'
            cl_ef_r = df_base[mask_R & mask_has_closer].groupby('Filtro_Closer').size().reset_index(name='Ocorridos')
            cl_ef_f = df_base[mask_F & mask_has_closer].groupby('Filtro_Closer').size().reset_index(name='Fechados')
            ef_cl = cl_ef_r.merge(cl_ef_f, on='Filtro_Closer', how='outer').fillna(0)
            ef_cl = ef_cl.rename(columns={'Filtro_Closer': 'Closer Responsável'})
            ef_cl['Ocorrido x Fechado (%)'] = ef_cl.apply(lambda row: f"{(row['Fechados']/row['Ocorridos']*100):.1f}%" if row['Ocorridos'] > 0 else "-", axis=1)
            col_ef_cl = ['Closer Responsável', 'Ocorridos', 'Fechados', 'Ocorrido x Fechado (%)']
            st.dataframe(ef_cl[col_ef_cl].sort_values(by='Ocorridos', ascending=False), use_container_width=True, hide_index=True)

    # ==========================================
    # PÁGINAS FUTURAS
    # ==========================================
    elif pagina_selecionada == "Comercial por Produto":
        st.markdown("<h1 style='color: #0b1c30;'>Comercial por Produto</h1>", unsafe_allow_html=True)
        st.info("Módulo em desenvolvimento.")
        
    elif pagina_selecionada == "Cancelamentos / Churn":
        st.markdown("<h1 style='color: #0b1c30;'>Cancelamentos e Churn</h1>", unsafe_allow_html=True)
        st.info("Módulo em desenvolvimento.")
        
    elif pagina_selecionada == "Configurações":
        st.markdown("<h1 style='color: #0b1c30;'>Configurações</h1>", unsafe_allow_html=True)
        st.info("Painel de administração.")

except Exception as e:
    st.error(f"Erro Crítico: {e}")
