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
    "Média = gasto do partido no mês ÷ parlamentares do partido com despesa no mês. "
    "% da cota = gasto do partido no mês ÷ soma das cotas mensais (por UF) dos seus parlamentares com despesa no mês."
)
METRICA_VARIACAO = "Variação vs. média mensal do partido"
METRICA_TOTAL = "Total gasto"
METRICA_MEDIA = "Média por parlamentar"
METRICA_COTA = "% da cota usada"
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
ROTULO_PCT_COTA = "% da cota usada"
OUTRAS = "Outras categorias"
# Rótulo no fim das barras de G2 e G3: valor comparado às médias do recorte e geral
ROTULO_VALOR_VS_MEDIAS = "{valor} ({vs_recorte} recorte · {vs_geral} geral)"
ROTULO_VALOR_VS_MEDIA_GERAL = "{valor} ({vs_geral})"
LEGENDA_MEDIA_SELECIONADOS = "Média de gasto do recorte: {valor}"
LEGENDA_MEDIA_TODOS = "Média de gasto do conjunto: {valor}"
CHECK_MEDIA_TODOS = "Exibir média de gasto total"
AJUDA_MEDIA_TODOS = "Linha pontilhada com a média de todos os parlamentares da base, ignorando os filtros."
CHECK_MEDIA_FILTRO = "Exibir média de gasto após filtro"
AJUDA_MEDIA_FILTRO = "Linha tracejada com a média dos gastos dos parlamentares que atendem aos filtros."

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
HOVER_G2_PARTE = "da média do partido"
ROTULO_VS_RECORTE = "vs. média do recorte"
ROTULO_VS_GERAL = "vs. média geral"
LEITURA_G2 = "a média do recorte é de **{valor}** por parlamentar"
LEITURA_G2_COMPARACAO = (
    ". **{maior}** tem a maior média ({valor_maior}) "
    "e **{menor}** a menor ({valor_menor}), uma diferença de {diferenca}."
)

