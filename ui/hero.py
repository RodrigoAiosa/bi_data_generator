"""ui/hero.py — Bloco hero da página principal."""

import streamlit as st


def render_hero() -> None:
    """Renderiza o cabeçalho hero com título, subtítulo e estatísticas."""
    st.markdown("""
<div class="hero-wrapper">
    <div class="hero-badge">Star Schema · 10 Setores · dCalendario</div>
    <h1 class="hero-title">
        Dados reais para seu projeto de<br><span class="accent">Business Intelligence</span>
    </h1>
    <p class="hero-subtitle">
        Gere bases profissionais no modelo estrela em segundos.
        Tabelas fato, dimensões e dCalendario prontos para Power BI, Tableau e qualquer ferramenta de BI.
    </p>
    <div class="hero-stats">
        <div class="hero-stat">
            <span class="hero-stat-number">10</span>
            <span class="hero-stat-label">Setores</span>
        </div>
        <div class="hero-stat">
            <span class="hero-stat-number">10k</span>
            <span class="hero-stat-label">Linhas máx.</span>
        </div>
        <div class="hero-stat">
            <span class="hero-stat-number">.zip</span>
            <span class="hero-stat-label">Download</span>
        </div>
        <div class="hero-stat">
            <span class="hero-stat-number">free</span>
            <span class="hero-stat-label">Sem cadastro</span>
        </div>
    </div>
    <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)
