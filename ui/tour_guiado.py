"""
ui/tour_guiado.py: Tour guiado de primeira visita.

Mostra, uma vez por sessão (a primeira vez que a pessoa abre o app),
um resumo rápido das 6 ferramentas disponíveis, num modal (st.dialog),
com um botão "Pular" sempre tão visível e proeminente quanto o de
continuar, pra nunca prender ninguém.
"""
import streamlit as st

_FERRAMENTAS = [
    ("🏭", "Gerador de Setores", "100 setores de negócio prontos, com medidas DAX e modelo TMDL pro Power BI."),
    ("🤖", "Automatizar BI", "Envie sua própria planilha e receba medidas DAX e modelo automaticamente."),
    ("🎓", "Simulador PL-300", "Quiz de prática pra certificação oficial da Microsoft, com nota por domínio."),
    ("🧬", "Dados Causais", "Gera uma relação causa-efeito conhecida, pra praticar inferência causal de verdade."),
    ("📐", "Formatar DAX", "Cola uma medida bagunçada e recebe ela formatada, pronta pra usar."),
    ("🔧", "Formatar M", "O mesmo formatador, só que pra código Power Query."),
]


@st.dialog("Bem-vindo ao BI Data Generator! 👋", width="large")
def _mostrar_tour_dialog() -> None:
    st.markdown(
        "Esse app tem **6 ferramentas** dentro dele, todas de graça, sem cadastro, "
        "sem IA por trás. Um resumo rápido antes de você começar:"
    )
    for emoji, nome, descricao in _FERRAMENTAS:
        st.markdown(f"**{emoji} {nome}**  \n{descricao}")

    st.markdown("")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Pular", use_container_width=True, key="tour_pular"):
            st.session_state["_tour_visto"] = True
            st.rerun()
    with col2:
        if st.button("Entendi, vamos começar! 🚀", type="primary", use_container_width=True, key="tour_entendi"):
            st.session_state["_tour_visto"] = True
            st.rerun()


def exibir_tour_se_primeira_visita() -> None:
    """Chame uma vez, bem no início de main(), antes de qualquer outra coisa."""
    if not st.session_state.get("_tour_visto"):
        _mostrar_tour_dialog()
