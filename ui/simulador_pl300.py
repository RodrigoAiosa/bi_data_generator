"""
styles.py: Paleta, tipografia e helpers visuais do Painel de Acesso.

Mesma identidade visual "documento/papel" usada no BI Data Generator:
fundo claro, tipografia serifada (Bitter) + monoespaçada (IBM Plex Mono),
paleta ink/verde/rust/dourado.
"""
import streamlit as st

PAPER_BODY = "#EEF0EA"
PAPER      = "#F8F9F4"
GRID       = "#D8DAD0"
TEXT       = "#6B6F66"
INK        = "#16233F"
GREEN      = "#1F6F54"
RUST       = "#A63D2F"
GOLD       = "#B8862E"
PALETTE    = [INK, GREEN, RUST, GOLD, "#223058", "#6E86A8", "#8A7F5E"]

FONT_DISPLAY = "Bitter, serif"
FONT_MONO    = "IBM Plex Mono, monospace"
FONT_BODY    = "Inter, sans-serif"

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
    7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

ACOES_LABEL = {
    "gerou_base": "Gerou base",
    "gerou_sql": "Gerou SQL",
    "baixou_zip": "Baixou ZIP",
    "baixou_dicionario": "Baixou dicionário",
    "baixou_sql": "Baixou SQL",
    "abriu_simulador_pl300": "Simulador PL-300",
}


def injetar_css() -> None:
    """Injeta o CSS customizado (lido de styles.css) na página."""
    with open(__file__.replace("styles.py", "styles.css"), encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def metric_html(label: str, value: str, sub: str = "", icon: str = "") -> str:
    """HTML de um card de KPI no formato 'selo/carimbo', com ícone e rótulo no topo esquerdo."""
    sub_html = f'<p class="kpi-sub">{sub}</p>' if sub else ""
    icon_html = f'<span class="kpi-icon">{icon}</span>' if icon else ""
    return (
        f'<div class="kpi-stamp">'
        f'<div class="kpi-header">{icon_html}<p class="kpi-label">{label}</p></div>'
        f'<p class="kpi-value">{value}</p>{sub_html}'
        f'</div>'
    )


def fmt_num(v, casas: int = 0) -> str:
    """Formata número no padrão brasileiro: ponto no milhar, vírgula no decimal."""
    s = f"{v:,.{casas}f}"
    return s.translate(str.maketrans({",": "\x00", ".": ","})).replace("\x00", ".")


def base_layout(fig, titulo: str = ""):
    """Aplica o tema visual padrão a uma figura Plotly."""
    fig.update_layout(
        height=340,
        paper_bgcolor=PAPER, plot_bgcolor=PAPER,
        font=dict(family=FONT_BODY, color=TEXT, size=12),
        title=dict(text=titulo, font=dict(color=INK, size=14, family=FONT_DISPLAY), x=0.01),
        margin=dict(l=10, r=10, t=40 if titulo else 10, b=10),
        colorway=PALETTE,
        separators=",.",
        legend=dict(font=dict(family=FONT_MONO, size=11, color="#000000")),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, title="", tickfont=dict(family=FONT_MONO, size=10, color="#000000"))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, title="", tickfont=dict(family=FONT_MONO, size=10, color="#000000"))
    return fig
