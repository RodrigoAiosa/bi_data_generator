"""Testes do back-end das ferramentas (servico/ferramentas.py), sem Streamlit."""
import base64
import io
import json
import zipfile
from datetime import date

import pytest

from servico.ferramentas import ErroUsuario, executar
from servico.pacote import gerar_pacote, gerar_tabelas

BASE = {"setor": "🏪 E-commerce", "linhas": 800, "inicio": "2023-01-01", "fim": "2024-06-30",
        "mes_fiscal": 1, "seed": 7, "anomalia": False, "deriva": False, "idioma": "pt"}


def test_base_reproduzivel_por_seed():
    a, _ = gerar_tabelas("🐾 Pet & Veterinária", 300, date(2024, 1, 1), date(2024, 12, 31), seed=3, anomalia=True)
    b, _ = gerar_tabelas("🐾 Pet & Veterinária", 300, date(2024, 1, 1), date(2024, 12, 31), seed=3, anomalia=True)
    assert all(a[k].equals(b[k]) for k in a)


def test_formatadores_e_auditor():
    assert "DIVIDE" in executar({"acao": "formatar_dax", "texto": "T=DIVIDE(SUM(a[b]),COUNTROWS(a))"})["resultado"]
    assert "let" in executar({"acao": "formatar_m", "texto": 'let S = Table.Distinct(T) in S'})["resultado"]
    r = executar({"acao": "auditar", "texto": "createOrReplace\n\n\ttable T\n\t\tmeasure 'A' = SUM(T[x])/SUM(T[y])\n"})
    assert 0 <= r["relatorio"]["nota"] <= 100


def test_ferramentas_dependentes_da_base():
    dims = executar({"acao": "scd_info", "base": BASE})["dimensoes"]
    assert executar({"acao": "scd", "base": BASE, "dim": dims[0]["nome"], "n_mudancas": 3})["alteradas"] >= 1
    fatos = executar({"acao": "causal_info", "base": BASE})["fatos"]
    f = next(iter(fatos)); cols = fatos[f]["colunas"]
    r = executar({"acao": "causal", "base": BASE, "fato": f, "causa": cols[0], "efeito": cols[1], "direcao": 1})
    assert r["serie"]["x"] and r["gabarito"]
    m = executar({"acao": "sandbox_modelo", "base": BASE})
    assert executar({"acao": "sandbox_exec", "base": BASE, "expressao": m["exemplos"][0]})["valor"] > 0
    cat = executar({"acao": "qa_catalogo", "base": BASE})["perguntas"]
    assert cat and executar({"acao": "qa_perguntar", "base": BASE, "pergunta": cat[0]["texto"]})["entendida"]
    assert len(executar({"acao": "pl300", "n": 5, "base": BASE})["perguntas"]) == 5


def test_automatizar_e_carrossel():
    csv = b"data,valor,cliente\n2024-01-05,10.5,A\n2024-02-05,20,B\n"
    arq = [{"nome": "v.csv", "base64": base64.b64encode(csv).decode()}]
    assert executar({"acao": "automatizar_ler", "arquivos": arq})["tabelas"][0]["colunas"]
    r = executar({"acao": "automatizar_gerar", "arquivos": arq, "tipos": {}})
    assert r["medidas"] and r["zip_base64"]
    z, _ = gerar_pacote("🏪 E-commerce", 200, date(2024, 1, 1), date(2024, 12, 31))
    out = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(z)) as zi, zipfile.ZipFile(out, "w") as zo:
        for n in zi.namelist():
            if n.startswith("PowerBI/") and "/pages/" in n:
                zo.writestr(n[8:], zi.read(n))
    pg = executar({"acao": "carrossel_paginas", "zip_base64": base64.b64encode(out.getvalue()).decode()})["paginas"]
    link = "reportId=11111111-2222-3333-4444-555555555555&ctid=aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    assert "<html" in executar({"acao": "carrossel_html", "paginas": pg, "link": link, "intervalo": 5})["html"].lower()


@pytest.mark.parametrize("corpo", [
    {"acao": "nao_existe"}, {"acao": "formatar_dax", "texto": ""}, {"acao": "scd", "base": None},
    {"acao": "sandbox_exec", "base": BASE, "expressao": "Total = FOO("},
    {"acao": "pl300", "n": 7},
])
def test_erros_de_usuario(corpo):
    with pytest.raises(ErroUsuario):
        executar(corpo)


def test_resposta_serializavel():
    json.dumps(executar({"acao": "scd", "base": BASE, "dim": executar({"acao": "scd_info", "base": BASE})["dimensoes"][0]["nome"], "n_mudancas": 2}))


def test_sql_dialetos_e_tipos():
    from servico.ferramentas import executar
    base = {"setor": "🏪 E-commerce", "linhas": 200, "inicio": "2024-01-01", "fim": "2024-06-30",
            "mes_fiscal": 1, "seed": 1, "anomalia": False, "deriva": False, "idioma": "pt"}
    for d in ("sqlserver", "postgresql", "mysql"):
        for tp in ("ddl", "insert", "completo", "relatorios"):
            r = executar({"acao": "sql", "base": base, "dialeto": d, "tipo": tp})
            assert r["nome"] and r["kb"] > 0 and (r.get("sql") or r.get("zip_base64") or r.get("url"))
