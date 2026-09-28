"""
ui/cadastro.py: tela de cadastro obrigatório, exibida uma vez antes do
usuário poder usar o BI Data Generator. Bloqueia o resto do app até que o
visitante se cadastre (ou confirme que já se cadastrou antes, por e-mail).

Se o Supabase não estiver configurado (sem `supabase_url`/`supabase_anon_key`
em st.secrets — caso do ambiente local, CI e testes), o cadastro é liberado
automaticamente: o app funciona normalmente, só sem exigir/gravar cadastro.
"""
import streamlit as st

from data_acesso import (
    cadastrar,
    celular_valido,
    email_cadastrado,
    email_valido,
    esta_configurado,
    limpar_celular,
)
from i18n import get_lang, set_lang

_ESTADOS_BR = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO",
]

_SEXO_OPCOES = {
    "pt": ["Feminino", "Masculino", "Outro", "Prefiro não informar"],
    "en": ["Female", "Male", "Other", "Prefer not to say"],
}

_STR: dict[str, dict[str, str]] = {
    "titulo":          {"pt": "📊 BI Data Generator PRO", "en": "📊 BI Data Generator PRO"},
    "subtitulo":        {"pt": "Antes de começar, complete seu cadastro gratuito — leva menos de 1 minuto.",
                          "en": "Before you start, complete your free registration — it takes less than a minute."},
    "aba_cadastrar":    {"pt": "📝 Cadastrar", "en": "📝 Register"},
    "aba_ja_tenho":     {"pt": "✅ Já sou cadastrado", "en": "✅ I already registered"},
    "nome_label":       {"pt": "Nome completo", "en": "Full name"},
    "sexo_label":       {"pt": "Sexo", "en": "Gender"},
    "email_label":      {"pt": "E-mail", "en": "Email"},
    "celular_label":    {"pt": "Celular", "en": "Phone"},
    "celular_help":     {"pt": "Somente números, com DDD (ex: 11999999999).",
                          "en": "Digits only, with area code (e.g. 11999999999)."},
    "celular_placeholder": {"pt": "11999999999", "en": "11999999999"},
    "estado_label":     {"pt": "Estado", "en": "State"},
    "estado_outro":     {"pt": "Fora do Brasil / Outro", "en": "Outside Brazil / Other"},
    "cidade_label":     {"pt": "Cidade", "en": "City"},
    "btn_cadastrar":    {"pt": "Cadastrar e começar", "en": "Register and start"},
    "erro_campos":      {"pt": "⚠️ Preencha todos os campos antes de continuar.",
                          "en": "⚠️ Please fill in all fields before continuing."},
    "erro_email":       {"pt": "⚠️ Digite um e-mail válido.", "en": "⚠️ Enter a valid email."},
    "erro_celular":     {"pt": "⚠️ Digite um celular válido: só números, com DDD (10 ou 11 dígitos).",
                          "en": "⚠️ Enter a valid phone: digits only, with area code (10 or 11 digits)."},
    "erro_duplicado":   {"pt": "Este e-mail já está cadastrado. Use a aba **{aba}** para continuar.",
                          "en": "This email is already registered. Use the **{aba}** tab to continue."},
    "erro_rede":        {"pt": "😕 Não foi possível concluir o cadastro agora. Verifique sua conexão e tente novamente.",
                          "en": "😕 Could not complete the registration right now. Check your connection and try again."},
    "sucesso":          {"pt": "✅ Cadastro concluído! Redirecionando…", "en": "✅ Registration complete! Redirecting…"},
    "ja_tenho_intro":   {"pt": "Já se cadastrou antes? Confirme seu e-mail para continuar sem preencher tudo de novo.",
                          "en": "Already registered before? Confirm your email to continue without filling everything again."},
    "email_check_label":{"pt": "Seu e-mail cadastrado", "en": "Your registered email"},
    "btn_verificar":    {"pt": "Verificar e continuar", "en": "Verify and continue"},
    "nao_encontrado":   {"pt": "Não encontramos esse e-mail cadastrado. Use a aba **{aba}** para se cadastrar.",
                          "en": "We couldn't find that email registered. Use the **{aba}** tab to register."},
    "erro_verificacao": {"pt": "😕 Não foi possível verificar agora. Tente novamente em alguns instantes.",
                          "en": "😕 Could not verify right now. Please try again in a moment."},
}


