"""ui/sidebar.py: Sidebar completa com toggle de idioma, pesquisa e SQL DDL/INSERT."""

from datetime import date

import streamlit as st

from config import SETORES, SETORES_INFO, SLIDER_DEFAULT, SLIDER_MAX, SLIDER_MIN, SLIDER_STEP
from i18n import get_lang, set_lang, t

_LABEL_STYLE = (
    'font-family: Syne, sans-serif; font-size: 0.7rem; font-weight: 700;'
    ' letter-spacing: 2px; text-transform: uppercase; color: #4a5568;'
)

_SQL_STRINGS = {
    "title":    {"pt": "🗄️ Script SQL",            "en": "🗄️ SQL Script"},
    "hint":     {"pt": "Gera DDL, INSERT ou script completo para o setor selecionado.",
                 "en": "Generates DDL, INSERT or full script for the selected sector."},
    "help_detail": {
        "pt": (
            "📋 CREATE TABLE (DDL)\n"
            "Gera apenas a estrutura das tabelas: tipos de dados inferidos automaticamente, "
            "chaves primárias e índices sugeridos. Ideal para criar o banco do zero.\n\n"
            "💾 INSERT INTO (dados)\n"
            "Popula as tabelas com os dados gerados. Usa o volume definido no slider. "
            "Gera blocos de 500 linhas por INSERT.\n\n"
            "📦 Completo (DDL + INSERT)\n"
            "Combina os dois scripts num único arquivo. "
            "Cole no SSMS, DBeaver ou psql e execute para recriar o banco completo."
        ),
        "en": (
            "📋 CREATE TABLE (DDL)\n"
            "Generates table structure only: auto-inferred data types, "
            "primary keys and suggested indexes. Ideal to create the database from scratch.\n\n"
            "💾 INSERT INTO (data)\n"
            "Populates tables with generated data. Uses the volume set in the slider. "
            "Generates blocks of 500 rows per INSERT.\n\n"
            "📦 Full (DDL + INSERT)\n"
            "Combines both scripts into a single file. "
            "Paste into SSMS, DBeaver or psql and run to recreate the full database."
        ),
    },
    "dialect":  {"pt": "Dialeto",                  "en": "Dialect"},
    "tipo":     {"pt": "Tipo de script",           "en": "Script type"},
    "opt_ddl":  {"pt": "CREATE TABLE (DDL)",       "en": "CREATE TABLE (DDL)"},
    "opt_ins":  {"pt": "INSERT INTO (dados)",      "en": "INSERT INTO (data)"},
    "opt_full": {"pt": "Completo (DDL + INSERT)",  "en": "Full (DDL + INSERT)"},
    "btn":      {"pt": "⬇️ Gerar & Baixar SQL",   "en": "⬇️ Generate & Download SQL"},
    "spin":     {"pt": "Gerando script SQL…",      "en": "Generating SQL script…"},
    "preview":  {"pt": "👁️ Preview SQL",           "en": "👁️ SQL Preview"},
    "trunc":    {"pt": "-- ... (truncado, baixe o arquivo para o script completo)",
                 "en": "-- ... (truncated, download the file for the full script)"},
    "warn_ins": {"pt": "⚠️ INSERT usa o volume definido no slider acima.",
                 "en": "⚠️ INSERT uses the volume set in the slider above."},
}


def _build_index() -> dict[str, str]:
    index = {}
    for key in SETORES:
        nome_limpo = key.split(" ", 1)[-1].lower()
        desc = ""
        for _ico, nome_info, desc_info in SETORES_INFO:
            if nome_info.lower() in nome_limpo or nome_limpo in nome_info.lower():
                desc = desc_info.lower()
                break
        index[key] = f"{nome_limpo} {desc}"
    return index

_BUSCA_INDEX = _build_index()


def _filtrar_setores(query: str) -> list[str]:
    q = query.strip().lower()
    if not q:
        return list(SETORES.keys())
    return [k for k, texto in _BUSCA_INDEX.items() if q in texto]


