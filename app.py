"""
ui/dados_causais.py: Aba "Dados Causais".

Diferente do resto do gerador (que produz dados só ESTATISTICAMENTE
plausíveis), aqui a relação causa-efeito entre duas variáveis é conhecida
de propósito, e é construída EM CIMA do setor que você já gerou na aba
"Gerador de Setores": a coluna de causa usa os valores reais agregados
por semana da base gerada; a coluna de efeito é simulada a partir da
fórmula causal (com defasagem, confundidor e ruído configuráveis), pra
manter o gabarito 100% confiável.

Serve pra praticar inferência causal, teste A/B e marketing mix modeling
com um cenário onde a resposta certa é conhecida de antemão, em cima dos
seus próprios dados gerados, não de um exemplo genérico desconectado.
"""
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from log_acesso import registrar_evento


def _detectar_coluna_data(df: pd.DataFrame) -> str | None:
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
    for col in df.columns:
        if any(p in col.lower() for p in ["data", "date", "dt_"]):
            return col
    return None


def _colunas_numericas_validas(df: pd.DataFrame) -> list:
    """
    Colunas candidatas a causa/efeito: numéricas de verdade (excluindo
    chave/FK, tipo id_*/sk_*) mais colunas booleanas (tratadas como
    taxa 0/1, ex.: 'usou_personal'), o que amplia bastante quais setores
    têm pelo menos 2 métricas utilizáveis nesse cenário.
    """
    numericas = df.select_dtypes(include="number").columns.tolist()
    booleanas = df.select_dtypes(include="bool").columns.tolist()
    candidatas = [c for c in numericas if not c.lower().startswith(("id_", "sk_"))]
    candidatas += booleanas
    return candidatas


def gerar_cenario_causal_do_setor(
    df_fato: pd.DataFrame, col_data: str, col_causa: str, col_efeito_label: str,
    direcao: int, tem_confundidor: bool, efeito_pct: float, defasagem: int,
    ruido_pct: float, nome_setor: str, fato_nome: str, seed: int | None = None,
) -> tuple[pd.DataFrame, dict]:
    """
    Monta a série temporal real (agregada por semana) da coluna de causa
    escolhida, a partir da base já gerada, e calcula um efeito SIMULADO
    causalmente a partir dela (com defasagem, confundidor e ruído). O
    gabarito documenta exatamente o que é real e o que é simulado.
    """
    rng = np.random.default_rng(seed)

    df = df_fato[[col_data, col_causa]].copy()
    df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
    df = df.dropna(subset=[col_data])
    if df.empty:
        raise ValueError("Não foi possível interpretar a coluna de data dessa tabela fato.")

    serie = df.set_index(col_data).resample("W")[col_causa].sum().reset_index()
    serie.columns = ["data", "causa"]
    n_periodos = len(serie)
    if n_periodos < 6:
        raise ValueError(
            "Poucos períodos pra montar uma série temporal causal (gere a base com um "
            "período mais longo, pelo menos 6 semanas)."
        )

    causa = serie["causa"].values.astype(float)
    desvio = causa.std()
    causa_normalizada = (causa - causa.mean()) / (desvio if desvio else 1)

    confundidor = None
    if tem_confundidor:
        confundidor = 1 + 0.15 * np.sin(2 * np.pi * np.arange(n_periodos) / 52)

    media_abs = float(np.abs(causa).mean())
    base_efeito = media_abs * 4.0 if media_abs else 100.0

    efeito = np.full(n_periodos, base_efeito)
    for t in range(n_periodos):
        t_ref = max(0, t - defasagem)
        contrib_causal = direcao * (efeito_pct / 100) * base_efeito * causa_normalizada[t_ref]
        contrib_confundidor = (confundidor[t] - 1) * base_efeito * 0.5 if confundidor is not None else 0.0
        efeito[t] = base_efeito + contrib_causal + contrib_confundidor

    ruido_efeito = rng.normal(0, base_efeito * (ruido_pct / 100), n_periodos)
    efeito = np.clip(efeito + ruido_efeito, 0, None)

    nome_col_efeito = f"{col_efeito_label} (simulado)"
    df_final = pd.DataFrame({
        "data": serie["data"],
        col_causa: causa.round(2),
        nome_col_efeito: efeito.round(2),
    })
    if confundidor is not None:
        df_final["Índice de Sazonalidade"] = confundidor.round(4)

    gabarito = {
        "setor": nome_setor,
        "tabela_fato": fato_nome,
        "coluna_causa": f"{col_causa} (valores REAIS da base gerada, agregados por semana)",
        "coluna_efeito": f"{nome_col_efeito} (valores 100% SIMULADOS pela fórmula causal)",
        "relacao_causal": f"{col_causa} {'AUMENTA' if direcao > 0 else 'REDUZ'} {col_efeito_label}",
        "forca_do_efeito_pct": efeito_pct,
        "defasagem_em_semanas": defasagem,
        "tem_confundidor": tem_confundidor,
        "intensidade_do_ruido_pct": ruido_pct,
        "aviso": (
            f"A coluna '{col_causa}' usa os valores reais agregados por semana da base de "
            f"'{nome_setor}' que você gerou. Já a coluna '{nome_col_efeito}' não usa os "
            f"valores reais de '{col_efeito_label}' na base original, ela é inteiramente "
            f"recalculada pela fórmula causal, pra garantir que o gabarito seja confiável."
        ),
    }
    return df_final, gabarito


