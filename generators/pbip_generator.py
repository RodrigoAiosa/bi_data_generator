"""
generators/pbip_generator.py

Gera um Power BI Project (PBIP) completo: a estrutura oficial de pastas que o
Power BI Desktop abre exatamente como abre um .pbix (mesma experiência visual),
só que baseada em arquivos de texto (TMDL para o modelo, JSON para o
relatório) em vez de um binário proprietário — que não há como gerar de forma
confiável fora do próprio Power BI Desktop.

Reaproveita as funções já testadas de generators/tmdl_generator.py (geração de
tabela, relacionamentos e medidas), só reorganizando o conteúdo na estrutura
de múltiplos arquivos que o PBIP nativo espera (em vez do script único de
"createOrReplace" usado para colar no Tabular Editor).

O relatório vem com uma página em branco (sem visuais) — o valor principal
está no modelo semântico já vir 100% pronto: tabelas, relacionamentos e todas
as medidas DAX, prontas para arrastar num canvas em branco.
"""

from __future__ import annotations

import io
import zipfile

import pandas as pd

from generators.tmdl_generator import _medidas_tmdl, _relacionamentos, _tabela_tmdl

_CAMINHO_PADRAO = "C:\\Dados\\"


def _dedentar(bloco: str) -> str:
    """Remove exatamente 1 nível de indentação (tab) de cada linha.

    As funções de generators/tmdl_generator.py foram escritas para produzir
    um script 'createOrReplace' (formato usado para colar no Tabular Editor),
    por isso todo o conteúdo já vem indentado 1 nível a mais do que um
    arquivo .tmdl nativo de um projeto PBIP espera (onde 'table X' fica na
    coluna 0, não indentado como filho de um bloco 'createOrReplace').
    """
    linhas = bloco.split("\n")
    return "\n".join(l[1:] if l.startswith("\t") else l for l in linhas)


def _expressions_tmdl() -> str:
    bruto = (
        '\texpression CaminhoPasta = \n'
        f'\t\t\t"{_CAMINHO_PADRAO}" meta [IsParameterQuery=true, List={{"{_CAMINHO_PADRAO}"}}, '
        f'DefaultValue="{_CAMINHO_PADRAO}", Type="Text", IsParameterQueryRequired=true]\n'
        "\t\tannotation PBI_ResultType = Text\n"
    )
    return _dedentar(bruto)


def _model_tmdl(nomes_tabelas: list[str]) -> str:
    linhas = [
        "model Model",
        "\tculture: pt-BR",
        "\tdiscourageImplicitMeasures",
        "\tsourceQueryCulture: pt-BR",
        "",
        f'\tannotation PBI_QueryOrder = {list(nomes_tabelas)!r}'.replace("'", '"'),
        "",
    ]
    for nome in nomes_tabelas:
        linhas.append(f"\tref table {nome}")
    linhas.append("")
    return "\n".join(linhas)


def _database_tmdl() -> str:
    return "database\n\tcompatibilityLevel: 1567\n"


def _pbip_json(nome_setor: str) -> str:
    return (
        '{\n'
        '  "version": "1.0",\n'
        '  "artifacts": [\n'
        '    {\n'
        f'      "report": {{ "path": "{nome_setor}.Report" }}\n'
        '    }\n'
        '  ],\n'
        '  "settings": { "enableAutoRecovery": true }\n'
        '}\n'
    )


def _definition_pbir(nome_setor: str) -> str:
    return (
        '{\n'
        '  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",\n'
        '  "version": "4.0",\n'
        '  "datasetReference": {\n'
        f'    "byPath": {{ "path": "../{nome_setor}.SemanticModel" }}\n'
        '  }\n'
        '}\n'
    )


def _report_json() -> str:
    return (
        '{\n'
        '  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.0.0/schema.json",\n'
        '  "themeCollection": {},\n'
        '  "filterConfig": {},\n'
        '  "objects": {},\n'
        '  "settings": {},\n'
        '  "resourcePackages": [],\n'
        '  "annotations": []\n'
        '}\n'
    )


def _report_version_json() -> str:
    return '{\n  "version": "4.0"\n}\n'


def _pages_json(page_name: str) -> str:
    return (
        '{\n'
        '  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",\n'
        f'  "pageOrder": ["{page_name}"],\n'
        f'  "activePageName": "{page_name}"\n'
        '}\n'
    )


def _page_json(page_name: str, display_name: str) -> str:
    return (
        '{\n'
        '  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.4.0/schema.json",\n'
        f'  "name": "{page_name}",\n'
        f'  "displayName": "{display_name}",\n'
        '  "displayOption": "FitToPage",\n'
        '  "height": 720,\n'
        '  "width": 1280\n'
        '}\n'
    )


def _definition_pbism() -> str:
    return '{\n  "version": "4.0",\n  "settings": {}\n}\n'


