import streamlit as st
import pandas as pd

# 1. Configuração de Layout e Estilo (Mantido original)
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

    # Nomes das colunas para evitar erros
    col_sdr = '[IS/SDR] SDR Responsável'
    col_closer = '[IS/Closer] Closer Responsável'
    col_contato = 'Contato Realizado ' if 'Contato Realizado ' in df.columns else 'Contato Realizado'
    col_reuniao = '[IS/Closer] Reunião Ocorrida ' if '[IS/Closer] Reunião Ocorrida ' in df.columns else '[IS/Closer] Reunião Ocorrida'

    # Barra Lateral (Adicionando filtros de pessoas sem alterar os de data/tipo/origem)
    st.sidebar.header("Filtros")
    data_min, data_max = df['Data de criação'].min().date(), df['Data de criação'].max().date()
    periodo = st.sidebar.date_input("Data de criação", [data_min, data_max])
    
    tipos = sorted(df["[IS] Tipo de lead"].dropna().unique().tolist())
    filtro_tipo = st.sidebar.multiselect("Tipo de Lead", tipos, default=tipos)
    
    origens = sorted(df["[IS] Origem do lead"].dropna().unique().tolist())
    filtro_origem = st.sidebar.multiselect("Origem do Lead", origens, default=origens)

    # Novos filtros de pessoas
    sdrs = sorted(df[col_sdr].dropna().unique().tolist())
    filtro_sdr = st.sidebar.multiselect("SDR Responsável", sdrs, default=sdrs)

    closers = sorted(df[col_closer].dropna().unique().tolist())
    filtro_closer = st.sidebar.multiselect("Closer Responsável", closers, default=closers)

    # Aplicação do Filtro (Lógica expandida com segurança)
    if isinstance(periodo, (list, tuple)) and len(periodo) == 2:
        mask = (df['Data de criação'].dt.date >= periodo[0]) & (df['Data de criação'].dt.date <= periodo[1]) & \
               (df["[IS] Tipo de lead"].isin(filtro_tipo)) & (df["[IS] Origem do lead"].isin(filtro_origem)) & \
               (df[col_sdr].fillna('Vazio').isin(filtro_sdr if filtro_sdr else ['Vazio'])) & \
               (df[col_closer].fillna('Vazio').isin(filtro_closer if filtro_closer else ['Vazio']))
        df_f = df[mask].copy()
    else:
        df_f = df.copy()

    # 2. LÓGICA DE CASCATA NO TOPO (Mantida original)
    L = len(df_f)
    C = df_f[col_contato].notna().sum()
    A = df_f['[IS/SDR] Data do Agendamento'].notna().sum()
    R = df_f[col_reuniao].notna().sum()
    F = df_f[df_f['Etapa do negócio'].isin(['Fechado', 'Pago'])].shape[0]

    st.title("📊 Dashboard de Conversão Comercial")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Leads", L)
    m2.metric("Contato", C, f"{(C/L*100):.1f}% s/ Lead" if L>0 else "0%")
    m3.metric("Agendado", A, f"{(A/C*100):.1f}% s/ Contato" if C>0 else "0%")
    m4.metric("Ocorrido", R, f"{(R/A*100):.1f}% s/ Agend." if A>0 else "0%")
    m5.metric("Fechado", F, f"{(F/R*100):.1f}% s/ Ocorr." if R>0 else "0%")

    st.divider()

    # 3. TABELAS ORIGEM/TIPO (Mantidas originais)
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

    # 4. NOVAS VISÕES (SDR e Closer)
    st.subheader("🏆 Performance por Equipe")
    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.write("**SDR: Leads, Contato, Agendado e Ocorrido**")
        df_sdr = df_f.groupby(col_sdr).agg(
            Leads=('ID do registro.', 'count'),
            Contatos=(col_contato, 'count'),
            Agendados=('[IS/SDR] Data do Agendamento', 'count'),
            Ocorridos=(col_reuniao, 'count')
        ).reset_index()
        df_sdr['Cont/Lead %'] = (df_sdr['Contatos']/df_sdr['Leads']*100).round(1).astype(str) + '%'
        df_sdr['Agend/Cont %'] = (df_sdr['Agendados']/df_sdr['Contatos']*100).round(1).astype(str) + '%'
        df_sdr['Ocorr/Agend %'] = (df_sdr['Ocorridos']/df_sdr['Agendados']*100).round(1).astype(str) + '%'
        st.dataframe(df_sdr, use_container_width=True, hide_index=True)

    with col_p2:
        st.write("**Closer: Ocorrido e Fechado (Somente com Responsável)**")
        # Regra solicitada: Apenas registros com Closer Responsável preenchido
        df_closer_limpo = df_f[df_f[col_closer].notna()].copy()
        if not df_closer_limpo.empty:
            df_cl = df_closer_limpo.groupby(col_closer).agg(Ocorridos=(col_reuniao, 'count')).reset_index()
            f_cl = df_closer_limpo[df_closer_limpo['Etapa do negócio'].isin(['Fechado', 'Pago'])].groupby(col_closer)['ID do registro.'].count().reset_index()
            f_cl.columns = [col_closer, 'Fechados']
            df_cl = df_cl.merge(f_cl, on=col_closer, how='left').fillna(0)
            df_cl['Fechado/Ocorrido %'] = (df_cl['Fechados']/df_cl['Ocorridos']*100).round(1).astype(str) + '%'
            st.dataframe(df_cl, use_container_width=True, hide_index=True)
        else:
            st.info("Selecione um Closer com dados atribuídos.")

    st.subheader("🎯 Eficiência Geral (Impacto no Lead)")
    col_e1, col_e2 = st.columns(2)

    with col_e1:
        st.write("**SDR: Lead para Ocorrido e Lead para Fechado**")
        ef_sdr = df_sdr[['[IS/SDR] SDR Responsável', 'Leads', 'Ocorridos']].copy()
        f_s = df_f[df_f['Etapa do negócio'].isin(['Fechado', 'Pago'])].groupby(col_sdr)['ID do registro.'].count().reset_index()
        f_s.columns = [col_sdr, 'Fechados']
        ef_sdr = ef_sdr.merge(f_s, on=col_sdr, how='left').fillna(0)
        ef_sdr['Lead x Ocorrido %'] = (ef_sdr['Ocorridos']/ef_sdr['Leads']*100).round(1).astype(str) + '%'
        ef_sdr['Lead x Fechado %'] = (ef_sdr['Fechados']/ef_sdr['Leads']*100).round(1).astype(str) + '%'
        st.dataframe(ef_sdr[[col_sdr, 'Leads', 'Lead x Ocorrido %', 'Lead x Fechado %']], use_container_width=True, hide_index=True)

    with col_e2:
        st.write("**Closer: Lead para Fechado**")
        if not df_closer_limpo.empty:
            ef_cl = df_closer_limpo.groupby(col_closer).agg(Leads_Atrib=('ID do registro.', 'count')).reset_index()
            f_cl2 = df_closer_limpo[df_closer_limpo['Etapa do negócio'].isin(['Fechado', 'Pago'])].groupby(col_closer)['ID do registro.'].count().reset_index()
            f_cl2.columns = [col_closer, 'Fechados']
            ef_cl = ef_cl.merge(f_cl2, on=col_closer, how='left').fillna(0)
            ef_cl['Lead x Fechado %'] = (ef_cl['Fechados']/ef_cl['Leads_Atrib']*100).round(1).astype(str) + '%'
            st.dataframe(ef_cl, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Erro: {e}")
