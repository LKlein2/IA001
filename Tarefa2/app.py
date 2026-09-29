from pathlib import Path

import altair as alt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Caminho do CSV relativo a este arquivo: IA001/Real/Ano-2025.csv
CAMINHO_DADOS = Path(__file__).resolve().parent.parent / "Real" / "Ano-2025.csv"

# Somente as colunas usadas no dashboard (reduz memória e tempo de leitura)
COLUNAS = [
    "txNomeParlamentar",
    "sgPartido",
    "sgUF",
    "txtDescricao",
    "vlrLiquido",
    "numMes",
    "numAno",
    "nuDeputadoId",
]


def formatar_reais(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@st.cache_data
def carregar_dados(caminho=CAMINHO_DADOS):
    df = pd.read_csv(caminho, sep=";", encoding="utf-8-sig", usecols=COLUNAS, low_memory=False)

    # Recorte temporal: somente 2025
    df = df[df["numAno"] == 2025]

    # Remove lançamentos de lideranças (sem partido) e deputados sem partido
    df = df[df["sgPartido"].notna() & (df["sgPartido"] != "S.PART.")]

    # Mantém somente despesas positivas, como na Atividade 01
    # (valores negativos são estornos/ajustes de natureza indeterminada)
    df = df[df["vlrLiquido"] > 0]

    df["numMes"] = df["numMes"].astype(int)

    return df.reset_index(drop=True)


MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def rotulo_categoria(categoria):
    # "COMBUSTÍVEIS E LUBRIFICANTES." -> "Combustíveis e lubrificantes"
    rotulo = categoria.rstrip(". ").capitalize()
    # Mantém siglas em maiúsculas (ex.: "Passagem aérea - SIGEPA")
    return rotulo.replace("sigepa", "SIGEPA").replace("- rpa", "- RPA")

def escapar_markdown(texto):
    # No st.markdown, o texto entre dois "$" vira fórmula LaTeX; escapa o cifrão
    return texto.replace("$", r"\$")


def formatar_percentual(valor):
    return f"{valor:.1f}%".replace(".", ",")


def formatar_milhoes(valor):
    # Formato compacto para KPIs e rótulos: "R$ 46,7 mi" ou "R$ 172,9 mil"
    if valor >= 1e6:
        texto = f"R$ {valor / 1e6:,.1f} mi"
    else:
        texto = f"R$ {valor / 1e3:,.1f} mil"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def adicionar_linhas_media(fig, media_selecionados, media_todos):
    # Duas referências verticais: média do recorte filtrado (cinza, tracejada)
    # e média de todos os parlamentares da base (violeta, pontilhada).
    # Os valores vão para a legenda para não ficarem sobre as barras.
    linhas = [
        (media_selecionados, "dash", "#52514e",
         f"Média dos parlamentares selecionados: {formatar_milhoes(media_selecionados)}"),
        (media_todos, "dot", "#4a3aa7",
         f"Média de todos os parlamentares: {formatar_milhoes(media_todos)}"),
    ]
    for valor, tracejado, cor, nome in linhas:
        fig.add_vline(x=valor, line_dash=tracejado, line_width=2.5, line_color=cor)
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="lines",
                line=dict(dash=tracejado, width=2.5, color=cor),
                name=nome,
            )
        )


def aviso_medias_iguais(media_selecionados, media_todos):
    if abs(media_selecionados - media_todos) < 1:
        st.caption(
            "Com todos os parlamentares selecionados, as duas médias coincidem e as linhas se sobrepõem. "
            "Aplique um filtro para compará-las."
        )


# Paleta categórica em ordem fixa (validada para daltonismo); "Outras" em cinza neutro
PALETA = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
COR_OUTRAS = "#a3a29c"
OUTRAS = "Outras categorias"
# Rampa sequencial (azul, claro -> escuro) para a matriz mensal
RAMPA_AZUL = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]
N_CATEGORIAS_DESTAQUE = 5


