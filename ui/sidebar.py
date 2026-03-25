"""ui/sidebar.py — Sidebar completa da aplicação."""

from datetime import date

import streamlit as st

from config import SETORES, SLIDER_DEFAULT, SLIDER_MAX, SLIDER_MIN, SLIDER_STEP

_LABEL_STYLE = (
    'font-family: Syne, sans-serif; font-size: 0.7rem; font-weight: 700;'
    ' letter-spacing: 2px; text-transform: uppercase; color: #4a5568;'
)


def render_sidebar() -> tuple[str, date, date, int, bool]:
    """
    Renderiza a sidebar completa.

    Returns
    -------
    setor : str
    data_inicio : date
    data_fim : date
    n_linhas : int
    gerar : bool
    """
    with st.sidebar:
        # ── Logo / título ──────────────────────────────────────────────────
        st.markdown("""
        <div style="padding: 8px 0 20px;">
            <div style="font-family: Syne, sans-serif; font-size: 1.1rem; font-weight: 800;
                        color: #f0f4ff; margin-bottom: 4px;">BI Data Generator</div>
            <div style="font-family: Syne, sans-serif; font-size: 0.65rem; font-weight: 700;
                        letter-spacing: 3px; text-transform: uppercase; color: #a78bfa;
                        background: rgba(167,139,250,0.1); border: 1px solid rgba(167,139,250,0.25);
                        border-radius: 100px; padding: 3px 12px; display: inline-block;">PRO</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            '<div style="height:1px; background: rgba(167,139,250,0.15); margin-bottom:20px;"></div>',
            unsafe_allow_html=True,
        )

        # ── Setor ──────────────────────────────────────────────────────────
        st.markdown(f'<p style="{_LABEL_STYLE} margin-bottom: 10px;">Setor</p>', unsafe_allow_html=True)
        setor = st.selectbox("", list(SETORES.keys()), label_visibility="collapsed")

        # ── Período ────────────────────────────────────────────────────────
        st.markdown(f'<p style="{_LABEL_STYLE} margin: 18px 0 10px;">Período</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Início", value=date(2023, 1, 1))
        with col2:
            data_fim = st.date_input("Fim", value=date(2023, 12, 31))

        if data_fim <= data_inicio:
            st.markdown(
                '<div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);'
                'border-radius:10px;padding:10px 14px;font-size:0.8rem;color:#fca5a5;margin-top:8px;">'
                '&#9888; Data fim deve ser após a data início.</div>',
                unsafe_allow_html=True,
            )

        # ── Volume de dados ────────────────────────────────────────────────
        st.markdown(f'<p style="{_LABEL_STYLE} margin: 18px 0 10px;">Volume de dados</p>', unsafe_allow_html=True)
        n_linhas = st.slider(
            "",
            min_value=SLIDER_MIN,
            max_value=SLIDER_MAX,
            value=SLIDER_DEFAULT,
            step=SLIDER_STEP,
            label_visibility="collapsed",
        )
        st.markdown(
            f'<p style="font-size:0.75rem;color:#7b8ba8;text-align:center;margin-top:-8px;">'
            f'{n_linhas:,} linhas na tabela fato</p>',
            unsafe_allow_html=True,
        )

        # ── Divider + Botão ────────────────────────────────────────────────
        st.markdown(
            '<div style="height:1px; background: rgba(167,139,250,0.15); margin: 20px 0;"></div>',
            unsafe_allow_html=True,
        )
        gerar = st.button("Gerar base agora", use_container_width=True, type="primary")

    return setor, data_inicio, data_fim, n_linhas, gerar
