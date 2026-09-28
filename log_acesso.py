"""
log_acesso.py: grava eventos de uso do app na tabela `logs_uso` do
Supabase (início de sessão, cada clique/ação relevante e o tempo de
permanência), ligados ao cadastro (`id_registro`) quando disponível.

Substituiu o log anterior, que ia para uma planilha do Google Sheets via
um Web App do Apps Script — agora tudo fica no mesmo banco do cadastro
(ver data_acesso.py e a tabela `registros`).

Reaproveita a configuração do Supabase (supabase_url/supabase_anon_key em
st.secrets) já usada por data_acesso.py. Se não estiver configurado,
todas as funções aqui viram no-op: o app continua funcionando
normalmente, só sem gravar log (dev local, CI, testes).

O log é sempre "best-effort": qualquer erro de rede/timeout é engolido
silenciosamente, para nunca travar ou quebrar a experiência do usuário.
"""
import re
import uuid
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

import requests
import streamlit as st

from data_acesso import _config as _supabase_config

_TIMEOUT_SEG = 3
_FUSO_BRASILIA = ZoneInfo("America/Sao_Paulo")


def _agora() -> datetime:
    """Horário atual sempre no fuso de Brasília, independente de onde o servidor do Streamlit estiver rodando."""
    return datetime.now(_FUSO_BRASILIA)


def _registrar_diagnostico(tipo: str, status: str, detalhe: str = "") -> None:
    if "log_debug" not in st.session_state:
        st.session_state.log_debug = []
    st.session_state.log_debug.append({
        "quando": _agora().strftime("%H:%M:%S"),
        "tipo": tipo,
        "status": status,
        "detalhe": detalhe,
    })
    st.session_state.log_debug = st.session_state.log_debug[-20:]  # guarda só os últimos 20


def _inserir_log(payload: dict) -> None:
    """INSERT best-effort em logs_uso — nunca levanta exceção, nunca trava a UI."""
    url, key = _supabase_config()
    tipo = payload.get("tipo_evento", "?")
    if not url or not key:
        _registrar_diagnostico(tipo, "sem_supabase_configurado")
        return
    try:
        resp = requests.post(
            f"{url}/rest/v1/logs_uso",
            json=payload,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            timeout=_TIMEOUT_SEG,
        )
        _registrar_diagnostico(tipo, f"http_{resp.status_code}", resp.text[:200])
    except Exception as e:
        _registrar_diagnostico(tipo, "excecao", str(e))


def _detectar_dispositivo_navegador() -> tuple[str, str]:
    ua = ""
    try:
        if hasattr(st, "context") and hasattr(st.context, "headers"):
            ua = st.context.headers.get("User-Agent", "") or ""
    except Exception:
        ua = ""

    dispositivo = "mobile" if re.search(r"Mobi|Android.*Mobile|iPhone|iPad", ua) else "desktop"

    if "Edg/" in ua:
        navegador = "Edge"
    elif "Chrome/" in ua and "Chromium" not in ua:
        navegador = "Chrome"
    elif "Firefox/" in ua:
        navegador = "Firefox"
    elif "Safari/" in ua and "Chrome" not in ua:
        navegador = "Safari"
    elif ua:
        navegador = "Outro"
    else:
        navegador = "Desconhecido"

    return dispositivo, navegador


def _id_registro_atual() -> Optional[int]:
    """id_registro da pessoa logada nesta sessão (ver ui/cadastro.py), ou
    None se o Supabase não estiver configurado, ou o gate não tiver
    conseguido recuperar o ID (nunca bloqueia o log por causa disso)."""
    return st.session_state.get("cadastro_id_registro")


def iniciar_sessao(idioma: str) -> None:
    """Chame uma vez por sessão, bem no início do app (dentro de main(), após o gate de cadastro)."""
    if "id_sessao" in st.session_state:
        return

    dispositivo, navegador = _detectar_dispositivo_navegador()
    st.session_state.id_sessao = uuid.uuid4().hex[:8]
    st.session_state.inicio_acesso = _agora()

    _inserir_log({
        "id_registro": _id_registro_atual(),
        "id_sessao": st.session_state.id_sessao,
        "tipo_evento": "sessao_inicio",
        "dispositivo": dispositivo,
        "navegador": navegador,
        "idioma_interface": idioma,
    })


def registrar_evento(acao: str, setor: str = "", volume=None,
                      anomalia: bool = False, drift: bool = False,
                      status: str = "sucesso", erro: str = "") -> None:
    """
    Chame a cada clique/ação relevante: troca de aba, gerou_base,
    gerou_sql, baixou_zip, formatou_dax, trocou_idioma... Cada chamada
    grava 1 linha em logs_uso com duracao_segundos = tempo decorrido desde
    o início da sessão — aproxima "quanto tempo ficou na ferramenta" pelo
    último clique conhecido, já que o Streamlit não tem um evento
    confiável de "fechou a aba"/"saiu do site".
    """
    if "id_sessao" not in st.session_state:
        return

    inicio = st.session_state.get("inicio_acesso")
    duracao_seg = int((_agora() - inicio).total_seconds()) if inicio else None

    _inserir_log({
        "id_registro": _id_registro_atual(),
        "id_sessao": st.session_state.id_sessao,
        "tipo_evento": "clique",
        "acao": acao,
        "setor_gerado": setor or None,
        "volume_linhas": volume,
        "anomalia_ativada": bool(anomalia),
        "deriva_temporal_ativada": bool(drift),
        "status": status,
        "erro_detalhe": erro or None,
        "duracao_segundos": duracao_seg,
    })


def mostrar_diagnostico() -> None:
    """
    Mostra um painel de diagnóstico do log de uso, só quando a URL tem
    ?debug=1 (ex.: https://seu-app.streamlit.app/?debug=1). Não aparece
    pra usuários normais, é só pra conferir se a gravação no Supabase está
    funcionando de verdade.
    """
    try:
        eh_debug = st.query_params.get("debug") == "1"
    except Exception:
        eh_debug = False
    if not eh_debug:
        return

    with st.sidebar.expander("🔧 Diagnóstico do log de uso", expanded=True):
        url, _key = _supabase_config()
        if url:
            st.success(f"Supabase configurado: {url}")
        else:
            st.error("supabase_url/supabase_anon_key NÃO configurados em st.secrets.")

        st.caption(f"id_registro desta sessão: {_id_registro_atual()}")

        historico = st.session_state.get("log_debug", [])
        if not historico:
            st.info("Nenhuma tentativa de log registrada ainda nesta sessão.")
        else:
            for item in reversed(historico):
                cor = "✅" if item["status"].startswith("http_2") else "❌"
                st.write(f"{cor} `{item['quando']}` {item['tipo']}: {item['status']}")
                if item["detalhe"]:
                    st.caption(item["detalhe"])
