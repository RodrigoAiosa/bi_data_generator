# 📊 BI Data Generator

Gerador de **dados fictícios em modelo estrela** (fato + dimensões + calendário) para quem quer praticar **Power BI, DAX, SQL e modelagem dimensional** sem depender de bases reais, sensíveis ou difíceis de conseguir.

Em poucos segundos você escolhe um setor de negócio, define um período e um volume de linhas, e recebe um pacote completo com tabela fato, dimensões, tabela calendário, medidas DAX sugeridas, dicionário de dados e — se quiser — os scripts SQL para recriar tudo em um banco relacional.

> Aplicação construída em **Streamlit** e distribuída publicamente em:
> 🔗 **<https://rodrigoaiosa.streamlit.app>**

---

## 📚 Sumário

- [Visão geral](#-visão-geral)
- [Estrutura do repositório](#-estrutura-do-repositório)
- [Qual versão usar?](#-qual-versão-usar)
- [Instalação e execução local](#-instalação-e-execução-local)
- [Como usar o app](#-como-usar-o-app)
- [Setores de negócio disponíveis](#-setores-de-negócio-disponíveis-70)
- [Modelo de dados gerado (Star Schema)](#-modelo-de-dados-gerado-star-schema)
- [Recursos principais](#-recursos-principais)
- [Exportação SQL (DDL / INSERT)](#-exportação-sql-ddl--insert)
- [Modo anomalias](#-modo-anomalias)
- [Internacionalização (PT/EN)](#-internacionalização-pten)
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
