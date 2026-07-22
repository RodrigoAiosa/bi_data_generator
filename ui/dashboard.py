"""
ui/dashboard.py
Dashboard com KPIs e gráficos interativos por setor — com suporte a i18n.
Estilo visual: "documento/papel" (fundo claro, tipografia serifada Bitter +
IBM Plex Mono, paleta ink/green/rust/gold), aplicado via styles/css.py
dentro do container st.container(key="dash_paper").
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from i18n import td, resolve_sector_name

_PAPER_BODY = "#EEF0EA"
_PAPER      = "#F8F9F4"
_GRID       = "#D8DAD0"
_TEXT       = "#6B6F66"
_INK        = "#16233F"
_GREEN      = "#1F6F54"
_RUST       = "#A63D2F"
_GOLD       = "#B8862E"
_ACCENT     = _INK
_PALETTE    = [_INK, _GREEN, _RUST, _GOLD, "#223058", "#6E86A8", "#8A7F5E"]
_FONT_DISPLAY = "Bitter, serif"
_FONT_MONO    = "IBM Plex Mono, monospace"
_FONT_BODY    = "Inter, sans-serif"


def _fmt_num(v, decimals=0):
    """
    Formata um número no padrão brasileiro: ponto como separador de milhar,
    vírgula como separador decimal (ex.: 36.331.804,47).
    """
    try:
        decimals = int(decimals)
    except (TypeError, ValueError):
        decimals = 0
    s = f"{v:,.{decimals}f}"
    return s.translate(str.maketrans({",": "\x00", ".": ","})).replace("\x00", ".")


def _detectar_col_data(df: pd.DataFrame):
    """Acha a coluna de data mais provável de uma tabela fato (id_data, sk_data, data_x, x_data...)."""
    candidatos = [c for c in df.columns if "data" in c.lower()]
    if not candidatos:
        return None
    prioritarios = [c for c in candidatos if c.lower() in ("id_data", "sk_data")]
    return prioritarios[0] if prioritarios else candidatos[0]


def _filtro_ano(tabelas: dict) -> dict:
    """
    Mostra (se aplicável) um filtro de ano no topo do dashboard e retorna uma
    cópia de `tabelas` com as tabelas fato filtradas para o ano escolhido.

    Não aparece filtro nenhum se:
    - nenhuma tabela fato tiver coluna de data reconhecível, ou
    - só existir 1 ano de dados no período gerado.
    """
    from i18n import get_lang
    lang = get_lang()

    fato_keys = [k for k in tabelas if k.startswith("Fato")]
    cols_data = {}
    anos = set()
    for k in fato_keys:
        col = _detectar_col_data(tabelas[k])
        if col is not None and len(tabelas[k]):
            cols_data[k] = col
            anos |= set(pd.to_datetime(tabelas[k][col]).dt.year.tolist())

    if not cols_data or len(anos) <= 1:
        return tabelas

    anos_ordenados = sorted(anos)
    label = "Ano" if lang == "pt" else "Year"
    todos = "Todos os anos" if lang == "pt" else "All years"
    opcoes = [todos] + [str(a) for a in anos_ordenados]

    col_filtro, _ = st.columns([1, 3])
    with col_filtro:
        escolha = st.selectbox(label, opcoes, key="dash_filtro_ano")

    if escolha == todos:
        return tabelas

    ano_sel = int(escolha)
    filtradas = dict(tabelas)
    for k, col in cols_data.items():
        df = filtradas[k]
        filtradas[k] = df[pd.to_datetime(df[col]).dt.year == ano_sel].reset_index(drop=True)
    return filtradas


def _base_layout(fig, title=""):
    fig.update_layout(
        paper_bgcolor=_PAPER, plot_bgcolor=_PAPER,
        font=dict(family=_FONT_BODY, color=_TEXT, size=12),
        title=dict(text=title, font=dict(color=_INK, size=15, family=_FONT_DISPLAY), x=0.01),
        margin=dict(l=16, r=16, t=44 if title else 16, b=16),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=_TEXT, family=_FONT_MONO, size=11)),
        colorway=_PALETTE,
        separators=",.",  # "," decimal · "." milhar — padrão brasileiro em eixos e hover
    )
    fig.update_xaxes(gridcolor=_GRID, zeroline=False, tickfont=dict(color=_TEXT, family=_FONT_MONO, size=10))
    fig.update_yaxes(gridcolor=_GRID, zeroline=False, tickfont=dict(color=_TEXT, family=_FONT_MONO, size=10))
    return fig


def _metric(label, value, sub="", delta=""):
    delta_html = f'<span class="kpi-delta">▲ {delta}</span>' if delta else ""
    sub_html   = f'<p class="kpi-sub">{sub}</p>' if sub else ""
    return f'<div class="kpi-stamp"><p class="kpi-label">{label}</p><p class="kpi-value">{value}</p>{sub_html}{delta_html}</div>'


def _kpi_row(metrics):
    cols = st.columns(len(metrics))
    for col, args in zip(cols, metrics):
        with col:
            st.markdown(_metric(*args), unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:28px'></div>", unsafe_allow_html=True)


def _chart_row(figs):
    cols = st.columns([w for _, w in figs])
    for col, (fig, _) in zip(cols, figs):
        with col:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _section(key):
    st.markdown(f'<h3 class="section-header">{td(key)}</h3>', unsafe_allow_html=True)


def _dashboard_header(nome_setor: str, tabelas: dict) -> None:
    """Cabeçalho estilo 'relatório impresso' no topo da aba Dashboard."""
    from i18n import get_lang
    lang = get_lang()
    fato_key = next((k for k in tabelas if k.startswith("Fato")), None)
    n = len(tabelas[fato_key]) if fato_key else 0
    eyebrow = "Relatório de Business Intelligence · Dados Sintéticos" if lang == "pt" \
        else "Business Intelligence Report · Synthetic Data"
    meta = f"{_fmt_num(n, 0)} registros na tabela fato · Base gerada para fins de estudo" if lang == "pt" \
        else f"{_fmt_num(n, 0)} records in fact table · Data generated for study purposes"
    stamp = "gerado" if lang == "pt" else "generated"
    st.markdown(f"""
<div class="dash-header">
    <div class="dash-stamp">&#10003; {stamp}</div>
    <p class="dash-eyebrow">{eyebrow}</p>
    <h1 class="dash-title">{nome_setor}</h1>
    <p class="dash-meta">{meta}</p>
