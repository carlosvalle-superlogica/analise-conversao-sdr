import streamlit as st
import pandas as pd

# 1. Configuração de Layout e Estilo (Mantendo o original aprovado)
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

    # Nomes fixos das colunas
    col_sdr = '[IS/SDR] SDR Responsável'
    col_closer = '[IS/Closer] Closer Responsável'
    col_contato = 'Contato Realizado ' if 'Contato Realizado ' in df.columns else 'Contato Realizado'
    col_reuniao = '[IS/Closer] Reunião Ocorrida ' if '[IS/Closer] Reunião Ocorrida ' in df.columns else '[IS/Closer] Reunião Ocorrida'

    # --- BARRA LATERAL (Filtros) ---
    st.sidebar.header("Filtros")
    data_min, data_max = df['Data de criação'].min().date(), df['Data de criação'].max().date()
    periodo = st.sidebar.date_input("Data de criação", [data_min, data_max])
    
    filtro_tipo = st.sidebar.multiselect("Tipo de Lead", sorted(df["[IS] Tipo de lead"].dropna().unique()), default=df["[IS] Tipo de lead"].dropna().unique())
    filtro_origem = st.sidebar.multiselect("Origem do Lead", sorted(df["[IS] Origem do lead"].dropna().unique()), default=df["[IS] Origem do lead"].dropna().unique())
    
    # Filtros de Pessoas
    lista_sdr = sorted(df[col_sdr].dropna().unique())
    filtro_sdr = st.sidebar.multiselect("SDR Responsável", lista_sdr, default=lista_sdr)

    lista_closer = sorted(df[col_closer].dropna().unique())
    filtro_closer = st.sidebar.multiselect("Closer Responsável", lista_closer, default=lista_closer)

    # Aplicação do Filtro Global (Lógica estável)
    if isinstance(periodo, (list, tuple)) and len(periodo) == 2:
        mask = (df['Data de criação'].dt.date >= periodo[0]) & (df['Data de criação'].dt.date <= periodo[1]) & \
               (df["[IS] Tipo de lead"].isin(filtro_tipo)) & (df["[IS] Origem do lead"].isin(filtro_origem)) & \
               (df[col_sdr].fillna('Vazio').isin(filtro_sdr if filtro_sdr else ['Vazio'])) & \
               (df[col_closer].fillna('Vazio').isin(filtro_closer if filtro_closer else ['Vazio']))
        df_f = df[mask].copy()
    else:
        df_f = df.copy()

    # --- 2. FUNIL EM CASCATA NO TOPO (Mantido original) ---
    L, C = len(df_f), df_f[col_contato].notna().sum()
    A, R = df_f['[IS/SDR] Data do Agendamento'].notna().sum(), df_f[col_reuniao].notna().sum()
    F = df_f[df_f['Etapa do negócio'].isin(['Fechado', 'Pago'])].shape[0]

    st.title("📊 Dashboard de Conversão Comercial")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Leads", L)
    m2.metric("Contato", C, f"{(C/L*100):.1f}% s/ Lead" if L>0 else "0%")
    m3.metric("Agendado", A, f"{(A/C*100):.1f}% s/ Contato" if C>0 else "0%")
    m4.metric("Ocorrido", R, f"{(R/A*100):.1f}% s/ Agend." if A>0 else "0%")
    m5.metric("Fechado", F, f"{(F/R*100):.1f}% s/ Ocorr." if R>0 else "0%")
    st.divider()

    # --- 3. TABELAS ORIGEM/TIPO (Mantidas originais) ---
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

    c_a, c_b = st.columns(2)
    with c_a:
        st.subheader("📍 Por Origem")
        st.dataframe(criar_tabela_segmentada(df_f, "[IS] Origem do lead"), use_container_width=True, hide_index=True)
    with c_b:
        st.subheader("🏷️ Por Tipo")
        st.dataframe(criar_tabela_segmentada(df_f, "[IS] Tipo de lead"), use_container_width=True, hide_index=True)
    st.divider()

    # --- 4. NOVAS VISÕES (SDR E CLOSER) ---
    st.subheader("🏆 Performance por Equipe")
    cp1, cp2 = st.columns(2)

    with cp1:
        st.write("**Performance SDR**")
        df_sdr_perf = df_f.groupby(col_sdr).agg(
            Leads=('ID do registro.', 'count'),
            Contatos=(col_contato, 'count'),
            Agendados=('[IS/SDR] Data do Agendamento', 'count'),
            Ocorridos=(col_reuniao, 'count')
        ).reset_index()
        df_sdr_perf['Cont/Lead %'] = (df_sdr_perf['Contatos']/df_sdr_perf['Leads']*100).round(1).astype(str) + '%'
        df_sdr_perf['Agend/Cont %'] = (df_sdr_perf['Agendados']/df_sdr_perf['Contatos']*100).round(1).astype(str) + '%'
        df_sdr_perf['Ocorr/Agend %'] = (df_sdr_perf['Ocorridos']/df_sdr_perf['Agendados']*100).round(1).astype(str) + '%'
        st.dataframe(df_sdr_perf, use_container_width=True, hide_index=True)

    with cp2:
        st.write("**Performance Closer (Sem nomes vazios)**")
        # REGRA: Apenas registros onde o Closer Responsável NÃO é nulo
        df_closer_only = df_f[df_f[col_closer].notna()].copy()
        if not df_closer_only.empty:
            df_cl_perf = df_closer_only.groupby(col_closer).agg(Ocorridos=(col_reuniao, 'count')).reset_index()
            f_cl = df_closer_only[df_closer_only['Etapa do negócio'].isin(['Fechado', 'Pago'])].groupby(col_closer)['ID do registro.'].count().reset_index()
            f_cl.columns = [col_closer, 'Fechados']
            df_cl_perf = df_cl_perf.merge(f_cl, on=col_closer, how='left').fillna(0)
            df_cl_perf['Fechado/Ocorrido %'] = (df_cl_perf['Fechados']/df_cl_perf['Ocorridos']*100).round(1).astype(str) + '%'
            st.dataframe(df_cl_perf, use_container_width=True, hide_index=True)
        else:
            st.info("Filtre um Closer Responsável para ver os dados.")

    st.subheader("🎯 Eficiência Geral")
    ce1, ce2 = st.columns(2)

    with ce1:
        st.write("**Eficiência SDR: Impacto no Lead**")
        ef_sdr = df_sdr_perf[['[IS/SDR] SDR Responsável', 'Leads', 'Ocorridos']].copy()
        f_s_total = df_f[df_f['Etapa do negócio'].isin(['Fechado', 'Pago'])].groupby(col_sdr)['ID do registro.'].count().reset_index()
        f_s_total.columns = [col_sdr, 'Fechados']
        ef_sdr = ef_sdr.merge(f_s_total, on=col_sdr, how='left').fillna(0)
        ef_sdr['Lead x Ocorrido %'] = (ef_sdr['Ocorridos']/ef_sdr['Leads']*100).round(1).astype(str) + '%'
        ef_sdr['Lead x Fechado %'] = (ef_sdr['Fechados']/ef_sdr['Leads']*100).round(1).astype(str) + '%'
        st.dataframe(ef_sdr[[col_sdr, 'Leads', 'Lead x Ocorrido %', 'Lead x Fechado %']], use_container_width=True, hide_index=True)

    with ce2:
        st.write("**Eficiência Closer: Lead para Fechado**")
        if not df_closer_only.empty:
            ef_cl = df_closer_only.groupby(col_closer).agg(Leads_Atrib=('ID do registro.', 'count')).reset_index()
            f_cl_total = df_closer_only[df_closer_only['Etapa do negócio'].isin(['Fechado', 'Pago'])].groupby(col_closer)['ID do registro.'].count().reset_index()
            f_cl_total.columns = [col_closer, 'Fechados']
            ef_cl = ef_cl.merge(f_cl_total, on=col_closer, how='left').fillna(0)
            ef_cl['Lead x Fechado %'] = (ef_cl['Fechados']/ef_cl['Leads_Atrib']*100).round(1).astype(str) + '%'
            st.dataframe(ef_cl[[col_closer, 'Leads_Atrib', 'Lead x Fechado %']], use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Erro ao processar colunas. Verifique o CSV: {e}")
