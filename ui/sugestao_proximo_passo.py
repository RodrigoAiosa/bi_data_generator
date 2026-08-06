"""
ui/sugestao_proximo_passo.py: Sugestão de próximo passo entre abas.

Como o Streamlit não permite pular programaticamente de uma aba pra
outra (troca de aba é só uma decisão visual do navegador, não existe
callback do lado do servidor), essas sugestões são só um convite
textual apontando pra aba certa. Sempre aparecem DEPOIS de uma ação
já concluída, nunca interrompem nem bloqueiam o fluxo principal.
"""
import streamlit as st


def sugerir(mensagem: str) -> None:
    """Mostra uma sugestão de próximo passo, com um pouco de destaque visual."""
    st.markdown(
        f'<div class="sugestao-proximo-passo">💡 {mensagem}</div>',
        unsafe_allow_html=True,
    )
