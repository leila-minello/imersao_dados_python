import streamlit as st
import pandas as pd
import plotly.express as px

# configuração da página
st.set_page_config(
    page_title="Dashboard de Salários",
    page_icon="📊",
    layout="wide"
)

# carregando os dados
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# criando a sidebar
st.sidebar.header("🔍 Filtros de dados")

# filtros para visualização
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de contratação", contratos_disponiveis, default=contratos_disponiveis)

tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# filtragem do dataframe, para quando o usuário selecionar eles serem atualizados automaticamente na visualização
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# conteúdo principal da página
st.title("📑 Dashboard de Análise de Salários")
st.markdown("Nessa página você vai poder explorar dados salariais da área de dados nos últimos anos e filtrar conforme quiser!")

# métricas
st.subheader("Métricas gerais (Salário anual em USD)")

# função para caso nao houver filtros selecionados
if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_reg = df_filtrado.shape[0]
    cargo_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_maximo, salario_maximo, total_reg, cargo_frequente = 0, 0, 0, ""

# definição das colunas com as métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_reg:,}")
col4.metric("Cargo mais frequente", cargo_frequente)

st.markdown("---")

# visualização com gráficos

st.subheader("📈 Gráficos")

col_graf1, col_graf2 = st.columns(2)

# gráfico de barra dos top10 cargos com maior salário médio
with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h', # horizontal
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibição no gráfico de cargos.")

# histograma de distribuição de salários
with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição salarial anual",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibição no histograma de distribuição.")

col_graf3, col_graf4 = st.columns(2)

# gráfico de pizza de proporção dos tipos de trabalho
with col_graf3:
    if not df_filtrado.empty:
        remoto_cont = df_filtrado['remoto'].value_counts().reset_index()
        remoto_cont.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_cont,
            names='tipo_trabalho',
            values='quantidade',
            title="Proporção dos tipos de trabalho",
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibição no gráfico de tipos de trabalho.")

# gráfico de média salarial

with col_graf4:
    if not df_filtrado.empty:
        df_cientista = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_pais_ds =  df_cientista.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_pais_ds,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibição no gráfico de países.")

st.subheader("Dados detalhados")
st.dataframe(df_filtrado)