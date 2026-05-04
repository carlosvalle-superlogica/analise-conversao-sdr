import streamlit as st
import pandas as pd

# ==========================================
# 1. CONFIGURAÇÃO DE LAYOUT E ESTILO
# ==========================================
st.set_page_config(page_title="Análise CRM", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Fonte Inter Global */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Cores de Fundo (White Theme) */
    .stApp { background-color: #ffffff !important; }
    [data-testid="stSidebar"] {
        background-color: #f0f2f6 !important;
        border-right: 1px solid #e6e9ef !important;
    }

    /* Cards KPI */
    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #e6e9ef !important;
        border-radius: 0.5rem !important;
        padding: 1rem !important;
        box-shadow: none !important;
    }
    
    /* NOME DOS CARDS (Títulos das Métricas) - Forçado para AZUL */
    [data-testid="stMetricLabel"] {
        color: #1565C0 !important; 
        font-size: 0.85rem !important; 
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    /* VALOR DOS CARDS */
    [data-testid="stMetricValue"] {
        color: #31333f !important;
        font-size: 2.25rem !important;
        font-weight: 700 !important;
        margin-top: 0.25rem !important;
    }
    
    /* PERCENTAGEM DOS CARDS */
    [data-testid="stMetricDelta"] > div {
        background-color: transparent !important;
        color: #09ab3b !important; /* Verde */
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        padding: 0 !important;
        margin-top: 0.25rem !important;
    }
    [data-testid="stMetricDelta"] svg { display: none !important; }

    /* Filtros Selecionados */
    span[data-baseweb="tag"] {
        background-color: #1565C0 !important;
        color: white !important;
        border-radius: 4px;
    }

    /* TÍTULOS GERAIS DA PÁGINA (Forçado para AZUL) */
    h1, h2, h3, h4 { 
        color: #1565C0 !important; 
        font-weight: 700 !important; 
    }
    
    /* Tabelas */
    .stDataFrame {
        border: 1px solid #e6e9ef !important;
        border-radius: 0.5rem !important;
    }
    hr { border-color: #e6e9ef !important; margin: 2rem 0 !important; }
    </style>
    """, unsafe_allow_html=True)

try:
    # ==========================================
    # 2. CONTROLE MASTER DE UNIDADE DE NEGÓCIO
    # ==========================================
    st.sidebar.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <div style="background-color: #1565C0; color: white; width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px;">CR</div>
            <div>
                <div style="color: #31333f; font-weight: 700; font-size: 18px; line-height: 1;">Análise</div>
                <div style="color: #5e606b; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Enterprise Analytics</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("<label style='font-size: 12px; font-weight: 700; color: #5e606b; text-transform: uppercase;'>Pipeline Principal</label>", unsafe_allow_html=True)
    unidade_negocio = st.sidebar.selectbox(
        "Selecione o Pipeline", 
        ["Comercial B2B (Aquisições)", "[PFI] Comercial Canais"],
        label_visibility="collapsed"
    )
    
    st.sidebar.divider()

    # ==========================================
    # MENU LATERAL COMUM
    # ==========================================
    st.sidebar.markdown("<label style='font-size: 12px; font-weight: 700; color: #5e606b; text-transform: uppercase;'>Navegação</label>", unsafe_allow_html=True)
    menu_opcoes = ["📊 Dashboard Geral", "📦 Visão de Produtos", "💰 Receita", "❌ Perdidos", "⚙️ Configurações"]
    pagina_selecionada = st.sidebar.radio("Navegação Principal", menu_opcoes, label_visibility="collapsed")

    # ==========================================
    # 3. LÓGICA DE APLICATIVO POR UNIDADE
    # ==========================================
    if unidade_negocio == "Comercial B2B (Aquisições)":
        
        # --- CARREGAMENTO DE DADOS ---
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
        
        if pagina_selecionada == "📊 Dashboard Geral":
            st.markdown("<h1 style='font-size: 28px; margin-bottom: 4px;'>Dashboard Geral (Aquisições)</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color: #5e606b; margin-bottom: 20px;'>Visão consolidada de performance do B2B.</p>", unsafe_allow_html=True)
            
            with st.expander("🔍 FILTROS (Deixe vazio para ver tudo)", expanded=False):
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    data_min, data_max = df['Data de criação'].dropna().min().date(), df['Data de criação'].dropna().max().date()
                    periodo = st.date_input("Período do Evento", [data_min, data_max])
                with col_f2:
                    tipos = sorted(df["[IS] Tipo de lead"].dropna().unique().tolist())
                    filtro_tipo = st.multiselect("Tipo de Lead", tipos, default=[]) 
                    origens = sorted(df["[IS] Origem do lead"].dropna().unique().tolist())
                    filtro_origem = st.multiselect("Origem do Lead", origens, default=[])
                with col_f3:
                    lista_sdr = sorted(df['Filtro_SDR'].unique().tolist())
                    filtro_sdr = st.multiselect("SDR Responsável", lista_sdr, default=[])
                    lista_closer = sorted(df['Filtro_Closer'].unique().tolist())
                    filtro_closer = st.multiselect("Closer Responsável", lista_closer, default=[])

            tipo_final = filtro_tipo if filtro_tipo else tipos
            origem_final = filtro_origem if filtro_origem else origens
            sdr_final = filtro_sdr if filtro_sdr else lista_sdr
            closer_final = filtro_closer if filtro_closer else lista_closer

            # MÁSCARA BASE DOS ATRIBUTOS (Aplicado a Período e YTD)
            mask_atributos = ((df["[IS] Tipo de lead"].isin(tipo_final)) & (df["[IS] Origem do lead"].isin(origem_final)) & (df['Filtro_SDR'].isin(sdr_final)) & (df['Filtro_Closer'].isin(closer_final)))
            df_base = df[mask_atributos].copy()

            # --- MÁSCARAS DO PERÍODO SELECIONADO ---
            if isinstance(periodo, (list, tuple)) and len(periodo) == 2:
                p_start, p_end = periodo[0], periodo[1]
                mask_L = (df_base['Data de criação'].dt.date >= p_start) & (df_base['Data de criação'].dt.date <= p_end)
                mask_C = (df_base['Data Contato'].dt.date >= p_start) & (df_base['Data Contato'].dt.date <= p_end)
                mask_A = (df_base['Data Agendamento'].dt.date >= p_start) & (df_base['Data Agendamento'].dt.date <= p_end)
                mask_R = (df_base['Data Reuniao'].dt.date >= p_start) & (df_base['Data Reuniao'].dt.date <= p_end)
                mask_F = (df_base['Data Fechamento'].dt.date >= p_start) & (df_base['Data Fechamento'].dt.date <= p_end) & (df_base['Etapa do negócio'].isin(['Fechado', 'Pago']))
                ano_ref = p_end.year
            else:
                mask_L = df_base['Data de criação'].notna(); mask_C = df_base['Data Contato'].notna(); mask_A = df_base['Data Agendamento'].notna(); mask_R = df_base['Data Reuniao'].notna(); mask_F = df_base['Etapa do negócio'].isin(['Fechado', 'Pago'])
                ano_ref = df_base['Data de criação'].dt.year.max() if not df_base.empty else 2026

            L, C, A, R, F = mask_L.sum(), mask_C.sum(), mask_A.sum(), mask_R.sum(), mask_F.sum()

            # --- MÁSCARAS DO ACUMULADO DO ANO (YTD) ---
            mask_L_ytd = df_base['Data de criação'].dt.year == ano_ref
            mask_C_ytd = df_base['Data Contato'].dt.year == ano_ref
            mask_A_ytd = df_base['Data Agendamento'].dt.year == ano_ref
            mask_R_ytd = df_base['Data Reuniao'].dt.year == ano_ref
            mask_F_ytd = (df_base['Data Fechamento'].dt.year == ano_ref) & (df_base['Etapa do negócio'].isin(['Fechado', 'Pago']))
            
            L_ytd, C_ytd, A_ytd = mask_L_ytd.sum(), mask_C_ytd.sum(), mask_A_ytd.sum()
            R_ytd, F_ytd = mask_R_ytd.sum(), mask_F_ytd.sum()

            st.write("")
            
            # --- RENDERIZAÇÃO: PERÍODO SELECIONADO ---
            st.markdown("<h3 style='font-size: 14px; color: #5e606b; margin-bottom: 10px; text-transform: uppercase;'>Visão do Período Selecionado</h3>", unsafe_allow_html=True)
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Leads Entrantes", f"{L:,.0f}".replace(',','.'))
            m2.metric("Contatos Feitos", f"{C:,.0f}".replace(',','.'), f"{(C/L*100):.1f}% Contato" if L>0 else "0%")
            m3.metric("Agendamentos", f"{A:,.0f}".replace(',','.'), f"{(A/C*100):.1f}% Agendado" if C>0 else "0%")
            m4.metric("Reuniões Ocorridas", f"{R:,.0f}".replace(',','.'), f"{(R/A*100):.1f}% Ocorrido" if A>0 else "0%")
            m5.metric("Negócios Fechados", f"{F:,.0f}".replace(',','.'), f"{(F/R*100):.1f}% Fechado" if R>0 else "0%")

            st.write("")

            # --- RENDERIZAÇÃO: ACUMULADO DO ANO ---
            st.markdown(f"<h3 style='font-size: 14px; color: #5e606b; margin-bottom: 10px; text-transform: uppercase;'>Acumulado do Ano ({ano_ref})</h3>", unsafe_allow_html=True)
            my1, my2, my3, my4, my5 = st.columns(5)
            my1.metric("Leads (YTD)", f"{L_ytd:,.0f}".replace(',','.'))
            my2.metric("Contatos (YTD)", f"{C_ytd:,.0f}".replace(',','.'), f"{(C_ytd/L_ytd*100):.1f}% Contato" if L_ytd>0 else "0%")
            my3.metric("Agendamentos (YTD)", f"{A_ytd:,.0f}".replace(',','.'), f"{(A_ytd/C_ytd*100):.1f}% Agendado" if C_ytd>0 else "0%")
            my4.metric("Reuniões (YTD)", f"{R_ytd:,.0f}".replace(',','.'), f"{(R_ytd/A_ytd*100):.1f}% Ocorrido" if A_ytd>0 else "0%")
            my5.metric("Fechados (YTD)", f"{F_ytd:,.0f}".replace(',','.'), f"{(F_ytd/R_ytd*100):.1f}% Fechado" if R_ytd>0 else "0%")

            st.divider()

            def criar_tabela_evento(coluna_nome):
                leads_cat = df_base[mask_L].groupby(coluna_nome).size().reset_index(name='Leads')
                reunioes_cat = df_base[mask_R].groupby(coluna_nome).size().reset_index(name='Reunioes')
                fechados_cat = df_base[mask_F].groupby(coluna_nome).size().reset_index(name='Fechados')
                tabela = leads_cat.merge(reunioes_cat, on=coluna_nome, how='outer').merge(fechados_cat, on=coluna_nome, how='outer').fillna(0)
                tabela['Lead x Reunião (%)'] = tabela.apply(lambda row: f"{(row['Reunioes']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
                tabela['Lead x Fechado (%)'] = tabela.apply(lambda row: f"{(row['Fechados']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
                return tabela[[coluna_nome, 'Leads', 'Lead x Reunião (%)', 'Lead x Fechado (%)']].sort_values(by='Leads', ascending=False)

            c_a, c_b = st.columns(2)
            with c_a: st.subheader("📍 Por Origem"); st.dataframe(criar_tabela_evento("[IS] Origem do lead"), use_container_width=True, hide_index=True)
            with c_b: st.subheader("🏷️ Por Tipo"); st.dataframe(criar_tabela_evento("[IS] Tipo de lead"), use_container_width=True, hide_index=True)

            st.divider()

            st.subheader("🏆 Performance por SDR")
            sdr_l = df_base[mask_L].groupby('Filtro_SDR').size().reset_index(name='Leads')
            sdr_c = df_base[mask_C].groupby('Filtro_SDR').size().reset_index(name='Contatos')
            sdr_a = df_base[mask_A].groupby('Filtro_SDR').size().reset_index(name='Agendados')
            sdr_r = df_base[mask_R].groupby('Filtro_SDR').size().reset_index(name='Ocorridos')
            df_sdr = sdr_l.merge(sdr_c, on='Filtro_SDR', how='outer').merge(sdr_a, on='Filtro_SDR', how='outer').merge(sdr_r, on='Filtro_SDR', how='outer').fillna(0).rename(columns={'Filtro_SDR': 'SDR Responsável'})
            df_sdr['Cont/Lead (%)'] = df_sdr.apply(lambda row: f"{(row['Contatos']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
            df_sdr['Agend/Cont (%)'] = df_sdr.apply(lambda row: f"{(row['Agendados']/row['Contatos']*100):.1f}%" if row['Contatos'] > 0 else "-", axis=1)
            df_sdr['Ocorr/Agend (%)'] = df_sdr.apply(lambda row: f"{(row['Ocorridos']/row['Agendados']*100):.1f}%" if row['Agendados'] > 0 else "-", axis=1)
            col_sdr = ['SDR Responsável', 'Leads', 'Contatos', 'Agendados', 'Ocorridos', 'Cont/Lead (%)', 'Agend/Cont (%)', 'Ocorr/Agend (%)']
            st.dataframe(df_sdr[col_sdr].sort_values(by='Leads', ascending=False), use_container_width=True, hide_index=True)

            st.divider()
            
            col_ef1, col_ef2 = st.columns(2)
            with col_ef1:
                st.write("**SDR: Lead x Ocorrido e Fechado**")
                sdr_ef_l = df_base[mask_L].groupby('Filtro_SDR').size().reset_index(name='Leads')
                sdr_ef_r = df_base[mask_R].groupby('Filtro_SDR').size().reset_index(name='Ocorridos')
                sdr_ef_f = df_base[mask_F].groupby('Filtro_SDR').size().reset_index(name='Fechados')
                ef_sdr = sdr_ef_l.merge(sdr_ef_r, on='Filtro_SDR', how='outer').merge(sdr_ef_f, on='Filtro_SDR', how='outer').fillna(0).rename(columns={'Filtro_SDR': 'SDR Responsável'})
                ef_sdr['Lead x Ocorrido (%)'] = ef_sdr.apply(lambda row: f"{(row['Ocorridos']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
                ef_sdr['Lead x Fechado (%)'] = ef_sdr.apply(lambda row: f"{(row['Fechados']/row['Leads']*100):.1f}%" if row['Leads'] > 0 else "-", axis=1)
                st.dataframe(ef_sdr[['SDR Responsável', 'Leads', 'Ocorridos', 'Fechados', 'Lead x Ocorrido (%)', 'Lead x Fechado (%)']].sort_values(by='Leads', ascending=False), use_container_width=True, hide_index=True)

            with col_ef2:
                st.write("**Closer: Ocorrido x Fechado**")
                mask_has_closer = df_base['Filtro_Closer'] != 'Sem Closer'
                cl_ef_r = df_base[mask_R & mask_has_closer].groupby('Filtro_Closer').size().reset_index(name='Ocorridos')
                cl_ef_f = df_base[mask_F & mask_has_closer].groupby('Filtro_Closer').size().reset_index(name='Fechados')
                ef_cl = cl_ef_r.merge(cl_ef_f, on='Filtro_Closer', how='outer').fillna(0).rename(columns={'Filtro_Closer': 'Closer Responsável'})
                ef_cl['Ocorrido x Fechado (%)'] = ef_cl.apply(lambda row: f"{(row['Fechados']/row['Ocorridos']*100):.1f}%" if row['Ocorridos'] > 0 else "-", axis=1)
                st.dataframe(ef_cl[['Closer Responsável', 'Ocorridos', 'Fechados', 'Ocorrido x Fechado (%)']].sort_values(by='Ocorridos', ascending=False), use_container_width=True, hide_index=True)

        elif pagina_selecionada == "📦 Visão de Produtos":
            st.title("Visão de Produtos (Aquisições)")
            st.info("Em breve: Análise detalhada dos SKUs vendidos.")
        elif pagina_selecionada == "💰 Receita":
            st.title("Receita (Aquisições)")
            st.info("Em breve: Ticket Médio, MRR e Análise de Faturamento B2B.")
        elif pagina_selecionada == "❌ Perdidos":
            st.title("Perdidos (Aquisições)")
            st.info("Em breve: Diagnóstico de perda de leads.")
        elif pagina_selecionada == "⚙️ Configurações":
            st.title("Configurações do Sistema")
            st.info("Gestão de bases e acessos.")

    # ==========================================
    # 4. LÓGICA DE CANAIS
    # ==========================================
    elif unidade_negocio == "[PFI] Comercial Canais":
        if pagina_selecionada == "📊 Dashboard Geral":
            st.markdown("<h1 style='font-size: 28px; margin-bottom: 4px;'>Dashboard Geral (Canais)</h1>", unsafe_allow_html=True)
            st.info("O ambiente de Canais está isolado com sucesso. Aguardando a extração do CSV 'bd-canais.csv' e mapeamento das colunas para replicar o motor analítico!")
        else:
            st.title(f"{pagina_selecionada} (Canais)")
            st.info("Ambiente estruturado e aguardando integração de dados.")

except Exception as e:
    st.error(f"Erro no processamento de dados: {e}")
