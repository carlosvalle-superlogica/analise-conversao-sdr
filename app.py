import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO DE LAYOUT E ESTILO (Contraste Máximo Azul/Branco)
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
                st.error("Usuário ou senha incorretos.")

if not st.session_state['autenticado']:
    login()
else:
    try:
        # 2. CARREGAMENTO E TRATAMENTO DE DADOS
        df = pd.read_csv('bd-teste-sistema.csv')
        df.columns = df.columns.str.strip()

        df['Data de criação'] = pd.to_datetime(df['Data de criação'], errors='coerce')
        df['Contato Realizado'] = pd.to_datetime(df['Contato Realizado'], errors='coerce')
        df['[IS/SDR] Data do Agendamento'] = pd.to_datetime(df['[IS/SDR] Data do Agendamento'], errors='coerce')
        df['[IS/Closer] Reunião Ocorrida'] = pd.to_datetime(df['[IS/Closer] Reunião Ocorrida'], errors='coerce')
        df['Data de fechamento'] = pd.to_datetime(df['Data de fechamento'], errors='coerce')

        df['Filtro_SDR'] = df['[IS/SDR] SDR Responsável'].fillna('Sem SDR')
        df['Filtro_Closer'] = df['[IS/SDR] Closer Responsável'].fillna('Sem Closer')

        # --- MENU LATERAL ---
        st.sidebar.markdown(f"<h3 style='color: #1565C0;'>Perfil: {st.session_state['perfil'].upper()}</h3>", unsafe_allow_html=True)
        menu_opcoes = ["📊 Dashboard Geral", "📦 Visão de Produtos", "💰 Receita", "❌ Perdidos", "⚙️ Configurações"]
        pagina_selecionada = st.sidebar.radio("Navegação Principal", menu_opcoes, label_visibility="collapsed")
        
        st.sidebar.divider()
        if st.sidebar.button("Encerrar Sessão"):
            st.session_state['autenticado'] = False
            st.rerun()

        if pagina_selecionada == "📊 Dashboard Geral":
            st.title("📊 Dashboard Comercial")
            
            # --- FILTROS NO TOPO (Expander) ---
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

            # --- FUNIL DO PERÍODO ---
            st.subheader("📅 Resultados do Período Selecionado")
            L, C, A, R, F = mL.sum(), mC.sum(), mA.sum(), mR.sum(), mF.sum()
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Leads", f"{L}")
            c2.metric("Contato", f"{C}", f"{(C/L*100):.1f}%" if L>0 else "0%")
            c3.metric("Agendado", f"{A}", f"{(A/C*100):.1f}%" if C>0 else "0%")
            c4.metric("Ocorrido", f"{R}", f"{(R/A*100):.1f}%" if A>0 else "0%")
            c5.metric("Fechado", f"{F}", f"{(F/R*100):.1f}%" if R>0 else "0%")

            st.divider()

            # --- BLOCO EXCLUSIVO MASTER (ACUMULADO ANUAL COM FECHADO E %) ---
            if st.session_state['perfil'] == "master":
                st.subheader(f"📈 Acumulado do Ano ({ano_ref})")
                
                # Cálculos YTD
                y_leads = (df_base['Data de criação'].dt.year == ano_ref).sum()
                y_contatos = (df_base['Contato Realizado'].dt.year == ano_ref).sum()
                y_agendados = (df_base['[IS/SDR] Data do Agendamento'].dt.year == ano_ref).sum()
                y_ocorridos = (df_base['[IS/Closer] Reunião Ocorrida'].dt.year == ano_ref).sum()
                y_fechados = ((df_base['Data de fechamento'].dt.year == ano_ref) & (df_base['Etapa do negócio'].isin(['Fechado', 'Pago']))).sum()

                cy1, cy2, cy3, cy4, cy5 = st.columns(5)
                cy1.metric("Leads (Ano)", f"{y_leads}")
                cy2.metric("Contato (Ano)", f"{y_contatos}", f"{(y_contatos/y_leads*100):.1f}%" if y_leads>0 else "0%")
                cy3.metric("Agendado (Ano)", f"{y_agendados}", f"{(y_agendados/y_contatos*100):.1f}%" if y_contatos>0 else "0%")
                cy4.metric("Ocorrido (Ano)", f"{y_ocorridos}", f"{(y_ocorridos/y_agendados*100):.1f}%" if y_agendados>0 else "0%")
                cy5.metric("Fechado (Ano)", f"{y_fechados}", f"{(y_fechados/y_ocorridos*100):.1f}%" if y_ocorridos>0 else "0%")

                st.divider()
                st.subheader("🏆 Performance SDR (Período)")
                sdr_perf = df_base[mL].groupby('Filtro_SDR').size().reset_index(name='Leads').sort_values('Leads', ascending=False)
                st.dataframe(sdr_perf, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
