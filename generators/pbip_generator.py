"""
generators/pbip_generator.py
Gera um projeto Power BI (.pbip) completo por setor: pasta de Relatório
(Report) + Modelo Semântico (SemanticModel) em TMDL nativo, prontos para
abrir direto no Power BI Desktop via Arquivo > Abrir > Procurar (sem passar
pelo Tabular Editor, ao contrário do model.tmdl "createOrReplace" gerado por
generators/tmdl_generator.py, pensado para colar via Advanced Scripting).

Reaproveita TODA a lógica de tabelas/relacionamentos/medidas já testada em
tmdl_generator.py (_tabela_tmdl, _relacionamentos, _medidas_tmdl) — a única
diferença estrutural entre os dois formatos é a indentação (o script
"createOrReplace" tem `table` em 1 tab e column/measure em 2, enquanto o
TMDL nativo de pasta tem `table` em 0 tabs e column/measure em 1) e a
distribuição em arquivos (nativo: 1 arquivo por tabela em definition/tables/,
em vez de tudo concatenado num único model.tmdl). Por isso _dedent() só
remove 1 tab de cada linha em vez de reescrever essa lógica.
"""

from __future__ import annotations

import json

import pandas as pd

from generators.tmdl_generator import _medidas_tmdl, _relacionamentos, _tabela_tmdl

_COMPATIBILITY_LEVEL = 1567  # nível estável em projetos TMDL desde 2023/2024; o Power BI Desktop faz upgrade automático se a versão instalada exigir um nível maior.


def _sanitizar_nome(nome_setor: str) -> str:
    """Nome seguro para pasta/arquivo do Power BI (sem espaço, & ou barra)."""
    return nome_setor.replace(" ", "_").replace("&", "e").replace("/", "_")


def _dedent(bloco: str) -> str:
    """Remove 1 tab de cada linha: formato 'createOrReplace' (Tabular Editor,
    2 níveis a partir da tabela) -> TMDL nativo de pasta PBIP (1 nível)."""
    return "\n".join(l[1:] if l.startswith("\t") else l for l in bloco.split("\n"))


def _platform_json(tipo: str, display_name: str) -> str:
    """Conteúdo do arquivo `.platform` exigido em cada item (Report/SemanticModel)
    de um projeto Fabric/Power BI baseado em pasta."""
    conteudo = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": tipo, "displayName": display_name},
        "config": {"version": "2.0", "logicalId": "00000000-0000-0000-0000-000000000000"},
    }
    return json.dumps(conteudo, indent=2, ensure_ascii=False)


def _report_files(nome_limpo: str) -> dict[str, str]:
    """Relatório mínimo (1 página em branco) — o valor deste template está no
    modelo semântico (tabelas, relacionamentos, medidas), não em visuais
    pré-montados; um relatório vazio é o ponto de partida mais seguro para
    o usuário montar o próprio dashboard sobre um modelo já pronto."""
    pbir = {
        # $schema é OBRIGATÓRIO (confirmado via fetch direto do schema oficial:
        # required = ["$schema", "version", "datasetReference"]) — estava
        # faltando aqui, mesmo tipo de lacuna que causou o erro do
        # definition.pbism.
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0",
        "datasetReference": {"byPath": {"path": f"../{nome_limpo}.SemanticModel"}},
    }
    report_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/1.2.0/schema.json",
        "themeCollection": {
            "baseTheme": {"name": "CY24SU06", "reportVersionAtImport": "5.0", "type": "SharedResources"}
        },
        "layoutOptimization": "None",
        "publicCustomVisuals": [],
        "resourcePackages": [],
        "settings": {},
    }
    pages_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
        "pageOrder": ["ReportSection1"],
        "activePageName": "ReportSection1",
    }
    page_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/1.3.0/schema.json",
        "name": "ReportSection1",
        "displayName": "Página 1",
        "displayOption": "FitToPage",
        "height": 720,
        "width": 1280,
    }

    base = f"{nome_limpo}.Report"
    return {
        f"{base}/.platform": _platform_json("Report", nome_limpo),
        f"{base}/definition.pbir": json.dumps(pbir, indent=2, ensure_ascii=False),
        f"{base}/definition/report.json": json.dumps(report_json, indent=2, ensure_ascii=False),
        f"{base}/definition/pages/pages.json": json.dumps(pages_json, indent=2, ensure_ascii=False),
        f"{base}/definition/pages/ReportSection1/page.json": json.dumps(page_json, indent=2, ensure_ascii=False),
    }


