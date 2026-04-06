# BI Data Generator PRO

Gerador de bases de dados no modelo **Star Schema** para projetos de BI.  
Compatível com Power BI, Tableau e qualquer ferramenta de análise de dados.

---

## 🚀 Funcionalidades

- ✅ **16 setores** disponíveis para geração de dados
- ✅ Modelo **Star Schema** com tabelas Fato e Dimensões
- ✅ Tabela `dCalendario` automática para análises temporais
- ✅ Preview interativo dos dados gerados
- ✅ Dashboard automático com métricas e gráficos
- ✅ Download em **ZIP** com todos os CSVs
- ✅ Interface moderna e responsiva

---

## 📁 Estrutura do projeto

# BI Data Generator PRO

Gerador de bases de dados no modelo **Star Schema** para projetos de BI.  
Compatível com Power BI, Tableau e qualquer ferramenta de análise de dados.

---

## 🚀 Funcionalidades

- ✅ **16 setores** disponíveis para geração de dados
- ✅ Modelo **Star Schema** com tabelas Fato e Dimensões
- ✅ Tabela `dCalendario` automática para análises temporais
- ✅ Preview interativo dos dados gerados
- ✅ Dashboard automático com métricas e gráficos
- ✅ Download em **ZIP** com todos os CSVs
- ✅ Interface moderna e responsiva
- ✅ Suporte a Bridge Tables (relacionamentos N:N)

---

## 📁 Estrutura do projeto
bi_data_generator/
├── app.py ← Entry point (streamlit run app.py)
├── config.py ← Mapa de setores + constantes globais
├── requirements.txt
├── styles/
│ ├── init.py
│ └── css.py ← Todo o CSS/tema em um único lugar
├── generators/
│ ├── init.py
│ ├── helpers.py ← new_ids, dcalendario, rand_dates, to_zip
│ ├── varejo.py
│ ├── financeiro.py
│ ├── saude.py
│ ├── tecnologia.py
│ ├── educacao.py
│ ├── logistica.py
│ ├── energia.py
│ ├── telecom.py
│ ├── industria.py
│ ├── agronegocio.py
│ ├── hotelaria.py
│ ├── streaming.py
│ ├── ecommerce.py
│ ├── rh.py
│ ├── mobilidade.py
│ └── fintech.py
└── ui/
├── init.py
├── sidebar.py ← Inputs do usuário
├── hero.py ← Cabeçalho visual
├── estado_inicial.py ← Tela de boas-vindas + flip-cards
└── resultado.py ← Métricas, preview, dashboard e download

text

---

## 🛠️ Instalação e execução