# ---------------------------------------------------------------------------
# Página
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Cota Parlamentar 2025", layout="wide")

df = carregar_dados()

# ---------------------------------------------------------------------------
# Sidebar — controles interativos
# ---------------------------------------------------------------------------
st.sidebar.header("Filtros")

partidos_disponiveis = (
    df.groupby("sgPartido")["vlrLiquido"].sum().sort_values(ascending=False).index.tolist()
)
partidos = st.sidebar.multiselect(
    "Partidos",
    options=partidos_disponiveis,
    default=partidos_disponiveis,
    help="Ordenados pelo gasto total em 2025.",
)

ufs_disponiveis = sorted(df["sgUF"].unique())
ufs = st.sidebar.multiselect(
    "Estados (UF)",
    options=ufs_disponiveis,
    default=ufs_disponiveis,
    help="UF pela qual o parlamentar foi eleito.",
)

mes_inicio, mes_fim = st.sidebar.select_slider(
    "Período (meses de 2025)",
    options=list(range(1, 13)),
    value=(1, 12),
    format_func=lambda m: MESES[m - 1],
)

categorias_disponiveis = (
    df.groupby("txtDescricao")["vlrLiquido"].sum().sort_values(ascending=False).index.tolist()
)
categorias = st.sidebar.multiselect(
    "Categorias de despesa",
    options=categorias_disponiveis,
    default=categorias_disponiveis,
    format_func=rotulo_categoria,
    help="Ordenadas pelo gasto total em 2025.",
)

top_n = st.sidebar.radio(
    "Parlamentares no ranking",
    options=[10, 20, 30, 40, 50],
    horizontal=True,
    help="Quantos parlamentares com maior gasto exibir no gráfico de ranking.",
)

metrica_matriz = st.sidebar.radio(
    "Métrica da matriz mensal",
    options=["Total gasto", "Média por parlamentar"],
    help="Média = gasto do partido no mês ÷ parlamentares do partido com despesa no mês.",
)

st.sidebar.caption(
    "Fonte: Câmara dos Deputados — Cota para o Exercício da Atividade Parlamentar (CEAP), 2025. "
    "Excluídos lançamentos de lideranças, sem partido e valores negativos (estornos)."
)

df_filtrado = df[
    df["sgPartido"].isin(partidos)
    & df["sgUF"].isin(ufs)
    & df["numMes"].between(mes_inicio, mes_fim)
    & df["txtDescricao"].isin(categorias)
]

if df_filtrado.empty:
    st.warning(
        "Nenhuma despesa encontrada para a combinação de filtros selecionada. "
        "Selecione ao menos um partido, um estado e uma categoria, ou amplie o período."
    )
    st.stop()

# Cores fixas por categoria: as 5 maiores do ano recebem uma cor própria e o
# restante vira "Outras". A cor segue a categoria, não muda com os filtros.
categorias_destaque = categorias_disponiveis[:N_CATEGORIAS_DESTAQUE]
cor_categoria = {rotulo_categoria(c): cor for c, cor in zip(categorias_destaque, PALETA)}
cor_categoria[OUTRAS] = COR_OUTRAS
ordem_categorias = list(cor_categoria)

df_filtrado = df_filtrado.assign(
    categoria_grafico=df_filtrado["txtDescricao"]
    .where(df_filtrado["txtDescricao"].isin(categorias_destaque))
    .map(rotulo_categoria, na_action="ignore")
    .fillna(OUTRAS)
)

# ---------------------------------------------------------------------------
# Cabeçalho e indicadores
# ---------------------------------------------------------------------------
st.title("Cota Parlamentar 2025 — como os partidos usam o dinheiro público")
st.markdown(
    "Despesas reembolsadas pela **Cota para o Exercício da Atividade Parlamentar (CEAP)** "
    "aos deputados federais em 2025. Use os filtros ao lado para comparar partidos, "
    "períodos e categorias de gasto. Valores em reais (R$), valor líquido."
)

