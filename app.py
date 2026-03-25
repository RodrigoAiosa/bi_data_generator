import streamlit as st

from config import PAGE_CONFIG, SETORES
from styles.css import inject_css
from ui import (
    render_estado_inicial,
    render_hero,
    render_resultado,
    render_sidebar,
)

st.set_page_config(**PAGE_CONFIG)


def main() -> None:
    inject_css()
    render_hero()

    setor, data_inicio, data_fim, n_linhas, gerar = render_sidebar()

    if gerar:
        if data_fim <= data_inicio:
            st.error("Corrija as datas antes de gerar.")
            st.stop()

        with st.spinner("Gerando base de dados..."):
            fn      = SETORES[setor]
            nome    = setor.split(" ", 1)[1]   # remove o emoji do label
            tabelas = fn(n_linhas, data_inicio, data_fim)

        render_resultado(nome, tabelas)
    else:
        render_estado_inicial()


if __name__ == "__main__":
    main()
