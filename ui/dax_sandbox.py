"""
ui/dax_sandbox.py: Aba "🧮 DAX Sandbox".

Escolha um setor (reaproveitando a última geração, se os parâmetros
baterem), veja o diagrama do modelo estrela (Fato/Dim relacionados) e
escreva uma medida DAX (subconjunto pedagógico: SUM, AVERAGE, MIN, MAX,
COUNTROWS, DISTINCTCOUNT, DIVIDE, CALCULATE com filtros — inclusive
cruzando para uma dimensão relacionada) para ver o resultado calculado de
verdade contra os dados, não apenas formatado como texto.
"""

import datetime
import random

import streamlit as st

from config import SETORES
from generators.dax_engine import avaliar_medida, DaxError
from log_acesso import registrar_evento
from ui.cache_utils import gerar_bruto_com_cache
from ui.sugestao_proximo_passo import sugerir

_VOLUME_SANDBOX = 500  # volume pequeno o bastante pra ser instantâneo, grande o bastante pra ser representativo


def _detectar_fk(tabela_fato: str, tabela_dim: str, tabelas: dict) -> tuple[str, str] | None:
    """Mesma heurística de generators/dax_engine.py e generators/relatorios_gerenciais.py."""
    if tabela_dim not in tabelas or tabela_fato not in tabelas:
        return None
    dim_df = tabelas[tabela_dim]
    pk_dim = dim_df.columns[0]
    sufixo_dim = tabela_dim[3:].lower() if tabela_dim.startswith("Dim") else tabela_dim.lower()
    for col in tabelas[tabela_fato].columns:
        if not col.lower().startswith(("id_", "sk_")):
            continue
        sufixo_col = col.split("_", 1)[1] if "_" in col else col[3:]
        if sufixo_col.lower() in sufixo_dim or sufixo_dim in sufixo_col.lower():
            return col, pk_dim
    return None


