# Dashboard Streamlit

## Requisitos
- Python 3.11 ou superior (testado com Python 3.14)
- Bibliotecas listadas em `requirements.txt`

## Dados

Fonte: Câmara dos Deputados — Dados Abertos, cota parlamentar.
- Página do conjunto: https://dadosabertos.camara.leg.br/swagger/api.html?tab=staticfile
- Arquivo utilizado: https://www.camara.leg.br/cotas/Ano-2025.csv.zip
- Data de acesso: 22/09/2026

Descompacte o .ZIP e mantenha a estrutura original

```
IA001/
├── Real/
│   └── Ano-2025.csv      <- arquivo descompactado da Câmara
└── Tarefa2/
    ├── app.py
    ├── requirements.txt
    └── README.md
```

## Instalação

No terminal, a partir da pasta `Tarefa2`:

**PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Execução

Com o ambiente virtual ativado, na pasta `Tarefa2`:

```bash
streamlit run app.py
```

O navegador abre em `http://localhost:8501`. 
Na primeira abertura, a leitura do CSV leva alguns segundos. Depois disso, os dados ficam em cache e os filtros respondem rapidamente.