"""
ui/dados_causais.py: Aba "Dados Causais".

Diferente do resto do gerador (que produz dados só ESTATISTICAMENTE
plausíveis), aqui a relação causa-efeito entre duas variáveis é conhecida
de propósito: o dado é gerado encadeando matematicamente a causa no
efeito (com defasagem, confundidor e ruído configuráveis), e o "gabarito
causal" com os parâmetros reais usados fica disponível pra conferência.

Serve pra praticar inferência causal, teste A/B e marketing mix modeling
com um cenário onde a resposta certa é conhecida de antemão, algo que
datasets sintéticos comuns (inclusive o resto deste projeto) não oferecem.
"""
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from log_acesso import registrar_evento

CENARIOS_CAUSAIS = {
    "marketing_vendas": {
        "nome": "📢 Marketing → Vendas (com defasagem)",
        "descricao": (
            "Investimento em marketing causa aumento nas vendas, mas o efeito não é "
            "imediato: leva algumas semanas até aparecer, e existe uma sazonalidade "
            "que afeta as vendas por fora do marketing (um confundidor clássico)."
        ),
        "causa_nome": "Investimento em Marketing",
        "causa_unidade": "R$",
        "efeito_nome": "Vendas",
        "efeito_unidade": "R$",
        "direcao": 1,
        "tem_confundidor": True,
        "confundidor_nome": "Índice de Sazonalidade",
        "efeito_padrao_pct": 15,
        "defasagem_padrao": 2,
        "granularidade": "semana",
        "base_causa": 8000,
        "escala_efeito": 3.0,
    },
    "preco_demanda": {
        "nome": "🏷️ Preço → Demanda (elasticidade)",
        "descricao": (
            "Aumento de preço reduz a quantidade demandada (elasticidade-preço "
            "clássica de microeconomia). O efeito é praticamente imediato, sem "
            "defasagem relevante, e sem confundidor externo neste cenário."
        ),
        "causa_nome": "Preço do Produto",
        "causa_unidade": "R$",
        "efeito_nome": "Unidades Vendidas",
        "efeito_unidade": "un",
        "direcao": -1,
        "tem_confundidor": False,
        "confundidor_nome": None,
        "efeito_padrao_pct": 20,
        "defasagem_padrao": 0,
        "granularidade": "dia",
        "base_causa": 80,
        "escala_efeito": 12.0,
    },
    "treinamento_produtividade": {
        "nome": "🎓 Treinamento → Produtividade",
        "descricao": (
            "Horas de treinamento da equipe causam aumento de produtividade, mas "
            "o aprendizado leva algumas semanas até virar prática. A rotatividade "
            "da equipe (turnover) é um confundidor: afeta a produtividade por conta própria."
        ),
        "causa_nome": "Horas de Treinamento",
        "causa_unidade": "h",
        "efeito_nome": "Produtividade",
        "efeito_unidade": "unidades/h",
        "direcao": 1,
        "tem_confundidor": True,
        "confundidor_nome": "Taxa de Rotatividade (Turnover)",
        "efeito_padrao_pct": 10,
        "defasagem_padrao": 3,
        "granularidade": "semana",
        "base_causa": 20,
        "escala_efeito": 2.5,
    },
    "manutencao_falhas": {
        "nome": "🔧 Manutenção Preventiva → Redução de Falhas",
        "descricao": (
            "Mais horas de manutenção preventiva reduzem a taxa de falhas do "
            "equipamento, com uma pequena defasagem até o efeito aparecer. "
            "Sem confundidor relevante neste cenário."
        ),
        "causa_nome": "Horas de Manutenção Preventiva",
        "causa_unidade": "h",
        "efeito_nome": "Taxa de Falhas",
        "efeito_unidade": "falhas/100 unidades",
        "direcao": -1,
        "tem_confundidor": False,
        "confundidor_nome": None,
        "efeito_padrao_pct": 25,
        "defasagem_padrao": 1,
        "granularidade": "semana",
        "base_causa": 15,
        "escala_efeito": 1.8,
    },
}


