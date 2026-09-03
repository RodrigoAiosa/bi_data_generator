"""
ui/carrossel_pbi.py: Aba "🖥️ Carrossel Power BI".

Envie o arquivo .pbix do seu relatório (ou o .zip de um projeto .pbip),
marque quais páginas quer incluir, cole o link (ou o código de inserção)
do relatório publicado no Power BI Service, e baixe um arquivo HTML
pronto que alterna sozinho entre as páginas selecionadas a cada N
segundos — útil para deixar num monitor/TV de sala em modo apresentação.
"""

import streamlit as st

from generators.carrossel_pbi import (
    ArquivoInvalidoError,
    extrair_paginas_do_zip,
    extrair_report_id_ctid,
    gerar_html_carrossel,
    montar_url_embed,
)


def render_carrossel_pbi() -> None:
    st.markdown("## 🖥️ Carrossel Power BI")
    st.caption(
        "Envie o **arquivo .pbix** do seu relatório (ou o .zip de um projeto .pbip), "
        "marque quais páginas quer incluir, cole o **link do relatório publicado** no "
        "Power BI Service, e baixe um HTML pronto que alterna sozinho entre as páginas "
        "selecionadas a cada X segundos — ótimo para deixar rodando num monitor ou TV de "
        "sala em modo apresentação."
    )

    with st.expander("❓ Onde encontro esse link?"):
        st.markdown(
            "No Power BI Service, abra o relatório publicado e vá em **Arquivo → Inserir "
            "relatório → Site ou portal**. Cole aqui embaixo o link (ou o código `<iframe>` "
            "inteiro) que aparece lá — a ferramenta identifica sozinha o `reportId` e o "
            "`ctid` dentro dele, não precisa recortar nada."
        )

    arquivo = st.file_uploader(
        "Arquivo .pbix (ou .zip de um projeto .pbip)",
        type=["pbix", "zip"],
        key="carrossel_arquivo",
        help="Envie o .pbix exportado do Power BI Desktop normalmente. Também aceita o "
             ".zip de um projeto .pbip (com PBIR), se você usar esse formato.",
    )

    if not arquivo:
        st.info("Envie o arquivo para começar.")
        return

    try:
        paginas = extrair_paginas_do_zip(arquivo.getvalue())
    except ArquivoInvalidoError as e:
        st.error(str(e))
        return

    st.success(f"✅ {len(paginas)} página(s) encontrada(s) no relatório.")

    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        marcar_todas = st.button("☑️ Marcar todas", use_container_width=True, key="carrossel_marcar_todas")
    with col_sel2:
        desmarcar_todas = st.button("⬜ Desmarcar todas", use_container_width=True, key="carrossel_desmarcar_todas")

    st.markdown("**Marque as páginas que quer incluir no carrossel:**")
    paginas_selecionadas = []
    for i, (nome, page_id) in enumerate(paginas):
        chave = f"carrossel_pagina_{i}_{page_id}"
        if marcar_todas:
            st.session_state[chave] = True
        if desmarcar_todas:
            st.session_state[chave] = False
        st.session_state.setdefault(chave, True)
        marcada = st.checkbox(f"{nome}  \u2003`{page_id}`", key=chave)
        if marcada:
            paginas_selecionadas.append((nome, page_id))

    if not paginas_selecionadas:
        st.warning("Marque pelo menos uma página para continuar.")
        return

    st.divider()
    link_relatorio = st.text_area(
        "Link (ou código de inserção) do relatório publicado",
        key="carrossel_link",
        placeholder="https://app.powerbi.com/reportEmbed?reportId=...&autoAuth=true&ctid=...",
        height=100,
    )

    col3, col4, col5 = st.columns(3)
    with col3:
        intervalo = st.number_input("Trocar a cada (segundos)", min_value=1, max_value=3600, value=10, key="carrossel_intervalo")
    with col4:
        chromeless = st.checkbox("chromeless (sem barra de ferramentas)", value=True, key="carrossel_chromeless")
    with col5:
        auto_auth = st.checkbox("autoAuth", value=True, key="carrossel_autoauth")

    if not link_relatorio.strip():
        st.warning("Cole acima o link (ou código de inserção) do relatório para gerar o HTML do carrossel.")
        return

    ids = extrair_report_id_ctid(link_relatorio)
    if ids is None:
        st.error(
            "Não encontrei o `reportId` e o `ctid` nesse texto. Confirme que colou o link "
            "(ou o `<iframe>`) obtido em **Arquivo → Inserir relatório → Site ou portal**, "
            "no Power BI Service — não o link do arquivo .pbix nem outro tipo de "
            "compartilhamento."
        )
        return
    report_id, ctid = ids

    paginas_com_url = [
        (nome, page_id, montar_url_embed(report_id, ctid, page_id, chromeless, auto_auth))
        for nome, page_id in paginas_selecionadas
    ]

    with st.expander(f"📄 {len(paginas_com_url)} página(s) selecionada(s) — URLs de embed geradas", expanded=True):
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
