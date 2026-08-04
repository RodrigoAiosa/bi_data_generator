# 📊 BI Data Generator

Gerador de **dados fictícios em modelo estrela** (fato + dimensões + calendário) para quem quer praticar **Power BI, DAX, SQL e modelagem dimensional** sem depender de bases reais, sensíveis ou difíceis de conseguir.

Em poucos segundos você escolhe um setor de negócio, define um período e um volume de linhas, e recebe um pacote completo com tabela fato, dimensões, tabela calendário, medidas DAX sugeridas, modelo TMDL pronto para o Power BI, dicionário de dados e, se quiser, os scripts SQL para recriar tudo em um banco relacional.

O app principal tem **6 abas**: o Gerador de Setores (100 bases prontas), o Automatizar BI (envie sua própria planilha e gere medidas/modelo automaticamente), o Simulador de Certificação PL-300 (quiz de prática para a certificação oficial da Microsoft), o Dados Causais (gera uma relação causa-efeito conhecida de propósito, em cima do setor que você já gerou), o Formatar DAX (cola uma expressão bagunçada e recebe ela formatada) e o Formatar M (o mesmo princípio, mas para código Power Query).

> Aplicação construída em **Streamlit** e distribuída publicamente em:
> 🔗 **https://rodrigoaiosa.streamlit.app**

---

## 📚 Sumário

