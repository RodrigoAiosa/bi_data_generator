"""ui/hero.py — Bloco hero com i18n."""

import streamlit as st
from config import SETORES
from i18n import t


def render_hero() -> None:
    n = len(SETORES)
    st.markdown(f"""
<div class="hero-wrapper">
    <div class="hero-badge">{t("hero_badge", n=n)}</div>
    <h1 class="hero-title">
        {t("hero_title")}<br><span class="accent">Business Intelligence</span>
    </h1>
    <p class="hero-subtitle">{t("hero_subtitle")}</p>
    <div class="hero-stats">
        <div class="hero-stat">
            <span class="hero-stat-number">{n}</span>
            <span class="hero-stat-label">{t("hero_stat_sectors")}</span>
        </div>
        <div class="hero-stat">
            <span class="hero-stat-number">100k</span>
            <span class="hero-stat-label">{t("hero_stat_rows")}</span>
        </div>
        <div class="hero-stat">
            <span class="hero-stat-number">.zip</span>
            <span class="hero-stat-label">{t("hero_stat_download")}</span>
        </div>
        <div class="hero-stat">
            <span class="hero-stat-number">free</span>
            <span class="hero-stat-label">{t("hero_stat_free")}</span>
        </div>
    </div>
    <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)
