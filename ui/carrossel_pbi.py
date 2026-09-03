"""
ui/carrossel_pbi.py: Aba "🖥️ Carrossel Power BI".

Envie o ZIP do seu projeto Power BI (formato .pbip/PBIR — a pasta que tem
Report/definition/pages/pages.json), informe o reportId e o ctid do
relatório publicado no Power BI Service, e baixe um arquivo HTML pronto
que alterna sozinho entre as páginas do relatório a cada N segundos —
útil para deixar num monitor/TV de sala em modo apresentação.
"""

import streamlit as st

from generators.carrossel_pbi import (
    ArquivoInvalidoError,
    extrair_paginas_do_zip,
    gerar_html_carrossel,
    montar_url_embed,
)


def render_carrossel_pbi() -> None:
    st.markdown("## 🖥️ Carrossel Power BI")
    st.caption(
        "Envie o **ZIP do seu projeto Power BI** (formato .pbip com PBIR — precisa conter "
        "`Report/definition/pages/pages.json`), informe o **reportId** e o **ctid** do "
        "relatório já publicado no Power BI Service, e baixe um HTML pronto que alterna "
        "sozinho entre as páginas do relatório a cada X segundos — ótimo para deixar rodando "
        "num monitor ou TV de sala em modo apresentação."
    )

    with st.expander("❓ Onde encontro o reportId e o ctid?"):
        st.markdown(
            "No Power BI Service, abra o relatório publicado e vá em **Arquivo → Inserir "
            "relatório → Site ou portal**. Na URL/código gerado, copie os valores depois de "
            "`reportId=` e `ctid=` — são dois GUIDs, algo como "
            "`a416b3a1-5446-422b-9d1c-9ac5c3089fd7`."
        )

    arquivo = st.file_uploader(
        "ZIP do projeto Power BI",
        type=["zip"],
        key="carrossel_zip",
        help="Compacte a pasta do seu projeto .pbip (ou pelo menos a pasta 'Report') em um .zip.",
    )

    col1, col2 = st.columns(2)
    with col1:
        report_id = st.text_input("reportId", key="carrossel_report_id", placeholder="a416b3a1-5446-422b-9d1c-9ac5c3089fd7")
    with col2:
        ctid = st.text_input("ctid (tenant)", key="carrossel_ctid", placeholder="3606e3a2-62f5-40ac-ad22-0d6c80989030")

    col3, col4, col5 = st.columns(3)
    with col3:
        intervalo = st.number_input("Trocar a cada (segundos)", min_value=1, max_value=3600, value=10, key="carrossel_intervalo")
    with col4:
        chromeless = st.checkbox("chromeless (sem barra de ferramentas)", value=True, key="carrossel_chromeless")
    with col5:
        auto_auth = st.checkbox("autoAuth", value=True, key="carrossel_autoauth")

    if not arquivo:
        st.info("Envie o ZIP do projeto para começar.")
        return

    try:
        paginas = extrair_paginas_do_zip(arquivo.getvalue())
    except ArquivoInvalidoError as e:
        st.error(str(e))
        return

    st.success(f"✅ {len(paginas)} página(s) encontrada(s) no projeto.")

    if not report_id.strip() or not ctid.strip():
        st.warning("Preencha o **reportId** e o **ctid** acima para gerar as URLs de embed e o HTML do carrossel.")
        with st.expander("📄 Páginas encontradas (ordem do relatório)", expanded=True):
            for i, (nome, page_id) in enumerate(paginas, 1):
                st.markdown(f"{i}. **{nome}** — `{page_id}`")
        return

    paginas_com_url = [
        (nome, page_id, montar_url_embed(report_id.strip(), ctid.strip(), page_id, chromeless, auto_auth))
        for nome, page_id in paginas
    ]

    with st.expander("📄 Páginas e URLs de embed geradas", expanded=True):
        for i, (nome, page_id, url) in enumerate(paginas_com_url, 1):
            st.markdown(f"**{i}. {nome}**")
            st.code(url, language="text")

    html_carrossel = gerar_html_carrossel(paginas_com_url, intervalo_seg=int(intervalo))
    st.download_button(
        label="📥 Baixar carrossel.html",
        data=html_carrossel,
        file_name="carrossel_powerbi.html",
        mime="text/html",
        use_container_width=True,
    )
    st.caption(
        "Abra o arquivo baixado em qualquer navegador (de preferência já autenticado no "
        "Power BI, já que os relatórios usam `autoAuth`) e deixe em tela cheia — ele troca de "
        f"página sozinho a cada {int(intervalo)} segundo(s), em loop."
    )
