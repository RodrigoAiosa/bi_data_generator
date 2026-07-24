"""
log_acesso.py: envia eventos de acesso e uso do app para a planilha de
controle (Google Sheets), via um Web App do Google Apps Script.

Como configurar:
1. Publique o Code.gs (fornecido junto) como Web App na planilha.
2. Copie a URL de implantação gerada.
3. Configure essa URL em .streamlit/secrets.toml:

    log_webhook_url = "https://script.google.com/macros/s/SEU_ID/exec"

Se a URL não estiver configurada, todas as funções aqui viram no-op:
o app continua funcionando normalmente, só sem gravar log.

O log é sempre "best-effort": qualquer erro de rede/timeout é engolido
silenciosamente, para nunca travar ou quebrar a experiência do usuário.
"""
import re
import uuid
from datetime import datetime

import requests
import streamlit as st

_TIMEOUT_SEG = 3


def _webhook_url() -> str:
    try:
        return st.secrets.get("log_webhook_url", "")
    except Exception:
        return ""


def _post(payload: dict) -> None:
    url = _webhook_url()
    if not url:
        return
    try:
        requests.post(url, json=payload, timeout=_TIMEOUT_SEG)
    except Exception:
        pass  # log nunca pode derrubar o app


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


def iniciar_sessao(idioma: str) -> None:
    """Chame uma vez por sessão, bem no início do app (dentro de main())."""
    if "id_sessao" in st.session_state:
        return

    dispositivo, navegador = _detectar_dispositivo_navegador()
    agora = datetime.now()

    st.session_state.id_sessao = uuid.uuid4().hex[:8]
    st.session_state.inicio_acesso = agora

    _post({
        "tipo": "sessao_inicio",
        "id_sessao": st.session_state.id_sessao,
        "id_user": st.session_state.id_sessao,
        "data_hora": agora.strftime("%Y-%m-%d"),
        "inicio_acesso": agora.strftime("%H:%M:%S"),
        "dispositivo": dispositivo,
        "navegador": navegador,
        "idioma_interface": idioma,
        "origem_acesso": "link_direto",
        "novo_usuario": "sim",
    })


def _atualizar_fim_sessao() -> None:
    if "id_sessao" not in st.session_state or "inicio_acesso" not in st.session_state:
        return
    agora = datetime.now()
    duracao_seg = int((agora - st.session_state.inicio_acesso).total_seconds())
    horas, resto = divmod(max(duracao_seg, 0), 3600)
    minutos, segundos = divmod(resto, 60)

    _post({
        "tipo": "sessao_fim",
        "id_sessao": st.session_state.id_sessao,
        "fim_acesso": agora.strftime("%H:%M:%S"),
        "duracao": f"{horas:02d}:{minutos:02d}:{segundos:02d}",
    })


def registrar_evento(acao: str, setor: str = "", volume=None,
                      anomalia: bool = False, drift: bool = False,
                      status: str = "sucesso", erro: str = "") -> None:
    """
    Chame a cada ação relevante: gerou_base, gerou_sql, baixou_zip,
    baixou_dicionario, baixou_sql... Também atualiza fim_acesso/duracao
    da sessão (aproxima o "fim" pelo último evento conhecido).
    """
    if "id_sessao" not in st.session_state:
        return

    _post({
        "tipo": "evento",
        "id_sessao": st.session_state.id_sessao,
        "data_hora_evento": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "acao": acao,
        "setor_gerado": setor,
        "volume_linhas": volume,
        "anomalia_ativada": "sim" if anomalia else "nao",
        "deriva_temporal_ativada": "sim" if drift else "nao",
        "status": status,
        "erro_detalhe": erro,
    })
    _atualizar_fim_sessao()
