import streamlit as st
import pandas as pd

# 1. Configuração de Layout e Estilo (Mantendo o padrão aprovado)
st.set_page_config(page_title="Análise Comercial", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F0F8FF; }
    span[data-baseweb="tag"] { background-color: #1565C0 !important; color: white !important; }
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
    df['Data de criação'] = pd.to_datetime(df['Data de criação'], errors='coerce')
    df = df.dropna(subset=['Data de criação'])

    # Identificação de colunas flexíveis
    col_sdr = '[IS/SDR] SDR Responsável'
    col_closer = '[IS/Closer] Closer Responsável'
    col_contato = 'Contato Realizado' if 'Contato Realizado' in df.columns else df.columns[df.columns.str.contains('Contato Realizado')].tolist()[0]
    col_reuniao = '[IS/Closer] Reunião Ocorrida' if '[IS/Closer] Reunião Ocorrida' in df.columns else df.columns[df.columns.str.contains('Reunião Ocorrida')].tolist()[0]

    # --- BARRA LATERAL (Inclusão dos novos filtros) ---
    st.sidebar.header("Filtros")
    data_min, data_max = df['Data de criação'].min().date(), df['Data de criação'].max().date()
    periodo = st.sidebar.date_input("Data de criação", [data_min, data_max])
    
    tipos = sorted(df["[IS] Tipo de lead"].dropna().unique().tolist())
    filtro_tipo = st.sidebar.multiselect("Tipo de Lead", tipos, default=tipos)
    
    origens = sorted(df["[IS] Origem do lead"].dropna().unique().tolist())
    filtro_origem = st.sidebar.multiselect("Origem do Lead", origens, default=origens)

    # Novos Filtros de Pessoas
    sdrs_lista = sorted(df[col_sdr].dropna().unique().tolist())
    filtro_sdr = st.sidebar.multiselect("SDR Responsável", sdrs_lista, default=sdrs_lista)

    closers_lista = sorted(df[col_closer].dropna().unique().tolist())
    filtro_closer = st.sidebar.multiselect("Closer Responsável", closers_lista, default=closers_lista)

    # --- APLICAÇÃO DOS FILTROS ---
    if isinstance(periodo, (list, tuple)) and len(periodo) == 2:
        mask = (df['Data de criação'].dt.date >= periodo[0]) & \
               (df['Data de criação'].dt.date <= periodo[1]) & \
               (df["[IS] Tipo de lead"].isin(filtro_tipo)) & \
               (df["[IS] Origem do lead"].isin(filtro_origem)) & \
               (df[col_sdr].fillna('Sem SDR').isin(filtro_sdr if filtro_sdr else ['Sem SDR'])) & \
               (df[col_closer].fillna('Sem Closer').isin(filtro_closer if filtro_closer else ['Sem Closer']))
        df_f = df[mask].copy()
    else:
        df_f = df.copy()

    # --- TOPO: FUNIL EM CASCATA ---
    L, C = len(df_f), df_f[col_contato].notna().sum()
    A, R = df_f['[IS/SDR] Data do Agendamento'].notna().sum(), df_f[col_reuniao].notna().sum()
    F = df_f[df_f['Etapa do negócio'].isin(['Fechado', 'Pago'])].shape[0]

    st.title("📊 Dashboard Comercial")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Leads", L)
    m2.metric("Contato", C, f"{(C/L*100):.1f}% s/ Lead" if L>0 else "0%")
    m3.metric("Agendado", A, f"{(A/C*100):.1f}% s/ Contato" if C>0 else "0%")
    m4.metric("Ocorrido", R, f"{(R/A*100):.1f}% s/ Agend." if A>0 else "0%")
    m5.metric("Fechado", F, f"{(F/R*100):.1f}% s/ Ocorr." if R>0 else "0%")
    st.divider()

    # --- MEIO: ORIGEM E TIPO ---
    def criar_tabela_segmentada(df_filtrado, coluna_nome):
        tabela = df_filtrado.groupby(coluna_nome).agg(Leads=('ID do registro.', 'count')).reset_index()
        reunioes_cat = df_filtrado[df_filtrado[col_reuniao].notna()].groupby(coluna_nome)['ID do registro.'].count().reset_index()
        reunioes_cat.columns = [coluna_nome, 'Reunioes']
        fechados_cat = df_filtrado[df_filtrado['Etapa do negócio'].isin(['Fechado', 'Pago'])].groupby(coluna_nome)['ID do registro.'].count().reset_index()
        fechados_cat.columns = [coluna_nome, 'Fechados']
        tabela = tabela.merge(reunioes_cat, on=coluna_nome, how='left').merge(fechados_cat, on=coluna_nome, how='left').fillna(0)
        tabela['Lead x Reunião (%)'] = (tabela['Reunioes'] / tabela['Leads'] * 100).round(1).astype(str) + '%'
        tabela['Lead x Fechado (%)'] = (tabela['Fechados'] / tabela['Leads'] * 100).round(1).astype(str) + '%'
        return tabela[[coluna_nome, 'Leads', 'Lead x Reunião (%)', 'Lead x Fechado (%)']].sort_values(by='Leads', ascending=False)

    c_orig, c_tipo = st.columns(2)
    with c_orig:
        st.subheader("📍 Por Origem")
        st.dataframe(criar_tabela_segmentada(df_f, "[IS] Origem do lead"), use_container_width=True, hide_index=True)
    with c_tipo:
        st.subheader("🏷️ Por Tipo")
        st.dataframe(criar_tabela_segmentada(df_f, "[IS] Tipo de lead"), use_container_width=True, hide_index=True)
    st.divider()

    # --- PERFORMANCE SDR ---
    st.subheader("🏆 Performance SDR (Funil Inicial)")
    df_sdr_valid = df_f[df_f[col_sdr].notna()] # Apenas quem tem SDR
    perf_sdr = df_sdr_valid.groupby(col_sdr).agg(
        Leads=('ID do registro.', 'count'),
        Contatos=(col_contato, 'count'),
        Agendados=('[IS/SDR] Data do Agendamento', 'count'),
        Ocorridos=(col_reuniao, 'count')
    ).reset_index()
    perf_sdr['Cont/Lead'] = (perf_sdr['Contatos']/perf_sdr['Leads']*100).round(1).astype(str) + '%'
    perf_sdr['Agend/Cont'] = (perf_sdr['Agendados']/perf_sdr['Contatos']*100).round(1).astype(str) + '%'
    perf_sdr['Ocorr/Agend'] = (perf_sdr['Ocorridos']/perf_sdr['Agendados']*100).round(1).astype(str) + '%'
    st.dataframe(perf_sdr, use_container_width=True, hide_index=True)

    # --- PERFORMANCE CLOSER (Apenas com Closer Responsável) ---
    st.subheader("🤝 Performance Closer (Fechamento)")
    df_closer_valid = df_f[df_f[col_closer].notna()] # REMOVE VAZIOS CONFORME SOLICITADO
    if not df_closer_valid.empty:
        perf_closer = df_closer_valid.groupby(col_closer).agg(Ocorridos=(col_reuniao, 'count')).reset_index()
        fechados_closer = df_closer_valid[df_closer_valid['Etapa do negócio'].isin(['Fechado', 'Pago'])].groupby(col_closer)['ID do registro.'].count().reset_index()
        fechados_closer.columns = [col_closer, 'Fechados']
        perf_closer = perf_closer.merge(fechados_closer, on=col_closer, how='left').fillna(0)
        perf_closer['Fechado/Ocorrido'] = (perf_closer['Fechados']/perf_closer['Ocorridos']*100).round(1).astype(str) + '%'
        st.dataframe(perf_closer, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum Closer atribuído no período selecionado.")

    # --- EFICIÊNCIA FINAL ---
    st.divider()
    st.subheader("🎯 Eficiência de Conversão Final")
    col_s_f, col_c_f = st.columns(2)
    
    with col_s_f:
        st.write("**SDR: Lead para Ocorrido e Fechado**")
        efic_sdr = perf_sdr.copy()
        fech_sdr = df_f[df_f['Etapa do negócio'].isin(['Fechado', 'Pago'])].groupby(col_sdr)['ID do registro.'].count().reset_index()
        fech_sdr.columns = [col_sdr, 'Fechados']
        efic_sdr = efic_sdr.merge(fech_sdr, on=col_sdr, how='left').fillna(0)
        efic_sdr['Lead x Ocorrido (%)'] = (efic_sdr['Ocorridos']/efic_sdr['Leads']*100).round(1).astype(str) + '%'
        efic_sdr['Lead x Fechado (%)'] = (efic_sdr['Fechados']/efic_sdr['Leads']*100).round(1).astype(str) + '%'
        st.dataframe(efic_sdr[[col_sdr, 'Leads', 'Lead x Ocorrido (%)', 'Lead x Fechado (%)']], use_container_width=True, hide_index=True)

    with col_c_f:
        st.write("**Closer: Lead para Fechado**")
        if not df_closer_valid.empty:
            leads_por_closer = df_closer_valid.groupby(col_closer)['ID do registro.'].count().reset_index()
            leads_por_closer.columns = [col_closer, 'Leads Atribuídos']
            efic_closer = perf_closer.merge(leads_por_closer, on=col_closer, how='left').fillna(0)
            efic_closer['Lead x Fechado (%)'] = (efic_closer['Fechados']/efic_closer['Leads Atribuídos']*100).round(1).astype(str) + '%'
            st.dataframe(efic_closer[[col_closer, 'Leads Atribuídos', 'Lead x Fechado (%)']], use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Erro: {e}")
