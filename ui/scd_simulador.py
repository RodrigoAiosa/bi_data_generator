"""
ui/scd_simulador.py: Aba "🕰️ Simulador de Dimensões Mutáveis".

Depende da base já gerada na aba "🏭 Gerador de Setores" (mesmo padrão de
ui/dados_causais.py) — pega uma dimensão dessa base e simula a passagem
do tempo: gera uma segunda "fotografia" dela com mudanças reais
injetadas, junto com um gabarito exato de quem mudou o quê, e mostra como
ficaria o resultado correto nos 3 tratamentos clássicos de Slowly
Changing Dimension (Tipo 1, 2 e 3).
"""

import uuid

import streamlit as st

from generators.scd_simulador import gerar_cenario_scd, ScdError
from log_acesso import registrar_evento
from ui.sugestao_proximo_passo import sugerir


def render_scd_simulador() -> None:
    st.markdown("## 🕰️ Simulador de Dimensões Mutáveis")
    st.caption(
        "Pratique o assunto mais confuso (e mais cobrado no PL-300) de modelagem "
        "dimensional: **Slowly Changing Dimensions**. A ferramenta pega uma dimensão da "
        "base que você já gerou, simula uma passagem de tempo com mudanças reais "
        "injetadas (cliente mudou de segmento, produto trocou de categoria...), e monta "
        "o **gabarito exato** de quem mudou o quê — junto com o resultado correto dos "
        "3 tratamentos clássicos (Tipo 1, 2 e 3), pra você comparar com a sua própria "
        "implementação."
    )

    dados_gerados = st.session_state.get("ultima_geracao")
    if not dados_gerados:
        st.info(
            "Gere uma base primeiro na aba '🏭 Gerador de Setores' (escolha um setor, "
            "defina o período e clique em 'Gerar base agora'). O cenário de dimensão "
            "mutável é construído em cima dela."
        )
        return

    nome_setor = dados_gerados["nome"]
    tabelas = dados_gerados["tabelas"]
    dim_keys = [k for k in tabelas if k.startswith("Dim")]

    if not dim_keys:
        st.warning("Essa base não tem nenhuma tabela de dimensão pra usar nesse exercício.")
        return

    dim_escolhida = st.selectbox("Dimensão", dim_keys, key="scd_dim_escolhida")
    df_dim = tabelas[dim_escolhida]

    n_linhas_dim = len(df_dim)
    max_mudancas = max(1, min(n_linhas_dim, 100))
    default_mudancas = max(1, min(10, max_mudancas))

    n_mudancas = st.slider(
        "Quantas linhas devem mudar entre as duas fotografias?",
        min_value=1, max_value=max_mudancas, value=default_mudancas,
        key="scd_n_mudancas",
        help=f"'{dim_escolhida}' tem {n_linhas_dim} linha(s) no total.",
    )

    if st.button("🕰️ Gerar cenário", type="primary", use_container_width=True, key="btn_gerar_scd"):
        try:
            resultado = gerar_cenario_scd(tabelas, dim_escolhida, n_mudancas)
        except ScdError as e:
            st.error(str(e))
            return

        st.session_state["scd_resultado"] = resultado
        st.session_state["scd_dim_nome"] = dim_escolhida
        st.session_state["scd_id"] = uuid.uuid4().hex
        registrar_evento(
            "gerou_scd", setor=nome_setor, volume=len(resultado["gabarito"]), status="sucesso"
        )

    if "scd_resultado" not in st.session_state:
        return

    resultado = st.session_state["scd_resultado"]
    pk = resultado["coluna_pk"]
    gabarito = resultado["gabarito"]

    st.success(
        f"Cenário gerado em cima de **{st.session_state['scd_dim_nome']}** "
        f"({len(gabarito)} linha(s) alterada(s), de {len(resultado['snapshot_t0'])} no total)."
    )

    st.markdown("### 🔎 As duas fotografias")
    col_t0, col_t1 = st.columns(2)
    with col_t0:
        st.markdown("**T0 (antes)**")
        st.dataframe(resultado["snapshot_t0"], use_container_width=True, height=250)
    with col_t1:
        st.markdown("**T1 (depois)**")
        st.dataframe(resultado["snapshot_t1"], use_container_width=True, height=250)

    with st.expander("🔍 Ver gabarito (spoiler — tente identificar as mudanças sozinho antes)"):
        st.dataframe(gabarito, use_container_width=True)

    st.markdown("### 🧩 Os 3 tratamentos clássicos de SCD")
    tab1, tab2, tab3 = st.tabs(["Tipo 1 (sobrescreve)", "Tipo 2 (histórico)", "Tipo 3 (coluna anterior)"])

    with tab1:
        st.caption(
            "**SCD Tipo 1**: a linha é simplesmente sobrescrita com o valor novo — mais "
            "simples de implementar, mas perde o histórico por completo. Bom quando o "
            "dado antigo não tem nenhum valor analítico (ex.: corrigir um erro de "
            "digitação)."
        )
        st.dataframe(resultado["scd_tipo1"], use_container_width=True)

    with tab2:
        st.caption(
            "**SCD Tipo 2**: a linha antiga é preservada (com `DataFimValidade` "
            "preenchida e `RegistroAtual = False`), e uma linha nova é adicionada pro "
            "valor atual — precisa de uma chave substituta (`sk_scd`) própria, já que a "
            "mesma chave natural agora aparece em mais de uma linha. É o único dos 3 que "
            "preserva o histórico completo pra análise (ex.: 'quantas vendas esse "
            "vendedor teve enquanto ainda estava no time B?')."
        )
        st.dataframe(resultado["scd_tipo2"], use_container_width=True)

    with tab3:
        st.caption(
            "**SCD Tipo 3**: continua uma linha só por chave, mas guarda o valor "
            "anterior numa coluna irmã (`<coluna>_Anterior`). Só guarda a ÚLTIMA "
            "mudança (não uma linha por mudança, como o Tipo 2) — bom pra comparar "
            "'antes x depois' de uma mudança pontual, ruim pra reconstruir todo o "
            "histórico se a mesma coluna mudar várias vezes."
        )
        st.dataframe(resultado["scd_tipo3"], use_container_width=True)

    st.markdown("### 📥 Download")
    col_dl1, col_dl2, col_dl3, col_dl4 = st.columns(4)
    with col_dl1:
        st.download_button(
            "T0 (antes)", data=resultado["snapshot_t0"].to_csv(index=False).encode("utf-8"),
            file_name="scd_t0_antes.csv", mime="text/csv", use_container_width=True,
        )
    with col_dl2:
        st.download_button(
            "T1 (depois)", data=resultado["snapshot_t1"].to_csv(index=False).encode("utf-8"),
            file_name="scd_t1_depois.csv", mime="text/csv", use_container_width=True,
        )
    with col_dl3:
        st.download_button(
            "Gabarito", data=gabarito.to_csv(index=False).encode("utf-8"),
            file_name="scd_gabarito.csv", mime="text/csv", use_container_width=True,
        )
    with col_dl4:
        st.download_button(
            "SCD Tipo 2 (completo)", data=resultado["scd_tipo2"].to_csv(index=False).encode("utf-8"),
            file_name="scd_tipo2_resultado.csv", mime="text/csv", use_container_width=True,
        )

    sugerir(
        "Quer ver essas mesmas mudanças calculadas com DAX de verdade? Cole uma medida "
        "usando `USERELATIONSHIP` na aba **🧮 DAX Sandbox** pra praticar como lidar com "
        "relacionamento inativo (comum quando se usa SCD Tipo 2)."
    )