periodo = (
    "Ano inteiro" if (mes_inicio, mes_fim) == (1, 12)
    else f"{MESES[mes_inicio - 1]}–{MESES[mes_fim - 1]} 2025"
)

total_gasto = df_filtrado["vlrLiquido"].sum()
n_parlamentares = df_filtrado["nuDeputadoId"].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Gasto total", formatar_milhoes(total_gasto), help=formatar_reais(total_gasto))
col2.metric("Parlamentares com despesa", f"{n_parlamentares}")
col3.metric("Média por parlamentar", formatar_reais(total_gasto / n_parlamentares))
col4.metric("Partidos selecionados", f"{df_filtrado['sgPartido'].nunique()}", help=periodo)

# ---------------------------------------------------------------------------
# V1 — Gasto total por partido e categoria (Plotly)
# ---------------------------------------------------------------------------
st.subheader("Quanto cada partido gastou — e em quê")

gasto_partido_cat = (
    df_filtrado.groupby(["sgPartido", "categoria_grafico"], as_index=False)["vlrLiquido"].sum()
)
total_partido = gasto_partido_cat.groupby("sgPartido")["vlrLiquido"].sum().sort_values()
gasto_partido_cat["percentual"] = (
    gasto_partido_cat["vlrLiquido"] / gasto_partido_cat["sgPartido"].map(total_partido) * 100
)
gasto_partido_cat["valor_fmt"] = gasto_partido_cat["vlrLiquido"].map(formatar_reais)

fig_v1 = px.bar(
    gasto_partido_cat,
    x="vlrLiquido",
    y="sgPartido",
    color="categoria_grafico",
    orientation="h",
    color_discrete_map=cor_categoria,
    category_orders={"sgPartido": total_partido.index.tolist()[::-1], "categoria_grafico": ordem_categorias},
    custom_data=["categoria_grafico", "valor_fmt", "percentual"],
    labels={"vlrLiquido": "Valor líquido total (R$)", "sgPartido": "Partido", "categoria_grafico": "Categoria"},
)
fig_v1.update_traces(
    hovertemplate="<b>%{y}</b><br>%{customdata[0]}<br>%{customdata[1]} "
    "(%{customdata[2]:.1f}% do partido)<extra></extra>",
)
# Rótulo direto só com o total de cada partido, no fim da barra
fig_v1.add_trace(
    go.Scatter(
        x=total_partido.values,
        y=total_partido.index,
        mode="text",
        text=[formatar_milhoes(v) for v in total_partido.values],
        textposition="middle right",
        showlegend=False,
        hoverinfo="skip",
    )
)
fig_v1.update_layout(
    barmode="stack",
    bargap=0.25,
    height=max(320, 28 * len(total_partido) + 140),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text=""),
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(tickformat=",.0f", range=[0, total_partido.max() * 1.15], separatethousands=True),
    separators=",.",
)
st.plotly_chart(fig_v1, width="stretch")

partido_maior = total_partido.index[-1]
cat_principal = (
    df_filtrado.groupby("categoria_grafico")["vlrLiquido"].sum().drop(OUTRAS, errors="ignore")
)
texto_v1 = (
    f"**Leitura:** no recorte selecionado, **{partido_maior}** tem o maior gasto absoluto "
    f"({formatar_reais(total_partido.iloc[-1])}, "
    f"{formatar_percentual(total_partido.iloc[-1] / total_gasto * 100)} do total). "
)
if not cat_principal.empty:
    texto_v1 += (
        f"Entre as categorias destacadas, **{cat_principal.idxmax()}** é a que mais pesa. "
    )
texto_v1 += (
    "O total absoluto reflete também o tamanho da bancada — partidos com mais deputados "
    "tendem a gastar mais. A média por parlamentar (próximo gráfico) corrige esse efeito."
)
st.markdown(escapar_markdown(texto_v1))

