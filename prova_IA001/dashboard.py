from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ===========================================================================
# Textos da interface
# Todos os rótulos exibidos ficam aqui. Os que têm {chaves} são modelos
# preenchidos com .format() no ponto de uso.
# ===========================================================================

# Página e cabeçalho
TITULO_ABA = "Airbnb Zona Sul - Rio"
TITULO_PAGINA = "Airbnb na Zona Sul do Rio - onde está a oferta e quem a controla"
TEXTO_INTRODUCAO = (
    "Anúncios de hospedagem do Airbnb nos 18 bairros da **Zona Sul** do Rio de Janeiro "
    "(Área de Planejamento 2.1). Use os filtros ao lado para escolher bairros e "
    "categorias de anunciante. Todos os gráficos respondem aos mesmos filtros."
)
PREFIXO_LEITURA = "**Leitura:** "

# Barra lateral - filtros
TITULO_FILTROS = "Filtros disponíveis"
FILTRO_BAIRROS = "Bairros da Zona Sul"
AJUDA_BAIRROS = "Ordenados pelo número de anúncios."
FILTRO_CATEGORIAS = "Categorias de anunciante"
AJUDA_CATEGORIAS = (
    "Profissional = imóvel inteiro de anfitrião com mais de um anúncio. "
    "Individual = anfitrião com um único anúncio. "
    "Outros = anfitrião com vários anúncios, mas oferecendo quarto (privativo, compartilhado ou de hotel)."
)
FILTRO_TOP_N = "Bairros no gráfico de composição"
AJUDA_TOP_N = "Quantos bairros com mais anúncios exibir na comparação entre profissionais e individuais."
FILTRO_MAPA = "Tipo de mapa"
MAPA_PONTOS = "Pontos (um por anúncio)"
MAPA_DENSIDADE = "Densidade (mapa de calor)"
TEXTO_FONTE = (
    "Fonte: Inside Airbnb - Rio de Janeiro - listings.csv. "
    "Excluídos 14 anúncios sem identificação do anfitrião. A Zona Sul é definida pela lista "
    "de bairros da AP 2.1 da Prefeitura do Rio, pois o arquivo não traz a região."
)
AVISO_SEM_DADOS = (
    "Nenhum anúncio encontrado para a combinação de filtros selecionada. "
    "Selecione ao menos um bairro e uma categoria."
)

# Indicadores (KPIs)
KPI_ANUNCIOS = "Anúncios na seleção"
KPI_MAIOR_BAIRRO = "Fatia do maior bairro ({bairro})"
KPI_PROFISSIONAL = "Oferta profissional"
KPI_INDIVIDUAL = "Oferta individual"

# Seções
TITULO_P1 = "P1 - Quais bairros concentram a oferta na Zona Sul?"
TITULO_P2 = "P2 - Profissionais ou individuais: quem oferta nos bairros com mais anúncios?"
TITULO_TABELA = "Ver tabela por bairro"

# Gráfico 1 - ranking de bairros
G1_TITULO = "Anúncios por bairro da Zona Sul"
G1_EIXO_X = "Número de anúncios"
G1_EIXO_Y = "Bairro"
G1_ROTULO = "{n} · {pct} ({acum} acum.)"
G1_LEITURA = (
    "**{bairro}** tem {n} anúncios, {pct} da seleção. Os {k} maiores bairros somam "
    "{pct_k} da oferta; são necessários {n80} de {total} bairros para chegar a 80%."
)

# Gráfico 2 - mapa
G2_TITULO = "Localização dos anúncios na Zona Sul por categoria de anunciante"
G2_TITULO_DENSIDADE = "Densidade de anúncios na Zona Sul"
G2_LEGENDA = "Categoria de anunciante"
G2_LEITURA = (
    "Cada ponto é um anúncio. "
    "A oferta se adensa na faixa de praia. Clique numa categoria da legenda."
)

# Gráfico 3 - composição por bairro
G3_TITULO = "Composição da oferta por categoria de anunciante nos {k} bairros com mais anúncios"
G3_EIXO_X = "Participação na oferta do bairro (%)"
G3_EIXO_Y = "Bairro (número de anúncios)"
G3_LEGENDA = "Categoria de anunciante"
G3_LEITURA = (
    "Maior participação profissional: **{max_b}** ({max_p}). Menor: **{min_b}** ({min_p}). "
    "Percentuais calculados entre as categorias selecionadas."
)

# Tabela
COL_BAIRRO = "Bairro"
COL_ANUNCIOS = "Anúncios"
COL_PCT = "% da seleção"

# ===========================================================================
# Definições da análise
# ===========================================================================

CAMINHO_DADOS = Path(__file__).parent / "listings.csv"

# Bairros da Área de Planejamento 2.1 (Zona Sul) da Prefeitura do Rio
ZONA_SUL = [
    "Botafogo", "Catete", "Copacabana", "Cosme Velho", "Flamengo", "Gávea",
    "Glória", "Humaitá", "Ipanema", "Jardim Botânico", "Lagoa", "Laranjeiras",
    "Leblon", "Leme", "Rocinha", "São Conrado", "Urca", "Vidigal",
]

