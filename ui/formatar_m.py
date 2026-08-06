"""
ui/formatar_m.py: Aba "Formatar M".

Cola um código M (Power Query) bagunçado, tudo numa linha só, e recebe
ele formatado: bloco `let ... in ...` com cada passo em sua própria
linha, expressões longas quebradas por profundidade de parênteses/
colchetes/chaves, identificadores entre aspas (#"Nome do Passo")
preservados. Implementação própria (não usa nenhum serviço externo).
"""
import random

import streamlit as st

from generators.m_formatter import formatar_m
from log_acesso import registrar_evento
from ui.sugestao_proximo_passo import sugerir

_EXEMPLOS = [
    'let Source = Csv.Document(File.Contents("C:\\Dados\\arquivo.csv"),'
    '[Delimiter=",", Encoding=65001]), #"Changed Type" = '
    'Table.TransformColumnTypes(Source,{{"Coluna1", Int64.Type}}) '
    'in #"Changed Type"',

    'let Source = Table.NestedJoin(Vendas, {"id_cliente"}, Clientes, {"id_cliente"}, '
    '"Clientes", JoinKind.LeftOuter), #"Expanded Clientes" = '
    'Table.ExpandTableColumn(Source, "Clientes", {"nome"}) in #"Expanded Clientes"',

    'let Fonte = Excel.Workbook(File.Contents("C:\\Dados\\vendas.xlsx"), null, true), '
    '#"Planilha1_Sheet" = Fonte{[Item="Planilha1",Kind="Sheet"]}[Data], '
    '#"Cabeçalhos Promovidos" = Table.PromoteHeaders(#"Planilha1_Sheet", [PromoteAllScalars=true]) '
    'in #"Cabeçalhos Promovidos"',

    'let Origem = Table.SelectRows(Vendas, each [valor_total] > 100 and [status] = "Aprovado"), '
    '#"Colunas Removidas" = Table.RemoveColumns(Origem,{"observacao", "id_interno"}) '
    'in #"Colunas Removidas"',

    'let Source = Table.Group(Vendas, {"id_cliente"}, {{"Total", each List.Sum([valor_total]), '
    'type nullable number}}) in Source',
]


def _sortear_exemplo() -> str:
    """Sorteia um exemplo, evitando repetir o mesmo que acabou de ser usado."""
    ultimo = st.session_state.get("_m_ultimo_exemplo")
    candidatos = [e for e in _EXEMPLOS if e != ultimo] or _EXEMPLOS
    escolhido = random.choice(candidatos)
    st.session_state["_m_ultimo_exemplo"] = escolhido
    return escolhido


def render_formatar_m() -> None:
    st.markdown("## 🔧 Formatar M")
    st.caption(
        "Cole um código M (Power Query) bagunçado, tudo numa linha só, e receba ele "
        "formatado: cada passo do bloco `let...in` em sua própria linha, expressões "
        "longas quebradas por profundidade, identificadores entre aspas preservados."
    )

    if st.session_state.get("_m_inserir_exemplo"):
        st.session_state["formatar_m_entrada"] = _sortear_exemplo()
        st.session_state["_m_inserir_exemplo"] = False

    m_bruto = st.text_area(
        "Cole o código M aqui",
        height=180,
        placeholder=_EXEMPLOS[0],
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

        sugerir(
            "Também tem alguma medida DAX bagunçada pra arrumar? "
            "A aba **📐 Formatar DAX** faz o mesmo tipo de formatação, só que pra DAX."
        )
