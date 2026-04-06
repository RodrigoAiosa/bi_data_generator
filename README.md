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


#	Emoji	Setor	Tabela Fato	Principais dimensões
1	🛒	Varejo	FatoVendas	Cliente, Produto, Vendedor, Filial, Geo
2	💰	Financeiro	FatoTransacao	Conta, Agência, Produto Financeiro
3	🏥	Saúde	FatoAtendimento	Paciente, Médico, Procedimento, Unidade
4	💻	Tecnologia	FatoContrato	Cliente, Produto SaaS, Agente
5	📚	Educação	FatoMatricula	Aluno, Curso, Instrutor, Turma
6	🚚	Logística	FatoEntrega	Transportadora, Rota, Cliente, Veículo
7	⚡	Energia	FatoConsumo	Consumidor, Medidor, Subestação, Tarifa
8	📡	Telecom	FatoChamada	Assinante, Plano, Torre, Destino
9	🏭	Indústria	FatoProducao	Máquina, Insumo, Produto, Operador
10	🌾	Agronegócio	FatoSafra	Cultura, Propriedade, Insumo, Clima
11	🏨	Hotelaria	FatoReserva	Hóspede, Hotel, Quarto, Canal
12	🎬	Streaming	FatoStreaming	Assinante, Conteúdo, Artista, Dispositivo
13	🏪	E-commerce	FatoPedido	Cliente, Produto, Plataforma, Pagamento, Frete
14	🏢	Recursos Humanos	FatoHorasTrabalhadas	Funcionário, Departamento, Cargo, Projeto
15	🚗	Mobilidade	FatoViagem	Motorista, Passageiro, Veículo, Rota
16	🏦	Fintech	FatoTransacao	Usuário, Cartão, Comerciante, Antifraude

Todas as bases incluem **dCalendario** compatível com Power Query.
