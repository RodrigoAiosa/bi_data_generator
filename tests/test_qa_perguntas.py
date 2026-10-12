"""Catálogo de perguntas da aba "Pergunte aos Dados": toda pergunta oferecida
na lista precisa ser respondida de verdade pelo motor (nunca "não entendi")."""
from config import obter_gerador
from generators.qa_engine import responder_pergunta
from generators.qa_perguntas import gerar_catalogo
from tests.conftest import DATA_INICIO, DATA_FIM


def test_catalogo_do_setor_so_tem_perguntas_respondiveis(nome_setor):
    tabelas = obter_gerador(nome_setor)(300, DATA_INICIO, DATA_FIM)
    catalogo = gerar_catalogo(tabelas)
    assert catalogo, f"{nome_setor}: catálogo vazio"
    textos = [p.texto for p in catalogo]
    assert len(textos) == len(set(textos)), f"{nome_setor}: perguntas repetidas"
    assert "Quantos registros existem?" in textos
    for p in catalogo:
        r = responder_pergunta(p.texto, tabelas)
        assert r.entendida, f"{nome_setor}: '{p.texto}' não foi entendida"