# G3 - Parlamentares que mais gastaram
TITULO_G3 = "Os {n} parlamentares que mais gastaram - e em quê"
HOVER_G3_PARTE = "do parlamentar"
LEGENDA_COTA_G3 = "Cota do parlamentar no período"
ROTULO_COTA_PERIODO = "Cota no período"
ROTULO_MESES_ATIVOS = "Meses com despesa"
NOTA_G3_COTA = (
    "O fundo cinza de cada barra é a cota do parlamentar no período: cota mensal da UF dele "
    "× meses em que teve despesa. O saldo não usado acumula ao longo do ano."
)
LEITURA_G3 = (
    "**{parlamentar}** lidera o ranking com {valor} "
    "({percentual} acima da média do recorte); "
    "a maior parte foi em **{categoria}** ({percentual_categoria}). "
    "Entre os {n} maiores gastos, o partido mais frequente é "
    "**{partido}** ({n_partido} parlamentares). "
)
TITULO_RESUMO_G3 = "Resumo do ranking: quantos são de cada partido e estado"
ABA_RESUMO_PARTIDO = "Por partido"
ABA_RESUMO_UF = "Por estado"
ABA_RESUMO_PARTIDO_UF = "Partido + estado"
ROTULO_UF = "Estado (UF)"
ROTULO_PARTIDO_UF = "Partido-UF"
COLUNA_RESUMO_QTD = "Parlamentares no ranking"
COLUNA_RESUMO_PCT = "% do ranking"
COLUNA_RESUMO_GASTO = "Gasto somado"

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
LEGENDA_COR_G4_COTA = "% da cota mensal usada"
NOTA_G4_COTA = (
    "Cada quadrado compara o gasto do partido no mês com a soma das cotas mensais (que variam por UF) "
    "dos seus parlamentares com despesa no mês: azul = abaixo do teto, vermelho = acima. "
    "Passar de 100% é possível porque o saldo não usado da cota acumula ao longo do ano. "
    "Quadrados vazios indicam meses fora do período selecionado ou sem despesas registradas."
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
# Teto mensal da CEAP por UF (sem cabeçalho: "UF;valor")
CAMINHO_COTA = Path(__file__).resolve().parent.parent / "Real" / "valor-cota.csv"

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
# Cota de cada parlamentar no G3: fundo translúcido e marca no fim
COR_COTA_FUNDO = "#a3a29c"
OPACIDADE_COTA_FUNDO = 0.3
COR_COTA_MARCA = "#7a7974"
# Rampa sequencial (azul, claro -> escuro) para a matriz mensal
RAMPA_AZUL = ["#FFFFFF", "#C9B6B8", "#B68187", "#B95B66", "#B2182B"]
# Escala divergente para a variação (-100% a +100%)
DIVERGENTE = ["#FFFFFF", "#EB8F8F", "#B2182B"]
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

def adicionar_linhas_media(fig, media_selecionados, media_todos, exibir_selecionados, exibir_todos, sem_filtro):
    # Até duas referências verticais, conforme os checkboxes da barra lateral:
    # média do recorte filtrado (tracejada) e média de todos os parlamentares
    # da base (pontilhada). Os valores vão para a legenda para não ficarem
    # sobre as barras. Sem filtro as duas médias coincidem: fica só a geral.
    if sem_filtro:
        exibir_todos = exibir_todos or exibir_selecionados
        exibir_selecionados = False
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

def resumo_ranking(parlamentares, chave, rotulo):
    # Conta quantos parlamentares do ranking caem em cada grupo (partido, UF...);
    # "chave" é uma Series alinhada a "parlamentares" com o grupo de cada um
    resumo = (
        parlamentares.groupby(chave.rename(rotulo))["total"]
        .agg(qtd="size", gasto="sum")
        .sort_values(["qtd", "gasto"], ascending=False)
        .reset_index()
    )
    return pd.DataFrame({
        rotulo: resumo[rotulo],
        COLUNA_RESUMO_QTD: resumo["qtd"],
        COLUNA_RESUMO_PCT: (resumo["qtd"] / len(parlamentares) * 100).map(formatar_percentual),
        COLUNA_RESUMO_GASTO: resumo["gasto"].map(formatar_milhoes),
    })

def exibir_resumo(aba, tabela):
    aba.dataframe(
        tabela,
        hide_index=True,
        width="stretch",
        height=min(400, 35 * len(tabela) + 38),
        column_config={
            COLUNA_RESUMO_QTD: st.column_config.ProgressColumn(
                format="%d", min_value=0, max_value=int(tabela[COLUNA_RESUMO_QTD].max())
            )
        },
    )

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

@st.cache_data
def carregar_cota(caminho=CAMINHO_COTA):
    # Series UF -> valor máximo mensal da cota (R$)
    cota = pd.read_csv(
        caminho, sep=";", header=None, names=["sgUF", "cota"],
        decimal=",", thousands=".", encoding="utf-8-sig",
    )
    return cota.set_index("sgUF")["cota"]

# ---------------------------------------------------------------------------
# Página
# ---------------------------------------------------------------------------
st.set_page_config(page_title=TITULO_ABA, layout="wide")

df = carregar_dados()
cota_uf = carregar_cota()

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
    options=[METRICA_VARIACAO, METRICA_TOTAL, METRICA_MEDIA, METRICA_COTA],
    help=AJUDA_METRICA,
)

exibir_media_todos = st.sidebar.checkbox(CHECK_MEDIA_TODOS, value=True, help=AJUDA_MEDIA_TODOS)
exibir_media_filtro = st.sidebar.checkbox(CHECK_MEDIA_FILTRO, value=True, help=AJUDA_MEDIA_FILTRO)

st.sidebar.caption(TEXTO_FONTE)

filtro_sem_categoria = (
    df["sgPartido"].isin(partidos)
    & df["sgUF"].isin(ufs)
    & df["numMes"].between(mes_inicio, mes_fim)
)
df_filtrado = df[filtro_sem_categoria & df["txtDescricao"].isin(categorias)]

if df_filtrado.empty:
    st.warning(AVISO_SEM_DADOS)
    st.stop()
# Nenhum filtro restringe a base: média do recorte = média geral
sem_filtro = len(df_filtrado) == len(df)

# Cota disponível: um registro por parlamentar × mês com despesa, valendo a cota
# mensal da UF dele. Ignora o filtro de categoria para o teto não encolher.
ativos = df.loc[filtro_sem_categoria, ["nuDeputadoId", "sgPartido", "sgUF", "numMes"]].drop_duplicates(
    subset=["nuDeputadoId", "numMes"]
)
ativos["cota"] = ativos["sgUF"].map(cota_uf)

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
media_partido["pct_cota"] = (
    media_partido["total"] / media_partido["sgPartido"].map(ativos.groupby("sgPartido")["cota"].sum()) * 100
)
media_partido["pct_cota_fmt"] = media_partido["pct_cota"].map(formatar_percentual, na_action="ignore")
media_geral = total_gasto / n_parlamentares
# Média de todos os parlamentares da base, ignorando os filtros
media_todos = df["vlrLiquido"].sum() / df["nuDeputadoId"].nunique()
# Quanto a média de cada partido fica acima/abaixo da média do recorte e da média geral
media_partido["vs_recorte_fmt"] = ((media_partido["media"] / media_geral - 1) * 100).map(formatar_variacao)
media_partido["vs_geral_fmt"] = ((media_partido["media"] / media_todos - 1) * 100).map(formatar_variacao)


