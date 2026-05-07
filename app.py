import streamlit as st
import pandas as pd

# ==============================================================================
# ESTRUTURA BLINDADA - CONFIGURAÇÃO E ESTILO (DESIGN DE SISTEMA PREMIUM)
# ==============================================================================
st.set_page_config(page_title="Sistema de Gestão Comercial", layout="wide")

st.markdown("""
    <style>
    /* Importação de fonte moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #F8FAFC;
    }

    /* CORREÇÃO DA BARRA SUPERIOR */
    header {background-color: transparent !important;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Customização da Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
        box-shadow: 4px 0px 15px rgba(0,0,0,0.03);
    }

    /* TRANSFORMAÇÃO DO MENU LATERAL EM CAIXAS/BOTÕES */
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        margin-bottom: 8px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
        transition: all 0.2s ease-in-out !important;
        cursor: pointer;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: #F8FAFC !important;
        border-color: #CBD5E1 !important;
        transform: translateY(-1px);
        box-shadow: 0 3px 6px rgba(0,0,0,0.05) !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label p {
        margin-left: 0 !important;
        font-weight: 600 !important;
        color: #334155 !important;
        font-size: 0.95rem !important;
    }

    /* Cards de Métricas Estilo SaaS */
    div[data-testid="stMetricValue"] {
        background-color: #FFFFFF; 
        border-radius: 12px; 
        padding: 20px !important; 
        border: 1px solid #E2E8F0; 
        color: #0F172A;
        font-weight: 700;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
    }
    
    [data-testid="stMetricDelta"] > div {
        background-color: #EFF6FF !important; 
        color: #1E40AF !important; 
        border-radius: 6px; 
        padding: 4px 10px; 
        font-weight: 600;
        font-size: 0.85rem;
    }

    /* Estilização dos Expanders (Filtros) */
    .stExpander {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }

    /* Estilização das Tabelas / Dataframes */
    .stDataFrame {
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        overflow: hidden;
    }

    /* Títulos e Subtítulos - Tipografia Refinada */
    h1 { color: #0F172A !important; font-weight: 800 !important; letter-spacing: -0.025em; }
    h2 { color: #1E293B !important; font-weight: 700 !important; letter-spacing: -0.02em; }
    h3 { color: #334155 !important; font-weight: 600 !important; letter-spacing: -0.01em; }
    h4 { color: #475569 !important; font-weight: 600 !important; }

    /* Botões */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    /* Títulos dos Filtros e Tags */
    div[data-testid="stMultiSelect"] label p, 
    div[data-testid="stDateInput"] label p {
        color: #1E40AF !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
    }
    span[data-baseweb="tag"] { background-color: #1E40AF !important; border-radius: 6px !important;}
    span[data-baseweb="tag"] span { color: #FFFFFF !important; font-weight: 500 !important; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# LÓGICA BLINDADA - SISTEMA DE ACESSO E PERMISSÕES
# ==============================================================================
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
    st.session_state['perfil'] = None

def login():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.write("")
        st.markdown("<h1 style='text-align: center;'>🔐 Acesso ao Sistema</h1>", unsafe_allow_html=True)
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")
        if st.button("Entrar no Dashboard", use_container_width=True):
            if u == "aquisições" and s == "1987":
                st.session_state.update({'autenticado': True, 'perfil': 'master'})
                st.rerun()
            elif u == "mkt" and s == "123":
                st.session_state.update({'autenticado': True, 'perfil': 'operador'})
                st.rerun()
            else:
                st.error("Credenciais inválidas.")

if not st.session_state['autenticado']:
    login()
else:
    try:
        # ==============================================================================
        # LÓGICA BLINDADA - MAPEAMENTO E TRATAMENTO DE COLUNAS HUBSPOT
        # ==============================================================================
        df = pd.read_csv('bd-teste-sistema.csv')
        df.columns = df.columns.str.strip()

        colunas_data = ['Data de criação', 'Contato Realizado', '[IS/SDR] Data do Agendamento', 
                        '[IS/Closer] Reunião Ocorrida', 'Data de fechamento']
        for col in colunas_data:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        df['Filtro_SDR'] = df['[IS/SDR] SDR Responsável'].fillna('Sem SDR')
        df['Filtro_Closer'] = df['[IS/SDR] Closer Responsável'].fillna('Sem Closer')

        # --- BARRA LATERAL (SIDEBAR) ---
        st.sidebar.markdown("<h2 style='font-size: 1.1rem; margin-bottom: 5px;'>Pipeline</h2>", unsafe_allow_html=True)
        pipeline_selecionado = st.sidebar.selectbox("Pipeline", ["Aquisições", "Canais"], label_visibility="collapsed")
        
        st.sidebar.markdown("<br><h2 style='font-size: 1.1rem; margin-bottom: 5px;'>Módulos</h2>", unsafe_allow_html=True)
        
        # Oculta menus para o Marketing
        if st.session_state['perfil'] == "master":
            menu_opcoes = ["📊 Dashboard Geral", "📦 Produtos / Closer's / VC", "💰 Receita", "❌ Perdidos", "⚙️ Configurações"]
        else:
            menu_opcoes = ["📊 Dashboard Geral"]
            
        pagina_selecionada = st.sidebar.radio("Navegação", menu_opcoes, label_visibility="collapsed")
        
        st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
        st.sidebar.divider()
        if st.sidebar.button("🚪 Sair do Sistema", use_container_width=True):
            st.session_state['autenticado'] = False
            st.rerun()

        # ==============================================================================
        # LÓGICA BLINDADA - FILTROS GLOBAIS
        # ==============================================================================
        with st.expander("🔍 Parâmetros de Filtro", expanded=True):
            col_esq, col_dir = st.columns(2)
            
            with col_esq:
                data_min, data_max = df['Data de criação'].dropna().min().date(), df['Data de criação'].dropna().max().date()
                periodo = st.date_input("Período de Análise", [data_min, data_max])
                
                lista_tipos = sorted(df["[IS] Tipo de lead"].dropna().unique().tolist())
                tipos_sel = st.multiselect("Tipo de Lead", lista_tipos, default=lista_tipos)
                
                lista_origens = sorted(df["[IS] Origem do lead"].dropna().unique().tolist())
                origens_sel = st.multiselect("Origem do Lead", lista_origens, default=lista_origens)
                
            with col_dir:
                lista_jornada = sorted(df["[IS] Lead com Jornada:"].dropna().unique().tolist())
                jornada_sel = st.multiselect("Jornada do Lead", lista_jornada, default=lista_jornada)
                
                if st.session_state['perfil'] == "master":
                    st.markdown("<div style='height: 70px;'></div>", unsafe_allow_html=True) 
                    lista_sdrs = sorted(df['Filtro_SDR'].unique().tolist())
                    sdrs_sel = st.multiselect("SDR Responsável", lista_sdrs, default=lista_sdrs)
                    
                    lista_closers = sorted(df['Filtro_Closer'].unique().tolist())
                    closers_sel = st.multiselect("Closer Responsável", lista_closers, default=lista_closers)
                else:
                    sdrs_sel = df['Filtro_SDR'].unique().tolist()
                    closers_sel = df['Filtro_Closer'].unique().tolist()

        # ==============================================================================
        # LÓGICA BLINDADA - APLICAÇÃO DOS FILTROS E MÁSCARAS MATEMÁTICAS
        # ==============================================================================
        df_base = df[
            (df["[IS] Origem do lead"].isin(origens_sel)) &
            (df["[IS] Tipo de lead"].isin(tipos_sel)) &
            (df["[IS] Lead com Jornada:"].isin(jornada_sel)) &
            (df['Filtro_SDR'].isin(sdrs_sel)) &
            (df['Filtro_Closer'].isin(closers_sel))
        ].copy()

        if len(periodo) == 2:
            p_start, p_end = periodo[0], periodo[1]
            mL = (df_base['Data de criação'].dt.date >= p_start) & (df_base['Data de criação'].dt.date <= p_end)
            mC = (df_base['Contato Realizado'].dt.date >= p_start) & (df_base['Contato Realizado'].dt.date <= p_end)
            mA = (df_base['[IS/SDR] Data do Agendamento'].dt.date >= p_start) & (df_base['[IS/SDR] Data do Agendamento'].dt.date <= p_end)
            mR = (df_base['[IS/Closer] Reunião Ocorrida'].dt.date >= p_start) & (df_base['[IS/Closer] Reunião Ocorrida'].dt.date <= p_end)
            mF = (df_base['Data de fechamento'].dt.date >= p_start) & (df_base['Data de fechamento'].dt.date <= p_end) & (df_base['Etapa do negócio'].isin(['Fechado', 'Pago']))
            ano_ref = p_end.year
        else:
            # Proteção contra erros se o utilizador não selecionar a segunda data no calendário
            p_end = df['Data de criação'].max()
            ano_ref = p_end.year if pd.notna(p_end) else 2026
            mL = pd.Series([False]*len(df_base), index=df_base.index)
            mC = pd.Series([False]*len(df_base), index=df_base.index)
            mA = pd.Series([False]*len(df_base), index=df_base.index)
            mR = pd.Series([False]*len(df_base), index=df_base.index)
            mF = pd.Series([False]*len(df_base), index=df_base.index)

        # ==============================================================================
        # ROTEAMENTO DE PÁGINAS E PIPELINES
        # ==============================================================================
        if pipeline_selecionado == "Aquisições":
            
            # --------------------------------------------------------------------------
            # PÁGINA: DASHBOARD GERAL
            # --------------------------------------------------------------------------
            if pagina_selecionada == "📊 Dashboard Geral":
                st.markdown("### 📈 Performance de Funil: Aquisições")
                
                L = mL.sum()
                C = mC.sum()
                A = mA.sum()
                R = mR.sum()
                F = mF.sum()
                
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Leads", f"{L}")
                c2.metric("Contato", f"{C}", f"{(C/L*100):.1f}%" if L>0 else "0%")
                c3.metric("Agendado", f"{A}", f"{(A/C*100):.1f}%" if C>0 else "0%")
                c4.metric("Ocorrido", f"{R}", f"{(R/A*100):.1f}%" if A>0 else "0%")
                c5.metric("Fechado", f"{F}", f"{(F/R*100):.1f}%" if R>0 else "0%")

                st.divider()

                def criar_tabela_mkt(coluna_nome):
                    l_cat = df_base[mL].groupby(coluna_nome).size().reset_index(name='Leads')
                    r_cat = df_base[mR].groupby(coluna_nome).size().reset_index(name='Ocorridos')
                    f_cat = df_base[mF].groupby(coluna_nome).size().reset_index(name='Fechados')
                    
                    t = l_cat.merge(r_cat, on=coluna_nome, how='outer').merge(f_cat, on=coluna_nome, how='outer').fillna(0)
                    t['L x Ocorrido (%)'] = t.apply(lambda row: f"{(row['Ocorridos']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "0%", axis=1)
                    t['L x Fechado (%)'] = t.apply(lambda row: f"{(row['Fechados']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "0%", axis=1)
                    return t.sort_values(by='Leads', ascending=False)

                v1, v2, v3 = st.columns(3)
                with v1: 
                    st.subheader("📍 Por Origem")
                    st.dataframe(criar_tabela_mkt("[IS] Origem do lead"), use_container_width=True, hide_index=True)
                with v2: 
                    st.subheader("🏷️ Por Tipo")
                    st.dataframe(criar_tabela_mkt("[IS] Tipo de lead"), use_container_width=True, hide_index=True)
                with v3: 
                    st.subheader("🚀 Por Jornada")
                    st.dataframe(criar_tabela_mkt("[IS] Lead com Jornada:"), use_container_width=True, hide_index=True)

                if st.session_state['perfil'] == "master":
                    st.divider()
                    
                    st.subheader(f"📈 Acumulado do Ano ({ano_ref})")
                    myL = (df_base['Data de criação'].dt.year == ano_ref).sum()
                    myC = (df_base['Contato Realizado'].dt.year == ano_ref).sum()
                    myA = (df_base['[IS/SDR] Data do Agendamento'].dt.year == ano_ref).sum()
                    myR = (df_base['[IS/Closer] Reunião Ocorrida'].dt.year == ano_ref).sum()
                    myF = ((df_base['Data de fechamento'].dt.year == ano_ref) & (df_base['Etapa do negócio'].isin(['Fechado', 'Pago']))).sum()
                    
                    cy1, cy2, cy3, cy4, cy5 = st.columns(5)
                    cy1.metric("Leads (Ano)", f"{myL}")
                    cy2.metric("Contato (Ano)", f"{myC}", f"{(myC/myL*100):.1f}%" if myL>0 else "0%")
                    cy3.metric("Agendado (Ano)", f"{myA}", f"{(myA/myC*100):.1f}%" if myC>0 else "0%")
                    cy4.metric("Ocorrido (Ano)", f"{myR}", f"{(myR/myA*100):.1f}%" if myA>0 else "0%")
                    cy5.metric("Fechado (Ano)", f"{myF}", f"{(myF/myR*100):.1f}%" if myR>0 else "0%")

                    st.divider()
                    
                    st.subheader("🏆 Performance SDR: Funil de Conversão (Período)")
                    s_l = df_base[mL].groupby('Filtro_SDR').size().reset_index(name='Leads')
                    s_c = df_base[mC].groupby('Filtro_SDR').size().reset_index(name='Contatos')
                    s_a = df_base[mA].groupby('Filtro_SDR').size().reset_index(name='Agendados')
                    s_r = df_base[mR].groupby('Filtro_SDR').size().reset_index(name='Ocorridos')
                    s_f = df_base[mF].groupby('Filtro_SDR').size().reset_index(name='Fechados')
                    
                    t_sdr_funil = s_l.merge(s_c, on='Filtro_SDR', how='outer') \
                                     .merge(s_a, on='Filtro_SDR', how='outer') \
                                     .merge(s_r, on='Filtro_SDR', how='outer') \
                                     .merge(s_f, on='Filtro_SDR', how='outer').fillna(0)
                    
                    t_sdr_funil['C/L (%)'] = t_sdr_funil.apply(lambda r: f"{(r['Contatos']/r['Leads']*100):.1f}%" if r['Leads']>0 else "0%", axis=1)
                    t_sdr_funil['A/C (%)'] = t_sdr_funil.apply(lambda r: f"{(r['Agendados']/r['Contatos']*100):.1f}%" if r['Contatos']>0 else "0%", axis=1)
                    t_sdr_funil['O/A (%)'] = t_sdr_funil.apply(lambda r: f"{(r['Ocorridos']/r['Agendados']*100):.1f}%" if r['Agendados']>0 else "0%", axis=1)
                    t_sdr_funil['F/O (%)'] = t_sdr_funil.apply(lambda r: f"{(r['Fechados']/r['Ocorridos']*100):.1f}%" if r['Ocorridos']>0 else "0%", axis=1)
                    
                    st.dataframe(t_sdr_funil.rename(columns={'Filtro_SDR': 'SDR Responsável'}).sort_values(by='Leads', ascending=False), use_container_width=True, hide_index=True)

                    st.write("")
                    
                    col_ef1, col_ef2, col_ef3 = st.columns(3)
                    
                    with col_ef1:
                        st.subheader("🎯 Eficiência SDR")
                        t_sdr_q = t_sdr_funil[['Filtro_SDR', 'Leads', 'Ocorridos', 'Fechados']].copy()
                        t_sdr_q['L x Ocorrido %'] = t_sdr_q.apply(lambda r: f"{(r['Ocorridos']/r['Leads']*100):.1f}%" if r['Leads']>0 else "0%", axis=1)
                        t_sdr_q['L x Fechado %'] = t_sdr_q.apply(lambda r: f"{(r['Fechados']/r['Leads']*100):.1f}%" if r['Leads']>0 else "0%", axis=1)
                        st.dataframe(t_sdr_q.rename(columns={'Filtro_SDR': 'SDR Responsável'}).sort_values(by='Leads', ascending=False), use_container_width=True, hide_index=True)

                    with col_ef2:
                        st.subheader("🎯 Eficiência Closer")
                        cl_r = df_base[mR & (df_base['Filtro_Closer'] != 'Sem Closer')].groupby('Filtro_Closer').size().reset_index(name='Ocorridos')
                        cl_f = df_base[mF & (df_base['Filtro_Closer'] != 'Sem Closer')].groupby('Filtro_Closer').size().reset_index(name='Fechados')
                        t_cl = cl_r.merge(cl_f, on='Filtro_Closer', how='outer').fillna(0)
                        t_cl['Ocorrido x Fechado %'] = t_cl.apply(lambda r: f"{(r['Fechados']/r['Ocorridos']*100):.1f}%" if r['Ocorridos']>0 else "0%", axis=1)
                        st.dataframe(t_cl.rename(columns={'Filtro_Closer': 'Closer Responsável'}).sort_values(by='Ocorridos', ascending=False), use_container_width=True, hide_index=True)

                    with col_ef3:
                        st.subheader("🎯 Eficiência CS")
                        col_cs = '[CS] CS que indicou'
                        if col_cs in df_base.columns:
                            mask_cs = df_base[col_cs].notna() & (df_base[col_cs] != "")
                            cs_l = df_base[mL & mask_cs].groupby(col_cs).size().reset_index(name='Leads')
                            cs_r = df_base[mR & mask_cs].groupby(col_cs).size().reset_index(name='Ocorridos')
                            cs_f = df_base[mF & mask_cs].groupby(col_cs).size().reset_index(name='Fechados')
                            
                            t_cs = cs_l.merge(cs_r, on=col_cs, how='outer').merge(cs_f, on=col_cs, how='outer').fillna(0)
                            t_cs['L x Ocorrido %'] = t_cs.apply(lambda r: f"{(r['Ocorridos']/r['Leads']*100):.1f}%" if r['Leads']>0 else "0%", axis=1)
                            t_cs['L x Fechado %'] = t_cs.apply(lambda r: f"{(r['Fechados']/r['Leads']*100):.1f}%" if r['Leads']>0 else "0%", axis=1)
                            
                            st.dataframe(t_cs.rename(columns={col_cs: 'CS Responsável'}).sort_values(by='Leads', ascending=False), use_container_width=True, hide_index=True)
                        else:
                            st.warning(f"Coluna '{col_cs}' não encontrada.")

            # --------------------------------------------------------------------------
            # PÁGINA: PRODUTOS / CLOSER'S / VC
            # --------------------------------------------------------------------------
            elif pagina_selecionada == "📦 Produtos / Closer's / VC":
                st.markdown("### 📦 Produtos / Closer's / VC")
                
                total_reunioes = mR.sum()
                total_clientes = mF.sum()
                
                col_prod = '[IS/Closer] Produtos Fechados'
                
                if col_prod in df_base.columns:
                    # Garantir que dados que possam ser números se tornem texto para não quebrar o .split
                    df_vendas = df_base[mF][col_prod].dropna().astype(str)
                    
                    produtos_separados = df_vendas.str.split(';').explode().str.strip()
                    produtos_separados = produtos_separados[produtos_separados != ""]
                    
                    contagem_prod = produtos_separados.value_counts().reset_index()
                    contagem_prod.columns = ['Produto', 'Qtd. Vendida']
                    total_produtos = contagem_prod['Qtd. Vendida'].sum()
                    
                    conv_cliente = (total_clientes / total_reunioes * 100) if total_reunioes > 0 else 0.0
                    conv_produto = (total_produtos / total_reunioes * 100) if total_reunioes > 0 else 0.0
                    
                    st.subheader("🎯 Resumo de Conversão (Período)")
                    cp1, cp2, cp3, cp4, cp5 = st.columns(5)
                    cp1.metric("Reuniões Ocorridas", f"{total_reunioes}")
                    cp2.metric("Clientes Fechados", f"{total_clientes}")
                    cp3.metric("Produtos Vendidos", f"{total_produtos}")
                    
                    # AJUSTE DE NOMENCLATURA DOS CARDS PARA MÁXIMA CLAREZA
                    cp4.metric("Conv. Clientes / Reuniões", f"{conv_cliente:.1f}%")
                    cp5.metric("Conv. Produtos / Reuniões", f"{conv_produto:.1f}%")
                    
                    st.divider()

                    st.subheader("📊 Performance por Produto Fechado")
                    
                    contagem_prod['% do Mix (Total Vendido)'] = contagem_prod['Qtd. Vendida'].apply(
                        lambda x: f"{(x / total_produtos * 100):.1f}%" if total_produtos > 0 else "0.0%"
                    )
                    
                    contagem_prod['% Produto / Reunião'] = contagem_prod['Qtd. Vendida'].apply(
                        lambda x: f"{(x / total_reunioes * 100):.1f}%" if total_reunioes > 0 else "0.0%"
                    )
                    
                    col_tabela, col_vazia = st.columns([7, 3])
                    
                    with col_tabela:
                        st.dataframe(
                            contagem_prod[['Produto', 'Qtd. Vendida', '% do Mix (Total Vendido)', '% Produto / Reunião']].sort_values(by='Qtd. Vendida', ascending=False),
                            use_container_width=True,
                            hide_index=True
                        )
                    
                    st.write("")
                    st.divider()
                    
                    st.subheader("🤝 Sinergia da Equipe (Conversão Ocorrido x Fechado)")
                    
                    df_sync_r = df_base[mR].groupby(['Filtro_SDR', 'Filtro_Closer']).size().reset_index(name='Ocorridos')
                    df_sync_f = df_base[mF].groupby(['Filtro_SDR', 'Filtro_Closer']).size().reset_index(name='Fechados')
                    df_sync = pd.merge(df_sync_r, df_sync_f, on=['Filtro_SDR', 'Filtro_Closer'], how='outer').fillna(0)
                    
                    def format_sync_percent_only(row):
                        occ = int(row['Ocorridos'])
                        fec = int(row['Fechados'])
                        if occ == 0:
                            return "-"
                        else:
                            conv = (fec / occ) * 100
                            return f"{conv:.1f}%"
                            
                    df_sync['Conversao_Limpa'] = df_sync.apply(format_sync_percent_only, axis=1)
                    
                    pivot_sdr_closer = df_sync.pivot(index='Filtro_SDR', columns='Filtro_Closer', values='Conversao_Limpa').fillna('-')
                    pivot_closer_sdr = df_sync.pivot(index='Filtro_Closer', columns='Filtro_SDR', values='Conversao_Limpa').fillna('-')
                    
                    col_mat1, col_mat2 = st.columns(2)
                    
                    with col_mat1:
                        st.markdown("<h4 style='color: #334155;'>🔄 Visão: SDR por Closer</h4>", unsafe_allow_html=True)
                        st.dataframe(pivot_sdr_closer, use_container_width=True)
                        
                    with col_mat2:
                        st.markdown("<h4 style='color: #334155;'>🔄 Visão: Closer por SDR</h4>", unsafe_allow_html=True)
                        st.dataframe(pivot_closer_sdr, use_container_width=True)
                    
                    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
                    
                else:
                    st.warning(f"A coluna '{col_prod}' não foi encontrada na base de dados.")

            # --------------------------------------------------------------------------
            # OUTRAS PÁGINAS
            # --------------------------------------------------------------------------
            else:
                st.markdown(f"### {pagina_selecionada} - Aquisições")
                st.info("Página em desenvolvimento estrutural.")

        # ==============================================================================
        # LÓGICA BLINDADA - CANAIS
        # ==============================================================================
        elif pipeline_selecionado == "Canais":
            st.markdown("### 📈 Performance de Funil: Canais")
            st.warning("Aguardando importação do ficheiro 'bd-canais.csv' para processamento de dados específicos desta unidade.")

    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
