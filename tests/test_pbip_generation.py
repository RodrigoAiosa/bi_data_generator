"""
tests/test_pbip_generation.py

Valida o template .pbip contra os SCHEMAS JSON OFICIAIS de verdade
(baixados diretamente das URLs da Microsoft, não um exemplo de terceiros
— foi confiar num exemplo de terceiros que causou os 2 primeiros bugs
reais encontrados nesta funcionalidade). Isso pega exatamente a classe de
erro que já apareceu 3 vezes em produção antes deste arquivo existir:
"Cannot find file X" / "Property Y has not been defined".
"""
import json

import jsonschema
import pytest

from config import obter_gerador
from generators.pbip_generator import gerar_pbip
from tests.conftest import DATA_INICIO, DATA_FIM

# Schemas baixados e confirmados diretamente das URLs oficiais da Microsoft
# (developer.microsoft.com/json-schemas/fabric/...) — ver o histórico de
# commits de generators/pbip_generator.py pro link exato de cada um.
_SCHEMA_PBISM = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "$schema": {"type": "string", "pattern": r"^https://developer\.microsoft\.com/json-schemas/fabric/item/semanticModel/definitionProperties/1\.[0-9]+\.[0-9]+/schema\.json$"},
        "version": {"type": "string"},
        "settings": {
            "type": ["object", "null"], "additionalProperties": False,
            "properties": {
                "qnaEnabled": {"type": ["boolean", "null"]},
                "qnaLsdlSharingPermissions": {"type": "integer", "enum": [0, 1]},
            },
        },
    },
    "required": ["$schema", "version"],
}

_SCHEMA_PBIR = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "$schema": {"type": "string", "pattern": r"^https://developer\.microsoft\.com/json-schemas/fabric/item/report/definitionProperties/2\.[0-9]+\.[0-9]+/schema\.json$"},
        "version": {"type": "string"},
        "datasetReference": {
            "type": "object", "additionalProperties": False,
            "properties": {
                "byPath": {"type": ["object", "null"], "additionalProperties": False,
                           "properties": {"path": {"type": "string"}}, "required": ["path"]},
                "byConnection": {"type": ["object", "null"], "additionalProperties": False,
                                 "properties": {"connectionString": {"type": "string"}}, "required": ["connectionString"]},
            },
        },
    },
    "required": ["$schema", "version", "datasetReference"],
}


@pytest.fixture(scope="module")
def arquivos_pbip_por_setor():
    """Gera o .pbip uma vez por setor e reaproveita entre os testes deste
    arquivo (evita gerar a base 2x pro mesmo setor)."""
    cache: dict[str, dict[str, str]] = {}

    def _gerar(nome_setor: str) -> dict[str, str]:
        if nome_setor not in cache:
            fn = obter_gerador(nome_setor)
            tabelas = fn(200, DATA_INICIO, DATA_FIM)
            cache[nome_setor] = gerar_pbip(nome_setor, tabelas)
        return cache[nome_setor]

    return _gerar


def test_pbip_gera_sem_excecao(nome_setor, arquivos_pbip_por_setor):
    arquivos = arquivos_pbip_por_setor(nome_setor)
    assert arquivos, f"{nome_setor}: gerar_pbip devolveu vazio"


def test_todo_json_do_pbip_e_sintaticamente_valido(nome_setor, arquivos_pbip_por_setor):
    arquivos = arquivos_pbip_por_setor(nome_setor)
    for caminho, conteudo in arquivos.items():
        if caminho.endswith((".json", ".pbism", ".pbir", ".platform")):
            try:
                json.loads(conteudo)
            except json.JSONDecodeError as e:
                pytest.fail(f"{nome_setor}/{caminho}: JSON inválido — {e}")


def test_definition_pbism_bate_com_schema_oficial(nome_setor, arquivos_pbip_por_setor):
    arquivos = arquivos_pbip_por_setor(nome_setor)
    caminho = next(k for k in arquivos if k.endswith(".SemanticModel/definition.pbism"))
    conteudo = json.loads(arquivos[caminho])
    jsonschema.validate(instance=conteudo, schema=_SCHEMA_PBISM)


