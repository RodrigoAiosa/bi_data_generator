# BI Data Generator PRO

## Visão Geral do Projeto

O **BI Data Generator PRO** é uma ferramenta robusta e interativa, desenvolvida em Python com Streamlit, projetada para gerar conjuntos de dados sintéticos no modelo **Star Schema**. Esses dados são ideais para projetos de Business Intelligence (BI), sendo compatíveis com ferramentas como Power BI, Tableau, Qlik Sense e outras plataformas de análise de dados. A aplicação permite aos usuários criar bases de dados realistas para diversos setores de negócio, facilitando o desenvolvimento, teste e demonstração de dashboards e relatórios de BI sem a necessidade de dados reais sensíveis.

## Funcionalidades Principais

- **Geração de Dados Multi-Setor**: Suporte para 16 setores de negócio distintos, incluindo Varejo, Financeiro, Saúde, Tecnologia, Educação, Logística, Energia, Telecom, Indústria, Agronegócio, Hotelaria, Streaming, E-commerce, Recursos Humanos, Mobilidade e Fintech. Cada setor possui um gerador de dados especializado que simula transações e entidades relevantes para aquele domínio.
- **Estrutura Star Schema**: Todos os conjuntos de dados são gerados seguindo o modelo Star Schema, com tabelas fato e tabelas dimensão, otimizadas para análise de BI.
- **dCalendario Integrado**: Cada base de dados inclui uma tabela `dCalendario` (tabela de datas) compatível com Power Query, facilitando a criação de análises temporais.
- **Dashboards Interativos**: A aplicação oferece dashboards interativos e específicos para cada setor, construídos com Plotly, permitindo a visualização e exploração imediata dos dados gerados diretamente na interface do Streamlit.
- **Configuração Flexível**: Os usuários podem definir o setor, o período de tempo (data de início e fim) e o volume de linhas (até 100.000 registros) para a tabela fato, proporcionando flexibilidade na criação de cenários de dados.
- **Exportação Conveniente**: Os dados gerados são exportados como múltiplos arquivos CSV, organizados e compactados em um único arquivo ZIP, pronto para ser importado em qualquer ferramenta de BI.
- **Interface Intuitiva**: Desenvolvido com Streamlit, o aplicativo possui uma interface de usuário limpa, moderna e responsiva, com um tema visual profissional.

## Tecnologias Utilizadas

- **Python**: Linguagem de programação principal.
- **Streamlit**: Framework para construção da interface web interativa.
- **Pandas**: Biblioteca para manipulação e análise de dados.
- **NumPy**: Biblioteca para computação numérica.
- **Faker**: Biblioteca para geração de dados sintéticos realistas.
- **Plotly**: Biblioteca para criação de gráficos interativos e dashboards.

## Estrutura do Projeto

```
bi_data_generator/
├── app.py                  ← Ponto de entrada da aplicação Streamlit
├── config.py               ← Mapeamento de setores, configurações globais e constantes
├── requirements.txt        ← Dependências do projeto
├── styles/
│   ├── __init__.py
│   └── css.py              ← Estilos CSS e tema da aplicação
├── generators/
│   ├── __init__.py         ← Exporta as funções geradoras de dados
│   ├── helpers.py          ← Funções auxiliares (geração de IDs, dCalendario, etc.)
│   ├── agronegocio.py      ← Gerador de dados para o setor de Agronegócio
│   ├── ecommerce.py        ← Gerador de dados para o setor de E-commerce
│   ├── educacao.py         ← Gerador de dados para o setor de Educação
│   ├── energia.py          ← Gerador de dados para o setor de Energia
│   ├── financeiro.py       ← Gerador de dados para o setor Financeiro
│   ├── fintech.py          ← Gerador de dados para o setor de Fintech
│   ├── hotelaria.py        ← Gerador de dados para o setor de Hotelaria
│   ├── industria.py        ← Gerador de dados para o setor Industrial
│   ├── logistica.py        ← Gerador de dados para o setor de Logística
│   ├── mobilidade.py       ← Gerador de dados para o setor de Mobilidade
│   ├── rh.py               ← Gerador de dados para o setor de Recursos Humanos
│   ├── saude.py            ← Gerador de dados para o setor de Saúde
│   ├── streaming.py        ← Gerador de dados para o setor de Streaming
│   ├── tecnologia.py       ← Gerador de dados para o setor de Tecnologia
│   ├── telecom.py          ← Gerador de dados para o setor de Telecomunicações
│   └── varejo.py           ← Gerador de dados para o setor de Varejo
└── ui/
    ├── __init__.py
    ├── dashboard.py        ← Funções para renderização dos dashboards interativos
    ├── estado_inicial.py   ← Componentes da tela inicial e flip-cards
    ├── hero.py             ← Componente de cabeçalho visual (Hero Section)
    ├── resultado.py        ← Componentes para exibição dos resultados e download
    └── sidebar.py          ← Componentes da barra lateral (inputs do usuário)
```

