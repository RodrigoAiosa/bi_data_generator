# BI Data Generator PRO

Gerador de bases de dados no modelo **Star Schema** para projetos de BI.  
Compatível com Power BI, Tableau e qualquer ferramenta de análise de dados.

---

## Estrutura do projeto

```
bi_data_generator/
├── app.py                  ← Entry point (streamlit run app.py)
├── config.py               ← Mapa de setores + constantes globais
├── requirements.txt
├── styles/
│   ├── __init__.py
│   └── css.py              ← Todo o CSS/tema em um único lugar
├── generators/
│   ├── __init__.py
│   ├── helpers.py          ← new_ids, dcalendario, rand_dates, to_zip
│   ├── varejo.py
│   ├── financeiro.py
│   ├── saude.py
│   ├── tecnologia.py
│   ├── educacao.py
│   ├── logistica.py
│   ├── energia.py
│   ├── telecom.py
│   ├── industria.py
│   └── agronegocio.py
└── ui/
    ├── __init__.py
    ├── sidebar.py          ← Inputs do usuário
    ├── hero.py             ← Cabeçalho visual
    ├── estado_inicial.py   ← Tela de boas-vindas + flip-cards
    └── resultado.py        ← Métricas, preview e download
```

---

## Instalação e execução

```bash
# 1. Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute
streamlit run app.py
```

---

## Como adicionar um novo setor

1. Crie `generators/meu_setor.py` com uma função `gerar_meu_setor(n, start, end) -> dict[str, pd.DataFrame]`
2. Exporte-a em `generators/__init__.py`
3. Adicione duas linhas em `config.py`:

```python
from generators import gerar_meu_setor          # import

SETORES["🆕 Meu Setor"] = gerar_meu_setor       # registro

SETORES_INFO.append(("🆕", "Meu Setor", "Descrição para o flip-card"))
```

Pronto — a sidebar, os flip-cards e o download são atualizados automaticamente.

---

## Setores disponíveis

| Emoji | Setor       | Tabela Fato      | Principais dimensões                         |
|-------|-------------|------------------|----------------------------------------------|
| 🛒    | Varejo      | FatoVendas       | Cliente, Produto, Vendedor, Filial, Geo      |
| 💰    | Financeiro  | FatoTransacao    | Conta, Agência, Produto                      |
| 🏥    | Saúde       | FatoAtendimento  | Paciente, Médico, Procedimento, Unidade      |
| 💻    | Tecnologia  | FatoContrato     | Cliente, Produto, Agente                     |
| 📚    | Educação    | FatoMatricula    | Aluno, Curso, Instrutor                      |
| 🚚    | Logística   | FatoEntrega      | Transportadora, Rota, Cliente                |
| ⚡    | Energia     | FatoConsumo      | Consumidor, Medidor, Subestação              |
| 📡    | Telecom     | FatoChamada      | Assinante, Plano, Torre                      |
| 🏭    | Indústria   | FatoProducao     | Máquina, Insumo, Produto, Operador           |
| 🌾    | Agronegócio | FatoSafra        | Cultura, Propriedade, Insumo                 |

Todas as bases incluem **dCalendario** compatível com Power Query.
