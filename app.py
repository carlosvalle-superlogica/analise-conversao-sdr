import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO DE LAYOUT E ESTILO
st.set_page_config(page_title="Sistema de Gestão Comercial", layout="wide")

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
    
    /* CAIXA DE FILTROS (EXPANDER) */
    [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 2px solid #1565C0 !important;
        border-radius: 8px !important;
    }
    
    /* Títulos dos Filtros */
    div[data-testid="stMultiSelect"] label p, 
    div[data-testid="stDateInput"] label p {
        color: #0D47A1 !important;
        font-weight: 800 !important;
        font-size: 15px !important;
    }
    
    /* Tags Selecionadas (Contraste Azul/Branco) */
    span[data-baseweb="tag"] {
        background-color: #1565C0 !important;
    }
    span[data-baseweb="tag"] span {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    span[data-baseweb="tag"] svg { fill: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE ACESSO ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
    st.session_state['perfil'] = None

def login():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.write("")
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
                st.error("Dados de acesso incorretos.")

if not st.session_state['autenticado']:
    login()
else:
    try:
        # 2. CARREGAMENTO E LIMPEZA DE DADOS
        df = pd.read_csv('bd-teste-sistema.csv')
        df.columns = df.columns.str.strip()

        # Conversão de Datas
        df['Data de criação'] = pd.to_datetime(df['Data de criação'], errors='coerce')
        df['Contato Realizado'] = pd.to_datetime(df['Contato Realizado'], errors='coerce')
        df['[IS/SDR] Data do Agendamento'] = pd.to_datetime(df['[IS/SDR] Data do Agendamento'], errors='coerce')
        df['[IS/Closer] Reunião Ocorrida'] = pd.to_datetime(df['[IS/Closer] Reunião Ocorrida'], errors='coerce')
        df['Data de fechamento'] = pd.to_datetime(df['Data de fechamento'], errors='coerce')

        # Tratamento de Equipe
        df['Filtro_SDR'] = df['[IS/SDR] SDR Responsável'].fillna('Sem SDR')
        df['Filtro_Closer'] = df['[IS/SDR] Closer Responsável'].fillna('Sem Closer')

        # --- NAVEGAÇÃO LATERAL ---
        st.sidebar.markdown(f"<h3 style='color: #1565C0;'>Perfil: {st.session_state['perfil'].upper()}</h3>", unsafe_allow_html=True)
        st.sidebar.divider()
        
        menu_opcoes = ["📊 Dashboard Geral", "📦 Visão de Produtos", "💰 Receita", "❌ Perdidos", "⚙️ Configurações"]
        pagina_selecionada = st.sidebar.radio("Navegação Principal", menu_opcoes, label_visibility="collapsed")
        
        st.sidebar.divider()
        if st.sidebar.button("Encerrar Sessão"):
            st.session_state['autenticado'] = False
            st.rerun()

        # --- CONTEÚDO: DASHBOARD GERAL ---
        if pagina_selecionada == "📊 Dashboard Geral":
            st.title("📊 Dashboard Comercial")
            
            # FILTROS NO TOPO (Expander)
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
                    if st.session_state['perfil'] == "master":
                        st.markdown("<div style='height: 72px;'></div>", unsafe_allow_html=True) 
                        lista_sdrs = sorted(df['Filtro_SDR'].unique().tolist())
                        sdrs_sel = st.multiselect("SDR Responsável", lista_sdrs, default=lista_sdrs)
                        
                        lista_closers = sorted(df['Filtro_Closer'].unique().tolist())
                        closers_sel = st.multiselect("Closer Responsável", lista_closers, default=lista_closers)
                    else:
                        sdrs_sel = df['Filtro_SDR'].unique().tolist()
                        closers_sel = df['Filtro_Closer'].unique().tolist()

            # Aplicação dos Filtros
            df_base = df[
                (df["[IS] Origem do lead"].isin(origens_sel)) &
                (df["[IS] Tipo de lead"].isin(tipos_sel)) &
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

            # METRICAS DO PERIODO
            st.subheader("📅 Resultados do Período Selecionado")
            L, C, A, R, F = mL.sum(), mC.sum(), mA.sum(), mR.sum(), mF.sum()
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Leads", f"{L}")
            c2.metric("Contato", f"{C}", f"{(C/L*100):.1f}%" if L>0 else "0%")
            c3.metric("Agendado", f"{A}", f"{(A/C*100):.1f}%" if C>0 else "0%")
            c4.metric("Ocorrido", f"{R}", f"{(R/A*100):.1f}%" if A>0 else "0%")
            c5.metric("Fechado", f"{F}", f"{(F/R*100):.1f}%" if R>0 else "0%")

            st.divider()

            # TABELAS DE APOIO (ORIGEM E TIPO)
            def criar_tabela_evento(coluna_nome, mask_l, mask_r, mask_f):
                l_cat = df_base[mask_l].groupby(coluna_nome).size().reset_index(name='Leads')
                r_cat = df_base[mask_r].groupby(coluna_nome).size().reset_index(name='Reunioes')
                f_cat = df_base[mask_f].groupby(coluna_nome).size().reset_index(name='Fechados')
                t = l_cat.merge(r_cat, on=coluna_nome, how='outer').merge(f_cat, on=coluna_nome, how='outer').fillna(0)
                t['% Conv'] = t.apply(lambda row: f"{(row['Fechados']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "0%", axis=1)
                return t.sort_values(by='Leads', ascending=False)

            ca, cb = st.columns(2)
            with ca: 
                st.subheader("📍 Por Origem")
                st.dataframe(criar_tabela_evento("[IS] Origem do lead", mL, mR, mF), use_container_width=True, hide_index=True)
            with cb: 
                st.subheader("🏷️ Por Tipo")
                st.dataframe(criar_tabela_evento("[IS] Tipo de lead", mL, mR, mF), use_container_width=True, hide_index=True)

            # BLOCO MASTER: ACUMULADO E PERFORMANCE TIME
            if st.session_state['perfil'] == "master":
                st.divider()
                st.subheader(f"📈 Acumulado do Ano ({ano_ref})")
                
                myL = (df_base['Data de criação'].dt.year == ano_ref)
                myC = (df_base['Contato Realizado'].dt.year == ano_ref)
                myA = (df_base['[IS/SDR] Data do Agendamento'].dt.year == ano_ref)
                myR = (df_base['[IS/Closer] Reunião Ocorrida'].dt.year == ano_ref)
                myF = (df_base['Data de fechamento'].dt.year == ano_ref) & (df_base['Etapa do negócio'].isin(['Fechado', 'Pago']))
                
                Ly, Cy, Ay, Ry, Fy = myL.sum(), myC.sum(), myA.sum(), myR.sum(), myF.sum()
                
                cy1, cy2, cy3, cy4, cy5 = st.columns(5)
                cy1.metric("Leads (Ano)", f"{Ly}")
                cy2.metric("Contato (Ano)", f"{Cy}", f"{(Cy/Ly*100):.1f}%" if Ly>0 else "0%")
                cy3.metric("Agendado (Ano)", f"{Ay}", f"{(Ay/Cy*100):.1f}%" if Cy>0 else "0%")
                cy4.metric("Ocorrido (Ano)", f"{Ry}", f"{(Ry/Ay*100):.1f}%" if Ay>0 else "0%")
                cy5.metric("Fechado (Ano)", f"{Fy}", f"{(Fy/Ry*100):.1f}%" if Ry>0 else "0%")

                st.divider()
                
                # PERFORMANCE SDR
                st.subheader("🏆 Performance por SDR (Período)")
                sdr_l = df_base[mL].groupby('Filtro_SDR').size().reset_index(name='Leads')
                sdr_c = df_base[mC].groupby('Filtro_SDR').size().reset_index(name='Contatos')
                sdr_a = df_base[mA].groupby('Filtro_SDR').size().reset_index(name='Agendados')
                sdr_r = df_base[mR].groupby('Filtro_SDR').size().reset_index(name='Ocorridos')
                
                df_sdr = sdr_l.merge(sdr_c, on='Filtro_SDR', how='outer').merge(sdr_a, on='Filtro_SDR', how='outer').merge(sdr_r, on='Filtro_SDR', how='outer').fillna(0)
                df_sdr['Cont/Lead %'] = df_sdr.apply(lambda r: f"{(r['Contatos']/r['Leads']*100):.1f}%" if r['Leads']>0 else "0%", axis=1)
                df_sdr['Agend/Cont %'] = df_sdr.apply(lambda r: f"{(r['Agendados']/r['Contatos']*100):.1f}%" if r['Contatos']>0 else "0%", axis=1)
                df_sdr['Ocorr/Agend %'] = df_sdr.apply(lambda r: f"{(r['Ocorridos']/r['Agendados']*100):.1f}%" if r['Agendados']>0 else "0%", axis=1)
                st.dataframe(df_sdr.sort_values(by='Leads', ascending=False), use_container_width=True, hide_index=True)

                st.write("")
                # EFICIÊNCIA CLOSER
                st.subheader("🎯 Eficiência Closer (Período)")
                cl_r = df_base[mR & (df_base['Filtro_Closer'] != 'Sem Closer')].groupby('Filtro_Closer').size().reset_index(name='Ocorridos')
                cl_f = df_base[mF & (df_base['Filtro_Closer'] != 'Sem Closer')].groupby('Filtro_Closer').size().reset_index(name='Fechados')
                df_cl = cl_r.merge(cl_f, on='Filtro_Closer', how='outer').fillna(0)
                df_cl['% Conv.'] = df_cl.apply(lambda r: f"{(r['Fechados']/r['Ocorridos']*100):.1f}%" if r['Ocorridos']>0 else "0%", axis=1)
                st.dataframe(df_cl.sort_values(by='Ocorridos', ascending=False), use_container_width=True, hide_index=True)

        else:
            st.title(pagina_selecionada)
            st.info("Página em desenvolvimento.")

    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
