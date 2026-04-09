# BI Data Generator PRO 📊

Uma ferramenta robusta e interativa para gerar bases de dados sintéticas no modelo **Star Schema**, ideal para projetos de Business Intelligence (BI). Desenvolvida em Python com Streamlit, compatível com Power BI, Tableau, Qlik Sense e qualquer ferramenta de análise de dados.

---

## 📋 Visão Geral do Projeto

O **BI Data Generator PRO** é uma solução completa para criar conjuntos de dados realistas e contextualizados para **20 setores de negócio distintos**. Perfeito para:

- ✅ Desenvolvimento e teste de dashboards e relatórios BI
- ✅ Demonstração de funcionalidades sem dados reais sensíveis
- ✅ Treinamento e educação em Business Intelligence
- ✅ Prototipagem rápida de soluções de análise de dados
- ✅ Validação de modelos de dados em Star Schema

Todos os dados gerados seguem o padrão **Star Schema**, com tabelas fato e tabelas dimensão otimizadas para análise, e incluem uma tabela `dCalendario` compatível com Power Query.

---

## ✨ Funcionalidades Principais

### 🎯 Geração de Dados Multi-Setor
Suporte para **20 setores de negócio especializados**, cada um com estrutura de dados e métricas realistas:
- Varejo
- Financeiro
- Saúde
- Tecnologia
- Educação
- Logística
- Energia
- Telecom
- Indústria
- Agronegócio
- Hotelaria
- Streaming
- E-commerce
- Recursos Humanos
- Mobilidade
- Fintech
- Turismo
- Imobiliário
- Seguros
- Construção Civil

### 📐 Arquitetura Star Schema
- Tabelas **Fato** (fact tables) com métricas de negócio
- Tabelas **Dimensão** (dimension tables) com dados descritivos
- Relacionamentos bem definidos para análise eficiente
- Índices e chaves primárias/estrangeiras configuradas

### 📅 Calendário Integrado
- Tabela `dCalendario` compatível com **Power Query**
- Colunas: Data, Ano, Mês, MêsAno, IdMesAno, DiaSemanaBR, QuartalAno
- Facilita criação de análises temporais e comparações year-over-year

### 📊 Dashboards Interativos
- Dashboards específicos para cada setor
- Construídos com **Plotly** para máxima interatividade
- Visualizações em tempo real dos dados gerados
- Indicadores KPI customizados por setor

### ⚙️ Configuração Flexível
- Seleção de setor de negócio
- Período de tempo customizável (data início e fim)
- Volume de linhas ajustável: **100 até 100.000 registros**
- Geração rápida com caching automático

### 📦 Exportação Conveniente
- Múltiplos arquivos CSV bem organizados
- Compactação automática em arquivo ZIP
- Pronto para importar em qualquer ferramenta BI
- Nomes de arquivos padronizados e descritivos

### 🎨 Interface Intuitiva
- UI moderna e responsiva com Streamlit
- Tema visual profissional com CSS customizado
- Flip-cards informativos para cada setor
- Tabs navegáveis para diferentes views
- Preview automático dos dados antes da geração

---

## 🛠 Tecnologias Utilizadas

| Tecnologia | Versão | Função |
|-----------|--------|--------|
| **Python** | 3.8+ | Linguagem principal |
| **Streamlit** | ≥1.32.0 | Framework web interativo |
| **Pandas** | ≥2.0.0 | Manipulação e análise de dados |
| **NumPy** | ≥1.26.0 | Computação numérica |
| **Faker** | ≥24.0.0 | Geração de dados sintéticos realistas |
| **Plotly** | ≥5.18.0 | Gráficos e dashboards interativos |

---

## 📁 Estrutura do Projeto