PROFISSIONAL = "Profissional"
INDIVIDUAL = "Individual"
OUTROS = "Outros"
CATEGORIAS = [PROFISSIONAL, INDIVIDUAL, OUTROS]

# Cor fixa por categoria (não muda quando um filtro remove categorias)
CORES = {PROFISSIONAL: "#2a78d6", INDIVIDUAL: "#eb6834", OUTROS: "#9a9890"}
COR_BARRA = "#2a78d6"

CENTRO_MAPA = {"lat": -22.97, "lon": -43.205}
ZOOM_MAPA = 12


# ===========================================================================
# Funções auxiliares
# ===========================================================================

def formatar_inteiro(valor):
    return f"{valor:,.0f}".replace(",", ".")


def formatar_percentual(valor):
    return f"{valor:.1%}".replace(".", ",")


def exibir_leitura(texto):
    st.markdown(PREFIXO_LEITURA + texto)


def preparar(df):
    """Recorta a Zona Sul e classifica cada anúncio por categoria de anunciante."""
    df = df.dropna(subset=["host_id"])
    zs = df[df["neighbourhood"].isin(ZONA_SUL)].copy()
    inteiro = zs["room_type"] == "Entire home/apt"
    varios = zs["calculated_host_listings_count"] > 1
    zs["categoria"] = np.select(
        [inteiro & varios, ~varios],
        [PROFISSIONAL, INDIVIDUAL],
        default=OUTROS,
    )
    zs["categoria"] = pd.Categorical(zs["categoria"], categories=CATEGORIAS)
    return zs


@st.cache_data
def carregar_dados(caminho=CAMINHO_DADOS):
    return preparar(pd.read_csv(caminho))


def grafico_ranking(dados):
    contagem = dados["neighbourhood"].value_counts()
    tabela = pd.DataFrame({"bairro": contagem.index, "n": contagem.values})
    tabela["pct"] = tabela["n"] / tabela["n"].sum()
    tabela["pct_acum"] = tabela["pct"].cumsum()
    tabela["rotulo"] = [
        G1_ROTULO.format(n=formatar_inteiro(n), pct=formatar_percentual(p), acum=formatar_percentual(a))
        for n, p, a in zip(tabela["n"], tabela["pct"], tabela["pct_acum"])
    ]
    fig = px.bar(
        tabela, x="n", y="bairro", orientation="h", text="rotulo",
        title=G1_TITULO,
        labels={"n": G1_EIXO_X, "bairro": G1_EIXO_Y},
        custom_data=["pct", "pct_acum"],
    )
    fig.update_traces(
        marker_color=COR_BARRA, textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>%{x:,} anúncios<br>%{customdata[0]:.1%} da seleção<br>%{customdata[1]:.1%} acumulado<extra></extra>",
    )
    fig.update_layout(
        yaxis={"categoryorder": "total ascending", "title_standoff": 12, "automargin": True},
        height=max(320, 28 * len(tabela) + 120),
        margin={"l": 150, "r": 190},
        separators=",.",
    )
    return fig, tabela


def grafico_mapa(dados, tipo):
    if tipo == MAPA_DENSIDADE:
        fig = px.density_map(
            dados, lat="latitude", lon="longitude", radius=6,
            center=CENTRO_MAPA, zoom=ZOOM_MAPA, map_style="open-street-map",
            title=G2_TITULO_DENSIDADE, color_continuous_scale="Blues",
        )
        fig.update_layout(coloraxis_colorbar={"title": "Densidade"})
    else:
        fig = px.scatter_map(
            dados, lat="latitude", lon="longitude", color="categoria",
            color_discrete_map=CORES, category_orders={"categoria": CATEGORIAS},
            hover_name="name",
            hover_data={"neighbourhood": True, "calculated_host_listings_count": True,
                        "room_type": True, "latitude": False, "longitude": False},
            labels={"categoria": G2_LEGENDA, "neighbourhood": "Bairro",
                    "calculated_host_listings_count": "Anúncios do anfitrião",
                    "room_type": "Tipo"},
            center=CENTRO_MAPA, zoom=ZOOM_MAPA, map_style="open-street-map",
            title=G2_TITULO, opacity=0.35,
        )
        fig.update_traces(marker={"size": 4})
        fig.update_layout(legend={"orientation": "h", "y": -0.02, "itemsizing": "constant"})
    fig.update_layout(height=600, margin={"l": 0, "r": 0, "b": 0})
    return fig