- [Visão geral](#-visão-geral)
- [Estrutura do repositório](#-estrutura-do-repositório)
- [Qual versão usar?](#-qual-versão-usar)
- [Instalação e execução local](#-instalação-e-execução-local)
- [Como usar o app](#-como-usar-o-app)
- [Setores de negócio disponíveis](#-setores-de-negócio-disponíveis-100)
- [Quantidade de medidas DAX por setor](#-quantidade-de-medidas-dax-geradas-por-setor)
- [Modelo de dados gerado (Star Schema)](#-modelo-de-dados-gerado-star-schema)
- [Recursos principais](#-recursos-principais)
- [Exportação SQL (DDL / INSERT)](#-exportação-sql-ddl--insert)
- [Modo anomalias, deriva temporal e case de negócio](#-modo-anomalias-deriva-temporal-e-case-de-negócio)
- [Automatizar BI (suas próprias planilhas)](#-automatizar-bi-suas-próprias-planilhas)
- [Simulador de Certificação PL-300](#-simulador-de-certificação-pl-300)
- [Dados Causais (relação causa-efeito conhecida)](#-dados-causais-relação-causa-efeito-conhecida)
- [Formatar DAX](#-formatar-dax)
- [Formatar M](#-formatar-m)
- [Log de acesso e painel de uso](#-log-de-acesso-e-painel-de-uso)
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
- **Modelo TMDL** com tabelas, relacionamentos e medidas prontos para importar no Power BI;
- **Dicionário de dados** explicando cada tabela e coluna;
- Scripts **SQL (DDL/INSERT)** para recriar a base em SQL Server, PostgreSQL ou MySQL;
- Um **case de negócio fictício**, gerado automaticamente, transformando a base num exercício com objetivo real a resolver;
- Um modo **Automatizar BI**, que aplica esse mesmo motor de medidas/modelo em **planilhas que você mesmo envia** (.csv/.xlsx);
- Um **Simulador de Certificação PL-300**, com perguntas originais organizadas nos 4 domínios oficiais do exame.

---

## 🗂 Estrutura do repositório

O repositório evoluiu ao longo do tempo e hoje contém a versão principal na raiz, além de versões anteriores/alternativas mantidas em subpastas para referência e compatibilidade com deploys já existentes.

```
bi_data_generator/
├── app.py                      # ⭐ App principal (BI Data Generator PRO), versão mais completa
├── config.py                   # Configuração da página, slider de volume e dicionário de 100 setores
├── i18n.py                     # Sistema de internacionalização (PT-BR / EN)
├── helpers.py                  # Funções utilitárias no nível raiz
├── log_acesso.py               # Log de acesso e uso (sessão, eventos) enviado para uma planilha Google Sheets
├── requirements.txt            # Dependências do app principal
├── LICENSE
│
├── generators/                 # 🏭 Um módulo por setor de negócio (108 arquivos)
│   ├── __init__.py             # Exporta todas as funções gerar_<setor>
│   ├── helpers.py              # dcalendario(), new_ids(), get_faker(), rand_dates(), to_zip()...
│   ├── dicionario.py           # Gera o dicionário de dados (CSV zipado) com descrições PT/EN
│   ├── medidas.py              # Gera a bateria de medidas DAX sugeridas por tabela fato
│   ├── sql_generator.py        # Gera DDL / INSERT / script completo (SQL Server, PostgreSQL, MySQL)
│   ├── tmdl_generator.py       # Gera o modelo TMDL (tabelas, relacionamentos e medidas) para o Power BI
│   ├── case_negocio.py         # Gera o case de negócio fictício que acompanha cada base
│   ├── concept_drift.py        # Injeta deriva temporal (concept drift) genérica na tabela fato
│   ├── dax_formatter.py         # Motor de formatação de expressões DAX (tokenizador + quebra de linha)
│   ├── m_formatter.py           # Motor de formatação de código M / Power Query (mesmo princípio, adaptado)
│   ├── varejo.py, financeiro.py, saude.py, ecommerce.py, ... (um arquivo por setor)
│   └── ...
│
├── ui/                          # 🎨 Componentes de interface do app principal
│   ├── hero.py                  # Seção de topo (hero) da landing
│   ├── sidebar.py                # Sidebar: busca de setor, período, volume, botão gerar, export SQL
│   ├── estado_inicial.py         # Tela inicial / onboarding ("Como usar")
│   ├── resultado.py               # Métricas, preview de tabelas, medidas DAX, gabarito e download do ZIP
│   ├── automatizar_bi.py           # Aba "Automatizar BI": upload de planilha, tipos, medidas e TMDL
│   └── simulador_pl300.py           # Aba "Simulador PL-300": quiz de prática para a certificação
│   └── dados_causais.py             # Aba "Dados Causais": relação causa-efeito conhecida, em cima do setor gerado
│   └── formatar_dax.py              # Aba "Formatar DAX": cola uma expressão bagunçada e recebe ela formatada
│   └── formatar_m.py                # Aba "Formatar M": mesmo princípio, pra código Power Query
│
├── styles/
│   ├── css.py                   # CSS customizado injetado no Streamlit (tema Power BI: amarelo/preto)
│   └── seo.py                   # (opcional) meta tags de SEO
│
├── bi_data_generator/            # 📦 Versão completa "standalone" (55 setores*), código-fonte espelhado
│   ├── app.py
│   ├── config.py
│   └── generators/
│
└── escoladax_simples/            # 📦 Versão enxuta (8 setores), ideal para começar
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
| **BI Data Generator PRO** (recomendada) | raiz do repositório (`app.py`) | 100 setores | Uso geral, estudo avançado, portfólio, prática de Power BI/DAX/SQL completa |
| **BI Data Generator (completo)** | `bi_data_generator/` | 55 setores* | Espelho da versão principal, útil se você quiser hospedar separadamente |
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

> ⚠️ Cada subpasta tem seu próprio `requirements.txt`: instale as dependências dentro da pasta do app que for rodar.

---

## 🖱 Como usar o app

O app abre com **6 abas**: "🏭 Gerador de Setores", "🤖 Automatizar BI", "🎓 Simulador PL-300", "🧬 Dados Causais", "📐 Formatar DAX" e "🔧 Formatar M".

### Aba 🏭 Gerador de Setores

1. **Escolha o setor**: use a caixa de busca na barra lateral para filtrar entre os 100 setores disponíveis (ex.: digitar "saúde", "log", "marketing").
2. **Defina o período**: datas de início e fim; a tabela `dCalendario` é gerada automaticamente cobrindo esse intervalo.
3. **Defina o volume de dados**: slider de 100 a 100.000 linhas na tabela fato (o volume das dimensões é ajustado proporcionalmente).
4. *(Opcional)* **Ative "Injetar anomalias nos dados"** para adicionar problemas propositais (veja [Modo anomalias, deriva temporal e case de negócio](#-modo-anomalias-deriva-temporal-e-case-de-negócio)).
5. *(Opcional)* **Ative "Simular deriva temporal (concept drift)"** para fazer uma categoria ganhar participação gradualmente ao longo do período, sem evento único que explique.
6. Clique em **"Gerar base agora"**. Uma barra de progresso mostra as etapas reais: criação de dimensões, geração da fato, cálculo de métricas, compactação do ZIP.
7. A tela de resultado mostra, nessa ordem:
   - Um **case de negócio fictício**, gerado automaticamente para o setor escolhido;
   - O **resumo das tabelas** geradas e o **preview** de cada uma;
   - As **medidas DAX sugeridas**, organizadas por categoria;
   - O **gabarito** (se anomalia ou deriva temporal estiverem ativas), num expansor colapsado tipo spoiler;
   - O **botão de download** do `.zip` completo.
8. Baixe o **dicionário de dados** (Excel/CSV zipado) com a descrição de cada tabela e coluna.
9. *(Opcional)* Na barra lateral, gere o **script SQL** (DDL, INSERT ou completo) no dialeto desejado.
10. *(Opcional)* Se você já gerou um cenário na aba "🧬 Dados Causais" **antes** de clicar em "Baixar Base", o `.zip` também inclui o CSV causal e o gabarito (veja a seção dedicada).

### Aba 🤖 Automatizar BI

Veja a seção [Automatizar BI (suas próprias planilhas)](#-automatizar-bi-suas-próprias-planilhas) para o passo a passo completo.

### Aba 🎓 Simulador PL-300

Veja a seção [Simulador de Certificação PL-300](#-simulador-de-certificação-pl-300) para o passo a passo completo.

### Aba 🧬 Dados Causais

Veja a seção [Dados Causais (relação causa-efeito conhecida)](#-dados-causais-relação-causa-efeito-conhecida) para o passo a passo completo.

### Aba 📐 Formatar DAX

Veja a seção [Formatar DAX](#-formatar-dax) para o passo a passo completo.

### Aba 🔧 Formatar M

Veja a seção [Formatar M](#-formatar-m) para o passo a passo completo.

---

## 🏭 Setores de negócio disponíveis (100)

| Setor | Conteúdo típico |
|---|---|
| 🏋️ Academia & Fitness | Check-ins, alunos, instrutores, pagamentos e avaliações físicas |
| 📢 Agência de Publicidade | Projetos, campanhas de mídia, equipe e clientes |
| 🌱 AgTech | Sensores IoT, drones, monitoramento e agricultura de precisão |
| 🌾 Agronegócio | Safras, culturas, propriedades e insumos |
| 🍔 Alimentos & Bebidas | Produção, plantas, produtos e fornecedores |
| 🎰 Apostas Esportivas & iGaming | Apostas, jogadores, eventos esportivos e transações |
| 🏛️ Arquitetura & Design | Projetos, serviços, honorários e gestão de obras |
| 🔩 Assistência Técnica de Eletrônicos | Ordens de serviço, técnicos, peças e reparos |
| 🎬 Audiovisual & Produtora | Produções, orçamentos, recursos e bilheteria |
| 🔧 Autopeças & Oficina Mecânica | Peças, serviços, clientes e canais de venda |
| ✈️ Aviação Civil | Voos, passageiros, aeronaves e aeroportos |
| 💄 Beleza & Estética | Vendas, serviços, agenda e salões parceiros |
| 🧬 Biotecnologia | Genômica, CRISPR, pesquisa e experimentos laboratoriais |
| 🪙 Blockchain & Criptomoedas | Transações, moedas, usuários e carteiras digitais |
| 📞 Call Center & BPO | Atendimentos, atendentes, clientes e avaliação de qualidade |
| 📜 Cartório & Serviços Notariais | Atos notariais, tabeliães, clientes e protestos |
| 🎫 Casa Lotérica & Correspondente Bancário | Transações, apostas de loteria, unidades e serviços |
| 🔐 Cibersegurança | Incidentes, vulnerabilidades, ativos e SLA de resposta (SOC) |
| 🎥 Cinema & Exibição | Sessões, filmes, salas e bomboniere |
| 🚙 Concessionária de Veículos | Vendas, veículos, vendedores e test-drives |
| 🏢 Condomínio & Facilities | Cotas, despesas, ocorrências e manutenção |
| 🧾 Consórcios | Parcelas, contemplações, grupos e cotistas |
| 🏗️ Construção Civil | Obras, custos, materiais e fornecedores |
| 📊 Consultoria Empresarial | Projetos, consultores, faturas e clientes |
| 💳 Cooperativa de Crédito | Operações, cooperados, produtos e sobras distribuídas |
| 📦 Correios & Encomendas | Envios, agências, serviços e ocorrências |
| 🪑 Coworking & Espaços Compartilhados | Reservas, assinaturas, espaços e clientes |
| 🤝 CRM | Oportunidades, contas, contatos e atividades comerciais |
| 🖥️ Data Center & Cloud Hosting | Consumo, instâncias, clientes e incidentes |
| 🚁 Drones & Serviços Aéreos | Missões, drones, manutenção e clientes |
| ♻️ Economia Circular | Reciclagem, logística reversa, créditos de carbono e ESG |
| 🏪 E-commerce | Pedidos, clientes, produtos, fretes e pagamentos |
| 📖 Editora & Publicação | Livros, vendas, canais e estoque |
| 📚 Educação | Matrículas, alunos, cursos e instrutores |
| ⚡ Energia | Consumo, medidores, subestações e tarifas |
| 🎓 Ensino Superior | Matrículas, disciplinas, cursos e desempenho acadêmico |
| 🚀 Espacial & Aeroespacial | Missões, satélites, lançamentos e operações |
| 🏟️ Esportes | Partidas, atletas, clubes e competições |
| 🅿️ Estacionamento & Zona Azul | Entradas, estacionamentos, clientes e multas |
| 🎉 Eventos & Entretenimento | Ingressos, fornecedores, receitas e NPS |
| 💊 Farmacêutico | Produtos, representantes, vendas e estoque |
| 💰 Financeiro | Transações bancárias, contas e agências |
| 🏦 Fintech | Transações, cartões, usuários, comerciantes e antifraude |
| 🌲 Florestal & Papel | Talhões, espécies, colheita e carbono |
| 🏷️ Franquias | Unidades, royalties, taxas e faturamento |
| 🥩 Frigorífico & Processamento de Carnes | Abate, produtos, unidades e canais de venda |
| ⚰️ Funerária & Serviços Funerários | Atendimentos, serviços, planos preventivos e clientes |
| 🎮 Games & eSports | Partidas, jogadores, jogos e monetização in-game |
| 🏛️ Governo & Setor Público | Despesas, receitas, licitações e contratos |
| 🖨️ Gráfica & Comunicação Visual | Pedidos, produção, produtos e clientes |
| 🩺 Home Care | Visitas, pacientes, profissionais e ocorrências |
| 🏨 Hotelaria | Reservas, hóspedes, hotéis, quartos e canais |
| 🏠 Imobiliário | Vendas, aluguéis, imóveis e corretores |
| 🏭 Indústria | Produção, máquinas, insumos e operadores |
| 💍 Joalheria & Relojoaria | Vendas, produtos, clientes e assistência técnica |
| ⚖️ Jurídico | Processos, advogados, clientes e tribunais |
| 🔬 Laboratório & Diagnóstico | Exames, pacientes, laudos e convênios |
| 🔨 Leilão | Lances, lotes, arrematantes e arrematações |
| 🚗 Locadora de Veículos | Reservas, frota, clientes, multas e diárias |
| 🛠️ Locação de Equipamentos | Locações, equipamentos, manutenção e clientes |
| 🏖️ Locação por Temporada | Reservas, imóveis, hóspedes e avaliações |
| 🚚 Logística | Entregas, transportadoras, rotas e clientes |
| 🚴 Logística Urbana | Entregas last mile, entregadores e SLA |
| 🪵 Marcenaria & Móveis Planejados | Contratos, projetos, produção e clientes |
| 📣 Marketing Digital | Campanhas, canais, performance e conversões |
| ⚙️ Metalurgia & Siderurgia | Produção, fornos, produtos e vendas |
| 🚇 Metrô & Trem Urbano | Validações, estações, linhas e ocorrências |
| 📲 Migração Claro Brasil (Portabilidade) | Migrações IN/OUT, serviços, operadoras e motivos de portabilidade |
| ⛏️ Mineração | Extrações, minas, minerais e equipamentos |
| 🚗 Mobilidade | Viagens, motoristas, passageiros, rotas e veículos |
| 👗 Moda & Vestuário | Coleções, vendas, estoque e devoluções |
| 🖼️ Museus & Cultura | Visitas, exposições, eventos culturais e ingressos |
| 🦷 Odontologia | Consultas, dentistas, pacientes, procedimentos e convênios |
| 👓 Óptica | Vendas, produtos, clientes e exames de vista |
| 📎 Papelaria & Material Escolar | Vendas, produtos, lojas e estoque |
| 🐄 Pecuária | Fazendas, rebanho, manejo e produção |
| 🐟 Pesca & Aquicultura | Espécies, produção, qualidade e biomassa |
| 🐾 Pet & Veterinária | Atendimentos, pets, tutores e serviços veterinários |
| 🛢️ Petróleo & Gás | Produção, poços, plataformas e custos operacionais |
| 🏊 Piscina & Spa | Serviços, clientes, técnicos e consumo de produtos químicos |
| 🗑️ Reciclagem & Gestão de Resíduos | Coletas, materiais, cooperativas e vendas de material |
| 🏢 Recursos Humanos | Horas trabalhadas, funcionários, projetos e cargos |
| 🍽️ Restaurantes & Food Service | Pedidos, cardápio, unidades, reservas e delivery |
| ☁️ SaaS B2B | Assinaturas, MRR, churn, NPS e planos |
| 💧 Saneamento & Água | Consumo, faturas, estações de tratamento e ligações |
| 🏥 Saúde | Atendimentos, pacientes, médicos e procedimentos |
| 🧠 Saúde Mental | Sessões, profissionais, pacientes e diagnósticos |
| 🔒 Segurança Privada | Escalações, vigilantes, clientes e ocorrências |
| 🛡️ Seguros | Apólices, segurados, corretores e sinistros |
| 🦄 Startups & Venture Capital | Rodadas, valuations, MRR e métricas de crescimento |
| 🎬 Streaming | Plays, assinantes, conteúdos, artistas |
| 💻 Tecnologia | Contratos SaaS, clientes e planos |
| 📡 Telecom | Chamadas, assinantes, planos e torres |
| 🤲 Terceiro Setor & ONGs | Doações, projetos sociais, doadores e execução |
| 🧵 Têxtil & Confecção | Fibras, produção, eficiência e clientes |
| 🚛 Transporte | Viagens, frota, combustível, manutenção e rentabilidade |
| ✈️ Turismo | Viagens, pacotes, agências e destinos |
| 🛒 Varejo | Vendas, clientes, produtos e filiais |
| ✈️ Viagens Corporativas | Viajantes, custos, política de viagem e SLA |
| 🍷 Vinícola & Vitivinicultura | Produção, vinhedos, vinhos e canais de venda |

A versão **EscolaDAX Simples** disponibiliza 8 destes setores (Varejo, Financeiro, Saúde, E-commerce, Logística, Educação, Imobiliário e SaaS B2B).

> \* A pasta `bi_data_generator/` (versão espelhada standalone) ainda está parada em 55 setores. Replique os arquivos de `generators/` e as entradas de `config.py`/`i18n.py` nela caso queira mantê-la em paridade com a raiz (hoje com 100 setores).

---

## 🧮 Quantidade de medidas DAX geradas por setor

Cada setor gera uma quantidade diferente de medidas DAX automaticamente, dependendo de quantas tabelas fato, colunas numéricas e chaves estrangeiras ele tem (setores multi-fato e com mais colunas de valor multiplicam a base de medidas). Somando os 100 setores, o motor já sabe escrever **6.916 medidas DAX diferentes**, sem depender de nenhuma IA.

| Setor | Medidas DAX |
| --- | --- |
| 🚛 Transporte | 303 |
| 📣 Marketing Digital | 215 |
| 🏛️ Governo & Setor Público | 185 |
| 🚗 Mobilidade | 160 |
| ☁️ SaaS B2B | 146 |
| 🛢️ Petróleo & Gás | 140 |
| 🦄 Startups & Venture Capital | 137 |
| 💊 Farmacêutico | 118 |
| 🏪 E-commerce | 116 |
| 🏦 Fintech | 116 |
| 🏟️ Esportes | 103 |
| ⛏️ Mineração | 103 |
| 🤝 CRM | 98 |
| 🌾 Agronegócio | 92 |
| 🍔 Alimentos & Bebidas | 92 |
| 🧵 Têxtil & Confecção | 92 |
| 🚀 Espacial & Aeroespacial | 91 |
| 🐟 Pesca & Aquicultura | 91 |
| ✈️ Viagens Corporativas | 91 |
| 🏋️ Academia & Fitness | 84 |
| 👗 Moda & Vestuário | 83 |
| 🏢 Recursos Humanos | 83 |
| 📢 Agência de Publicidade | 82 |
| 💄 Beleza & Estética | 82 |
| ♻️ Economia Circular | 82 |
| 🎉 Eventos & Entretenimento | 82 |
| 🏷️ Franquias | 82 |
| 🍽️ Restaurantes & Food Service | 82 |
| ⚖️ Jurídico | 81 |
| 🌲 Florestal & Papel | 80 |
| 🎮 Games & eSports | 80 |
| 🎬 Audiovisual & Produtora | 79 |
| 🚗 Locadora de Veículos | 72 |
| 🐄 Pecuária | 72 |
| ✈️ Aviação Civil | 71 |
| 📖 Editora & Publicação | 71 |
| 🥩 Frigorífico & Processamento de Carnes | 71 |
| ⚡ Energia | 70 |
| 🚴 Logística Urbana | 69 |
| 💧 Saneamento & Água | 69 |
| 🏢 Condomínio & Facilities | 63 |
| 🚙 Concessionária de Veículos | 61 |
| 🏖️ Locação por Temporada | 61 |
| 📎 Papelaria & Material Escolar | 61 |
| 🔧 Autopeças & Oficina Mecânica | 60 |
| 📞 Call Center & BPO | 60 |
| 🔐 Cibersegurança | 60 |
| 🎥 Cinema & Exibição | 60 |
| 🖥️ Data Center & Cloud Hosting | 60 |
| 🚁 Drones & Serviços Aéreos | 60 |
| 🖨️ Gráfica & Comunicação Visual | 60 |
| 🏭 Indústria | 60 |
| 🛠️ Locação de Equipamentos | 60 |
| 🖼️ Museus & Cultura | 60 |
| 🍷 Vinícola & Vitivinicultura | 60 |
| 🌱 AgTech | 59 |
| 🧬 Biotecnologia | 59 |
| 🚚 Logística | 59 |
| 🧠 Saúde Mental | 58 |
| 🪙 Blockchain & Criptomoedas | 50 |
| 🎓 Ensino Superior | 50 |
| ⚙️ Metalurgia & Siderurgia | 50 |
| 🦷 Odontologia | 50 |
| 🎰 Apostas Esportivas & iGaming | 49 |
| 📜 Cartório & Serviços Notariais | 49 |
| 🎫 Casa Lotérica & Correspondente Bancário | 49 |
| 📊 Consultoria Empresarial | 49 |
| 📦 Correios & Encomendas | 49 |
| 🪑 Coworking & Espaços Compartilhados | 49 |
| ⚰️ Funerária & Serviços Funerários | 49 |
| 🪵 Marcenaria & Móveis Planejados | 49 |
| 👓 Óptica | 49 |
| 🏊 Piscina & Spa | 49 |
| 🛒 Varejo | 49 |
| 🎬 Streaming | 48 |
| 📡 Telecom | 48 |
| 🔬 Laboratório & Diagnóstico | 47 |
| 📲 Migração Claro Brasil (Portabilidade) | 47 |
| 🧾 Consórcios | 39 |
| 🗑️ Reciclagem & Gestão de Resíduos | 39 |
| 🔩 Assistência Técnica de Eletrônicos | 38 |
| 🏗️ Construção Civil | 38 |
| 💳 Cooperativa de Crédito | 38 |
| 🅿️ Estacionamento & Zona Azul | 38 |
| 🩺 Home Care | 38 |
| 🏨 Hotelaria | 38 |
| 💍 Joalheria & Relojoaria | 38 |
| 🔨 Leilão | 38 |
| 🤲 Terceiro Setor & ONGs | 38 |
| 📚 Educação | 37 |
| 🛡️ Seguros | 37 |
| 💻 Tecnologia | 37 |
| 🏛️ Arquitetura & Design | 36 |
| 🏥 Saúde | 27 |
| 🔒 Segurança Privada | 27 |
| ✈️ Turismo | 27 |
| 💰 Financeiro | 26 |
| 🐾 Pet & Veterinária | 25 |
| 🚇 Metrô & Trem Urbano | 16 |
| 🏠 Imobiliário | 15 |

---

## 🗃 Modelo de dados gerado (Star Schema)

Cada base gerada segue o padrão de modelagem dimensional (esquema estrela):

- **Tabela Fato** (`Fato*`): uma linha por evento/transação, com chaves estrangeiras (`sk_*` / `id_*`) para as dimensões e colunas numéricas (valores, quantidades, métricas).
- **Tabelas Dimensão** (`Dim*` ou nome do setor): chave primária e atributos descritivos (nomes, categorias, localizações etc.).
- **Tabela `dCalendario`**: gerada automaticamente para o período escolhido, com colunas `Data`, `Ano`, `Mes`, `MesAno` e `IdMesAno`, pronta para relacionar com Power Query/Power BI.
- **Tabelas Bridge** (`Bridge*`): quando o setor exige, tabelas de associação para relacionamentos N:N.

**Dica de modelagem sugerida pelo próprio app:** importe os CSVs no Power BI e crie relacionamentos usando as colunas `sk_*` (chave estrangeira) da tabela Fato até a chave primária correspondente em cada dimensão, e conecte `dCalendario[Data]` ao campo de data da tabela Fato.

Em setores onde uma fato referencia outra fato (ex.: despesas ou abastecimentos vinculados a uma viagem específica), o modelo TMDL gerado já resolve automaticamente qualquer ambiguidade de relacionamento: a fato-filha mantém o vínculo ativo com a fato-pai, e tem o link direto com o calendário desativado quando necessário, evitando o erro "caminhos ambíguos" ao aplicar o modelo no Power BI.

---

## ✨ Recursos principais

- **100 setores de negócio** com dados contextualmente coerentes (nomes, categorias, faixas de valores e distribuições plausíveis para cada indústria).
- **Volume configurável**: de 100 a 100.000 linhas na tabela fato via slider.
- **Período configurável**: qualquer intervalo de datas, com geração automática da `dCalendario`.
- **Busca de setor** na barra lateral, com índice construído a partir do nome e da descrição de cada setor.
- **Barra de progresso real**, com etapas (dimensões, fato, métricas, compactação).
- **Medidas DAX sugeridas automaticamente** (`generators/medidas.py`), organizadas por categoria e prontas para colar no Power BI. Somando os 100 setores, já são mais de 6.900 medidas diferentes que o motor sabe escrever sozinho, sem depender de nenhuma IA.
- **Modelo TMDL** (`generators/tmdl_generator.py`): tabelas, relacionamentos e medidas prontos para importar no Power BI (Tabular Editor), com resolução automática de ambiguidade de relacionamento, inclusive em cadeias fato-para-fato.
- **Dicionário de dados** (`generators/dicionario.py`): explica o significado de cada tabela e coluna com base em padrões de nome (`id_`, `valor_`, `qtd_`, `status`, `data_`, etc.), disponível em PT/EN e exportado como ZIP.
- **Case de negócio automático** (`generators/case_negocio.py`): cada base vem com um parágrafo de contexto fictício, adaptado ao setor e ao modo ativo (anomalia, deriva temporal ou nenhum dos dois), transformando a geração num exercício com objetivo real.
- **Gabarito de anomalias e deriva temporal**: quando algum desses modos está ativo, um expansor colapsado (tipo spoiler) revela exatamente o que foi alterado e onde, útil para quem ensina conferir se a análise encontrou o problema certo.
- **Exportação em ZIP**: todas as tabelas em CSV, mais `model.tmdl`, `case_negocio.txt` e (quando aplicável) `gabarito.txt`, compactados em um único arquivo pronto para importar no Power BI, Tableau, Excel ou Python.
- **Exportação SQL** (DDL/INSERT/completo) em múltiplos dialetos, veja a seção dedicada abaixo.
- **Modo anomalias**: injeta problemas propositais nos dados para prática de análise de causa raiz.
- **Deriva temporal (concept drift)**: simula uma categoria ganhando participação gradualmente ao longo do período, para praticar detecção de tendência e mudança de comportamento.
- **Interface bilíngue** PT-BR / EN, com toggle na barra lateral.
- **Tema visual customizado** (`styles/css.py`), inspirado na paleta oficial do Power BI (amarelo e preto).
- **Automatizar BI** (`ui/automatizar_bi.py`): envie sua própria planilha (.csv/.xlsx) e receba medidas DAX completas, tabela Calendario e modelo TMDL, gerados automaticamente a partir das colunas reais que você enviou.
- **Simulador de Certificação PL-300** (`ui/simulador_pl300.py`): quiz de prática com perguntas originais nos 4 domínios oficiais do exame, com correção, nota por domínio, explicação e download do resultado em CSV para acompanhar a evolução ao longo do tempo.
- **Dados Causais** (`ui/dados_causais.py`): gera uma relação causa-efeito conhecida de propósito (com defasagem, confundidor e ruído configuráveis) em cima do setor que você já gerou, com gabarito causal documentado.
- **Formatar DAX** (`ui/formatar_dax.py` + `generators/dax_formatter.py`): cola uma expressão ou medida DAX bagunçada e recebe ela formatada, com quebra de linha por profundidade de parênteses e espaçamento consistente, no mesmo espírito do daxformatter.com.
- **Formatar M** (`ui/formatar_m.py` + `generators/m_formatter.py`): mesmo princípio do formatador de DAX, adaptado pra sintaxe do Power Query (`let...in`, record, lista).
- **Log de acesso** (`log_acesso.py`): registra uso real do app numa planilha Google Sheets, com um painel de análise separado ([`dash_bi_data_generator`](https://github.com/RodrigoAiosa/dash_bi_data_generator)).

---

## 🗄 Exportação SQL (DDL / INSERT)

Além do ZIP de CSVs, a barra lateral do app principal permite gerar diretamente um script SQL para o setor selecionado (`generators/sql_generator.py`), com suporte a:

- **Dialetos**: SQL Server, PostgreSQL e MySQL, com mapeamento automático de tipos (`INT`/`BIGINT`, `DECIMAL`/`NUMERIC`, `BIT`/`BOOLEAN`/`TINYINT(1)`, `NVARCHAR`/`VARCHAR`, `DATETIME2`/`TIMESTAMP`/`DATETIME`, entre outros).
- **Tipos de script**:
  - 📋 **CREATE TABLE (DDL)**: apenas a estrutura das tabelas, com tipos inferidos, chaves primárias (`id_`/`sk_`) e índices sugeridos. Ideal para criar o banco do zero.
  - 💾 **INSERT INTO (dados)**: popula as tabelas com os dados gerados, no volume definido no slider, em blocos de 500 linhas por `INSERT`.
  - 📦 **Completo (DDL + INSERT)**: os dois combinados em um único arquivo, pronto para colar no SSMS, DBeaver ou `psql` e recriar o banco inteiro.
- **Overrides de tamanho de coluna** para campos conhecidos (CPF, CNPJ, CNH, placa, UF, e-mail, telefone, CEP, URL, descrição, observação, endereço etc.), evitando `VARCHAR` genérico demais.
- **Preview do script** direto na interface antes do download (com truncamento visual para scripts muito longos).

---

## 🧪 Modo anomalias, deriva temporal e case de negócio

### Case de negócio automático

Toda base gerada vem acompanhada de um parágrafo de contexto fictício (`generators/case_negocio.py`): você é contratado(a) como Analista de BI numa empresa fictícia do setor escolhido, e recebe um problema de negócio pra resolver com os dados. O texto se adapta automaticamente conforme o cenário:

- **Sem anomalia nem deriva ativas**: uma pergunta de negócio genérica (ex.: entender o desempenho do KPI principal).
- **Com anomalia ativa**: o gatilho aponta pro tipo de sintoma (sem entregar a resposta exata, essa fica só no gabarito).
- **Com deriva temporal ativa**: o gatilho menciona uma mudança de comportamento gradual e não percebida.

O texto vai também no ZIP de download, como `case_negocio.txt`.

### Modo anomalias

Ao ativar o toggle **"Injetar anomalias nos dados"**, o app aplica quatro tipos de problemas propositais na tabela fato, pensados para prática de análise de causa raiz:

1. **Spike de churn/cancelamento**: força um mês aleatório a concentrar cancelamentos (quando há coluna booleana + coluna de data).
2. **Margem negativa**: cerca de 4% dos registros recebem margem/lucro/desconto negativo e exagerado.
3. **Sazonalidade extrema**: um trimestre aleatório sofre queda artificial de 70% no valor principal.
4. **Outliers de valor**: cerca de 1% dos registros recebem valores 10 a 30 vezes acima da média.

### Deriva temporal (concept drift)

Ao ativar o toggle **"Simular deriva temporal (concept drift)"** (`generators/concept_drift.py`), uma categoria de uma coluna categórica da tabela fato (canal, segmento, status etc.) ganha participação **gradualmente** ao longo do período gerado, sem nenhum evento único que explique a mudança. Diferente do modo anomalias (mudanças abruptas e pontuais), esse modo é pensado para praticar detecção de tendência e mudança de comportamento ao longo do tempo.

### Gabarito

Quando qualquer um dos dois modos acima está ativo, um aviso é exibido na interface (`⚠️ Modo anomalia ativo` / `🧬 Deriva temporal ativa`) para deixar claro que os dados contêm alterações intencionais. Um expansor colapsado, tipo spoiler ("🔍 Ver gabarito"), revela exatamente o que foi alterado, onde e quantas linhas foram afetadas, útil para quem ensina conferir se a análise encontrou o problema certo. O gabarito também vai no ZIP de download, como `gabarito.txt`.

---

## 🤖 Automatizar BI (suas próprias planilhas)

A segunda aba do app aplica o mesmo motor de medidas DAX e modelo TMDL usado nos 100 setores prontos, só que em **planilhas que você mesmo envia**, sem depender do padrão Fato/Dimensão dos setores prontos.

### Passo a passo

1. Envie um ou mais arquivos **.csv** ou **.xlsx** (um Excel com várias abas vira várias tabelas separadas automaticamente).
2. Cada tabela aparece num expansor com preview das 10 primeiras linhas e um combobox por coluna, já com um **tipo sugerido automaticamente** (Texto, Número inteiro/decimal, Data, Data e hora, Verdadeiro/Falso, Chave/ID), que você pode ajustar.
3. Clique em **"🧮 Gerar medidas DAX"**. O motor gera:
   - **Perguntas de negócio** montadas a partir das colunas reais que você enviou (não são um exemplo fictício);
   - **Medidas DAX completas**: agregações básicas, contagens, percentual de participação e, quando existir coluna de data, **Time Intelligence completo** (Mês Anterior, %MoM, Ano Anterior, %YoY, YTD, MTD);
   - Uma tabela **Calendario** gerada automaticamente, cobrindo do menor ao maior valor de data encontrado nas tabelas enviadas;
   - Um **model.tmdl completo**, com os relacionamentos detectados automaticamente entre as tabelas (mesma lógica de resolução de ambiguidade usada no Gerador de Setores).
4. Baixe o que precisar: só as medidas (`.txt`), só o `Calendario.csv`, ou o **modelo completo** (`.zip` com os CSVs de cada tabela + `model.tmdl`, pronto para importar no Power BI ou no Tabular Editor).

### Reparos automáticos

Alguns arquivos exportados de forma errada chegam com todas as colunas despejadas como texto corrido numa única coluna (o cabeçalho vira o nome de uma única coluna cheia de vírgulas). O Automatizar BI detecta esse padrão e **desmembra automaticamente** de volta em colunas de verdade, avisando na tela quando isso acontece. Também corrige automaticamente acentuação quebrada (texto UTF-8 lido como Latin-1, tipo "CobranÃ§a" em vez de "Cobrança").

---

## 🎓 Simulador de Certificação PL-300

A terceira aba é um quiz de prática para a certificação **PL-300 (Microsoft Certified: Power BI Data Analyst Associate)**, com **perguntas 100% originais** (escritas para este projeto, nunca reproduzidas de prova real ou de sites de "exam dump"), organizadas nos 4 domínios oficiais do exame:

- Preparar os dados
- Modelar os dados
- Visualizar e analisar os dados
- Gerenciar e proteger o Power BI

Algumas perguntas usam a base que você acabou de gerar na aba do Gerador de Setores como contexto (nome do setor, tabela fato, coluna real).

### Como usar

1. Escolha quantas perguntas quer no simulado (5/10/15/20) e clique em **"🎲 Sortear novo simulado"**.
2. Responda todas as perguntas no formulário.
3. Clique em **"✅ Corrigir simulado"** para ver a nota geral, o desempenho por domínio, e a revisão pergunta a pergunta com explicação.
4. Baixe o **"📥 Baixar resultado desta prova (.csv)"**.

### Acompanhando a evolução ao longo do tempo

Cada prova corrigida gera um CSV com uma linha por pergunta respondida, no formato:

```
data_hora;pergunta;resposta_aluno;resposta_correta;total_acertos;total_erros;%total_acerto
```

O `data_hora` (fuso de Brasília) marca o momento exato daquela tentativa, e os campos `total_acertos`/`total_erros`/`%total_acerto` se repetem em toda linha do arquivo, representando o resultado geral daquela prova. Guardando o arquivo baixado a cada nova tentativa e empilhando as linhas de vários arquivos numa mesma planilha (ex.: colar um embaixo do outro no Excel/Google Sheets), dá para montar o próprio histórico de evolução ao longo do tempo, sem depender de nenhuma conta ou login.

### Fontes oficiais (recomendado usar junto)

Este simulador não substitui o exame real nem o material oficial. Um expansor na própria tela linka direto para:

- [Practice Assessment oficial (gratuito), no Microsoft Learn](https://learn.microsoft.com/en-us/credentials/certifications/data-analyst-associate/practice/assessment?assessment-type=practice&assessmentId=48&practice-assessment-type=certification)
- [Guia de estudo oficial da prova](https://aka.ms/pl300-StudyGuide)
- [Página da certificação PL-300](https://learn.microsoft.com/en-us/credentials/certifications/data-analyst-associate/)

---

## 🧬 Dados Causais (relação causa-efeito conhecida)

Diferente do resto do gerador, onde os dados são só **estatisticamente plausíveis**, essa aba constrói uma relação de causa e efeito **conhecida de propósito**, em cima do setor que você já gerou. Serve para praticar inferência causal, teste A/B e marketing mix modeling com a resposta certa documentada, algo que datasets sintéticos comuns não oferecem.

### Como funciona

1. Gere uma base normalmente na aba "🏭 Gerador de Setores" primeiro (a aba "Dados Causais" avisa e pede isso, caso ainda não tenha sido feito).
2. Escolha, entre as colunas numéricas reais da tabela fato daquele setor, **qual coluna é a CAUSA** e **qual coluna representa o EFEITO**.
3. Defina se a causa **aumenta** ou **reduz** o efeito, se quer incluir um **confundidor** (uma sazonalidade cíclica que afeta o efeito por fora da causa escolhida), a **força do efeito causal** (%), a **defasagem** (quantas semanas depois a causa realmente aparece no efeito) e a **intensidade do ruído** estatístico.
4. Clique em **"🧬 Gerar cenário causal"**.

### O que é real e o que é simulado

- A coluna de **causa** usa os **valores reais** da sua base, agregados por semana.
- A coluna de **efeito** é **100% simulada** pela fórmula causal (defasagem + confundidor + ruído). Ela não usa os valores reais da coluna escolhida na base original, isso é necessário para garantir que o gabarito seja confiável.
- Um expansor colapsado ("🔍 Ver gabarito causal") documenta a força do efeito, a defasagem exata, se há confundidor e a intensidade do ruído usados.

### Validação

Em testes com vários setores diferentes, a correlação medida **com a defasagem correta é sempre mais forte** do que sem considerar a defasagem (ex.: de 0,21 para 0,93 num teste real), confirmando que o mecanismo causal realmente se manifesta nos dados gerados, não é só uma promessa.

### Downloads

- Dentro da própria aba: **"📥 Baixar dados (.csv)"** e **"📥 Baixar gabarito causal (.txt)"**.
- Se você já tiver gerado um cenário causal **antes** de clicar em "Baixar Base" na aba "Gerador de Setores", o `.zip` principal daquele setor também inclui automaticamente o CSV causal (nomeado `fato_<setor>_causais.csv`) e o `gabarito_causal.txt`.

---

## 📐 Formatar DAX

Cola uma expressão ou medida DAX bagunçada (sem espaço, tudo numa linha só) e recebe ela formatada, cada argumento de função numa linha própria quando a expressão é longa ou tem múltiplos argumentos, `VAR`/`RETURN` cada um na sua linha, espaçamento consistente ao redor de operadores.

É uma **implementação própria** (`generators/dax_formatter.py`), não chama nem depende do daxformatter.com: um tokenizador reconhece funções, colunas/medidas (`Tabela[Coluna]`, `[Medida]`), operadores, `VAR`/`RETURN` e strings, e um motor de renderização decide, pela profundidade de parênteses, quando quebrar cada argumento numa linha própria.

### Como usar

1. Cole a expressão DAX no campo de texto (ou clique em **"💡 Usar exemplo"** para testar sem ter uma medida em mãos, um exemplo diferente é sorteado a cada clique, entre 7 opções, sem repetir o do clique anterior).
2. Clique em **"📐 Formatar"**.
3. O resultado aparece formatado, com indentação e quebra de linha, pronto para copiar direto do bloco de código.
4. Baixe o resultado em `.dax` se quiser guardar.

### O que o formatador aceita

- Uma expressão solta (ex.: `SUM(FatoVendas[valor_total])`);
- Uma medida completa no formato `Nome da Medida = expressão`;
- Expressões com `VAR`/`RETURN`;
- Nomes de medida, coluna e tabela com acentuação (ex.: "Preço Médio", "Mês Anterior").

---

## 🔧 Formatar M

Cola um código M (Power Query) bagunçado, tudo numa linha só, e recebe ele formatado: bloco `let ... in ...` com cada passo em sua própria linha, expressões longas quebradas por profundidade de parênteses/colchetes/chaves, identificadores entre aspas (`#"Nome do Passo"`) preservados.

É uma **implementação própria** (`generators/m_formatter.py` + `ui/formatar_m.py`), reaproveitando o mesmo princípio do formatador de DAX (tokenizar e quebrar por profundidade), adaptado pra sintaxe própria do M: suporta os 3 tipos de agrupamento (`()` chamada de função, `{}` lista, `[]` record).

### Como usar

1. Cole o código M no campo de texto (ou clique em **"💡 Usar exemplo"**, um exemplo diferente é sorteado a cada clique, entre 5 opções, sem repetir o do clique anterior).
2. Clique em **"🔧 Formatar"**.
3. O resultado aparece formatado, pronto para copiar direto do bloco de código.
4. Baixe o resultado em `.m` se quiser guardar.

### O que o formatador aceita

- Um bloco completo `let ... in ...`, com qualquer número de passos;
- Uma expressão solta, sem `let`/`in` (ex.: `Table.SelectRows(Source, each [Coluna] > 100)`);
- Identificadores entre aspas com espaço no nome (ex.: `#"Changed Type"`, `#"Expanded Clientes"`);
- Nomes de coluna e passo com acentuação (ex.: `[Preço]`, `"Preço Médio"`).

---

## 📊 Log de acesso e painel de uso

O app registra automaticamente eventos de uso (início de sessão, geração de base, download de ZIP/dicionário/SQL) numa planilha do Google Sheets, via `log_acesso.py` e um Web App do Google Apps Script.

- O log é **best-effort**: se o webhook não estiver configurado ou a chamada falhar, o app continua funcionando normalmente, só sem gravar aquele evento.
- Os horários gravados usam sempre o fuso de Brasília (`America/Sao_Paulo`), independente de onde o servidor do Streamlit estiver rodando.
- Para configurar, defina `log_webhook_url` em `st.secrets` com a URL do seu Web App do Apps Script (veja o cabeçalho de `log_acesso.py` para o passo a passo completo de publicação).
- Existe um **painel de acesso separado** (outro projeto Streamlit, [`dash_bi_data_generator`](https://github.com/RodrigoAiosa/dash_bi_data_generator)) que lê essa mesma planilha e mostra KPIs, gráficos e filtros (Ano, Mês, Dia, Setor, Ação, Status, Dispositivo) sobre o uso real do app.

---

## 🌐 Internacionalização (PT/EN)

Todo o texto da interface (sidebar, hero, resultado, case de negócio, mensagens de erro, dicionário de dados, script SQL) é controlado pelo módulo `i18n.py`, com mais de 800 linhas de strings mapeadas para **Português (pt)** e **Inglês (en)**. O toggle de idioma fica na barra lateral e afeta:

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

Todos os dados gerados são **100% fictícios e sintéticos**, criados com o pacote [`Faker`](https://faker.readthedocs.io/) e regras de negócio simuladas. Nenhuma informação real de pessoas, empresas ou entidades é utilizada. O projeto é destinado a fins **educacionais e de portfólio**, para estudo de Power BI, DAX, modelagem dimensional e SQL.
