"""ui/sidebar.py — Sidebar completa com toggle de idioma e pesquisa."""

from datetime import date

import streamlit as st

from config import SETORES, SETORES_INFO, SLIDER_DEFAULT, SLIDER_MAX, SLIDER_MIN, SLIDER_STEP
from i18n import get_lang, set_lang, t

_LABEL_STYLE = (
    'font-family: Syne, sans-serif; font-size: 0.7rem; font-weight: 700;'
    ' letter-spacing: 2px; text-transform: uppercase; color: #4a5568;'
)

# Índice de busca: chave do setor → texto pesquisável (nome + descrição)
def _build_index() -> dict[str, str]:
    index = {}
    for key in SETORES:
        nome_limpo = key.split(" ", 1)[-1].lower()
        desc = ""
        for _ico, nome_info, desc_info in SETORES_INFO:
            if nome_info.lower() in nome_limpo or nome_limpo in nome_info.lower():
                desc = desc_info.lower()
                break
        index[key] = f"{nome_limpo} {desc}"
    return index

_BUSCA_INDEX = _build_index()


def _filtrar_setores(query: str) -> list[str]:
    q = query.strip().lower()
    if not q:
        return list(SETORES.keys())
    return [k for k, texto in _BUSCA_INDEX.items() if q in texto]


def render_sidebar() -> tuple[str, date, date, int, bool]:
    with st.sidebar:
        # ── Logo ──────────────────────────────────────────────────────────
        st.markdown("""
        <div style="padding: 8px 0 16px;">
            <div style="font-family: Syne, sans-serif; font-size: 1.1rem; font-weight: 800;
                        color: #f0f4ff; margin-bottom: 4px;">BI Data Generator</div>
            <div style="font-family: Syne, sans-serif; font-size: 0.65rem; font-weight: 700;
                        letter-spacing: 3px; text-transform: uppercase; color: #a78bfa;
                        background: rgba(167,139,250,0.1); border: 1px solid rgba(167,139,250,0.25);
                        border-radius: 100px; padding: 3px 12px; display: inline-block;">PRO</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Toggle de idioma ───────────────────────────────────────────────
        if st.button(t("lang_toggle"), use_container_width=True):
            set_lang("en" if get_lang() == "pt" else "pt")
            st.rerun()

        st.markdown(
            '<div style="height:1px; background: rgba(167,139,250,0.15); margin: 16px 0;"></div>',
            unsafe_allow_html=True,
        )

        # ── Pesquisa ───────────────────────────────────────────────────────
        st.markdown(f'<p style="{_LABEL_STYLE} margin-bottom: 8px;">{t("search_label")}</p>', unsafe_allow_html=True)
        query = st.text_input(
            "",
            placeholder=t("search_placeholder"),
            label_visibility="collapsed",
            key="busca_setor",
        )

        setores_filtrados = _filtrar_setores(query)

        if query and not setores_filtrados:
            st.markdown(
                f'<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.25);'
                f'border-radius:10px;padding:8px 12px;font-size:0.78rem;color:#fca5a5;margin-bottom:10px;">'
                f'{t("search_empty")}</div>',
                unsafe_allow_html=True,
            )
            setores_filtrados = list(SETORES.keys())

        if query and setores_filtrados:
            st.markdown(
                f'<p style="font-size:0.72rem;color:#a78bfa;margin:-4px 0 8px;">'
                f'{t("search_found", n=len(setores_filtrados))}</p>',
                unsafe_allow_html=True,
            )

        # ── Setor ──────────────────────────────────────────────────────────
        st.markdown(f'<p style="{_LABEL_STYLE} margin-bottom: 10px;">{t("sector_label")}</p>', unsafe_allow_html=True)
        setor = st.selectbox("", setores_filtrados, label_visibility="collapsed")

        # ── Período ────────────────────────────────────────────────────────
        st.markdown(f'<p style="{_LABEL_STYLE} margin: 18px 0 10px;">{t("period_label")}</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input(t("start_label"), value=date(2023, 1, 1))
        with col2:
            data_fim = st.date_input(t("end_label"), value=date(2023, 12, 31))

        if data_fim <= data_inicio:
            st.markdown(
                f'<div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);'
                f'border-radius:10px;padding:10px 14px;font-size:0.8rem;color:#fca5a5;margin-top:8px;">'
                f'{t("date_error")}</div>',
                unsafe_allow_html=True,
            )

        # ── Volume ────────────────────────────────────────────────────────
        st.markdown(f'<p style="{_LABEL_STYLE} margin: 18px 0 10px;">{t("volume_label")}</p>', unsafe_allow_html=True)
        n_linhas = st.slider("", min_value=SLIDER_MIN, max_value=SLIDER_MAX,
                             value=SLIDER_DEFAULT, step=SLIDER_STEP, label_visibility="collapsed")
        st.markdown(
            f'<p style="font-size:0.75rem;color:#7b8ba8;text-align:center;margin-top:-8px;">'
            f'{t("volume_hint", n=f"{n_linhas:,}")}</p>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div style="height:1px; background: rgba(167,139,250,0.15); margin: 20px 0;"></div>',
            unsafe_allow_html=True,
        )
        gerar = st.button(t("gerar_btn"), use_container_width=True, type="primary")

    return setor, data_inicio, data_fim, n_linhas, gerar