```
bi_data_generator/
│
├── app.py                              ← Entry point (streamlit run app.py)
├── config.py                           ← Configurações globais e mapa de setores
├── requirements.txt                    ← Dependências do projeto
│
├── styles/
│   ├── __init__.py
│   └── css.py                          ← Estilos CSS/tema da aplicação
│
├── generators/                         ← Geradores de dados por setor
│   ├── __init__.py                     ← Exporta todas as funções geradoras
│   ├── helpers.py                      ← Funções auxiliares (IDs, dCalendario, etc.)
│   ├── varejo.py                       ← Gerador: Varejo
│   ├── financeiro.py                   ← Gerador: Financeiro
│   ├── saude.py                        ← Gerador: Saúde
│   ├── tecnologia.py                   ← Gerador: Tecnologia
│   ├── educacao.py                     ← Gerador: Educação
│   ├── logistica.py                    ← Gerador: Logística
│   ├── energia.py                      ← Gerador: Energia
│   ├── telecom.py                      ← Gerador: Telecom
│   ├── industria.py                    ← Gerador: Indústria
│   ├── agronegocio.py                  ← Gerador: Agronegócio
│   ├── hotelaria.py                    ← Gerador: Hotelaria
│   ├── streaming.py                    ← Gerador: Streaming
│   ├── ecommerce.py                    ← Gerador: E-commerce
│   ├── rh.py                           ← Gerador: Recursos Humanos
│   ├── mobilidade.py                   ← Gerador: Mobilidade
│   ├── fintech.py                      ← Gerador: Fintech
│   ├── turismo.py                      ← Gerador: Turismo
│   ├── imobiliario.py                  ← Gerador: Imobiliário
│   ├── seguros.py                      ← Gerador: Seguros
│   └── construcao.py                   ← Gerador: Construção Civil
│
└── ui/                                 ← Componentes da interface
    ├── __init__.py                     ← Exporta componentes UI
    ├── dashboard.py                    ← Funções de renderização dos dashboards
    ├── estado_inicial.py               ← Tela inicial e flip-cards informativos
    ├── hero.py                         ← Seção de cabeçalho (Hero Section)
    ├── resultado.py                    ← Exibição de resultados e download
    └── sidebar.py                      ← Barra lateral com inputs do usuário
```

---

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git (para clonar o repositório)

### Passo a Passo

#### 1. Clone o repositório
```bash
git clone https://github.com/RodrigoAiosa/bi_data_generator.git
cd bi_data_generator
```

#### 2. Crie e ative um ambiente virtual (recomendado)

**No Linux/macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
```

**No Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

#### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

#### 4. Execute a aplicação
```bash
streamlit run app.py
```

A aplicação abrirá automaticamente no seu navegador padrão (geralmente em `http://localhost:8501`).

---

## 📖 Como Usar

### Fluxo Básico

1. **Selecione um Setor**: Na barra lateral esquerda, escolha um dos 20 setores disponíveis
2. **Configure os Parâmetros**:
   - Defina a data inicial (padrão: 01/01/2023)
   - Defina a data final (padrão: 31/12/2023)
   - Ajuste a quantidade de linhas da tabela fato (100 a 100.000)
3. **Visualize o Preview**: Veja um dashboard automático com 2.000 linhas de exemplo
4. **Gere os Dados**: Clique em "Gerar base agora" com seus parâmetros customizados
5. **Analise e Exporte**: 
   - Aba "Base de Dados": Visualize tabelas, métricas e preview
   - Aba "Dashboard": Explore visualizações interativas
   - Download automático em arquivo ZIP com todos os CSVs

### Amostra Automática vs. Dados Reais

- **Preview Automático**: 2.000 linhas geradas automaticamente para visualizar o setor
- **Dados Reais**: Personalize a quantidade de linhas (até 100.000) e período de tempo

---

## 📊 Setores Disponíveis e Estrutura de Dados

Abaixo está a tabela detalhada de todos os 20 setores suportados, suas tabelas e principais dimensões:

| Emoji | Setor | Tabela Fato | Principais Dimensões |
|-------|-------|-------------|----------------------|
| 🛒 | Varejo | FatoVendas | Cliente, Produto, Vendedor, Filial, Geografia |
| 💰 | Financeiro | FatoTransacao | Conta, Agência, Produto, Cliente |
| 🏥 | Saúde | FatoAtendimento | Paciente, Médico, Procedimento, Unidade |
| 💻 | Tecnologia | FatoContrato | Cliente, Produto, Agente, Plano |
| 📚 | Educação | FatoMatricula | Aluno, Curso, Instrutor, Unidade |
| 🚚 | Logística | FatoEntrega | Transportadora, Rota, Cliente, Produto |
| ⚡ | Energia | FatoConsumo | Consumidor, Medidor, Subestação, Tarifa |
| 📡 | Telecom | FatoChamada | Assinante, Plano, Torre, Serviço |
| 🏭 | Indústria | FatoProducao | Máquina, Insumo, Produto, Operador |
| 🌾 | Agronegócio | FatoSafra | Cultura, Propriedade, Insumo, Colheita |
| 🏨 | Hotelaria | FatoReserva | Hóspede, Hotel, Quarto, Canal, Período |
| 🎬 | Streaming | FatoPlay | Assinante, Conteúdo, Artista, Gênero |
| 🏪 | E-commerce | FatoPedido | Cliente, Produto, Frete, Pagamento, Vendedor |
| 🏢 | Recursos Humanos | FatoHorasTrabalhadas | Funcionário, Projeto, Cargo, Departamento |
| 🚗 | Mobilidade | FatoViagem | Motorista, Passageiro, Rota, Veículo, Aplicativo |
| 🏦 | Fintech | FatoTransacao | Usuário, Cartão, Comerciante, Dispositivo, Antifraude |
| ✈️ | Turismo | FatoViagem | Passageiro, Pacote, Agência, Destino |
| 🏠 | Imobiliário | FatoVenda | Vendedor, Imóvel, Corretor, Tipo, Localização |
| 🛡️ | Seguros | FatoApolice | Segurado, Tipo, Corretor, Ramo, Sinistro |
| 🏗️ | Construção Civil | FatoObra | Obra, Custo, Material, Fornecedor, Etapa |

**Todos os setores incluem:** `dCalendario` com colunas Data, Ano, Mês, MêsAno, IdMesAno

---

## 🔧 Como Adicionar um Novo Setor

O projeto foi estruturado para facilitar a adição de novos setores de negócio. Siga o passo a passo:

### Passo 1: Criar o Gerador de Dados

Crie um arquivo `generators/meu_novo_setor.py` com uma função geradora:

```python
"""generators/meu_novo_setor.py — Setor: Meu Novo Setor"""

from datetime import date
import pandas as pd
from .helpers import new_ids, dcalendario, rand_dates

def gerar_meu_novo_setor(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    """
    Gera dados sintéticos para Meu Novo Setor.
    
    Args:
        n: Número de linhas da tabela fato
        start: Data inicial
        end: Data final
    
    Returns:
        Dicionário com tabelas do Star Schema (chave: nome da tabela, valor: DataFrame)
    """
    
    # Definir número de registros para cada dimensão
    n_entidade1 = min(n, 1000)
    n_entidade2 = min(500, n // 10)
    
    # Criar tabelas dimensão
    dim_entidade1 = pd.DataFrame({
        "id_entidade1": new_ids(n_entidade1),
        "nome": [f"Entidade {i}" for i in range(1, n_entidade1 + 1)],
        # ... mais colunas
    })
    
    dim_entidade2 = pd.DataFrame({
        "id_entidade2": new_ids(n_entidade2),
        # ... colunas
    })
    
    # Criar tabela fato
    fato_tabela = pd.DataFrame({
        "id_fato": new_ids(n),
        "id_entidade1": np.random.choice(dim_entidade1["id_entidade1"], n),
        "id_entidade2": np.random.choice(dim_entidade2["id_entidade2"], n),
        "data": rand_dates(start, end, n),
        "valor": np.random.uniform(100, 5000, n),
        # ... mais métricas
    })
    
    # Retornar dicionário com todas as tabelas
    return {
        "DimEntidade1": dim_entidade1,
        "DimEntidade2": dim_entidade2,
        "FatoTabela": fato_tabela,
        "dCalendario": dcalendario(start, end),
    }
```

