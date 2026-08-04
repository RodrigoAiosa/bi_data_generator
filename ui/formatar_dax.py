"""
ui/formatar_dax.py: Aba "Formatar DAX".

Cola uma expressão ou medida DAX bagunçada (sem espaço, sem quebra de
linha) e recebe ela formatada: cada argumento de função numa linha
própria quando a expressão é longa ou tem múltiplos argumentos, VAR/
RETURN cada um na sua linha, espaçamento consistente ao redor de
operadores. Implementação própria (não usa nem chama o daxformatter.com),
inspirada no mesmo espírito de formatação.
"""
import streamlit as st

from generators.dax_formatter import formatar_dax
from log_acesso import registrar_evento

_EXEMPLO = (
    "Valor Lance Mês Anterior=CALCULATE([Total Valor Lance],"
    "DATEADD(dCalendario[Data],-1,MONTH))"
)


def render_formatar_dax() -> None:
    st.markdown("## 📐 Formatar DAX")
    st.caption(
        "Cole uma expressão ou medida DAX bagunçada (sem espaço, tudo numa linha só) "
        "e receba ela formatada, no mesmo espírito do daxformatter.com: cada argumento "
        "de função numa linha própria, VAR/RETURN separados, espaçamento consistente."
    )

    if st.session_state.get("_dax_inserir_exemplo"):
        st.session_state["formatar_dax_entrada"] = _EXEMPLO
        st.session_state["_dax_inserir_exemplo"] = False

    dax_bruto = st.text_area(
        "Cole a expressão DAX aqui",
        height=160,
        placeholder=_EXEMPLO,
        key="formatar_dax_entrada",
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        formatar_clicado = st.button("📐 Formatar", type="primary", use_container_width=True, key="btn_formatar_dax")
    with col2:
        usar_exemplo = st.button("💡 Usar exemplo", use_container_width=True, key="btn_exemplo_dax")

    if usar_exemplo:
        st.session_state["_dax_inserir_exemplo"] = True
        st.rerun()

    if formatar_clicado:
        texto = dax_bruto.strip()
        if not texto:
            st.warning("Cole uma expressão DAX antes de formatar.")
        else:
            try:
                resultado = formatar_dax(texto)
                st.session_state["formatar_dax_resultado"] = resultado
                registrar_evento("formatou_dax", volume=len(texto), status="sucesso")
            except Exception as e:
                st.session_state.pop("formatar_dax_resultado", None)
                st.error(f"Não foi possível formatar essa expressão. Detalhe: {e}")
                registrar_evento("formatou_dax", volume=len(texto), status="erro", erro=str(e))

    if "formatar_dax_resultado" in st.session_state:
        st.markdown("### ✅ DAX formatado")
        st.code(st.session_state["formatar_dax_resultado"], language="dax")

        st.download_button(
            "📥 Baixar como .dax",
            data=st.session_state["formatar_dax_resultado"].encode("utf-8"),
            file_name="medida_formatada.dax",
            mime="text/plain",
            use_container_width=True,
        )