def render_sidebar() -> tuple[str, date, date, int, bool]:
    with st.sidebar:

        # ── Logo ──────────────────────────────────────────────────────────
        st.markdown("""
        <div style="padding: 8px 0 16px;">
            <div style="font-family: Syne, sans-serif; font-size: 1.1rem; font-weight: 800;
                        color: #f0f4ff; margin-bottom: 4px;">BI Data Generator</div>
            <div style="font-family: Syne, sans-serif; font-size: 0.65rem; font-weight: 700;
                        letter-spacing: 3px; text-transform: uppercase; color: #a78bfa;
                        background: rgba(167,139,250,0.1); border: 1px solid rgba(167,139,250,0.25);
                        border-radius: 100px; padding: 3px 12px; display: inline-block;">PRO</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Toggle de idioma ───────────────────────────────────────────────
        if st.button(t("lang_toggle"), use_container_width=True):
            set_lang("en" if get_lang() == "pt" else "pt")
            st.rerun()

        st.markdown(
            '<div style="height:1px; background: rgba(167,139,250,0.15); margin: 16px 0;"></div>',
            unsafe_allow_html=True,
        )

        # ── Pesquisa ───────────────────────────────────────────────────────
        lang = get_lang()
        st.markdown(f'<p style="{_LABEL_STYLE} margin-bottom: 8px;">{t("search_label")}</p>', unsafe_allow_html=True)
        query = st.text_input(
            "",
            placeholder=t("search_placeholder"),
            label_visibility="collapsed",
            key="busca_setor",
        )

        setores_filtrados = _filtrar_setores(query)

        if query and not setores_filtrados:
            st.markdown(
                f'<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.25);'
                f'border-radius:10px;padding:8px 12px;font-size:0.78rem;color:#fca5a5;margin-bottom:10px;">'
                f'{t("search_empty")}</div>',
                unsafe_allow_html=True,
            )
            setores_filtrados = list(SETORES.keys())

        if query and setores_filtrados:
            st.markdown(
                f'<p style="font-size:0.72rem;color:#a78bfa;margin:-4px 0 8px;">'
                f'{t("search_found", n=len(setores_filtrados))}</p>',
                unsafe_allow_html=True,
            )

        # ── Setor ──────────────────────────────────────────────────────────
        st.markdown(f'<p style="{_LABEL_STYLE} margin-bottom: 10px;">{t("sector_label")}</p>', unsafe_allow_html=True)
        setor = st.selectbox("", setores_filtrados, label_visibility="collapsed")

        # ── Período ────────────────────────────────────────────────────────
        st.markdown(f'<p style="{_LABEL_STYLE} margin: 18px 0 10px;">{t("period_label")}</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input(t("start_label"), value=date(2023, 1, 1))
        with col2:
            data_fim = st.date_input(t("end_label"), value=date(2023, 12, 31))

        if data_fim <= data_inicio:
            st.markdown(
                f'<div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);'
                f'border-radius:10px;padding:10px 14px;font-size:0.8rem;color:#fca5a5;margin-top:8px;">'
                f'{t("date_error")}</div>',
                unsafe_allow_html=True,
            )

        # ── Volume ─────────────────────────────────────────────────────────
        st.markdown(f'<p style="{_LABEL_STYLE} margin: 18px 0 10px;">{t("volume_label")}</p>', unsafe_allow_html=True)
        n_linhas = st.slider("", min_value=SLIDER_MIN, max_value=SLIDER_MAX,
                             value=SLIDER_DEFAULT, step=SLIDER_STEP, label_visibility="collapsed")
        st.markdown(
            f'<p style="font-size:0.75rem;color:#7b8ba8;text-align:center;margin-top:-8px;">'
            f'{t("volume_hint", n=f"{n_linhas:,}")}</p>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div style="height:1px; background: rgba(167,139,250,0.15); margin: 20px 0;"></div>',
            unsafe_allow_html=True,
        )
        gerar = st.button(t("gerar_btn"), use_container_width=True, type="primary")

        # ── Script SQL ─────────────────────────────────────────────────────
        st.markdown(
            '<div style="height:1px; background: rgba(167,139,250,0.15); margin: 20px 0;"></div>',
            unsafe_allow_html=True,
        )

        def _s(key: str) -> str:
            return _SQL_STRINGS[key][lang]

        st.markdown(f'<p style="{_LABEL_STYLE} margin-bottom: 6px;">{_s("title")}</p>', unsafe_allow_html=True)
        sql_help_text = _s("help_detail").replace("\n", "<br>")
        st.markdown(
            f'''<div style="display:flex;align-items:flex-start;gap:4px;margin-bottom:12px;">
                <span style="font-size:0.72rem;color:#7b8ba8;line-height:1.4;">{_s("hint")}</span>
                <span style="position:relative;display:inline-block;cursor:pointer;"
                      class="sql-help-icon">
                  <span style="font-size:0.7rem;color:#7b8ba8;font-weight:600;
                               border:1px solid #7b8ba8;border-radius:50%;
                               width:14px;height:14px;display:inline-flex;
                               align-items:center;justify-content:center;
                               line-height:1;flex-shrink:0;">?</span>
                  <span style="visibility:hidden;opacity:0;transition:opacity 0.2s;
                               position:absolute;left:20px;top:-4px;z-index:9999;
                               background:#1e1b4b;border:1px solid rgba(167,139,250,0.3);
                               border-radius:8px;padding:10px 14px;
                               font-size:0.72rem;color:#c4b5fd;
                               width:220px;line-height:1.5;
                               white-space:pre-line;"
                        class="sql-tooltip">{sql_help_text}</span>
                </span>
            </div>
            <style>
            .sql-help-icon:hover .sql-tooltip {{
                visibility: visible !important;
                opacity: 1 !important;
            }}
            </style>''',
            unsafe_allow_html=True,
        )

        dialect_choice = st.selectbox(
            _s("dialect"),
            options=["SQL Server", "PostgreSQL", "MySQL"],
            key="sql_dialect",
        )
        script_type = st.selectbox(
            _s("tipo"),
            options=[_s("opt_ddl"), _s("opt_ins"), _s("opt_full")],
            key="sql_tipo",
        )

        dialect_map = {"SQL Server": "sqlserver", "PostgreSQL": "postgresql", "MySQL": "mysql"}
        dialect_key  = dialect_map[dialect_choice]

        if script_type in (_s("opt_ins"), _s("opt_full")):
            st.markdown(
                f'<p style="font-size:0.70rem;color:#f59e0b;margin:4px 0 8px;">{_s("warn_ins")}</p>',
                unsafe_allow_html=True,
            )

        if st.button(_s("btn"), use_container_width=True, key="btn_gerar_sql"):
            from generators.sql_generator import gerar_sql, gerar_sql_insert, gerar_sql_completo
            from log_acesso import registrar_evento

            fn          = SETORES[setor]
            nome_setor  = setor.split(" ", 1)[1]

            with st.spinner(_s("spin")):
                tabelas_sql = fn(n_linhas, data_inicio, data_fim)

                if script_type == _s("opt_ddl"):
                    sql_content = gerar_sql(nome_setor, tabelas_sql, dialect_key)
                    sufixo = "DDL"
                elif script_type == _s("opt_ins"):
                    sql_content = gerar_sql_insert(nome_setor, tabelas_sql, dialect_key)
                    sufixo = "INSERT"
                else:
                    sql_content = gerar_sql_completo(nome_setor, tabelas_sql, dialect_key)
                    sufixo = "COMPLETO"

            registrar_evento("gerou_sql", setor=nome_setor, volume=n_linhas)

            nome_limpo   = nome_setor.replace(" ", "_").replace("&", "e").replace("/", "_")
            nome_arquivo = f"{sufixo}_{nome_limpo}_{dialect_key}.sql"
            tamanho_kb   = len(sql_content.encode("utf-8")) / 1024

            st.download_button(
                label=f"📥 {nome_arquivo}  ({tamanho_kb:.0f} KB)",
                data=sql_content.encode("utf-8"),
                file_name=nome_arquivo,
                mime="text/plain",
                use_container_width=True,
                key="dl_sql_file",
                on_click=lambda: registrar_evento("baixou_sql", setor=nome_setor),
            )

            with st.expander(_s("preview"), expanded=True):
                preview = sql_content[:3_000]
                if len(sql_content) > 3_000:
                    preview += f"\n\n{_s('trunc')}"
                st.code(preview, language="sql")

    return setor, data_inicio, data_fim, n_linhas, gerar
