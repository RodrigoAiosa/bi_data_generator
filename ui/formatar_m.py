"""
ui/formatar_m.py: Aba "Formatar M".

Cola um código M (Power Query) bagunçado, tudo numa linha só, e recebe
ele formatado: bloco `let ... in ...` com cada passo em sua própria
linha, expressões longas quebradas por profundidade de parênteses/
colchetes/chaves, identificadores entre aspas (#"Nome do Passo")
preservados. Implementação própria (não usa nenhum serviço externo).
"""
import streamlit as st

from generators.m_formatter import formatar_m
from log_acesso import registrar_evento

_EXEMPLO = (
    'let Source = Csv.Document(File.Contents("C:\\Dados\\arquivo.csv"),'
    '[Delimiter=",", Encoding=65001]), #"Changed Type" = '
    'Table.TransformColumnTypes(Source,{{"Coluna1", Int64.Type}}) '
    'in #"Changed Type"'
)


def render_formatar_m() -> None:
    st.markdown("## 🔧 Formatar M")
    st.caption(
        "Cole um código M (Power Query) bagunçado, tudo numa linha só, e receba ele "
        "formatado: cada passo do bloco `let...in` em sua própria linha, expressões "
        "longas quebradas por profundidade, identificadores entre aspas preservados."
    )

    if st.session_state.get("_m_inserir_exemplo"):
        st.session_state["formatar_m_entrada"] = _EXEMPLO
        st.session_state["_m_inserir_exemplo"] = False

    m_bruto = st.text_area(
        "Cole o código M aqui",
        height=180,
        placeholder=_EXEMPLO,
        key="formatar_m_entrada",
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        formatar_clicado = st.button("🔧 Formatar", type="primary", use_container_width=True, key="btn_formatar_m")
    with col2:
        usar_exemplo = st.button("💡 Usar exemplo", use_container_width=True, key="btn_exemplo_m")

    if usar_exemplo:
        st.session_state["_m_inserir_exemplo"] = True
        st.rerun()

    if formatar_clicado:
        texto = m_bruto.strip()
        if not texto:
            st.warning("Cole um código M antes de formatar.")
        else:
            try:
                resultado = formatar_m(texto)
                st.session_state["formatar_m_resultado"] = resultado
                registrar_evento("formatou_m", volume=len(texto), status="sucesso")
            except Exception as e:
                st.session_state.pop("formatar_m_resultado", None)
                st.error(f"Não foi possível formatar esse código M. Detalhe: {e}")
                registrar_evento("formatou_m", volume=len(texto), status="erro", erro=str(e))

    if "formatar_m_resultado" in st.session_state:
        st.markdown("### ✅ M formatado")
        st.code(st.session_state["formatar_m_resultado"], language="powerquery")

        st.download_button(
            "📥 Baixar como .m",
            data=st.session_state["formatar_m_resultado"].encode("utf-8"),
            file_name="consulta_formatada.m",
            mime="text/plain",
            use_container_width=True,
        )
