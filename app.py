"""
app.py: Entry point do BI Data Generator PRO.

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
from generators.case_negocio import gerar_case_negocio, detectar_kpi_label
from generators.concept_drift import injetar_concept_drift
from i18n import t
from styles.css import inject_css
try:
    from styles.seo import inject_seo
except Exception:
    def inject_seo(lang: str = "pt") -> None:
        pass  # seo.py não encontrado, SEO desabilitado
from ui import (
    render_estado_inicial,
    render_hero,
    render_resultado,
    render_sidebar,
)

st.set_page_config(**PAGE_CONFIG)

# ── Strings de anomalia e deriva temporal ────────────────────────────────────
_ANOMALY_LABEL = {"pt": "🧪 Injetar anomalias nos dados", "en": "🧪 Inject anomalies into data"}
_ANOMALY_HELP  = {
    "pt": "Adiciona problemas reais: spike de churn, produto com margem negativa, sazonalidade extrema e outliers de valor. Ideal para praticar análise de causa raiz.",
    "en": "Adds real-world issues: churn spike, negative-margin product, extreme seasonality and value outliers. Great for practicing root-cause analysis.",
}
_ANOMALY_BADGE = {
    "pt": "⚠️ **Modo anomalia ativo**: dados contém problemas intencionais para análise de causa raiz.",
    "en": "⚠️ **Anomaly mode active**: data contains intentional issues for root-cause analysis.",
}
_DRIFT_LABEL = {"pt": "🧬 Simular deriva temporal (concept drift)", "en": "🧬 Simulate temporal drift (concept drift)"}
_DRIFT_HELP  = {
    "pt": "Faz uma categoria ganhar participação aos poucos ao longo do período, sem evento único que explique. Ideal para praticar detecção de tendência/mudança de comportamento.",
    "en": "Gradually shifts a category's share over the period, with no single event to explain it. Great for practicing trend and behavior-change detection.",
}
_DRIFT_BADGE = {
    "pt": "🧬 **Deriva temporal ativa**: a participação de uma categoria muda gradualmente ao longo do período.",
    "en": "🧬 **Temporal drift active**: one category's share shifts gradually over the period.",
}
_GABARITO_TITULO = {
    "pt": "🔍 Ver gabarito (spoiler: revela onde estão as anomalias/deriva)",
    "en": "🔍 View answer key (spoiler: reveals where the anomalies/drift are)",
}
_CASE_TITULO = {"pt": "📖 Seu case de negócio", "en": "📖 Your business case"}

# ── Passos da barra de progresso ─────────────────────────────────────────────
_STEPS_PT = ["Criando dimensões…", "Gerando tabela fato…", "Calculando métricas…", "Compactando ZIP…"]
_STEPS_EN = ["Building dimensions…", "Generating fact table…", "Computing metrics…", "Compressing ZIP…"]


def _get_lang() -> str:
    from i18n import get_lang
    return get_lang()


def _fmt_num_br(v, decimals=2):
    """Formata número no padrão brasileiro: ponto como milhar, vírgula como decimal."""
    s = f"{v:,.{decimals}f}"
    return s.translate(str.maketrans({",": "\x00", ".": ","})).replace("\x00", ".")


# ── Injeção de anomalias ─────────────────────────────────────────────────────

def _injetar_anomalias(tabelas: dict[str, pd.DataFrame]) -> tuple[dict[str, pd.DataFrame], list[dict]]:
    """
    Injeta 4 tipos de anomalias nos dados para prática de análise de causa raiz:
      1. Spike de churn / cancelamentos em um mês aleatório
      2. Produto / item com margem negativa
      3. Sazonalidade extrema (queda abrupta num trimestre)
      4. Outliers de valor (registros com valores 10 a 30x acima da média)

    Retorna as tabelas modificadas e o gabarito: uma lista com o que foi
    alterado exatamente, para quem ensina conferir se a análise do aluno
    encontrou o problema certo.
    """
    tabelas = {k: v.copy() for k, v in tabelas.items()}
    gabarito: list[dict] = []

    fato_key = next((k for k in tabelas if k.startswith("Fato")), None)
    if fato_key is None:
        return tabelas, gabarito

    fato = tabelas[fato_key]
    num_cols = fato.select_dtypes(include="number").columns.tolist()
    date_cols = [c for c in fato.columns if "data" in c.lower() or "date" in c.lower()]
    bool_cols = [c for c in fato.columns if fato[c].dtype == bool]
    val_col   = next((c for c in num_cols if any(k in c for k in ["valor","receita","preco","total","mrr"])), num_cols[0] if num_cols else None)

    # Garante dtype float na coluna de valor: evita erro do pandas ao atribuir
    # multiplicadores fracionários (sazonalidade/outliers) numa coluna int64.
    if val_col is not None and pd.api.types.is_integer_dtype(fato[val_col]):
        fato[val_col] = fato[val_col].astype(float)

    # 1. Spike de churn / cancelamentos num mês aleatório
    if bool_cols and date_cols:
        try:
            date_col = date_cols[0]
            fato[date_col] = pd.to_datetime(fato[date_col], errors="coerce")
            meses = fato[date_col].dt.month.dropna().unique()
            mes_spike = random.choice(list(meses))
            mask = fato[date_col].dt.month == mes_spike
            fato.loc[mask, bool_cols[0]] = True   # força cancelamento/churn no mês
            gabarito.append({
                "tipo": "Spike de Cancelamento/Churn",
                "localizacao": f"Mês {int(mes_spike)} (coluna '{bool_cols[0]}', tabela {fato_key})",
                "detalhe": f"Todos os registros de {fato_key} no mês {int(mes_spike)} tiveram '{bool_cols[0]}' forçado para True. {int(mask.sum())} linhas afetadas.",
            })
        except Exception:
            pass

    # 2. Produto / categoria com margem negativa
    margem_cols = [c for c in num_cols if "margem" in c or "lucro" in c or "desconto" in c]
    if margem_cols:
        if pd.api.types.is_integer_dtype(fato[margem_cols[0]]):
            fato[margem_cols[0]] = fato[margem_cols[0]].astype(float)
        n_neg = max(1, int(len(fato) * 0.04))
        idx = fato.sample(n_neg).index
        media_original = fato[margem_cols[0]].mean()
        fato.loc[idx, margem_cols[0]] = -abs(media_original) * np.random.uniform(1.1, 2.5, n_neg)
        gabarito.append({
            "tipo": "Margem/Lucro Negativo Artificial",
            "localizacao": f"{n_neg} registros aleatórios (coluna '{margem_cols[0]}', tabela {fato_key})",
            "detalhe": f"Valores de '{margem_cols[0]}' foram forçados para negativo (entre 1,1x e 2,5x a média original, em módulo). Média original antes da alteração: {_fmt_num_br(media_original)}.",
        })

    # 3. Sazonalidade extrema: queda de 70% num trimestre aleatório
    if val_col and date_cols:
        try:
            date_col = date_cols[0]
            trimestres = fato[date_col].dt.quarter.dropna().unique()
            trim_queda = random.choice(list(trimestres))
            mask = fato[date_col].dt.quarter == trim_queda
            fato.loc[mask, val_col] = fato.loc[mask, val_col] * 0.30
            gabarito.append({
                "tipo": "Queda Artificial de Sazonalidade",
                "localizacao": f"Trimestre Q{int(trim_queda)} (coluna '{val_col}', tabela {fato_key})",
                "detalhe": f"Valores de '{val_col}' no Q{int(trim_queda)} foram reduzidos para 30% do valor original (queda de 70%). {int(mask.sum())} linhas afetadas.",
            })
        except Exception:
            pass

    # 4. Outliers de valor (1% dos registros com valores extremos)
    if val_col:
        n_out = max(1, int(len(fato) * 0.01))
        idx = fato.sample(n_out).index
        media = fato[val_col].mean()
        fato.loc[idx, val_col] = media * np.random.uniform(10, 30, n_out)
        gabarito.append({
            "tipo": "Outliers de Valor",
            "localizacao": f"{n_out} registros aleatórios (coluna '{val_col}', tabela {fato_key})",
            "detalhe": f"Valores foram multiplicados por um fator entre 10x e 30x a média. Média original antes da alteração: {_fmt_num_br(media)}.",
        })

    tabelas[fato_key] = fato
    return tabelas, gabarito


# ── Barra de progresso ────────────────────────────────────────────────────────

def _gerar_com_progresso(setor: str, n_linhas: int, data_inicio, data_fim, anomalia: bool, drift: bool) -> tuple[dict, list[dict]]:
    """Gera os dados exibindo barra de progresso com etapas reais. Retorna (tabelas, gabarito)."""
    lang   = _get_lang()
    steps  = _STEPS_EN if lang == "en" else _STEPS_PT
    fn     = SETORES[setor]

    bar    = st.progress(0, text=steps[0])
    status = st.empty()

    # Etapa 1: dimensões (simulada antes da geração)
    time.sleep(0.3)
    bar.progress(20, text=steps[0])

    # Etapa 2: geração real
    bar.progress(40, text=steps[1])
    tabelas = fn(n_linhas, data_inicio, data_fim)

    # Etapa 3: anomalias / deriva temporal / métricas
    bar.progress(70, text=steps[2])
    gabarito: list[dict] = []
    if anomalia:
        tabelas, gab_anomalia = _injetar_anomalias(tabelas)
        gabarito.extend(gab_anomalia)
    if drift:
        tabelas, gab_drift = injetar_concept_drift(tabelas)
        gabarito.extend(gab_drift)
    time.sleep(0.2)

    # Etapa 4: compactação
    bar.progress(90, text=steps[3])
    time.sleep(0.2)

    bar.progress(100, text="✅ Concluído!" if lang == "pt" else "✅ Done!")
    time.sleep(0.4)
    bar.empty()
    status.empty()

    return tabelas, gabarito


# ── Formatação do gabarito em texto ──────────────────────────────────────────

def _formatar_gabarito(gabarito: list[dict], lang: str) -> str:
    if not gabarito:
        return ""
    titulo = "GABARITO: Anomalias e Deriva Temporal Injetadas" if lang == "pt" else "ANSWER KEY: Injected Anomalies and Concept Drift"
    linhas = [titulo, "=" * len(titulo), ""]
    for i, item in enumerate(gabarito, 1):
        linhas.append(f"{i}. {item['tipo']}")
        linhas.append(f"   {'Localização' if lang == 'pt' else 'Location'}: {item['localizacao']}")
        linhas.append(f"   {'Detalhe' if lang == 'pt' else 'Detail'}: {item['detalhe']}")
        linhas.append("")
    return "\n".join(linhas)


# ── Render resultado com dicionário ──────────────────────────────────────────

def _render_resultado_completo(nome: str, tabelas: dict, anomalia: bool, drift: bool, gabarito: list[dict]) -> None:
    lang = _get_lang()

    if anomalia:
        st.warning(_ANOMALY_BADGE[lang])
    if drift:
        st.warning(_DRIFT_BADGE[lang])

    # ── Case de negócio ─────────────────────────────────────────────────────
    kpi_label = detectar_kpi_label(tabelas)
    case_texto = gerar_case_negocio(nome, kpi_label, lang=lang, anomalia_ativa=anomalia, drift_ativo=drift)
    st.markdown(f'<h3 class="section-header-plain">{_CASE_TITULO[lang]}</h3>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-box">{case_texto}</div>', unsafe_allow_html=True)

    extra_files = {"case_negocio.txt": case_texto}
    gabarito_texto = _formatar_gabarito(gabarito, lang)
    if gabarito_texto:
        extra_files["gabarito.txt"] = gabarito_texto

    render_resultado(nome, tabelas, extra_files=extra_files)

    # ── Gabarito (spoiler, só aparece se houver anomalia/drift ativos) ──────
    if gabarito:
        with st.expander(_GABARITO_TITULO[lang], expanded=False):
            for i, item in enumerate(gabarito, 1):
                st.markdown(f"**{i}. {item['tipo']}**")
                st.caption(f"{'Localização' if lang == 'pt' else 'Location'}: {item['localizacao']}")
                st.markdown(item["detalhe"])
                st.divider()

    # ── Dicionário de dados ──────────────────────────────────────────────────
    st.markdown("---")
    label = "📖Dicionário de Dados" if lang == "pt" else "📖 Data Dictionary"
    hint  = ("Baixe o dicionário Excel com descrição de cada tabela e coluna."
             if lang == "pt" else
             "Download the Excel dictionary with descriptions for each table and column.")

    st.markdown(f"**{label}**: {hint}")

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

    # Toggles de anomalia e deriva temporal, abaixo do hero
    lang    = _get_lang()
    anomalia = st.sidebar.toggle(
        _ANOMALY_LABEL[lang],
        value=False,
        help=_ANOMALY_HELP[lang],
    )
    drift = st.sidebar.toggle(
        _DRIFT_LABEL[lang],
        value=False,
        help=_DRIFT_HELP[lang],
    )

    if gerar:
        if data_fim <= data_inicio:
            st.error(t("date_error_stop"))
            st.stop()

        tabelas, gabarito = _gerar_com_progresso(setor, n_linhas, data_inicio, data_fim, anomalia, drift)
        _render_resultado_completo(nome, tabelas, anomalia, drift, gabarito)

    else:
        render_estado_inicial()


if __name__ == "__main__":
    main()
