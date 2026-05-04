import streamlit as st
import pandas as pd

# 1. Configuração de Layout e Estilo (Estável e Aprovado)
st.set_page_config(page_title="Análise SDR", layout="wide")

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

    # Identificação de colunas
    col_sdr = '[IS/SDR] SDR Responsável'
    col_closer = '[IS/Closer] Closer Responsável'
    col_contato = 'Contato Realizado' if 'Contato Realizado' in df.columns else df.columns[df.columns.str.contains('Contato Realizado')].tolist()[0]
    col_reuniao = '[IS/Closer] Reunião Ocorrida' if '[IS/Closer] Reunião Ocorrida' in df.columns else df.columns[df.columns.str.contains('Reunião Ocorrida')].tolist()[0]

    # --- BARRA LATERAL ---
    st.sidebar.header("Filtros")
    data_min, data_max = df['Data de criação'].min().date(), df['Data de criação'].max().date()
    periodo = st.sidebar.date_input("Data de criação", [data_min, data_max])
    
    tipos = sorted(df["[IS] Tipo de lead"].dropna().unique().tolist())
    filtro_tipo = st.sidebar.multiselect("Tipo de Lead", tipos, default=tipos)
    
    origens = sorted(df["[IS] Origem do lead"].dropna().unique().tolist())
    filtro_origem = st.sidebar.multiselect("Origem do Lead", origens, default=origens)

    sdrs_lista = sorted(df[col_sdr].dropna().unique().tolist())
    filtro_sdr = st.sidebar.multiselect("SDR Responsável", sdrs_lista, default=sdrs_lista)

    closers_lista = sorted(df[col_closer].dropna().unique().tolist())
    filtro_closer = st.sidebar.multiselect("Closer Responsável", closers_lista, default=closers_lista)

    # Aplicação do Filtro Global (Seguro)
    if isinstance(periodo, (list, tuple)) and len(periodo) == 2:
        mask = (df['Data de criação'].dt.date >= periodo[0]) & \
               (df['Data de criação'].dt.date <= periodo[1]) & \
               (df["[IS] Tipo de lead"].isin(filtro_tipo)) & \
               (df["[IS] Origem do lead"].isin(filtro_origem)) & \
               (df[col_sdr].fillna('Vazio').isin(filtro_sdr if filtro_sdr else ['Vazio'])) & \
               (df[col_closer].fillna('Vazio').isin(filtro_closer if filtro_closer else ['Vazio']))
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

    # --- ORIGEM E TIPO ---
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

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📍 Por Origem")
        st.dataframe(criar_tabela_segmentada(df_f, "[IS] Origem do lead"), use_container_width=True, hide_index=True)
    with c2:
        st.subheader("🏷️ Por Tipo")
        st.dataframe(criar_tabela_segmentada(df_f, "[IS] Tipo de lead"), use_container_width=True, hide_index=True)
    st.divider()

    # --- PERFORMANCE SDR ---
    st.subheader("🏆 Performance SDR (Funil Inicial)")
    perf_sdr = df_f.groupby(col_sdr).agg(
        Leads=('ID do registro.', 'count'),
        Contatos=(col_contato, 'count'),
        Agendados=('[IS/SDR] Data do Agendamento', 'count'),
        Ocorridos=(col_reuniao, 'count')
    ).reset_index()
    perf_sdr['Cont/Lead'] = (perf_sdr['Contatos']/perf_sdr['Leads']*100).round(1).astype(str) + '%'
    perf_sdr['Agend/Cont'] = (perf_sdr['Agendados']/perf_sdr['Contatos']*100).round(1).astype(str) + '%'
    perf_sdr['Ocorr/Agend'] = (perf_sdr['Ocorridos']/perf_sdr['Agendados']*100).round(1).astype(str) + '%'
    st.dataframe(perf_sdr, use_container_width=True, hide_index=True)

    # --- PERFORMANCE CLOSER (Aqui aplicamos o filtro de NÃO VAZIO) ---
    st.subheader("🤝 Performance Closer (Fechamento)")
    df_closer_f = df_f[df_f[col_closer].notna()].copy() # Apenas Closer com nome
    if not df_closer_f.empty:
        perf_closer = df_closer_f.groupby(col_closer).agg(Ocorridos=(col_reuniao, 'count')).reset_index()
        fech_cl = df_closer_f[df_closer_f['Etapa do negócio'].isin(['Fechado', 'Pago'])].groupby(col_closer)['ID do registro.'].count().reset_index()
        fech_cl.columns = [col_closer, 'Fechados']
        perf_closer = perf_closer.merge(fech_cl, on=col_closer, how='left').fillna(0)
        perf_closer['Fechado/Ocorrido'] = (perf_closer['Fechados']/perf_closer['Ocorridos']*100).round(1).astype(str) + '%'
        st.dataframe(perf_closer, use_container_width=True, hide_index=True)

    # --- EFICIÊNCIA FINAL ---
    st.divider()
    st.subheader("🎯 Eficiência de Conversão Final")
    cf1, cf2 = st.columns(2)
    with cf1:
        st.write("**SDR: Impacto Final**")
        efic_sdr = perf_sdr.copy()
        fech_s = df_f[df_f['Etapa do negócio'].isin(['Fechado', 'Pago'])].groupby(col_sdr)['ID do registro.'].count().reset_index()
        fech_s.columns = [col_sdr, 'Fechados']
        efic_sdr = efic_sdr.merge(fech_s, on=col_sdr, how='left').fillna(0)
        efic_sdr['Lead x Ocorrido (%)'] = (efic_sdr['Ocorridos']/efic_sdr['Leads']*100).round(1).astype(str) + '%'
        efic_sdr['Lead x Fechado (%)'] = (efic_sdr['Fechados']/efic_sdr['Leads']*100).round(1).astype(str) + '%'
        st.dataframe(efic_sdr[[col_sdr, 'Leads', 'Lead x Ocorrido (%)', 'Lead x Fechado (%)']], use_container_width=True, hide_index=True)
    with cf2:
        st.write("**Closer: Impacto Final**")
        if not df_closer_f.empty:
            leads_c = df_closer_f.groupby(col_closer)['ID do registro.'].count().reset_index()
            leads_c.columns = [col_closer, 'Leads Atribuídos']
            efic_closer = perf_closer.merge(leads_c, on=col_closer, how='left').fillna(0)
            efic_closer['Lead x Fechado (%)'] = (efic_closer['Fechados']/efic_closer['Leads Atribuídos']*100).round(1).astype(str) + '%'
            st.dataframe(efic_closer[[col_closer, 'Leads Atribuídos', 'Lead x Fechado (%)']], use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Erro: {e}")
