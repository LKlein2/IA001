from pathlib import Path

import altair as alt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ===========================================================================
# Textos da interface
# Todos os rótulos exibidos ficam aqui. Os que têm {chaves} são modelos
# preenchidos com .format() no ponto de uso.
# ===========================================================================

# Página e cabeçalho
TITULO_ABA = "Cota Parlamentar 2025"
TITULO_PAGINA = "Cota Parlamentar 2025 - como os partidos usam o dinheiro público"
TEXTO_INTRODUCAO = (
    "Despesas reembolsadas pela **Cota para o Exercício da Atividade Parlamentar (CEAP)** "
    "aos deputados federais em 2025. Use os filtros ao lado para comparar partidos, "
    "períodos e categorias de gasto. Valores em reais (R$), valor líquido."
)
PREFIXO_LEITURA = "**Leitura:** "

# Barra lateral - filtros
TITULO_FILTROS = "Filtros disponíveis"
FILTRO_PARTIDOS = "Partidos"
AJUDA_PARTIDOS = "Ordenados pelo gasto total em 2025."
FILTRO_UFS = "Estados (UF)"
AJUDA_UFS = "Estado pelo qual o parlamentar foi eleito."
FILTRO_PERIODO = "Período (meses de 2025)"
FILTRO_CATEGORIAS = "Categorias de despesa"
AJUDA_CATEGORIAS = "Ordenadas pelo gasto total em 2025."
FILTRO_TOP_N = "Parlamentares no ranking de gastões"
AJUDA_TOP_N = "Quantos parlamentares com maior gasto exibir no gráfico de ranking."
OPCOES_TOP_N = [10, 20, 30, 40, 50]
FILTRO_METRICA = "Métrica da matriz mensal"
AJUDA_METRICA = (
    "Variação = gasto do partido no mês comparado à média mensal do próprio partido no período. "
    "Média = gasto do partido no mês ÷ parlamentares do partido com despesa no mês."
)
METRICA_VARIACAO = "Variação vs. média mensal do partido"
METRICA_TOTAL = "Total gasto"
METRICA_MEDIA = "Média por parlamentar"
TEXTO_FONTE = (
    "Fonte: Câmara dos Deputados - Cota para o Exercício da Atividade Parlamentar (CEAP), 2025. "
    "Excluídos lançamentos de lideranças, sem partido e valores negativos (estornos)."
)
AVISO_SEM_DADOS = (
    "Nenhuma despesa encontrada para a combinação de filtros selecionada. "
    "Selecione ao menos um partido, um estado e uma categoria, ou amplie o período."
)

# Indicadores (KPIs)
KPI_GASTO_TOTAL = "Gasto total"
KPI_PARLAMENTARES = "Parlamentares com despesa"
KPI_MEDIA = "Média por parlamentar"
KPI_PARTIDOS = "Partidos selecionados"
PERIODO_ANO_INTEIRO = "Ano inteiro"
PERIODO_INTERVALO = "{inicio}–{fim} 2025"

# Rótulos comuns aos gráficos
EIXO_VALOR_TOTAL = "Valor líquido total (R$)"
ROTULO_PARTIDO = "Partido"
ROTULO_PARLAMENTAR = "Parlamentar"
ROTULO_CATEGORIA = "Categoria"
ROTULO_MES = "Mês"
ROTULO_GASTO_TOTAL = "Gasto total"
ROTULO_PARLAMENTARES = "Parlamentares com despesa"
ROTULO_MEDIA = "Média por parlamentar"
OUTRAS = "Outras categorias"
LEGENDA_MEDIA_SELECIONADOS = "Média de gasto de todos os parlamentares após filtro: {valor}"
LEGENDA_MEDIA_TODOS = "Média de gasto total de todos os parlamentares: {valor}"
CHECK_MEDIA_TODOS = "Exibir média de gasto total"
AJUDA_MEDIA_TODOS = "Linha pontilhada com a média de todos os parlamentares da base, ignorando os filtros."
CHECK_MEDIA_FILTRO = "Exibir média de gasto após filtro"
AJUDA_MEDIA_FILTRO = "Linha tracejada com a média dos gastos dos parlamentares que atendem aos filtros."
AVISO_MEDIAS_IGUAIS = (
    "Com todos os parlamentares selecionados, as duas médias coincidem e as linhas se sobrepõem. "
    "Aplique um filtro para compará-las."
)

