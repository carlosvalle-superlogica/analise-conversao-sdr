import streamlit as st
import pandas as pd

# 1. Configuração de Layout e Estilo (Agora mais premium)
st.set_page_config(page_title="Hub de Análise Comercial", layout="wide", initial_sidebar_state="expanded")

# --- CSS PERSONALIZADO (Estilo Premium baseado nos seus exemplos) ---
st.markdown("""
    <style>
    /* Fundo geral e fonte */
    .stApp { 
        background-color: #F8FAFC; 
        font-family: 'Inter', sans-serif;
    }
    
    /* Personalização da Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Títulos principais */
    h1, h2, h3 { 
        color: #1E293B !important; 
        font-weight: 700;
    }
    
    /* Cards das Métricas Principais (Topo) */
    div[data-testid="stMetricValue"] {
        background-color: #FFFFFF; 
        border-radius: 8px; 
        padding: 15px; 
        border: 1px solid #E2E8F0; 
        color: #0F172A;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        font-size: 28px !important;
        font-weight: bold;
    }
    
    /* Tags de percentagem (Deltas) */
    [data-testid="stMetricDelta"] > div {
        background-color: #DBEAFE !important; 
        color: #1D4ED8 !important; 
        border-radius: 4px; 
        padding: 4px 8px; 
        font-weight: 600;
        font-size: 14px;
        margin-top: 5px;
    }
    [data-testid="stMetricDelta"] svg { display: none; }
    
    /* Tabelas */
    .stDataFrame {
        background-color: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        padding: 10px;
    }
    
    /* Estilo para os separadores horizontais */
    hr {
        border-color: #E2E8F0;
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

try:
    # --- CÓDIGO DEFINITIVO INTACTO: LENDO A DATA EXATA DE CADA EVENTO ---
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
    # ----------------------------------------------------------------------

    # ==========================================
    # MENU LATERAL - NAVEGAÇÃO PRINCIPAL
    # ==========================================
    st.sidebar.markdown("### 🧭 Menu Principal")
    
    # Criamos as opções de navegação inspiradas nas suas imagens
    menu_opcoes = [
        "📊 Dashboard Comercial", 
        "📦 Comercial por Produto", 
        "❌ Cancelamentos / Churn",
        "⚙️ Configurações"
    ]
    
    pagina_selecionada = st.sidebar.radio("Selecione a secção:", menu_opcoes)
    
    st.sidebar.divider() # Linha de divisão para os filtros

    # ==========================================
    # PÁGINA 1: DASHBOARD COMERCIAL (O NOSSO CÓDIGO ATUAL)
    # ==========================================
    if pagina_selecionada == "📊 Dashboard Comercial":
        
        # --- FILTROS (Apenas visíveis nesta página) ---
        st.sidebar.markdown("### 🔎 Filtros")
        data_min, data_max = df['Data de criação'].dropna().min().date(), df['Data de criação'].dropna().max().date()
        periodo = st.sidebar.date_input("Período do Evento", [data_min, data_max])
        
        tipos = sorted(df["[IS] Tipo de lead"].dropna().unique().tolist())
        filtro_tipo = st.sidebar.multiselect("Tipo de Lead", tipos, default=tipos)
        
        origens = sorted(df["[IS] Origem do lead"].dropna().unique().tolist())
        filtro_origem = st.sidebar.multiselect("Origem do Lead", origens, default=origens)
    
        lista_sdr = sorted(df['Filtro_SDR'].unique().tolist())
        filtro_sdr = st.sidebar.multiselect("SDR Responsável", lista_sdr, default=lista_sdr)
    
        lista_closer = sorted(df['Filtro_Closer'].unique().tolist())
        filtro_closer = st.sidebar.multiselect("Closer Responsável", lista_closer, default=lista_closer)
    
        # --- APLICAÇÃO DOS FILTROS (Lógica intacta) ---
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
    
        # --- RENDERIZAÇÃO DO CONTEÚDO ---
        L, C, A, R, F = mask_L.sum(), mask_C.sum(), mask_A.sum(), mask_R.sum(), mask_F.sum()
    
        st.title("Visão Geral - Comercial")
        st.markdown("Acompanhe o funil de conversão e a performance da equipa em tempo real.")
        st.write("") # Espaço extra
    
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total de Leads", L)
        m2.metric("Contactos", C, f"{(C/L*100):.1f}% s/ Lead" if L>0 else "0%")
        m3.metric("Agendamentos", A, f"{(A/C*100):.1f}% s/ Contato" if C>0 else "0%")
        m4.metric("Reuniões", R, f"{(R/A*100):.1f}% s/ Agend." if A>0 else "0%")
        m5.metric("Fechos", F, f"{(F/R*100):.1f}% s/ Ocorr." if R>0 else "0%")
    
        st.divider()
    
        # TABELAS DE ORIGEM E TIPO
        def criar_tabela_evento(coluna_nome):
            leads_cat = df_base[mask_L].groupby(coluna_nome).size().reset_index(name='Leads')
            reunioes_cat = df_base[mask_R].groupby(coluna_nome).size().reset_index(name='Reuniões')
            fechados_cat = df_base[mask_F].groupby(coluna_nome).size().reset_index(name='Fechos')
            tabela = leads_cat.merge(reunioes_cat, on=coluna_nome, how='outer').merge(fechados_cat, on=coluna_nome, how='outer').fillna(0)
            tabela['Lead x Reunião (%)'] = tabela.apply(lambda row: f"{(row['Reuniões']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
            tabela['Lead x Fechado (%)'] = tabela.apply(lambda row: f"{(row['Fechos']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
            return tabela[[coluna_nome, 'Leads', 'Lead x Reunião (%)', 'Lead x Fechado (%)']].sort_values(by='Leads', ascending=False)
    
        c_a, c_b = st.columns(2)
        with c_a:
            st.markdown("#### 📍 Volume por Origem")
            st.dataframe(criar_tabela_evento("[IS] Origem do lead"), use_container_width=True, hide_index=True)
        with c_b:
            st.markdown("#### 🏷️ Volume por Tipo")
            st.dataframe(criar_tabela_evento("[IS] Tipo de lead"), use_container_width=True, hide_index=True)
    
        st.divider()
    
        # PERFORMANCE POR SDR
        st.markdown("#### 🏆 Desempenho por SDR")
        sdr_l = df_base[mask_L].groupby('Filtro_SDR').size().reset_index(name='Leads')
        sdr_c = df_base[mask_C].groupby('Filtro_SDR').size().reset_index(name='Contatos')
        sdr_a = df_base[mask_A].groupby('Filtro_SDR').size().reset_index(name='Agendados')
        sdr_r = df_base[mask_R].groupby('Filtro_SDR').size().reset_index(name='Reuniões')
        df_sdr = sdr_l.merge(sdr_c, on='Filtro_SDR', how='outer').merge(sdr_a, on='Filtro_SDR', how='outer').merge(sdr_r, on='Filtro_SDR', how='outer').fillna(0)
        df_sdr = df_sdr.rename(columns={'Filtro_SDR': 'SDR Responsável'})
        df_sdr['Cont/Lead (%)'] = df_sdr.apply(lambda row: f"{(row['Contatos']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
        df_sdr['Agend/Cont (%)'] = df_sdr.apply(lambda row: f"{(row['Agendados']/row['Contatos']*100):.1f}%" if row['Contatos'] > 0 else "-", axis=1)
        df_sdr['Reun./Agend (%)'] = df_sdr.apply(lambda row: f"{(row['Reuniões']/row['Agendados']*100):.1f}%" if row['Agendados'] > 0 else "-", axis=1)
        colunas_sdr = ['SDR Responsável', 'Leads', 'Contatos', 'Agendados', 'Reuniões', 'Cont/Lead (%)', 'Agend/Cont (%)', 'Reun./Agend (%)']
        st.dataframe(df_sdr[colunas_sdr].sort_values(by='Leads', ascending=False), use_container_width=True, hide_index=True)
    
        st.divider()
    
        # EFICIÊNCIA GERAL (SDR x CLOSER)
        st.markdown("#### 🎯 Eficiência de Fecho")
        
        col_ef1, col_ef2 = st.columns(2)
        
        with col_ef1:
            st.markdown("**SDR: Impacto Final** *(Lead x Ocorrido / Fechado)*")
            sdr_ef_l = df_base[mask_L].groupby('Filtro_SDR').size().reset_index(name='Leads')
            sdr_ef_r = df_base[mask_R].groupby('Filtro_SDR').size().reset_index(name='Reuniões')
            sdr_ef_f = df_base[mask_F].groupby('Filtro_SDR').size().reset_index(name='Fechos')
            ef_sdr = sdr_ef_l.merge(sdr_ef_r, on='Filtro_SDR', how='outer').merge(sdr_ef_f, on='Filtro_SDR', how='outer').fillna(0)
            ef_sdr = ef_sdr.rename(columns={'Filtro_SDR': 'SDR Responsável'})
            ef_sdr['Lead x Reunião (%)'] = ef_sdr.apply(lambda row: f"{(row['Reuniões']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
            ef_sdr['Lead x Fechado (%)'] = ef_sdr.apply(lambda row: f"{(row['Fechos']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
            col_ef_sdr = ['SDR Responsável', 'Leads', 'Reuniões', 'Fechos', 'Lead x Reunião (%)', 'Lead x Fechado (%)']
            st.dataframe(ef_sdr[col_ef_sdr].sort_values(by='Leads', ascending=False), use_container_width=True, hide_index=True)
    
        with col_ef2:
            st.markdown("**Closer: Taxa de Fecho** *(Ocorrido x Fechado)*")
            mask_has_closer = df_base['Filtro_Closer'] != 'Sem Closer'
            cl_ef_r = df_base[mask_R & mask_has_closer].groupby('Filtro_Closer').size().reset_index(name='Reuniões')
            cl_ef_f = df_base[mask_F & mask_has_closer].groupby('Filtro_Closer').size().reset_index(name='Fechos')
            ef_cl = cl_ef_r.merge(cl_ef_f, on='Filtro_Closer', how='outer').fillna(0)
            ef_cl = ef_cl.rename(columns={'Filtro_Closer': 'Closer Responsável'})
            ef_cl['Taxa de Fecho (%)'] = ef_cl.apply(lambda row: f"{(row['Fechos']/row['Reuniões']*100):.1f}%" if row['Reuniões'] > 0 else "-", axis=1)
            col_ef_cl = ['Closer Responsável', 'Reuniões', 'Fechos', 'Taxa de Fecho (%)']
            st.dataframe(ef_cl[col_ef_cl].sort_values(by='Reuniões', ascending=False), use_container_width=True, hide_index=True)


    # ==========================================
    # PÁGINAS FUTURAS (Espaços reservados)
    # ==========================================
    elif pagina_selecionada == "📦 Comercial por Produto":
        st.title("Análise por Produto")
        st.info("Módulo em desenvolvimento. Aqui analisaremos o desempenho individual de cada produto fechado.")
        
    elif pagina_selecionada == "❌ Cancelamentos / Churn":
        st.title("Gestão de Cancelamentos")
        st.info("Módulo em desenvolvimento. Espaço dedicado à análise de churn e motivos de perda.")
        
    elif pagina_selecionada == "⚙️ Configurações":
        st.title("Configurações do Sistema")
        st.info("Painel de administração e gestão de utilizadores.")

except Exception as e:
    st.error(f"Ocorreu um erro no processamento: {e}")
