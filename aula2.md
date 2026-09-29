# Aula 2 — Fundamentos da Visualização de Dados

## Visualização como comunicação

A visualização de dados tem como objetivo comunicar informações de forma clara e fiel aos dados. Uma figura pode estar estatisticamente correta e ainda assim apresentar uma comunicação visual ruim.

Wilke classifica problemas de visualização em três níveis:

* **Ugly:** visualmente pouco atraente, mas sem distorcer os dados.
* **Bad:** dificulta ou induz uma interpretação inadequada.
* **Wrong:** representa os dados de forma incorreta.

## Dados, Aesthetics e Escalas

Visualizar dados envolve mapear variáveis para propriedades visuais (*aesthetics*), como:

* posição;
* cor;
* tamanho;
* forma;
* tipo e espessura de linha.

As escalas fazem a correspondência entre os valores dos dados e essas propriedades visuais. A escolha deve considerar o tipo de variável, que pode ser contínua, discreta, categórica ou ordenada.

## Escolha do gráfico

O tipo de visualização deve estar relacionado ao objetivo da análise:

* **Quantidades:** barras e pontos.
* **Distribuições:** histogramas, densidade, boxplots e violinos.
* **Proporções:** barras e gráficos de composição.
* **Relações:** scatterplots e matrizes de dispersão.
* **Séries temporais:** linhas.
* **Dados geográficos:** mapas.
* **Incerteza:** barras de erro.

## Percepção e cores

A escolha das cores influencia a interpretação dos dados. Mapas de cores como o **arco-íris** podem criar diferenças perceptuais que não correspondem aos valores reais. Paletas perceptualmente uniformes, como *viridis*, são mais adequadas para representar valores contínuos.

## Distribuições e sobreposição

Histogramas dependem da escolha dos intervalos (*bins*), que pode alterar a percepção da distribuição. Outras alternativas incluem densidade, boxplots e CDF.

Quando muitos pontos se sobrepõem (*overplotting*), podem ser utilizados:

* **Jittering**, para separar pontos;
* **Transparência**, para evidenciar regiões de maior densidade;
* **Hexbinning**, para agregar observações em células.

## Relações entre variáveis

**Scatterplots** permitem observar associações entre variáveis contínuas. Para múltiplas variáveis, podem ser utilizados matrizes de dispersão, matrizes de correlação e técnicas de redução de dimensionalidade, como PCA.

## Séries temporais

Gráficos de linhas enfatizam a ordem temporal e facilitam a identificação de tendências. A rotulagem direta das séries pode reduzir a dependência de legendas. Séries temporais também podem ser decompostas em **tendência, sazonalidade e resíduo**.

## Boas práticas de design

Alguns princípios importantes:

* manter escalas e cores comparáveis entre gráficos;
* utilizar títulos e rótulos informativos;
* ordenar categorias quando isso facilitar comparações;
* usar *small multiples* para comparar grupos;
* utilizar redundância visual quando melhorar a compreensão;
* evitar elementos gráficos desnecessários;
* evitar **3D** quando ele não representa uma característica real dos dados.

**Ideia central:** uma boa visualização deve representar os dados corretamente e, ao mesmo tempo, facilitar a percepção e a interpretação das informações.
