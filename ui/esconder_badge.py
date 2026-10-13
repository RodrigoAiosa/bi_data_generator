"""
ui/esconder_badge.py: reforço em JavaScript para esconder o selo
"Hosted with Streamlit" (e a foto do dono) que o Streamlit Cloud injeta no
canto inferior direito. O CSS de styles/css.py cobre os nomes de classe
conhecidos, mas esses nomes são gerados e mudam; aqui o selo é achado pelo
CONTEÚDO (texto / link para streamlit.io/cloud) e escondido junto com o
contêiner fixo em que ele está. Mesmo hack same-origin de ui/cadastro.py
(st.iframe + window.parent.document).
"""
import streamlit as st


def esconder_selo_streamlit() -> None:
    st.iframe(
        """
        <script>
        (function() {
            const doc = window.parent.document;
            function esconder() {
                const alvos = new Set();
                doc.querySelectorAll('a[href*="streamlit.io/cloud"]').forEach(a => alvos.add(a));
                doc.querySelectorAll('body *').forEach(el => {
                    if (el.children.length === 0 && /hosted with streamlit/i.test(el.textContent || '')) alvos.add(el);
                });
                alvos.forEach(el => {
                    // sobe até o contêiner posicionado (fixed) do selo, sem passar do <body>
                    let alvo = el, n = el;
                    for (let i = 0; i < 6 && n && n !== doc.body; i++, n = n.parentElement) {
                        const pos = window.parent.getComputedStyle(n).position;
                        if (pos === 'fixed') { alvo = n; break; }
                    }
                    alvo.style.setProperty('display', 'none', 'important');
                });
            }
            new MutationObserver(esconder).observe(doc.body, { childList: true, subtree: true });
            esconder();
        })();
        </script>
        """,
        height=1,
    )