def _semantic_model_files(nome_limpo: str, tabelas: dict[str, pd.DataFrame]) -> dict[str, str]:
    base = f"{nome_limpo}.SemanticModel"
    arquivos: dict[str, str] = {
        f"{base}/.platform": _platform_json("SemanticModel", nome_limpo),
        # definition.pbism é um arquivo OBRIGATÓRIO na raiz da pasta .SemanticModel
        # (não dentro de definition/) — sem ele o Power BI Desktop recusa abrir o
        # projeto com "DatasetDefinition: Required artifact is missing". Schema
        # confirmado na documentação OFICIAL da Microsoft (Fabric REST API,
        # SemanticModel definition, learn.microsoft.com/rest/api/fabric/articles/
        # item-management/definitions/semantic-model-definition) — NÃO tem
        # 'datasetReference' (isso é do definition.pbir, de Report; uma tentativa
        # anterior baseada numa fonte de terceiros misturou os dois schemas por
        # engano, causando "Property 'datasetReference' has not been defined and
        # the schema does not allow additional properties").
        f"{base}/definition.pbism": json.dumps(
            {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
                "version": "4.2",
                "settings": {"qnaEnabled": False},
            },
            indent=2, ensure_ascii=False,
        ) + "\n",
        f"{base}/definition/database.tmdl": f"database {nome_limpo}\n\tcompatibilityLevel: {_COMPATIBILITY_LEVEL}\n",
    }

    nomes_tabelas = list(tabelas.keys())
    medidas_tmdl = _medidas_tmdl(tabelas)
    ordem = nomes_tabelas + (["Medidas"] if medidas_tmdl else [])

    arquivos[f"{base}/definition/model.tmdl"] = (
        "model Model\n"
        "\tculture: pt-BR\n"
        "\tdefaultPowerBIDataSourceVersion: powerBI_V3\n"
        "\tsourceQueryCulture: pt-BR\n\n"
        f"annotation PBI_QueryOrder = {json.dumps(ordem, ensure_ascii=False)}\n"
    )

    arquivos[f"{base}/definition/expressions.tmdl"] = _dedent(
        '\texpression CaminhoPasta = \n'
        '\t\t\t"C:\\Dados\\" meta [IsParameterQuery=true, List={"C:\\Dados\\"}, '
        'DefaultValue="C:\\Dados\\", Type="Text", IsParameterQueryRequired=true]\n'
        "\t\tannotation PBI_ResultType = Text\n"
    )

    for nome_tabela, df in tabelas.items():
        arquivos[f"{base}/definition/tables/{nome_tabela}.tmdl"] = _dedent(_tabela_tmdl(nome_tabela, df))

    if medidas_tmdl:
        arquivos[f"{base}/definition/tables/Medidas.tmdl"] = _dedent(medidas_tmdl)

    rel_blocos = _relacionamentos(tabelas)
    if rel_blocos:
        arquivos[f"{base}/definition/relationships.tmdl"] = _dedent("".join(rel_blocos))

    return arquivos


def gerar_pbip(nome_setor: str, tabelas: dict[str, pd.DataFrame]) -> dict[str, str]:
    """
    Gera todos os arquivos de um projeto .pbip (Report + SemanticModel em
    TMDL nativo) para o setor, prontos para abrir direto no Power BI Desktop
    (Arquivo > Abrir > Procurar > selecionar o arquivo <setor>.pbip).

    Retorna {caminho_relativo_no_zip: conteúdo}, para empacotar junto com os
    CSVs via generators.helpers.to_zip(tabelas, extra_files=gerar_pbip(...)).

    Depois de abrir, é preciso apontar o parâmetro de Power Query
    `CaminhoPasta` (Transformar Dados > Gerenciar Parâmetros) para a pasta
    onde os CSVs deste mesmo .zip foram extraídos, e clicar em Atualizar —
    igual ao fluxo do model.tmdl via Tabular Editor, só que sem esse
    intermediário.
    """
    nome_limpo = _sanitizar_nome(nome_setor)

    pbip_raiz = {
        "version": "1.0",
        "artifacts": [{"report": {"path": f"{nome_limpo}.Report"}}],
        "settings": {"enableAutoRecovery": True},
    }

    arquivos: dict[str, str] = {f"{nome_limpo}.pbip": json.dumps(pbip_raiz, indent=2, ensure_ascii=False)}
    arquivos.update(_report_files(nome_limpo))
    arquivos.update(_semantic_model_files(nome_limpo, tabelas))
    return arquivos