# ---------------------------------------------------------------------------
# V2 — Média gasta por parlamentar em cada partido (Plotly)
# ---------------------------------------------------------------------------
st.subheader("Quanto gasta, em média, cada parlamentar de cada partido")

media_partido = (
    df_filtrado.groupby("sgPartido")
    .agg(total=("vlrLiquido", "sum"), parlamentares=("nuDeputadoId", "nunique"))
    .assign(media=lambda d: d["total"] / d["parlamentares"])
    .sort_values("media")
    .reset_index()
)
media_partido["rotulo"] = media_partido["sgPartido"] + " (" + media_partido["parlamentares"].astype(str) + ")"
media_partido["media_fmt"] = media_partido["media"].map(formatar_reais)
media_partido["total_fmt"] = media_partido["total"].map(formatar_reais)
media_geral = total_gasto / n_parlamentares

fig_v2 = go.Figure(
    go.Bar(
        x=media_partido["media"],
        y=media_partido["rotulo"],
        orientation="h",
        marker_color=PALETA[0],
        showlegend=False,
        text=media_partido["media"].map(formatar_milhoes),
        textposition="outside",
        cliponaxis=False,
        customdata=media_partido[["sgPartido", "media_fmt", "parlamentares", "total_fmt"]],
        hovertemplate="<b>%{customdata[0]}</b><br>Média por parlamentar: %{customdata[1]}"
        "<br>Parlamentares com despesa: %{customdata[2]}<br>Gasto total: %{customdata[3]}<extra></extra>",
    )
)
# Média de todos os parlamentares da base, ignorando os filtros
media_todos = df["vlrLiquido"].sum() / df["nuDeputadoId"].nunique()
adicionar_linhas_media(fig_v2, media_geral, media_todos)
fig_v2.update_layout(
    bargap=0.25,
    height=max(320, 28 * len(media_partido) + 140),
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(
        title="Média por parlamentar (R$)",
        tickformat=",.0f",
        range=[0, max(media_partido["media"].max(), media_todos) * 1.18],
    ),
    yaxis=dict(title="Partido (nº de parlamentares com despesa)"),
    separators=",.",
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
)
st.plotly_chart(fig_v2, width="stretch")
aviso_medias_iguais(media_geral, media_todos)

maior, menor = media_partido.iloc[-1], media_partido.iloc[0]
texto_v2 = f"**Leitura:** a média geral é de **{formatar_reais(media_geral)}** por parlamentar"
if len(media_partido) > 1:
    texto_v2 += (
        f". **{maior['sgPartido']}** tem a maior média ({formatar_reais(maior['media'])}) "
        f"e **{menor['sgPartido']}** a menor ({formatar_reais(menor['media'])}), "
        f"uma diferença de {formatar_percentual((maior['media'] / menor['media'] - 1) * 100)}"
    )
texto_v2 += (
    ". Partidos com poucos parlamentares (número entre parênteses) têm médias mais instáveis. "
    "A contagem inclui suplentes que exerceram mandato por parte do ano, o que reduz a média "
    "dos partidos em que houve mais substituições."
)
st.markdown(escapar_markdown(texto_v2))

# ---------------------------------------------------------------------------
# V3 — Parlamentares que mais gastaram, por categoria (Plotly)
# ---------------------------------------------------------------------------
# Agrupa pelo id do deputado (nomes podem se repetir); partido e UF para o rótulo
parlamentares = (
    df_filtrado.groupby("nuDeputadoId")
    .agg(
        nome=("txNomeParlamentar", "first"),
        partido=("sgPartido", "first"),
        uf=("sgUF", "first"),
        total=("vlrLiquido", "sum"),
    )
    .nlargest(top_n, "total")
)
parlamentares["rotulo"] = (
    parlamentares["nome"] + " (" + parlamentares["partido"] + "-" + parlamentares["uf"] + ")"
)

# O recorte pode ter menos parlamentares que o top N pedido
st.subheader(f"Os {len(parlamentares)} parlamentares que mais gastaram — e em quê")

