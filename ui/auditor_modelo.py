"""
ui/auditor_modelo.py: Aba "Auditor de Modelo".

Cola (ou envia) o TMDL de um modelo Power BI DE VERDADE, do seu próprio
trabalho (não gerado por este projeto), e recebe uma nota de 0 a 100
mais uma lista de achados de qualidade e boas práticas, cada um com
sugestão de correção: medida duplicada disfarçada, divisão sem DIVIDE(),
coluna calculada que poderia ser medida, coluna técnica exposta,
nomenclatura inconsistente, e organização de pastas.

Implementação própria (análise de texto/regex), não usa nenhum serviço
externo nem sobe o modelo pra lugar nenhum além desta sessão.
"""
import streamlit as st

from generators.auditor_modelo import auditar_modelo
from log_acesso import registrar_evento

_SEVERIDADE_ICONE = {"alta": "🔴", "média": "🟡", "baixa": "🔵"}
_SEVERIDADE_ORDEM = {"alta": 0, "média": 1, "baixa": 2}


def _cor_nota(nota: int) -> str:
    if nota >= 85:
        return "🟢"
    if nota >= 60:
        return "🟡"
    return "🔴"


def render_auditor_modelo() -> None:
    st.markdown("## 🩺 Auditor de Modelo")
    st.caption(
        "Cole o TMDL de um modelo Power BI seu de verdade (não precisa ser gerado por este "
        "projeto) e receba uma nota de qualidade com achados acionáveis: medida duplicada, "
        "divisão sem DIVIDE(), coluna calculada que poderia ser medida, coluna técnica "
        "exposta, nomenclatura inconsistente e organização de pastas."
    )
    st.info(
        "💡 No Tabular Editor (2 ou 3), clique com o botão direito no modelo → "
        "**\"Advanced Scripting\"** ou use **\"Copy as TMDL\"**/**\"Script\"** pra pegar o "
        "texto completo do seu modelo real."
    )

    tmdl_bruto = st.text_area(
        "Cole o TMDL do seu modelo aqui",
        height=220,
        placeholder="createOrReplace\n\n\ttable Medidas\n\t\tmeasure 'Total Vendas' = SUM(...)\n\t\t\tdisplayFolder: Agregações\n...",
        key="auditor_tmdl_entrada",
    )

    arquivo = st.file_uploader("Ou envie um arquivo .tmdl / .txt", type=["tmdl", "txt"], key="auditor_tmdl_arquivo")
    if arquivo is not None:
        tmdl_bruto = arquivo.read().decode("utf-8", errors="ignore")

    if st.button("🩺 Auditar modelo", type="primary", use_container_width=True, key="btn_auditar_modelo"):
        texto = (tmdl_bruto or "").strip()
        if not texto:
            st.warning("Cole ou envie o TMDL do seu modelo antes de auditar.")
        else:
            try:
                relatorio = auditar_modelo(texto)
                st.session_state["auditor_relatorio"] = relatorio
                registrar_evento("auditou_modelo", volume=len(texto), status="sucesso")
            except Exception as e:
                st.session_state.pop("auditor_relatorio", None)
                st.error(f"Não foi possível analisar esse TMDL. Detalhe: {e}")
                registrar_evento("auditou_modelo", volume=len(texto), status="erro", erro=str(e))

    if "auditor_relatorio" not in st.session_state:
        return

    relatorio = st.session_state["auditor_relatorio"]
    resumo = relatorio["resumo"]

    st.markdown("### Resultado da auditoria")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Nota", f"{_cor_nota(relatorio['nota'])} {relatorio['nota']}/100")
    with col2:
        st.metric("Medidas analisadas", resumo["total_medidas"])
    with col3:
        st.metric("Colunas analisadas", resumo["total_colunas"])
    with col4:
        st.metric("Achados", resumo["total_achados"])

    if not relatorio["achados"]:
        st.success("Nenhum achado! Esse modelo passou por todas as checagens sem nenhum ponto de atenção.")
    else:
        achados_ordenados = sorted(relatorio["achados"], key=lambda a: _SEVERIDADE_ORDEM.get(a["severidade"], 9))
        st.markdown("### Achados")
        for a in achados_ordenados:
            icone = _SEVERIDADE_ICONE.get(a["severidade"], "⚪")
            with st.expander(f"{icone} [{a['categoria']}] {a['mensagem'][:80]}"):
                st.markdown(f"**Onde:** {a['medida']}")
                st.markdown(f"**O que é:** {a['mensagem']}")
                st.markdown(f"**Sugestão:** {a['sugestao']}")

        linhas_relatorio = [
            f"AUDITORIA DE MODELO POWER BI", "",
            f"Nota: {relatorio['nota']}/100",
            f"Medidas analisadas: {resumo['total_medidas']}",
            f"Colunas analisadas: {resumo['total_colunas']}",
            f"Relacionamentos analisados: {resumo['total_relacionamentos']}",
            f"Total de achados: {resumo['total_achados']}", "",
        ]
        for a in achados_ordenados:
            linhas_relatorio.append(f"[{a['severidade'].upper()}] {a['categoria']}")
            linhas_relatorio.append(f"  Onde: {a['medida']}")
            linhas_relatorio.append(f"  {a['mensagem']}")
            linhas_relatorio.append(f"  Sugestão: {a['sugestao']}")
            linhas_relatorio.append("")

        st.download_button(
            "📥 Baixar relatório completo (.txt)",
            data="\n".join(linhas_relatorio).encode("utf-8"),
            file_name="auditoria_modelo.txt",
            mime="text/plain",
            use_container_width=True,
        )