def rotulo_vs_medias(valor):
    # "R$ 120,3 mil (+12,0% recorte · +5,1% geral)"; sem filtro as duas
    # comparações são iguais e fica só "R$ 120,3 mil (+5,1%)"
    modelo = ROTULO_VALOR_VS_MEDIA_GERAL if sem_filtro else ROTULO_VALOR_VS_MEDIAS
    return modelo.format(
        valor=formatar_milhoes(valor),
        vs_recorte=formatar_variacao((valor / media_geral - 1) * 100),
        vs_geral=formatar_variacao((valor / media_todos - 1) * 100),
    )


media_partido["rotulo_valor"] = media_partido["media"].map(rotulo_vs_medias)

# Média por parlamentar quebrada por categoria: gasto do partido na categoria
# ÷ parlamentares do partido (as partes somam a média do partido)
media_partido_cat = gasto_partido_cat.merge(
    media_partido[["sgPartido", "rotulo", "parlamentares"]], on="sgPartido"
)
media_partido_cat["media_cat"] = media_partido_cat["vlrLiquido"] / media_partido_cat["parlamentares"]
media_partido_cat["media_cat_fmt"] = media_partido_cat["media_cat"].map(formatar_reais)

fig_G2 = px.bar(
    media_partido_cat,
    x="media_cat",
    y="rotulo",
    color="categoria_grafico",
    orientation="h",
    color_discrete_map=cor_categoria,
    # Maior média no topo
    category_orders={"rotulo": media_partido["rotulo"].tolist()[::-1], "categoria_grafico": ordem_categorias},
    custom_data=["categoria_grafico", "media_cat_fmt", "percentual"],
)
fig_G2.update_traces(hovertemplate=hover_categoria(HOVER_G2_PARTE))
# Rótulo com a média do partido no fim da barra; o tooltip dele traz o resumo do partido
fig_G2.add_trace(
    go.Scatter(
        x=media_partido["media"],
        y=media_partido["rotulo"],
        mode="text",
        text=media_partido["rotulo_valor"],
        textposition="middle right",
        showlegend=False,
        customdata=media_partido[
            ["sgPartido", "media_fmt", "parlamentares", "total_fmt", "pct_cota_fmt", "vs_recorte_fmt", "vs_geral_fmt"]
        ],
        hovertemplate=f"<b>%{{customdata[0]}}</b><br>{ROTULO_MEDIA}: %{{customdata[1]}}"
        + ("" if sem_filtro else f"<br>{ROTULO_VS_RECORTE}: %{{customdata[5]}}")
        + f"<br>{ROTULO_VS_GERAL}: %{{customdata[6]}}"
        f"<br>{ROTULO_PARLAMENTARES}: %{{customdata[2]}}<br>{ROTULO_GASTO_TOTAL}: %{{customdata[3]}}"
        f"<br>{ROTULO_PCT_COTA}: %{{customdata[4]}}<extra></extra>",
    )
)
adicionar_linhas_media(fig_G2, media_geral, media_todos, exibir_media_filtro, exibir_media_todos, sem_filtro)
fig_G2.update_layout(
    barmode="stack",
    bargap=0.25,
    height=max(320, 28 * len(media_partido) + 140),
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(
        title=EIXO_X_G2,
        tickformat=",.0f",
        # Folga à direita para o rótulo com as duas comparações
        range=[0, max(media_partido["media"].max(), media_todos) * 1.6],
    ),
    yaxis=dict(title=EIXO_Y_G2),
    separators=",.",
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text=""),
)
st.plotly_chart(fig_G2, width="stretch")

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
# Cota de cada parlamentar no período: cota mensal da UF × meses com despesa
cota_parlamentar = ativos.groupby("nuDeputadoId")["cota"].agg(cota="sum", meses="size")
parlamentares = parlamentares.join(cota_parlamentar)
parlamentares["pct_cota"] = parlamentares["total"] / parlamentares["cota"] * 100

# O recorte pode ter menos parlamentares que o top N pedido
st.subheader(TITULO_G3.format(n=len(parlamentares)))

