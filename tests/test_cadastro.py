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
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    monkeypatch.setattr(data_acesso.requests, "post", lambda *a, **k: Mock(status_code=201, text=""))

    at = AppTest.from_file(_CAMINHO_APP, default_timeout=180)
    at.run()

    # Preenche todos os campos de texto do formulário de cadastro (primeira
    # aba) com valores válidos e envia.
    for ti in at.text_input:
        eh_email = "mail" in (ti.label or "").lower()
        valor = "ana@exemplo.com" if eh_email else "Preenchido"
        ti.set_value(valor)

    botao = next(b for b in at.button if _s_btn_cadastrar(b))
    botao.click().run()
    assert not at.exception
    assert bool(at.session_state.get("cadastro_ok")) is True


def _s_btn_cadastrar(botao) -> bool:
    return botao.label in ("Cadastrar e começar", "Register and start")


def test_gate_fail_open_sem_configuracao_nao_bloqueia():
    """Sem secrets (caso real deste ambiente de teste/CI), o gate nunca deve
    aparecer — é a rede de segurança que garante que a suíte antiga
    (test_app_tabs.py) continua funcionando sem depender do Supabase."""
    at = AppTest.from_file(_CAMINHO_APP, default_timeout=180)
    at.run()
    assert not at.exception
    assert len(at.tabs) == 11