def gerar_dados_causais(
    cenario_key: str, n_periodos: int, efeito_pct: float, defasagem: int,
    ruido_pct: float, seed: int | None = None,
) -> tuple[pd.DataFrame, dict]:
    """
    Gera (df, gabarito) para o cenário causal escolhido. A variável causa
    é um passeio aleatório com leve tendência; o efeito é calculado a
    partir da causa DEFASADA (efeito[t] depende de causa[t - defasagem]),
    mais a contribuição de um confundidor (quando existe) e ruído
    aleatório por cima. O gabarito documenta os parâmetros reais usados.
    """
    cfg = CENARIOS_CAUSAIS[cenario_key]
    rng = np.random.default_rng(seed)

    base_causa = cfg["base_causa"]
    tendencia = np.linspace(0, base_causa * 0.15, n_periodos)
    passeio = np.cumsum(rng.normal(0, base_causa * 0.02, n_periodos))
    causa = base_causa + tendencia + passeio
    causa = np.clip(causa, base_causa * 0.25, None)

    confundidor = None
    if cfg["tem_confundidor"]:
        ciclo = 52 if cfg["granularidade"] == "semana" else 365
        confundidor = 1 + 0.15 * np.sin(2 * np.pi * np.arange(n_periodos) / ciclo)

    causa_normalizada = (causa - causa.mean()) / (causa.std() if causa.std() else 1)
    base_efeito = base_causa * cfg["escala_efeito"]

    efeito = np.full(n_periodos, float(base_efeito))
    for t in range(n_periodos):
        t_ref = max(0, t - defasagem)
        contrib_causal = cfg["direcao"] * (efeito_pct / 100) * base_efeito * causa_normalizada[t_ref]
        contrib_confundidor = (confundidor[t] - 1) * base_efeito * 0.5 if confundidor is not None else 0.0
        efeito[t] = base_efeito + contrib_causal + contrib_confundidor

    ruido_efeito = rng.normal(0, base_efeito * (ruido_pct / 100), n_periodos)
    efeito = np.clip(efeito + ruido_efeito, 0, None)

    freq = "W" if cfg["granularidade"] == "semana" else "D"
    datas = pd.date_range("2024-01-01", periods=n_periodos, freq=freq)

    df = pd.DataFrame({
        "data": datas,
        cfg["causa_nome"]: causa.round(2),
        cfg["efeito_nome"]: efeito.round(2),
    })
    if confundidor is not None:
        df[cfg["confundidor_nome"]] = confundidor.round(4)

    gabarito = {
        "cenario": cfg["nome"],
        "relacao_causal": (
            f"{cfg['causa_nome']} {'AUMENTA' if cfg['direcao'] > 0 else 'REDUZ'} "
            f"{cfg['efeito_nome']}"
        ),
        "forca_do_efeito_pct": efeito_pct,
        "defasagem_em_periodos": defasagem,
        "granularidade": cfg["granularidade"],
        "tem_confundidor": cfg["tem_confundidor"],
        "nome_do_confundidor": cfg["confundidor_nome"] or "(nenhum neste cenário)",
        "intensidade_do_ruido_pct": ruido_pct,
        "aviso": (
            "O efeito em cada período depende da CAUSA de 'defasagem_em_periodos' "
            "períodos atrás, não da causa no mesmo período. Testar correlação sem "
            "considerar essa defasagem vai subestimar (ou não encontrar) a relação real."
        ),
    }
    return df, gabarito


def _montar_gabarito_txt(gabarito: dict) -> str:
    linhas = ["GABARITO CAUSAL (não olhe antes de tentar sua própria análise)", ""]
    for chave, valor in gabarito.items():
        linhas.append(f"{chave}: {valor}")
    return "\n".join(linhas)


def render_dados_causais() -> None:
    st.markdown("## 🧬 Dados Causais")
    st.caption(
        "Diferente do resto do gerador (dados só estatisticamente plausíveis), aqui a "
        "relação causa-efeito entre duas variáveis é conhecida de propósito, com "
        "defasagem, confundidor e ruído configuráveis. Ideal para praticar inferência "
        "causal, teste A/B e marketing mix modeling com o gabarito certo na mão."
    )

    cenario_key = st.selectbox(
        "Cenário causal",
        options=list(CENARIOS_CAUSAIS.keys()),
        format_func=lambda k: CENARIOS_CAUSAIS[k]["nome"],
    )
    cfg = CENARIOS_CAUSAIS[cenario_key]
    st.info(cfg["descricao"])

    col1, col2, col3 = st.columns(3)
    with col1:
        n_periodos = st.slider("Quantos períodos gerar?", 26, 156, 78)
    with col2:
        efeito_pct = st.slider(
            "Força do efeito causal (%)", 5, 60, cfg["efeito_padrao_pct"],
            help="Quanto maior, mais forte a causa realmente empurra o efeito.",
        )
    with col3:
        defasagem = st.slider(
            f"Defasagem ({cfg['granularidade']}s)", 0, 8, cfg["defasagem_padrao"],
            help="Quantos períodos depois da causa o efeito realmente aparece.",
        )

    ruido_pct = st.slider(
        "Intensidade do ruído estatístico (%)", 0, 50, 15,
        help="Quanto maior, mais difícil enxergar a relação causal no meio do barulho, "
             "mais parecido com dado real.",
    )

    if st.button("🧬 Gerar dados causais", type="primary", use_container_width=True, key="btn_gerar_causal"):
        df, gabarito = gerar_dados_causais(cenario_key, n_periodos, efeito_pct, defasagem, ruido_pct)
        st.session_state["causal_df"] = df
        st.session_state["causal_gabarito"] = gabarito
        st.session_state["causal_cfg"] = cfg
        registrar_evento("gerou_dados_causais", setor=cfg["nome"], volume=n_periodos, status="sucesso")

    if "causal_df" not in st.session_state:
        return

    df = st.session_state["causal_df"]
    cfg_atual = st.session_state["causal_cfg"]
    gabarito = st.session_state["causal_gabarito"]

    st.markdown("### 📈 Causa e efeito ao longo do tempo")
    fig = px.line(
        df, x="data", y=[cfg_atual["causa_nome"], cfg_atual["efeito_nome"]],
        labels={"value": "", "variable": "", "data": ""},
    )
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
            data=_montar_gabarito_txt(gabarito).encode("utf-8"),
            file_name="gabarito_causal.txt",
            mime="text/plain",
            use_container_width=True,
        )