def test_definition_pbir_bate_com_schema_oficial(nome_setor, arquivos_pbip_por_setor):
    arquivos = arquivos_pbip_por_setor(nome_setor)
    caminho = next(k for k in arquivos if k.endswith(".Report/definition.pbir"))
    conteudo = json.loads(arquivos[caminho])
    jsonschema.validate(instance=conteudo, schema=_SCHEMA_PBIR)


def test_definition_version_json_presente(nome_setor, arquivos_pbip_por_setor):
    """definition/version.json é obrigatório (confirmado por erro real em
    produção — ver commit bdf0924). Aqui só confere presença/JSON válido;
    o CONTEÚDO exato não foi confirmado contra um schema oficial (ver nota
    no próprio pbip_generator.py) — daí a aba de download estar marcada
    como beta."""
    arquivos = arquivos_pbip_por_setor(nome_setor)
    caminho = next((k for k in arquivos if k.endswith(".Report/definition/version.json")), None)
    assert caminho is not None, f"{nome_setor}: definition/version.json ausente"
    json.loads(arquivos[caminho])  # só confirma que é JSON válido


# ── Mockup do relatório (PBIR: páginas e visuais) ─────────────────────────────
import re


def _refs_do_visual(no, acum):
    """Coleta (tabela, propriedade, tipo) de todo Column/Measure do visual.json."""
    if isinstance(no, dict):
        for tipo in ("Column", "Measure"):
            if tipo in no:
                ent = no[tipo]["Expression"]["SourceRef"]["Entity"]
                acum.add((ent, no[tipo]["Property"], tipo))
        for v in no.values():
            _refs_do_visual(v, acum)
    elif isinstance(no, list):
        for v in no:
            _refs_do_visual(v, acum)


def _visuais(arquivos):
    return {k: json.loads(v) for k, v in arquivos.items() if k.endswith("/visual.json")}


def test_version_json_segue_schema_oficial(nome_setor, arquivos_pbip_por_setor):
    arquivos = arquivos_pbip_por_setor(nome_setor)
    caminho = next(k for k in arquivos if k.endswith(".Report/definition/version.json"))
    c = json.loads(arquivos[caminho])
    assert c["$schema"].endswith("/versionMetadata/1.0.0/schema.json")
    assert re.match(r"^[1-9][0-9]*\.(0|[1-9][0-9]*)\.0$", c["version"])


def test_relatorio_tem_paginas_e_visuais(nome_setor, arquivos_pbip_por_setor):
    arquivos = arquivos_pbip_por_setor(nome_setor)
    pages = json.loads(next(v for k, v in arquivos.items() if k.endswith("pages/pages.json")))
    assert pages["pageOrder"] and pages["activePageName"] in pages["pageOrder"]
    for pag in pages["pageOrder"]:
        page_json = next(k for k in arquivos if k.endswith(f"pages/{pag}/page.json"))
        assert json.loads(arquivos[page_json])["name"] == pag
    vis = _visuais(arquivos)
    assert vis, f"{nome_setor}: relatório sem nenhum visual"
    tipos = {v["visual"]["visualType"] for v in vis.values()}
    assert {"card", "textbox"} <= tipos, f"{nome_setor}: faltam cartões/cabeçalho ({tipos})"


def test_visuais_so_referenciam_o_que_existe_no_modelo(nome_setor, arquivos_pbip_por_setor):
    """Campo inexistente = visual com erro no Power BI Desktop."""
    arquivos = arquivos_pbip_por_setor(nome_setor)
    modelo = {}
    for k, v in arquivos.items():
        m = re.search(r"definition/tables/(.+)\.tmdl$", k)
        if m:
            modelo[m.group(1)] = v
    for caminho, vis in _visuais(arquivos).items():
        refs = set()
        _refs_do_visual(vis, refs)
        for ent, prop, tipo in refs:
            assert ent in modelo, f"{nome_setor}/{caminho}: tabela {ent} inexistente"
            padrao = f"\tcolumn {prop}\n" if tipo == "Column" else f"\tmeasure '{prop}' ="
            assert padrao in modelo[ent], f"{nome_setor}/{caminho}: {tipo} {ent}[{prop}] inexistente"