# G1 - Gasto por partido e categoria
TITULO_G1 = "Quanto cada partido gastou - e em quê"
HOVER_G1_PARTE = "do partido"
LEITURA_G1 = (
    "no recorte selecionado, **{partido}** tem o maior gasto absoluto "
    "({valor}, {percentual} do total). "
)
LEITURA_G1_CATEGORIA = "Entre as categorias destacadas, **{categoria}** é a que mais pesa. "

# G2 - Média por parlamentar em cada partido
TITULO_G2 = "Quanto gasta, em média, cada parlamentar de cada partido"
EIXO_X_G2 = "Média por parlamentar (R$)"
EIXO_Y_G2 = "Partido (nº de parlamentares com despesa)"
LEITURA_G2 = "a média geral é de **{valor}** por parlamentar"
LEITURA_G2_COMPARACAO = (
    ". **{maior}** tem a maior média ({valor_maior}) "
    "e **{menor}** a menor ({valor_menor}), uma diferença de {diferenca}."
)

# G3 - Parlamentares que mais gastaram
TITULO_G3 = "Os {n} parlamentares que mais gastaram - e em quê"
HOVER_G3_PARTE = "do parlamentar"
ROTULO_G3_VALOR = "{valor} ({percentual} {sentido} da média geral)"
ROTULO_G3_ACIMA = "acima"
ROTULO_G3_ABAIXO = "abaixo"
LEITURA_G3 = (
    "**{parlamentar}** lidera o ranking com {valor} "
    "({percentual} acima da média do recorte); "
    "a maior parte foi em **{categoria}** ({percentual_categoria}). "
    "Entre os {n} maiores gastos, o partido mais frequente é "
    "**{partido}** ({n_partido} parlamentares). "
)

# G4 - Matriz partido × mês
TITULO_G4 = "Gasto mês a mês por partido - {metrica}"
EIXO_X_G4 = "Mês de 2025"
LEGENDA_COR_G4 = "{metrica} (R$)"
LEGENDA_COR_G4_UNIDADE = "mil"
LEGENDA_COR_G4_VARIACAO = "Variação x Média mensal"
ROTULO_MEDIA_MENSAL_PARTIDO = "Média mensal do partido"
ROTULO_VARIACAO = "Variação vs. média mensal"
NOTA_G4_VARIACAO = (
    "Cada quadrado compara o gasto do partido no mês com a média mensal do próprio partido "
    "no período selecionado: vermelho = acima da média, azul = abaixo, cinza = próximo da média. "
    "Assim, partidos grandes e pequenos ficam na mesma escala. "
    "Quadrados vazios indicam meses fora do período selecionado ou sem despesas registradas. "
    "O mês é o de competência da despesa (numMes)."
)
NOTA_G4 = (
    "Cada quadrado é um partido em um mês; quanto mais escuro, maior o valor. "
    "Quadrados vazios indicam meses fora do período selecionado ou sem despesas registradas. "
    "O mês é o de competência da despesa (numMes)."
)

MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

# ===========================================================================
# Dados e aparência
# ===========================================================================

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

# Paleta categórica em ordem fixa (validada para daltonismo); "Outras" em cinza neutro
PALETA = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
COR_OUTRAS = "#a3a29c"
# Linhas de referência: média dos selecionados (cinza) e de todos (violeta)
COR_MEDIA_SELECIONADOS = "#52514e"
COR_MEDIA_TODOS = "#4a3aa7"
# Rampa sequencial (azul, claro -> escuro) para a matriz mensal
RAMPA_AZUL = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]
# Escala divergente para a variação (-100% a +100%)
DIVERGENTE = ["#2166AC", "#F7F7F7", "#B2182B"]
# Limite da escala de variação (%); valores além disso ficam com a cor máxima
LIMITE_VARIACAO = 100
N_CATEGORIAS_DESTAQUE = 5


