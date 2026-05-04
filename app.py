import streamlit as st
import pandas as pd

# 1. Configuração de Layout e Estilo (Nativo e Seguro)
st.set_page_config(page_title="Análise Comercial", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F0F8FF; }
    
    /* Força a cor AZUL nos filtros selecionados e remove o vermelho padrão */
    span[data-baseweb="tag"] { background-color: #1565C0 !important; color: white !important; border-radius: 4px; }
    
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
    # CÓDIGO DEFINITIVO INTACTO: LENDO A DATA EXATA DE CADA EVENTO
    # -------------------------------------------------------------
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
    # MENU LATERAL
    # ==========================================
    st.sidebar.markdown("## 🧭 Análise")
    
    menu_opcoes = [
        "📊 Dashboard Geral", 
        "📦 Visão de Produtos", 
        "💰 Receita",
        "❌ Perdidos",
        "⚙️ Configurações"
    ]
    
    pagina_selecionada = st.sidebar.radio("Navegação Principal", menu_opcoes, label_visibility="collapsed")
    st.sidebar.divider()

    # ==========================================
    # PÁGINA 1: DASHBOARD COMERCIAL (OFICIAL)
    # ==========================================
    if pagina_selecionada == "📊 Dashboard Geral":
    
        # --- CAIXA DE FILTROS (Vazios por padrão) ---
        with st.expander("🔍 FILTROS DO RELATÓRIO", expanded=False):
            st.markdown("<span style='color: #1565C0; font-size: 13px;'>*Dica: Deixe os campos vazios para ver todas as opções.*</span>", unsafe_allow_html=True)
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                data_min, data_max = df['Data de criação'].dropna().min().date(), df['Data de criação'].dropna().max().date()
                periodo = st.date_input("Período do Evento", [data_min, data_max])
            with col_f2:
                tipos = sorted(df["[IS] Tipo de lead"].dropna().unique().tolist())
                # Default = [] (Lista vazia para não poluir a tela)
                filtro_tipo = st.multiselect("Tipo de Lead", tipos, default=[]) 
                origens = sorted(df["[IS] Origem do lead"].dropna().unique().tolist())
                filtro_origem = st.multiselect("Origem do Lead", origens, default=[])
            with col_f3:
                lista_sdr = sorted(df['Filtro_SDR'].unique().tolist())
                filtro_sdr = st.multiselect("SDR Responsável", lista_sdr, default=[])
                lista_closer = sorted(df['Filtro_Closer'].unique().tolist())
                filtro_closer = st.multiselect("Closer Responsável", lista_closer, default=[])

        # Lógica inteligente: se a lista de filtro estiver vazia, o sistema usa todas as opções disponíveis
        tipo_final = filtro_tipo if filtro_tipo else tipos
        origem_final = filtro_origem if filtro_origem else origens
        sdr_final = filtro_sdr if filtro_sdr else lista_sdr
        closer_final = filtro_closer if filtro_closer else lista_closer

        # Aplicação do Filtro de Atributos
        mask_atributos = (
            (df["[IS] Tipo de lead"].isin(tipo_final)) & 
            (df["[IS] Origem do lead"].isin(origem_final)) &
            (df['Filtro_SDR'].isin(sdr_final)) &
            (df['Filtro_Closer'].isin(closer_final))
        )
        df_base = df[mask_atributos].copy()

        # Aplicação do Filtro TEMPORAL (Lógica de Evento do HubSpot)
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

        # CÁLCULOS DO TOPO
        L, C, A, R, F = mask_L.sum(), mask_C.sum(), mask_A.sum(), mask_R.sum(), mask_F.sum()

        st.title("📊 Dashboard de Conversão")

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Leads", L)
        m2.metric("Contato", C, f"{(C/L*100):.1f}% s/ Lead" if L>0 else "0%")
        m3.metric("Agendado", A, f"{(A/C*100):.1f}% s/ Contato" if C>0 else "0%")
        m4.metric("Ocorrido", R, f"{(R/A*100):.1f}% s/ Agend." if A>0 else "0%")
        m5.metric("Fechado", F, f"{(F/R*100):.1f}% s/ Ocorr." if R>0 else "0%")

        st.divider()

        # TABELAS DE ORIGEM E TIPO
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
            st.subheader("📍 Por Origem")
            st.dataframe(criar_tabela_evento("[IS] Origem do lead"), use_container_width=True, hide_index=True)
        with c_b:
            st.subheader("🏷️ Por Tipo")
            st.dataframe(criar_tabela_evento("[IS] Tipo de lead"), use_container_width=True, hide_index=True)

        st.divider()

        # PERFORMANCE POR SDR
        st.subheader("🏆 Performance por SDR")
        sdr_l = df_base[mask_L].groupby('Filtro_SDR').size().reset_index(name='Leads')
        sdr_c = df_base[mask_C].groupby('Filtro_SDR').size().reset_index(name='Contatos')
        sdr_a = df_base[mask_A].groupby('Filtro_SDR').size().reset_index(name='Agendados')
        sdr_r = df_base[mask_R].groupby('Filtro_SDR').size().reset_index(name='Ocorridos')
        
        df_sdr = sdr_l.merge(sdr_c, on='Filtro_SDR', how='outer').merge(sdr_a, on='Filtro_SDR', how='outer').merge(sdr_r, on='Filtro_SDR', how='outer').fillna(0)
        df_sdr = df_sdr.rename(columns={'Filtro_SDR': 'SDR Responsável'})
        
        df_sdr['Cont/Lead (%)'] = df_sdr.apply(lambda row: f"{(row['Contatos']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
        df_sdr['Agend/Cont (%)'] = df_sdr.apply(lambda row: f"{(row['Agendados']/row['Contatos']*100):.1f}%" if row['Contatos'] > 0 else "-", axis=1)
        df_sdr['Ocorr/Agend (%)'] = df_sdr.apply(lambda row: f"{(row['Ocorridos']/row['Agendados']*100):.1f}%" if row['Agendados'] > 0 else "-", axis=1)
        
        colunas_sdr = ['SDR Responsável', 'Leads', 'Contatos', 'Agendados', 'Ocorridos', 'Cont/Lead (%)', 'Agend/Cont (%)', 'Ocorr/Agend (%)']
        st.dataframe(df_sdr[colunas_sdr].sort_values(by='Leads', ascending=False), use_container_width=True, hide_index=True)

        # EFICIÊNCIA GERAL DE FECHAMENTO (SDR x CLOSER)
        st.divider()
        st.subheader("🎯 Eficiência Geral de Fechamento")
        
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
    elif pagina_selecionada == "📦 Visão de Produtos":
        st.title("📦 Visão de Produtos")
        st.info("Em breve: Análise de desempenho por produto.")
        
    elif pagina_selecionada == "💰 Receita":
        st.title("💰 Receita")
        st.info("Em breve: Acompanhamento de faturamento.")
        
    elif pagina_selecionada == "❌ Perdidos":
        st.title("❌ Perdidos")
        st.info("Em breve: Análise de motivos de perda.")
        
    elif pagina_selecionada == "⚙️ Configurações":
        st.title("⚙️ Configurações")
        st.info("Painel de administração.")

except Exception as e:
    st.error(f"Erro no processamento de dados: {e}")