def test_visuais_cabem_na_pagina_e_nomes_unicos(nome_setor, arquivos_pbip_por_setor):
    arquivos = arquivos_pbip_por_setor(nome_setor)
    vistos = set()
    for caminho, vis in _visuais(arquivos).items():
        pos = vis["position"]
        assert pos["x"] >= 0 and pos["y"] >= 0 and pos["width"] > 0 and pos["height"] > 0
        assert pos["x"] + pos["width"] <= 1280 and pos["y"] + pos["height"] <= 720, f"{caminho} fora da página"
        assert caminho not in vistos
        vistos.add(caminho)
        assert caminho.split("/visuals/")[1].split("/")[0] == vis["name"]


def test_calendario_so_e_usado_em_fato_ligada(nome_setor, arquivos_pbip_por_setor):
    """Filtro/eixo de dCalendario numa página só faz sentido se a fato da página
    tem relação ativa com o calendário."""
    arquivos = arquivos_pbip_por_setor(nome_setor)
    rel = next((v for k, v in arquivos.items() if k.endswith("relationships.tmdl")), "")
    for caminho, vis in _visuais(arquivos).items():
        refs = set()
        _refs_do_visual(vis, refs)
        if any(e == "dCalendario" for e, _, _ in refs):
            assert "toColumn: dCalendario." in rel, f"{nome_setor}/{caminho}: usa dCalendario sem relação"


def test_zip_com_csvs_e_projeto_powerbi():
    import io, zipfile
    from generators.helpers import to_zip
    from generators.pbip_leiame import LEIAME_PBIP

    nome = next(iter(__import__("config").SETORES))
    tabelas = obter_gerador(nome)(100, DATA_INICIO, DATA_FIM)
    extra = {f"PowerBI/{k}": v for k, v in gerar_pbip(nome.split(" ", 1)[1], tabelas).items()}
    extra["LEIA-ME.txt"] = LEIAME_PBIP
    z = zipfile.ZipFile(io.BytesIO(to_zip(tabelas, extra_files=extra)))
    nomes = z.namelist()
    for t in tabelas:
        assert f"{t}.csv" in nomes
    assert any(n.startswith("PowerBI/") and n.endswith(".pbip") for n in nomes)
    assert any(n.endswith("/visual.json") for n in nomes) and "LEIA-ME.txt" in nomes


def test_dados_embutidos_dispensam_caminho_de_pasta(nome_setor, arquivos_pbip_por_setor):
    """Base pequena: nenhum caminho fixo (C:\\Dados) nem parâmetro; dados vão no modelo."""
    arquivos = arquivos_pbip_por_setor(nome_setor)
    modelo = {k: v for k, v in arquivos.items() if ".SemanticModel/" in k}
    assert not any(k.endswith("expressions.tmdl") for k in modelo)
    texto = "\n".join(modelo.values())
    assert "CaminhoPasta" not in texto and "C:\\Dados" not in texto and "File.Contents" not in texto
    assert "Binary.Decompress" in texto


def test_dados_embutidos_reconstituem_a_tabela():
    import base64, zlib
    nome = next(iter(__import__("config").SETORES))
    tabelas = obter_gerador(nome)(150, DATA_INICIO, DATA_FIM)
    arq = gerar_pbip("X", tabelas)
    fato = next(n for n in tabelas if n.startswith("Fato"))
    tmdl = arq[f"X.SemanticModel/definition/tables/{fato}.tmdl"]
    b64 = "".join(re.findall(r'"([A-Za-z0-9+/=]+)"', re.search(r"Partes = \{(.*?)\},", tmdl).group(1)))
    linhas = json.loads(zlib.decompress(base64.b64decode(b64), -15))
    assert len(linhas) == len(tabelas[fato]) and len(linhas[0]) == len(tabelas[fato].columns)


def test_base_grande_tambem_e_embutida_sem_caminho():
    """100 mil linhas: continua sem parâmetro/caminho (dados em pedaços no modelo)."""
    import pandas as pd
    from generators.tmdl_generator import _m_query
    df = pd.DataFrame({"id_a": range(100_000), "v": [1.5] * 100_000, "t": ["abc"] * 100_000})
    m = _m_query("T", df, embutir=True)
    assert "File.Contents" not in m and "Text.Combine(Partes)" in m
    assert max(len(x) for x in m.split("\n")) > 1000  # lista de pedaços numa linha, cada um <= 20000
    assert all(len(x) <= 20000 for x in re.findall(r'"([A-Za-z0-9+/=]{100,})"', m))