def _instrucoes_txt(nome_setor: str) -> str:
    return (
        f"BI Data Generator PRO — Projeto Power BI (PBIP): {nome_setor}\n"
        f"{'=' * 60}\n\n"
        "COMO ABRIR:\n"
        f"1. Extraia todo o conteúdo deste ZIP numa pasta (ex.: C:\\PBIP\\{nome_setor}\\).\n"
        f"2. Dê 2 cliques no arquivo \"{nome_setor}.pbip\" — o Power BI Desktop abre\n"
        "   automaticamente com o modelo (tabelas, relacionamentos e todas as medidas\n"
        "   DAX) já pronto, e uma página de relatório em branco.\n\n"
        "IMPORTANTE — antes de atualizar os dados:\n"
        "O modelo lê os CSVs a partir de um parâmetro chamado \"CaminhoPasta\", que por\n"
        f"padrão aponta para \"{_CAMINHO_PADRAO}\". Você precisa ajustá-lo para a pasta\n"
        "\"Data\" que veio dentro deste mesmo ZIP:\n"
        "  a) No Power BI Desktop, vá em Página Inicial > Transformar Dados > Editar\n"
        "     Parâmetros;\n"
        "  b) Em \"CaminhoPasta\", cole o caminho completo da pasta Data extraída\n"
        f"     (ex.: C:\\PBIP\\{nome_setor}\\Data\\ — IMPORTANTE: termine com uma barra\n"
        "     invertida \\);\n"
        "  c) Clique em OK e depois em \"Fechar e Aplicar\".\n\n"
        "O QUE JÁ VEM PRONTO:\n"
        "- Todas as tabelas (dimensões, fato e calendário), com tipos de dado corretos;\n"
        "- Todos os relacionamentos entre as tabelas;\n"
        "- Todas as medidas DAX sugeridas para este setor, organizadas por pasta.\n\n"
        "O QUE VOCÊ PRECISA MONTAR:\n"
        "- Os visuais (gráficos, cartões, tabelas) — o relatório vem com uma página em\n"
        "  branco de propósito, pronta para você arrastar os campos do modelo.\n\n"
        "Formato do arquivo: este é um Power BI Project (PBIP), o formato oficial mais\n"
        "novo da Microsoft — o Power BI Desktop abre exatamente como abre um .pbix.\n"
    )


def gerar_pbip(nome_setor: str, tabelas: dict[str, pd.DataFrame]) -> bytes:
    """
    Gera um Power BI Project (PBIP) completo em um ZIP, pronto para extrair e
    abrir no Power BI Desktop (arquivo .pbip na raiz).

    Inclui: modelo semântico completo (tabelas, relacionamentos, medidas DAX),
    uma página de relatório em branco, os CSVs de dados e um arquivo de
    instruções.
    """
    nome_projeto = nome_setor.replace(" ", "_").replace("/", "-")
    report_folder = f"{nome_projeto}.Report"
    model_folder = f"{nome_projeto}.SemanticModel"
    page_name = "ReportSection1"

    nomes_tabelas = list(tabelas.keys())
    tem_medidas = bool(_medidas_tmdl(tabelas).strip())
    if tem_medidas:
        nomes_tabelas = nomes_tabelas + ["Medidas"]

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # ── Raiz do projeto ──────────────────────────────────────────────
        zf.writestr(f"{nome_projeto}.pbip", _pbip_json(nome_projeto))
        zf.writestr("LEIA-ME.txt", _instrucoes_txt(nome_projeto))
        zf.writestr(
            ".gitignore",
            "**/.pbi/localSettings.json\n**/.pbi/cache.abf\n",
        )

        # ── Dados (CSVs que o M vai ler via CaminhoPasta) ──────────────────
        for nome_tabela, df in tabelas.items():
            zf.writestr(f"Data/{nome_tabela}.csv", df.to_csv(index=False))

        # ── SemanticModel ──────────────────────────────────────────────────
        zf.writestr(f"{model_folder}/definition.pbism", _definition_pbism())
        zf.writestr(f"{model_folder}/definition/database.tmdl", _database_tmdl())
        zf.writestr(f"{model_folder}/definition/model.tmdl", _model_tmdl(nomes_tabelas))
        zf.writestr(f"{model_folder}/definition/expressions.tmdl", _expressions_tmdl())

        for nome_tabela, df in tabelas.items():
            conteudo = _dedentar(_tabela_tmdl(nome_tabela, df))
            zf.writestr(f"{model_folder}/definition/tables/{nome_tabela}.tmdl", conteudo)

        if tem_medidas:
            conteudo_medidas = _dedentar(_medidas_tmdl(tabelas))
            zf.writestr(f"{model_folder}/definition/tables/Medidas.tmdl", conteudo_medidas)

        blocos_rel = _relacionamentos(tabelas)
        if blocos_rel:
            conteudo_rel = "".join(_dedentar(b) for b in blocos_rel)
            zf.writestr(f"{model_folder}/definition/relationships.tmdl", conteudo_rel)

        # ── Report (uma página em branco) ───────────────────────────────────
        zf.writestr(f"{report_folder}/definition.pbir", _definition_pbir(nome_projeto))
        zf.writestr(f"{report_folder}/definition/report.json", _report_json())
        zf.writestr(f"{report_folder}/definition/version.json", _report_version_json())
        zf.writestr(f"{report_folder}/definition/pages/pages.json", _pages_json(page_name))
        zf.writestr(
            f"{report_folder}/definition/pages/{page_name}/page.json",
            _page_json(page_name, "Página 1"),
        )

    return buffer.getvalue()
