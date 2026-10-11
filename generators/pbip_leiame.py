"""Texto do LEIA-ME.txt incluído no zip de download."""

LEIAME_PBIP = """BI DATA GENERATOR - Base + Projeto Power BI
===========================================

O que vem neste .zip
  *.csv            Bases: tabelas fato e dimensao (modelo estrela) + dCalendario
  PowerBI/         Projeto Power BI (.pbip) com modelo semantico (relacionamentos
                   e medidas DAX) e um painel de exemplo minimalista, com
                   filtros (segmentacoes), cartoes de KPI e graficos
  model.tmdl       Opcional: mesmo modelo, para colar no Tabular Editor

Como abrir o painel (Power BI Desktop)
  1. Extraia TODO o .zip em uma pasta (ex.: C:\\Dados\\MeuSetor).
  2. Abra o Power BI Desktop e va em Arquivo > Abrir > Procurar e selecione
     o arquivo PowerBI\\<setor>.pbip.
     (Se pedir, habilite em Opcoes > Recursos de visualizacao:
      "Salvar como projeto do Power BI (.pbip)" e
      "Formato de metadados de relatorio do Power BI (PBIR)").
  3. Em Transformar dados > Gerenciar parametros, altere CaminhoPasta para a
     pasta onde estao os CSVs, terminando com barra invertida
     (ex.: C:\\Dados\\MeuSetor\\).
  4. Clique em Atualizar. Os visuais passam a mostrar os dados.

Dicas
  - Cada pagina do painel corresponde a uma tabela fato.
  - Os visuais sao um ponto de partida: arraste novas medidas da tabela
    "Medidas" e personalize cores e layout a vontade.
"""