</div>
<div class="dash-tear"></div>
""", unsafe_allow_html=True)


def _by_month(df, date_col, val_col):
    d = df.copy()
    d["_m"] = pd.to_datetime(d[date_col]).dt.to_period("M").astype(str)
    return d.groupby("_m")[val_col].sum().reset_index().rename(columns={"_m": "mes"})


def _fmt_pct_delta(v):
    return f"{v:+.1f}%" if pd.notna(v) else "—"


def _monthly_chart(df, date_col, val_col, title, y_label, agg="sum"):
    """
    Gráfico de evolução mensal do indicador principal de qualquer setor, com
    %MoM (mês vs. mês anterior) e %YoY (mês vs. mesmo mês do ano anterior)
    disponíveis no hover de cada ponto, e a variação do último mês exibida
    como selo no canto superior do gráfico. Funciona para os 70 setores.
    """
    d = df.copy()
    d["_m"] = pd.to_datetime(d[date_col]).dt.to_period("M").astype(str)
    grp = d.groupby("_m")[val_col]
    by_mes = (grp.mean() if agg == "mean" else grp.sum()).reset_index().rename(columns={"_m": "mes"})
    by_mes = by_mes.sort_values("mes").reset_index(drop=True)

    by_mes["_mom"] = by_mes[val_col].pct_change() * 100
    by_mes["_yoy"] = by_mes[val_col].pct_change(periods=12) * 100
    by_mes["_mom_fmt"] = by_mes["_mom"].apply(_fmt_pct_delta)
    by_mes["_yoy_fmt"] = by_mes["_yoy"].apply(_fmt_pct_delta)

    fig = px.area(by_mes, x="mes", y=val_col, labels={"mes": "", val_col: y_label})
    fig.update_traces(
        line_color=_ACCENT, fillcolor="rgba(22,35,63,0.08)",
        customdata=by_mes[["_mom_fmt", "_yoy_fmt"]].to_numpy(),
        hovertemplate="%{x}<br>" + y_label + ": %{y:,.2f}"
                      "<br>MoM: %{customdata[0]}<br>YoY: %{customdata[1]}<extra></extra>",
    )
    _base_layout(fig, title)

    partes = []
    if len(by_mes) > 1 and pd.notna(by_mes["_mom"].iloc[-1]):
        v = by_mes["_mom"].iloc[-1]
        cor = _GREEN if v >= 0 else _RUST
        partes.append(f"<span style='color:{cor}'>{'▲' if v >= 0 else '▼'} {v:+.1f}% MoM</span>")
    if len(by_mes) > 12 and pd.notna(by_mes["_yoy"].iloc[-1]):
        v = by_mes["_yoy"].iloc[-1]
        cor = _GREEN if v >= 0 else _RUST
        partes.append(f"<span style='color:{cor}'>{'▲' if v >= 0 else '▼'} {v:+.1f}% YoY</span>")
    if partes:
        fig.add_annotation(
            xref="paper", yref="paper", x=1, y=1.16, showarrow=False, align="right",
            font=dict(size=11, family=_FONT_MONO), text="   ".join(partes),
        )
    return fig


# ── 🛒 VAREJO ─────────────────────────────────────────────────────────────────
def _dash_varejo(tabelas):
    fato = tabelas["FatoVendas"]; produto = tabelas["DimProduto"]; vendedor = tabelas["DimVendedor"]
    receita = fato["valor_total"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"), f"R$ {_fmt_num(receita, 0)}",               f"{_fmt_num(n, 0)} {td('sales')}"),
        (td("avg_ticket"),    f"R$ {_fmt_num(fato['valor_total'].mean(), 2)}", td("per_sale")),
        (td("avg_discount"),  f"{fato['desconto'].mean()*100:.1f}%",   td("on_full_price")),
        (td("avg_qty"),       f"{fato['quantidade'].mean():.1f}",       td("units")),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "valor_total", td("monthly_revenue"), "valor_total")

    merged = fato.merge(produto[["id_produto","categoria"]], on="id_produto")
    by_cat = merged.groupby("categoria")["valor_total"].sum().reset_index().sort_values("valor_total")
    fig_cat = px.bar(by_cat, x="valor_total", y="categoria", orientation="h",
                     labels={"valor_total":td("revenue_brl"),"categoria":""})
    fig_cat.update_traces(marker_color=_ACCENT)
    _base_layout(fig_cat, td("revenue_by_category"))

    _section("channels")
    _chart_row([(fig_mes,3),(fig_cat,2)])

    by_canal = fato.groupby("canal")["valor_total"].sum().reset_index()
    fig_canal = px.pie(by_canal, names="canal", values="valor_total", hole=0.55, color_discrete_sequence=_PALETTE)
    fig_canal.update_traces(textfont_color=_INK)
    _base_layout(fig_canal, td("revenue_by_channel"))

    top_v = (fato.groupby("id_vendedor")["valor_total"].sum().reset_index()
             .sort_values("valor_total",ascending=False).head(10)
             .merge(vendedor[["id_vendedor","nome"]], on="id_vendedor"))
    fig_vend = px.bar(top_v, x="valor_total", y="nome", orientation="h",
                      labels={"valor_total":td("revenue_brl"),"nome":""},
                      color="valor_total", color_continuous_scale=["#16233F","#A63D2F","#B8862E"])
    fig_vend.update_layout(coloraxis_showscale=False)
    _base_layout(fig_vend, td("top10_sellers"))
    _chart_row([(fig_canal,1),(fig_vend,2)])


# ── 💰 FINANCEIRO ─────────────────────────────────────────────────────────────
def _dash_financeiro(tabelas):
    fato = tabelas["FatoTransacao"]; produto = tabelas["DimProduto"]
    vol = fato["valor"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_volume"),   f"R$ {_fmt_num(vol, 0)}",                      f"{_fmt_num(n, 0)} {td('transactions')}"),
        (td("approval_rate"),  f"{(fato['status']=='Aprovada').mean()*100:.1f}%", td("approved_tx")),
        (td("avg_value"),      f"R$ {_fmt_num(fato['valor'].mean(), 2)}",      td("per_tx")),
        (td("avg_balance"),    f"R$ {_fmt_num(fato['saldo_apos'].mean(), 0)}", td("after_tx")),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "valor", td("monthly_volume"), "valor")

    by_tipo = fato.groupby("tipo")["valor"].sum().reset_index().sort_values("valor")
    fig_tipo = px.bar(by_tipo, x="valor", y="tipo", orientation="h",
                      labels={"valor":td("volume_brl"),"tipo":""},
                      color="valor", color_continuous_scale=["#16233F","#B8862E"])
    fig_tipo.update_layout(coloraxis_showscale=False)
    _base_layout(fig_tipo, td("volume_by_type"))

    _section("distribution")
    _chart_row([(fig_mes,3),(fig_tipo,2)])

    by_status = fato["status"].value_counts().reset_index()
    fig_status = px.pie(by_status, names="status", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
    fig_status.update_traces(textfont_color=_INK)
    _base_layout(fig_status, td("status_dist"))

    merged = fato.merge(produto[["id_produto","categoria"]], on="id_produto")
    by_cat = merged.groupby("categoria")["valor"].sum().reset_index().sort_values("valor",ascending=False)
    fig_cat = px.bar(by_cat, x="categoria", y="valor",
                     labels={"valor":td("volume_brl"),"categoria":""},
                     color="valor", color_continuous_scale=["#16233F","#A63D2F","#B8862E"])
    fig_cat.update_layout(coloraxis_showscale=False)
    _base_layout(fig_cat, td("volume_by_product"))
    _chart_row([(fig_status,1),(fig_cat,2)])


# ── 🏥 SAÚDE ──────────────────────────────────────────────────────────────────
def _dash_saude(tabelas):
    fato = tabelas["FatoAtendimento"]; medico = tabelas["DimMedico"]; paciente = tabelas["DimPaciente"]
    receita = fato["valor_cobrado"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),  f"R$ {_fmt_num(receita, 0)}",                     f"{_fmt_num(n, 0)} {td('visits')}"),
        (td("discharge_rate"), f"{(fato['resultado']=='Alta').mean()*100:.1f}%", td("of_visits")),
        (td("avg_duration"),   f"{fato['duracao_min'].mean():.0f} min",   td("per_visit")),
        (td("avg_value"),      f"R$ {_fmt_num(fato['valor_cobrado'].mean(), 2)}", td("per_visit")),
    ])
    fato_cnt = fato.copy(); fato_cnt["_contagem"] = 1
    fig_mes = _monthly_chart(fato_cnt, "id_data", "_contagem", td("monthly_visits"), td("visits_axis"))

    merged = fato.merge(medico[["id_medico","especialidade"]], on="id_medico")
    by_esp = merged.groupby("especialidade").size().reset_index(name="count").sort_values("count")
    fig_esp = px.bar(by_esp, x="count", y="especialidade", orientation="h",
                     labels={"count":td("visits_axis"),"especialidade":td("specialty")},
                     color="count", color_continuous_scale=["#16233F","#B8862E"])
    fig_esp.update_layout(coloraxis_showscale=False)
    _base_layout(fig_esp, td("visits_by_specialty"))

    _section("results")
    _chart_row([(fig_mes,3),(fig_esp,2)])

    by_res = fato["resultado"].value_counts().reset_index()
    fig_res = px.pie(by_res, names="resultado", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
    fig_res.update_traces(textfont_color=_INK)
    _base_layout(fig_res, td("result_dist"))

    m2 = fato.merge(paciente[["id_paciente","convenio"]], on="id_paciente")
    by_conv = m2.groupby("convenio")["valor_cobrado"].sum().reset_index().sort_values("valor_cobrado",ascending=False)
    fig_conv = px.bar(by_conv, x="convenio", y="valor_cobrado",
                      labels={"valor_cobrado":td("revenue_brl"),"convenio":""},
                      color="valor_cobrado", color_continuous_scale=["#16233F","#A63D2F","#B8862E"])
    fig_conv.update_layout(coloraxis_showscale=False)
    _base_layout(fig_conv, td("revenue_by_plan"))
    _chart_row([(fig_res,1),(fig_conv,2)])


# ── 💻 TECNOLOGIA ─────────────────────────────────────────────────────────────
def _dash_tecnologia(tabelas):
    fato = tabelas["FatoContrato"]; cliente = tabelas["DimCliente"]
    _section("overview")
    _kpi_row([
        (td("total_mrr"),   f"R$ {_fmt_num(fato['valor_mrr'].sum(), 0)}",  f"{_fmt_num(len(fato), 0)} {td('contracts')}"),
        (td("total_arr"),   f"R$ {_fmt_num(fato['arr'].sum(), 0)}",         td("arr_sub")),
        (td("avg_nps"),     f"{fato['nps'].mean():.1f}",             td("nps_scale")),
        (td("churn_rate"),  f"{(fato['tipo']=='Churn').mean()*100:.1f}%", td("of_contracts")),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "valor_mrr", td("mrr_by_month"), "valor_mrr")

    by_tipo = fato["tipo"].value_counts().reset_index()
    fig_tipo = px.pie(by_tipo, names="tipo", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
    fig_tipo.update_traces(textfont_color=_INK)
    _base_layout(fig_tipo, td("contracts_by_type"))

    _section("segmentation")
    _chart_row([(fig_mes,3),(fig_tipo,2)])

    nps_d = fato["nps"].value_counts().sort_index().reset_index()
    colors = ["#ef4444" if v<=6 else "#f59e0b" if v<=8 else "#4ade80" for v in nps_d["nps"]]
    fig_nps = go.Figure(go.Bar(x=nps_d["nps"].astype(str), y=nps_d["count"], marker_color=colors))
    _base_layout(fig_nps, td("nps_dist"))
    fig_nps.update_xaxes(title_text=td("score"))
    fig_nps.update_yaxes(title_text=td("contracts_axis"))

    merged = fato.merge(cliente[["id_cliente","setor"]], on="id_cliente")
    by_seg = merged.groupby("setor")["valor_mrr"].sum().reset_index().sort_values("valor_mrr",ascending=False)
    fig_seg = px.bar(by_seg, x="setor", y="valor_mrr",
                     labels={"valor_mrr":"MRR (R$)","setor":""},
                     color="valor_mrr", color_continuous_scale=["#16233F","#A63D2F","#B8862E"])
    fig_seg.update_layout(coloraxis_showscale=False)
    _base_layout(fig_seg, td("mrr_by_segment"))
    _chart_row([(fig_nps,2),(fig_seg,3)])


# ── 📚 EDUCAÇÃO ───────────────────────────────────────────────────────────────
def _dash_educacao(tabelas):
    fato = tabelas["FatoMatricula"]; curso = tabelas["DimCurso"]
    _section("overview")
    _kpi_row([
        (td("total_revenue"),    f"R$ {_fmt_num(fato['valor_pago'].sum(), 0)}",    f"{_fmt_num(len(fato), 0)} {td('enrollments')}"),
        (td("completion_rate"),  f"{fato['concluiu'].mean()*100:.1f}%",     td("of_students")),
        (td("avg_grade"),        f"{fato['nota_final'].mean():.2f}",         td("nps_scale")),
        (td("avg_ticket"),       f"R$ {_fmt_num(fato['valor_pago'].mean(), 2)}",    td("per_enrollment")),
    ])
    fato2 = fato.copy(); fato2["mes"] = pd.to_datetime(fato2["id_data"]).dt.to_period("M").astype(str)
    cnt = fato2.groupby("mes").size().reset_index(name="count")
    fig_mes = px.area(cnt, x="mes", y="count", labels={"mes":"","count":td("enrollments_axis")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_enrollments"))

    m1 = fato.merge(curso[["id_curso","modalidade"]], on="id_curso")
    by_mod = m1.groupby("modalidade").size().reset_index(name="count")
    fig_mod = px.pie(by_mod, names="modalidade", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
    fig_mod.update_traces(textfont_color=_INK)
    _base_layout(fig_mod, td("by_modality"))

    _section("area_performance")
    _chart_row([(fig_mes,3),(fig_mod,2)])

    m2 = fato.merge(curso[["id_curso","area"]], on="id_curso")
    by_area = m2.groupby("area")["valor_pago"].sum().reset_index().sort_values("valor_pago")
    fig_area = px.bar(by_area, x="valor_pago", y="area", orientation="h",
                      labels={"valor_pago":td("revenue_brl"),"area":td("area")},
                      color="valor_pago", color_continuous_scale=["#16233F","#B8862E"])
    fig_area.update_layout(coloraxis_showscale=False)
    _base_layout(fig_area, td("revenue_by_area"))

    fig_notas = px.histogram(fato, x="nota_final", nbins=20,
                             labels={"nota_final":td("grade"),"count":td("students")},
                             color_discrete_sequence=[_ACCENT])
    _base_layout(fig_notas, td("grade_dist"))
    _chart_row([(fig_area,2),(fig_notas,3)])


# ── 🚚 LOGÍSTICA ──────────────────────────────────────────────────────────────
def _dash_logistica(tabelas):
    fato = tabelas["FatoEntrega"]; trans = tabelas["DimTransportadora"]
    frete_total = fato["valor_frete"].sum()
    _section("overview")
    _kpi_row([
        (td("freight_revenue"), f"R$ {_fmt_num(frete_total, 0)}",              f"{_fmt_num(len(fato), 0)} {td('deliveries')}"),
        (td("avg_freight"),     f"R$ {_fmt_num(fato['valor_frete'].mean(), 2)}",td("per_delivery")),
        (td("delivery_rate"),   f"{(fato['status']=='Entregue').mean()*100:.1f}%", td("completed")),
        (td("on_time"),         f"{(fato['dias_entregue']<=fato['prazo_acordado']).mean()*100:.1f}%", td("within_deadline")),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "valor_frete", td("monthly_freight"), "valor_frete")

    by_status = fato["status"].value_counts().reset_index()
    fig_status = px.pie(by_status, names="status", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
    fig_status.update_traces(textfont_color=_INK)
    _base_layout(fig_status, td("delivery_status"))

    _section("carriers_routes")
    _chart_row([(fig_mes,3),(fig_status,2)])

    top_t = (fato.groupby("id_transportadora")["valor_frete"].sum().reset_index()
             .sort_values("valor_frete",ascending=False).head(10)
             .merge(trans[["id_transportadora","nome"]], on="id_transportadora"))
    fig_trans = px.bar(top_t, x="valor_frete", y="nome", orientation="h",
                       labels={"valor_frete":td("revenue_brl"),"nome":""},
                       color="valor_frete", color_continuous_scale=["#16233F","#B8862E"])
    fig_trans.update_layout(coloraxis_showscale=False)
    _base_layout(fig_trans, td("top_carriers"))

    fato["atraso"] = (fato["dias_entregue"] - fato["prazo_acordado"]).clip(lower=0)
    at = fato.merge(trans[["id_transportadora","tipo"]], on="id_transportadora")
    by_tipo = at.groupby("tipo")["atraso"].mean().reset_index()
    fig_atr = px.bar(by_tipo, x="tipo", y="atraso",
                     labels={"atraso":td("delay_days"),"tipo":""},
                     color="atraso", color_continuous_scale=["#4ade80","#f59e0b","#ef4444"])
    fig_atr.update_layout(coloraxis_showscale=False)
    _base_layout(fig_atr, td("avg_delay_type"))
    _chart_row([(fig_trans,3),(fig_atr,2)])


# ── ⚡ ENERGIA ────────────────────────────────────────────────────────────────
def _dash_energia(tabelas):
    fato = tabelas["FatoConsumo"]; consumidor = tabelas["DimConsumidor"]
    _section("overview")
    _kpi_row([
        (td("total_consumption"), f"{_fmt_num(fato['consumo_kwh'].sum(), 0)} kWh", f"{_fmt_num(len(fato), 0)} {td('readings')}"),
        (td("total_billing"),     f"R$ {_fmt_num(fato['valor_fatura'].sum(), 0)}",  td("all_bills")),
        (td("avg_bill"),          f"R$ {_fmt_num(fato['valor_fatura'].mean(), 2)}", td("per_reading")),
        (td("power_factor"),      f"{fato['fator_potencia'].mean():.3f}",    td("overall_avg")),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "consumo_kwh", td("monthly_consumption"), "consumo_kwh")

    merged = fato.merge(consumidor[["id_consumidor","classe"]], on="id_consumidor")
    by_cls = merged.groupby("classe")["consumo_kwh"].sum().reset_index().sort_values("consumo_kwh")
    fig_cls = px.bar(by_cls, x="consumo_kwh", y="classe", orientation="h",
                     labels={"consumo_kwh":td("consumption_kwh"),"classe":td("class_")},
                     color="consumo_kwh", color_continuous_scale=["#16233F","#B8862E"])
    fig_cls.update_layout(coloraxis_showscale=False)
    _base_layout(fig_cls, td("consumption_by_class"))

    _section("tariffs")
    _chart_row([(fig_mes,3),(fig_cls,2)])

    fato2 = fato.copy(); fato2["mes"] = pd.to_datetime(fato2["id_data"]).dt.to_period("M").astype(str)
    by_tar = fato2.groupby("mes")["tarifa_kwh"].mean().reset_index()
    fig_tar = px.line(by_tar, x="mes", y="tarifa_kwh",
                      labels={"mes":"","tarifa_kwh":td("tariff_avg")}, markers=True)
    fig_tar.update_traces(line_color=_ACCENT, marker_color=_ACCENT)
    _base_layout(fig_tar, td("tariff_evolution"))

    by_fat = merged.groupby("classe")["valor_fatura"].sum().reset_index().sort_values("valor_fatura",ascending=False)
    fig_fat = px.pie(by_fat, names="classe", values="valor_fatura", hole=0.55, color_discrete_sequence=_PALETTE)
    fig_fat.update_traces(textfont_color=_INK)
    _base_layout(fig_fat, td("revenue_by_class"))
    _chart_row([(fig_tar,3),(fig_fat,2)])


# ── 📡 TELECOM ────────────────────────────────────────────────────────────────
def _dash_telecom(tabelas):
    fato = tabelas["FatoChamada"]
    has_custo     = "custo" in fato.columns
    has_qualidade = "qualidade_sinal" in fato.columns
    _section("overview")
    metrics = [
        (td("total_calls"),   f"{_fmt_num(len(fato), 0)}",                          td("in_period")),
        (td("avg_duration"),  f"{fato['duracao_seg'].mean():.1f}s",       td("per_call")),
    ]
    if has_custo:
        metrics.append((td("total_cost"), f"R$ {_fmt_num(fato['custo'].sum(), 2)}", td("billed_calls")))
    else:
        metrics.append((td("avg_data"),   f"{fato['dados_mb'].mean():.1f} MB", td("avg_per_call")))
    if has_qualidade:
        metrics.append((td("avg_quality"), f"{fato['qualidade_sinal'].mean():.1f}/5", td("signal_score")))
    else:
        metrics.append((td("quality_dbm"), f"{fato['qualidade_dbm'].mean():.0f} dBm", td("avg_signal")))
    _kpi_row(metrics)

    fato2 = fato.copy(); fato2["dia"] = pd.to_datetime(fato2["id_data"]).dt.date
    by_dia = fato2.groupby("dia").size().reset_index(name="count")
    fig_dia = px.line(by_dia, x="dia", y="count", labels={"dia":"","count":td("calls_axis")})
    fig_dia.update_traces(line_color=_ACCENT)
    _base_layout(fig_dia, td("daily_calls"))
    _chart_row([(fig_dia,1)])


# ── 🏭 INDÚSTRIA ──────────────────────────────────────────────────────────────
def _dash_industria(tabelas):
    fato = tabelas["FatoProducao"]
    qtd_col   = "quantidade" if "quantidade" in fato.columns else "qtd_produzida"
    refugo_col= "refugo_pct" if "refugo_pct" in fato.columns else "qtd_refugo"
    oee_col   = "oee" if "oee" in fato.columns else "oee_pct"
    custo_col = "custo_producao" if "custo_producao" in fato.columns else "custo_total"
    qtd_total = fato[qtd_col].sum()
    refugo_t  = fato[refugo_col].sum()
    refugo_pct= (refugo_t/qtd_total*100) if qtd_total>0 else 0
    _section("overview")
    _kpi_row([
        (td("total_production"), f"{_fmt_num(qtd_total, 0)}", td("unit_plural")),
        (td("scrap_rate"),       f"{refugo_pct:.2f}%", td("loss")),
        (td("avg_oee"),          f"{fato[oee_col].mean()*100:.1f}%", td("global_efficiency")),
        (td("total_cost"),       f"R$ {_fmt_num(fato[custo_col].sum(), 0)}", td("production_sub")),
    ])
    if "id_maquina" in fato.columns:
        by_maq = fato.groupby("id_maquina")[qtd_col].sum().reset_index()
        fig_maq = px.bar(by_maq, x="id_maquina", y=qtd_col,
                         labels={qtd_col:td("qty_produced"),"id_maquina":td("machine")})
        _base_layout(fig_maq, td("production_by_machine"))
        _chart_row([(fig_maq,1)])
    else:
        st.info(td("no_machine_data"))


# ── 🌾 AGRONEGÓCIO ────────────────────────────────────────────────────────────
def _dash_agronegocio(tabelas):
    fato = tabelas["FatoSafra"]; cultura = tabelas["DimCultura"]; prop = tabelas["DimPropriedade"]
    area_col  = next((c for c in ['area_plantada_ha','area_plantada','area_ha'] if c in fato.columns), None)
    custo_col = next((c for c in ['custo_total','custo_ha','custo'] if c in fato.columns), None)
    receita   = fato["receita"].sum() if "receita" in fato.columns else 0
    producao  = fato["producao_ton"].sum() if "producao_ton" in fato.columns else 0
    n_safras  = len(fato)
    area_total= fato[area_col].sum() if area_col else 0
    produtividade = producao/area_total if area_total>0 else 0
    custo_total   = fato[custo_col].sum() if custo_col else 0
    _section("overview")
    _kpi_row([
        (td("total_revenue"), f"R$ {_fmt_num(receita, 0)}",                              f"{_fmt_num(n_safras, 0)} safras"),
        (td("total_production") if "total_production" in {} else "Produção Total", f"{_fmt_num(producao, 0)} t", "toneladas colhidas"),
        (td("productivity") if "productivity" in {} else "Produtividade",          f"{produtividade:.2f} t/ha", "t/ha média"),
        (td("avg_cost") if "avg_cost" in {} else "Custo Médio",                   f"R$ {_fmt_num(custo_total/n_safras if n_safras else 0, 2)}", "por safra"),
    ])

    figs = []
    if "receita" in fato.columns:
        fig_mes = _monthly_chart(fato, "id_data", "receita", td("monthly_revenue"), "receita")
        figs.append((fig_mes,3))

    if "producao_ton" in fato.columns and "id_cultura" in fato.columns:
        merged = fato.merge(cultura[["id_cultura","nome"]], on="id_cultura")
        by_cult = merged.groupby("nome")["producao_ton"].sum().reset_index().sort_values("producao_ton").tail(10)
        fig_cult = px.bar(by_cult, x="producao_ton", y="nome", orientation="h",
                          labels={"producao_ton":td("production_ton"),"nome":td("crop")},
                          color="producao_ton", color_continuous_scale=["#16233F","#B8862E"])
        fig_cult.update_layout(coloraxis_showscale=False)
        _base_layout(fig_cult, td("top10_crops"))
        figs.append((fig_cult,2))

    if figs: _chart_row(figs)

    figs2 = []
    if "produtividade_tha" in fato.columns and "id_cultura" in fato.columns:
        merged2 = fato.merge(cultura[["id_cultura","nome"]], on="id_cultura")
        by_prod = merged2.groupby("nome")["produtividade_tha"].mean().reset_index().sort_values("produtividade_tha",ascending=False).head(10)
        fig_prod = px.bar(by_prod, x="produtividade_tha", y="nome", orientation="h",
                          labels={"produtividade_tha":td("productivity_tha"),"nome":td("crop")},
                          color="produtividade_tha", color_continuous_scale=["#16233F","#6E86A8","#B8862E"])
        fig_prod.update_layout(coloraxis_showscale=False)
        _base_layout(fig_prod, td("top10_productivity"))
        figs2.append((fig_prod,2))

    if "status" in fato.columns:
        by_status = fato["status"].value_counts().reset_index()
        fig_status = px.pie(by_status, names="status", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
        fig_status.update_traces(textfont_color=_INK)
        _base_layout(fig_status, td("harvest_status"))
        figs2.append((fig_status,1))

    if figs2: _chart_row(figs2)


# ── ✈️ TURISMO ────────────────────────────────────────────────────────────────
def _dash_turismo(tabelas):
    fato = tabelas["FatoViagens"]; destino = tabelas["DimDestino"]
    _section("overview")
    tx_cancel = (fato["status"]=="Cancelada").mean()*100 if "status" in fato.columns else 0
    _kpi_row([
        (td("total_revenue"),   f"R$ {_fmt_num(fato['valor_pago'].sum(), 0)}",  f"{_fmt_num(len(fato), 0)} viagens"),
        (td("avg_ticket"),      f"R$ {_fmt_num(fato['valor_pago'].mean(), 2)}", td("per_booking")),
        (td("cancel_rate"),     f"{tx_cancel:.1f}%",                     td("cancelled_status")),
        (td("total_passengers"),f"{_fmt_num(fato['passageiros'].sum(), 0)}",         td("persons")),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "valor_pago", td("monthly_revenue"), "valor_pago")

    fig_pais = None
    if "id_destino" in fato.columns:
        merged = fato.merge(destino[["id_destino","pais"]], on="id_destino")
        by_pais = merged.groupby("pais")["valor_pago"].sum().reset_index().sort_values("valor_pago",ascending=False).head(10)
        fig_pais = px.bar(by_pais, x="pais", y="valor_pago",
                          labels={"valor_pago":td("revenue_brl"),"pais":td("country")},
                          color="valor_pago", color_continuous_scale=_PALETTE)
        fig_pais.update_layout(coloraxis_showscale=False)
        _base_layout(fig_pais, td("revenue_by_country"))

    _chart_row([(fig_mes,3),(fig_pais,2)] if fig_pais else [(fig_mes,1)])


# ── 🏠 IMOBILIÁRIO ────────────────────────────────────────────────────────────
def _dash_imobiliario(tabelas):
    fato = tabelas["FatoVendas"]; imovel = tabelas["DimImovel"]
    tx_venda = (fato["tipo_negocio"]=="Venda").mean()*100 if "tipo_negocio" in fato.columns else 50
    _section("overview")
    _kpi_row([
        (td("business_volume"), f"R$ {_fmt_num(fato['valor_final'].sum(), 0)}",  f"{_fmt_num(len(fato), 0)} {td('contracts')}"),
        (td("avg_value"),       f"R$ {_fmt_num(fato['valor_final'].mean(), 2)}", td("per_contract")),
        (td("pct_sales"),       f"{tx_venda:.1f}%",                       td("vs_rentals")),
        (td("avg_area"),        f"{imovel['area_m2'].mean():.1f} m²",     td("per_property")),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "valor_final", td("monthly_business"), "valor_final")

    merged = fato.merge(imovel[["id_imovel","tipo"]], on="id_imovel")
    by_tipo = merged.groupby("tipo")["valor_final"].sum().reset_index()
    fig_tipo = px.pie(by_tipo, names="tipo", values="valor_final", hole=0.55, color_discrete_sequence=_PALETTE)
    fig_tipo.update_traces(textfont_color=_INK)
    _base_layout(fig_tipo, td("by_property_type"))
    _chart_row([(fig_mes,3),(fig_tipo,2)])


# ── 🛡️ SEGUROS ────────────────────────────────────────────────────────────────
def _dash_seguros(tabelas):
    fato = tabelas["FatoApolices"]; plano = tabelas["DimPlano"]
    premios = fato["valor_premio"].sum(); indenizacoes = fato["valor_indenizacao"].sum()
    loss_ratio = indenizacoes/premios*100 if premios>0 else 0
    _section("overview")
    _kpi_row([
        (td("total_premiums"), f"R$ {_fmt_num(premios, 0)}",             f"{_fmt_num(len(fato), 0)} {td('policies')}"),
        (td("paid_claims"),    f"R$ {_fmt_num(indenizacoes, 0)}",         td("claims_paid")),
        (td("loss_ratio"),     f"{loss_ratio:.1f}%",              td("sp_ratio")),
        (td("avg_premium"),    f"R$ {_fmt_num(fato['valor_premio'].mean(), 2)}", td("per_policy")),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "valor_premio", td("monthly_premiums"), "valor_premio")

    merged = fato.merge(plano[["id_plano","tipo"]], on="id_plano")
    by_tipo = merged.groupby("tipo")["valor_premio"].sum().reset_index().sort_values("valor_premio")
    fig_tipo = px.bar(by_tipo, x="valor_premio", y="tipo", orientation="h",
                      labels={"valor_premio":td("premiums_brl"),"tipo":""},
                      color="valor_premio", color_continuous_scale=["#16233F","#B8862E"])
    fig_tipo.update_layout(coloraxis_showscale=False)
    _base_layout(fig_tipo, td("premiums_by_type"))
    _chart_row([(fig_mes,3),(fig_tipo,2)])


# ── 🏗️ CONSTRUÇÃO ─────────────────────────────────────────────────────────────
def _dash_construcao(tabelas):
    fato = tabelas["FatoCustos"]; projeto = tabelas["DimProjeto"]
    custo_total = fato["custo_real"].sum(); horas = fato["horas_trabalhadas"].sum()
    _section("overview")
    _kpi_row([
        (td("total_real_cost"), f"R$ {_fmt_num(custo_total, 0)}",        f"{_fmt_num(len(fato), 0)} {td('cost_entries')}"),
        (td("total_hours"),     f"{_fmt_num(horas, 0)}h",                  td("labor")),
        (td("cost_per_hour"),   f"R$ {_fmt_num(custo_total/horas if horas else 0, 2)}", td("efficiency")),
        (td("num_projects"),    f"{len(projeto)}",                  td("active_projects")),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "custo_real", td("monthly_costs"), "custo_real")

    merged = fato.merge(projeto[["id_projeto","nome"]], on="id_projeto")
    by_proj = merged.groupby("nome")["custo_real"].sum().reset_index().sort_values("custo_real",ascending=False).head(10)
    fig_proj = px.bar(by_proj, x="nome", y="custo_real",
                      labels={"custo_real":td("cost_brl"),"nome":td("project")},
                      color="custo_real", color_continuous_scale=_PALETTE)
    fig_proj.update_layout(coloraxis_showscale=False)
    _base_layout(fig_proj, td("top10_projects"))
    _chart_row([(fig_mes,3),(fig_proj,2)])


# ════════════════════════════════════════════════════════════════════════════
#  NOVOS DASHBOARDS
# ════════════════════════════════════════════════════════════════════════════

# ── 🏨 HOTELARIA ─────────────────────────────────────────────────────────────
def _dash_hotelaria(tabelas):
    fato = tabelas.get("FatoReserva") or tabelas.get("FatoReservas")
    if fato is None:
        st.warning("Tabela FatoReserva não encontrada.")
        return
    receita = fato["valor_total"].sum() if "valor_total" in fato else fato.select_dtypes("number").iloc[:,0].sum()
    n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),  f"R$ {_fmt_num(receita, 0)}",                    f"{_fmt_num(n, 0)} {td('in_period')}"),
        (td("avg_ticket"),     f"R$ {_fmt_num(receita/n, 2)}" if n else "—",    td("per_booking")),
        (td("avg_value"),      f"{fato['diarias'].mean():.1f}" if 'diarias' in fato.columns else "—", td("in_period")),
        (td("total_volume"),   f"{_fmt_num(n, 0)}",                                 td("in_period")),
    ])
    val_col = "valor_total" if "valor_total" in fato.columns else fato.select_dtypes("number").columns[0]
    date_col = [c for c in fato.columns if "data" in c][0]
    fig_mes = _monthly_chart(fato, date_col, val_col, td("monthly_revenue"), val_col)
    if "canal" in fato.columns:
        by_canal = fato.groupby("canal")[val_col].sum().reset_index()
        fig_canal = px.pie(by_canal, names="canal", values=val_col, hole=0.55, color_discrete_sequence=_PALETTE)
        _base_layout(fig_canal, td("revenue_by_channel"))
        _chart_row([(fig_mes, 3), (fig_canal, 2)])
    else:
        st.plotly_chart(fig_mes, use_container_width=True, config={"displayModeBar": False})


# ── 🎬 STREAMING ─────────────────────────────────────────────────────────────
def _dash_streaming(tabelas):
    fato = tabelas.get("FatoPlay") or tabelas.get("FatoPlays")
    if fato is None:
        st.warning("Tabela FatoPlay não encontrada.")
        return
    n = len(fato)
    _section("overview")
    num_cols = fato.select_dtypes("number").columns
    receita_col = next((c for c in ["receita","valor","receita_usd"] if c in fato.columns), num_cols[0] if len(num_cols) else None)
    dur_col = next((c for c in ["duracao_min","duracao","tempo_min"] if c in fato.columns), None)
    receita = fato[receita_col].sum() if receita_col else 0
    dur_media = fato[dur_col].mean() if dur_col else 0
    _kpi_row([
        (td("total_revenue"),  f"R$ {_fmt_num(receita, 0)}",        f"{_fmt_num(n, 0)} plays"),
        (td("avg_value"),      f"{dur_media:.0f} min",       td("per_visit")),
        (td("total_volume"),   f"{_fmt_num(n, 0)}",                     td("in_period")),
        (td("efficiency"),     f"{_fmt_num(fato[dur_col].sum()/60, 0)}h" if dur_col else "—", td("in_period")),
    ])
    date_col = [c for c in fato.columns if "data" in c][0]
    fig_mes = _monthly_chart(fato, date_col, receita_col or num_cols[0], td("monthly_revenue"), td("revenue_brl"))
    if "genero" in fato.columns:
        by_gen = fato.groupby("genero")[receita_col].sum().reset_index().sort_values(receita_col, ascending=False).head(8)
        fig_gen = px.bar(by_gen, x=receita_col, y="genero", orientation="h",
                         labels={receita_col: td("revenue_brl"), "genero": ""})
        fig_gen.update_traces(marker_color=_ACCENT)
        _base_layout(fig_gen, td("revenue_by_category"))
        _chart_row([(fig_mes, 3), (fig_gen, 2)])
    else:
        st.plotly_chart(fig_mes, use_container_width=True, config={"displayModeBar": False})


# ── 🏪 E-COMMERCE ─────────────────────────────────────────────────────────────
def _dash_ecommerce(tabelas):
    fato = tabelas["FatoPedido"]; produto = tabelas["DimProduto"]
    receita = fato["valor_total"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),  f"R$ {_fmt_num(receita, 0)}",                          f"{_fmt_num(n, 0)} {td('sales')}"),
        (td("avg_ticket"),     f"R$ {_fmt_num(fato['valor_total'].mean(), 2)}",        td("per_sale")),
        (td("avg_discount"),   f"R$ {_fmt_num(fato['desconto'].mean(), 2)}",           td("per_sale")),
        (td("efficiency"),     f"{(fato['status']=='entregue').mean()*100:.1f}%" if 'status' in fato.columns else "—", td("completed")),
    ])
    fig_mes = _monthly_chart(fato, "data_pedido", "valor_total", td("monthly_revenue"), "valor_total")
    merged = fato.merge(produto[["sk_produto", "categoria"]], on="sk_produto", how="left")
    by_cat = merged.groupby("categoria")["valor_total"].sum().reset_index().sort_values("valor_total").tail(10)
    fig_cat = px.bar(by_cat, x="valor_total", y="categoria", orientation="h",
                     labels={"valor_total": td("revenue_brl"), "categoria": ""})
    fig_cat.update_traces(marker_color=_ACCENT)
    _base_layout(fig_cat, td("revenue_by_category"))
    _section("distribution")
    _chart_row([(fig_mes, 3), (fig_cat, 2)])
    if "status" in fato.columns:
        by_status = fato["status"].value_counts().reset_index()
        by_status.columns = ["status", "count"]
        fig_status = px.pie(by_status, names="status", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
        _base_layout(fig_status, td("status_dist"))
        st.plotly_chart(fig_status, use_container_width=True, config={"displayModeBar": False})


# ── 🏢 RECURSOS HUMANOS ───────────────────────────────────────────────────────
def _dash_rh(tabelas):
    fato = tabelas["FatoHorasTrabalhadas"]; dept = tabelas["DimDepartamento"]; cargo = tabelas["DimCargo"]
    n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),  f"R$ {_fmt_num(fato['custo_diario'].sum(), 0)}",          f"{_fmt_num(n, 0)} {td('in_period')}"),
        (td("avg_value"),      f"{fato['horas_trabalhadas'].mean():.1f}h",        td("per_visit")),
        (td("efficiency"),     f"{fato['produtividade'].mean():.1f}%",            td("global_efficiency")),
        (td("score"),          f"{fato['satisfacao'].mean():.2f}",                td("overall_avg")),
    ])
    fig_mes = _monthly_chart(fato, "data_registro", "custo_diario", td("monthly_costs"), "custo_diario")
    merged = fato.merge(dept[["sk_departamento", "nome_departamento"]], on="sk_departamento", how="left")
    by_dept = merged.groupby("nome_departamento")["custo_diario"].sum().reset_index().sort_values("custo_diario").tail(10)
    fig_dept = px.bar(by_dept, x="custo_diario", y="nome_departamento", orientation="h",
                      labels={"custo_diario": td("cost_brl"), "nome_departamento": ""})
    fig_dept.update_traces(marker_color=_ACCENT)
    _base_layout(fig_dept, td("revenue_by_area"))
    _section("segmentation")
    _chart_row([(fig_mes, 3), (fig_dept, 2)])
    fig_prod = px.histogram(fato, x="produtividade", nbins=30, color_discrete_sequence=[_ACCENT],
                            labels={"produtividade": td("efficiency")})
    _base_layout(fig_prod, td("grade_dist"))
    st.plotly_chart(fig_prod, use_container_width=True, config={"displayModeBar": False})


# ── 🚗 MOBILIDADE ─────────────────────────────────────────────────────────────
def _dash_mobilidade(tabelas):
    fato = tabelas["FatoViagem"]
    receita = fato["valor_total"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),  f"R$ {_fmt_num(receita, 0)}",                              f"{_fmt_num(n, 0)} viagens"),
        (td("avg_ticket"),     f"R$ {_fmt_num(fato['valor_total'].mean(), 2)}",            td("per_sale")),
        (td("efficiency"),     f"{fato['distancia_km'].mean():.1f} km",            td("per_sale")),
        (td("score"),          f"{fato['avaliacao_passageiro'].mean():.2f}",        td("overall_avg")),
    ])
    fato["_data"] = pd.to_datetime(fato["data_hora_inicio"]).dt.date.astype(str)
    fig_mes = _monthly_chart(fato, "_data", "valor_total", td("monthly_revenue"), "valor_total")
    if "status" in fato.columns:
        by_status = fato["status"].value_counts().reset_index()
        by_status.columns = ["status", "count"]
        fig_status = px.pie(by_status, names="status", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
        _base_layout(fig_status, td("status_dist"))
        _chart_row([(fig_mes, 3), (fig_status, 2)])
    else:
        st.plotly_chart(fig_mes, use_container_width=True, config={"displayModeBar": False})


# ── 🏦 FINTECH ────────────────────────────────────────────────────────────────
def _dash_fintech(tabelas):
    fato = tabelas["FatoTransacao"]
    vol = fato["valor"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_volume"),   f"R$ {_fmt_num(vol, 0)}",                                    f"{_fmt_num(n, 0)} {td('transactions')}"),
        (td("approval_rate"),  f"{(fato['status']=='aprovada').mean()*100:.1f}%",    td("approved_tx")),
        (td("avg_value"),      f"R$ {_fmt_num(fato['valor'].mean(), 2)}",                    td("per_tx")),
        (td("avg_ticket"),     f"R$ {_fmt_num(fato['cashback_valor'].mean(), 2)}",           "cashback médio"),
    ])
    fato["_d"] = pd.to_datetime(fato["data_hora"]).dt.date.astype(str)
    fig_mes = _monthly_chart(fato, "_d", "valor", td("monthly_volume"), "valor")
    comerciante = tabelas["DimComerciante"]
    merged = fato.merge(comerciante[["sk_comerciante","categoria"]], on="sk_comerciante", how="left")
    by_cat = merged.groupby("categoria")["valor"].sum().reset_index().sort_values("valor").tail(10)
    fig_cat = px.bar(by_cat, x="valor", y="categoria", orientation="h",
                     labels={"valor": td("volume_brl"), "categoria": ""})
    fig_cat.update_traces(marker_color=_ACCENT)
    _base_layout(fig_cat, td("volume_by_product"))
    _section("distribution")
    _chart_row([(fig_mes, 3), (fig_cat, 2)])
    by_status = fato["status"].value_counts().reset_index()
    by_status.columns = ["status", "count"]
    fig_status = px.pie(by_status, names="status", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
    _base_layout(fig_status, td("status_dist"))
    st.plotly_chart(fig_status, use_container_width=True, config={"displayModeBar": False})


# ── ⛏️ MINERAÇÃO ──────────────────────────────────────────────────────────────
def _dash_mineracao(tabelas):
    fato = tabelas["FatoExtracao"]; mina = tabelas["DimMina"]; mineral = tabelas["DimMineral"]
    receita = fato["receita"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),     f"R$ {_fmt_num(receita, 0)}",                               f"{_fmt_num(n, 0)} {td('in_period')}"),
        (td("total_production"),  f"{_fmt_num(fato['volume_extraido_ton'].sum(), 0)} t",       td("production_sub")),
        (td("efficiency"),        f"{fato['indice_seguranca'].mean():.1f}",            td("score")),
        (td("avg_cost"),          f"R$ {_fmt_num(fato['custo_operacional'].mean(), 2)}",       td("per_visit")),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "receita", td("monthly_revenue"), "receita")
    merged = fato.merge(mineral[["id_mineral","nome"]], on="id_mineral", how="left")
    by_min = merged.groupby("nome")["volume_extraido_ton"].sum().reset_index().sort_values("volume_extraido_ton").tail(10)
    fig_min = px.bar(by_min, x="volume_extraido_ton", y="nome", orientation="h",
                     labels={"volume_extraido_ton": "Volume (t)", "nome": ""})
    fig_min.update_traces(marker_color=_ACCENT)
    _base_layout(fig_min, td("top10_crops"))
    _chart_row([(fig_mes, 3), (fig_min, 2)])


# ── ⚖️ JURÍDICO ───────────────────────────────────────────────────────────────
def _dash_juridico(tabelas):
    fato = tabelas["FatoProcesso"]; advogado = tabelas["DimAdvogado"]
    honorarios = fato["honorarios"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),  f"R$ {_fmt_num(honorarios, 0)}",                                f"{_fmt_num(n, 0)} processos"),
        (td("avg_value"),      f"R$ {_fmt_num(fato['valor_causa'].mean(), 2)}",                 "valor médio da causa"),
        (td("efficiency"),     f"{fato['resultado_favoravel'].mean()*100:.1f}%",        "taxa de êxito"),
        (td("avg_delay_type"), f"{fato['duracao_dias'].mean():.0f} dias",               "duração média"),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "honorarios", td("monthly_revenue"), "honorarios")
    by_area = fato.groupby("area_direito")["honorarios"].sum().reset_index().sort_values("honorarios").tail(8)
    fig_area = px.bar(by_area, x="honorarios", y="area_direito", orientation="h",
                      labels={"honorarios": td("revenue_brl"), "area_direito": td("area")})
    fig_area.update_traces(marker_color=_ACCENT)
    _base_layout(fig_area, td("revenue_by_area"))
    _chart_row([(fig_mes, 3), (fig_area, 2)])
    by_status = fato["status"].value_counts().reset_index()
    by_status.columns = ["status", "count"]
    fig_status = px.pie(by_status, names="status", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
    _base_layout(fig_status, td("status_dist"))
    st.plotly_chart(fig_status, use_container_width=True, config={"displayModeBar": False})


# ── 🏟️ ESPORTES ──────────────────────────────────────────────────────────────
def _dash_esportes(tabelas):
    fato = tabelas["FatoPartida"]; clube = tabelas["DimClube"]
    receita = (fato["receita_bilheteria"] + fato["receita_tv"] + fato["receita_patrocinio"]).sum()
    n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),  f"R$ {_fmt_num(receita, 0)}",                               f"{_fmt_num(n, 0)} partidas"),
        (td("avg_ticket"),     f"{_fmt_num(fato['publico'].mean(), 0)}",                    "público médio"),
        (td("score"),          f"{fato['gols_casa'].mean() + fato['gols_fora'].mean():.2f}", "gols/partida"),
        (td("efficiency"),     f"{fato['receita_bilheteria'].sum()/receita*100:.1f}%", "% bilheteria"),
    ])
    fato["receita_total"] = fato["receita_bilheteria"] + fato["receita_tv"] + fato["receita_patrocinio"]
    fig_mes = _monthly_chart(fato, "id_data", "receita_total", td("monthly_revenue"), "receita_total")
    by_res = fato["resultado"].value_counts().reset_index()
    by_res.columns = ["resultado", "count"]
    fig_res = px.pie(by_res, names="resultado", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
    _base_layout(fig_res, td("result_dist"))
    _chart_row([(fig_mes, 3), (fig_res, 2)])


# ── ☁️ SAAS B2B ──────────────────────────────────────────────────────────────
def _dash_saas_b2b(tabelas):
    fato = tabelas["FatoAssinatura"]; plano = tabelas["DimPlano"]; cliente = tabelas["DimCliente"]
    mrr_total = fato["mrr"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_mrr"),      f"R$ {_fmt_num(mrr_total, 0)}",                              f"{_fmt_num(n, 0)} {td('in_period')}"),
        (td("arr_sub"),        f"R$ {_fmt_num(fato['arr'].mean(), 0)}",                      td("per_contract")),
        (td("nps_scale"),      f"{fato['nps'].mean():.1f}",                          td("overall_avg")),
        (td("efficiency"),     f"{fato['churn'].mean()*100:.1f}%",                   "churn rate"),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "mrr", td("mrr_by_month"), "mrr")
    merged = fato.merge(cliente[["id_cliente","segmento"]], on="id_cliente", how="left")
    by_seg = merged.groupby("segmento")["mrr"].sum().reset_index()
    fig_seg = px.pie(by_seg, names="segmento", values="mrr", hole=0.55, color_discrete_sequence=_PALETTE)
    _base_layout(fig_seg, td("mrr_by_segment"))
    _section("segmentation")
    _chart_row([(fig_mes, 3), (fig_seg, 2)])
    fig_nps = px.histogram(fato, x="nps", nbins=20, color_discrete_sequence=[_ACCENT],
                           labels={"nps": td("nps_scale")})
    _base_layout(fig_nps, td("nps_dist"))
    st.plotly_chart(fig_nps, use_container_width=True, config={"displayModeBar": False})


# ── 🤝 CRM ────────────────────────────────────────────────────────────────────
def _dash_crm(tabelas):
    fato = tabelas["FatoOportunidade"]; vendedor = tabelas["DimVendedor"]
    receita = fato["valor_fechado"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),  f"R$ {_fmt_num(receita, 0)}",                                  f"{_fmt_num(n, 0)} oportunidades"),
        (td("efficiency"),     f"{fato['ganho'].mean()*100:.1f}%",                     "win rate"),
        (td("avg_ticket"),     f"R$ {_fmt_num(fato['valor_estimado'].mean(), 2)}",             "valor médio"),
        (td("avg_delay_type"), f"{fato['ciclo_vendas_dias'].mean():.0f} dias",         "ciclo médio"),
    ])
    fig_mes = _monthly_chart(fato, "id_data_abertura", "valor_fechado", td("monthly_revenue"), "valor_fechado")
    by_estagio = fato.groupby("estagio")["valor_estimado"].sum().reset_index()
    fig_funnel = px.bar(by_estagio, x="estagio", y="valor_estimado",
                        labels={"valor_estimado": td("revenue_brl"), "estagio": ""},
                        color="valor_estimado", color_continuous_scale=_PALETTE)
    fig_funnel.update_layout(coloraxis_showscale=False)
    _base_layout(fig_funnel, "Pipeline por Estágio")
    _section("segmentation")
    _chart_row([(fig_mes, 3), (fig_funnel, 2)])


# ── 💊 FARMACÊUTICO ───────────────────────────────────────────────────────────
def _dash_farmaceutico(tabelas):
    fato = tabelas["FatoVenda"]; produto = tabelas["DimProduto"]
    receita = fato["valor_liquido"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),  f"R$ {_fmt_num(receita, 0)}",                              f"{_fmt_num(n, 0)} {td('sales')}"),
        (td("avg_ticket"),     f"R$ {_fmt_num(fato['valor_liquido'].mean(), 2)}",          td("per_sale")),
        (td("avg_discount"),   f"{fato['desconto_pct'].mean():.1f}%",             td("on_full_price")),
        (td("efficiency"),     f"{(~fato['devolvido']).mean()*100:.1f}%",          "taxa de retenção"),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "valor_liquido", td("monthly_revenue"), "valor_liquido")
    merged = fato.merge(produto[["id_produto","classe_terapeutica"]], on="id_produto", how="left")
    by_class = merged.groupby("classe_terapeutica")["valor_liquido"].sum().reset_index().sort_values("valor_liquido").tail(10)
    fig_class = px.bar(by_class, x="valor_liquido", y="classe_terapeutica", orientation="h",
                       labels={"valor_liquido": td("revenue_brl"), "classe_terapeutica": td("class_")})
    fig_class.update_traces(marker_color=_ACCENT)
    _base_layout(fig_class, td("revenue_by_class"))
    _section("segmentation")
    _chart_row([(fig_mes, 3), (fig_class, 2)])


# ── 📣 MARKETING DIGITAL ─────────────────────────────────────────────────────
def _dash_marketing(tabelas):
    fato = tabelas["FatoPerformance"]; conv = tabelas["FatoConversao"]; canal = tabelas["DimCanal"]
    investimento = fato["investimento"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_volume"),   f"R$ {_fmt_num(investimento, 0)}",                             f"{_fmt_num(n, 0)} campanhas/dia"),
        (td("efficiency"),     f"{fato['ctr_pct'].mean():.2f}%",                      "CTR médio"),
        (td("avg_value"),      f"R$ {_fmt_num(fato['cpc'].mean(), 2)}",                       "CPC médio"),
        (td("score"),          f"{conv['roas'].mean():.2f}x",                         "ROAS médio"),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "investimento", td("monthly_costs"), "investimento")
    merged = fato.merge(canal[["id_canal","nome"]], on="id_canal", how="left")
    by_canal = merged.groupby("nome")["investimento"].sum().reset_index().sort_values("investimento")
    fig_canal = px.bar(by_canal, x="investimento", y="nome", orientation="h",
                       labels={"investimento": td("cost_brl"), "nome": ""})
    fig_canal.update_traces(marker_color=_ACCENT)
    _base_layout(fig_canal, td("revenue_by_channel"))
    _section("channels")
    _chart_row([(fig_mes, 3), (fig_canal, 2)])
    by_disp = fato.groupby("dispositivo")["investimento"].sum().reset_index()
    fig_disp = px.pie(by_disp, names="dispositivo", values="investimento", hole=0.55, color_discrete_sequence=_PALETTE)
    _base_layout(fig_disp, "Investimento por Dispositivo")
    st.plotly_chart(fig_disp, use_container_width=True, config={"displayModeBar": False})


# ── 🛢️ PETRÓLEO & GÁS ────────────────────────────────────────────────────────
def _dash_petroleo(tabelas):
    fato = tabelas["FatoProducao"]; custo = tabelas["FatoCusto"]; plat = tabelas["DimPlataforma"]
    receita = fato["receita_usd"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),     f"US$ {_fmt_num(receita, 0)}",                               f"{_fmt_num(n, 0)} registros"),
        (td("total_production"),  f"{_fmt_num(fato['vol_oleo_bbl'].sum(), 0)} bbl",             "óleo total"),
        (td("efficiency"),        f"{fato['eficiencia_pct'].mean():.1f}%",              td("global_efficiency")),
        (td("avg_cost"),          f"US$ {_fmt_num(custo['lifting_cost_bbl'].mean(), 2)}",       "lifting cost/bbl"),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "receita_usd", td("monthly_revenue"), "receita_usd")
    by_tipo = custo.groupby("tipo_custo")["valor_usd"].sum().reset_index().sort_values("valor_usd")
    fig_custo = px.bar(by_tipo, x="valor_usd", y="tipo_custo", orientation="h",
                       labels={"valor_usd": "Valor (US$)", "tipo_custo": ""})
    fig_custo.update_traces(marker_color=_ACCENT)
    _base_layout(fig_custo, td("volume_by_type"))
    _section("distribution")
    _chart_row([(fig_mes, 3), (fig_custo, 2)])


# ── 🏛️ GOVERNO & SETOR PÚBLICO ────────────────────────────────────────────────
def _dash_governo(tabelas):
    fato = tabelas["FatoDespesa"]; orgao = tabelas["DimOrgao"]
    pago = fato["valor_pago"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_volume"),   f"R$ {_fmt_num(pago, 0)}",                                  f"{_fmt_num(n, 0)} despesas"),
        (td("efficiency"),     f"{fato['execucao_pct'].mean():.1f}%",              "execução orçamentária"),
        (td("avg_value"),      f"R$ {_fmt_num(fato['valor_empenhado'].sum(), 0)}",         "total empenhado"),
        (td("score"),          f"R$ {_fmt_num(fato['valor_liquidado'].sum(), 0)}",         "total liquidado"),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "valor_pago", td("monthly_volume"), "valor_pago")
    by_tipo = fato.groupby("tipo_despesa")["valor_pago"].sum().reset_index().sort_values("valor_pago")
    fig_tipo = px.bar(by_tipo, x="valor_pago", y="tipo_despesa", orientation="h",
                      labels={"valor_pago": td("volume_brl"), "tipo_despesa": ""})
    fig_tipo.update_traces(marker_color=_ACCENT)
    _base_layout(fig_tipo, td("volume_by_type"))
    _section("distribution")
    _chart_row([(fig_mes, 3), (fig_tipo, 2)])
    rec = tabelas["FatoReceita"]
    by_fonte = rec.groupby("fonte_receita")["valor_arrecadado"].sum().reset_index()
    fig_fonte = px.pie(by_fonte, names="fonte_receita", values="valor_arrecadado", hole=0.55, color_discrete_sequence=_PALETTE)
    _base_layout(fig_fonte, "Arrecadação por Fonte")
    st.plotly_chart(fig_fonte, use_container_width=True, config={"displayModeBar": False})


# ── 🍔 ALIMENTOS & BEBIDAS ────────────────────────────────────────────────────
def _dash_alimenticio(tabelas):
    fato = tabelas["FatoProducao"]; produto = tabelas["DimProduto"]; planta = tabelas["DimPlanta"]
    receita = fato["receita"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),    f"R$ {_fmt_num(receita, 0)}",                               f"{_fmt_num(n, 0)} lotes"),
        (td("total_production"), f"{_fmt_num(fato['volume_produzido_kg'].sum(), 0)} kg",      td("production_sub")),
        (td("efficiency"),       f"{100 - fato['indice_refugo_pct'].mean():.1f}%",   "aproveitamento"),
        (td("avg_cost"),         f"R$ {_fmt_num(fato['custo_producao'].mean(), 2)}",          "custo médio/lote"),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "receita", td("monthly_revenue"), "receita")
    merged = fato.merge(produto[["id_produto","categoria"]], on="id_produto", how="left")
    by_cat = merged.groupby("categoria")["receita"].sum().reset_index().sort_values("receita").tail(10)
    fig_cat = px.bar(by_cat, x="receita", y="categoria", orientation="h",
                     labels={"receita": td("revenue_brl"), "categoria": ""})
    fig_cat.update_traces(marker_color=_ACCENT)
    _base_layout(fig_cat, td("revenue_by_category"))
    _section("distribution")
    _chart_row([(fig_mes, 3), (fig_cat, 2)])
    by_conf = fato["conformidade_anvisa"].value_counts().reset_index()
    by_conf.columns = ["conformidade", "count"]
    fig_conf = px.pie(by_conf, names="conformidade", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
    _base_layout(fig_conf, "Conformidade ANVISA")
    st.plotly_chart(fig_conf, use_container_width=True, config={"displayModeBar": False})


# ── 📲 MIGRAÇÃO CLARO BRASIL (PORTABILIDADE) ─────────────────────────────────
def _dash_portabilidade_claro(tabelas):
    fato = tabelas["FatoMigracao"]
    n_in  = int((fato["direcao"] == "IN").sum())
    n_out = int((fato["direcao"] == "OUT").sum())
    saldo = n_in - n_out
    receita_liquida = fato["receita_liquida_mensal"].sum()

    _section("overview")
    _kpi_row([
        (td("migrations_in"),  f"{_fmt_num(n_in, 0)}",  td("gained_from_competitors")),
        (td("migrations_out"), f"{_fmt_num(n_out, 0)}", td("lost_to_competitors")),
        (td("net_balance"),    f"{saldo:+,}", td("in_minus_out")),
        (td("net_revenue"),    f"R$ {_fmt_num(receita_liquida, 0)}", td("mrr_impact")),
    ])

    fato2 = fato.copy()
    fato2["mes"] = pd.to_datetime(fato2["id_data"]).dt.to_period("M").astype(str)
    by_mes_dir = fato2.groupby(["mes", "direcao"]).size().reset_index(name="count")
    fig_mes = px.line(by_mes_dir, x="mes", y="count", color="direcao",
                      labels={"mes": "", "count": td("migrations_axis"), "direcao": ""},
                      color_discrete_map={"IN": "#4ade80", "OUT": "#f87171"}, markers=True)
    _base_layout(fig_mes, td("monthly_in_vs_out"))
    _chart_row([(fig_mes, 1)])

    _section("reasons_and_channels")
    out_reasons = (fato2[fato2["direcao"] == "OUT"]["motivo"]
                   .value_counts().reset_index().head(8))
    out_reasons.columns = ["motivo", "count"]
    fig_out = px.bar(out_reasons.sort_values("count"), x="count", y="motivo", orientation="h",
                     labels={"count": td("migrations_axis"), "motivo": ""},
                     color_discrete_sequence=["#f87171"])
    _base_layout(fig_out, td("top_out_reasons"))

    by_canal = fato2.groupby("canal").size().reset_index(name="count").sort_values("count", ascending=False)
    fig_canal = px.bar(by_canal, x="canal", y="count",
                       labels={"canal": "", "count": td("migrations_axis")},
                       color_discrete_sequence=[_ACCENT])
    _base_layout(fig_canal, td("migrations_by_channel"))
    _chart_row([(fig_out, 3), (fig_canal, 2)])

    _section("services_and_regions")
    by_srv = fato2.groupby(["categoria_servico", "direcao"]).size().reset_index(name="count")
    fig_srv = px.bar(by_srv, x="categoria_servico", y="count", color="direcao", barmode="group",
                     labels={"categoria_servico": "", "count": td("migrations_axis"), "direcao": ""},
                     color_discrete_map={"IN": "#4ade80", "OUT": "#f87171"})
    _base_layout(fig_srv, td("migrations_by_service"))

    by_uf = fato2.groupby("uf").size().reset_index(name="count").sort_values("count", ascending=False).head(10)
    fig_uf = px.bar(by_uf, x="uf", y="count",
                    labels={"uf": "", "count": td("migrations_axis")},
                    color="count", color_continuous_scale=["#16233F","#B8862E"])
    fig_uf.update_layout(coloraxis_showscale=False)
    _base_layout(fig_uf, td("migrations_by_state"))
    _chart_row([(fig_srv, 3), (fig_uf, 2)])


# ── ✈️ AVIAÇÃO CIVIL ──────────────────────────────────────────────────────────
def _dash_aviacao(tabelas):
    fato = tabelas["FatoBilhete"]; aeroporto = tabelas["DimAeroporto"]
    n = len(fato)
    on_time = fato["status_voo"].isin(["No Horário", "Antecipado"]).mean() * 100
    atrasados = fato[fato["status_voo"] == "Atrasado"]

    _section("overview")
    _kpi_row([
        (td("total_flights"),        f"{_fmt_num(n, 0)}",                                    td("issued_tickets")),
        (td("on_time_rate"),         f"{on_time:.1f}%",                            td("on_time_or_early")),
        (td("avg_delay"),            f"{atrasados['atraso_min'].mean():.0f} min" if len(atrasados) else "0 min", td("among_delayed")),
        (td("total_ticket_revenue"), f"R$ {_fmt_num(fato['valor_passagem'].sum(), 0)}",    td("avg_per_ticket")),
    ])

    by_status = fato["status_voo"].value_counts().reset_index()
    by_status.columns = ["status", "count"]
    fig_status = px.pie(by_status, names="status", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
    fig_status.update_traces(textfont_color=_INK)
    _base_layout(fig_status, td("flights_by_status"))

    merged = fato.merge(aeroporto[["id_aeroporto", "codigo_iata"]],
                         left_on="id_aeroporto_origem", right_on="id_aeroporto", how="left")
    by_rota = merged.groupby("codigo_iata").size().reset_index(name="count").sort_values("count", ascending=False).head(10)
    fig_rota = px.bar(by_rota, x="codigo_iata", y="count",
                      labels={"codigo_iata": "", "count": td("flights_axis")},
                      color_discrete_sequence=[_ACCENT])
    _base_layout(fig_rota, td("top_routes"))
    _chart_row([(fig_status, 2), (fig_rota, 3)])

    _section("routes_and_classes")
    by_classe = fato.groupby("classe_cabine")["valor_passagem"].sum().reset_index().sort_values("valor_passagem")
    fig_classe = px.bar(by_classe, x="valor_passagem", y="classe_cabine", orientation="h",
                        labels={"valor_passagem": td("total_ticket_revenue"), "classe_cabine": ""},
                        color_discrete_sequence=[_ACCENT])
    _base_layout(fig_classe, td("tickets_by_cabin_class"))
    _chart_row([(fig_classe, 1)])


# ── 🐾 PET & VETERINÁRIA ──────────────────────────────────────────────────────
def _dash_pet(tabelas):
    fato = tabelas["FatoAtendimento"]; pet = tabelas["DimPet"]
    n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_appointments"), f"{_fmt_num(n, 0)}",                                 td("appointments_sub")),
        (td("avg_ticket_pet"),     f"R$ {_fmt_num(fato['valor_cobrado'].mean(), 2)}", td("per_appointment")),
        (td("return_rate"),        f"{fato['retorno_necessario'].mean()*100:.1f}%", td("need_follow_up")),
        (td("avg_rating"),         f"{fato['nota_avaliacao'].mean():.1f}/5",  td("out_of_5")),
    ])

    by_cat = fato.groupby("categoria_servico")["valor_cobrado"].sum().reset_index().sort_values("valor_cobrado")
    fig_cat = px.bar(by_cat, x="valor_cobrado", y="categoria_servico", orientation="h",
                     labels={"valor_cobrado": td("total_revenue"), "categoria_servico": ""},
                     color_discrete_sequence=[_ACCENT])
    _base_layout(fig_cat, td("revenue_by_category"))

    merged = fato.merge(pet[["id_pet", "especie"]], on="id_pet", how="left")
    by_esp = merged.groupby("especie").size().reset_index(name="count").sort_values("count", ascending=False)
    fig_esp = px.bar(by_esp, x="especie", y="count",
                     labels={"especie": "", "count": td("appointments_sub")},
                     color_discrete_sequence=[_ACCENT])
    _base_layout(fig_esp, td("appointments_by_species"))
    _chart_row([(fig_cat, 3), (fig_esp, 2)])

    _section("species_and_payments")
    by_pag = fato["forma_pagamento"].value_counts().reset_index()
    by_pag.columns = ["forma", "count"]
    fig_pag = px.pie(by_pag, names="forma", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
    fig_pag.update_traces(textfont_color=_INK)
    _base_layout(fig_pag, td("payment_methods"))
    _chart_row([(fig_pag, 1)])


# ── 🎮 GAMES & ESPORTS ────────────────────────────────────────────────────────
def _dash_games(tabelas):
    fato = tabelas["FatoSessao"]; jogo = tabelas["DimJogo"]
    n = len(fato)
    taxa_compra = (fato["valor_gasto_loja"] > 0).mean() * 100
    _section("overview")
    _kpi_row([
        (td("total_sessions"),       f"{_fmt_num(n, 0)}",                                     td("sessions_sub")),
        (td("avg_session_duration"), f"{fato['duracao_min'].mean():.0f} min",       td("per_session")),
        (td("monetization_revenue"), f"R$ {_fmt_num(fato['valor_gasto_loja'].sum(), 0)}",   td("store_purchases")),
        (td("purchase_rate"),        f"{taxa_compra:.1f}%",                        td("of_sessions")),
    ])

    merged = fato.merge(jogo[["id_jogo", "nome_jogo"]], on="id_jogo", how="left")
    by_jogo = merged.groupby("nome_jogo").size().reset_index(name="count").sort_values("count", ascending=False)
    fig_jogo = px.bar(by_jogo, x="count", y="nome_jogo", orientation="h",
                      labels={"count": td("sessions_axis"), "nome_jogo": ""},
                      color_discrete_sequence=[_ACCENT])
    _base_layout(fig_jogo, td("sessions_by_game"))

    by_plat = fato.groupby("plataforma")["valor_gasto_loja"].sum().reset_index().sort_values("valor_gasto_loja", ascending=False)
    fig_plat = px.pie(by_plat, names="plataforma", values="valor_gasto_loja", hole=0.55, color_discrete_sequence=_PALETTE)
    fig_plat.update_traces(textfont_color=_INK)
    _base_layout(fig_plat, td("revenue_by_platform"))
    _chart_row([(fig_jogo, 3), (fig_plat, 2)])

    _section("platforms_and_events")
    by_evento = fato.groupby("tipo_evento").size().reset_index(name="count").sort_values("count", ascending=False)
    fig_evento = px.bar(by_evento, x="tipo_evento", y="count",
                        labels={"tipo_evento": "", "count": td("sessions_axis")},
                        color_discrete_sequence=[_ACCENT])
    _base_layout(fig_evento, td("sessions_by_event_type"))
    _chart_row([(fig_evento, 1)])


# ── 💧 SANEAMENTO & ÁGUA ──────────────────────────────────────────────────────
def _dash_saneamento(tabelas):
    fato = tabelas["FatoConsumo"]
    _section("overview")
    _kpi_row([
        (td("total_water_consumption"), f"{_fmt_num(fato['consumo_agua_m3'].sum(), 0)} m³", td("readings_sub")),
        (td("total_billing_water"),     f"R$ {_fmt_num(fato['valor_fatura'].sum(), 0)}",    td("all_invoices")),
        (td("default_rate"),            f"{fato['status_pagamento'].isin(['Vencido','Em Aberto']).mean()*100:.1f}%", td("overdue_or_open")),
        (td("avg_loss_index"),          f"{fato['indice_perdas_pct'].mean():.1f}%", td("network_leakage")),
    ])

    fig_mes = _monthly_chart(fato, "id_data", "consumo_agua_m3", td("monthly_consumption_water"), "consumo_agua_m3")

    by_lig = fato.groupby("tipo_ligacao")["consumo_agua_m3"].sum().reset_index().sort_values("consumo_agua_m3")
    fig_lig = px.bar(by_lig, x="consumo_agua_m3", y="tipo_ligacao", orientation="h",
                     labels={"consumo_agua_m3": td("total_water_consumption"), "tipo_ligacao": ""},
                     color_discrete_sequence=[_ACCENT])
    _base_layout(fig_lig, td("consumption_by_connection"))
    _chart_row([(fig_mes, 3), (fig_lig, 2)])

    _section("connections_and_payments")
    by_status = fato["status_pagamento"].value_counts().reset_index()
    by_status.columns = ["status", "count"]
    fig_status = px.pie(by_status, names="status", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
    fig_status.update_traces(textfont_color=_INK)
    _base_layout(fig_status, td("payment_status"))
    _chart_row([(fig_status, 1)])


# ════════════════════════════════════════════════════════════════════════════
#  DISPATCHER — deve ficar APÓS todas as funções _dash_*
# ════════════════════════════════════════════════════════════════════════════
_DASHBOARDS = {
    # Originais
    "Varejo":                    _dash_varejo,
    "Financeiro":                _dash_financeiro,
    "Saúde":                     _dash_saude,
    "Tecnologia":                _dash_tecnologia,
    "Educação":                  _dash_educacao,
    "Logística":                 _dash_logistica,
    "Energia":                   _dash_energia,
    "Telecom":                   _dash_telecom,
    "Indústria":                 _dash_industria,
    "Agronegócio":               _dash_agronegocio,
    "Turismo":                   _dash_turismo,
    "Imobiliário":               _dash_imobiliario,
    "Seguros":                   _dash_seguros,
    "Construção Civil":          _dash_construcao,
    # Novos
    "Hotelaria":                 _dash_hotelaria,
    "Streaming":                 _dash_streaming,
    "E-commerce":                _dash_ecommerce,
    "Recursos Humanos":          _dash_rh,
    "Mobilidade":                _dash_mobilidade,
    "Fintech":                   _dash_fintech,
    "Mineração":                 _dash_mineracao,
    "Jurídico":                  _dash_juridico,
    "Esportes":                  _dash_esportes,
    "SaaS B2B":                  _dash_saas_b2b,
    "CRM":                       _dash_crm,
    "Farmacêutico":              _dash_farmaceutico,
    "Marketing Digital":         _dash_marketing,
    "Petróleo & Gás":            _dash_petroleo,
    "Governo & Setor Público":   _dash_governo,
    "Alimentos & Bebidas":       _dash_alimenticio,
    "Migração Claro Brasil (Portabilidade)": _dash_portabilidade_claro,
    "Aviação Civil":             _dash_aviacao,
    "Pet & Veterinária":         _dash_pet,
    "Games & eSports":           _dash_games,
    "Saneamento & Água":         _dash_saneamento,
}


def _dash_generico(nome: str, tabelas: dict) -> None:
    """
    Dashboard genérico para setores sem dashboard específico.
    Renderiza KPIs e gráficos automaticamente com base nas tabelas disponíveis.
    """
    from i18n import get_lang, td
    lang = get_lang()

    fato_key = next((k for k in tabelas if k.startswith("Fato")), None)
    if fato_key is None:
        st.info("📦 Dados gerados com sucesso. Baixe o ZIP para usar no Power BI ou Tableau.")
        return

    fato = tabelas[fato_key]
    num_cols = fato.select_dtypes("number").columns.tolist()
    date_cols = [c for c in fato.columns if "data" in c.lower() or "date" in c.lower()]
    val_col = next((c for c in num_cols if any(k in c for k in
                    ["valor","receita","preco","total","mrr","custo","faturamento"])),
                   num_cols[0] if num_cols else None)

    # KPIs automáticos
    _section("overview")
    kpis = []
    if val_col:
        kpis.append((td("total_revenue"), f"R$ {_fmt_num(fato[val_col].sum(), 2)}", f"{_fmt_num(len(fato), 0)} registros"))
    if len(num_cols) > 1:
        col2 = next((c for c in num_cols if c != val_col), None)
        if col2:
            kpis.append((col2.replace("_"," ").title(), f"{_fmt_num(fato[col2].mean(), 2)}", "média"))
    bool_cols = [c for c in fato.columns if fato[c].dtype == bool]
    if bool_cols:
        kpis.append((bool_cols[0].replace("_"," ").title(),
                     f"{fato[bool_cols[0]].mean()*100:.1f}%", "taxa"))
    kpis.append(("Registros", f"{_fmt_num(len(fato), 0)}", fato_key))
    _kpi_row(kpis[:4])

    # Gráfico de linha mensal
    if val_col and date_cols:
        fig_mes = _monthly_chart(
            fato, date_cols[0], val_col,
            f"{val_col.replace('_',' ').title()} por Mês" if lang == "pt"
            else f"{val_col.replace('_',' ').title()} by Month",
            val_col.replace("_", " ").title(),
        )
        st.plotly_chart(fig_mes, use_container_width=True, config={"displayModeBar": False})

    # Tabela de dimensões disponíveis
    dim_keys = [k for k in tabelas if k.startswith("Dim")]
    if dim_keys:
        _section("segmentation")
        col_cat = next((c for k in dim_keys for c in tabelas[k].columns
                        if c.lower() in ["nome","name","tipo","type","categoria","category"]), None)
        if col_cat and val_col:
            dim_key = next(k for k in dim_keys if col_cat in tabelas[k].columns)
            pk = tabelas[dim_key].columns[0]
            fk = next((c for c in fato.columns if pk in c or c in pk), None)
            if fk:
                merged = fato.merge(tabelas[dim_key][[pk, col_cat]], left_on=fk, right_on=pk, how="left")
                by_cat = merged.groupby(col_cat)[val_col].sum().reset_index().sort_values(val_col).tail(10)
                fig_cat = px.bar(by_cat, x=val_col, y=col_cat, orientation="h",
                                 labels={val_col: "", col_cat: ""})
                fig_cat.update_traces(marker_color=_ACCENT)
                _base_layout(fig_cat, f"Top 10 por {col_cat.replace('_',' ').title()}")
                st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False})


def render_dashboard(nome: str, tabelas: dict) -> None:
    """
    Dispatcher de dashboards.
    1. Busca dashboard específico pelo nome PT
    2. Fallback: dashboard genérico que se adapta a qualquer tabela

    Todo o conteúdo é renderizado dentro de um container com key="dash_paper",
    que o styles/css.py estiliza no formato "documento/papel" (ver .st-key-dash_paper).
    """
    from i18n import get_lang, resolve_sector_name as _rsn

    pt_name = _rsn(nome)
    fn = _DASHBOARDS.get(pt_name) or _DASHBOARDS.get(nome)

    with st.container(key="dash_paper"):
        _dashboard_header(nome, tabelas)
        tabelas_filtradas = _filtro_ano(tabelas)
        if fn is not None:
            try:
                fn(tabelas_filtradas)
            except KeyError as e:
                # Tabela esperada não existe — usa dashboard genérico
                lang = get_lang()
                st.warning(f"{'Usando dashboard genérico — tabela' if lang == 'pt' else 'Using generic dashboard — table'} {e} {'não encontrada.' if lang == 'pt' else 'not found.'}")
                _dash_generico(nome, tabelas_filtradas)
        else:
            _dash_generico(nome, tabelas_filtradas)


# ════════════════════════════════════════════════════════════════════════════
#  DASHBOARDS — 16 NOVOS SETORES
# ════════════════════════════════════════════════════════════════════════════

# ── 👗 MODA & VESTUÁRIO ───────────────────────────────────────────────────
def _dash_moda(tabelas):
    fato = tabelas["FatoVenda"]; est = tabelas["FatoEstoque"]
    receita = fato["valor_total"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),   f"R$ {_fmt_num(receita, 0)}",                          f"{_fmt_num(n, 0)} {td('sales')}"),
        (td("avg_ticket"),      f"R$ {_fmt_num(fato['valor_total'].mean(), 2)}",        td("per_sale")),
        (td("avg_discount"),    f"{fato['desconto_pct'].mean():.1f}%",          td("on_full_price")),
        (td("efficiency"),      f"{(~fato['devolucao']).mean()*100:.1f}%",      "retenção"),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "valor_total", td("monthly_revenue"), "valor_total")

    by_canal = fato.groupby("canal")["valor_total"].sum().reset_index().sort_values("valor_total")
    fig_canal = px.bar(by_canal, x="valor_total", y="canal", orientation="h",
                       labels={"valor_total": td("revenue_brl"), "canal": ""})
    fig_canal.update_traces(marker_color=_ACCENT)
    _base_layout(fig_canal, td("revenue_by_channel"))
    _chart_row([(fig_mes, 3), (fig_canal, 2)])

    _section("distribution")
    by_cat = fato.groupby("tamanho")["valor_total"].sum().reset_index()
    fig_tam = px.pie(by_cat, names="tamanho", values="valor_total", hole=0.55,
                     color_discrete_sequence=_PALETTE)
    _base_layout(fig_tam, "Vendas por Tamanho")
    rup = est["ruptura"].mean() * 100
    by_ruptura = pd.DataFrame({"status": ["Com Estoque", "Ruptura"],
                                "pct":   [100 - rup, rup]})
    fig_rup = px.pie(by_ruptura, names="status", values="pct", hole=0.55,
                     color_discrete_sequence=_PALETTE)
    _base_layout(fig_rup, "Ruptura de Estoque")
    _chart_row([(fig_tam, 1), (fig_rup, 1)])


# ── 🎉 EVENTOS & ENTRETENIMENTO ───────────────────────────────────────────
def _dash_eventos(tabelas):
    fato = tabelas["FatoEvento"]; forn = tabelas["FatoFornecedor"]
    receita = fato["receita_total"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),   f"R$ {_fmt_num(receita, 0)}",                           f"{_fmt_num(n, 0)} eventos"),
        (td("avg_ticket"),      f"R$ {_fmt_num(fato['receita_total'].mean(), 0)}",       "receita média"),
        (td("efficiency"),      f"{fato['margem_pct'].mean():.1f}%",             "margem média"),
        (td("nps_scale"),       f"{fato['nps'].mean():.1f}",                     td("overall_avg")),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "receita_total", td("monthly_revenue"), "receita_total")

    dim_ev = tabelas["DimEvento"]
    by_tipo = fato.merge(dim_ev[["id_evento","tipo"]], on="id_evento", how="left")
    by_tipo = by_tipo.groupby("tipo")["receita_total"].sum().reset_index().sort_values("receita_total")
    fig_tipo = px.bar(by_tipo, x="receita_total", y="tipo", orientation="h",
                      labels={"receita_total": td("revenue_brl"), "tipo": ""})
    fig_tipo.update_traces(marker_color=_ACCENT)
    _base_layout(fig_tipo, td("revenue_by_category"))
    _chart_row([(fig_mes, 3), (fig_tipo, 2)])

    _section("distribution")
    by_forn = forn.groupby("tipo_fornecedor")["valor_contratado"].sum().reset_index()
    fig_forn = px.pie(by_forn, names="tipo_fornecedor", values="valor_contratado",
                      hole=0.55, color_discrete_sequence=_PALETTE)
    _base_layout(fig_forn, "Custo por Fornecedor")
    st.plotly_chart(fig_forn, use_container_width=True, config={"displayModeBar": False})


# ── 🔬 LABORATÓRIO & DIAGNÓSTICO ─────────────────────────────────────────
def _dash_laboratorio(tabelas):
    fato = tabelas["FatoExame"]
    receita = fato["valor_cobrado"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),   f"R$ {_fmt_num(receita, 0)}",                           f"{_fmt_num(n, 0)} exames"),
        (td("efficiency"),      f"{fato['dentro_prazo'].mean()*100:.1f}%",       td("within_deadline")),
        (td("avg_value"),       f"{fato['tempo_resposta_h'].mean():.1f}h",       "tempo médio"),
        (td("score"),           f"{fato['resultado_normal'].mean()*100:.1f}%",   "resultados normais"),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "valor_cobrado", td("monthly_revenue"), "valor_cobrado")

    by_conv = fato.groupby("convenio")["valor_cobrado"].sum().reset_index().sort_values("valor_cobrado")
    fig_conv = px.bar(by_conv, x="valor_cobrado", y="convenio", orientation="h",
                      labels={"valor_cobrado": td("revenue_brl"), "convenio": ""})
    fig_conv.update_traces(marker_color=_ACCENT)
    _base_layout(fig_conv, "Receita por Convênio")
    _chart_row([(fig_mes, 3), (fig_conv, 2)])

    _section("distribution")
    by_status = fato["status"].value_counts().reset_index()
    by_status.columns = ["status", "count"]
    fig_st = px.pie(by_status, names="status", values="count", hole=0.55,
                    color_discrete_sequence=_PALETTE)
    _base_layout(fig_st, td("status_dist"))
    st.plotly_chart(fig_st, use_container_width=True, config={"displayModeBar": False})


# ── 🏷️ FRANQUIAS ─────────────────────────────────────────────────────────
def _dash_franquias(tabelas):
    fato = tabelas["FatoDesempenho"]; taxa = tabelas["FatoTaxa"]
    fat = fato["faturamento"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),   f"R$ {_fmt_num(fat, 0)}",                               f"{_fmt_num(n, 0)} registros"),
        (td("avg_ticket"),      f"R$ {_fmt_num(fato['faturamento'].mean(), 0)}",         "faturamento médio"),
        (td("nps_scale"),       f"{fato['satisfacao_nps'].mean():.1f}",          td("overall_avg")),
        (td("efficiency"),      f"{fato['meta_atingida'].mean()*100:.1f}%",      "meta atingida"),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "faturamento", td("monthly_revenue"), "faturamento")

    dim_marc = tabelas["DimMarca"]
    by_marc = fato.merge(dim_marc[["id_marca","nome"]], on="id_marca", how="left")
    by_marc = by_marc.groupby("nome")["faturamento"].sum().reset_index().sort_values("faturamento").tail(10)
    fig_marc = px.bar(by_marc, x="faturamento", y="nome", orientation="h",
                      labels={"faturamento": td("revenue_brl"), "nome": ""})
    fig_marc.update_traces(marker_color=_ACCENT)
    _base_layout(fig_marc, "Top Marcas por Faturamento")
    _chart_row([(fig_mes, 3), (fig_marc, 2)])

    _section("distribution")
    by_taxa = taxa.groupby("tipo_taxa")["valor"].sum().reset_index()
    fig_taxa = px.pie(by_taxa, names="tipo_taxa", values="valor", hole=0.55,
                      color_discrete_sequence=_PALETTE)
    _base_layout(fig_taxa, "Distribuição de Taxas")
    st.plotly_chart(fig_taxa, use_container_width=True, config={"displayModeBar": False})


# ── 🏢 CONDOMÍNIO & FACILITIES ────────────────────────────────────────────
def _dash_condominio(tabelas):
    cota = tabelas["FatoCota"]; ocorr = tabelas["FatoOcorrencia"]; desp = tabelas["FatoDespesa"]
    arrecadado = cota[cota["pago"]]["valor_cota"].sum(); n = len(cota)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),   f"R$ {_fmt_num(arrecadado, 0)}",                        f"{_fmt_num(n, 0)} cotas"),
        (td("efficiency"),      f"{(~cota['inadimplente']).mean()*100:.1f}%",    "adimplência"),
        (td("avg_value"),       f"R$ {_fmt_num(desp['valor'].sum(), 0)}",               "total despesas"),
        (td("score"),           f"{_fmt_num(len(ocorr), 0)}",                              "ocorrências"),
    ])
    fig_mes = _monthly_chart(cota, "id_data", "valor_cota", "Arrecadação Mensal", "valor_cota")

    by_desp = desp.groupby("tipo_despesa")["valor"].sum().reset_index().sort_values("valor")
    fig_desp = px.bar(by_desp, x="valor", y="tipo_despesa", orientation="h",
                      labels={"valor": td("cost_brl"), "tipo_despesa": ""})
    fig_desp.update_traces(marker_color=_ACCENT)
    _base_layout(fig_desp, "Despesas por Tipo")
    _chart_row([(fig_mes, 3), (fig_desp, 2)])

    _section("distribution")
    by_ocorr = ocorr["tipo"].value_counts().reset_index()
    by_ocorr.columns = ["tipo", "count"]
    fig_oc = px.pie(by_ocorr, names="tipo", values="count", hole=0.55,
                    color_discrete_sequence=_PALETTE)
    _base_layout(fig_oc, "Ocorrências por Tipo")
    st.plotly_chart(fig_oc, use_container_width=True, config={"displayModeBar": False})


# ── 🧠 SAÚDE MENTAL ───────────────────────────────────────────────────────
def _dash_saude_mental(tabelas):
    fato = tabelas["FatoSessao"]
    receita = fato["valor_recebido"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),   f"R$ {_fmt_num(receita, 0)}",                           f"{_fmt_num(n, 0)} sessões"),
        (td("avg_ticket"),      f"R$ {_fmt_num(fato['valor_recebido'].mean(), 2)}",      "por sessão"),
        (td("efficiency"),      f"{(~fato['faltou']).mean()*100:.1f}%",          "presença"),
        (td("score"),           f"{fato['avaliacao'].mean():.2f}",               td("overall_avg")),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "valor_recebido", td("monthly_revenue"), "valor_recebido")

    by_modal = fato.groupby("modalidade")["valor_recebido"].sum().reset_index()
    fig_modal = px.pie(by_modal, names="modalidade", values="valor_recebido",
                       hole=0.55, color_discrete_sequence=_PALETTE)
    _base_layout(fig_modal, "Receita por Modalidade")
    _chart_row([(fig_mes, 3), (fig_modal, 2)])

    _section("distribution")
    by_status = fato["status"].value_counts().reset_index()
    by_status.columns = ["status", "count"]
    fig_st = px.pie(by_status, names="status", values="count", hole=0.55,
                    color_discrete_sequence=_PALETTE)
    _base_layout(fig_st, td("status_dist"))
    st.plotly_chart(fig_st, use_container_width=True, config={"displayModeBar": False})


# ── 🌲 FLORESTAL & PAPEL ─────────────────────────────────────────────────
def _dash_florestal(tabelas):
    fato = tabelas["FatoProducao"]
    receita = fato["receita"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),    f"R$ {_fmt_num(receita, 0)}",                          f"{_fmt_num(n, 0)} lotes"),
        (td("total_production"), f"{_fmt_num(fato['volume_m3'].sum(), 0)} m³",          "volume total"),
        (td("efficiency"),       f"{fato['produtividade_map'].mean():.1f}",      "MAP médio (m³/ha/ano)"),
        (td("score"),            f"{_fmt_num(fato['carbono_ton'].sum(), 0)} t",          "carbono sequestrado"),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "receita", td("monthly_revenue"), "receita")

    by_prod = fato.groupby("produto")["volume_m3"].sum().reset_index().sort_values("volume_m3")
    fig_prod = px.bar(by_prod, x="volume_m3", y="produto", orientation="h",
                      labels={"volume_m3": "Volume (m³)", "produto": ""})
    fig_prod.update_traces(marker_color=_ACCENT)
    _base_layout(fig_prod, "Volume por Produto")
    _chart_row([(fig_mes, 3), (fig_prod, 2)])

    _section("distribution")
    by_manejo = fato.groupby("tipo_manejo")["receita"].sum().reset_index()
    fig_manejo = px.pie(by_manejo, names="tipo_manejo", values="receita",
                        hole=0.55, color_discrete_sequence=_PALETTE)
    _base_layout(fig_manejo, "Receita por Tipo de Manejo")
    st.plotly_chart(fig_manejo, use_container_width=True, config={"displayModeBar": False})


# ── 🦄 STARTUPS & VENTURE CAPITAL ────────────────────────────────────────
def _dash_startup(tabelas):
    rodada = tabelas["FatoRodada"]; metrica = tabelas["FatoMetrica"]
    captado = rodada["valor_captado"].sum(); n = len(rodada)
    _section("overview")
    _kpi_row([
        (td("total_volume"),    f"R$ {_fmt_num(captado, 0)}",                           f"{_fmt_num(n, 0)} rodadas"),
        (td("avg_ticket"),      f"R$ {_fmt_num(rodada['valuation_post'].mean(), 0)}",    "valuation médio"),
        (td("total_mrr"),       f"R$ {_fmt_num(metrica['mrr'].mean(), 0)}",             "MRR médio"),
        (td("efficiency"),      f"{metrica['churn_pct'].mean():.1f}%",          "churn médio"),
    ])
    fig_mes = _monthly_chart(rodada, "id_data", "valor_captado", "Captação Mensal", "valor_captado")

    by_est = rodada.groupby("estagio")["valor_captado"].sum().reset_index()
    fig_est = px.pie(by_est, names="estagio", values="valor_captado",
                     hole=0.55, color_discrete_sequence=_PALETTE)
    _base_layout(fig_est, "Captação por Estágio")
    _chart_row([(fig_mes, 3), (fig_est, 2)])

    _section("distribution")
    fig_mrr = _monthly_chart(metrica, "id_data", "mrr", td("mrr_by_month"), "mrr")
    st.plotly_chart(fig_mrr, use_container_width=True, config={"displayModeBar": False})


# ── 🎬 AUDIOVISUAL & PRODUTORA ────────────────────────────────────────────
def _dash_audiovisual(tabelas):
    fato = tabelas["FatoProducao"]
    receita = fato["receita"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),   f"R$ {_fmt_num(receita, 0)}",                           f"{_fmt_num(n, 0)} produções"),
        (td("avg_cost"),        f"R$ {_fmt_num(fato['custo_realizado'].mean(), 0)}",     "custo médio"),
        (td("efficiency"),      f"{fato['roi_pct'].mean():.1f}%",               "ROI médio"),
        (td("score"),           f"{_fmt_num(fato['views_total'].sum(), 0)}",            "views totais"),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "receita", td("monthly_revenue"), "receita")

    by_dept = fato.groupby("departamento")["custo_realizado"].sum().reset_index().sort_values("custo_realizado")
    fig_dept = px.bar(by_dept, x="custo_realizado", y="departamento", orientation="h",
                      labels={"custo_realizado": td("cost_brl"), "departamento": ""})
    fig_dept.update_traces(marker_color=_ACCENT)
    _base_layout(fig_dept, "Custo por Departamento")
    _chart_row([(fig_mes, 3), (fig_dept, 2)])

    _section("distribution")
    by_views = _by_month(fato, "id_data", "views_total")
    fig_views = px.bar(by_views, x="mes", y="views_total",
                       labels={"mes":"","views_total":"Views"})
    fig_views.update_traces(marker_color=_ACCENT)
    _base_layout(fig_views, "Views por Mês")
    st.plotly_chart(fig_views, use_container_width=True, config={"displayModeBar": False})


# ── 🐟 PESCA & AQUICULTURA ────────────────────────────────────────────────
def _dash_pesca(tabelas):
    fato = tabelas["FatoProducao"]
    receita = fato["receita"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),    f"R$ {_fmt_num(receita, 0)}",                          f"{_fmt_num(n, 0)} lotes"),
        (td("total_production"), f"{_fmt_num(fato['peso_kg'].sum(), 0)} kg",            "biomassa total"),
        (td("efficiency"),       f"{fato['fcr_real'].mean():.2f}",              "FCR médio"),
        (td("score"),            f"{fato['mortalidade_pct'].mean():.1f}%",      "mortalidade média"),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "receita", td("monthly_revenue"), "receita")

    dim_esp = tabelas["DimEspecie"]
    by_esp = fato.merge(dim_esp[["id_especie","nome"]], on="id_especie", how="left")
    by_esp = by_esp.groupby("nome")["peso_kg"].sum().reset_index().sort_values("peso_kg")
    fig_esp = px.bar(by_esp, x="peso_kg", y="nome", orientation="h",
                     labels={"peso_kg": "Biomassa (kg)", "nome": ""})
    fig_esp.update_traces(marker_color=_ACCENT)
    _base_layout(fig_esp, "Biomassa por Espécie")
    _chart_row([(fig_mes, 3), (fig_esp, 2)])

    _section("distribution")
    by_dest = fato.groupby("destino")["receita"].sum().reset_index()
    fig_dest = px.pie(by_dest, names="destino", values="receita",
                      hole=0.55, color_discrete_sequence=_PALETTE)
    _base_layout(fig_dest, "Receita por Destino")
    st.plotly_chart(fig_dest, use_container_width=True, config={"displayModeBar": False})


# ── 🧵 TÊXTIL & CONFECÇÃO ────────────────────────────────────────────────
def _dash_textil(tabelas):
    fato = tabelas["FatoProducao"]
    receita = fato["receita"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),    f"R$ {_fmt_num(receita, 0)}",                          f"{_fmt_num(n, 0)} lotes"),
        (td("total_production"), f"{_fmt_num(fato['volume_kg'].sum(), 0)} kg",          "volume produzido"),
        (td("efficiency"),       f"{fato['eficiencia_pct'].mean():.1f}%",       "eficiência média"),
        (td("score"),            f"{fato['refugo_pct'].mean():.1f}%",           "refugo médio"),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "receita", td("monthly_revenue"), "receita")

    by_proc = fato.groupby("processo")["volume_kg"].sum().reset_index().sort_values("volume_kg")
    fig_proc = px.bar(by_proc, x="volume_kg", y="processo", orientation="h",
                      labels={"volume_kg": "Volume (kg)", "processo": ""})
    fig_proc.update_traces(marker_color=_ACCENT)
    _base_layout(fig_proc, "Volume por Processo")
    _chart_row([(fig_mes, 3), (fig_proc, 2)])

    _section("distribution")
    fig_efi = px.histogram(fato, x="eficiencia_pct", nbins=20,
                           color_discrete_sequence=[_ACCENT],
                           labels={"eficiencia_pct": td("efficiency")})
    _base_layout(fig_efi, "Distribuição de Eficiência")
    st.plotly_chart(fig_efi, use_container_width=True, config={"displayModeBar": False})


# ── 🏛️ ARQUITETURA & DESIGN ──────────────────────────────────────────────
def _dash_arquitetura(tabelas):
    fato = tabelas["FatoServico"]
    receita = fato["valor_total"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),   f"R$ {_fmt_num(receita, 0)}",                           f"{_fmt_num(n, 0)} serviços"),
        (td("avg_ticket"),      f"R$ {_fmt_num(fato['valor_hora'].mean(), 2)}",         "valor/hora médio"),
        (td("efficiency"),      f"{fato['aprovado_cliente'].mean()*100:.1f}%",  "aprovação cliente"),
        (td("score"),           f"{fato['retrabalho'].mean()*100:.1f}%",        "taxa retrabalho"),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "valor_total", td("monthly_revenue"), "valor_total")

    by_serv = fato.groupby("tipo_servico")["valor_total"].sum().reset_index().sort_values("valor_total")
    fig_serv = px.bar(by_serv, x="valor_total", y="tipo_servico", orientation="h",
                      labels={"valor_total": td("revenue_brl"), "tipo_servico": ""})
    fig_serv.update_traces(marker_color=_ACCENT)
    _base_layout(fig_serv, "Receita por Serviço")
    _chart_row([(fig_mes, 3), (fig_serv, 2)])

    _section("distribution")
    dim_proj = tabelas["DimProjeto"]
    by_tipo = dim_proj["tipo"].value_counts().reset_index()
    by_tipo.columns = ["tipo", "count"]
    fig_tipo = px.pie(by_tipo, names="tipo", values="count",
                      hole=0.55, color_discrete_sequence=_PALETTE)
    _base_layout(fig_tipo, "Projetos por Tipo")
    st.plotly_chart(fig_tipo, use_container_width=True, config={"displayModeBar": False})


# ── ✈️ VIAGENS CORPORATIVAS ───────────────────────────────────────────────
def _dash_viagem_corp(tabelas):
    fato = tabelas["FatoViagem"]
    custo = fato["custo_total"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_volume"),    f"R$ {_fmt_num(custo, 0)}",                             f"{_fmt_num(n, 0)} viagens"),
        (td("avg_cost"),        f"R$ {_fmt_num(fato['custo_total'].mean(), 2)}",        "custo médio"),
        (td("efficiency"),      f"{(fato['politica']=='Dentro da política').mean()*100:.1f}%", "dentro da política"),
        (td("score"),           f"{fato['nps_viajante'].mean():.1f}",           "NPS viajante"),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "custo_total", td("monthly_costs"), "custo_total")

    dim_viaj = tabelas["DimViajante"]
    by_dept = fato.merge(dim_viaj[["id_viajante","departamento"]], on="id_viajante", how="left")
    by_dept = by_dept.groupby("departamento")["custo_total"].sum().reset_index().sort_values("custo_total")
    fig_dept = px.bar(by_dept, x="custo_total", y="departamento", orientation="h",
                      labels={"custo_total": td("cost_brl"), "departamento": ""})
    fig_dept.update_traces(marker_color=_ACCENT)
    _base_layout(fig_dept, "Custo por Departamento")
    _chart_row([(fig_mes, 3), (fig_dept, 2)])

    _section("distribution")
    by_motivo = fato.groupby("motivo")["custo_total"].sum().reset_index()
    fig_mot = px.pie(by_motivo, names="motivo", values="custo_total",
                     hole=0.55, color_discrete_sequence=_PALETTE)
    _base_layout(fig_mot, "Custo por Motivo de Viagem")
    st.plotly_chart(fig_mot, use_container_width=True, config={"displayModeBar": False})


# ── 🚀 ESPACIAL & AEROESPACIAL ────────────────────────────────────────────
def _dash_espacial(tabelas):
    fato = tabelas["FatoOperacao"]
    custo = fato["custo_realizado"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_volume"),    f"US$ {custo/1e9:.2f}B",                        f"{_fmt_num(n, 0)} operações"),
        (td("efficiency"),      f"{fato['disponibilidade_pct'].mean():.2f}%",   "disponibilidade"),
        (td("score"),           f"{_fmt_num(fato['anomalias'].sum(), 0)}",                 "anomalias totais"),
        (td("avg_value"),       f"{_fmt_num(fato['dados_coletados_gb'].sum(), 0)} GB",  "dados coletados"),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "custo_realizado", "Custo Mensal de Operações", "custo_realizado")

    dim_miss = tabelas["DimMissao"]
    by_tipo = dim_miss.groupby("tipo")["orcamento_mi"].sum().reset_index().sort_values("orcamento_mi")
    fig_tipo = px.bar(by_tipo, x="orcamento_mi", y="tipo", orientation="h",
                      labels={"orcamento_mi": "Orçamento (mi US$)", "tipo": ""})
    fig_tipo.update_traces(marker_color=_ACCENT)
    _base_layout(fig_tipo, "Orçamento por Tipo de Missão")
    _chart_row([(fig_mes, 3), (fig_tipo, 2)])

    _section("distribution")
    by_seg = dim_miss["segmento"].value_counts().reset_index()
    by_seg.columns = ["segmento", "count"]
    fig_seg = px.pie(by_seg, names="segmento", values="count",
                     hole=0.55, color_discrete_sequence=_PALETTE)
    _base_layout(fig_seg, "Missões por Segmento")
    st.plotly_chart(fig_seg, use_container_width=True, config={"displayModeBar": False})


# ── 💄 BELEZA & ESTÉTICA ─────────────────────────────────────────────────
def _dash_beleza(tabelas):
    venda = tabelas["FatoVenda"]; agenda = tabelas["FatoAgenda"]
    receita = venda["valor_total"].sum() + agenda["valor_servico"].sum()
    n_venda = len(venda); n_ag = len(agenda)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),   f"R$ {_fmt_num(receita, 0)}",                           f"{_fmt_num(n_venda, 0)} vendas / {_fmt_num(n_ag, 0)} agendamentos"),
        (td("avg_ticket"),      f"R$ {_fmt_num(venda['valor_total'].mean(), 2)}",        "ticket médio venda"),
        (td("efficiency"),      f"{(agenda['status']=='Realizado').mean()*100:.1f}%", "taxa realização"),
        (td("score"),           f"{agenda['avaliacao'].mean():.2f}",            "avaliação média"),
    ])
    fig_mes = _monthly_chart(venda, "id_data", "valor_total", td("monthly_revenue"), "valor_total")

    by_canal = venda.groupby("canal")["valor_total"].sum().reset_index().sort_values("valor_total")
    fig_canal = px.bar(by_canal, x="valor_total", y="canal", orientation="h",
                       labels={"valor_total": td("revenue_brl"), "canal": ""})
    fig_canal.update_traces(marker_color=_ACCENT)
    _base_layout(fig_canal, td("revenue_by_channel"))
    _chart_row([(fig_mes, 3), (fig_canal, 2)])

    _section("segmentation")
    by_serv = agenda.groupby("servico")["valor_servico"].sum().reset_index().sort_values("valor_servico").tail(8)
    fig_serv = px.bar(by_serv, x="valor_servico", y="servico", orientation="h",
                      labels={"valor_servico": td("revenue_brl"), "servico": ""})
    fig_serv.update_traces(marker_color=_ACCENT)
    _base_layout(fig_serv, "Top Serviços por Receita")
    st.plotly_chart(fig_serv, use_container_width=True, config={"displayModeBar": False})


# ── 🚴 LOGÍSTICA URBANA ───────────────────────────────────────────────────
def _dash_logistica_urbana(tabelas):
    fato = tabelas["FatoEntrega"]
    frete = fato["valor_frete"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),   f"R$ {_fmt_num(frete, 0)}",                             f"{_fmt_num(n, 0)} entregas"),
        (td("efficiency"),      f"{(~fato['falha']).mean()*100:.1f}%",          "taxa de sucesso"),
        (td("avg_ticket"),      f"{fato['dentro_sla'].mean()*100:.1f}%",        "dentro do SLA"),
        (td("score"),           f"{fato['avaliacao'].mean():.2f}",              "avaliação média"),
    ])
    fig_mes = _monthly_chart(fato, "id_data", "valor_frete", td("monthly_revenue"), "valor_frete")

    by_status = fato["status"].value_counts().reset_index()
    by_status.columns = ["status", "count"]
    fig_st = px.pie(by_status, names="status", values="count",
                    hole=0.55, color_discrete_sequence=_PALETTE)
    _base_layout(fig_st, td("status_dist"))
    _chart_row([(fig_mes, 3), (fig_st, 2)])

    _section("distribution")
    falha_df = fato[fato["falha"] & (fato["motivo_falha"] != "N/A")]
    if len(falha_df):
        by_motivo = falha_df["motivo_falha"].value_counts().reset_index()
        by_motivo.columns = ["motivo", "count"]
        fig_mot = px.bar(by_motivo, x="count", y="motivo", orientation="h",
                         labels={"count": "Ocorrências", "motivo": ""})
        fig_mot.update_traces(marker_color=_ACCENT)
        _base_layout(fig_mot, "Motivos de Falha na Entrega")
        st.plotly_chart(fig_mot, use_container_width=True, config={"displayModeBar": False})

# Registra os 16 novos setores no dispatcher
# e aliases para compatibilidade com setores externos
_DASHBOARDS.update({
    "Moda & Vestuário":          _dash_moda,
    "Eventos & Entretenimento":  _dash_eventos,
    "Laboratório & Diagnóstico": _dash_laboratorio,
    "Franquias":                 _dash_franquias,
    "Condomínio & Facilities":   _dash_condominio,
    "Saúde Mental":              _dash_saude_mental,
    "Florestal & Papel":         _dash_florestal,
    "Startups & Venture Capital":_dash_startup,
    "Audiovisual & Produtora":   _dash_audiovisual,
    "Pesca & Aquicultura":       _dash_pesca,
    "Têxtil & Confecção":        _dash_textil,
    "Arquitetura & Design":      _dash_arquitetura,
    "Viagens Corporativas":      _dash_viagem_corp,
    "Espacial & Aeroespacial":   _dash_espacial,
    "Beleza & Estética":         _dash_beleza,
    "Logística Urbana":          _dash_logistica_urbana,
})