# ===========================================================================
# Funções auxiliares
# ===========================================================================
def formatar_reais(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_percentual(valor):
    return f"{valor:.1f}%".replace(".", ",")

def formatar_variacao(valor):
    # "+23,4%" / "-12,0%"
    return ("+" if valor > 0 else "") + formatar_percentual(valor)


def formatar_milhoes(valor):
    # Formato compacto para KPIs e rótulos: "R$ 46,7 mi" ou "R$ 172,9 mil"
    if valor >= 1e6:
        texto = f"R$ {valor / 1e6:,.1f} mi"
    else:
        texto = f"R$ {valor / 1e3:,.1f} mil"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")

def rotulo_categoria(categoria):
    # "COMBUSTÍVEIS E LUBRIFICANTES." -> "Combustíveis e lubrificantes"
    rotulo = categoria.rstrip(". ").capitalize()
    # Mantém siglas em maiúsculas (ex.: "Passagem aérea - SIGEPA")
    return rotulo.replace("sigepa", "SIGEPA").replace("- rpa", "- RPA")

def escapar_markdown(texto):
    # No st.markdown, o texto entre dois "$" vira fórmula LaTeX; escapa o cifrão
    return texto.replace("$", r"\$")

def exibir_leitura(texto):
    st.markdown(escapar_markdown(PREFIXO_LEITURA + texto))

def hover_categoria(parte):
    # Tooltip das barras empilhadas: nome, categoria, valor e % do todo
    return (
        "<b>%{y}</b><br>%{customdata[0]}<br>%{customdata[1]} "
        f"(%{{customdata[2]:.1f}}% {parte})<extra></extra>"
    )

def adicionar_linhas_media(fig, media_selecionados, media_todos, exibir_selecionados, exibir_todos):
    # Até duas referências verticais, conforme os checkboxes da barra lateral:
    # média do recorte filtrado (tracejada) e média de todos os parlamentares
    # da base (pontilhada). Os valores vão para a legenda para não ficarem
    # sobre as barras.
    linhas = []
    if exibir_selecionados:
        linhas.append((media_selecionados, "dash", COR_MEDIA_SELECIONADOS,
                       LEGENDA_MEDIA_SELECIONADOS.format(valor=formatar_milhoes(media_selecionados))))
    if exibir_todos:
        linhas.append((media_todos, "dot", COR_MEDIA_TODOS,
                       LEGENDA_MEDIA_TODOS.format(valor=formatar_milhoes(media_todos))))
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

def aviso_medias_iguais(media_selecionados, media_todos, exibir_selecionados, exibir_todos):
    # Só faz sentido avisar quando as duas linhas estão visíveis
    if exibir_selecionados and exibir_todos and abs(media_selecionados - media_todos) < 1:
        st.caption(AVISO_MEDIAS_IGUAIS)

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

# ---------------------------------------------------------------------------
# Página
# ---------------------------------------------------------------------------
st.set_page_config(page_title=TITULO_ABA, layout="wide")

df = carregar_dados()

# ---------------------------------------------------------------------------
# Sidebar - controles interativos
# ---------------------------------------------------------------------------
st.sidebar.header(TITULO_FILTROS)

partidos_disponiveis = (
    df.groupby("sgPartido")["vlrLiquido"].sum().sort_values(ascending=False).index.tolist()
)
partidos = st.sidebar.multiselect(
    FILTRO_PARTIDOS,
    options=partidos_disponiveis,
    default=partidos_disponiveis,
    help=AJUDA_PARTIDOS,
)

ufs_disponiveis = sorted(df["sgUF"].unique())
ufs = st.sidebar.multiselect(
    FILTRO_UFS,
    options=ufs_disponiveis,
    default=ufs_disponiveis,
    help=AJUDA_UFS,
)

mes_inicio, mes_fim = st.sidebar.select_slider(
    FILTRO_PERIODO,
    options=list(range(1, 13)),
    value=(1, 12),
    format_func=lambda m: MESES[m - 1],
)

categorias_disponiveis = (
    df.groupby("txtDescricao")["vlrLiquido"].sum().sort_values(ascending=False).index.tolist()
)
categorias = st.sidebar.multiselect(
    FILTRO_CATEGORIAS,
    options=categorias_disponiveis,
    default=categorias_disponiveis,
    format_func=rotulo_categoria,
    help=AJUDA_CATEGORIAS,
)

top_n = st.sidebar.radio(
    FILTRO_TOP_N,
    options=OPCOES_TOP_N,
    horizontal=True,
    help=AJUDA_TOP_N,
)

metrica_matriz = st.sidebar.radio(
    FILTRO_METRICA,
    options=[METRICA_VARIACAO, METRICA_TOTAL, METRICA_MEDIA],
    help=AJUDA_METRICA,
)

exibir_media_todos = st.sidebar.checkbox(CHECK_MEDIA_TODOS, value=True, help=AJUDA_MEDIA_TODOS)
exibir_media_filtro = st.sidebar.checkbox(CHECK_MEDIA_FILTRO, value=True, help=AJUDA_MEDIA_FILTRO)

st.sidebar.caption(TEXTO_FONTE)

df_filtrado = df[
    df["sgPartido"].isin(partidos)
    & df["sgUF"].isin(ufs)
    & df["numMes"].between(mes_inicio, mes_fim)
    & df["txtDescricao"].isin(categorias)
]

if df_filtrado.empty:
    st.warning(AVISO_SEM_DADOS)
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
st.title(TITULO_PAGINA)
st.markdown(TEXTO_INTRODUCAO)

periodo = (
    PERIODO_ANO_INTEIRO if (mes_inicio, mes_fim) == (1, 12)
    else PERIODO_INTERVALO.format(inicio=MESES[mes_inicio - 1], fim=MESES[mes_fim - 1])
)

total_gasto = df_filtrado["vlrLiquido"].sum()
n_parlamentares = df_filtrado["nuDeputadoId"].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric(KPI_GASTO_TOTAL, formatar_milhoes(total_gasto), help=formatar_reais(total_gasto))
col2.metric(KPI_PARLAMENTARES, f"{n_parlamentares}")
col3.metric(KPI_MEDIA, formatar_reais(total_gasto / n_parlamentares))
col4.metric(KPI_PARTIDOS, f"{df_filtrado['sgPartido'].nunique()}", help=periodo)

# ---------------------------------------------------------------------------
# G1 - Gasto total por partido e categoria (Plotly)
# ---------------------------------------------------------------------------
st.subheader(TITULO_G1)

gasto_partido_cat = (
    df_filtrado.groupby(["sgPartido", "categoria_grafico"], as_index=False)["vlrLiquido"].sum()
)
total_partido = gasto_partido_cat.groupby("sgPartido")["vlrLiquido"].sum().sort_values()
gasto_partido_cat["percentual"] = (
    gasto_partido_cat["vlrLiquido"] / gasto_partido_cat["sgPartido"].map(total_partido) * 100
)
gasto_partido_cat["valor_fmt"] = gasto_partido_cat["vlrLiquido"].map(formatar_reais)

fig_G1 = px.bar(
    gasto_partido_cat,
    x="vlrLiquido",
    y="sgPartido",
    color="categoria_grafico",
    orientation="h",
    color_discrete_map=cor_categoria,
    category_orders={"sgPartido": total_partido.index.tolist()[::-1], "categoria_grafico": ordem_categorias},
    custom_data=["categoria_grafico", "valor_fmt", "percentual"],
    labels={"vlrLiquido": EIXO_VALOR_TOTAL, "sgPartido": ROTULO_PARTIDO, "categoria_grafico": ROTULO_CATEGORIA},
)
fig_G1.update_traces(hovertemplate=hover_categoria(HOVER_G1_PARTE))
# Rótulo direto só com o total de cada partido, no fim da barra
fig_G1.add_trace(
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
fig_G1.update_layout(
    barmode="stack",
    bargap=0.25,
    height=max(320, 28 * len(total_partido) + 140),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text=""),
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(tickformat=",.0f", range=[0, total_partido.max() * 1.15], separatethousands=True),
    separators=",.",
)
st.plotly_chart(fig_G1, width="stretch")

cat_principal = (
    df_filtrado.groupby("categoria_grafico")["vlrLiquido"].sum().drop(OUTRAS, errors="ignore")
)
texto_G1 = LEITURA_G1.format(
    partido=total_partido.index[-1],
    valor=formatar_reais(total_partido.iloc[-1]),
    percentual=formatar_percentual(total_partido.iloc[-1] / total_gasto * 100),
)
if not cat_principal.empty:
    texto_G1 += LEITURA_G1_CATEGORIA.format(categoria=cat_principal.idxmax())
exibir_leitura(texto_G1)

# ---------------------------------------------------------------------------
# G2 - Média gasta por parlamentar em cada partido (Plotly)
# ---------------------------------------------------------------------------
st.subheader(TITULO_G2)

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

fig_G2 = go.Figure(
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
        hovertemplate=f"<b>%{{customdata[0]}}</b><br>{ROTULO_MEDIA}: %{{customdata[1]}}"
        f"<br>{ROTULO_PARLAMENTARES}: %{{customdata[2]}}<br>{ROTULO_GASTO_TOTAL}: %{{customdata[3]}}<extra></extra>",
    )
)
# Média de todos os parlamentares da base, ignorando os filtros
media_todos = df["vlrLiquido"].sum() / df["nuDeputadoId"].nunique()
adicionar_linhas_media(fig_G2, media_geral, media_todos, exibir_media_filtro, exibir_media_todos)
fig_G2.update_layout(
    bargap=0.25,
    height=max(320, 28 * len(media_partido) + 140),
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(
        title=EIXO_X_G2,
        tickformat=",.0f",
        range=[0, max(media_partido["media"].max(), media_todos) * 1.18],
    ),
    yaxis=dict(title=EIXO_Y_G2),
    separators=",.",
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
)
st.plotly_chart(fig_G2, width="stretch")
aviso_medias_iguais(media_geral, media_todos, exibir_media_filtro, exibir_media_todos)

