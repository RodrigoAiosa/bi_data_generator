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


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def buscar_cidades(uf: str) -> list[str]:
    """
    Busca a lista de municípios de um estado brasileiro na API pública do
    IBGE (não depende do Supabase). Cacheada por 24h por UF, já que a
    lista de cidades de um estado não muda de um dia pro outro.

    Retorna [] em caso de erro/timeout/UF desconhecida — quem chama deve
    cair para um campo de texto livre nesse caso, nunca travar o cadastro
    por causa disso (mesmo espírito "best-effort" do resto do arquivo).
    """
    try:
        resp = requests.get(
            f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios",
            timeout=_TIMEOUT_SEG,
        )
        if resp.status_code != 200:
            return []
        dados = resp.json()
        return sorted({item["nome"] for item in dados if isinstance(item, dict) and item.get("nome")})
    except Exception:
        return []


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


def obter_id_registro(email: str) -> Optional[int]:
    """
    Devolve o id_registro de um e-mail já cadastrado (via RPC
    obter_id_registro), ou None se não existir ou não foi possível
    verificar. Usado pra linkar os logs de uso (logs_uso.id_registro) à
    sessão de quem confirma "já sou cadastrado" sem passar pelo formulário
    de novo.
    """
    url, key = _config()
    if not url or not key or not email:
        return None
    try:
        resp = requests.post(
            f"{url}/rest/v1/rpc/obter_id_registro",
            json={"p_email": email.strip()},
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            timeout=_TIMEOUT_SEG,
        )
        if resp.status_code == 200:
            valor = resp.json()
            return int(valor) if valor is not None else None
        return None
    except Exception:
        return None


URL_APP = "https://ai-bidatagenerator.streamlit.app/"


def _rpc(nome: str, payload: dict):
    """POST numa RPC do Supabase. Devolve o JSON da resposta ou None em qualquer falha."""
    url, key = _config()
    if not url or not key:
        return None
    try:
        resp = requests.post(
            f"{url}/rest/v1/rpc/{nome}",
            json=payload,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            timeout=_TIMEOUT_SEG,
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None


def criar_link_compartilhamento(id_registro: Optional[int]) -> Optional[str]:
    """
    Gera (ou recupera, é idempotente) o código de divulgação de um cadastro,
    via RPC criar_link_compartilhamento. Devolve só o código (ex.: "a1b2c3d4e5")
    ou None se não foi possível — quem chama simplesmente não mostra o link.
    """
    if not id_registro:
        return None
    valor = _rpc("criar_link_compartilhamento", {"p_id_registro": int(id_registro)})
    return valor if isinstance(valor, str) and valor else None


def montar_url_compartilhamento(codigo: str) -> str:
    return f"{URL_APP}?ref={codigo}"


def registrar_clique_compartilhamento(codigo: str, id_sessao: str) -> bool:
    """Registra que a sessão `id_sessao` chegou pelo link `codigo`. True se gravou
    um clique novo (False: código inválido, clique repetido ou falha)."""
    if not codigo or not id_sessao:
        return False
    return _rpc(
        "registrar_clique_compartilhamento",
        {"p_codigo": codigo, "p_id_sessao": id_sessao},
    ) is True


def cadastrar(nome_completo: str, sexo: str, email: str, celular: str,
              estado: str, cidade: str) -> tuple[bool, str, Optional[int]]:
    """
    Insere um novo registro na tabela `registros` via REST (INSERT-only,
    permitido pela política de RLS para o role anon). Retorna
    (sucesso, mensagem_de_erro_amigavel, id_registro_ou_None).
    """
    url, key = _config()
    if not url or not key:
        return False, "Cadastro não está configurado neste ambiente.", None

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
                # "minimal": a tabela `registros` só tem política de INSERT
                # pro público (sem SELECT), de propósito — pedir
                # "return=representation" faria o PostgREST tentar ler a
                # linha de volta e, sem política de SELECT, o role anon
                # toma 401 mesmo com o INSERT já tendo funcionado. Por isso
                # buscamos o id_registro depois, via obter_id_registro()
                # (RPC SECURITY DEFINER, já usada no fluxo "já sou
                # cadastrado"), que é o jeito seguro de ler esse dado.
                "Prefer": "return=minimal",
            },
            timeout=_TIMEOUT_SEG,
        )
        if resp.status_code in (200, 201, 204):
            id_registro = obter_id_registro(payload["email"])
            return True, "", id_registro
        # 409 = violação de unicidade (e-mail já cadastrado)
        if resp.status_code == 409 or "duplicate key" in resp.text.lower() or "23505" in resp.text:
            return False, "duplicado", None
        return False, f"erro_http_{resp.status_code}", None
    except Exception:
        return False, "erro_rede", None
