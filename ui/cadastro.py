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
    buscar_cidades,
    cadastrar,
    celular_valido,
    email_cadastrado,
    email_valido,
    esta_configurado,
    limpar_celular,
    obter_id_registro,
)
from i18n import get_lang, set_lang
from log_acesso import registrar_evento

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
    "cidade_placeholder": {"pt": "Selecione a cidade…", "en": "Select the city…"},
    "cidade_offline_aviso": {"pt": "Não consegui carregar a lista de cidades agora — digite manualmente.",
                              "en": "Couldn't load the city list right now — type it manually."},
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


# Bandeiras desenhadas em SVG (não emoji): o emoji 🇧🇷/🇺🇸 depende da fonte
# do sistema operacional e no Windows/Chrome cai para o texto "BR"/"US" em
# vez de mostrar a bandeira — por isso desenhamos o ícone nós mesmos.
_BANDEIRA_BR = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 24 16'%3E%3Crect width='24' height='16' fill='%23009739'/%3E"
    "%3Cpolygon points='12,2 22,8 12,14 2,8' fill='%23FEDD00'/%3E"
    "%3Ccircle cx='12' cy='8' r='4' fill='%23012169'/%3E%3C/svg%3E"
)
_BANDEIRA_US = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 24 16'%3E%3Crect width='24' height='16' fill='%23B22234'/%3E"
    "%3Cg fill='white'%3E%3Crect y='1.23' width='24' height='1.23'/%3E"
    "%3Crect y='3.69' width='24' height='1.23'/%3E%3Crect y='6.15' width='24' height='1.23'/%3E"
    "%3Crect y='8.61' width='24' height='1.23'/%3E%3Crect y='11.08' width='24' height='1.23'/%3E"
    "%3Crect y='13.54' width='24' height='1.23'/%3E%3C/g%3E"
    "%3Crect width='10' height='8.6' fill='%233C3B6E'/%3E%3C/svg%3E"
)


