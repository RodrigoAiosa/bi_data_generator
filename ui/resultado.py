"""ui/resultado.py: Métricas, preview de tabelas, dashboard e download."""

import pandas as pd
import streamlit as st

from generators.helpers import to_zip


def render_resultado(nome: str, tabelas: dict[str, pd.DataFrame], extra_files: dict[str, str] | None = None) -> None:
    """Renderiza métricas, abas de preview e botão de download do ZIP.

    extra_files: arquivos de texto adicionais para incluir no .zip de download
    (ex.: {"case_negocio.txt": "...", "gabarito.txt": "..."})."""

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
        # Ícone baseado no tipo da tabela
        if tname.startswith("dCal"):
            icon = "📅"
        elif tname.startswith("Fato"):
            icon = "📊"
        elif tname.startswith("Bridge"):
            icon = "🔗"
        else:
            icon = "📋"
            
        with cols[i % n_cols]:
            st.markdown(f"""
            <div class="stat-card">
                <span class="stat-card-icon">{icon}</span>
                <span class="stat-number">{len(tdf):,}</span>
                <span class="stat-label">{tname}</span>
                <span class="stat-sublabel">{len(tdf.columns)} colunas</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Preview das tabelas (incluindo bridges) ────────────────────────────
    st.markdown('<h3 class="section-header">Preview das tabelas</h3>', unsafe_allow_html=True)

    # Separar tabelas principais e bridges
    main_tables = {k: v for k, v in tabelas.items() if not k.startswith("Bridge")}
    bridge_tables = {k: v for k, v in tabelas.items() if k.startswith("Bridge")}
    
    # Tabs para tabelas principais
    if main_tables:
        tabs = st.tabs(list(main_tables.keys()))
        for tab, (tname, tdf) in zip(tabs, main_tables.items()):
            with tab:
                st.dataframe(tdf.head(20), use_container_width=True)
                st.caption(f"{len(tdf):,} linhas · {len(tdf.columns)} colunas")
    
    # Exibir bridges em expansor separado (se existirem)
    if bridge_tables:
        with st.expander("🔗 Tabelas Bridge (Relacionamentos N:N)"):
            for tname, tdf in bridge_tables.items():
                st.markdown(f"**{tname}**")
                st.dataframe(tdf.head(20), use_container_width=True)
                st.caption(f"{len(tdf):,} linhas · {len(tdf.columns)} colunas")
                st.divider()

    # ── Medidas DAX (geradas automaticamente) ──────────────────────────────
    from generators.medidas import gerar_bateria_medidas
    medidas_por_fato = gerar_bateria_medidas(tabelas)

    total_medidas = sum(
        len(lista)
        for categorias in medidas_por_fato.values()
        for lista in categorias.values()
    )

    st.markdown(
        f'<h3 class="section-header">🧮 Medidas DAX sugeridas ({total_medidas})</h3>',
        unsafe_allow_html=True,
    )

    if medidas_por_fato:
        for fato_key, categorias in medidas_por_fato.items():
            st.markdown(f"**{fato_key}**")
            for categoria, lista in categorias.items():
                if not lista:
                    continue
                with st.expander(f"{categoria} ({len(lista)})", expanded=False):
                    for m in lista:
                        st.markdown(f"**{m['nome']}**")
                        st.code(m["formula"], language="dax")
                        st.caption(m["descricao"])
                        st.divider()
    else:
        st.info("Nenhuma tabela fato encontrada para gerar medidas.")

    # ── Download ───────────────────────────────────────────────────────────
    st.markdown('<h3 class="section-header-plain">Download</h3>', unsafe_allow_html=True)

    from generators.tmdl_generator import gerar_tmdl
    tmdl_conteudo = gerar_tmdl(nome, tabelas)

    arquivos_zip = {"model.tmdl": tmdl_conteudo}
    if extra_files:
        arquivos_zip.update(extra_files)

    zip_bytes    = to_zip(tabelas, extra_files=arquivos_zip)
    nome_arquivo = f"Base_BI_{nome.replace(' ', '_')}.zip"

    from log_acesso import registrar_evento

    st.download_button(
        label=f"📥 Baixar {nome_arquivo}",
        data=zip_bytes,
        file_name=nome_arquivo,
        mime="application/zip",
        use_container_width=True,
        type="primary",
        on_click=lambda: registrar_evento("baixou_zip", setor=nome),
    )
    st.caption("O .zip inclui os CSVs de cada tabela + `model.tmdl` com todas as tabelas, "
               "relacionamentos e medidas DAX prontos para importar no Power BI (Tabular Editor / TMDL).")

    st.markdown("""
    <div class="info-box">
        <strong>💡 Dica Power BI:</strong> Importe os CSVs e crie relações usando as colunas
        <code>sk_*</code> (FK) da tabela Fato para as respectivas dimensões.
        Conecte <code>dCalendario[Data]</code> ao campo de data da tabela Fato.
    </div>
    """, unsafe_allow_html=True)