def _s(key: str, lang: str, **kwargs) -> str:
    texto = _STR[key][lang]
    return texto.format(**kwargs) if kwargs else texto


def _lang_toggle(lang: str) -> None:
    _, col = st.columns([5, 1])
    with col:
        label = "🇺🇸 English" if lang == "pt" else "🇧🇷 Português"
        if st.button(label, key="cadastro_lang_toggle", use_container_width=True):
            set_lang("en" if lang == "pt" else "pt")
            st.rerun()


def _form_cadastrar(lang: str) -> None:
    with st.form("form_cadastro", clear_on_submit=False):
        nome = st.text_input(_s("nome_label", lang))
        col_a, col_b = st.columns(2)
        with col_a:
            sexo = st.selectbox(_s("sexo_label", lang), _SEXO_OPCOES[lang])
        with col_b:
            email = st.text_input(_s("email_label", lang))
        col_c, col_d = st.columns(2)
        with col_c:
            celular = st.text_input(
                _s("celular_label", lang),
                max_chars=15,
                placeholder=_s("celular_placeholder", lang),
                help=_s("celular_help", lang),
            )
        with col_d:
            estado = st.selectbox(_s("estado_label", lang), _ESTADOS_BR + [_s("estado_outro", lang)])
        cidade = st.text_input(_s("cidade_label", lang))

        enviado = st.form_submit_button(_s("btn_cadastrar", lang), use_container_width=True)

    if not enviado:
        return

    celular_limpo = limpar_celular(celular)
    if not all([nome.strip(), sexo, email.strip(), celular_limpo, estado, cidade.strip()]):
        st.error(_s("erro_campos", lang))
        return
    if not email_valido(email):
        st.error(_s("erro_email", lang))
        return
    if not celular_valido(celular):
        st.error(_s("erro_celular", lang))
        return

    with st.spinner("…"):
        ok, erro = cadastrar(nome, sexo, email, celular, estado, cidade)

    if ok:
        st.session_state["cadastro_ok"] = True
        st.session_state["cadastro_email"] = email.strip()
        st.success(_s("sucesso", lang))
        st.rerun()
    elif erro == "duplicado":
        st.warning(_s("erro_duplicado", lang, aba=_s("aba_ja_tenho", lang)))
    else:
        st.error(_s("erro_rede", lang))


def _form_ja_tenho(lang: str) -> None:
    st.markdown(_s("ja_tenho_intro", lang))
    with st.form("form_ja_tenho"):
        email = st.text_input(_s("email_check_label", lang))
        verificar = st.form_submit_button(_s("btn_verificar", lang), use_container_width=True)

    if not verificar:
        return

    if not email_valido(email):
        st.error(_s("erro_email", lang))
        return

    with st.spinner("…"):
        existe = email_cadastrado(email)

    if existe is True:
        st.session_state["cadastro_ok"] = True
        st.session_state["cadastro_email"] = email.strip()
        st.success(_s("sucesso", lang))
        st.rerun()
    elif existe is False:
        st.warning(_s("nao_encontrado", lang, aba=_s("aba_cadastrar", lang)))
    else:
        st.error(_s("erro_verificacao", lang))


def render_gate_cadastro() -> bool:
    """
    Retorna True se o app pode continuar (cadastro não exigido, ou já feito
    nesta sessão). Retorna False depois de renderizar a tela de cadastro —
    quem chama deve interromper o restante do app nesse caso.
    """
    if not esta_configurado():
        return True
    if st.session_state.get("cadastro_ok"):
        return True

    lang = get_lang()
    _lang_toggle(lang)

    st.markdown(
        f'<h1 style="text-align:center; color:#F2C811; font-family:\'DM Sans\',sans-serif;">'
        f'{_s("titulo", lang)}</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p style="text-align:center; color:#B3B0AD; margin-bottom:2rem;">{_s("subtitulo", lang)}</p>',
        unsafe_allow_html=True,
    )

    col_esq, col_meio, col_dir = st.columns([1, 3, 1])
    with col_meio:
        aba_cad, aba_ok = st.tabs([_s("aba_cadastrar", lang), _s("aba_ja_tenho", lang)])
        with aba_cad:
            _form_cadastrar(lang)
        with aba_ok:
            _form_ja_tenho(lang)

    return False
