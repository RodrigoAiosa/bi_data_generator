"""
ui/formatar_dax.py: Aba "Formatar DAX".

Cola uma expressão ou medida DAX bagunçada (sem espaço, sem quebra de
linha) e recebe ela formatada: cada argumento de função numa linha
própria quando a expressão é longa ou tem múltiplos argumentos, VAR/
RETURN cada um na sua linha, espaçamento consistente ao redor de
operadores. Implementação própria (não usa nem chama o daxformatter.com),
inspirada no mesmo espírito de formatação.
"""
import random

import streamlit as st

from generators.dax_formatter import formatar_dax
from log_acesso import registrar_evento

_EXEMPLOS = [
    "Valor Lance Mês Anterior=CALCULATE([Total Valor Lance],DATEADD(dCalendario[Data],-1,MONTH))",
    "% do Total Vendas=DIVIDE([Total Vendas],CALCULATE([Total Vendas],ALL(FatoVendas)))",
    "Total=SUM(FatoVendas[valor_total])+SUM(FatoVendas[frete])-SUM(FatoVendas[desconto])",
    "Media Movel = VAR TotalAtual = SUM(Vendas[Valor]) VAR TotalAnterior = CALCULATE(SUM(Vendas[Valor]), DATEADD(Calendario[Data], -1, MONTH)) RETURN DIVIDE(TotalAtual, TotalAnterior)",
    "Qtde Distinta de Cliente=DISTINCTCOUNT(FatoVendas[id_cliente])",
    "Receita Acumulada no Ano (YTD)=TOTALYTD([Total Vendas],dCalendario[Data])",
    "Ticket Médio=DIVIDE(SUM(FatoVendas[valor_total]),DISTINCTCOUNT(FatoVendas[id_venda]))",
]


def _sortear_exemplo() -> str:
    """Sorteia um exemplo, evitando repetir o mesmo que acabou de ser usado."""
    ultimo = st.session_state.get("_dax_ultimo_exemplo")
    candidatos = [e for e in _EXEMPLOS if e != ultimo] or _EXEMPLOS
    escolhido = random.choice(candidatos)
    st.session_state["_dax_ultimo_exemplo"] = escolhido
    return escolhido


def render_formatar_dax() -> None:
    st.markdown("## 📐 Formatar DAX")
    st.caption(
        "Cole uma expressão ou medida DAX bagunçada (sem espaço, tudo numa linha só) "
        "e receba ela formatada, no mesmo espírito do daxformatter.com: cada argumento "
        "de função numa linha própria, VAR/RETURN separados, espaçamento consistente."
    )

    if st.session_state.get("_dax_inserir_exemplo"):
        st.session_state["formatar_dax_entrada"] = _sortear_exemplo()
        st.session_state["_dax_inserir_exemplo"] = False

    dax_bruto = st.text_area(
        "Cole a expressão DAX aqui",
        height=160,
        placeholder=_EXEMPLOS[0],
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
