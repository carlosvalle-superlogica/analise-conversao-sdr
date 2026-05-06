import streamlit as st
import pandas as pd

# ==============================================================================
# ESTRUTURA BLINDADA - CONFIGURAÇÃO E ESTILO (PADRÃO CORPORATIVO AZUL)
# ==============================================================================
st.set_page_config(page_title="Sistema de Gestão Comercial - Blindado", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F0F8FF; }
    
    /* CARDS DE MÉTRICAS */
    div[data-testid="stMetricValue"] {
        background-color: #FFFFFF; border-radius: 10px; padding: 10px; border: 1px solid #90CAF9; color: #0D47A1;
    }
    [data-testid="stMetricDelta"] > div {
        background-color: #1565C0 !important; color: white !important; border-radius: 5px; padding: 2px 8px; font-weight: bold;
    }
    [data-testid="stMetricDelta"] svg { display: none; }
    h1, h2, h3, h4 { color: #1565C0 !important; font-weight: 700 !important; }
    
    /* CAIXA DE FILTROS */
    [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 2px solid #1565C0 !important;
        border-radius: 8px !important;
    }
    
    /* Títulos dos Filtros e Tags */
    div[data-testid="stMultiSelect"] label p, 
    div[data-testid="stDateInput"] label p {
        color: #0D47A1 !important;
        font-weight: 800 !important;
    }
    span[data-baseweb="tag"] { background-color: #1565C0 !important; }
    span[data-baseweb="tag"] span { color: #FFFFFF !important; font-weight: 600 !important; }
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
        st.title("🔐 Login de Acesso")
        u = st.text_input("Login")
        s = st.text_input("Senha", type="password")
        if st.button("Acessar Sistema"):
            if u == "aquisições" and s == "1987":
                st.session_state.update({'autenticado': True, 'perfil': 'master'})
                st.rerun()
            elif u == "mkt" and s == "123":
                st.session_state.update({'autenticado': True, 'perfil': 'operador'})
                st.rerun()
            else:
                st.error("Dados incorretos.")

if not st.session_state['autenticado']:
    login()
else:
    try:
        # ==============================================================================
        # LÓGICA BLINDADA - MAPEAMENTO E TRATAMENTO DE COLUNAS HUBSPOT
        # ==============================================================================
        df = pd.read_csv('bd-teste-sistema.csv')
        df.columns = df.columns.str.strip()

        # Datas Críticas
        df['Data de criação'] = pd.to_datetime(df['Data de criação'], errors='coerce')
        df['Contato Realizado'] = pd.to_datetime(df['Contato Realizado'], errors='coerce')
        df['[IS/SDR] Data do Agendamento'] = pd.to_datetime(df['[IS/SDR] Data do Agendamento'], errors='coerce')
        df['[IS/Closer] Reunião Ocorrida'] = pd.to_datetime(df['[IS/Closer] Reunião Ocorrida'], errors='coerce')
        df['Data de fechamento'] = pd.to_datetime(df['Data de fechamento'], errors='coerce')

        # Equipe e CS
        df['Filtro_SDR'] = df['[IS/SDR] SDR Responsável'].fillna('Sem SDR')
        df['Filtro_Closer'] = df['[IS/SDR] Closer Responsável'].fillna('Sem Closer')

        # --- BARRA LATERAL ---
        st.sidebar.markdown("<h2 style='color: #1565C0; font-size: 20px;'>Pipeline Principal</h2>", unsafe_allow_html=True)
        pipeline_selecionado = st.sidebar.selectbox("Selecione a Unidade", ["Aquisições", "Canais"], label_visibility="collapsed")
        
        st.sidebar.divider()
        
        # Oculta menus para o Marketing (Blindagem de Perfil)
        if st.session_state['perfil'] == "master":
            menu_opcoes = ["📊 Dashboard Geral", "📦 Visão de Produtos", "💰 Receita", "❌ Perdidos", "⚙️ Configurações"]
        else:
            menu_opcoes = ["📊 Dashboard Geral"]
            
        pagina_selecionada = st.sidebar.radio("Navegação Principal", menu_opcoes, label_visibility="collapsed")
        
        st.sidebar.divider()
        if st.sidebar.button("Encerrar Sessão"):
            st.session_state['autenticado'] = False
            st.rerun()

        # ==============================================================================
        # LÓGICA BLINDADA - FILTROS GLOBAIS (COMPARTILHADOS)
        # ==============================================================================
        with st.expander("🔍 FILTROS DO RELATÓRIO", expanded=True):
            col_esq, col_dir = st.columns(2)
            
            with col_esq:
                data_min, data_max = df['Data de criação'].dropna().min().date(), df['Data de criação'].dropna().max().date()
                periodo = st.date_input("Período do Evento", [data_min, data_max])
                
                lista_tipos = sorted(df["[IS] Tipo de lead"].dropna().unique().tolist())
                tipos_sel = st.multiselect("Tipo de Lead", lista_tipos, default=lista_tipos)
                
                lista_origens = sorted(df["[IS] Origem do lead"].dropna().unique().tolist())
                origens_sel = st.multiselect("Origem do Lead", lista_origens, default=lista_origens)
                
            with col_dir:
                lista_jornada = sorted(df["[IS] Lead com Jornada:"].dropna().unique().tolist())
                jornada_sel = st.multiselect("Jornada do Lead", lista_jornada, default=lista_jornada)
                
                if st.session_state['perfil'] == "master":
                    st.markdown("<div style='height: 72px;'></div>", unsafe_allow_html=True) 
                    lista_sdrs = sorted(df['Filtro_SDR'].unique().tolist())
                    sdrs_sel = st.multiselect("SDR Responsável", lista_sdrs, default=lista_sdrs)
                    
                    lista_closers = sorted(df['Filtro_Closer'].unique().tolist())
                    closers_sel = st.multiselect("Closer Responsável", lista_closers, default=lista_closers)
                else:
                    sdrs_sel = df['Filtro_SDR'].unique().tolist()
                    closers_sel = df['Filtro_Closer'].unique().tolist()

        # ==============================================================================
        # LÓGICA BLINDADA - APLICAÇÃO DOS FILTROS
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

        # ==============================================================================
        # ROTEAMENTO DE PÁGINAS E PIPELINES
        # ==============================================================================
        if pipeline_selecionado == "Aquisições":
            
            # --------------------------------------------------------------------------
            # PÁGINA: DASHBOARD GERAL
            # --------------------------------------------------------------------------
            if pagina_selecionada == "📊 Dashboard Geral":
                st.title("📊 Dashboard Comercial - Aquisições")
                
                # FUNIL DO PERÍODO
                st.subheader("📅 Resultados do Período Selecionado")
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

                # TABELAS DE APOIO (MKT)
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

                # VISÃO MASTER
                if st.session_state['perfil'] == "master":
                    st.divider()
                    
                    # ACUMULADO DO ANO
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
                    
                    # PERFORMANCE SDR - FUNIL COMPLETO
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
                    
                    # TABELAS DE EFICIÊNCIA (SDR, CLOSER, CS)
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
                        st.subheader("🎯 Eficiência CS (Indicações)")
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
            # PÁGINA: VISÃO DE PRODUTOS
            # --------------------------------------------------------------------------
            elif pagina_selecionada == "📦 Visão de Produtos":
                st.title("📦 Visão de Produtos - Aquisições")
                
                total_reunioes = mR.sum()
                total_clientes = mF.sum()
                
                col_prod = '[IS/Closer] Produtos Fechados'
                
                if col_prod in df_base.columns:
                    df_vendas = df_base[mF][col_prod].dropna()
                    
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
                    cp4.metric("Conv. Cliente", f"{conv_cliente:.1f}%")
                    cp5.metric("Conv. Produto", f"{conv_produto:.1f}%")
                    
                    st.divider()

                    st.subheader("📊 Performance por Produto Fechado")
                    st.info(f"A tabela exibe a relevância de cada produto no faturamento total (**% do Mix**) e a eficácia de venda por reunião (**Conversão vs Reuniões**).")
                    
                    contagem_prod['% do Mix (Total Vendido)'] = contagem_prod['Qtd. Vendida'].apply(
                        lambda x: f"{(x / total_produtos * 100):.1f}%" if total_produtos > 0 else "0.0%"
                    )
                    
                    contagem_prod['Conversão (vs Reuniões)'] = contagem_prod['Qtd. Vendida'].apply(
                        lambda x: f"{(x / total_reunioes * 100):.1f}%" if total_reunioes > 0 else "0.0%"
                    )
                    
                    col_tabela, col_vazia = st.columns([7, 3])
                    
                    with col_tabela:
                        st.dataframe(
                            contagem_prod[['Produto', 'Qtd. Vendida', '% do Mix (Total Vendido)', 'Conversão (vs Reuniões)']].sort_values(by='Qtd. Vendida', ascending=False),
                            use_container_width=True,
                            hide_index=True
                        )
                    
                    st.write("")
                    st.divider()
                    
                    # ==============================================================================
                    # MATRIZ DE SINERGIA: SDR X CLOSER (Ajustado para mostrar apenas a % de conversão)
                    # ==============================================================================
                    st.subheader("🤝 Sinergia da Equipe (Ocorrido x Fechado)")
                    st.info("A matriz abaixo cruza a taxa de conversão (% de fechamento sobre as reuniões ocorridas) entre os profissionais.")
                    
                    df_sync_r = df_base[mR].groupby(['Filtro_SDR', 'Filtro_Closer']).size().reset_index(name='Ocorridos')
                    df_sync_f = df_base[mF].groupby(['Filtro_SDR', 'Filtro_Closer']).size().reset_index(name='Fechados')
                    df_sync = pd.merge(df_sync_r, df_sync_f, on=['Filtro_SDR', 'Filtro_Closer'], how='outer').fillna(0)
                    
                    # Função limpa: Retorna APENAS a porcentagem de conversão, ou um traço se não houve reunião.
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
                        st.markdown("<h4 style='color: #0D47A1;'>🔄 Visão: SDR por Closer</h4>", unsafe_allow_html=True)
                        st.dataframe(pivot_sdr_closer, use_container_width=True)
                        
                    with col_mat2:
                        st.markdown("<h4 style='color: #0D47A1;'>🔄 Visão: Closer por SDR</h4>", unsafe_allow_html=True)
                        st.dataframe(pivot_closer_sdr, use_container_width=True)
                    
                    # ESPAÇAMENTO INFERIOR PARA MELHOR SCROLL
                    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
                    
                else:
                    st.warning(f"A coluna '{col_prod}' não foi encontrada na base de dados.")

            # --------------------------------------------------------------------------
            # OUTRAS PÁGINAS
            # --------------------------------------------------------------------------
            else:
                st.title(f"{pagina_selecionada} - Aquisições")
                st.info("Página em desenvolvimento estrutural.")

        # ==============================================================================
        # LÓGICA BLINDADA - CANAIS (PREPARADO PARA NOVO CSV)
        # ==============================================================================
        elif pipeline_selecionado == "Canais":
            st.title("📊 Dashboard Comercial - Canais")
            st.warning("Aguardando importação do arquivo 'bd-canais.csv' para processamento de dados específicos desta unidade.")

    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
