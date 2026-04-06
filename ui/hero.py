"""ui/hero.py — Bloco hero da página principal."""

import streamlit as st


def render_hero() -> None:
    """Renderiza o cabeçalho hero com título e subtítulo no estilo plataforma de leads."""
    st.markdown("""
<div class="hero-wrapper">
    <h1 class="hero-title">
        PLATAFORMA DE GERAÇÃO DE LEADS
    </h1>
    <p class="hero-subtitle">
        Extraia leads do Google Maps em segundos.
    </p>
    <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)