def grafico_composicao(dados, top_n):
    contagem = dados["neighbourhood"].value_counts()
    maiores = contagem.head(top_n).index
    sub = dados[dados["neighbourhood"].isin(maiores)]
    pct = pd.crosstab(sub["neighbourhood"], sub["categoria"], normalize="index")
    presentes = set(sub["categoria"].unique())
    pct = pct.reindex(columns=[c for c in CATEGORIAS if c in presentes])
    ordem = pct.sort_values(pct.columns[0]).index if len(pct.columns) else pct.index
    rotulos = {b: f"{b} ({formatar_inteiro(contagem[b])})" for b in pct.index}
    longo = (
        pct.loc[ordem].rename(index=rotulos)
        .reset_index().melt(id_vars="neighbourhood", var_name="categoria", value_name="pct")
    )
    fig = px.bar(
        longo, x="pct", y="neighbourhood", color="categoria", orientation="h",
        color_discrete_map=CORES, category_orders={"categoria": CATEGORIAS},
        title=G3_TITULO.format(k=len(pct)),
        labels={"pct": G3_EIXO_X, "neighbourhood": G3_EIXO_Y, "categoria": G3_LEGENDA},
        text="pct",
    )
    fig.update_traces(
        texttemplate="%{text:.0%}", textposition="inside",
        marker_line_color="white", marker_line_width=2,
        hovertemplate="<b>%{y}</b><br>%{fullData.name}: %{x:.1%}<extra></extra>",
    )
    fig.update_layout(
        barmode="stack", xaxis={"tickformat": ".0%", "range": [0, 1]},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.0, "x": 0},
        height=max(320, 45 * len(pct) + 180), separators=",.",
        margin={"l": 190, "t": 110},
        yaxis={"title_standoff": 12, "automargin": True},
    )
    return fig, pct


# ===========================================================================
# Aplicativo
# ===========================================================================

st.set_page_config(page_title=TITULO_ABA, layout="wide")
st.title(TITULO_PAGINA)
st.markdown(TEXTO_INTRODUCAO)

df = carregar_dados()

st.sidebar.header(TITULO_FILTROS)
bairros_ordenados = df["neighbourhood"].value_counts().index.tolist()
bairros = st.sidebar.multiselect(
    FILTRO_BAIRROS, bairros_ordenados, default=bairros_ordenados, help=AJUDA_BAIRROS
)
categorias = st.sidebar.multiselect(
    FILTRO_CATEGORIAS, CATEGORIAS, default=CATEGORIAS, help=AJUDA_CATEGORIAS
)
top_n = st.sidebar.slider(
    FILTRO_TOP_N, min_value=2, max_value=len(ZONA_SUL), value=5, help=AJUDA_TOP_N
)
tipo_mapa = st.sidebar.radio(FILTRO_MAPA, [MAPA_PONTOS, MAPA_DENSIDADE])

dados = df[df["neighbourhood"].isin(bairros) & df["categoria"].isin(categorias)]

if dados.empty:
    st.warning(AVISO_SEM_DADOS)
    st.stop()

# KPIs
total = len(dados)
contagem = dados["neighbourhood"].value_counts()
participacao = dados["categoria"].value_counts(normalize=True)
k1, k2, k3, k4 = st.columns(4)
k1.metric(KPI_ANUNCIOS, formatar_inteiro(total))
k2.metric(KPI_MAIOR_BAIRRO.format(bairro=contagem.index[0]), formatar_percentual(contagem.iloc[0] / total))
k3.metric(KPI_PROFISSIONAL, formatar_percentual(participacao.get(PROFISSIONAL, 0)))
k4.metric(KPI_INDIVIDUAL, formatar_percentual(participacao.get(INDIVIDUAL, 0)))

# P1
st.header(TITULO_P1)
col_ranking, col_mapa = st.columns([2, 3])
with col_ranking:
    fig, tabela = grafico_ranking(dados)
    st.plotly_chart(fig, width="stretch")
    k = min(5, len(tabela))
    exibir_leitura(G1_LEITURA.format(
        bairro=tabela["bairro"].iloc[0],
        n=formatar_inteiro(tabela["n"].iloc[0]),
        pct=formatar_percentual(tabela["n"].iloc[0] / total),
        k=k, pct_k=formatar_percentual(tabela["pct_acum"].iloc[k - 1]),
        n80=int((tabela["pct_acum"] < 0.8).sum()) + 1, total=len(tabela),
    ))
with col_mapa:
    st.plotly_chart(grafico_mapa(dados, tipo_mapa), width="stretch")
    exibir_leitura(G2_LEITURA)

# P2
st.header(TITULO_P2)
fig, pct = grafico_composicao(dados, top_n)
st.plotly_chart(fig, width="stretch")
if PROFISSIONAL in pct.columns:
    prof = pct[PROFISSIONAL]
    exibir_leitura(G3_LEITURA.format(
        max_b=prof.idxmax(), max_p=formatar_percentual(prof.max()),
        min_b=prof.idxmin(), min_p=formatar_percentual(prof.min()),
    ))

with st.expander(TITULO_TABELA):
    tabela_bairros = pd.crosstab(dados["neighbourhood"], dados["categoria"])
    tabela_bairros.insert(0, COL_ANUNCIOS, tabela_bairros.sum(axis=1))
    tabela_bairros.insert(1, COL_PCT, (tabela_bairros[COL_ANUNCIOS] / total * 100).round(1))
    tabela_bairros = tabela_bairros.sort_values(COL_ANUNCIOS, ascending=False)
    tabela_bairros.index.name = COL_BAIRRO
    st.dataframe(tabela_bairros, width="stretch")

st.caption(TEXTO_FONTE)