maior, menor = media_partido.iloc[-1], media_partido.iloc[0]
texto_G2 = LEITURA_G2.format(valor=formatar_reais(media_geral))
if len(media_partido) > 1:
    texto_G2 += LEITURA_G2_COMPARACAO.format(
        maior=maior["sgPartido"],
        valor_maior=formatar_reais(maior["media"]),
        menor=menor["sgPartido"],
        valor_menor=formatar_reais(menor["media"]),
        diferenca=formatar_percentual((maior["media"] / menor["media"] - 1) * 100),
    )
exibir_leitura(texto_G2)

# ---------------------------------------------------------------------------
# G3 - Parlamentares que mais gastaram, por categoria (Plotly)
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
st.subheader(TITULO_G3.format(n=len(parlamentares)))

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
    return ROTULO_G3_VALOR.format(
        valor=formatar_milhoes(valor),
        percentual=formatar_percentual(abs(diferenca)),
        sentido=ROTULO_G3_ACIMA if diferenca >= 0 else ROTULO_G3_ABAIXO,
    )


fig_G3 = px.bar(
    gasto_parl_cat,
    x="vlrLiquido",
    y="rotulo",
    color="categoria_grafico",
    orientation="h",
    color_discrete_map=cor_categoria,
    category_orders={"rotulo": parlamentares["rotulo"].tolist(), "categoria_grafico": ordem_categorias},
    custom_data=["categoria_grafico", "valor_fmt", "percentual"],
    labels={"vlrLiquido": EIXO_VALOR_TOTAL, "rotulo": ROTULO_PARLAMENTAR, "categoria_grafico": ROTULO_CATEGORIA},
)
fig_G3.update_traces(hovertemplate=hover_categoria(HOVER_G3_PARTE))
fig_G3.add_trace(
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
fig_G3.update_layout(
    barmode="stack",
    bargap=0.25,
    height=max(320, 28 * len(parlamentares) + 140),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text=""),
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(tickformat=",.0f", range=[0, max(parlamentares["total"].max(), media_todos) * 1.4]),
    separators=",.",
)
# Médias de todos os parlamentares (não só dos exibidos no ranking)
adicionar_linhas_media(fig_G3, media_geral, media_todos, exibir_media_filtro, exibir_media_todos)
st.plotly_chart(fig_G3, width="stretch")
aviso_medias_iguais(media_geral, media_todos, exibir_media_filtro, exibir_media_todos)

