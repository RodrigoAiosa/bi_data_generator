"""
app.py — Entry point do BI Data Generator PRO.

Execute com:
    streamlit run app.py
"""

import random
import time

import numpy as np
import pandas as pd
import streamlit as st

from config import PAGE_CONFIG, SETORES
from generators.dicionario import gerar_dicionario
from i18n import t
from styles.css import inject_css
try:
    from styles.seo import inject_seo
except Exception:
    def inject_seo(lang: str = "pt") -> None:
        pass  # seo.py não encontrado — SEO desabilitado
from ui import (
    render_dashboard,
    render_estado_inicial,
    render_hero,
    render_resultado,
    render_sidebar,
)

st.set_page_config(**PAGE_CONFIG)

_SAMPLE_SIZE = 2_000

# ── Strings de anomalia ───────────────────────────────────────────────────────
_ANOMALY_LABEL = {"pt": "🧪 Injetar anomalias nos dados", "en": "🧪 Inject anomalies into data"}
_ANOMALY_HELP  = {
    "pt": "Adiciona problemas reais: spike de churn, produto com margem negativa, sazonalidade extrema e outliers de valor. Ideal para praticar análise de causa raiz.",
    "en": "Adds real-world issues: churn spike, negative-margin product, extreme seasonality and value outliers. Great for practicing root-cause analysis.",
}
_ANOMALY_BADGE = {
    "pt": "⚠️ **Modo anomalia ativo** — dados contém problemas intencionais para análise de causa raiz.",
    "en": "⚠️ **Anomaly mode active** — data contains intentional issues for root-cause analysis.",
}

# ── Passos da barra de progresso ─────────────────────────────────────────────
_STEPS_PT = ["Criando dimensões…", "Gerando tabela fato…", "Calculando métricas…", "Compactando ZIP…"]
_STEPS_EN = ["Building dimensions…", "Generating fact table…", "Computing metrics…", "Compressing ZIP…"]


def _get_lang() -> str:
    from i18n import get_lang
    return get_lang()


# ── Injeção de anomalias ─────────────────────────────────────────────────────

