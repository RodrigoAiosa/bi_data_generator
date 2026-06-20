"""
i18n.py — Internacionalização da interface (PT / EN).

Uso:
    from i18n import t, get_lang
    st.button(t("gerar_btn"))
"""

import streamlit as st

# ── Textos da interface ───────────────────────────────────────────────────────

_STRINGS: dict[str, dict[str, str]] = {
    # Sidebar
    "lang_toggle":       {"pt": "🇺🇸 English", "en": "🇧🇷 Português"},
    "search_label":      {"pt": "Pesquisar setor", "en": "Search industry"},
    "search_placeholder":{"pt": "Ex: marketing, vendas, saúde…", "en": "e.g. marketing, sales, health…"},
    "search_found":      {"pt": "{n} setor(es) encontrado(s)", "en": "{n} industry(ies) found"},
    "search_empty":      {"pt": "🔍 Nenhum setor encontrado.", "en": "🔍 No industry found."},
    "sector_label":      {"pt": "Setor", "en": "Industry"},
    "period_label":      {"pt": "Período", "en": "Period"},
    "start_label":       {"pt": "Início", "en": "Start"},
    "end_label":         {"pt": "Fim", "en": "End"},
    "volume_label":      {"pt": "Volume de dados", "en": "Data volume"},
    "volume_hint":       {"pt": "{n} linhas na tabela fato", "en": "{n} rows in fact table"},
    "gerar_btn":         {"pt": "Gerar base agora", "en": "Generate dataset"},
    "date_error":        {"pt": "⚠ Data fim deve ser após a data início.", "en": "⚠ End date must be after start date."},

    # Hero
    "hero_badge":        {"pt": "Star Schema · {n} Setores · dCalendario", "en": "Star Schema · {n} Industries · Calendar Table"},
    "hero_title":        {"pt": "Dados reais para seu projeto de", "en": "Real data for your"},
    "hero_subtitle":     {"pt": "Gere bases profissionais no modelo estrela em segundos. Tabelas fato, dimensões e dCalendario prontos para Power BI, Tableau e qualquer ferramenta de BI.",
                          "en": "Generate professional star schema datasets in seconds. Fact tables, dimensions and a calendar table ready for Power BI, Tableau and any BI tool."},
    "hero_stat_sectors": {"pt": "Setores", "en": "Industries"},
    "hero_stat_rows":    {"pt": "Linhas máx.", "en": "Max rows"},
    "hero_stat_download":{"pt": "Download", "en": "Download"},
    "hero_stat_free":    {"pt": "Sem cadastro", "en": "No sign-up"},

    # Estado inicial
    "how_to_use":        {"pt": "Como usar", "en": "How to use"},
    "step1_title":       {"pt": "Escolha o setor", "en": "Choose an industry"},
    "step1_text":        {"pt": "Selecione entre {n} setores com dados contextualmente corretos", "en": "Pick from {n} industries with contextually accurate data"},
    "step2_title":       {"pt": "Defina o período", "en": "Set the period"},
    "step2_text":        {"pt": "Configure as datas — a dCalendario é gerada automaticamente", "en": "Set the dates — the calendar table is generated automatically"},
    "step3_title":       {"pt": "Clique em Gerar", "en": "Click Generate"},
    "step3_text":        {"pt": "A base completa é gerada em segundos com relações íntegras", "en": "The full dataset is generated in seconds with clean relationships"},
    "step4_title":       {"pt": "Baixe o .zip", "en": "Download the .zip"},
    "step4_text":        {"pt": "CSVs prontos para importar no Power BI, Tableau ou Python", "en": "CSVs ready to import into Power BI, Tableau or Python"},
    "sectors_available": {"pt": "Setores disponíveis", "en": "Available industries"},
    "star_schema_title": {"pt": "Estrutura Star Schema", "en": "Star Schema structure"},
    "star_schema_text":  {"pt": "Cada base inclui <strong>Tabela Fato</strong> com chaves estrangeiras (<code>id_*</code>) e métricas, <strong>Tabelas Dimensão</strong> com chaves primárias e atributos descritivos, e <strong>dCalendario</strong> com Data, Ano, Mês, MesAno e IdMesAno — compatível com Power Query. Tudo exportado em CSVs compactados em um único <code>.zip</code>.",
                          "en": "Each dataset includes a <strong>Fact Table</strong> with foreign keys (<code>id_*</code>) and metrics, <strong>Dimension Tables</strong> with primary keys and descriptive attributes, and a <strong>Calendar Table</strong> with Date, Year, Month, MonthYear and MonthYearId — Power Query compatible. Everything exported as CSVs in a single <code>.zip</code>."},

    # App / Tabs
    "tab_data":          {"pt": "📦 Base de Dados", "en": "📦 Dataset"},
    "tab_dashboard":     {"pt": "📊 Dashboard", "en": "📊 Dashboard"},
    "tab_home":          {"pt": "🏠 Início", "en": "🏠 Home"},
    "tab_preview":       {"pt": "📊 Dashboard — {nome}", "en": "📊 Dashboard — {nome}"},
    "preview_banner":    {"pt": "<strong style='color:#a78bfa;'>Preview automático</strong> — amostra de 2.000 linhas gerada para o setor selecionado. Para usar os dados reais configure os parâmetros e clique em <strong style='color:#a78bfa;'>Gerar base agora</strong>.",
                          "en": "<strong style='color:#a78bfa;'>Auto preview</strong> — 2,000-row sample generated for the selected industry. To use real data, set the parameters and click <strong style='color:#a78bfa;'>Generate dataset</strong>."},
    "spinner_preview":   {"pt": "Carregando preview de {nome}…", "en": "Loading preview for {nome}…"},
    "spinner_gerar":     {"pt": "Gerando base de dados…", "en": "Generating dataset…"},
    "date_error_stop":   {"pt": "Corrija as datas antes de gerar.", "en": "Fix the dates before generating."},
}

# ── Meses PT/EN para dCalendario ─────────────────────────────────────────────

MESES: dict[str, dict[int, str]] = {
    "pt": {1:"Jan",2:"Fev",3:"Mar",4:"Abr",5:"Mai",6:"Jun",
           7:"Jul",8:"Ago",9:"Set",10:"Out",11:"Nov",12:"Dez"},
    "en": {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
           7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"},
}

# ── Locale Faker por idioma ───────────────────────────────────────────────────

FAKER_LOCALE: dict[str, str] = {
    "pt": "pt_BR",
    "en": "en_US",
}


# ── API pública ───────────────────────────────────────────────────────────────

def get_lang() -> str:
    """Retorna 'pt' ou 'en' conforme seleção do usuário."""
    return st.session_state.get("lang", "pt")


def set_lang(lang: str) -> None:
    st.session_state["lang"] = lang


def t(key: str, **kwargs) -> str:
    """
    Retorna o texto traduzido para o idioma atual.

    Parâmetros de template são passados como kwargs:
        t("search_found", n=5)  →  "5 setor(es) encontrado(s)"
    """
    lang = get_lang()
    text = _STRINGS.get(key, {}).get(lang, _STRINGS.get(key, {}).get("pt", key))
    if kwargs:
        text = text.format(**kwargs)
    return text