primeiro = parlamentares.iloc[0]
cat_primeiro = gasto_parl_cat[gasto_parl_cat["nuDeputadoId"] == parlamentares.index[0]].nlargest(1, "vlrLiquido").iloc[0]
partidos_top = parlamentares["partido"].value_counts()
exibir_leitura(
    LEITURA_G3.format(
        parlamentar=primeiro["rotulo"],
        valor=formatar_reais(primeiro["total"]),
        percentual=formatar_percentual(primeiro["total"] / media_geral * 100 - 100),
        categoria=cat_primeiro["categoria_grafico"],
        percentual_categoria=formatar_percentual(cat_primeiro["percentual"]),
        n=len(parlamentares),
        partido=partidos_top.index[0],
        n_partido=partidos_top.iloc[0],
    )
)

# ---------------------------------------------------------------------------
# G4 - Matriz partido × mês (Altair)
# ---------------------------------------------------------------------------
st.subheader(TITULO_G4.format(metrica=metrica_matriz.lower()))

matriz = (
    df_filtrado.groupby(["sgPartido", "numMes"])
    .agg(total=("vlrLiquido", "sum"), parlamentares=("nuDeputadoId", "nunique"))
    .reset_index()
)
matriz["media"] = matriz["total"] / matriz["parlamentares"]
# Média mensal de cada partido no período e variação de cada mês em relação a ela
matriz["media_mensal_partido"] = matriz.groupby("sgPartido")["total"].transform("mean")
matriz["variacao"] = (matriz["total"] / matriz["media_mensal_partido"] - 1) * 100
matriz["mes"] = matriz["numMes"].map(lambda m: MESES[m - 1])
matriz["total_fmt"] = matriz["total"].map(formatar_reais)
matriz["media_fmt"] = matriz["media"].map(formatar_reais)
matriz["media_mensal_fmt"] = matriz["media_mensal_partido"].map(formatar_reais)
matriz["variacao_fmt"] = matriz["variacao"].map(formatar_variacao)