# Resumo do ranking: quantos dos N são de cada partido, estado e partido-UF
with st.expander(TITULO_RESUMO_G3, expanded=False):
    abas = st.tabs([ABA_RESUMO_PARTIDO, ABA_RESUMO_UF, ABA_RESUMO_PARTIDO_UF])
    tabelas = [
        resumo_ranking(parlamentares, parlamentares["partido"], ROTULO_PARTIDO),
        resumo_ranking(parlamentares, parlamentares["uf"], ROTULO_UF),
        resumo_ranking(
            parlamentares, parlamentares["partido"] + "-" + parlamentares["uf"], ROTULO_PARTIDO_UF
        ),
    ]
    for aba, tabela in zip(abas, tabelas):
        exibir_resumo(aba, tabela)

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

# Fundo de cada barra com a cota do parlamentar. Retângulos no eixo categórico
# usam a posição numérica da categoria (índice na ordem que o px definiu).
ordem_y = list(fig_G3.layout.yaxis.categoryarray or parlamentares["rotulo"])
meia_barra = (1 - 0.25) / 2  # bargap 0.25
for rotulo, cota in zip(parlamentares["rotulo"], parlamentares["cota"]):
    if pd.isna(cota):
        continue
    i = ordem_y.index(rotulo)
    fig_G3.add_shape(
        type="rect", layer="below", xref="x", yref="y",
        x0=0, x1=cota, y0=i - meia_barra, y1=i + meia_barra,
        fillcolor=COR_COTA_FUNDO, opacity=OPACIDADE_COTA_FUNDO, line_width=0,
    )
# Marca vertical no fim da cota: dá legenda e tooltip ao fundo
fig_G3.add_trace(
    go.Scatter(
        x=parlamentares["cota"],
        y=parlamentares["rotulo"],
        mode="markers",
        marker=dict(symbol="line-ns", size=22, line=dict(width=2.5, color=COR_COTA_MARCA)),
        name=LEGENDA_COTA_G3,
        customdata=list(zip(
            parlamentares["cota"].map(formatar_reais, na_action="ignore"),
            parlamentares["pct_cota"].map(formatar_percentual, na_action="ignore"),
            parlamentares["meses"],
        )),
        hovertemplate=f"<b>%{{y}}</b><br>{ROTULO_COTA_PERIODO}: %{{customdata[0]}}"
        f"<br>{ROTULO_PCT_COTA}: %{{customdata[1]}}<br>{ROTULO_MESES_ATIVOS}: %{{customdata[2]}}<extra></extra>",
    )
)
fig_G3.add_trace(
    go.Scatter(
        x=parlamentares["total"],
        y=parlamentares["rotulo"],
        mode="text",
        text=parlamentares["total"].map(rotulo_vs_medias),
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
    xaxis=dict(
        tickformat=",.0f",
        # Folga à direita para o rótulo com as duas comparações
        range=[0, max(max(parlamentares["total"].max(), media_todos) * 1.6, parlamentares["cota"].max() * 1.05)],
    ),
    separators=",.",
)
# Médias de todos os parlamentares (não só dos exibidos no ranking)
adicionar_linhas_media(fig_G3, media_geral, media_todos, exibir_media_filtro, exibir_media_todos, sem_filtro)
st.plotly_chart(fig_G3, width="stretch")
st.caption(NOTA_G3_COTA)

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
cota_partido_mes = ativos.groupby(["sgPartido", "numMes"])["cota"].sum().rename("cota").reset_index()
matriz = matriz.merge(cota_partido_mes, on=["sgPartido", "numMes"], how="left")
matriz["pct_cota"] = matriz["total"] / matriz["cota"] * 100
matriz["pct_cota_fmt"] = matriz["pct_cota"].map(formatar_percentual, na_action="ignore")

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
elif metrica_matriz == METRICA_COTA:
    # Divergente em torno de 100% da cota: azul abaixo do teto, vermelho acima
    coluna_valor = "pct_cota"
    cor = alt.Color(
        "pct_cota:Q",
        title=LEGENDA_COR_G4_COTA,
        scale=alt.Scale(domain=[50, 100, 150], range=DIVERGENTE, clamp=True),
        legend=alt.Legend(
            orient="bottom",
            direction="horizontal",
            gradientLength=320,
            labelExpr="format(datum.value, '.0f') + '%'",
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
            alt.Tooltip("pct_cota_fmt:N", title=ROTULO_PCT_COTA),
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
    st.caption(NOTA_G4_COTA if metrica_matriz == METRICA_COTA else NOTA_G4)
    pico =matriz.loc[matriz[coluna_valor].idxmax()]
    por_mes = matriz.groupby("numMes")["total"].sum()
