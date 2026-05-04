import streamlit as st
import pandas as pd

# ==========================================
# 1. CONFIGURAÇÃO DE LAYOUT E ESTILO (SAAS PREMIUM)
# ==========================================
st.set_page_config(page_title="ConversionCRM Analytics", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Importa a fonte Inter (Padrão de SaaS) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* 1. RESET E FUNDO PRINCIPAL */
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif !important;
    }
    .stApp {
        background-color: #f8fafc !important; /* Fundo cinza clarinho bem clean */
    }

    /* 2. BARRA LATERAL (Sidebar Premium) */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important; /* Azul marinho muito escuro */
        border-right: 1px solid #1e293b !important;
    }
    
    /* Textos da barra lateral brancos */
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }
    
    /* 3. MENU LATERAL NATIVO (Estilo Rádio Button Escondido) */
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
        display: none !important; /* Esconde a bolinha */
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        padding: 12px 16px !important;
        border-radius: 6px !important;
        margin-bottom: 8px !important;
        transition: all 0.2s ease !important;
        background-color: transparent !important;
        border-left: 3px solid transparent !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: #1e293b !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #1e293b !important;
        border-left: 3px solid #3b82f6 !important; /* Borda azul de ativo */
        color: #ffffff !important;
    }

    /* 4. CARDS DE MÉTRICAS (KPIs do Topo) */
    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 24px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
    }
    [data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-size: 32px !important;
        font-weight: 700 !important;
        margin-top: 8px !important;
    }
    
    /* Tag de Percentagem nos Cards */
    [data-testid="stMetricDelta"] > div {
        background-color: #eff6ff !important;
        color: #2563eb !important;
        border-radius: 6px !important;
        padding: 4px 10px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        margin-top: 8px !important;
    }
    [data-testid="stMetricDelta"] svg { display: none !important; }

    /* 5. TÍTULOS GERAIS */
    h1, h2, h3, h4 {
        color: #0f172a !important;
        font-weight: 700 !important;
    }

    /* 6. CAIXA DE FILTROS (Expander) */
    [data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1) !important;
    }
    
    /* 7. TABELAS (Estilo Limpo) */
    .stDataFrame {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 10px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Ajuste de separador horizontal */
    hr {
        border-color: #e2e8f0 !important;
        margin-top: 2rem !important;
        margin-bottom: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

try:
    # -------------------------------------------------------------
    # 2. CÓDIGO DEFINITIVO INTACTO: LÓGICA DE DADOS
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
    # 3. MENU LATERAL NATIVO (Estilizado pelo CSS)
    # ==========================================
    
    # Cabeçalho da Sidebar (Logo fictícia)
    st.sidebar.markdown("""
        <div style="padding: 10px 0px 30px 0px; display: flex; align-items: center; gap: 12px;">
            <div style="width: 36px; height: 36px; background-color: #3b82f6; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 20px;">C</div>
            <div>
                <div style="color: white; font-size: 18px; font-weight: 700; line-height: 1.2;">ConversionCRM</div>
                <div style="color: #94a3b8; font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">Analytics Pro</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Opções do menu
    menu_opcoes = [
        "📊 Dashboard Geral", 
        "📦 Visão de Produtos", 
        "❌ Churn / Cancelamentos",
        "⚙️ Configurações"
    ]
    
    pagina_selecionada = st.sidebar.radio("Navegação Principal", menu_opcoes, label_visibility="collapsed")
    
    # Rodapé da Sidebar
    st.sidebar.markdown("""
        <div style="position: absolute; bottom: 20px; border-top: 1px solid #1e293b; padding-top: 20px; width: 80%;">
            <div style="color: white; font-size: 14px; font-weight: 500;">Carlos Silva</div>
            <div style="color: #94a3b8; font-size: 12px;">Admin</div>
        </div>
    """, unsafe_allow_html=True)

    # ==========================================
    # 4. PÁGINA 1: DASHBOARD COMERCIAL (OFICIAL)
    # ==========================================
    if pagina_selecionada == "📊 Dashboard Geral":
        
        # Header da Página
        st.markdown("""
            <div style="margin-bottom: 24px;">
                <h1 style="font-size: 28px; color: #0f172a; margin-bottom: 8px;">Dashboard de Conversão</h1>
                <p style="font-size: 15px; color: #64748b; margin: 0;">Acompanhe em tempo real as métricas do funil de vendas e a eficiência da equipe.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # --- CAIXA DE FILTROS ---
        with st.expander("🔍  FILTROS DO RELATÓRIO", expanded=True):
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                data_min, data_max = df['Data de criação'].dropna().min().date(), df['Data de criação'].dropna().max().date()
                periodo = st.date_input("Período de Análise", [data_min, data_max])
            with col_f2:
                tipos = sorted(df["[IS] Tipo de lead"].dropna().unique().tolist())
                filtro_tipo = st.multiselect("Tipo de Lead", tipos, default=tipos)
                origens = sorted(df["[IS] Origem do lead"].dropna().unique().tolist())
                filtro_origem = st.multiselect("Origem do Lead", origens, default=origens)
            with col_f3:
                lista_sdr = sorted(df['Filtro_SDR'].unique().tolist())
                filtro_sdr = st.multiselect("Filtrar por SDR", lista_sdr, default=lista_sdr)
                lista_closer = sorted(df['Filtro_Closer'].unique().tolist())
                filtro_closer = st.multiselect("Filtrar por Closer", lista_closer, default=lista_closer)

        # --- APLICAÇÃO DOS FILTROS (MÁSCARAS) ---
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

        st.write("") # Quebra de linha visual

        # --- CARDS DE PERFORMANCE ---
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Volume de Leads", L)
        m2.metric("Contatos Feitos", C, f"{(C/L*100):.1f}% s/ Lead" if L>0 else "0%")
        m3.metric("Agendamentos", A, f"{(A/C*100):.1f}% s/ Contato" if C>0 else "0%")
        m4.metric("Reuniões Ocorridas", R, f"{(R/A*100):.1f}% s/ Agend." if A>0 else "0%")
        m5.metric("Negócios Fechados", F, f"{(F/R*100):.1f}% s/ Ocorr." if R>0 else "0%")

        st.divider()

        # --- TABELAS 1: ORIGEM E TIPO ---
        def criar_tabela_evento(coluna_nome):
            leads_cat = df_base[mask_L].groupby(coluna_nome).size().reset_index(name='Leads')
            reunioes_cat = df_base[mask_R].groupby(coluna_nome).size().reset_index(name='Reuniões')
            fechados_cat = df_base[mask_F].groupby(coluna_nome).size().reset_index(name='Fechados')
            tabela = leads_cat.merge(reunioes_cat, on=coluna_nome, how='outer').merge(fechados_cat, on=coluna_nome, how='outer').fillna(0)
            tabela['Lead x Reunião (%)'] = tabela.apply(lambda row: f"{(row['Reuniões']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
            tabela['Lead x Fechado (%)'] = tabela.apply(lambda row: f"{(row['Fechados']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
            return tabela[[coluna_nome, 'Leads', 'Lead x Reunião (%)', 'Lead x Fechado (%)']].sort_values(by='Leads', ascending=False)

        col_tbl1, col_tbl2 = st.columns(2)
        with col_tbl1:
            st.markdown("#### Distribuição por Origem")
            st.dataframe(criar_tabela_evento("[IS] Origem do lead"), use_container_width=True, hide_index=True)
        with col_tbl2:
            st.markdown("#### Distribuição por Tipo")
            st.dataframe(criar_tabela_evento("[IS] Tipo de lead"), use_container_width=True, hide_index=True)

        st.divider()

        # --- TABELA 2: FUNIL DO SDR ---
        st.markdown("#### 🏆 Eficiência Operacional (SDR)")
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

        # --- TABELAS 3: EFICIÊNCIA FINAL (SDR VS CLOSER) ---
        st.markdown("#### 🎯 Eficiência de Fechamento")
        col_ef1, col_ef2 = st.columns(2)
        
        with col_ef1:
            st.markdown("<p style='color:#64748b; font-weight: 600; margin-bottom: 5px;'>SDR: IMPACTO NO RESULTADO (Lead x Ocorrido / Fechado)</p>", unsafe_allow_html=True)
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
            st.markdown("<p style='color:#64748b; font-weight: 600; margin-bottom: 5px;'>CLOSER: TAXA DE CONVERSÃO (Ocorrido x Fechado)</p>", unsafe_allow_html=True)
            mask_has_closer = df_base['Filtro_Closer'] != 'Sem Closer'
            cl_ef_r = df_base[mask_R & mask_has_closer].groupby('Filtro_Closer').size().reset_index(name='Ocorridos')
            cl_ef_f = df_base[mask_F & mask_has_closer].groupby('Filtro_Closer').size().reset_index(name='Fechados')
            ef_cl = cl_ef_r.merge(cl_ef_f, on='Filtro_Closer', how='outer').fillna(0)
            ef_cl = ef_cl.rename(columns={'Filtro_Closer': 'Closer Responsável'})
            ef_cl['Ocorrido x Fechado (%)'] = ef_cl.apply(lambda row: f"{(row['Fechados']/row['Ocorridos']*100):.1f}%" if row['Ocorridos'] > 0 else "-", axis=1)
            col_ef_cl = ['Closer Responsável', 'Ocorridos', 'Fechados', 'Ocorrido x Fechado (%)']
            st.dataframe(ef_cl[col_ef_cl].sort_values(by='Ocorridos', ascending=False), use_container_width=True, hide_index=True)


    # ==========================================
    # 5. PÁGINAS FUTURAS (Reservadas e Seguras)
    # ==========================================
    elif pagina_selecionada == "📦 Visão de Produtos":
        st.title("Comercial por Produto")
        st.info("Módulo em desenvolvimento. Em breve, a análise detalhada por SKU/Produto será exibida aqui.")
        
    elif pagina_selecionada == "❌ Churn / Cancelamentos":
        st.title("Gestão de Churn")
        st.info("Módulo em desenvolvimento. Acompanhamento de cancelamentos e motivos de perda.")
        
    elif pagina_selecionada == "⚙️ Configurações":
        st.title("Painel de Controle")
        st.info("Em breve: Gestão de permissões, importação de base e definições globais.")

except Exception as e:
    st.error(f"Erro no processamento do painel: {e}")
