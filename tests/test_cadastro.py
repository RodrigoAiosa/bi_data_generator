"""
tests/test_cadastro.py

Testes do cadastro obrigatório (gate) antes do uso do app:
  - data_acesso.py: chamadas REST ao Supabase (mockando requests.post,
    sem depender de rede nem de credenciais reais).
  - ui/cadastro.py + gate em app.py: fluxo completo via AppTest, simulando
    Supabase "configurado" (monkeypatch em data_acesso._config) para
    exercitar o bloqueio de verdade — sem isso, o ambiente de teste (sem
    st.secrets) sempre libera o acesso (fail-open), então o gate nunca
    apareceria nos testes.
"""
from pathlib import Path
from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

import data_acesso
import ui.cadastro as cadastro_ui

_CAMINHO_APP = str(Path(__file__).resolve().parent.parent / "app.py")


# ── data_acesso: unitários, sem rede ────────────────────────────────────────

def test_nao_configurado_sem_secrets():
    """Sem supabase_url/supabase_anon_key em st.secrets, o módulo se declara
    não configurado — é o que garante o fail-open (dev local/CI/testes)."""
    assert data_acesso.esta_configurado() is False


def test_email_valido():
    assert data_acesso.email_valido("ana@exemplo.com") is True
    assert data_acesso.email_valido("nao-e-email") is False
    assert data_acesso.email_valido("") is False
    assert data_acesso.email_valido("ana@exemplo") is False  # sem TLD
    assert data_acesso.email_valido("ana@@exemplo.com") is False


def test_celular_valido_aceita_so_digitos_com_ddd():
    assert data_acesso.celular_valido("11999999999") is True   # celular, 11 dígitos
    assert data_acesso.celular_valido("1133334444") is True    # fixo, 10 dígitos


def test_celular_valido_aceita_formatado_mas_valida_pelos_digitos():
    """O usuário pode digitar com máscara — validamos pelos dígitos, mas
    quem persiste (cadastrar) sempre limpa antes de gravar."""
    assert data_acesso.celular_valido("(11) 99999-9999") is True


def test_celular_valido_rejeita_tamanho_errado_ou_letras():
    assert data_acesso.celular_valido("123") is False
    assert data_acesso.celular_valido("") is False
    assert data_acesso.celular_valido("abc99999999") is False


def test_limpar_celular_remove_tudo_que_nao_e_digito():
    assert data_acesso.limpar_celular("(11) 99999-9999") == "11999999999"
    assert data_acesso.limpar_celular("+55 11 99999-9999") == "5511999999999"


def test_cadastrar_grava_celular_limpo(monkeypatch):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    capturado = {}

    def _post_fake(url, json, headers, timeout):
        capturado["celular"] = json["celular"]
        return Mock(status_code=201, text="")

    monkeypatch.setattr(data_acesso.requests, "post", _post_fake)
    data_acesso.cadastrar("Ana", "Feminino", "ana@exemplo.com", "(11) 99999-9999", "SP", "São Paulo")
    assert capturado["celular"] == "11999999999"


def test_email_cadastrado_sem_configuracao_retorna_none():
    assert data_acesso.email_cadastrado("ana@exemplo.com") is None


def test_cadastrar_sem_configuracao_retorna_erro_amigavel():
    ok, erro = data_acesso.cadastrar("Ana", "Feminino", "ana@exemplo.com", "11999999999", "SP", "São Paulo")
    assert ok is False
    assert erro != ""


def test_email_cadastrado_true(monkeypatch):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    resp = Mock(status_code=200)
    resp.json.return_value = True
    monkeypatch.setattr(data_acesso.requests, "post", lambda *a, **k: resp)
    assert data_acesso.email_cadastrado("ana@exemplo.com") is True


def test_email_cadastrado_false(monkeypatch):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    resp = Mock(status_code=200)
    resp.json.return_value = False
    monkeypatch.setattr(data_acesso.requests, "post", lambda *a, **k: resp)
    assert data_acesso.email_cadastrado("ninguem@exemplo.com") is False


def test_email_cadastrado_erro_rede_retorna_none(monkeypatch):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))

    def _explode(*a, **k):
        raise ConnectionError("sem rede")

    monkeypatch.setattr(data_acesso.requests, "post", _explode)
    assert data_acesso.email_cadastrado("ana@exemplo.com") is None


def test_cadastrar_sucesso(monkeypatch):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    monkeypatch.setattr(data_acesso.requests, "post", lambda *a, **k: Mock(status_code=201, text=""))
    ok, erro = data_acesso.cadastrar("Ana", "Feminino", "ana@exemplo.com", "11999999999", "SP", "São Paulo")
    assert ok is True
    assert erro == ""


def test_cadastrar_email_duplicado(monkeypatch):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    resp = Mock(status_code=409, text="duplicate key value violates unique constraint")
    monkeypatch.setattr(data_acesso.requests, "post", lambda *a, **k: resp)
    ok, erro = data_acesso.cadastrar("Ana", "Feminino", "ana@exemplo.com", "11999999999", "SP", "São Paulo")
    assert ok is False
    assert erro == "duplicado"


def test_cadastrar_erro_rede(monkeypatch):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))

    def _explode(*a, **k):
        raise ConnectionError("sem rede")

    monkeypatch.setattr(data_acesso.requests, "post", _explode)
    ok, erro = data_acesso.cadastrar("Ana", "Feminino", "ana@exemplo.com", "11999999999", "SP", "São Paulo")
    assert ok is False
    assert erro == "erro_rede"


