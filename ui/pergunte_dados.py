"""
ui/pergunte_dados.py: Aba "💬 Pergunte aos Dados".

Escreva uma pergunta de negócio em português (ex.: "Qual foi o total de
vendas?", "Qual vendedor teve o maior faturamento?") e veja a resposta
calculada de verdade, junto com a medida DAX equivalente que foi gerada —
pra ensinar como transformar uma pergunta em código, não só entregar o
número pronto.

Reaproveita o mesmo cache/diagrama já usados na aba DAX Sandbox, e o
motor de reconhecimento de padrões de generators/qa_engine.py (sem
nenhum LLM — o projeto não tem essa dependência).
"""

import streamlit as st

from generators.qa_engine import responder_pergunta
from ui.cache_utils import gerar_bruto_com_cache
from ui.dax_sandbox import _montar_dot
from ui.sugestao_proximo_passo import sugerir

_EXEMPLOS_GENERICOS = [
    "Quantos registros existem?",
    "Qual foi o total de {medida}?",
    "Qual foi a média de {medida}?",
    "Qual é o ticket médio?",
]


def _primeira_medida(tabelas: dict) -> str:
    from generators.relatorios_gerenciais import _colunas_medida
    fato_tables = [t for t in tabelas if t.startswith("Fato")]
    if not fato_tables:
        return "valor"
    medidas = _colunas_medida(tabelas[fato_tables[0]])
    return medidas[0] if medidas else "valor"


def render_pergunte_dados(setor: str, n_linhas: int, data_inicio, data_fim) -> None:
    st.markdown("## 💬 Pergunte aos Dados")
    st.caption(
        "Escreva uma pergunta de negócio em português e veja a resposta calculada de "
        "verdade contra os dados do setor e volume escolhidos na barra lateral, junto "
        "com a medida DAX equivalente que foi gerada — assim você aprende a traduzir a "
        "pergunta em código, não só recebe o número pronto. **Importante:** isto não é "
        "um assistente de IA de linguagem natural — é um motor de reconhecimento de "
        "padrões, limitado a perguntas de agregação (total, média, contagem, ranking, "
        "ticket médio). Ele nunca tenta prever o futuro nem explicar causas — só calcula "
        "o que já existe nos dados."
    )

    carregar = st.button("🔄 Recarregar dados", key="qa_carregar")

    chave_atual = (setor, n_linhas)
    if carregar or st.session_state.get("qa_chave") != chave_atual:
        if n_linhas >= 20_000:
            st.caption(f"ℹ️ Volume grande selecionado ({n_linhas:,} linhas) — pode levar alguns segundos.")
        with st.spinner("Carregando dados do setor…"):
            tabelas = gerar_bruto_com_cache(setor, n_linhas, data_inicio, data_fim)
        st.session_state["qa_tabelas"] = tabelas
        st.session_state["qa_chave"] = chave_atual

    tabelas = st.session_state.get("qa_tabelas")
    if tabelas is None:
        st.info("Escolha um setor na barra lateral para começar.")
        return

    with st.expander("📊 Modelo do setor (clique para ver o diagrama)", expanded=False):
        st.graphviz_chart(_montar_dot(tabelas))

    medida_exemplo = _primeira_medida(tabelas).replace("_", " ")
    exemplos = [e.format(medida=medida_exemplo) for e in _EXEMPLOS_GENERICOS]
    st.caption("Exemplos: " + " · ".join(f"_{e}_" for e in exemplos))

    pergunta = st.text_input(
        "Sua pergunta",
        key="qa_pergunta",
        placeholder=f"Ex.: Qual foi o total de {medida_exemplo}?",
    )

    if st.button("🔎 Perguntar", type="primary", key="qa_perguntar"):
        if not pergunta.strip():
            st.warning("Escreva uma pergunta antes de clicar em Perguntar.")
        else:
            resp = responder_pergunta(pergunta, tabelas)
            if resp.entendida:
                st.success(resp.resposta_texto)
                if resp.aviso:
                    st.warning(resp.aviso)
                st.code(resp.medida_dax, language="sql")
                if resp.passos:
                    with st.expander("🔍 Passo a passo", expanded=True):
                        for p in resp.passos:
                            st.markdown(f"- {p}")
                if resp.tabela_resultado is not None:
                    st.dataframe(resp.tabela_resultado, use_container_width=True)
            else:
                st.error("Não consegui entender essa pergunta com o vocabulário que reconheço.")
                for s in resp.sugestoes:
                    st.caption(f"💡 {s}")

    sugerir(
        "Gostou da medida gerada? Teste variações dela direto na aba **🧮 DAX Sandbox** "
        "pra explorar ainda mais o que dá pra calcular com esses dados."
    )
