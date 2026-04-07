# BI Data Generator PRO

## Visão Geral do Projeto

O **BI Data Generator PRO** é uma ferramenta robusta e interativa, desenvolvida em Python com Streamlit, projetada para gerar conjuntos de dados sintéticos no modelo **Star Schema**. Esses dados são ideais para projetos de Business Intelligence (BI), sendo compatíveis com ferramentas como Power BI, Tableau, Qlik Sense e outras plataformas de análise de dados. A aplicação permite aos usuários criar bases de dados realistas para diversos setores de negócio, facilitando o desenvolvimento, teste e demonstração de dashboards e relatórios de BI sem a necessidade de dados reais sensíveis.

## Funcionalidades Principais

- **Geração de Dados Multi-Setor**: Suporte para 20 setores de negócio distintos, incluindo Varejo, Financeiro, Saúde, Tecnologia, Educação, Logística, Energia, Telecom, Indústria, Agronegócio, Hotelaria, Streaming, E-commerce, Recursos Humanos, Mobilidade, Fintech, Turismo, Imobiliário, Seguros e Construção Civil. Cada setor possui um gerador de dados especializado que simula transações e entidades relevantes para aquele domínio.
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


'''
bi_data_generator/
├── app.py ← Ponto de entrada da aplicação Streamlit
├── config.py ← Mapeamento de setores, configurações globais e constantes
├── requirements.txt ← Dependências do projeto
├── styles/
│ ├── init.py
│ └── css.py ← Estilos CSS e tema da aplicação
├── generators/
│ ├── init.py ← Exporta as funções geradoras de dados
│ ├── helpers.py ← Funções auxiliares (geração de IDs, dCalendario, etc.)
│ ├── agronegocio.py ← Gerador de dados para o setor de Agronegócio
│ ├── construcao_civil.py ← Gerador de dados para Construção Civil
│ ├── ecommerce.py ← Gerador de dados para o setor de E-commerce
│ ├── educacao.py ← Gerador de dados para o setor de Educação
│ ├── energia.py ← Gerador de dados para o setor de Energia
│ ├── financeiro.py ← Gerador de dados para o setor Financeiro
│ ├── fintech.py ← Gerador de dados para o setor de Fintech
│ ├── hotelaria.py ← Gerador de dados para o setor de Hotelaria
│ ├── imobiliario.py ← Gerador de dados para o setor Imobiliário
│ ├── industria.py ← Gerador de dados para o setor Industrial
│ ├── logistica.py ← Gerador de dados para o setor de Logística
│ ├── mobilidade.py ← Gerador de dados para o setor de Mobilidade
│ ├── rh.py ← Gerador de dados para o setor de Recursos Humanos
│ ├── saude.py ← Gerador de dados para o setor de Saúde
│ ├── seguros.py ← Gerador de dados para o setor de Seguros
│ ├── streaming.py ← Gerador de dados para o setor de Streaming
│ ├── tecnologia.py ← Gerador de dados para o setor de Tecnologia
│ ├── telecom.py ← Gerador de dados para o setor de Telecomunicações
│ ├── turismo.py ← Gerador de dados para o setor de Turismo
│ └── varejo.py ← Gerador de dados para o setor de Varejo
└── ui/
├── init.py
├── dashboard.py ← Funções para renderização dos dashboards interativos
├── estado_inicial.py ← Componentes da tela inicial e flip-cards
├── hero.py ← Componente de cabeçalho visual (Hero Section)
├── resultado.py ← Componentes para exibição dos resultados e download
└── sidebar.py ← Componentes da barra lateral (inputs do usuário)

'''
