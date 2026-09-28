"""
data_acesso.py: acesso ao Supabase (Postgres) para o cadastro obrigatório
de usuários, via API REST do PostgREST — mesmo padrão de "best-effort" do
log_acesso.py, mas aqui os erros SÃO importantes (não são só telemetria).

Como configurar (.streamlit/secrets.toml ou "Secrets" do Streamlit Cloud):

    supabase_url      = "https://SEU_PROJETO.supabase.co"
    supabase_anon_key = "eyJ..."   # chave pública "anon" (publishable), nunca a service_role

Se as duas chaves não estiverem configuradas, `esta_configurado()` retorna
False e o app (via ui/cadastro.py) libera o acesso sem exigir cadastro —
assim ambiente local/CI/dev continuam funcionando sem depender do Supabase.

Segurança: a tabela `registros` tem Row Level Security habilitado, sem
política de SELECT/UPDATE/DELETE para o público — a chave anon só consegue
INSERIR uma linha nova ou chamar a função `email_cadastrado`, que devolve
apenas um booleano (nunca expõe os dados de outras pessoas).
"""
import re
from typing import Optional

import requests
import streamlit as st

_TIMEOUT_SEG = 6
_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")
# Celular: só dígitos, DDD + número (fixo: 10, celular: 11 dígitos no padrão BR).
_CELULAR_REGEX = re.compile(r"^\d{10,11}$")
_NAO_DIGITO = re.compile(r"\D+")


def _config() -> tuple[str, str]:
    """Lê supabase_url/supabase_anon_key de st.secrets. Retorna ("", "") se ausentes."""
    try:
        url = st.secrets.get("supabase_url", "") or ""
        key = st.secrets.get("supabase_anon_key", "") or ""
        return url.rstrip("/"), key
    except Exception:
        return "", ""


def esta_configurado() -> bool:
    """True se as credenciais do Supabase estão presentes nos secrets."""
    url, key = _config()
    return bool(url and key)


def email_valido(email: str) -> bool:
    return bool(_EMAIL_REGEX.match((email or "").strip()))


def limpar_celular(celular: str) -> str:
    """Remove tudo que não for dígito (espaços, parênteses, hífen, +55...)."""
    return _NAO_DIGITO.sub("", celular or "")


def celular_valido(celular: str) -> bool:
    """True se, depois de limpo, sobrar só dígitos no padrão BR (DDD + número)."""
    return bool(_CELULAR_REGEX.match(limpar_celular(celular)))


def email_cadastrado(email: str) -> Optional[bool]:
    """
    Verifica (via RPC email_cadastrado, que só devolve true/false) se um
    e-mail já está cadastrado. Retorna None se não foi possível verificar
    (rede/erro) — quem chama decide como tratar a incerteza.
    """
    url, key = _config()
    if not url or not key or not email:
        return None
    try:
        resp = requests.post(
            f"{url}/rest/v1/rpc/email_cadastrado",
            json={"p_email": email.strip()},
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            timeout=_TIMEOUT_SEG,
        )
        if resp.status_code == 200:
            return bool(resp.json())
        return None
    except Exception:
        return None


def cadastrar(nome_completo: str, sexo: str, email: str, celular: str,
              estado: str, cidade: str) -> tuple[bool, str]:
    """
    Insere um novo registro na tabela `registros` via REST (INSERT-only,
    permitido pela política de RLS para o role anon). Retorna
    (sucesso, mensagem_de_erro_amigavel).
    """
    url, key = _config()
    if not url or not key:
        return False, "Cadastro não está configurado neste ambiente."

    payload = {
        "nome_completo": nome_completo.strip(),
        "sexo": sexo.strip(),
        "email": email.strip(),
        "celular": limpar_celular(celular),
        "estado": estado.strip(),
        "cidade": cidade.strip(),
    }
    try:
        resp = requests.post(
            f"{url}/rest/v1/registros",
            json=payload,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            timeout=_TIMEOUT_SEG,
        )
        if resp.status_code in (200, 201, 204):
            return True, ""
        # 409 = violação de unicidade (e-mail já cadastrado)
        if resp.status_code == 409 or "duplicate key" in resp.text.lower() or "23505" in resp.text:
            return False, "duplicado"
        return False, f"erro_http_{resp.status_code}"
    except Exception:
        return False, "erro_rede"