def _injetar_anomalias(tabelas: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
    Injeta 4 tipos de anomalias nos dados para prática de análise de causa raiz:
      1. Spike de churn / cancelamentos em um mês aleatório
      2. Produto / item com margem negativa
      3. Sazonalidade extrema (queda abrupta num trimestre)
      4. Outliers de valor (registros com valores 10–30x acima da média)
    """
    tabelas = {k: v.copy() for k, v in tabelas.items()}

    fato_key = next((k for k in tabelas if k.startswith("Fato")), None)
    if fato_key is None:
        return tabelas

    fato = tabelas[fato_key]
    num_cols = fato.select_dtypes(include="number").columns.tolist()
    date_cols = [c for c in fato.columns if "data" in c.lower() or "date" in c.lower()]
    bool_cols = [c for c in fato.columns if fato[c].dtype == bool]
    val_col   = next((c for c in num_cols if any(k in c for k in ["valor","receita","preco","total","mrr"])), num_cols[0] if num_cols else None)

    # 1. Spike de churn / cancelamentos num mês aleatório
    if bool_cols and date_cols:
        try:
            date_col = date_cols[0]
            fato[date_col] = pd.to_datetime(fato[date_col], errors="coerce")
            meses = fato[date_col].dt.month.dropna().unique()
            mes_spike = random.choice(list(meses))
            mask = fato[date_col].dt.month == mes_spike
            fato.loc[mask, bool_cols[0]] = True   # força cancelamento/churn no mês
        except Exception:
            pass

    # 2. Produto / categoria com margem negativa
    margem_cols = [c for c in num_cols if "margem" in c or "lucro" in c or "desconto" in c]
    if margem_cols:
        n_neg = max(1, int(len(fato) * 0.04))
        idx = fato.sample(n_neg).index
        fato.loc[idx, margem_cols[0]] = -abs(fato[margem_cols[0]].mean()) * np.random.uniform(1.1, 2.5, n_neg)

    # 3. Sazonalidade extrema — queda de 70% num trimestre aleatório
    if val_col and date_cols:
        try:
            date_col = date_cols[0]
            trimestres = fato[date_col].dt.quarter.dropna().unique()
            trim_queda = random.choice(list(trimestres))
            mask = fato[date_col].dt.quarter == trim_queda
            fato.loc[mask, val_col] = fato.loc[mask, val_col] * 0.30
        except Exception:
            pass

    # 4. Outliers de valor (1% dos registros com valores extremos)
    if val_col:
        n_out = max(1, int(len(fato) * 0.01))
        idx = fato.sample(n_out).index
        media = fato[val_col].mean()
        fato.loc[idx, val_col] = media * np.random.uniform(10, 30, n_out)

    tabelas[fato_key] = fato
    return tabelas


# ── Barra de progresso ───────────────────────────────────────────────────────

def _gerar_com_progresso(setor: str, n_linhas: int, data_inicio, data_fim, anomalia: bool) -> dict:
    """Gera os dados exibindo barra de progresso com etapas reais."""
    lang   = _get_lang()
    steps  = _STEPS_EN if lang == "en" else _STEPS_PT
    fn     = SETORES[setor]

    bar    = st.progress(0, text=steps[0])
    status = st.empty()

    # Etapa 1 — dimensões (simulada antes da geração)
    time.sleep(0.3)
    bar.progress(20, text=steps[0])

    # Etapa 2 — geração real
    bar.progress(40, text=steps[1])
    tabelas = fn(n_linhas, data_inicio, data_fim)

    # Etapa 3 — anomalias / métricas
    bar.progress(70, text=steps[2])
    if anomalia:
        tabelas = _injetar_anomalias(tabelas)
    time.sleep(0.2)

    # Etapa 4 — compactação
    bar.progress(90, text=steps[3])
    time.sleep(0.2)

    bar.progress(100, text="✅ Concluído!" if lang == "pt" else "✅ Done!")
    time.sleep(0.4)
    bar.empty()
    status.empty()

    return tabelas


# ── Cache do preview ──────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _gerar_amostra(setor: str) -> dict:
    from datetime import date
    fn = SETORES[setor]
    return fn(_SAMPLE_SIZE, date(2023, 1, 1), date(2023, 12, 31))


# ── Preview dashboard ─────────────────────────────────────────────────────────

def _render_dashboard_preview(nome: str, setor: str) -> None:
    st.markdown(f"""
    <div style="
        background: linear-gradient(145deg, rgba(167,139,250,0.07) 0%, rgba(124,58,237,0.04) 100%);
        border: 1px solid rgba(167,139,250,0.2); border-radius: 14px;
        padding: 14px 20px; margin-bottom: 28px;
        display: flex; align-items: center; gap: 12px;
        font-size: 0.88rem; color: #c4b5fd;">
        <span style="font-size:1.2rem;">⚡</span>
        <span>{t("preview_banner")}</span>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner(t("spinner_preview", nome=nome)):
        tabelas = _gerar_amostra(setor)

    render_dashboard(nome, tabelas)


# ── Render resultado com dicionário ──────────────────────────────────────────

def _render_resultado_completo(nome: str, tabelas: dict, anomalia: bool) -> None:
    if anomalia:
        st.warning(_ANOMALY_BADGE[_get_lang()])

    render_resultado(nome, tabelas)

    # ── Dicionário de dados ────────────────────────────────────────────────
    st.markdown("---")
    lang = _get_lang()
    label = "📖 Dicionário de Dados Completo" if lang == "pt" else "📖 Data Dictionary"
    hint  = ("Baixe o dicionário Excel com descrição de cada tabela e coluna."
             if lang == "pt" else
             "Download the Excel dictionary with descriptions for each table and column.")

    st.markdown(f"**{label}** — {hint}")

    dict_bytes    = gerar_dicionario(nome, tabelas)
    dict_filename = f"Dicionario_{nome.replace(' ', '_')}.zip"

    st.download_button(
        label=f"📥 {dict_filename}",
        data=dict_bytes,
        file_name=dict_filename,
        mime="application/zip",
        use_container_width=True,
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    inject_css()
    inject_seo(lang=_get_lang())
    render_hero()

    setor, data_inicio, data_fim, n_linhas, gerar = render_sidebar()
    nome = setor.split(" ", 1)[1]

    # Toggle anomalia abaixo do hero
    lang    = _get_lang()
    anomalia = st.sidebar.toggle(
        _ANOMALY_LABEL[lang],
        value=False,
        help=_ANOMALY_HELP[lang],
    )

    if gerar:
        if data_fim <= data_inicio:
            st.error(t("date_error_stop"))
            st.stop()

        tabelas = _gerar_com_progresso(setor, n_linhas, data_inicio, data_fim, anomalia)

        tab_base, tab_dash = st.tabs([t("tab_data"), t("tab_dashboard")])

        with tab_base:
            _render_resultado_completo(nome, tabelas, anomalia)

        with tab_dash:
            render_dashboard(nome, tabelas)

    else:
        tab_inicio, tab_preview = st.tabs([
            t("tab_home"),
            t("tab_preview", nome=nome),
        ])

        with tab_inicio:
            render_estado_inicial()

        with tab_preview:
            _render_dashboard_preview(nome, setor)


if __name__ == "__main__":
    main()
