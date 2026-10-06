"""ui/estado_inicial.py — Tela de boas-vindas com i18n."""

import html

import streamlit as st
from config import SETORES
from i18n import get_lang, get_setores_info, t

# Cards em inglês: o ícone identifica o setor, exceto nos ícones repetidos por
# mais de um setor — para esses, o nome em inglês aponta para o nome em português.
_EN_PARA_PT = {
    "News Agency": "Agência de Notícias", "Public Relations": "Relações Públicas",
    "Agribusiness": "Agronegócio", "Grain Elevator & Storage": "Cerealista & Armazém de Grãos",
    "Warehousing & Self Storage": "Armazenagem & Self Storage",
    "Shopping Mall Management": "Shopping Center & Administração de Malls",
    "Architecture & Design": "Arquitetura & Design", "Government & Public Sector": "Governo & Setor Público",
    "Audiovisual & Production": "Audiovisual & Produtora", "Streaming": "Streaming",
    "Civil Aviation": "Aviação Civil", "Tourism": "Turismo", "Corporate Travel": "Viagens Corporativas",
    "Condominium & Facilities": "Condomínio & Facilities", "Human Resources": "Recursos Humanos",
    "Postal & Parcel Service": "Correios & Encomendas", "Packaging Manufacturer": "Fábrica de Embalagens",
    "Data Center & Cloud Hosting": "Data Center & Cloud Hosting", "Telemedicine": "Telemedicina",
    "Sports": "Esportes", "Stadium & Arena": "Estádio & Arena",
    "Equipment Rental": "Locação de Equipamentos", "Industrial Maintenance": "Manutenção Industrial",
    "Car Rental": "Locadora de Veículos", "Mobility": "Mobilidade",
}


def chave_setor(ico: str, nome: str) -> str:
    """Chave de SETORES ("🏋️ Academia & Fitness") do card exibido, em PT ou EN."""
    chave_pt = f"{ico} {nome}"
    if chave_pt in SETORES:
        return chave_pt
    candidatas = [k for k in SETORES if k.startswith(f"{ico} ")]
    if len(candidatas) == 1:
        return candidatas[0]
    return f"{ico} {_EN_PARA_PT.get(nome, nome)}"


def _selecionar_setor() -> None:
    """on_change do campo oculto: o JS grava "<chave do setor>|<timestamp>" quando
    o usuário clica num card. Aqui o setor vira a seleção do filtro da sidebar."""
    bruto = st.session_state.get("setor_clique_proxy", "") or ""
    chave = bruto.rsplit("|", 1)[0]
    st.session_state["setor_clique_proxy"] = ""  # permite clicar no mesmo card de novo
    if chave in SETORES:
        st.session_state["busca_setor"] = ""  # a busca poderia esconder o setor escolhido
        st.session_state["setor_sel"] = chave
        st.session_state["setor_toast"] = chave


_JS_CLIQUE_CARD = """
<script>
(function() {
    const pai = window.parent;
    if (pai.__cardSetorAplicado) return;
    pai.__cardSetorAplicado = true;
    pai.document.addEventListener('click', function(e) {
        const card = e.target.closest && e.target.closest('.flip-wrapper[data-setor]');
        if (!card) return;
        const campo = pai.document.querySelector('input[aria-label="setor_clique_proxy"]');
        if (!campo) return;
        const setter = Object.getOwnPropertyDescriptor(pai.HTMLInputElement.prototype, 'value').set;
        setter.call(campo, card.dataset.setor + '|' + Date.now());
        campo.dispatchEvent(new Event('input', { bubbles: true }));
        campo.dispatchEvent(new FocusEvent('focusout', { bubbles: true }));
    });
})();
</script>
"""


def render_estado_inicial() -> None:
    n = len(SETORES)

    st.markdown(f'<h3 class="section-header">{t("how_to_use")}</h3>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="steps-grid">
        <div class="step-card">
            <span class="step-num">01</span><span class="step-icon">🏭</span>
            <div class="step-title">{t("step1_title")}</div>
            <div class="step-text">{t("step1_text", n=n)}</div>
        </div>
        <div class="step-card">
            <span class="step-num">02</span><span class="step-icon">📅</span>
            <div class="step-title">{t("step2_title")}</div>
            <div class="step-text">{t("step2_text")}</div>
        </div>
        <div class="step-card">
            <span class="step-num">03</span><span class="step-icon">🚀</span>
            <div class="step-title">{t("step3_title")}</div>
            <div class="step-text">{t("step3_text")}</div>
        </div>
        <div class="step-card">
            <span class="step-num">04</span><span class="step-icon">📦</span>
            <div class="step-title">{t("step4_title")}</div>
            <div class="step-text">{t("step4_text")}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<h3 class="section-header">{t("sectors_available")}</h3>', unsafe_allow_html=True)

    # Clique no card -> seleciona o setor no filtro da sidebar. O card é HTML puro
    # (sem clique em Python), então o JS preenche um campo de texto oculto e o
    # on_change dele atualiza o selectbox (key "setor_sel").
    st.text_input("setor_clique_proxy", key="setor_clique_proxy",
                  label_visibility="collapsed", on_change=_selecionar_setor)
    st.iframe(_JS_CLIQUE_CARD, height=1)

    escolhido = st.session_state.get("setor_sel")
    toast = st.session_state.pop("setor_toast", None)
    if toast:
        st.toast(("Setor selecionado: " if get_lang() == "pt" else "Industry selected: ")
                 + toast, icon="✅")

    cards_html = '<div class="sector-grid">'
    for ico, nome, desc in get_setores_info():
        chave = chave_setor(ico, nome)
        sel = " sel" if chave == escolhido else ""
        cards_html += f"""
        <div class="flip-wrapper{sel}" data-setor="{html.escape(chave, quote=True)}" title="{html.escape(chave, quote=True)}">
          <div class="flip-inner">
            <div class="flip-front">
              <span class="sector-card-icon">{ico}</span>
              <div class="sector-card-name">{nome}</div>
            </div>
            <div class="flip-back">
              <div class="flip-back-title">{nome}</div>
              <div class="flip-back-desc">{desc}</div>
            </div>
          </div>
        </div>"""
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    st.markdown(f'<h3 class="section-header">{t("star_schema_title")}</h3>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="info-box">{t("star_schema_text")}</div>
    """, unsafe_allow_html=True)