### Passo 2: Exportar no `__init__.py`

Abra `generators/__init__.py` e adicione:

```python
from .meu_novo_setor import gerar_meu_novo_setor

__all__ = [
    # ... geradores existentes
    "gerar_meu_novo_setor",
]
```

### Passo 3: Registrar no `config.py`

Abra `config.py` e adicione:

```python
from generators import (
    # ... imports existentes
    gerar_meu_novo_setor,
)

SETORES = {
    # ... setores existentes
    "🆕 Meu Novo Setor": gerar_meu_novo_setor,
}

SETORES_INFO = [
    # ... setores existentes
    ("🆕", "Meu Novo Setor", "Descrição breve do que este setor gera"),
]
```

### Passo 4: (Opcional) Adicionar Dashboard Customizado

Para adicionar visualizações customizadas, edite `ui/dashboard.py` e adicione uma função para seu setor.

**Pronto!** Seu novo setor agora estará disponível na barra lateral, nos flip-cards e no sistema de geração de dados.

---

## 📝 Detalhes Técnicos

### Funções Auxiliares (`generators/helpers.py`)

- **`new_ids(n)`**: Gera n IDs sequenciais e únicos
- **`dcalendario(start, end)`**: Cria tabela de datas com colunas de negócio
- **`rand_dates(start, end, n)`**: Gera n datas aleatórias no intervalo
- **`to_zip(dict_dataframes, nome_arquivo)`**: Compacta múltiplos DataFrames em ZIP

### Padrão de Dados

Cada gerador segue um padrão consistente:

1. **Dimensões**: Dados descritivos (clientes, produtos, locais, etc.)
2. **Fato**: Transações/eventos com métricas e chaves estrangeiras
3. **Calendário**: Tabela de datas para análises temporais
4. **Normalização**: Sem redundância de dados, relacionamentos bem definidos

### Caching com Streamlit

- Preview de 2.000 linhas é cacheado por setor (rápido)
- Dados reais não são cacheados (sempre frescos)
- Regenerar preview: limpar cache no menu Streamlit

---

## 🎯 Casos de Uso

### Desenvolvimento de BI
Gere dados realistas para desenvolver e testar dashboards antes de trabalhar com dados reais.

### Educação e Treinamento
Crie conjuntos de dados de diferentes setores para ensinar modelagem de BI e análise de dados.

### Demonstração de Produtos
Apresente ferramentas BI (Power BI, Tableau) com dados contextualizados de vários setores.

### Testes e QA
Valide pipelines ETL e modelos de dados com volumes conhecidos de dados sintéticos.

### Prototipagem Rápida
Crie rapidamente MVPs de soluções de BI sem aguardar dados reais.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para adicionar novos setores ou melhorias:

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/novo-setor`)
3. Commit suas mudanças (`git commit -m 'Adiciona novo setor'`)
4. Push para a branch (`git push origin feature/novo-setor`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto é de código aberto. Consulte o arquivo LICENSE para detalhes.

---

## 📧 Contato

**Desenvolvedor:** Rodrigo Aiosa  
**GitHub:** [RodrigoAiosa](https://github.com/RodrigoAiosa)  
**Repositório:** [bi_data_generator](https://github.com/RodrigoAiosa/bi_data_generator)

---

## 🎓 Recursos Adicionais

### Power BI Integration
Os dados gerados são totalmente compatíveis com Power BI:
- Star Schema nativo
- Tabela de datas para análises temporais
- CSVs prontos para importação
- Recomendações de relacionamentos

### Tableau & Qlik Sense
Igualmente compatíveis com outras ferramentas:
- Estrutura relacional clara
- Sem ambiguidades ou ciclos
- Dados limpos e validados

### Melhores Práticas
- Use a tabela `dCalendario` para análises de tempo
- Relacione todas as tabelas fato com as dimensões apropriadas
- Utilize IDs para melhor performance
- Considere agregações para volumes maiores que 50.000 linhas

---

**Desenvolvido com ❤️ para a comunidade de BI e Data Analytics**
