"""ui/estado_inicial.py — Tela de boas-vindas com i18n."""

import streamlit as st
from config import SETORES
from i18n import t, get_setores_info


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

    cards_html = '<div class="sector-grid">'
    for ico, nome, desc in get_setores_info():
        cards_html += f"""
        <div class="flip-wrapper">
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