def _lang_toggle(lang: str) -> None:
    # Dois ícones de bandeira (BR/EUA) em vez de um botão de texto: o
    # st.button continua existindo (é o que dispara o clique em Python) e
    # continua clicável normalmente, mas o CSS abaixo esconde o texto e
    # desenha a bandeira como fundo do botão — usando a classe
    # "st-key-<key>" que o Streamlit atribui ao container de cada botão.
    # O idioma ativo fica com o botão desabilitado e com um contorno
    # dourado, indicando visualmente qual está selecionado.
    # !important em tudo: styles/css.py já define regras globais de botão
    # com !important (background/cor/padding/border-radius), então sem
    # !important aqui elas vencem e a bandeira nunca aparece.
    st.markdown(
        f"""
        <style>
        .st-key-cadastro_lang_pt button, .st-key-cadastro_lang_en button {{
            width: 40px !important; height: 28px !important; min-width: 40px !important;
            padding: 0 !important; border-radius: 6px !important;
            background-size: cover !important; background-position: center !important;
            background-repeat: no-repeat !important; box-shadow: none !important;
            overflow: hidden !important; border: 2px solid transparent !important;
        }}
        .st-key-cadastro_lang_pt button * , .st-key-cadastro_lang_en button * {{
            font-size: 0 !important; color: transparent !important;
        }}
        .st-key-cadastro_lang_pt button, .st-key-cadastro_lang_pt button:disabled {{
            background-image: url("{_BANDEIRA_BR}") !important;
        }}
        .st-key-cadastro_lang_en button, .st-key-cadastro_lang_en button:disabled {{
            background-image: url("{_BANDEIRA_US}") !important;
        }}
        .st-key-cadastro_lang_pt button:disabled,
        .st-key-cadastro_lang_en button:disabled {{
            /* :disabled dá especificidade extra a essa regra, senão o
               background-image do botão "ativo" some (a regra global de
               botão em styles/css.py usa o shorthand "background: ... !important",
               que zera qualquer background-image que não tenha a mesma
               especificidade + posição depois dela na cascata). */
            opacity: 1 !important; border: 2px solid #F2C811 !important; cursor: default !important;
        }}
        .st-key-cadastro_lang_pt button:not(:disabled):hover,
        .st-key-cadastro_lang_en button:not(:disabled):hover {{
            border: 2px solid rgba(242,200,17,0.5) !important; transform: scale(1.08) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    # Centralizados no topo (em vez de alinhados à direita): margens iguais
    # dos dois lados, com as duas bandeiras juntas no meio.
    _, col_pt, col_en, _ = st.columns([4, 1, 1, 4])
    with col_pt:
        if st.button("BR", key="cadastro_lang_pt", disabled=(lang == "pt"), help="Português"):
            registrar_evento("trocou_idioma_tela_cadastro")
            set_lang("pt")
            st.rerun()
    with col_en:
        if st.button("US", key="cadastro_lang_en", disabled=(lang == "en"), help="English"):
            registrar_evento("trocou_idioma_tela_cadastro")
            set_lang("en")
            st.rerun()


def _filtro_celular_somente_digitos() -> None:
    """Impede digitar letra/símbolo/espaço no campo Celular em tempo real
    (não só limpar depois do Enter). st.text_input não tem um "modo
    numérico" nativo, então isso é feito via um pedacinho de JS: acha o
    <input> pelo aria-label (Streamlit usa o rótulo do widget como
    aria-label — por isso cobre "Celular" e "Phone", os dois idiomas do
    app), intercepta cada tecla digitada e reescreve o valor mantendo só
    dígitos, até 11 (mesmo limite de max_chars no st.text_input e da
    validação em data_acesso._CELULAR_REGEX — se um mudar, o outro
    precisa mudar junto). Um MutationObserver reanexa o listener sempre
    que o Streamlit redesenha a tela (troca de aba, de idioma etc.),
    porque o elemento é recriado a cada rerun.
    st.iframe roda esse HTML num <iframe> same-origin com JS liberado,
    por isso o script consegue acessar window.parent.document pra mexer
    no campo real, fora do iframe — é um hack (sem componente
    customizado "de verdade"), mas testado e funciona de forma estável
    neste app. (Usa st.iframe, não o antigo st.components.v1.html, que
    o próprio Streamlit já marca para remoção.)
    """
    st.iframe(
        """
        <script>
        (function() {
            const ROTULOS = ["Celular", "Phone"];
            function aplicarFiltro() {
                const doc = window.parent.document;
                let alvo = null;
                for (const rotulo of ROTULOS) {
                    alvo = doc.querySelector('input[aria-label="' + rotulo + '"]');
                    if (alvo) break;
                }
                if (!alvo || alvo.dataset.filtroCelularAplicado) return;
                alvo.dataset.filtroCelularAplicado = "1";
                alvo.addEventListener('input', function(e) {
                    const limpo = e.target.value.replace(/\\D/g, '').slice(0, 11);
                    if (limpo !== e.target.value) {
                        const setter = Object.getOwnPropertyDescriptor(
                            window.parent.HTMLInputElement.prototype, 'value'
                        ).set;
                        setter.call(e.target, limpo);
                        e.target.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                });
            }
            const obs = new MutationObserver(aplicarFiltro);
            obs.observe(window.parent.document.body, { childList: true, subtree: true });
            aplicarFiltro();
        })();
        </script>
        """,
        height=1,
    )


def _form_cadastrar(lang: str) -> None:
    # Sem st.form de propósito: widgets dentro de um form só disparam rerun
    # no submit, e a Cidade precisa atualizar em tempo real assim que o
    # Estado muda — então todo o bloco usa widgets soltos + botão comum,
    # na ordem pedida: Nome, Sexo, E-mail, Celular, Estado, Cidade.
    nome = st.text_input(_s("nome_label", lang), key="cad_nome")

    col_a, col_b = st.columns(2)
    with col_a:
        sexo = st.selectbox(_s("sexo_label", lang), _SEXO_OPCOES[lang], key="cad_sexo")
    with col_b:
        email = st.text_input(_s("email_label", lang), key="cad_email")

    def _normalizar_celular_digitado() -> None:
        """on_change: remove tudo que não for dígito assim que o campo é
        confirmado (Enter/blur) — quem cola/digita algo formatado, ex.
        "(11) 99999-9999", vê o campo já virar só dígitos, com espaço
        liberado pra completar os 11, em vez de descobrir isso só no erro."""
        bruto = st.session_state.get("cad_celular", "")
        limpo = limpar_celular(bruto)
        if limpo != bruto:
            st.session_state["cad_celular"] = limpo

    celular = st.text_input(
        _s("celular_label", lang),
        max_chars=11,  # DDD (2) + número (8 fixo / 9 celular) = no máx. 11 dígitos — bate com _CELULAR_REGEX
        placeholder=_s("celular_placeholder", lang),
        help=_s("celular_help", lang),
        key="cad_celular",
        on_change=_normalizar_celular_digitado,
    )
    _filtro_celular_somente_digitos()

    col_c, col_d = st.columns(2)
    with col_c:
        estado = st.selectbox(
            _s("estado_label", lang),
            _ESTADOS_BR + [_s("estado_outro", lang)],
            key="cadastro_estado_sel",
        )
    eh_outro_pais = estado == _s("estado_outro", lang)
    cidades = [] if eh_outro_pais else buscar_cidades(estado)
    with col_d:
        if cidades:
            cidade = st.selectbox(
                _s("cidade_label", lang),
                cidades,
                index=None,
                placeholder=_s("cidade_placeholder", lang),
                key="cad_cidade_sel",
            )
        else:
            cidade = st.text_input(_s("cidade_label", lang), key="cad_cidade_txt")
    if not cidades and not eh_outro_pais:
        st.caption(_s("cidade_offline_aviso", lang))

    enviado = st.button(_s("btn_cadastrar", lang), use_container_width=True, key="cad_submit_btn")

    if not enviado:
        return

    cidade = (cidade or "").strip()
    celular_limpo = limpar_celular(celular)
    if not all([nome.strip(), sexo, email.strip(), celular_limpo, estado, cidade]):
        st.error(_s("erro_campos", lang))
        registrar_evento("clicou_cadastrar", status="erro", erro="campos_faltando")
        return
    if not email_valido(email):
        st.error(_s("erro_email", lang))
        registrar_evento("clicou_cadastrar", status="erro", erro="email_invalido")
        return
    if not celular_valido(celular):
        st.error(_s("erro_celular", lang))
        registrar_evento("clicou_cadastrar", status="erro", erro="celular_invalido")
        return

    with st.spinner("…"):
        ok, erro, id_registro = cadastrar(nome, sexo, email, celular, estado, cidade)

    if ok:
        st.session_state["cadastro_ok"] = True
        st.session_state["cadastro_email"] = email.strip()
        st.session_state["cadastro_id_registro"] = id_registro
        registrar_evento("clicou_cadastrar", status="sucesso")
        st.success(_s("sucesso", lang))
        st.rerun()
    elif erro == "duplicado":
        st.warning(_s("erro_duplicado", lang, aba=_s("aba_ja_tenho", lang)))
        registrar_evento("clicou_cadastrar", status="erro", erro="duplicado")
    else:
        st.error(_s("erro_rede", lang))
        registrar_evento("clicou_cadastrar", status="erro", erro=erro)


def _form_ja_tenho(lang: str) -> None:
    st.markdown(_s("ja_tenho_intro", lang))
    with st.form("form_ja_tenho"):
        email = st.text_input(_s("email_check_label", lang))
        verificar = st.form_submit_button(_s("btn_verificar", lang), use_container_width=True)

    if not verificar:
        return

    if not email_valido(email):
        st.error(_s("erro_email", lang))
        registrar_evento("clicou_verificar_cadastro", status="erro", erro="email_invalido")
        return

    with st.spinner("…"):
        existe = email_cadastrado(email)

    if existe is True:
        st.session_state["cadastro_ok"] = True
        st.session_state["cadastro_email"] = email.strip()
        st.session_state["cadastro_id_registro"] = obter_id_registro(email)
        registrar_evento("clicou_verificar_cadastro", status="sucesso")
        st.success(_s("sucesso", lang))
        st.rerun()
    elif existe is False:
        st.warning(_s("nao_encontrado", lang, aba=_s("aba_cadastrar", lang)))
        registrar_evento("clicou_verificar_cadastro", status="erro", erro="nao_encontrado")
    else:
        st.error(_s("erro_verificacao", lang))
        registrar_evento("clicou_verificar_cadastro", status="erro", erro="erro_verificacao")


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
