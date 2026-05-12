import streamlit as st
import pandas as pd
import numpy as np

# ==============================================================================
# ESTRUTURA BLINDADA - CONFIGURAÇÃO E ESTILO (DESIGN PREMIUM)
# ==============================================================================
st.set_page_config(page_title="Sistema de Gestão Comercial", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #F8FAFC;
    }

    header {background-color: transparent !important;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Customização da Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
        box-shadow: 4px 0px 15px rgba(0,0,0,0.03);
    }

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

    /* Cards de Métricas */
    div[data-testid="stMetricValue"] {
        background-color: #FFFFFF; border-radius: 12px; padding: 20px !important; 
        border: 1px solid #E2E8F0; color: #0F172A; font-weight: 700;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
    }
    
    [data-testid="stMetricDelta"] > div {
        background-color: #EFF6FF !important; color: #1E40AF !important; 
        border-radius: 6px; padding: 4px 10px; font-weight: 600; font-size: 0.85rem;
    }

    .stExpander {
        background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 1rem;
    }

    .stDataFrame { border: 1px solid #E2E8F0; border-radius: 12px; overflow: hidden; }
    
    /* Centralização de células e cabeçalhos nas tabelas do Pandas */
    .stDataFrame td, .stDataFrame th { text-align: center !important; }

    h1 { color: #0F172A !important; font-weight: 800 !important; letter-spacing: -0.025em; }
    h2 { color: #1E293B !important; font-weight: 700 !important; letter-spacing: -0.02em; }
    h3 { color: #334155 !important; font-weight: 600 !important; letter-spacing: -0.01em; }
    
    div[data-testid="stMultiSelect"] label p, div[data-testid="stDateInput"] label p, div[data-testid="stSelectbox"] label p {
        color: #1E40AF !important; font-weight: 700 !important; font-size: 0.9rem !important;
    }
    span[data-baseweb="tag"] { background-color: #1E40AF !important; border-radius: 6px !important;}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# SISTEMA DE ACESSO
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
            if u == "aquisições" and s == "2024":
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
        # FUNÇÃO MATEMÁTICA DE FORMATAÇÃO DE TEMPO (DIAS, HORAS, MIN)
        # ==============================================================================
        def formata_tempo(td):
            if pd.isna(td): return "Sem dados"
            try:
                total_segundos = int(td.total_seconds())
                if total_segundos < 0: return "Sem dados"
                dias = total_segundos // 86400
                horas = (total_segundos % 86400) // 3600
                minutos = (total_segundos % 3600) // 60
                
                partes = []
                if dias > 0: partes.append(f"{dias} dias")
                if horas > 0: partes.append(f"{horas} horas")
                if minutos > 0 or not partes: partes.append(f"{minutos} min")
                return ", ".join(partes)
            except:
                return "Sem dados"

        # ==============================================================================
        # CARREGAMENTO E ENGENHARIA DE DADOS
        # ==============================================================================
        df = pd.read_csv('bd-teste-sistema.csv')
        df.columns = df.columns.str.strip()

        col_criacao = 'Data de criação'
        
        # Busca Dinâmica da coluna de Contato e Perdido (Inflexível a erros de aspas)
        col_1_contato = None
        for col in df.columns:
            if '1' in col and 'ontato' in col.lower():
                col_1_contato = col
                break
                
        col_perdido_ent = next((col for col in df.columns if 'Perdidos' in col and 'B2B' in col), None)

        colunas_data = [
            col_criacao, 
            'Contato Realizado', 
            '[IS/SDR] Data do Agendamento', 
            '[IS/Closer] Reunião Ocorrida', 
            'Data de fechamento',
            '[IS/SDR] Data de Fechamento Perdido'
        ]
        
        if col_1_contato: colunas_data.append(col_1_contato)
        if col_perdido_ent: colunas_data.append(col_perdido_ent)
        
        # Conversão bruta para Datetime
        for col in colunas_data:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Data Perda Blindada
        if '[IS/SDR] Data de Fechamento Perdido' in df.columns:
            df['Data Perda Blindada'] = df['[IS/SDR] Data de Fechamento Perdido'].fillna(df['Data de fechamento'])
        else:
            df['Data Perda Blindada'] = df['Data de fechamento']
        df['Data Perda Blindada'] = pd.to_datetime(df['Data Perda Blindada'], errors='coerce')

        # --- CÁLCULO BRUTO DO TMA (BLINDADO) ---
        if col_1_contato and col_1_contato in df.columns and col_criacao in df.columns:
            # Garante que ambas as colunas são datetime antes de subtrair
            mask_tma_valido = df[col_criacao].notna() & df[col_1_contato].notna()
            df['TMA_Timedelta'] = pd.NaT
            df.loc[mask_tma_valido, 'TMA_Timedelta'] = (
                df.loc[mask_tma_valido, col_1_contato] - df.loc[mask_tma_valido, col_criacao]
            )
            # Limpa anomalias do HubSpot (datas invertidas — resultado negativo)
            mask_negativo = df['TMA_Timedelta'].notna() & (df['TMA_Timedelta'].dt.total_seconds() < 0)
            df.loc[mask_negativo, 'TMA_Timedelta'] = pd.NaT
        else:
            df['TMA_Timedelta'] = pd.NaT

        # --- CÁLCULO DA PERSISTÊNCIA (BLINDADO) ---
        if col_perdido_ent and col_perdido_ent in df.columns and col_criacao in df.columns:
            mask_perm_valido = df[col_criacao].notna() & df[col_perdido_ent].notna()
            df['Perm_Timedelta'] = pd.NaT
            df.loc[mask_perm_valido, 'Perm_Timedelta'] = (
                df.loc[mask_perm_valido, col_perdido_ent] - df.loc[mask_perm_valido, col_criacao]
            )
            mask_perm_neg = df['Perm_Timedelta'].notna() & (df['Perm_Timedelta'].dt.total_seconds() < 0)
            df.loc[mask_perm_neg, 'Perm_Timedelta'] = pd.NaT
        else:
            df['Perm_Timedelta'] = pd.NaT

        # Normalizações Qualitativas
        df['Filtro_SDR'] = df['[IS/SDR] SDR Responsável'].fillna('Sem SDR')
        df['Filtro_Closer'] = df['[IS/SDR] Closer Responsável'].fillna('Sem Closer')
        
        if '[Comercial B2B] Repescagem' in df.columns:
            df['Repescagem_Limpa'] = df['[Comercial B2B] Repescagem'].fillna('Não').astype(str).str.strip().str.title()
        else:
            df['Repescagem_Limpa'] = 'Não'

        # --- BARRA LATERAL ---
        st.sidebar.markdown("<h2 style='font-size: 1.1rem; margin-bottom: 5px;'>Pipeline</h2>", unsafe_allow_html=True)
        pipeline_sel = st.sidebar.selectbox("Pipeline", ["Aquisições", "Canais"], label_visibility="collapsed")
        
        st.sidebar.markdown("<br><h2 style='font-size: 1.1rem; margin-bottom: 5px;'>Módulos</h2>", unsafe_allow_html=True)
        
        if st.session_state['perfil'] == "master":
            menu_opcoes = ["📊 Dashboard Geral", "📦 Produtos / Closer's / VC", "💰 Receita", "❌ Perdidos", "⚙️ Configurações"]
        else:
            menu_opcoes = ["📊 Dashboard Geral"]
            
        pagina_sel = st.sidebar.radio("Navegação", menu_opcoes, label_visibility="collapsed")
        
        st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
        st.sidebar.divider()
        if st.sidebar.button("🚪 Sair do Sistema", use_container_width=True):
            st.session_state['autenticado'] = False
            st.rerun()

        # ==============================================================================
        # FILTROS GLOBAIS
        # ==============================================================================
        with st.expander("🔍 Parâmetros de Filtro", expanded=True):
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                data_min, data_max = df['Data de criação'].dropna().min().date(), df['Data de criação'].dropna().max().date()
                periodo = st.date_input("Período de Análise", [data_min, data_max])
                tipos_sel = st.multiselect("Tipo de Lead", sorted(df["[IS] Tipo de lead"].dropna().unique().tolist()), default=sorted(df["[IS] Tipo de lead"].dropna().unique().tolist()))
            with c2:
                origens_sel = st.multiselect("Origem do Lead", sorted(df["[IS] Origem do lead"].dropna().unique().tolist()), default=sorted(df["[IS] Origem do lead"].dropna().unique().tolist()))
                jornada_sel = st.multiselect("Jornada", sorted(df["[IS] Lead com Jornada:"].dropna().unique().tolist()), default=sorted(df["[IS] Lead com Jornada:"].dropna().unique().tolist()))
            with c3:
                repescagem_filtro = st.selectbox("Repescagem?", ["Todos", "Sim", "Não"])
                if st.session_state['perfil'] == "master":
                    sdrs_sel = st.multiselect("SDR", sorted(df['Filtro_SDR'].unique().tolist()), default=sorted(df['Filtro_SDR'].unique().tolist()))
                    closers_sel = st.multiselect("Closer", sorted(df['Filtro_Closer'].unique().tolist()), default=sorted(df['Filtro_Closer'].unique().tolist()))
                else:
                    sdrs_sel, closers_sel = df['Filtro_SDR'].unique().tolist(), df['Filtro_Closer'].unique().tolist()

        # Aplicação dos Filtros Qualitativos
        df_base = df[
            (df["[IS] Origem do lead"].isin(origens_sel)) &
            (df["[IS] Tipo de lead"].isin(tipos_sel)) &
            (df["[IS] Lead com Jornada:"].isin(jornada_sel)) &
            (df['Filtro_SDR'].isin(sdrs_sel)) &
            (df['Filtro_Closer'].isin(closers_sel))
        ].copy()

        if repescagem_filtro != "Todos":
            df_base = df_base[df_base['Repescagem_Limpa'] == repescagem_filtro]

        # Máscaras Matemáticas de Data
        if len(periodo) == 2:
            p_start, p_end = periodo[0], periodo[1]
            mL = (df_base['Data de criação'].dt.date >= p_start) & (df_base['Data de criação'].dt.date <= p_end)
            mC = (df_base['Contato Realizado'].dt.date >= p_start) & (df_base['Contato Realizado'].dt.date <= p_end)
            mA = (df_base['[IS/SDR] Data do Agendamento'].dt.date >= p_start) & (df_base['[IS/SDR] Data do Agendamento'].dt.date <= p_end)
            mR = (df_base['[IS/Closer] Reunião Ocorrida'].dt.date >= p_start) & (df_base['[IS/Closer] Reunião Ocorrida'].dt.date <= p_end)
            mF = (df_base['Data de fechamento'].dt.date >= p_start) & (df_base['Data de fechamento'].dt.date <= p_end) & (df_base['Etapa do negócio'].isin(['Fechado', 'Pago']))
            mP = (df_base['Data Perda Blindada'].dt.date >= p_start) & (df_base['Data Perda Blindada'].dt.date <= p_end) & (df_base['Motivo de Fechamento Perdido'].notna())
            ano_ref = p_end.year
        else:
            p_end = df['Data de criação'].max()
            ano_ref = p_end.year if pd.notna(p_end) else 2026
            mL = mC = mA = mR = mF = mP = pd.Series([False]*len(df_base), index=df_base.index)

        # ==============================================================================
        # ROTEAMENTO DE PÁGINAS E PIPELINES
        # ==============================================================================
        if pipeline_sel == "Aquisições":
            
            # --------------------------------------------------------------------------
            # PÁGINA: DASHBOARD GERAL
            # --------------------------------------------------------------------------
            if pagina_sel == "📊 Dashboard Geral":
                st.markdown("### 📈 Performance de Funil: Aquisições")
                L, C, A, R, F = mL.sum(), mC.sum(), mA.sum(), mR.sum(), mF.sum()
                
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
                with v1: st.subheader("📍 Por Origem"); st.dataframe(criar_tabela_mkt("[IS] Origem do lead"), use_container_width=True, hide_index=True)
                with v2: st.subheader("🏷️ Por Tipo"); st.dataframe(criar_tabela_mkt("[IS] Tipo de lead"), use_container_width=True, hide_index=True)
                with v3: st.subheader("🚀 Por Jornada"); st.dataframe(criar_tabela_mkt("[IS] Lead com Jornada:"), use_container_width=True, hide_index=True)

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
                    
                    t_sdr_funil = s_l.merge(s_c, on='Filtro_SDR', how='outer').merge(s_a, on='Filtro_SDR', how='outer').merge(s_r, on='Filtro_SDR', how='outer').merge(s_f, on='Filtro_SDR', how='outer').fillna(0)
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

            # --------------------------------------------------------------------------
            # PÁGINA: PRODUTOS / CLOSER'S / VC
            # --------------------------------------------------------------------------
            elif pagina_sel == "📦 Produtos / Closer's / VC":
                st.markdown("### 📦 Produtos / Closer's / VC")
                tR, tF = mR.sum(), mF.sum()
                col_prod = '[IS/Closer] Produtos Fechados'
                
                if col_prod in df_base.columns:
                    df_vendas = df_base[mF][col_prod].dropna().astype(str)
                    produtos_separados = df_vendas.str.split(';').explode().str.strip()
                    produtos_separados = produtos_separados[produtos_separados != ""]
                    
                    contagem_prod = produtos_separados.value_counts().reset_index()
                    contagem_prod.columns = ['Produto', 'Qtd. Vendida']
                    total_produtos = contagem_prod['Qtd. Vendida'].sum()
                    
                    conv_cliente = (tF / tR * 100) if tR > 0 else 0.0
                    conv_produto = (total_produtos / tR * 100) if tR > 0 else 0.0
                    
                    cp1, cp2, cp3, cp4, cp5 = st.columns(5)
                    cp1.metric("Reuniões Ocorridas", f"{tR}")
                    cp2.metric("Clientes Fechados", f"{tF}")
                    cp3.metric("Produtos Vendidos", f"{total_produtos}")
                    cp4.metric("Conv. Clientes / Reuniões", f"{conv_cliente:.1f}%")
                    cp5.metric("Conv. Produtos / Reuniões", f"{conv_produto:.1f}%")
                    
                    st.divider()
                    st.subheader("📊 Performance por Produto Fechado")
                    contagem_prod['% do Mix (Total Vendido)'] = contagem_prod['Qtd. Vendida'].apply(lambda x: f"{(x / total_produtos * 100):.1f}%" if total_produtos > 0 else "0.0%")
                    contagem_prod['% Produto / Reunião'] = contagem_prod['Qtd. Vendida'].apply(lambda x: f"{(x / tR * 100):.1f}%" if tR > 0 else "0.0%")
                    
                    col_tabela, col_vazia = st.columns([7, 3])
                    with col_tabela:
                        st.dataframe(contagem_prod.sort_values(by='Qtd. Vendida', ascending=False), use_container_width=True, hide_index=True)
                    
                    st.divider()
                    st.subheader("🤝 Sinergia da Equipe (Conversão Ocorrido x Fechado)")
                    df_sync_r = df_base[mR].groupby(['Filtro_SDR', 'Filtro_Closer']).size().reset_index(name='Ocorridos')
                    df_sync_f = df_base[mF].groupby(['Filtro_SDR', 'Filtro_Closer']).size().reset_index(name='Fechados')
                    df_sync = pd.merge(df_sync_r, df_sync_f, on=['Filtro_SDR', 'Filtro_Closer'], how='outer').fillna(0)
                    
                    df_sync['Conversao_Limpa'] = df_sync.apply(lambda r: f"{(r['Fechados'] / r['Ocorridos'] * 100):.1f}%" if r['Ocorridos'] > 0 else "-", axis=1)
                    pivot_sdr_closer = df_sync.pivot(index='Filtro_SDR', columns='Filtro_Closer', values='Conversao_Limpa').fillna('-')
                    pivot_closer_sdr = df_sync.pivot(index='Filtro_Closer', columns='Filtro_SDR', values='Conversao_Limpa').fillna('-')
                    
                    col_mat1, col_mat2 = st.columns(2)
                    with col_mat1:
                        st.markdown("<h4 style='color: #334155;'>🔄 Visão: SDR por Closer</h4>", unsafe_allow_html=True)
                        st.dataframe(pivot_sdr_closer, use_container_width=True)
                    with col_mat2:
                        st.markdown("<h4 style='color: #334155;'>🔄 Visão: Closer por SDR</h4>", unsafe_allow_html=True)
                        st.dataframe(pivot_closer_sdr, use_container_width=True)

            # --------------------------------------------------------------------------
            # PÁGINA: ❌ PERDIDOS (A ANAMNESE ESTRATÉGICA)
            # --------------------------------------------------------------------------
            elif pagina_sel == "❌ Perdidos":
                st.markdown("### ❌ Gestão Estratégica de Perdas e Desperdício")
                
                # df_perdidos foca APENAS nos leads que caíram pra Perdido no período
                df_perdidos = df_base[mP].copy()
                total_perdas = len(df_perdidos)
                total_recebidos = mL.sum() 
                
                # ==========================================
                # 0. ANÁLISE DE TEMPO (TMA E PERSISTÊNCIA)
                # ==========================================
                st.markdown("<h4 style='color: #1E40AF; margin-top: 10px;'>⏳ Análise de Tempo Operacional</h4>", unsafe_allow_html=True)
                
                # TMA EXATO DA REGRA DO CARLOS:
                # 1. Filtra a base APENAS pelos leads criados no período (mL)
                df_tma_validos = df_base[mL].copy()
                
                if col_1_contato and col_1_contato in df_tma_validos.columns:
                    # 2. Usa filtro booleano em vez de dropna para evitar KeyError com nomes complexos
                    mask_tma_page = df_tma_validos[col_criacao].notna() & df_tma_validos[col_1_contato].notna()
                    df_tma_validos_filtrado = df_tma_validos.loc[mask_tma_page, 'TMA_Timedelta']
                    tma_validos_pos = df_tma_validos_filtrado[df_tma_validos_filtrado.notna()]
                    # 3. Calcula a média (independente de estar ganho, perdido ou aberto)
                    tma_medio_td = tma_validos_pos.mean() if not tma_validos_pos.empty else pd.NaT
                else:
                    tma_medio_td = pd.NaT
                    if col_1_contato:
                        st.warning(f"Atenção: A coluna de 1º Contato ('{col_1_contato}') foi identificada mas não está disponível no DataFrame filtrado.")
                    else:
                        st.warning("Atenção: Nenhuma coluna de 1º Contato foi encontrada. Verifique se o CSV exportado do HubSpot contém a coluna com '1' e 'ontato' no nome.")
                
                # PERMANÊNCIA: Apenas leads perdidos por 'Sem contato'
                if total_perdas > 0 and col_perdido_ent and col_perdido_ent in df_base.columns:
                    mask_sc = df_perdidos['Motivo de Fechamento Perdido'] == 'Sem contato'
                    mask_perm_fields = df_perdidos[col_criacao].notna() & df_perdidos[col_perdido_ent].notna()
                    df_perdidos_sc = df_perdidos[mask_sc & mask_perm_fields]
                    perm_media_td = df_perdidos_sc['Perm_Timedelta'].mean() if not df_perdidos_sc.empty else pd.NaT
                else:
                    perm_media_td = pd.NaT
                
                ct1, ct2 = st.columns(2)
                ct1.metric(
                    "TMA Médio (Data de Criação ➔ 1º Contato)", 
                    formata_tempo(tma_medio_td), 
                    "Calculado sobre toda a base filtrada que possui os dois campos preenchidos", 
                    delta_color="off"
                )
                ct2.metric(
                    "Permanência Média (Apenas motivo 'Sem Contato')", 
                    formata_tempo(perm_media_td), 
                    "Data de Criação ➔ Data de Perdido (Mede a persistência no lead)", 
                    delta_color="off"
                )
                
                st.divider()

                if total_perdas > 0:
                    df_perdidos['Responsavel_Papel'] = df_perdidos['[IS/Closer] Reunião Ocorrida'].apply(lambda x: 'Closer' if pd.notnull(x) else 'SDR')

                    # ==========================================
                    # 1. ANÁLISE DE DESPERDÍCIO (LEADS INVÁLIDOS)
                    # ==========================================
                    st.markdown("<h4 style='color: #B91C1C; margin-top: 10px; text-align: center;'>🗑️ Análise de Desperdício (Leads Inativos/Inválidos)</h4>", unsafe_allow_html=True)
                    
                    motivos_lixo = ['Sem contato', 'Dados inconsistentes', 'Desqualificado', 'Contato duplicado']
                    df_lixo = df_perdidos[df_perdidos['Motivo de Fechamento Perdido'].isin(motivos_lixo)]
                    total_lixo = len(df_lixo)
                    
                    if total_lixo > 0:
                        pct_sobre_recebidos = (total_lixo / total_recebidos * 100) if total_recebidos > 0 else 0
                        pct_sobre_perdidos = (total_lixo / total_perdas * 100) if total_perdas > 0 else 0
                        
                        tabela_lixo = df_lixo['Motivo de Fechamento Perdido'].value_counts().reset_index()
                        tabela_lixo.columns = ['Motivo (Inválido)', 'Quantidade']
                        
                        tabela_lixo['% sobre Todos os Recebidos'] = tabela_lixo['Quantidade'].apply(lambda x: f"{(x / total_recebidos * 100):.1f}%" if total_recebidos > 0 else "0.0%")
                        tabela_lixo['% sobre Todos os Perdidos'] = tabela_lixo['Quantidade'].apply(lambda x: f"{(x / total_perdas * 100):.1f}%" if total_perdas > 0 else "0.0%")
                        
                        linha_total = pd.DataFrame([{
                            'Motivo (Inválido)': '🚨 TOTAL ACUMULADO',
                            'Quantidade': total_lixo,
                            '% sobre Todos os Recebidos': f"{pct_sobre_recebidos:.1f}%",
                            '% sobre Todos os Perdidos': f"{pct_sobre_perdidos:.1f}%"
                        }])
                        tabela_lixo = pd.concat([tabela_lixo, linha_total], ignore_index=True)
                        
                        tabela_estilizada = tabela_lixo.style.set_properties(**{'text-align': 'center'})
                        
                        col_vazia1, col_tabela_central, col_vazia2 = st.columns([1.5, 7, 1.5])
                        with col_tabela_central:
                            st.dataframe(tabela_estilizada, use_container_width=True, hide_index=True)
                            st.caption(f"<div style='text-align: center; color: #334155; font-size: 0.95rem;'><b>Insight de Negócio:</b> Dos {total_recebidos} leads recebidos, <b>{pct_sobre_recebidos:.1f}%</b> foram descartados por falta de contato ou qualificação inicial. Isso significa que o time comercial pôde atuar de verdade em apenas {100-pct_sobre_recebidos:.1f}% da base.</div>", unsafe_allow_html=True)
                    
                    st.divider()

                    # ==========================================
                    # 2. MAIOR MOTIVO GERAL E POR PAPEL
                    # ==========================================
                    qtd_sdr = len(df_perdidos[df_perdidos['Responsavel_Papel'] == 'SDR'])
                    qtd_closer = len(df_perdidos[df_perdidos['Responsavel_Papel'] == 'Closer'])
                    
                    cp1, cp2, cp3 = st.columns(3)
                    cp1.metric("Total de Leads Perdidos", f"{total_perdas}")
                    cp2.metric("Perdas SDR (Pré-Reunião)", f"{qtd_sdr}", f"{(qtd_sdr/total_perdas*100):.1f}%" if total_perdas>0 else "0%", delta_color="off")
                    cp3.metric("Perdas Closer (Pós-Reunião)", f"{qtd_closer}", f"{(qtd_closer/total_perdas*100):.1f}%" if total_perdas>0 else "0%", delta_color="off")
                    
                    st.write("")
                    st.subheader("⚖️ Motivos de Perda por Papel na Equipe")
                    
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        st.markdown("<h4 style='color: #1E40AF;'>📉 Perdas SDR (Não chegaram na mesa)</h4>", unsafe_allow_html=True)
                        df_sdr_perdas = df_perdidos[df_perdidos['Responsavel_Papel'] == 'SDR']
                        if not df_sdr_perdas.empty:
                            m_sdr = df_sdr_perdas['Motivo de Fechamento Perdido'].value_counts().reset_index()
                            m_sdr.columns = ['Motivo', 'Quantidade']
                            m_sdr['%'] = m_sdr['Quantidade'].apply(lambda x: f"{(x/qtd_sdr*100):.1f}%")
                            st.dataframe(m_sdr, use_container_width=True, hide_index=True)
                            
                    with col_p2:
                        st.markdown("<h4 style='color: #1E40AF;'>📉 Perdas Closer (Ocorreu Reunião)</h4>", unsafe_allow_html=True)
                        df_closer_perdas = df_perdidos[df_perdidos['Responsavel_Papel'] == 'Closer']
                        if not df_closer_perdas.empty:
                            m_closer = df_closer_perdas['Motivo de Fechamento Perdido'].value_counts().reset_index()
                            m_closer.columns = ['Motivo', 'Quantidade']
                            m_closer['%'] = m_closer['Quantidade'].apply(lambda x: f"{(x/qtd_closer*100):.1f}%")
                            st.dataframe(m_closer, use_container_width=True, hide_index=True)

                    st.divider()

                    # ==========================================
                    # 3. ANÁLISE CRUZADA: ORIGEM X MOTIVO
                    # ==========================================
                    st.subheader("📍 Análise Cruzada: Origem x Motivo de Perda")
                    st.info("A matriz abaixo exibe o volume de perdas cruzando a Origem de Marketing com o Motivo.")
                    
                    pivot_origem = pd.crosstab(df_perdidos['[IS] Origem do lead'], df_perdidos['Motivo de Fechamento Perdido'], margins=True, margins_name='Total (Todas as Origens)')
                    pivot_origem = pivot_origem.sort_values('Total (Todas as Origens)', ascending=False)
                    st.dataframe(pivot_origem, use_container_width=True)

                    st.divider()

                    # ==========================================
                    # 4. AUDITORIA QUALITATIVA (COM TMA E DIAS NO FUNIL)
                    # ==========================================
                    st.subheader("🔍 Auditoria de Textos, Sub-motivos e Tempos Operacionais")
                    st.markdown("Examine cada lead para validar o tempo de resposta, o tempo de persistência e as anotações do time.")
                    
                    df_perdidos['TMA do Lead'] = df_perdidos['TMA_Timedelta'].apply(formata_tempo)
                    df_perdidos['Tempo no Funil'] = df_perdidos['Perm_Timedelta'].apply(formata_tempo)
                    
                    col_auditoria = ['Nome do negócio', 'Responsavel_Papel', 'TMA do Lead', 'Tempo no Funil', 'Motivo de Fechamento Perdido', 'Motivo de Fechamento Perdido (Sub-motivo)', 'Descrição de fechamento perdido', 'Repescagem_Limpa']
                    st.dataframe(df_perdidos[col_auditoria].fillna('-').rename(columns={'Responsavel_Papel': 'Responsável Pela Perda', 'Repescagem_Limpa': 'É Repescagem?'}), use_container_width=True, hide_index=True)
                    
                    st.markdown("<br><br><br>", unsafe_allow_html=True)
                else:
                    st.warning("🎉 Excelente! Não há nenhum lead perdido para o período e filtros selecionados.")

        elif pipeline_sel == "Canais":
            st.markdown("### 📈 Performance de Funil: Canais")
            st.warning("Aguardando importação do ficheiro 'bd-canais.csv' para processamento.")

    except Exception as e:
        st.error(f"Erro no processamento: {e}")