def montar_gabarito_causal_txt(gabarito: dict) -> str:
    linhas = ["GABARITO CAUSAL (não olhe antes de tentar sua própria análise)", ""]
    for chave, valor in gabarito.items():
        linhas.append(f"{chave}: {valor}")
    return "\n".join(linhas)


def render_dados_causais() -> None:
    st.markdown("## 🧬 Dados Causais")
    st.caption(
        "Diferente do resto do gerador (dados só estatisticamente plausíveis), aqui a "
        "relação causa-efeito é conhecida de propósito, construída em cima do setor que "
        "você já gerou. Ideal para praticar inferência causal, teste A/B e marketing mix "
        "modeling com o gabarito certo na mão."
    )

    dados_gerados = st.session_state.get("ultima_geracao")
    if not dados_gerados:
        st.info(
            "Gere uma base primeiro na aba '🏭 Gerador de Setores' (escolha um setor, defina "
            "o período e clique em 'Gerar base agora'). O cenário causal é construído em "
            "cima dela."
        )
        return

    nome_setor = dados_gerados["nome"]
    tabelas = dados_gerados["tabelas"]
    fato_keys = [k for k in tabelas if k.startswith("Fato")]

    if not fato_keys:
        st.warning("Essa base não tem nenhuma tabela fato pra usar como cenário causal.")
        return

    fato_escolhido = (
        st.selectbox("Tabela fato", fato_keys) if len(fato_keys) > 1 else fato_keys[0]
    )
    df_fato = tabelas[fato_escolhido]

    col_data = _detectar_coluna_data(df_fato)
    if not col_data:
        st.warning(f"A tabela '{fato_escolhido}' não tem coluna de data pra montar uma série temporal.")
        return

    colunas_num = _colunas_numericas_validas(df_fato)
    if len(colunas_num) < 2:
        st.warning(
            f"A tabela '{fato_escolhido}' precisa de pelo menos 2 colunas numéricas "
            f"(fora chaves) pra montar causa e efeito."
        )
        return

    st.success(f"Usando a base de **{nome_setor}** (tabela **{fato_escolhido}**) como cenário causal.")

    col1, col2 = st.columns(2)
    with col1:
        col_causa = st.selectbox(
            "Qual coluna é a CAUSA?", colunas_num, key="causal_col_causa",
            help="A variável que, na sua hipótese, provoca a mudança na outra. Os valores "
                 "usados são os REAIS da base que você gerou, agregados por semana.",
        )
    with col2:
        opcoes_efeito = [c for c in colunas_num if c != col_causa]
        col_efeito_label = st.selectbox(
            "Qual coluna representa o EFEITO?", opcoes_efeito, key="causal_col_efeito",
            help="Só o nome é usado como referência temática: o valor gerado é 100% "
                 "simulado pela fórmula causal (confira no gabarito depois de gerar).",
        )

    direcao_texto = st.radio(
        "A causa AUMENTA ou REDUZ o efeito?", ["Aumenta", "Reduz"], horizontal=True,
        help="Define a direção da relação: aumentar a causa também aumenta o efeito "
             "(positiva, ex.: marketing → vendas), ou aumentar a causa reduz o efeito "
             "(negativa, ex.: preço → demanda).",
    )
    direcao = 1 if direcao_texto == "Aumenta" else -1

    tem_confundidor = st.toggle(
        "Incluir um confundidor (sazonalidade)?", value=True,
        help="Um confundidor é uma terceira variável que afeta o efeito por fora da causa "
             "escolhida (aqui, uma sazonalidade cíclica ao longo do ano). Ajuda a treinar a "
             "diferença entre correlação espúria e causalidade real.",
    )

    col3, col4, col5 = st.columns(3)
    with col3:
        efeito_pct = st.slider(
            "Força do efeito causal (%)", 5, 60, 20,
            help="Quanto maior, mais forte a causa realmente empurra o efeito, tornando a "
                 "relação mais fácil de detectar numa análise estatística.",
        )
    with col4:
        defasagem = st.slider(
            "Defasagem (semanas)", 0, 8, 2,
            help="Quantas semanas depois da causa o efeito realmente aparece. Testar "
                 "correlação sem considerar essa defasagem tende a esconder ou subestimar "
                 "a relação real.",
        )
    with col5:
        ruido_pct = st.slider(
            "Intensidade do ruído (%)", 0, 50, 15,
            help="Quanto maior, mais difícil enxergar a relação causal no meio do barulho "
                 "estatístico, mais parecido com dado do mundo real.",
        )

    if st.button("🧬 Gerar cenário causal", type="primary", use_container_width=True, key="btn_gerar_causal"):
        try:
            df_causal, gabarito = gerar_cenario_causal_do_setor(
                df_fato, col_data, col_causa, col_efeito_label, direcao, tem_confundidor,
                efeito_pct, defasagem, ruido_pct, nome_setor, fato_escolhido,
            )
        except ValueError as e:
            st.error(str(e))
            return

        st.session_state["causal_df"] = df_causal
        st.session_state["causal_gabarito"] = gabarito
        registrar_evento("gerou_dados_causais", setor=nome_setor, volume=len(df_causal), status="sucesso")

    if "causal_df" not in st.session_state:
        return

    df = st.session_state["causal_df"]
    gabarito = st.session_state["causal_gabarito"]
    colunas_grafico = [c for c in df.columns if c != "data" and "Sazonalidade" not in c]

    st.markdown("### 📈 Causa e efeito ao longo do tempo")
    fig = px.line(df, x="data", y=colunas_grafico, labels={"value": "", "variable": "", "data": ""})
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🔬 Amostra dos dados")
    st.dataframe(df.head(10), use_container_width=True)

    with st.expander("🔍 Ver gabarito causal (spoiler, tente sua análise antes de abrir)"):
        for chave, valor in gabarito.items():
            st.markdown(f"**{chave}**: {valor}")

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            "📥 Baixar dados (.csv)",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="dados_causais.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_dl2:
        st.download_button(
            "📥 Baixar gabarito causal (.txt)",
            data=montar_gabarito_causal_txt(gabarito).encode("utf-8"),
            file_name="gabarito_causal.txt",
            mime="text/plain",
            use_container_width=True,
        )