def _html_escape(texto: str) -> str:
    return (
        str(texto)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _cartao_tabela(nome_tabela: str, df, cor_header: str, cor_borda: str, pk_col: str | None) -> str:
    """Monta o label HTML (Graphviz) de uma tabela como 'cartão': cabeçalho com o
    nome da tabela e uma linha por coluna — no mesmo espírito do Model View do
    Power BI Desktop."""
    linhas_html = [
        f'<TR><TD BGCOLOR="{cor_header}" ALIGN="CENTER"><B>{_html_escape(nome_tabela)}</B></TD></TR>'
    ]
    for col in df.columns:
        icone = "🔑 " if col == pk_col else ""
        linhas_html.append(
            f'<TR><TD PORT="{_html_escape(col)}" ALIGN="LEFT" BGCOLOR="#2B2B2B">'
            f'<FONT COLOR="white">{icone}{_html_escape(col)}</FONT></TD></TR>'
        )
    corpo = "".join(linhas_html)
    return (
        f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="5" '
        f'COLOR="{cor_borda}">{corpo}</TABLE>>'
    )


def _montar_dot(tabelas: dict) -> str:
    """Monta o diagrama DOT (Graphviz) do modelo, no estilo Model View do Power
    BI Desktop: cada tabela é um cartão listando suas colunas, e as linhas de
    relacionamento ligam exatamente a coluna de origem à coluna de destino,
    com marcadores de cardinalidade (1 : *)."""
    fato_tables = [t for t in tabelas if t.startswith("Fato")]
    dim_tables = [t for t in tabelas if t.startswith("Dim")]
    cal_tables = [t for t in tabelas if t.startswith("dCal")]
    outras_tables = [t for t in tabelas if t not in fato_tables and t not in dim_tables and t not in cal_tables]

    linhas = [
        "digraph G {",
        '  rankdir=LR; bgcolor="transparent"; nodesep=0.6; ranksep=0.9;',
        '  node [shape=plaintext, fontname="Arial", fontsize=10];',
        '  edge [fontname="Arial", fontsize=8, color="#666666", fontcolor="#666666"];',
    ]

    for t in fato_tables:
        pk = tabelas[t].columns[0]
        linhas.append(f'  "{t}" [label={_cartao_tabela(t, tabelas[t], "#FFD966", "#BF9000", pk)}];')
    for t in dim_tables:
        pk = tabelas[t].columns[0]
        linhas.append(f'  "{t}" [label={_cartao_tabela(t, tabelas[t], "#A9D18E", "#548235", pk)}];')
    for t in cal_tables:
        pk = tabelas[t].columns[0]
        linhas.append(f'  "{t}" [label={_cartao_tabela(t, tabelas[t], "#9DC3E6", "#2E75B6", pk)}];')
    for t in outras_tables:
        pk = tabelas[t].columns[0]
        linhas.append(f'  "{t}" [label={_cartao_tabela(t, tabelas[t], "#D9D9D9", "#808080", pk)}];')

    for fato_nome in fato_tables:
        for dim_nome in dim_tables:
            fk = _detectar_fk(fato_nome, dim_nome, tabelas)
            if fk:
                fk_col, pk_dim = fk
                linhas.append(
                    f'  "{fato_nome}":"{fk_col}":e -> "{dim_nome}":"{pk_dim}":w '
                    f'[arrowhead=none, taillabel="*", headlabel="1", labeldistance=1.8];'
                )
        for cal_nome in cal_tables:
            cal_pk = tabelas[cal_nome].columns[0]
            date_cols = [c for c in tabelas[fato_nome].columns if "data" in c.lower()]
            if date_cols:
                linhas.append(
                    f'  "{fato_nome}":"{date_cols[0]}":e -> "{cal_nome}":"{cal_pk}":w '
                    f'[arrowhead=none, style=dashed, taillabel="*", headlabel="1", labeldistance=1.8];'
                )

    # Tabelas ponte (N:N) e quaisquer outras que não sejam Fato/Dim/Calendário:
    # conecta com as dimensões relacionadas (ex.: BridgeConteudoArtista -> DimConteudo, DimArtista).
    for outras_nome in outras_tables:
        for dim_nome in dim_tables:
            fk = _detectar_fk(outras_nome, dim_nome, tabelas)
            if fk:
                fk_col, pk_dim = fk
                linhas.append(
                    f'  "{outras_nome}":"{fk_col}":e -> "{dim_nome}":"{pk_dim}":w '
                    f'[arrowhead=none, taillabel="*", headlabel="1", labeldistance=1.8];'
                )

    linhas.append("}")
    return "\n".join(linhas)


_EXEMPLOS_GENERICOS = [
    "Total = SUM({fato}[{medida}])",
    "Média = AVERAGE({fato}[{medida}])",
    "Qtd Registros = COUNTROWS({fato})",
    "Ticket Médio = DIVIDE(SUM({fato}[{medida}]), COUNTROWS({fato}))",
]


def _exemplo_com_calculate(fato: str, medida: str, dim: str, coluna_dim: str, valor: str) -> str:
    return f'Total Filtrado = CALCULATE(SUM({fato}[{medida}]), {dim}[{coluna_dim}]="{valor}")'


def _achar_medida_e_exemplos(tabelas: dict) -> tuple[str, str, list[str]]:
    fato_tables = [t for t in tabelas if t.startswith("Fato")]
    if not fato_tables:
        return "", "", []
    fato = fato_tables[0]
    df = tabelas[fato]
    numericas = [c for c in df.columns if df[c].dtype.kind in "if" and not c.lower().startswith(("id_", "sk_"))]
    if not numericas:
        return fato, "", []
    medida = numericas[0]
    exemplos = [e.format(fato=fato, medida=medida) for e in _EXEMPLOS_GENERICOS]

    dim_tables = [t for t in tabelas if t.startswith("Dim")]
    for dim in dim_tables:
        fk = _detectar_fk(fato, dim, tabelas)
        if not fk:
            continue
        dim_df = tabelas[dim]
        cats = [
            c for c in dim_df.columns
            if (dim_df[c].dtype == object or str(dim_df[c].dtype) == "str")
            and 2 <= dim_df[c].nunique() <= 20
        ]
        if cats:
            coluna_dim = cats[0]
            valor = str(dim_df[coluna_dim].iloc[0])
            exemplos.append(_exemplo_com_calculate(fato, medida, dim, coluna_dim, valor))
            break

    return fato, medida, exemplos


def render_dax_sandbox() -> None:
    st.markdown("## 🧮 DAX Sandbox")
    st.caption(
        "Escreva uma medida DAX e veja o resultado calculado de verdade contra os dados do "
        "setor escolhido — não é só formatação de texto, é o cálculo real rodando nas linhas "
        "geradas. Suporta um subconjunto pedagógico: SUM, AVERAGE, MIN, MAX, COUNTROWS, "
        "DISTINCTCOUNT, DIVIDE, CALCULATE (com filtros, inclusive cruzando para uma dimensão "
        "relacionada) e operadores aritméticos (+ - * /)."
    )

    setores_disponiveis = list(SETORES.keys())
    setor_default = st.session_state.get("ultima_geracao", {}).get("setor", setores_disponiveis[0])
    idx_default = setores_disponiveis.index(setor_default) if setor_default in setores_disponiveis else 0

    col1, col2 = st.columns([3, 1])
    with col1:
        setor = st.selectbox("Setor", options=setores_disponiveis, index=idx_default, key="dax_sandbox_setor")
    with col2:
        st.write("")
        st.write("")
        gerar_clicado = st.button("🔄 Carregar dados", use_container_width=True, key="dax_sandbox_carregar")

    chave_atual = (setor, _VOLUME_SANDBOX)
    if gerar_clicado or st.session_state.get("dax_sandbox_chave") != chave_atual:
        with st.spinner("Carregando dados do setor…"):
            tabelas = gerar_bruto_com_cache(
                setor, _VOLUME_SANDBOX,
                datetime.date(2024, 1, 1), datetime.date(2024, 12, 31),
            )
        st.session_state["dax_sandbox_tabelas"] = tabelas
        st.session_state["dax_sandbox_chave"] = chave_atual

    tabelas = st.session_state.get("dax_sandbox_tabelas")
    if tabelas is None:
        st.info("Escolha um setor e clique em **Carregar dados** para começar.")
        return

    with st.expander("📊 Modelo do setor (clique para ver o diagrama)", expanded=False):
        st.graphviz_chart(_montar_dot(tabelas))
        st.caption(
            "Tabelas Fato (amarelo) no centro, Dimensões (verde) e Calendário (azul) ao redor. "
            "As setas mostram a coluna usada para relacionar as tabelas."
        )
        for nome_tabela, df in tabelas.items():
            st.caption(f"**{nome_tabela}** ({len(df):,} linhas): {', '.join(df.columns)}")

    fato_padrao, medida_padrao, exemplos = _achar_medida_e_exemplos(tabelas)

    if not exemplos:
        st.warning("Não encontrei uma coluna numérica de medida neste setor para sugerir exemplos.")
    else:
        exemplo_escolhido = st.selectbox(
            "Exemplos prontos (escolha um para carregar, ou escreva o seu abaixo)",
            options=["— escrever a minha —"] + exemplos,
            key="dax_sandbox_exemplo_select",
        )
        if exemplo_escolhido != "— escrever a minha —" and st.session_state.get("dax_sandbox_ultimo_exemplo") != exemplo_escolhido:
            st.session_state["dax_sandbox_expressao"] = exemplo_escolhido
            st.session_state["dax_sandbox_ultimo_exemplo"] = exemplo_escolhido

    expressao = st.text_area(
        "Medida DAX",
        key="dax_sandbox_expressao",
        height=100,
        placeholder=f"Total = SUM({fato_padrao}[{medida_padrao}])" if fato_padrao else "Total = SUM(Tabela[Coluna])",
    )

    if st.button("▶️ Executar", type="primary", key="dax_sandbox_executar"):
        if not expressao.strip():
            st.warning("Escreva uma medida DAX antes de executar.")
        else:
            try:
                valor, passos, nome_medida = avaliar_medida(expressao, tabelas)
                registrar_evento("dax_sandbox_executou", setor=setor.split(" ", 1)[1] if " " in setor else setor)
                st.success(f"**{nome_medida}** = **{valor:,.4f}**")
                with st.expander("🔍 Passo a passo do cálculo", expanded=True):
                    for p in passos:
                        st.markdown(f"- {p}")
            except DaxError as e:
                st.error(f"❌ {e}")
            except Exception as e:
                st.error(
                    "Não consegui avaliar essa expressão. Confira a sintaxe (ex.: "
                    "`SUM(Tabela[Coluna])`, `DIVIDE(a, b)`, `CALCULATE(expr, Tabela[Coluna]=\"valor\")`)."
                )
                with st.expander("Detalhe técnico"):
                    st.caption(f"{type(e).__name__}: {e}")

    sugerir(
        "Já que você testou uma medida aqui, que tal levar essa mesma lógica pra aba "
        "**📐 Formatar DAX** pra deixá-la bonitinha antes de colar no seu Power BI de verdade?"
    )