# Linhas ordenadas pelo gasto total do partido no recorte (maior no topo)
ordem_partidos = total_partido.index.tolist()[::-1]

if metrica_matriz == METRICA_VARIACAO:
    # Escala simétrica em torno de zero, limitada para um único outlier não apagar o resto
    limite = min(max(matriz["variacao"].abs().max(), 10), LIMITE_VARIACAO)
    cor = alt.Color(
        "variacao:Q",
        title=LEGENDA_COR_G4_VARIACAO,
        scale=alt.Scale(domain=[-limite, 0, limite], range=DIVERGENTE, clamp=True),
        legend=alt.Legend(
            orient="bottom",
            direction="horizontal",
            gradientLength=320,
            labelExpr="(datum.value > 0 ? '+' : '') + format(datum.value, '.0f') + '%'",
        ),
    )
else:
    coluna_valor = "total" if metrica_matriz == METRICA_TOTAL else "media"
    cor = alt.Color(
        f"{coluna_valor}:Q",
        title=LEGENDA_COR_G4.format(metrica=metrica_matriz),
        scale=alt.Scale(range=RAMPA_AZUL, zero=True),
        legend=alt.Legend(
            orient="bottom",
            direction="horizontal",
            gradientLength=320,
            labelExpr=f"replace(format(datum.value / 1000, ',.0f'), ',', '.') + ' {LEGENDA_COR_G4_UNIDADE}'",
        ),
    )

matriz_chart = (
    alt.Chart(matriz)
    .mark_rect(cornerRadius=3)
    .encode(
        x=alt.X(
            "mes:O",
            title=EIXO_X_G4,
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
        color=cor,
        tooltip=[
            alt.Tooltip("sgPartido:N", title=ROTULO_PARTIDO),
            alt.Tooltip("mes:O", title=ROTULO_MES),
            alt.Tooltip("total_fmt:N", title=ROTULO_GASTO_TOTAL),
            alt.Tooltip("media_mensal_fmt:N", title=ROTULO_MEDIA_MENSAL_PARTIDO),
            alt.Tooltip("variacao_fmt:N", title=ROTULO_VARIACAO),
            alt.Tooltip("parlamentares:Q", title=ROTULO_PARLAMENTARES),
            alt.Tooltip("media_fmt:N", title=ROTULO_MEDIA),
        ],
    )
    # Mesmo passo nos dois eixos para que as células sejam quadradas
    .properties(width=alt.Step(34), height=alt.Step(34))
)
st.altair_chart(matriz_chart, width="content")

if metrica_matriz == METRICA_VARIACAO and matriz["numMes"].nunique() < 2:
    # Com um único mês, cada partido é igual à própria média: não há variação
    st.caption(NOTA_G4_VARIACAO)
elif metrica_matriz == METRICA_VARIACAO:
    st.caption(NOTA_G4_VARIACAO)
    pico = matriz.loc[matriz["variacao"].idxmax()]
    variacao_por_mes = matriz.groupby("numMes")["variacao"].mean()
else:
    st.caption(NOTA_G4)
    pico = matriz.loc[matriz[coluna_valor].idxmax()]
    por_mes = matriz.groupby("numMes")["total"].sum()
