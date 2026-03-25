"""ui/resultado.py — Métricas, preview de tabelas e download."""

import pandas as pd
import streamlit as st

from generators.helpers import to_zip


def render_resultado(nome: str, tabelas: dict[str, pd.DataFrame]) -> None:
    """Renderiza métricas, abas de preview e botão de download do ZIP."""

    st.markdown(
        f'<div class="success-box">✅ Base <strong>{nome}</strong> gerada com sucesso!'
        f' {len(tabelas)} tabelas prontas para download.</div>',
        unsafe_allow_html=True,
    )

    # ── Resumo das tabelas ─────────────────────────────────────────────────
    st.markdown('<h3 class="section-header-plain">Resumo da base gerada</h3>', unsafe_allow_html=True)

    n_cols = min(len(tabelas), 7)
    cols   = st.columns(n_cols)

    for i, (tname, tdf) in enumerate(tabelas.items()):
        icon = "📅" if tname.startswith("dCal") else ("📊" if tname.startswith("Fato") else "📋")
        with cols[i % n_cols]:
            st.markdown(f"""
            <div class="stat-card">
                <span class="stat-card-icon">{icon}</span>
                <span class="stat-number">{len(tdf):,}</span>
                <span class="stat-label">{tname}</span>
                <span class="stat-sublabel">{len(tdf.columns)} colunas</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Preview ────────────────────────────────────────────────────────────
    st.markdown('<h3 class="section-header">Preview das tabelas</h3>', unsafe_allow_html=True)

    tabs = st.tabs(list(tabelas.keys()))
    for tab, (tname, tdf) in zip(tabs, tabelas.items()):
        with tab:
            st.dataframe(tdf.head(20), use_container_width=True)
            st.caption(f"{len(tdf):,} linhas · {len(tdf.columns)} colunas")

    # ── Download ───────────────────────────────────────────────────────────
    st.markdown('<h3 class="section-header-plain">Download</h3>', unsafe_allow_html=True)

    zip_bytes    = to_zip(tabelas)
    nome_arquivo = f"Base_BI_{nome.replace(' ', '_')}.zip"

    st.download_button(
        label=f"Baixar {nome_arquivo}",
        data=zip_bytes,
        file_name=nome_arquivo,
        mime="application/zip",
        use_container_width=True,
        type="primary",
    )

    st.markdown("""
    <div class="info-box">
        <strong>Dica Power BI:</strong> Importe os CSVs e crie relações usando as colunas
        <code>id_*</code> (FK) da tabela Fato para as respectivas dimensões.
        Conecte <code>dCalendario[Data]</code> ao campo de data da tabela Fato.
    </div>
    """, unsafe_allow_html=True)
