# 📊 BI Data Generator

Gerador de **dados fictícios em modelo estrela** (fato + dimensões + calendário) para quem quer praticar **Power BI, DAX, SQL e modelagem dimensional** sem depender de bases reais, sensíveis ou difíceis de conseguir.

Em poucos segundos você escolhe um setor de negócio, define um período e um volume de linhas, e recebe um pacote completo com tabela fato, dimensões, tabela calendário, medidas DAX sugeridas, dicionário de dados e — se quiser — os scripts SQL para recriar tudo em um banco relacional.

> Aplicação construída em **Streamlit** e distribuída publicamente em:
> 🔗 **https://rodrigoaiosa.streamlit.app**

---

## 📚 Sumário

- [Visão geral](#-visão-geral)
- [Estrutura do repositório](#-estrutura-do-repositório)
- [Qual versão usar?](#-qual-versão-usar)
- [Instalação e execução local](#-instalação-e-execução-local)
- [Como usar o app](#-como-usar-o-app)
- [Setores de negócio disponíveis](#-setores-de-negócio-disponíveis-55)
- [Modelo de dados gerado (Star Schema)](#-modelo-de-dados-gerado-star-schema)
- [Recursos principais](#-recursos-principais)
- [Exportação SQL (DDL / INSERT)](#-exportação-sql-ddl--insert)
- [Modo anomalias](#-modo-anomalias)
- [Internacionalização (PT/EN)](#-internacionalização-ptEN)
- [Deploy no Streamlit Cloud](#-deploy-no-streamlit-cloud)
- [Requisitos e dependências](#-requisitos-e-dependências)
- [Roadmap / ideias futuras](#-roadmap--ideias-futuras)
- [Aviso legal](#-aviso-legal)

---

## 🧭 Visão geral

Este repositório reúne **múltiplos projetos** de geração de dados sintéticos para BI, todos seguindo o mesmo princípio: gerar bases realistas, com relacionamentos íntegros, prontas para importar em ferramentas de análise (Power BI, Tableau, Excel, Python, SQL).

O objetivo é resolver um problema comum de quem estuda ou ensina Business Intelligence: **falta de dados bons para praticar**. Criar tabelas manualmente é lento, não tem sazonalidade real, e raramente reflete um modelo dimensional coerente. O BI Data Generator resolve isso gerando, em segundos:

- Tabela **Fato** com chaves estrangeiras e métricas numéricas;
- Tabelas **Dimensão** com atributos descritivos e chave primária;
- Tabela **dCalendario** (compatível com Power Query) para análises de série temporal;
- **Medidas DAX** sugeridas automaticamente com base nas colunas geradas;
- **Dicionário de dados** explicando cada tabela e coluna;
- Scripts **SQL (DDL/INSERT)** para recriar a base em SQL Server, PostgreSQL ou MySQL;
- Um **dashboard interativo** de pré-visualização, direto no navegador.

---

## 🗂 Estrutura do repositório

O repositório evoluiu ao longo do tempo e hoje contém a versão principal na raiz, além de versões anteriores/alternativas mantidas em subpastas para referência e compatibilidade com deploys já existentes.

```
bi_data_generator/
├── app.py                      # ⭐ App principal (BI Data Generator PRO) — versão mais completa
├── config.py                   # Configuração da página, slider de volume e dicionário de 55 setores
├── i18n.py                     # Sistema de internacionalização (PT-BR / EN)
├── helpers.py                  # Funções utilitárias no nível raiz
├── requirements.txt            # Dependências do app principal
├── LICENSE
│
├── generators/                 # 🏭 Um módulo por setor de negócio (60 arquivos)
│   ├── __init__.py             # Exporta todas as funções gerar_<setor>
│   ├── helpers.py              # dcalendario(), new_ids(), get_faker(), rand_dates(), to_zip()...
│   ├── dicionario.py           # Gera o dicionário de dados (CSV zipado) com descrições PT/EN
│   ├── medidas.py              # Gera a bateria de medidas DAX sugeridas por tabela fato
│   ├── sql_generator.py        # Gera DDL / INSERT / script completo (SQL Server, PostgreSQL, MySQL)
│   ├── varejo.py, financeiro.py, saude.py, ecommerce.py, ... (um arquivo por setor)
│   └── ...
│
├── ui/                          # 🎨 Componentes de interface do app principal
│   ├── hero.py                  # Seção de topo (hero) da landing
│   ├── sidebar.py                # Sidebar: busca de setor, período, volume, botão gerar, export SQL
│   ├── estado_inicial.py         # Tela inicial / onboarding ("Como usar")
│   ├── resultado.py               # Métricas, preview de tabelas, medidas DAX, download do ZIP
│   └── dashboard.py                # Dashboard interativo (gráficos com Plotly/Streamlit)
│
├── styles/
│   ├── css.py                   # CSS customizado injetado no Streamlit (tema escuro/roxo)
│   └── seo.py                   # (opcional) meta tags de SEO
│
├── bi_data_generator/            # 📦 Versão completa "standalone" (55 setores) — código-fonte espelhado
│   ├── app.py
│   ├── config.py
│   └── generators/
│
└── escoladax_simples/            # 📦 Versão enxuta (8 setores) — ideal para começar
    ├── app.py
    ├── requirements.txt
    └── generators_bi/
        ├── __init__.py
        ├── helpers.py
        ├── setores.py
        └── medidas.py
```

> 💡 As pastas `bi_data_generator/` e `escoladax_simples/` são projetos Streamlit **independentes**, cada um com seu próprio `app.py` e `requirements.txt`. O `app.py` da raiz do repositório é a versão mais atual e mais completa (a que está publicada em produção).

---

## 🤔 Qual versão usar?

| Versão | Pasta | Setores | Indicado para |
|---|---|---|---|
| **BI Data Generator PRO** (recomendada) | raiz do repositório (`app.py`) | 55 setores | Uso geral, estudo avançado, portfólio, prática de Power BI/DAX/SQL completa |
| **BI Data Generator (completo)** | `bi_data_generator/` | 55 setores | Espelho da versão principal, útil se você quiser hospedar separadamente |
| **EscolaDAX Simples** | `escoladax_simples/` | 8 setores (Varejo, Financeiro, Saúde, E-commerce, Logística, Educação, Imobiliário, SaaS B2B) | Quem está começando e quer uma interface mais enxuta, com menos opções |

---

## 🚀 Instalação e execução local

### Pré-requisitos
- Python 3.10+ (recomendado 3.11)
- pip

### Versão principal (raiz do repositório)

```bash
git clone https://github.com/RodrigoAiosa/bi_data_generator.git
cd bi_data_generator
pip install -r requirements.txt
streamlit run app.py
```

O Streamlit vai abrir automaticamente em `http://localhost:8501`.

### Versão "EscolaDAX Simples"

```bash
cd escoladax_simples
pip install -r requirements.txt
streamlit run app.py
```

### Versão "BI Data Generator" (pasta espelhada)

```bash
cd bi_data_generator
pip install -r requirements.txt
streamlit run app.py
```

> ⚠️ Cada subpasta tem seu próprio `requirements.txt` — instale as dependências dentro da pasta do app que for rodar.

---

## 🖱 Como usar o app

1. **Escolha o setor** — use a caixa de busca na barra lateral para filtrar entre os 55 setores disponíveis (ex.: digitar "saúde", "log", "marketing").
2. **Defina o período** — datas de início e fim; a tabela `dCalendario` é gerada automaticamente cobrindo esse intervalo.
3. **Defina o volume de dados** — slider de 100 a 100.000 linhas na tabela fato (o volume das dimensões é ajustado proporcionalmente).
4. *(Opcional)* **Ative "Injetar anomalias"** para adicionar problemas propositais nos dados (veja [Modo anomalias](#-modo-anomalias)).
5. Clique em **"Gerar base agora"**. Uma barra de progresso mostra as etapas reais: criação de dimensões → geração da fato → cálculo de métricas → compactação do ZIP.
6. Navegue pelas abas:
   - **📦 Base de Dados** — resumo das tabelas, preview de cada uma, medidas DAX sugeridas e botão de download do `.zip`;
   - **📊 Dashboard** — visualizações automáticas (KPIs, distribuições por categoria, séries temporais) geradas a partir da fato.
7. Baixe o **dicionário de dados** (Excel/CSV zipado) com a descrição de cada tabela e coluna.
8. *(Opcional)* Na barra lateral, gere o **script SQL** (DDL, INSERT ou completo) no dialeto desejado.

Antes mesmo de clicar em "Gerar", o app já mostra uma aba de **preview automático**: uma amostra de 2.000 linhas do setor selecionado, para você ter uma ideia dos dados e do dashboard antes de configurar os parâmetros finais.

---

## 🏭 Setores de negócio disponíveis (55)

| Setor | Conteúdo típico |
|---|---|
| 🌱 AgTech | Sensores IoT, drones, monitoramento e agricultura de precisão |
| 🌾 Agronegócio | Safras, culturas, propriedades e insumos |
| 🍔 Alimentos & Bebidas | Produção, plantas, produtos e fornecedores |
| 🏛️ Arquitetura & Design | Projetos, serviços, honorários e gestão de obras |
| 🎬 Audiovisual & Produtora | Produções, orçamentos, recursos e bilheteria |
| ✈️ Aviação Civil | Voos, passageiros, aeronaves e aeroportos |
| 💄 Beleza & Estética | Vendas, serviços, agenda e salões parceiros |
| 🧬 Biotecnologia | Genômica, CRISPR, pesquisa e experimentos laboratoriais |
| 🏢 Condomínio & Facilities | Cotas, despesas, ocorrências e manutenção |
| 🏗️ Construção Civil | Obras, custos, materiais e fornecedores |
| 🤝 CRM | Oportunidades, contas, contatos e atividades comerciais |
| ♻️ Economia Circular | Reciclagem, logística reversa, créditos de carbono e ESG |
| 🏪 E-commerce | Pedidos, clientes, produtos, fretes e pagamentos |
| 📚 Educação | Matrículas, alunos, cursos e instrutores |
| ⚡ Energia | Consumo, medidores, subestações e tarifas |
| 🚀 Espacial & Aeroespacial | Missões, satélites, lançamentos e operações |
| 🏟️ Esportes | Partidas, atletas, clubes e competições |
| 🎉 Eventos & Entretenimento | Ingressos, fornecedores, receitas e NPS |
| 💊 Farmacêutico | Produtos, representantes, vendas e estoque |
| 💰 Financeiro | Transações bancárias, contas e agências |
| 🏦 Fintech | Transações, cartões, usuários, comerciantes e antifraude |
| 🌲 Florestal & Papel | Talhões, espécies, colheita e carbono |
| 🏷️ Franquias | Unidades, royalties, taxas e faturamento |
| 🎮 Games & eSports | Partidas, jogadores, jogos e monetização in-game |
| 🏛️ Governo & Setor Público | Despesas, receitas, licitações e contratos |
| 🏨 Hotelaria | Reservas, hóspedes, hotéis, quartos e canais |
| 🏠 Imobiliário | Vendas, aluguéis, imóveis e corretores |
| 🏭 Indústria | Produção, máquinas, insumos e operadores |
| ⚖️ Jurídico | Processos, advogados, clientes e tribunais |
| 🔬 Laboratório & Diagnóstico | Exames, pacientes, laudos e convênios |
| 🚚 Logística | Entregas, transportadoras, rotas e clientes |
| 🚴 Logística Urbana | Entregas last mile, entregadores e SLA |
| 📣 Marketing Digital | Campanhas, canais, performance e conversões |
| 📲 Migração Claro Brasil (Portabilidade) | Migrações IN/OUT, serviços, operadoras e motivos de portabilidade |
| ⛏️ Mineração | Extrações, minas, minerais e equipamentos |
| 🚗 Mobilidade | Viagens, motoristas, passageiros, rotas e veículos |
| 👗 Moda & Vestuário | Coleções, vendas, estoque e devoluções |
| 🐟 Pesca & Aquicultura | Espécies, produção, qualidade e biomassa |
| 🐾 Pet & Veterinária | Atendimentos, pets, tutores e serviços veterinários |
| 🛢️ Petróleo & Gás | Produção, poços, plataformas e custos operacionais |
| 🏢 Recursos Humanos | Horas trabalhadas, funcionários, projetos e cargos |
| ☁️ SaaS B2B | Assinaturas, MRR, churn, NPS e planos |
| 💧 Saneamento & Água | Consumo, faturas, estações de tratamento e ligações |
| 🏥 Saúde | Atendimentos, pacientes, médicos e procedimentos |
| 🧠 Saúde Mental | Sessões, profissionais, pacientes e diagnósticos |
| 🛡️ Seguros | Apólices, segurados, corretores e sinistros |
| 🦄 Startups & Venture Capital | Rodadas, valuations, MRR e métricas de crescimento |
| 🎬 Streaming | Plays, assinantes, conteúdos, artistas |
| 💻 Tecnologia | Contratos SaaS, clientes e planos |
| 📡 Telecom | Chamadas, assinantes, planos e torres |
| 🧵 Têxtil & Confecção | Fibras, produção, eficiência e clientes |
| 🚛 Transporte | Viagens, frota, combustível, manutenção e rentabilidade |
| ✈️ Turismo | Viagens, pacotes, agências e destinos |
| 🛒 Varejo | Vendas, clientes, produtos e filiais |
| ✈️ Viagens Corporativas | Viajantes, custos, política de viagem e SLA |

A versão **EscolaDAX Simples** disponibiliza 8 destes setores (Varejo, Financeiro, Saúde, E-commerce, Logística, Educação, Imobiliário e SaaS B2B).

---

## 🗃 Modelo de dados gerado (Star Schema)

Cada base gerada segue o padrão de modelagem dimensional (esquema estrela):

- **Tabela Fato** (`Fato*`) — uma linha por evento/transação, com chaves estrangeiras (`sk_*` / `id_*`) para as dimensões e colunas numéricas (valores, quantidades, métricas).
- **Tabelas Dimensão** (`Dim*` ou nome do setor) — chave primária e atributos descritivos (nomes, categorias, localizações etc.).
- **Tabela `dCalendario`** — gerada automaticamente para o período escolhido, com colunas `Data`, `Ano`, `Mes`, `MesAno` e `IdMesAno`, pronta para relacionar com Power Query/Power BI.
- **Tabelas Bridge** (`Bridge*`) — quando o setor exige, tabelas de associação para relacionamentos N:N.

**Dica de modelagem sugerida pelo próprio app:** importe os CSVs no Power BI e crie relacionamentos usando as colunas `sk_*` (chave estrangeira) da tabela Fato até a chave primária correspondente em cada dimensão, e conecte `dCalendario[Data]` ao campo de data da tabela Fato.

---

## ✨ Recursos principais

- **55 setores de negócio** com dados contextualmente coerentes (nomes, categorias, faixas de valores e distribuições plausíveis para cada indústria).
- **Volume configurável**: de 100 a 100.000 linhas na tabela fato via slider.
- **Período configurável**: qualquer intervalo de datas, com geração automática da `dCalendario`.
- **Busca de setor** na barra lateral, com índice construído a partir do nome e da descrição de cada setor.
- **Preview automático**: antes mesmo de gerar a base completa, uma amostra de 2.000 linhas já alimenta um dashboard de pré-visualização.
- **Barra de progresso real**, com etapas (dimensões → fato → métricas → compactação).
- **Medidas DAX sugeridas automaticamente** (`generators/medidas.py`), organizadas por categoria e prontas para colar no Power BI.
- **Dicionário de dados** (`generators/dicionario.py`): explica o significado de cada tabela e coluna com base em padrões de nome (`id_`, `valor_`, `qtd_`, `status`, `data_`, etc.), disponível em PT/EN e exportado como ZIP.
- **Dashboard interativo** (`ui/dashboard.py` / `render_dashboard`): KPIs automáticos (total de registros, soma de valores monetários, quantidades, número de tabelas), distribuição por categorias e séries temporais.
- **Exportação em ZIP**: todas as tabelas em CSV, compactadas em um único arquivo pronto para importar no Power BI, Tableau, Excel ou Python.
- **Exportação SQL** (DDL/INSERT/completo) em múltiplos dialetos — veja a seção dedicada abaixo.
- **Modo anomalias**: injeta problemas propositais nos dados para prática de análise de causa raiz.
- **Interface bilíngue** PT-BR / EN, com toggle na barra lateral.
- **Tema visual customizado** (`styles/css.py`), com identidade escura/roxa e cards estatísticos.

---

## 🗄 Exportação SQL (DDL / INSERT)

Além do ZIP de CSVs, a barra lateral do app principal permite gerar diretamente um script SQL para o setor selecionado (`generators/sql_generator.py`), com suporte a:

- **Dialetos**: SQL Server, PostgreSQL e MySQL — com mapeamento automático de tipos (`INT`/`BIGINT`, `DECIMAL`/`NUMERIC`, `BIT`/`BOOLEAN`/`TINYINT(1)`, `NVARCHAR`/`VARCHAR`, `DATETIME2`/`TIMESTAMP`/`DATETIME`, entre outros).
- **Tipos de script**:
  - 📋 **CREATE TABLE (DDL)** — apenas a estrutura das tabelas, com tipos inferidos, chaves primárias (`id_`/`sk_`) e índices sugeridos. Ideal para criar o banco do zero.
  - 💾 **INSERT INTO (dados)** — popula as tabelas com os dados gerados, no volume definido no slider, em blocos de 500 linhas por `INSERT`.
  - 📦 **Completo (DDL + INSERT)** — os dois combinados em um único arquivo, pronto para colar no SSMS, DBeaver ou `psql` e recriar o banco inteiro.
- **Overrides de tamanho de coluna** para campos conhecidos (CPF, CNPJ, CNH, placa, UF, e-mail, telefone, CEP, URL, descrição, observação, endereço etc.), evitando `VARCHAR` genérico demais.
- **Preview do script** direto na interface antes do download (com truncamento visual para scripts muito longos).

---

## 🧪 Modo anomalias

Ao ativar o toggle **"Injetar anomalias nos dados"**, o app aplica quatro tipos de problemas propositais na tabela fato, pensados para prática de análise de causa raiz:

1. **Spike de churn/cancelamento** — força um mês aleatório a concentrar cancelamentos (quando há coluna booleana + coluna de data).
2. **Margem negativa** — cerca de 4% dos registros recebem margem/lucro/desconto negativo e exagerado.
3. **Sazonalidade extrema** — um trimestre aleatório sofre queda artificial de 70% no valor principal.
4. **Outliers de valor** — cerca de 1% dos registros recebem valores 10 a 30 vezes acima da média.

Quando o modo está ativo, um aviso é exibido na interface (`⚠️ Modo anomalia ativo`) para deixar claro que os dados contêm problemas intencionais.

---

## 🌐 Internacionalização (PT/EN)

Todo o texto da interface — sidebar, hero, dashboard, mensagens de erro, dicionário de dados, script SQL — é controlado pelo módulo `i18n.py`, com mais de 800 linhas de strings mapeadas para **Português (pt)** e **Inglês (en)**. O toggle de idioma fica na barra lateral e afeta:

- Textos da interface e mensagens;
- Nomes de meses na `dCalendario`;
- Locale do `Faker` usado para gerar nomes, endereços e demais dados fictícios (`pt_BR` ou equivalente em inglês).

---

## ☁️ Deploy no Streamlit Cloud

Como há múltiplos apps no mesmo repositório, ao criar o app no Streamlit Cloud aponte o **"Main file path"** para o `app.py` desejado, por exemplo:

- `app.py` (versão principal, recomendada)
- `bi_data_generator/app.py`
- `escoladax_simples/app.py`

Cada app usa o `requirements.txt` da sua própria pasta (ou da raiz, no caso do app principal).

---

## 📦 Requisitos e dependências

Dependências principais (arquivo `requirements.txt` da raiz):

```
streamlit
pandas
numpy
faker
plotly
```

Python 3.10+ é recomendado devido ao uso de type hints modernos (`dict[str, pd.DataFrame]`) presentes no código.

---

## 🗺 Roadmap / ideias futuras

Ideias que fazem sentido para evolução do projeto (não implementadas ainda):

- Exportação direta em formato Parquet/Delta Table;
- Templates prontos de `.pbit` (Power BI) por setor;
- Mais opções de granularidade temporal na `dCalendario` (semana ISO, ano fiscal);
- Testes automatizados por gerador de setor;
- Documentação por gerador (schema de colunas de cada setor).

Contribuições e sugestões são bem-vindas via *issues* e *pull requests*.

---

## ⚖️ Aviso legal

Todos os dados gerados são **100% fictícios e sintéticos**, criados com o pacote [`Faker`](https://faker.readthedocs.io/) e regras de negócio simuladas. Nenhuma informação real de pessoas, empresas ou entidades é utilizada. O projeto é destinado a fins **educacionais e de portfólio** — para estudo de Power BI, DAX, modelagem dimensional e SQL.
