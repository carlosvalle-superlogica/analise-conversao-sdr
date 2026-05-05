import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO DE LAYOUT E ESTILO
st.set_page_config(page_title="Marketing Analytics - B2B", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    .stApp { background-color: #ffffff !important; }
    [data-testid="stMetricLabel"] { color: #1565C0 !important; font-weight: 700 !important; text-transform: uppercase; }
    h1, h2, h3 { color: #1565C0 !important; }
    [data-testid="stMetric"] { background-color: #f8f9fa !important; border: 1px solid #e6e9ef !important; border-radius: 10px !important; padding: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGIN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
    st.session_state['perfil'] = None

def login():
    st.title("🔐 Acesso ao Sistema de Marketing")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario == "admin" and senha == "admin123":
            st.session_state['autenticado'] = True
            st.session_state['perfil'] = "admin"
            st.rerun()
        elif usuario == "mkt" and senha == "mkt123":
            st.session_state['autenticado'] = True
            st.session_state['perfil'] = "operador"
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")

if not st.session_state['autenticado']:
    login()
else:
    if st.sidebar.button("Sair / Logout"):
        st.session_state['autenticado'] = False
        st.rerun()

    try:
        # CARREGAMENTO E TRATAMENTO
        df = pd.read_csv('bd-teste-sistema.csv')
        df.columns = df.columns.str.strip()

        df['Data de criação'] = pd.to_datetime(df['Data de criação'], errors='coerce')
        col_contato = 'Contato Realizado' if 'Contato Realizado' in df.columns else df.columns[df.columns.str.contains('Contato Realizado')].tolist()[0]
        df['Data Contato'] = pd.to_datetime(df[col_contato], errors='coerce')
        df['Data Agendamento'] = pd.to_datetime(df['[IS/SDR] Data do Agendamento'], errors='coerce')
        col_reuniao = '[IS/Closer] Reunião Ocorrida' if '[IS/Closer] Reunião Ocorrida' in df.columns else df.columns[df.columns.str.contains('Reunião Ocorrida')].tolist()[0]
        df['Data Reuniao'] = pd.to_datetime(df[col_reuniao], errors='coerce')
        df['Data Fechamento'] = pd.to_datetime(df['Data de fechamento'], errors='coerce')

        # FILTROS
        st.sidebar.header(f"Perfil: {st.session_state['perfil'].upper()}")
        data_min, data_max = df['Data de criação'].dropna().min().date(), df['Data de criação'].dropna().max().date()
        periodo = st.sidebar.date_input("Período de Análise", [data_min, data_max])

        todas_origens = sorted(df["[IS] Origem do lead"].dropna().unique().tolist())
        origens_sel = st.sidebar.multiselect("Filtrar Origens", todas_origens, default=todas_origens)

        df_base = df[df["[IS] Origem do lead"].isin(origens_sel)].copy()

        if len(periodo) == 2:
            p_start, p_end = periodo[0], periodo[1]
            
            # Máscaras Período
            mL = (df_base['Data de criação'].dt.date >= p_start) & (df_base['Data de criação'].dt.date <= p_end)
            mC = (df_base['Data Contato'].dt.date >= p_start) & (df_base['Data Contato'].dt.date <= p_end)
            mA = (df_base['Data Agendamento'].dt.date >= p_start) & (df_base['Data Agendamento'].dt.date <= p_end)
            mR = (df_base['Data Reuniao'].dt.date >= p_start) & (df_base['Data Reuniao'].dt.date <= p_end)
            mF = (df_base['Data Fechamento'].dt.date >= p_start) & (df_base['Data Fechamento'].dt.date <= p_end) & (df_base['Etapa do negócio'].isin(['Fechado', 'Pago']))
            
            L, C, A, R, F = mL.sum(), mC.sum(), mA.sum(), mR.sum(), mF.sum()

            st.title("📊 Funil de Marketing B2B")

            # 1. VISÃO DO PERÍODO (Sempre Visível)
            st.subheader(f"📅 Resultados do Período")
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Leads", f"{L}")
            c2.metric("Contatos", f"{C}", f"{(C/L*100):.1f}%" if L>0 else "0%")
            c3.metric("Agendados", f"{A}", f"{(A/C*100):.1f}%" if C>0 else "0%")
            c4.metric("Reuniões", f"{R}", f"{(R/A*100):.1f}%" if A>0 else "0%")
            c5.metric("Fechados", f"{F}", f"{(F/R*100):.1f}%" if R>0 else "0%")

            st.divider()

            # 2. PERFORMANCE POR CANAL (Sempre Visível)
            st.subheader("📍 Performance por Canal (Origem)")
            leads_origem = df_base[mL].groupby("[IS] Origem do lead").size().reset_index(name='Leads')
            fechados_origem = df_base[mF].groupby("[IS] Origem do lead").size().reset_index(name='Vendas')
            tab_origem = leads_origem.merge(fechados_origem, on="[IS] Origem do lead", how="left").fillna(0)
            tab_origem['Taxa Conv. (%)'] = (tab_origem['Vendas'] / tab_origem['Leads'] * 100).map('{:.1f}%'.format)
            st.dataframe(tab_origem.sort_values("Leads", ascending=False), use_container_width=True, hide_index=True)

            # 3. VISÃO EXCLUSIVA DO ADMIN (ACUMULADO DO ANO)
            if st.session_state['perfil'] == "admin":
                st.divider()
                ano_ref = p_end.year
                mY_L = df_base['Data de criação'].dt.year == ano_ref
                mY_F = (df_base['Data Fechamento'].dt.year == ano_ref) & (df_base['Etapa do negócio'].isin(['Fechado', 'Pago']))
                
                st.subheader(f"📈 [ADMIN] Acumulado do Ano ({ano_ref})")
                cy1, cy2 = st.columns(2)
                cy1.metric("Total Leads YTD", f"{mY_L.sum()}")
                cy2.metric("Total Fechados YTD", f"{mY_F.sum()}", f"{(mY_F.sum()/mY_L.sum()*100):.1f}% Conv. Geral" if mY_L.sum()>0 else "0%")

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