```bash
# 1. Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute
streamlit run app.py
Dependências (requirements.txt)
text
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
📊 Setores disponíveis
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
📋 Detalhes dos setores
1. 🛒 Varejo
Tabela Fato: FatoVendas

Métricas: Quantidade, valor_total, desconto, lucro

Dimensões: DimCliente, DimProduto, DimVendedor, DimFilial, DimGeografia

Aplicações: Análise de performance de vendas, sazonalidade, top produtos

2. 💰 Financeiro
Tabela Fato: FatoTransacao

Métricas: Valor, saldo, taxa_juros, prazo

Dimensões: DimConta, DimAgencia, DimProdutoFinanceiro

Aplicações: Análise de rentabilidade, risco de crédito, carteira de produtos

3. 🏥 Saúde
Tabela Fato: FatoAtendimento

Métricas: Custo, tempo_atendimento, gravidade

Dimensões: DimPaciente, DimMedico, DimProcedimento, DimUnidade

Aplicações: Análise de eficiência, custo por procedimento, tempo de espera

4. 💻 Tecnologia
Tabela Fato: FatoContrato

Métricas: Valor_contrato, usuarios_ativos, tempo_contrato

Dimensões: DimCliente, DimProdutoSaaS, DimAgente

Aplicações: MRR (Monthly Recurring Revenue), churn, expansão de conta

5. 📚 Educação
Tabela Fato: FatoMatricula

Métricas: Nota, frequencia, mensalidade

Dimensões: DimAluno, DimCurso, DimInstrutor, DimTurma

Aplicações: Análise de evasão, performance acadêmica, carga horária

6. 🚚 Logística
Tabela Fato: FatoEntrega

Métricas: Distancia, tempo_entrega, custo_frete

Dimensões: DimTransportadora, DimRota, DimCliente, DimVeiculo

Aplicações: Otimização de rotas, performance de entregadores, custo por km

7. ⚡ Energia
Tabela Fato: FatoConsumo

Métricas: Consumo_kwh, valor_conta, bandeira_tarifaria

Dimensões: DimConsumidor, DimMedidor, DimSubestacao, DimTarifa

Aplicações: Previsão de demanda, eficiência energética, picos de consumo

8. 📡 Telecom
Tabela Fato: FatoChamada

Métricas: Duracao, volume_dados, valor

Dimensões: DimAssinante, DimPlano, DimTorre, DimDestino

Aplicações: Análise de qualidade de serviço, rotatividade (churn), uso de rede

9. 🏭 Indústria
Tabela Fato: FatoProducao

Métricas: Quantidade_produzida, tempo_maquina, custo_insumo

Dimensões: DimMaquina, DimInsumo, DimProduto, DimOperador

Aplicações: Eficiência fabril, OEE (Overall Equipment Effectiveness), qualidade

10. 🌾 Agronegócio
Tabela Fato: FatoSafra

Métricas: Area_plantada, produtividade, perdas

Dimensões: DimCultura, DimPropriedade, DimInsumo, DimClima

Aplicações: Previsão de safra, análise de insumos, rentabilidade por hectare

11. 🏨 Hotelaria
Tabela Fato: FatoReserva

Métricas: Diarias, valor_total, cancelamentos, no-shows

Dimensões: DimHospede, DimHotel, DimQuarto, DimCanal

Aplicações: Revenue management, taxa de ocupação, sazonalidade, performance por canal

Indicadores: ADR (Average Daily Rate), RevPAR (Revenue Per Available Room), Occupancy Rate

12. 🎬 Streaming
Tabela Fato: FatoStreaming

Métricas: Minutos_assistidos, completude, avaliacao, pausas

Dimensões: DimAssinante, DimConteudo, DimArtista, DimDispositivo

Bridge Table: BridgeConteudoArtista (relacionamento N:N)

Aplicações: Churn prediction, recomendação de conteúdo, análise de binge-watching

Indicadores: Retention rate, engagement score, completion rate

13. 🏪 E-commerce
Tabela Fato: FatoPedido

Métricas: Valor_produtos, frete, desconto, margem_lucro

Dimensões: DimCliente, DimProduto, DimPlataforma, DimPagamento, DimFrete

Aplicações: Análise de conversão, carrinho abandonado, LTV (Lifetime Value)

Indicadores: Ticket médio, taxa de conversão, ROI por canal

14. 🏢 Recursos Humanos (RH)
Tabela Fato: FatoHorasTrabalhadas

Métricas: Horas_trabalhadas, horas_extras, produtividade, satisfacao

Dimensões: DimFuncionario, DimDepartamento, DimCargo, DimProjeto, DimAvaliacao

Aplicações: Análise de produtividade, planejamento de capacidade, turnover

Indicadores: Headcount, taxa de absenteísmo, horas por projeto

15. 🚗 Mobilidade
Tabela Fato: FatoViagem

Métricas: Distancia, tempo_viagem, valor, gorjeta, avaliacoes

Dimensões: DimMotorista, DimPassageiro, DimVeiculo, DimRota, DimPagamento

Aplicações: Otimização de rotas, análise de demanda, performance de motoristas

Indicadores: ETA accuracy, acceptance rate, earnings per hour

16. 🏦 Fintech
Tabela Fato: FatoTransacao

Métricas: Valor, parcelas, juros, taxa_maquina, cashback

Dimensões: DimUsuario, DimCartao, DimComerciante, DimDispositivo, DimAntifraude

Aplicações: Detecção de fraudes, análise de perfil de consumo, scoring de crédito

Indicadores: Taxa de aprovação, score médio de risco, volume de chargeback

🎯 Como adicionar um novo setor
Crie o arquivo do gerador em generators/meu_setor.py:

python
import pandas as pd
import numpy as np
from datetime import datetime
from .helpers import new_ids, dcalendario, rand_dates

def gerar_meu_setor(n_linhas: int, start_date, end_date) -> dict[str, pd.DataFrame]:
    # Converte datas
    if isinstance(start_date, str):
        start = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        start = start_date
    
    if isinstance(end_date, str):
        end = datetime.strptime(end_date, "%Y-%m-%d")
    else:
        end = end_date
    
    # Criar dimensões
    dim_exemplo = pd.DataFrame({
        "sk_exemplo": new_ids(100, "EXP"),
        "nome": [f"Exemplo {i+1}" for i in range(100)]
    })
    
    # Criar tabela fato
    fato_exemplo = pd.DataFrame({
        "sk_fato": new_ids(n_linhas, "FAT"),
        "data": rand_dates(start, end, n_linhas),
        "valor": np.random.uniform(10, 1000, n_linhas),
        "sk_exemplo": np.random.choice(dim_exemplo["sk_exemplo"], n_linhas)
    })
    
    return {
        "FatoExemplo": fato_exemplo,
        "DimExemplo": dim_exemplo,
        "dCalendario": dcalendario(start, end)
    }
Exporte em generators/__init__.py:

python
from .meu_setor import gerar_meu_setor

__all__ = [
    # ... existing exports ...
    "gerar_meu_setor"
]
Adicione em config.py:

python
from generators import gerar_meu_setor

SETORES["🆕 Meu Setor"] = gerar_meu_setor

SETORES_INFO.append(("🆕", "Meu Setor", "Descrição para o flip-card"))
Pronto — a sidebar, os flip-cards e o download são atualizados automaticamente.

📦 Exemplo de uso
Gerar dados via código Python
python
from generators import gerar_ecommerce

# Gerar 10.000 registros para 2023
tabelas = gerar_ecommerce(
    n_linhas=10000,
    start_date="2023-01-01",
    end_date="2023-12-31"
)

# Acessar as tabelas
fato_pedido = tabelas["FatoPedido"]
dim_cliente = tabelas["DimCliente"]
dim_produto = tabelas["DimProduto"]
dcalendario = tabelas["dCalendario"]

# Análise simples
vendas_por_mes = fato_pedido.groupby(fato_pedido["data_pedido"].dt.month)["valor_total"].sum()
print(vendas_por_mes)
Importar no Power BI













🎨 Interface do usuário
A aplicação Streamlit oferece:

Componente	Descrição
Sidebar	Seleção de setor, período e volume de dados
Flip-cards	Apresentação visual de todos os 16 setores
Preview automático	Amostra de 2.000 linhas para teste
Dashboard integrado	Métricas e gráficos automáticos
Download em ZIP	Todos os CSVs empacotados
Tabs organizadas	Início, Dashboard e Base de Dados
Screenshots (exemplo)
text
┌─────────────────────────────────────────────────────────────┐
│  🎯 BI Data Generator PRO                                   │
│  Gere dados Star Schema para seus projetos de BI            │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │
│ │   🛒    │ │   💰    │ │   🏥    │ │   💻    │            │
│ │ Varejo  │ │Financeiro│ │ Saúde  │ │Tecnologia│            │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘            │
│ ...                                                         │
├─────────────────────────────────────────────────────────────┤
│ Sidebar                          │ Main Area               │
│ ┌───────────────┐                │ ┌─────────────────────┐ │
│ │ Setor:        │                │ │ 📊 Dashboard        │ │
│ │ [Varejo ▼]    │                │ │                     │ │
│ │               │                │ │ • Métricas          │ │
│ │ Data Início   │                │ │ • Gráficos          │ │
│ │ [2023-01-01]  │                │ │ • Tabelas           │ │
│ │               │                │ └─────────────────────┘ │
│ │ Data Fim      │                │                         │
│ │ [2023-12-31]  │                │ ┌─────────────────────┐ │
│ │               │                │ │ 📦 Base de Dados    │ │
│ │ Linhas:       │                │ │ • Preview das       │ │
│ │ [5000]        │                │ │   tabelas           │ │
│ │               │                │ │ • Download ZIP      │ │
│ │ [🚀 Gerar]    │                │ └─────────────────────┘ │
│ └───────────────┘                │                         │
└─────────────────────────────────────────────────────────────┘
📊 Compatibilidade
Ferramenta	Suporte	Observação
Power BI	✅ Completo	Use dCalendario para inteligência de tempo
Tableau	✅ Completo	Relações automáticas via chaves estrangeiras
Excel	✅ Completo	Importação direta dos CSVs
Python	✅ Completo	Use pandas para análise avançada
SQL	✅ Completo	Importe para qualquer banco de dados
Looker	✅ Completo	Suporte a CSV e conexões nativas
Qlik Sense	✅ Completo	Importação via CSV
🔧 Funções helpers disponíveis
new_ids(n, prefix)
Gera lista de IDs únicos com prefixo opcional.

python
ids = new_ids(100, "CLI")  # ["CLI000001", "CLI000002", ...]
dcalendario(start, end)
Gera tabela calendário completa com:

Data, Ano, Mês, Trimestre, Semana

Dia da semana, Fim de semana, Mês/Ano

rand_dates(start, end, n)
Gera n datas aleatórias entre start e end.

to_zip(tabelas)
Converte dicionário de DataFrames para arquivo ZIP em memória.

📈 Métricas automáticas no Dashboard
O dashboard gera automaticamente:

Métricas principais: Total de registros, valores totais, quantidades

Distribuições: Gráficos de barras para colunas categóricas

Séries temporais: Evolução ao longo do tempo

Bridge Tables: Exibição de relacionamentos N:N

🤝 Contribuindo
Fork o projeto

Crie sua branch: git checkout -b feature/novo-setor

Commit suas mudanças: git commit -m 'feat: Adiciona novo setor'

Push para a branch: git push origin feature/novo-setor

Abra um Pull Request

Diretrizes para novos
