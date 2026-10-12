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


def test_dax_de_ranking_nao_carrega_a_resposta_pronta():
    """"Qual mês teve o maior total?" deve virar MAXX/TOPN sobre os itens distintos,
    não um CALCULATE com filtro fixo no vencedor (que já embute a resposta)."""
    from datetime import date
    from config import SETORES
    nome = next(n for n in SETORES if "Condom" in n)
    t = obter_gerador(nome)(500, DATA_INICIO, DATA_FIM)
    for q, it in [("Qual mês teve o maior total de valor cota?", "MAXX"),
                  ("Qual unidade teve o menor total de valor extra?", "MINX")]:
        r = responder_pergunta(q, t)
        assert r.entendida and it in r.medida_dax and "TOPN" in r.medida_dax and "CONCATENATEX" in r.medida_dax
        assert '="' not in r.medida_dax