gasto_parl_cat = (
    df_filtrado[df_filtrado["nuDeputadoId"].isin(parlamentares.index)]
    .groupby(["nuDeputadoId", "categoria_grafico"], as_index=False)["vlrLiquido"]
    .sum()
)
gasto_parl_cat["rotulo"] = gasto_parl_cat["nuDeputadoId"].map(parlamentares["rotulo"])
gasto_parl_cat["percentual"] = (
    gasto_parl_cat["vlrLiquido"] / gasto_parl_cat["nuDeputadoId"].map(parlamentares["total"]) * 100
)
gasto_parl_cat["valor_fmt"] = gasto_parl_cat["vlrLiquido"].map(formatar_reais)

def rotulo_vs_media(valor):
    # "R$ 674,5 mil (51,9% acima da média geral)"
    diferenca = (valor / media_geral - 1) * 100
    sentido = "acima" if diferenca >= 0 else "abaixo"
    return f"{formatar_milhoes(valor)} ({formatar_percentual(abs(diferenca))} {sentido} da média geral)"


fig_v3 = px.bar(
    gasto_parl_cat,
    x="vlrLiquido",
    y="rotulo",
    color="categoria_grafico",
    orientation="h",
    color_discrete_map=cor_categoria,
    category_orders={"rotulo": parlamentares["rotulo"].tolist(), "categoria_grafico": ordem_categorias},
    custom_data=["categoria_grafico", "valor_fmt", "percentual"],
    labels={"vlrLiquido": "Valor líquido total (R$)", "rotulo": "Parlamentar", "categoria_grafico": "Categoria"},
)
fig_v3.update_traces(
    hovertemplate="<b>%{y}</b><br>%{customdata[0]}<br>%{customdata[1]} "
    "(%{customdata[2]:.1f}% do parlamentar)<extra></extra>",
)
fig_v3.add_trace(
    go.Scatter(
        x=parlamentares["total"],
        y=parlamentares["rotulo"],
        mode="text",
        text=parlamentares["total"].map(rotulo_vs_media),
        textposition="middle right",
        showlegend=False,
        hoverinfo="skip",
    )
)
fig_v3.update_layout(
    barmode="stack",
    bargap=0.25,
    height=max(320, 28 * len(parlamentares) + 140),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text=""),
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(tickformat=",.0f", range=[0, max(parlamentares["total"].max(), media_todos) * 1.4]),
    separators=",.",
)
# Médias de todos os parlamentares (não só dos exibidos no ranking)
adicionar_linhas_media(fig_v3, media_geral, media_todos)
st.plotly_chart(fig_v3, width="stretch")
aviso_medias_iguais(media_geral, media_todos)

primeiro = parlamentares.iloc[0]
cat_primeiro = gasto_parl_cat[gasto_parl_cat["nuDeputadoId"] == parlamentares.index[0]].nlargest(1, "vlrLiquido").iloc[0]
partidos_top = parlamentares["partido"].value_counts()
texto_v3 = (
    f"**Leitura:** **{primeiro['rotulo']}** lidera o ranking com {formatar_reais(primeiro['total'])} "
    f"({formatar_percentual(primeiro['total'] / media_geral * 100 - 100)} acima da média do recorte); "
    f"a maior parte foi em **{cat_primeiro['categoria_grafico']}** "
    f"({formatar_percentual(cat_primeiro['percentual'])}). "
    f"Entre os {len(parlamentares)} maiores gastos, o partido mais frequente é "
    f"**{partidos_top.index[0]}** ({partidos_top.iloc[0]} parlamentares). "
    "Atenção: o limite mensal da cota varia por estado (é maior para UFs mais distantes de "
    "Brasília, como RR, AC e RO), então parte da diferença entre parlamentares vem da UF, "
    "não apenas do comportamento de gasto."
)
st.markdown(escapar_markdown(texto_v3))