# ── Gate completo, simulando Supabase configurado ───────────────────────────

def _rodar_com_supabase_configurado(monkeypatch) -> AppTest:
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    at = AppTest.from_file(_CAMINHO_APP, default_timeout=180)
    at.run()
    assert not at.exception
    return at


def test_gate_bloqueia_quando_supabase_configurado(monkeypatch):
    """Com Supabase 'configurado' e sem cadastro na sessão, o resto do app
    (sidebar com o seletor de 200 setores, abas do gerador) não deve
    renderizar — só a tela de cadastro."""
    at = _rodar_com_supabase_configurado(monkeypatch)
    # O seletor de setor (>100 opções) só existe depois do gate liberar.
    assert not any(len(s.options) > 100 for s in at.sidebar.selectbox)
    # A tela de cadastro tem os campos de texto do formulário.
    assert len(at.text_input) >= 5


def test_gate_libera_apos_cadastro_bem_sucedido(monkeypatch):
    """Simula a API do IBGE fora do ar (retorna []) — o campo cidade deve
    cair para texto livre, e o cadastro precisa continuar funcionando."""
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    monkeypatch.setattr(data_acesso.requests, "post", lambda *a, **k: Mock(status_code=201, text=""))
    monkeypatch.setattr(cadastro_ui, "buscar_cidades", lambda uf: [])

    at = AppTest.from_file(_CAMINHO_APP, default_timeout=180)
    at.run()

    # Preenche todos os campos de texto do formulário de cadastro (primeira
    # aba) com valores válidos e envia.
    for ti in at.text_input:
        rotulo = (ti.label or "").lower()
        if "mail" in rotulo:
            valor = "ana@exemplo.com"
        elif "celular" in rotulo or "phone" in rotulo:
            valor = "11999999999"
        else:
            valor = "Preenchido"
        ti.set_value(valor)

    botao = next(b for b in at.button if _s_btn_cadastrar(b))
    botao.click().run()
    assert not at.exception
    assert bool(at.session_state.get("cadastro_ok")) is True


def _s_btn_cadastrar(botao) -> bool:
    return botao.label in ("Cadastrar e começar", "Register and start")


def test_cidade_vira_selectbox_quando_ha_lista_de_cidades(monkeypatch):
    """Quando o IBGE responde, a cidade deixa de ser texto livre e vira uma
    lista das cidades do estado selecionado."""
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    monkeypatch.setattr(data_acesso.requests, "post", lambda *a, **k: Mock(status_code=201, text=""))
    monkeypatch.setattr(cadastro_ui, "buscar_cidades", lambda uf: ["Campinas", "São Paulo"] if uf == "SP" else [])

    at = AppTest.from_file(_CAMINHO_APP, default_timeout=180)
    at.run()

    # Estado padrão do selectbox é o primeiro (AC) — troca pra SP, que tem
    # cidades mockadas, disparando o rerun que popula o seletor de cidade.
    estado_sel = next(s for s in at.selectbox if s.label in ("Estado", "State"))
    estado_sel.set_value("SP").run()

    cidade_sel = next(s for s in at.selectbox if s.label in ("Cidade", "City"))
    assert list(cidade_sel.options) == ["Campinas", "São Paulo"]
    cidade_sel.set_value("São Paulo")

    for ti in at.text_input:
        rotulo = (ti.label or "").lower()
        if "mail" in rotulo:
            ti.set_value("ana@exemplo.com")
        elif "celular" in rotulo or "phone" in rotulo:
            ti.set_value("11999999999")
        else:
            ti.set_value("Preenchido")

    botao = next(b for b in at.button if _s_btn_cadastrar(b))
    botao.click().run()
    assert not at.exception
    assert bool(at.session_state.get("cadastro_ok")) is True


def test_estado_outro_nao_busca_cidades(monkeypatch):
    """'Fora do Brasil / Outro' deve manter cidade como texto livre e nunca
    chamar a API do IBGE."""
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    chamadas = []
    monkeypatch.setattr(cadastro_ui, "buscar_cidades", lambda uf: chamadas.append(uf) or [])

    at = AppTest.from_file(_CAMINHO_APP, default_timeout=180)
    at.run()

    estado_sel = next(s for s in at.selectbox if s.label in ("Estado", "State"))
    estado_sel.set_value("Fora do Brasil / Outro").run()

    # A primeira renderização (estado padrão "AC") busca cidades normalmente;
    # o que importa é que, com "Outro" selecionado, a UF especial nunca é
    # passada pra buscar_cidades.
    assert "Fora do Brasil / Outro" not in chamadas
    assert not any(s.label in ("Cidade", "City") for s in at.selectbox)
    assert any((ti.label or "") in ("Cidade", "City") for ti in at.text_input)


def test_gate_fail_open_sem_configuracao_nao_bloqueia():
    """Sem secrets (caso real deste ambiente de teste/CI), o gate nunca deve
    aparecer — é a rede de segurança que garante que a suíte antiga
    (test_app_tabs.py) continua funcionando sem depender do Supabase."""
    at = AppTest.from_file(_CAMINHO_APP, default_timeout=180)
    at.run()
    assert not at.exception
    assert len(at.tabs) == 11
