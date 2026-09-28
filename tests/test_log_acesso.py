"""
tests/test_log_acesso.py

Testes do log de uso (log_acesso.py -> tabela logs_uso no Supabase).
Mocka requests.post: nenhum teste aqui depende de rede nem de
credenciais reais.
"""
from unittest.mock import Mock

import streamlit as st

import log_acesso


def _limpar_sessao():
    for chave in ("id_sessao", "inicio_acesso", "cadastro_id_registro", "log_debug"):
        st.session_state.pop(chave, None)


def test_iniciar_sessao_sem_supabase_configurado_nao_falha(monkeypatch):
    monkeypatch.setattr(log_acesso, "_supabase_config", lambda: ("", ""))
    _limpar_sessao()
    log_acesso.iniciar_sessao("pt")
    assert "id_sessao" in st.session_state  # o id de sessão é local, sempre criado


def test_iniciar_sessao_grava_evento_sessao_inicio(monkeypatch):
    monkeypatch.setattr(log_acesso, "_supabase_config", lambda: ("https://fake.supabase.co", "chave"))
    capturado = {}

    def _post_fake(url, json, headers, timeout):
        capturado["url"] = url
        capturado["json"] = json
        return Mock(status_code=201, text="")

    monkeypatch.setattr(log_acesso.requests, "post", _post_fake)
    _limpar_sessao()
    log_acesso.iniciar_sessao("pt")

    assert capturado["url"].endswith("/rest/v1/logs_uso")
    assert capturado["json"]["tipo_evento"] == "sessao_inicio"
    assert capturado["json"]["idioma_interface"] == "pt"
    assert capturado["json"]["id_sessao"] == st.session_state["id_sessao"]


def test_iniciar_sessao_so_grava_uma_vez_por_sessao(monkeypatch):
    monkeypatch.setattr(log_acesso, "_supabase_config", lambda: ("https://fake.supabase.co", "chave"))
    chamadas = []
    monkeypatch.setattr(log_acesso.requests, "post", lambda *a, **k: chamadas.append(1) or Mock(status_code=201, text=""))
    _limpar_sessao()
    log_acesso.iniciar_sessao("pt")
    log_acesso.iniciar_sessao("pt")
    assert len(chamadas) == 1


def test_iniciar_sessao_usa_id_registro_da_sessao(monkeypatch):
    monkeypatch.setattr(log_acesso, "_supabase_config", lambda: ("https://fake.supabase.co", "chave"))
    capturado = {}
    monkeypatch.setattr(
        log_acesso.requests, "post",
        lambda url, json, headers, timeout: capturado.update(json=json) or Mock(status_code=201, text=""),
    )
    _limpar_sessao()
    st.session_state["cadastro_id_registro"] = 123
    log_acesso.iniciar_sessao("pt")
    assert capturado["json"]["id_registro"] == 123


def test_registrar_evento_sem_sessao_iniciada_nao_faz_nada(monkeypatch):
    chamadas = []
    monkeypatch.setattr(log_acesso.requests, "post", lambda *a, **k: chamadas.append(1))
    _limpar_sessao()
    log_acesso.registrar_evento("gerou_base")
    assert chamadas == []


def test_registrar_evento_grava_clique_com_duracao(monkeypatch):
    monkeypatch.setattr(log_acesso, "_supabase_config", lambda: ("https://fake.supabase.co", "chave"))
    monkeypatch.setattr(log_acesso.requests, "post", lambda *a, **k: Mock(status_code=201, text=""))
    _limpar_sessao()
    log_acesso.iniciar_sessao("pt")

    capturado = {}
    monkeypatch.setattr(
        log_acesso.requests, "post",
        lambda url, json, headers, timeout: capturado.update(json=json) or Mock(status_code=201, text=""),
    )
    log_acesso.registrar_evento("gerou_base", setor="Varejo", volume=1000, anomalia=True, drift=False)

    corpo = capturado["json"]
    assert corpo["tipo_evento"] == "clique"
    assert corpo["acao"] == "gerou_base"
    assert corpo["setor_gerado"] == "Varejo"
    assert corpo["volume_linhas"] == 1000
    assert corpo["anomalia_ativada"] is True
    assert corpo["deriva_temporal_ativada"] is False
    assert isinstance(corpo["duracao_segundos"], int)
    assert corpo["duracao_segundos"] >= 0


def test_registrar_evento_sem_supabase_configurado_nao_falha(monkeypatch):
    monkeypatch.setattr(log_acesso, "_supabase_config", lambda: ("", ""))
    _limpar_sessao()
    st.session_state["id_sessao"] = "abc123"
    log_acesso.registrar_evento("gerou_base")  # não deve levantar exceção


def test_registrar_evento_erro_rede_nao_propaga(monkeypatch):
    monkeypatch.setattr(log_acesso, "_supabase_config", lambda: ("https://fake.supabase.co", "chave"))
    _limpar_sessao()
    st.session_state["id_sessao"] = "abc123"
    st.session_state["inicio_acesso"] = log_acesso._agora()

    def _explode(*a, **k):
        raise ConnectionError("sem rede")

    monkeypatch.setattr(log_acesso.requests, "post", _explode)
    log_acesso.registrar_evento("gerou_base")  # não deve levantar exceção
