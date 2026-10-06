"""
tests/test_card_setor.py

Clique num card de "Setores disponíveis" seleciona o setor no filtro da sidebar.
"""
import html
from pathlib import Path

from streamlit.testing.v1 import AppTest

from config import SETORES, SETORES_INFO
from i18n import SETORES_INFO_EN
from ui.estado_inicial import chave_setor

_CAMINHO_APP = str(Path(__file__).resolve().parent.parent / "app.py")


def test_todo_card_mapeia_para_um_setor_distinto_pt_e_en():
    """Os 200 cards (PT e EN) devem apontar, um a um, para os 200 setores
    reais — inclusive nos ícones repetidos entre setores diferentes."""
    for info in (SETORES_INFO, SETORES_INFO_EN):
        chaves = [chave_setor(ico, nome) for ico, nome, _ in info]
        assert all(c in SETORES for c in chaves)
        assert len(set(chaves)) == len(SETORES) == 200


def test_mapeamento_en_corresponde_ao_mesmo_setor_do_pt():
    """O card "Tourism" (EN) deve selecionar o setor "Turismo", e não outro do
    mesmo ícone (✈️ Aviação Civil / Viagens Corporativas)."""
    en = {nome: ico for ico, nome, _ in SETORES_INFO_EN}
    assert chave_setor(en["Tourism"], "Tourism") == "✈️ Turismo"
    assert chave_setor(en["Civil Aviation"], "Civil Aviation") == "✈️ Aviação Civil"
    assert chave_setor(en["Corporate Travel"], "Corporate Travel") == "✈️ Viagens Corporativas"
    assert chave_setor(en["Human Resources"], "Human Resources") == "🏢 Recursos Humanos"


def _app():
    at = AppTest.from_file(_CAMINHO_APP, default_timeout=180)
    at.run()
    assert not at.exception
    return at


def test_clique_no_card_seleciona_setor_no_filtro():
    at = _app()
    alvo = "🏦 Banco & Instituição Financeira" if "🏦 Banco & Instituição Financeira" in SETORES else list(SETORES)[50]
    assert at.sidebar.selectbox[0].value != alvo
    proxy = next(t for t in at.text_input if t.key == "setor_clique_proxy")
    proxy.set_value(f"{alvo}|1700000000000").run()
    assert not at.exception
    assert at.session_state["setor_sel"] == alvo
    assert at.sidebar.selectbox[0].value == alvo
    # o campo oculto é zerado para o mesmo card poder ser clicado de novo
    assert at.session_state["setor_clique_proxy"] == ""


def test_clique_no_card_limpa_a_busca_para_nao_esconder_o_setor():
    at = _app()
    busca = next(t for t in at.sidebar.text_input if t.key == "busca_setor")
    busca.set_value("varejo").run()
    alvo = list(SETORES)[10]
    proxy = next(t for t in at.text_input if t.key == "setor_clique_proxy")
    proxy.set_value(f"{alvo}|1").run()
    assert not at.exception
    assert at.session_state["busca_setor"] == ""
    assert at.sidebar.selectbox[0].value == alvo


def test_chave_invalida_e_ignorada():
    at = _app()
    antes = at.sidebar.selectbox[0].value
    proxy = next(t for t in at.text_input if t.key == "setor_clique_proxy")
    proxy.set_value("setor que nao existe|1").run()
    assert not at.exception
    assert at.sidebar.selectbox[0].value == antes


def test_card_selecionado_fica_destacado_no_html():
    at = _app()
    alvo = list(SETORES)[7]
    next(t for t in at.text_input if t.key == "setor_clique_proxy").set_value(f"{alvo}|1").run()
    html_cards = " ".join(m.value for m in at.markdown if "sector-grid" in m.value)
    assert 'flip-wrapper sel" data-setor="' + html.escape(alvo, quote=True) in html_cards
    assert html_cards.count("flip-wrapper sel") == 1
