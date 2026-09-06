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