## Instalação e Execução

Para configurar e executar o BI Data Generator PRO localmente, siga os passos abaixo:

1.  **Clone o repositório:**

    ```bash
    git clone https://github.com/RodrigoAiosa/bi_data_generator.git
    cd bi_data_generator
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**

    ```bash
    python -m venv .venv
    # No Linux/macOS:
    source .venv/bin/activate
    # No Windows:
    .venv\Scripts\activate
    ```

3.  **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação Streamlit:**

    ```bash
    streamlit run app.py
    ```

    A aplicação será aberta automaticamente no seu navegador padrão.

## Como Adicionar um Novo Setor

O projeto é modular e permite a fácil adição de novos setores de negócio. Para incluir um novo gerador de dados, siga estas etapas:

1.  **Crie um novo arquivo de gerador:**
    Crie um arquivo `generators/meu_novo_setor.py` e defina uma função `gerar_meu_novo_setor(n_linhas, data_inicio, data_fim) -> dict[str, pd.DataFrame]`. Esta função deve retornar um dicionário onde as chaves são os nomes das tabelas (ex: `FatoVendas`, `DimCliente`) e os valores são DataFrames do Pandas.

2.  **Exporte a função no `__init__.py`:**
    Adicione a nova função ao arquivo `generators/__init__.py` para que ela seja exportada e reconhecida pelo sistema:

    ```python
    # Em generators/__init__.py
    from .meu_novo_setor import gerar_meu_novo_setor
    # ... (outras importações)

    __all__ = [
        # ... (outros geradores)
        "gerar_meu_novo_setor",
    ]
    ```

3.  **Registre o novo setor no `config.py`:**
    Atualize o arquivo `config.py` para incluir o novo setor nos dicionários `SETORES` e `SETORES_INFO`:

    ```python
    # Em config.py
    from generators import gerar_meu_novo_setor # Importe a nova função

    # ... (outras definições)

    SETORES = {
        # ... (outros setores)
        "✨ Meu Novo Setor": gerar_meu_novo_setor,
    }

    SETORES_INFO = [
        # ... (outras informações de setor)
        ("✨", "Meu Novo Setor", "Descrição breve do que este setor gera"),
    ]
    ```

Após esses passos, o novo setor estará disponível na barra lateral da aplicação, com seu próprio gerador de dados e dashboard interativo (se implementado na função geradora ou no `dashboard.py`).

## Setores Disponíveis e Estrutura de Dados

Abaixo está uma tabela detalhada dos setores atualmente suportados, suas principais tabelas fato e dimensões, e as chaves de relacionamento. Todos os conjuntos de dados incluem uma tabela `dCalendario` para análise temporal.

| Emoji | Setor             | Tabela Fato         | Principais Dimensões                                  |
|-------|-------------------|---------------------|-------------------------------------------------------|
| 🛒    | Varejo            | FatoVendas          | Cliente, Produto, Vendedor, Filial, Geografia         |
| 💰    | Financeiro        | FatoTransacao       | Conta, Agência, Produto, Cliente                      |
| 🏥    | Saúde             | FatoAtendimento     | Paciente, Médico, Procedimento, Unidade               |
| 💻    | Tecnologia        | FatoContrato        | Cliente, Produto, Agente, Plano                       |
| 📚    | Educação          | FatoMatricula       | Aluno, Curso, Instrutor, Unidade                      |
| 🚚    | Logística         | FatoEntrega         | Transportadora, Rota, Cliente, Produto                |
| ⚡    | Energia           | FatoConsumo         | Consumidor, Medidor, Subestação, Tarifa               |
| 📡    | Telecom           | FatoChamada         | Assinante, Plano, Torre, Serviço                      |
| 🏭    | Indústria         | FatoProducao        | Máquina, Insumo, Produto, Operador                    |
| 🌾    | Agronegócio       | FatoSafra           | Cultura, Propriedade, Insumo, Colheita                |
| 🏨    | Hotelaria         | FatoReserva         | Hóspede, Hotel, Quarto, Canal, Período                |
| 🎬    | Streaming         | FatoPlay            | Assinante, Conteúdo, Artista, Gênero                  |
| 🏪    | E-commerce        | FatoPedido          | Cliente, Produto, Frete, Pagamento, Vendedor          |
| 🏢    | Recursos Humanos  | FatoHorasTrabalhadas| Funcionário, Projeto, Cargo, Departamento             |
| 🚗    | Mobilidade        | FatoViagem          | Motorista, Passageiro, Rota, Veículo, Aplicativo      |
| 🏦    | Fintech           | FatoTransacao       | Usuário, Cartão, Comerciante, Dispositivo, Antifraude |

Todas as bases incluem `dCalendario` compatível com Power Query, com colunas como `Data`, `Ano`, `Mes`, `MesAno`, `IdMesAno`.
