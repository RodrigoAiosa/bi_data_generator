"""
app.py — Entry point do BI Data Generator PRO.

Execute com:
    streamlit run app.py
"""

import streamlit as st

from config import PAGE_CONFIG, SETORES
from styles.css import inject_css
from ui import (
    render_dashboard,
    render_estado_inicial,
    render_hero,
    render_resultado,
    render_sidebar,
)

st.set_page_config(**PAGE_CONFIG)

_SAMPLE_SIZE = 2_000   # linhas usadas no preview automático do dashboard


@st.cache_data(show_spinner=False)
def _gerar_amostra(setor: str) -> dict:
    """Gera amostra pequena para o preview do dashboard (cacheada por setor)."""
    from datetime import date
    fn = SETORES[setor]
    return fn(_SAMPLE_SIZE, date(2023, 1, 1), date(2023, 12, 31))


def render_dashboard_preview(nome: str, setor: str) -> None:
    """Preview do dashboard com amostra automática de 2.000 linhas."""
    st.markdown("""
    <div style="
        background: linear-gradient(145deg, rgba(167,139,250,0.07) 0%, rgba(124,58,237,0.04) 100%);
        border: 1px solid rgba(167,139,250,0.2);
        border-radius: 14px;
        padding: 14px 20px;
        margin-bottom: 28px;
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 0.88rem;
        color: #c4b5fd;
    ">
        <span style="font-size:1.2rem;">⚡</span>
        <span>
            <strong style="color:#a78bfa;">Preview automático</strong> —
            amostra de 2.000 linhas gerada para o setor selecionado.
            Para usar os dados reais configure os parâmetros e clique em
            <strong style="color:#a78bfa;">Gerar base agora</strong>.
        </span>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner(f"Carregando preview de {nome}..."):
        tabelas = _gerar_amostra(setor)

    render_dashboard(nome, tabelas)


def main() -> None:
    inject_css()
    render_hero()

    setor, data_inicio, data_fim, n_linhas, gerar = render_sidebar()
    nome = setor.split(" ", 1)[1]   # remove o emoji do label

    if gerar:
        # ── Geração real com parâmetros do usuário ────────────────────────
        if data_fim <= data_inicio:
            st.error("Corrija as datas antes de gerar.")
            st.stop()

        with st.spinner("Gerando base de dados..."):
            fn      = SETORES[setor]
            tabelas = fn(n_linhas, data_inicio, data_fim)

        tab_base, tab_dash = st.tabs(["📦 Base de Dados", "📊 Dashboard"])

        with tab_base:
            render_resultado(nome, tabelas)

        with tab_dash:
            render_dashboard(nome, tabelas)

    else:
        # ── Tela inicial: Início + preview do setor selecionado ───────────
        tab_inicio, tab_preview = st.tabs([
            "🏠 Início",
            f"📊 Dashboard — {nome}",
        ])

        with tab_inicio:
            render_estado_inicial()

        with tab_preview:
            render_dashboard_preview(nome, setor)


if __name__ == "__main__":
    main()