# ---------------------------------------------------------------------------
# V4 — Matriz partido × mês (Altair)
# ---------------------------------------------------------------------------
st.subheader(f"Gasto mês a mês por partido — {metrica_matriz.lower()}")

matriz = (
    df_filtrado.groupby(["sgPartido", "numMes"])
    .agg(total=("vlrLiquido", "sum"), parlamentares=("nuDeputadoId", "nunique"))
    .reset_index()
)
matriz["media"] = matriz["total"] / matriz["parlamentares"]
matriz["mes"] = matriz["numMes"].map(lambda m: MESES[m - 1])
matriz["total_fmt"] = matriz["total"].map(formatar_reais)
matriz["media_fmt"] = matriz["media"].map(formatar_reais)

coluna_valor = "total" if metrica_matriz == "Total gasto" else "media"
# Linhas ordenadas pelo gasto total do partido no recorte (maior no topo)
ordem_partidos = total_partido.index.tolist()[::-1]

matriz_chart = (
    alt.Chart(matriz)
    .mark_rect(cornerRadius=3)
    .encode(
        x=alt.X(
            "mes:O",
            title="Mês de 2025",
            sort=MESES,
            scale=alt.Scale(domain=MESES, paddingInner=0.1),
            axis=alt.Axis(orient="top", labelAngle=0, ticks=False, domain=False),
        ),
        y=alt.Y(
            "sgPartido:N",
            title=None,
            sort=ordem_partidos,
            scale=alt.Scale(paddingInner=0.1),
            axis=alt.Axis(ticks=False, domain=False),
        ),
        color=alt.Color(
            f"{coluna_valor}:Q",
            title=f"{metrica_matriz} (R$)",
            scale=alt.Scale(range=RAMPA_AZUL, zero=True),
            legend=alt.Legend(
                orient="bottom",
                direction="horizontal",
                gradientLength=320,
                labelExpr="replace(format(datum.value / 1000, ',.0f'), ',', '.') + ' mil'",
            ),
        ),
        tooltip=[
            alt.Tooltip("sgPartido:N", title="Partido"),
            alt.Tooltip("mes:O", title="Mês"),
            alt.Tooltip("total_fmt:N", title="Gasto total"),
            alt.Tooltip("parlamentares:Q", title="Parlamentares com despesa"),
            alt.Tooltip("media_fmt:N", title="Média por parlamentar"),
        ],
    )
    # Mesmo passo nos dois eixos para que as células sejam quadradas
    .properties(width=alt.Step(34), height=alt.Step(34))
)
st.altair_chart(matriz_chart, width="content")
st.caption(
    "Cada quadrado é um partido em um mês; quanto mais escuro, maior o valor. "
    "Quadrados vazios indicam meses fora do período selecionado ou sem despesas registradas. "
    "O mês é o de competência da despesa (numMes)."
)

pico = matriz.loc[matriz[coluna_valor].idxmax()]
por_mes = matriz.groupby("numMes")["total"].sum()
texto_v4 = (
    f"**Leitura:** o maior valor da matriz é de **{pico['sgPartido']}** em **{pico['mes']}** "
    f"({formatar_reais(pico[coluna_valor])}). "
)
if len(por_mes) > 1:
    texto_v4 += (
        f"Somando todos os partidos, o mês de maior gasto foi **{MESES[por_mes.idxmax() - 1]}** "
        f"({formatar_milhoes(por_mes.max())}) e o de menor, **{MESES[por_mes.idxmin() - 1]}** "
        f"({formatar_milhoes(por_mes.min())}). "
)
if metrica_matriz == "Total gasto":
    texto_v4 += "Em valor total, as linhas dos partidos com mais deputados ficam naturalmente mais escuras; "
    texto_v4 += "alterne para **Média por parlamentar** na barra lateral para comparar partidos de tamanhos diferentes."
else:
    texto_v4 += "Na média por parlamentar, partidos com poucos deputados podem ter meses muito claros ou muito escuros por efeito de um único gasto."
st.markdown(escapar_markdown(texto_v4))
