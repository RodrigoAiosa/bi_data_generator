"""
ui/dashboard.py
Dashboard com KPIs e gráficos interativos por setor — com suporte a i18n.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from i18n import td, resolve_sector_name

_BG      = "rgba(0,0,0,0)"
_PAPER   = "rgba(0,0,0,0)"
_GRID    = "rgba(167,139,250,0.08)"
_TEXT    = "#7b8ba8"
_ACCENT  = "#a78bfa"
_PALETTE = ["#a78bfa","#7c3aed","#c4b5fd","#6d28d9","#ddd6fe","#4c1d95","#ede9fe"]


def _base_layout(fig, title=""):
    fig.update_layout(
        paper_bgcolor=_PAPER, plot_bgcolor=_BG,
        font=dict(family="DM Sans, sans-serif", color=_TEXT, size=12),
        title=dict(text=title, font=dict(color="#e2e8f0", size=14, family="Syne, sans-serif"), x=0.01),
        margin=dict(l=16, r=16, t=40 if title else 16, b=16),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=_TEXT)),
        colorway=_PALETTE,
    )
    fig.update_xaxes(gridcolor=_GRID, zeroline=False, tickfont=dict(color=_TEXT))
    fig.update_yaxes(gridcolor=_GRID, zeroline=False, tickfont=dict(color=_TEXT))
    return fig


def _metric(label, value, sub="", delta=""):
    delta_html = f'<span style="font-size:0.78rem;color:#4ade80;margin-top:4px;display:block;">▲ {delta}</span>' if delta else ""
    sub_html   = f'<span class="stat-sublabel">{sub}</span>' if sub else ""
    return f'<div class="stat-card"><span class="stat-number">{value}</span><span class="stat-label">{label}</span>{sub_html}{delta_html}</div>'


def _kpi_row(metrics):
    cols = st.columns(len(metrics))
    for col, args in zip(cols, metrics):
        with col:
            st.markdown(_metric(*args), unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:32px'></div>", unsafe_allow_html=True)


def _chart_row(figs):
    cols = st.columns([w for _, w in figs])
    for col, (fig, _) in zip(cols, figs):
        with col:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _section(key):
    st.markdown(f'<h3 class="section-header">{td(key)}</h3>', unsafe_allow_html=True)


def _by_month(df, date_col, val_col):
    d = df.copy()
    d["_m"] = pd.to_datetime(d[date_col]).dt.to_period("M").astype(str)
    return d.groupby("_m")[val_col].sum().reset_index().rename(columns={"_m": "mes"})


# ── 🛒 VAREJO ─────────────────────────────────────────────────────────────────
def _dash_varejo(tabelas):
    fato = tabelas["FatoVendas"]; produto = tabelas["DimProduto"]; vendedor = tabelas["DimVendedor"]
    receita = fato["valor_total"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"), f"R$ {receita:,.0f}",               f"{n:,} {td('sales')}"),
        (td("avg_ticket"),    f"R$ {fato['valor_total'].mean():,.2f}", td("per_sale")),
        (td("avg_discount"),  f"{fato['desconto'].mean()*100:.1f}%",   td("on_full_price")),
        (td("avg_qty"),       f"{fato['quantidade'].mean():.1f}",       td("units")),
    ])
    by_mes = _by_month(fato, "id_data", "valor_total")
    fig_mes = px.area(by_mes, x="mes", y="valor_total", labels={"mes":"","valor_total":td("revenue_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_revenue"))

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
    fig_canal.update_traces(textfont_color="#e2e8f0")
    _base_layout(fig_canal, td("revenue_by_channel"))

    top_v = (fato.groupby("id_vendedor")["valor_total"].sum().reset_index()
             .sort_values("valor_total",ascending=False).head(10)
             .merge(vendedor[["id_vendedor","nome"]], on="id_vendedor"))
    fig_vend = px.bar(top_v, x="valor_total", y="nome", orientation="h",
                      labels={"valor_total":td("revenue_brl"),"nome":""},
                      color="valor_total", color_continuous_scale=["#6d28d9","#a78bfa","#c4b5fd"])
    fig_vend.update_layout(coloraxis_showscale=False)
    _base_layout(fig_vend, td("top10_sellers"))
    _chart_row([(fig_canal,1),(fig_vend,2)])


# ── 💰 FINANCEIRO ─────────────────────────────────────────────────────────────
def _dash_financeiro(tabelas):
    fato = tabelas["FatoTransacao"]; produto = tabelas["DimProduto"]
    vol = fato["valor"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_volume"),   f"R$ {vol:,.0f}",                      f"{n:,} {td('transactions')}"),
        (td("approval_rate"),  f"{(fato['status']=='Aprovada').mean()*100:.1f}%", td("approved_tx")),
        (td("avg_value"),      f"R$ {fato['valor'].mean():,.2f}",      td("per_tx")),
        (td("avg_balance"),    f"R$ {fato['saldo_apos'].mean():,.0f}", td("after_tx")),
    ])
    by_mes = _by_month(fato, "id_data", "valor")
    fig_mes = px.area(by_mes, x="mes", y="valor", labels={"mes":"","valor":td("volume_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_volume"))

    by_tipo = fato.groupby("tipo")["valor"].sum().reset_index().sort_values("valor")
    fig_tipo = px.bar(by_tipo, x="valor", y="tipo", orientation="h",
                      labels={"valor":td("volume_brl"),"tipo":""},
                      color="valor", color_continuous_scale=["#6d28d9","#a78bfa"])
    fig_tipo.update_layout(coloraxis_showscale=False)
    _base_layout(fig_tipo, td("volume_by_type"))

    _section("distribution")
    _chart_row([(fig_mes,3),(fig_tipo,2)])

    by_status = fato["status"].value_counts().reset_index()
    fig_status = px.pie(by_status, names="status", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
    fig_status.update_traces(textfont_color="#e2e8f0")
    _base_layout(fig_status, td("status_dist"))

    merged = fato.merge(produto[["id_produto","categoria"]], on="id_produto")
    by_cat = merged.groupby("categoria")["valor"].sum().reset_index().sort_values("valor",ascending=False)
    fig_cat = px.bar(by_cat, x="categoria", y="valor",
                     labels={"valor":td("volume_brl"),"categoria":""},
                     color="valor", color_continuous_scale=["#6d28d9","#a78bfa","#c4b5fd"])
    fig_cat.update_layout(coloraxis_showscale=False)
    _base_layout(fig_cat, td("volume_by_product"))
    _chart_row([(fig_status,1),(fig_cat,2)])


# ── 🏥 SAÚDE ──────────────────────────────────────────────────────────────────
def _dash_saude(tabelas):
    fato = tabelas["FatoAtendimento"]; medico = tabelas["DimMedico"]; paciente = tabelas["DimPaciente"]
    receita = fato["valor_cobrado"].sum(); n = len(fato)
    _section("overview")
    _kpi_row([
        (td("total_revenue"),  f"R$ {receita:,.0f}",                     f"{n:,} {td('visits')}"),
        (td("discharge_rate"), f"{(fato['resultado']=='Alta').mean()*100:.1f}%", td("of_visits")),
        (td("avg_duration"),   f"{fato['duracao_min'].mean():.0f} min",   td("per_visit")),
        (td("avg_value"),      f"R$ {fato['valor_cobrado'].mean():,.2f}", td("per_visit")),
    ])
    by_mes = _by_month(fato, "id_data", "valor_cobrado")
    fato2 = fato.copy(); fato2["mes"] = pd.to_datetime(fato2["id_data"]).dt.to_period("M").astype(str)
    cnt_mes = fato2.groupby("mes").size().reset_index(name="count")
    fig_mes = px.area(cnt_mes, x="mes", y="count", labels={"mes":"","count":td("visits_axis")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_visits"))

    merged = fato.merge(medico[["id_medico","especialidade"]], on="id_medico")
    by_esp = merged.groupby("especialidade").size().reset_index(name="count").sort_values("count")
    fig_esp = px.bar(by_esp, x="count", y="especialidade", orientation="h",
                     labels={"count":td("visits_axis"),"especialidade":td("specialty")},
                     color="count", color_continuous_scale=["#6d28d9","#a78bfa"])
    fig_esp.update_layout(coloraxis_showscale=False)
    _base_layout(fig_esp, td("visits_by_specialty"))

    _section("results")
    _chart_row([(fig_mes,3),(fig_esp,2)])

    by_res = fato["resultado"].value_counts().reset_index()
    fig_res = px.pie(by_res, names="resultado", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
    fig_res.update_traces(textfont_color="#e2e8f0")
    _base_layout(fig_res, td("result_dist"))

    m2 = fato.merge(paciente[["id_paciente","convenio"]], on="id_paciente")
    by_conv = m2.groupby("convenio")["valor_cobrado"].sum().reset_index().sort_values("valor_cobrado",ascending=False)
    fig_conv = px.bar(by_conv, x="convenio", y="valor_cobrado",
                      labels={"valor_cobrado":td("revenue_brl"),"convenio":""},
                      color="valor_cobrado", color_continuous_scale=["#6d28d9","#a78bfa","#c4b5fd"])
    fig_conv.update_layout(coloraxis_showscale=False)
    _base_layout(fig_conv, td("revenue_by_plan"))
    _chart_row([(fig_res,1),(fig_conv,2)])


# ── 💻 TECNOLOGIA ─────────────────────────────────────────────────────────────
def _dash_tecnologia(tabelas):
    fato = tabelas["FatoContrato"]; cliente = tabelas["DimCliente"]
    _section("overview")
    _kpi_row([
        (td("total_mrr"),   f"R$ {fato['valor_mrr'].sum():,.0f}",  f"{len(fato):,} {td('contracts')}"),
        (td("total_arr"),   f"R$ {fato['arr'].sum():,.0f}",         td("arr_sub")),
        (td("avg_nps"),     f"{fato['nps'].mean():.1f}",             td("nps_scale")),
        (td("churn_rate"),  f"{(fato['tipo']=='Churn').mean()*100:.1f}%", td("of_contracts")),
    ])
    by_mes = _by_month(fato, "id_data", "valor_mrr")
    fig_mes = px.area(by_mes, x="mes", y="valor_mrr", labels={"mes":"","valor_mrr":"MRR (R$)"})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("mrr_by_month"))

    by_tipo = fato["tipo"].value_counts().reset_index()
    fig_tipo = px.pie(by_tipo, names="tipo", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
    fig_tipo.update_traces(textfont_color="#e2e8f0")
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
                     color="valor_mrr", color_continuous_scale=["#6d28d9","#a78bfa","#c4b5fd"])
    fig_seg.update_layout(coloraxis_showscale=False)
    _base_layout(fig_seg, td("mrr_by_segment"))
    _chart_row([(fig_nps,2),(fig_seg,3)])


# ── 📚 EDUCAÇÃO ───────────────────────────────────────────────────────────────
def _dash_educacao(tabelas):
    fato = tabelas["FatoMatricula"]; curso = tabelas["DimCurso"]
    _section("overview")
    _kpi_row([
        (td("total_revenue"),    f"R$ {fato['valor_pago'].sum():,.0f}",    f"{len(fato):,} {td('enrollments')}"),
        (td("completion_rate"),  f"{fato['concluiu'].mean()*100:.1f}%",     td("of_students")),
        (td("avg_grade"),        f"{fato['nota_final'].mean():.2f}",         td("nps_scale")),
        (td("avg_ticket"),       f"R$ {fato['valor_pago'].mean():,.2f}",    td("per_enrollment")),
    ])
    fato2 = fato.copy(); fato2["mes"] = pd.to_datetime(fato2["id_data"]).dt.to_period("M").astype(str)
    cnt = fato2.groupby("mes").size().reset_index(name="count")
    fig_mes = px.area(cnt, x="mes", y="count", labels={"mes":"","count":td("enrollments_axis")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_enrollments"))

    m1 = fato.merge(curso[["id_curso","modalidade"]], on="id_curso")
    by_mod = m1.groupby("modalidade").size().reset_index(name="count")
    fig_mod = px.pie(by_mod, names="modalidade", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
    fig_mod.update_traces(textfont_color="#e2e8f0")
    _base_layout(fig_mod, td("by_modality"))

    _section("area_performance")
    _chart_row([(fig_mes,3),(fig_mod,2)])

    m2 = fato.merge(curso[["id_curso","area"]], on="id_curso")
    by_area = m2.groupby("area")["valor_pago"].sum().reset_index().sort_values("valor_pago")
    fig_area = px.bar(by_area, x="valor_pago", y="area", orientation="h",
                      labels={"valor_pago":td("revenue_brl"),"area":td("area")},
                      color="valor_pago", color_continuous_scale=["#6d28d9","#a78bfa"])
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
        (td("freight_revenue"), f"R$ {frete_total:,.0f}",              f"{len(fato):,} {td('deliveries')}"),
        (td("avg_freight"),     f"R$ {fato['valor_frete'].mean():,.2f}",td("per_delivery")),
        (td("delivery_rate"),   f"{(fato['status']=='Entregue').mean()*100:.1f}%", td("completed")),
        (td("on_time"),         f"{(fato['dias_entregue']<=fato['prazo_acordado']).mean()*100:.1f}%", td("within_deadline")),
    ])
    by_mes = _by_month(fato, "id_data", "valor_frete")
    fig_mes = px.area(by_mes, x="mes", y="valor_frete", labels={"mes":"","valor_frete":td("revenue_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_freight"))

    by_status = fato["status"].value_counts().reset_index()
    fig_status = px.pie(by_status, names="status", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
    fig_status.update_traces(textfont_color="#e2e8f0")
    _base_layout(fig_status, td("delivery_status"))

    _section("carriers_routes")
    _chart_row([(fig_mes,3),(fig_status,2)])

    top_t = (fato.groupby("id_transportadora")["valor_frete"].sum().reset_index()
             .sort_values("valor_frete",ascending=False).head(10)
             .merge(trans[["id_transportadora","nome"]], on="id_transportadora"))
    fig_trans = px.bar(top_t, x="valor_frete", y="nome", orientation="h",
                       labels={"valor_frete":td("revenue_brl"),"nome":""},
                       color="valor_frete", color_continuous_scale=["#6d28d9","#a78bfa"])
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
        (td("total_consumption"), f"{fato['consumo_kwh'].sum():,.0f} kWh", f"{len(fato):,} {td('readings')}"),
        (td("total_billing"),     f"R$ {fato['valor_fatura'].sum():,.0f}",  td("all_bills")),
        (td("avg_bill"),          f"R$ {fato['valor_fatura'].mean():,.2f}", td("per_reading")),
        (td("power_factor"),      f"{fato['fator_potencia'].mean():.3f}",    td("overall_avg")),
    ])
    by_mes = _by_month(fato, "id_data", "consumo_kwh")
    fig_mes = px.area(by_mes, x="mes", y="consumo_kwh", labels={"mes":"","consumo_kwh":td("consumption_kwh")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_consumption"))

    merged = fato.merge(consumidor[["id_consumidor","classe"]], on="id_consumidor")
    by_cls = merged.groupby("classe")["consumo_kwh"].sum().reset_index().sort_values("consumo_kwh")
    fig_cls = px.bar(by_cls, x="consumo_kwh", y="classe", orientation="h",
                     labels={"consumo_kwh":td("consumption_kwh"),"classe":td("class_")},
                     color="consumo_kwh", color_continuous_scale=["#6d28d9","#a78bfa"])
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
    fig_fat.update_traces(textfont_color="#e2e8f0")
    _base_layout(fig_fat, td("revenue_by_class"))
    _chart_row([(fig_tar,3),(fig_fat,2)])


# ── 📡 TELECOM ────────────────────────────────────────────────────────────────
def _dash_telecom(tabelas):
    fato = tabelas["FatoChamada"]
    has_custo     = "custo" in fato.columns
    has_qualidade = "qualidade_sinal" in fato.columns
    _section("overview")
    metrics = [
        (td("total_calls"),   f"{len(fato):,}",                          td("in_period")),
        (td("avg_duration"),  f"{fato['duracao_seg'].mean():.1f}s",       td("per_call")),
    ]
    if has_custo:
        metrics.append((td("total_cost"), f"R$ {fato['custo'].sum():,.2f}", td("billed_calls")))
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
        (td("total_production"), f"{qtd_total:,.0f}", td("unit_plural")),
        (td("scrap_rate"),       f"{refugo_pct:.2f}%", td("loss")),
        (td("avg_oee"),          f"{fato[oee_col].mean()*100:.1f}%", td("global_efficiency")),
        (td("total_cost"),       f"R$ {fato[custo_col].sum():,.0f}", td("production_sub")),
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
        (td("total_revenue"), f"R$ {receita:,.0f}",                              f"{n_safras:,} safras"),
        (td("total_production") if "total_production" in {} else "Produção Total", f"{producao:,.0f} t", "toneladas colhidas"),
        (td("productivity") if "productivity" in {} else "Produtividade",          f"{produtividade:.2f} t/ha", "t/ha média"),
        (td("avg_cost") if "avg_cost" in {} else "Custo Médio",                   f"R$ {custo_total/n_safras if n_safras else 0:,.2f}", "por safra"),
    ])

    figs = []
    if "receita" in fato.columns:
        by_mes = _by_month(fato, "id_data", "receita")
        fig_mes = px.area(by_mes, x="mes", y="receita", labels={"mes":"","receita":td("revenue_brl")})
        fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
        _base_layout(fig_mes, td("monthly_revenue"))
        figs.append((fig_mes,3))

    if "producao_ton" in fato.columns and "id_cultura" in fato.columns:
        merged = fato.merge(cultura[["id_cultura","nome"]], on="id_cultura")
        by_cult = merged.groupby("nome")["producao_ton"].sum().reset_index().sort_values("producao_ton").tail(10)
        fig_cult = px.bar(by_cult, x="producao_ton", y="nome", orientation="h",
                          labels={"producao_ton":td("production_ton"),"nome":td("crop")},
                          color="producao_ton", color_continuous_scale=["#6d28d9","#a78bfa"])
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
                          color="produtividade_tha", color_continuous_scale=["#a78bfa","#c4b5fd","#ddd6fe"])
        fig_prod.update_layout(coloraxis_showscale=False)
        _base_layout(fig_prod, td("top10_productivity"))
        figs2.append((fig_prod,2))

    if "status" in fato.columns:
        by_status = fato["status"].value_counts().reset_index()
        fig_status = px.pie(by_status, names="status", values="count", hole=0.55, color_discrete_sequence=_PALETTE)
        fig_status.update_traces(textfont_color="#e2e8f0")
        _base_layout(fig_status, td("harvest_status"))
        figs2.append((fig_status,1))

    if figs2: _chart_row(figs2)


# ── ✈️ TURISMO ────────────────────────────────────────────────────────────────
def _dash_turismo(tabelas):
    fato = tabelas["FatoViagens"]; destino = tabelas["DimDestino"]
    _section("overview")
    tx_cancel = (fato["status"]=="Cancelada").mean()*100 if "status" in fato.columns else 0
    _kpi_row([
        (td("total_revenue"),   f"R$ {fato['valor_pago'].sum():,.0f}",  f"{len(fato):,} viagens"),
        (td("avg_ticket"),      f"R$ {fato['valor_pago'].mean():,.2f}", td("per_booking")),
        (td("cancel_rate"),     f"{tx_cancel:.1f}%",                     td("cancelled_status")),
        (td("total_passengers"),f"{fato['passageiros'].sum():,}",         td("persons")),
    ])
    by_mes = _by_month(fato, "id_data", "valor_pago")
    fig_mes = px.area(by_mes, x="mes", y="valor_pago", labels={"mes":"","valor_pago":td("revenue_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_revenue"))

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
        (td("business_volume"), f"R$ {fato['valor_final'].sum():,.0f}",  f"{len(fato):,} {td('contracts')}"),
        (td("avg_value"),       f"R$ {fato['valor_final'].mean():,.2f}", td("per_contract")),
        (td("pct_sales"),       f"{tx_venda:.1f}%",                       td("vs_rentals")),
        (td("avg_area"),        f"{imovel['area_m2'].mean():.1f} m²",     td("per_property")),
    ])
    by_mes = _by_month(fato, "id_data", "valor_final")
    fig_mes = px.area(by_mes, x="mes", y="valor_final", labels={"mes":"","valor_final":td("volume_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_business"))

    merged = fato.merge(imovel[["id_imovel","tipo"]], on="id_imovel")
    by_tipo = merged.groupby("tipo")["valor_final"].sum().reset_index()
    fig_tipo = px.pie(by_tipo, names="tipo", values="valor_final", hole=0.55, color_discrete_sequence=_PALETTE)
    fig_tipo.update_traces(textfont_color="#e2e8f0")
    _base_layout(fig_tipo, td("by_property_type"))
    _chart_row([(fig_mes,3),(fig_tipo,2)])


# ── 🛡️ SEGUROS ────────────────────────────────────────────────────────────────
def _dash_seguros(tabelas):
    fato = tabelas["FatoApolices"]; plano = tabelas["DimPlano"]
    premios = fato["valor_premio"].sum(); indenizacoes = fato["valor_indenizacao"].sum()
    loss_ratio = indenizacoes/premios*100 if premios>0 else 0
    _section("overview")
    _kpi_row([
        (td("total_premiums"), f"R$ {premios:,.0f}",             f"{len(fato):,} {td('policies')}"),
        (td("paid_claims"),    f"R$ {indenizacoes:,.0f}",         td("claims_paid")),
        (td("loss_ratio"),     f"{loss_ratio:.1f}%",              td("sp_ratio")),
        (td("avg_premium"),    f"R$ {fato['valor_premio'].mean():,.2f}", td("per_policy")),
    ])
    by_mes = _by_month(fato, "id_data", "valor_premio")
    fig_mes = px.area(by_mes, x="mes", y="valor_premio", labels={"mes":"","valor_premio":td("premiums_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_premiums"))

    merged = fato.merge(plano[["id_plano","tipo"]], on="id_plano")
    by_tipo = merged.groupby("tipo")["valor_premio"].sum().reset_index().sort_values("valor_premio")
    fig_tipo = px.bar(by_tipo, x="valor_premio", y="tipo", orientation="h",
                      labels={"valor_premio":td("premiums_brl"),"tipo":""},
                      color="valor_premio", color_continuous_scale=["#6d28d9","#a78bfa"])
    fig_tipo.update_layout(coloraxis_showscale=False)
    _base_layout(fig_tipo, td("premiums_by_type"))
    _chart_row([(fig_mes,3),(fig_tipo,2)])


# ── 🏗️ CONSTRUÇÃO ─────────────────────────────────────────────────────────────
def _dash_construcao(tabelas):
    fato = tabelas["FatoCustos"]; projeto = tabelas["DimProjeto"]
    custo_total = fato["custo_real"].sum(); horas = fato["horas_trabalhadas"].sum()
    _section("overview")
    _kpi_row([
        (td("total_real_cost"), f"R$ {custo_total:,.0f}",        f"{len(fato):,} {td('cost_entries')}"),
        (td("total_hours"),     f"{horas:,.0f}h",                  td("labor")),
        (td("cost_per_hour"),   f"R$ {custo_total/horas if horas else 0:,.2f}", td("efficiency")),
        (td("num_projects"),    f"{len(projeto)}",                  td("active_projects")),
    ])
    by_mes = _by_month(fato, "id_data", "custo_real")
    fig_mes = px.area(by_mes, x="mes", y="custo_real", labels={"mes":"","custo_real":td("cost_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_costs"))

    merged = fato.merge(projeto[["id_projeto","nome"]], on="id_projeto")
    by_proj = merged.groupby("nome")["custo_real"].sum().reset_index().sort_values("custo_real",ascending=False).head(10)
    fig_proj = px.bar(by_proj, x="nome", y="custo_real",
                      labels={"custo_real":td("cost_brl"),"nome":td("project")},
                      color="custo_real", color_continuous_scale=_PALETTE)
    fig_proj.update_layout(coloraxis_showscale=False)
    _base_layout(fig_proj, td("top10_projects"))
    _chart_row([(fig_mes,3),(fig_proj,2)])


# ════════════════════════════════════════════════════════════════════════════
#  DISPATCHER
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
}


def render_dashboard(nome: str, tabelas: dict) -> None:
    pt_name = resolve_sector_name(nome)
    fn = _DASHBOARDS.get(pt_name)
    if fn is None:
        lang = __import__('i18n').get_lang()
        msg = f"Dashboard not available for '{nome}'." if lang=="en" else f"Dashboard não disponível para '{nome}'."
        st.warning(msg)
        return
    fn(tabelas)


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
        (td("total_revenue"),  f"R$ {receita:,.0f}",                    f"{n:,} {td('in_period')}"),
        (td("avg_ticket"),     f"R$ {receita/n:,.2f}" if n else "—",    td("per_booking")),
        (td("avg_value"),      f"{fato['diarias'].mean():.1f}" if 'diarias' in fato.columns else "—", td("in_period")),
        (td("total_volume"),   f"{n:,}",                                 td("in_period")),
    ])
    val_col = "valor_total" if "valor_total" in fato.columns else fato.select_dtypes("number").columns[0]
    date_col = [c for c in fato.columns if "data" in c][0]
    by_mes = _by_month(fato, date_col, val_col)
    fig_mes = px.area(by_mes, x="mes", y=val_col, labels={"mes": "", val_col: td("revenue_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_revenue"))
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
        (td("total_revenue"),  f"R$ {receita:,.0f}",        f"{n:,} plays"),
        (td("avg_value"),      f"{dur_media:.0f} min",       td("per_visit")),
        (td("total_volume"),   f"{n:,}",                     td("in_period")),
        (td("efficiency"),     f"{fato[dur_col].sum()/60:,.0f}h" if dur_col else "—", td("in_period")),
    ])
    date_col = [c for c in fato.columns if "data" in c][0]
    by_mes = _by_month(fato, date_col, receita_col or num_cols[0])
    fig_mes = px.area(by_mes, x="mes", y=by_mes.columns[1], labels={"mes": "", by_mes.columns[1]: td("revenue_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_revenue"))
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
        (td("total_revenue"),  f"R$ {receita:,.0f}",                          f"{n:,} {td('sales')}"),
        (td("avg_ticket"),     f"R$ {fato['valor_total'].mean():,.2f}",        td("per_sale")),
        (td("avg_discount"),   f"R$ {fato['desconto'].mean():,.2f}",           td("per_sale")),
        (td("efficiency"),     f"{(fato['status']=='entregue').mean()*100:.1f}%" if 'status' in fato.columns else "—", td("completed")),
    ])
    by_mes = _by_month(fato, "data_pedido", "valor_total")
    fig_mes = px.area(by_mes, x="mes", y="valor_total", labels={"mes": "", "valor_total": td("revenue_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_revenue"))
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
        (td("total_revenue"),  f"R$ {fato['custo_diario'].sum():,.0f}",          f"{n:,} {td('in_period')}"),
        (td("avg_value"),      f"{fato['horas_trabalhadas'].mean():.1f}h",        td("per_visit")),
        (td("efficiency"),     f"{fato['produtividade'].mean():.1f}%",            td("global_efficiency")),
        (td("score"),          f"{fato['satisfacao'].mean():.2f}",                td("overall_avg")),
    ])
    by_mes = _by_month(fato, "data_registro", "custo_diario")
    fig_mes = px.area(by_mes, x="mes", y="custo_diario", labels={"mes": "", "custo_diario": td("cost_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_costs"))
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
        (td("total_revenue"),  f"R$ {receita:,.0f}",                              f"{n:,} viagens"),
        (td("avg_ticket"),     f"R$ {fato['valor_total'].mean():,.2f}",            td("per_sale")),
        (td("efficiency"),     f"{fato['distancia_km'].mean():.1f} km",            td("per_sale")),
        (td("score"),          f"{fato['avaliacao_passageiro'].mean():.2f}",        td("overall_avg")),
    ])
    fato["_data"] = pd.to_datetime(fato["data_hora_inicio"]).dt.date.astype(str)
    by_mes = _by_month(fato, "_data", "valor_total")
    fig_mes = px.area(by_mes, x="mes", y="valor_total", labels={"mes": "", "valor_total": td("revenue_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_revenue"))
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
        (td("total_volume"),   f"R$ {vol:,.0f}",                                    f"{n:,} {td('transactions')}"),
        (td("approval_rate"),  f"{(fato['status']=='aprovada').mean()*100:.1f}%",    td("approved_tx")),
        (td("avg_value"),      f"R$ {fato['valor'].mean():,.2f}",                    td("per_tx")),
        (td("avg_ticket"),     f"R$ {fato['cashback_valor'].mean():,.2f}",           "cashback médio"),
    ])
    fato["_d"] = pd.to_datetime(fato["data_hora"]).dt.date.astype(str)
    by_mes = _by_month(fato, "_d", "valor")
    fig_mes = px.area(by_mes, x="mes", y="valor", labels={"mes": "", "valor": td("volume_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_volume"))
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
        (td("total_revenue"),     f"R$ {receita:,.0f}",                               f"{n:,} {td('in_period')}"),
        (td("total_production"),  f"{fato['volume_extraido_ton'].sum():,.0f} t",       td("production_sub")),
        (td("efficiency"),        f"{fato['indice_seguranca'].mean():.1f}",            td("score")),
        (td("avg_cost"),          f"R$ {fato['custo_operacional'].mean():,.2f}",       td("per_visit")),
    ])
    by_mes = _by_month(fato, "id_data", "receita")
    fig_mes = px.area(by_mes, x="mes", y="receita", labels={"mes": "", "receita": td("revenue_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_revenue"))
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
        (td("total_revenue"),  f"R$ {honorarios:,.0f}",                                f"{n:,} processos"),
        (td("avg_value"),      f"R$ {fato['valor_causa'].mean():,.2f}",                 "valor médio da causa"),
        (td("efficiency"),     f"{fato['resultado_favoravel'].mean()*100:.1f}%",        "taxa de êxito"),
        (td("avg_delay_type"), f"{fato['duracao_dias'].mean():.0f} dias",               "duração média"),
    ])
    by_mes = _by_month(fato, "id_data", "honorarios")
    fig_mes = px.area(by_mes, x="mes", y="honorarios", labels={"mes": "", "honorarios": td("revenue_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_revenue"))
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
        (td("total_revenue"),  f"R$ {receita:,.0f}",                               f"{n:,} partidas"),
        (td("avg_ticket"),     f"{fato['publico'].mean():,.0f}",                    "público médio"),
        (td("score"),          f"{fato['gols_casa'].mean() + fato['gols_fora'].mean():.2f}", "gols/partida"),
        (td("efficiency"),     f"{fato['receita_bilheteria'].sum()/receita*100:.1f}%", "% bilheteria"),
    ])
    fato["receita_total"] = fato["receita_bilheteria"] + fato["receita_tv"] + fato["receita_patrocinio"]
    by_mes = _by_month(fato, "id_data", "receita_total")
    fig_mes = px.area(by_mes, x="mes", y="receita_total", labels={"mes": "", "receita_total": td("revenue_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_revenue"))
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
        (td("total_mrr"),      f"R$ {mrr_total:,.0f}",                              f"{n:,} {td('in_period')}"),
        (td("arr_sub"),        f"R$ {fato['arr'].mean():,.0f}",                      td("per_contract")),
        (td("nps_scale"),      f"{fato['nps'].mean():.1f}",                          td("overall_avg")),
        (td("efficiency"),     f"{fato['churn'].mean()*100:.1f}%",                   "churn rate"),
    ])
    by_mes = _by_month(fato, "id_data", "mrr")
    fig_mes = px.area(by_mes, x="mes", y="mrr", labels={"mes": "", "mrr": "MRR (R$)"})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("mrr_by_month"))
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
        (td("total_revenue"),  f"R$ {receita:,.0f}",                                  f"{n:,} oportunidades"),
        (td("efficiency"),     f"{fato['ganho'].mean()*100:.1f}%",                     "win rate"),
        (td("avg_ticket"),     f"R$ {fato['valor_estimado'].mean():,.2f}",             "valor médio"),
        (td("avg_delay_type"), f"{fato['ciclo_vendas_dias'].mean():.0f} dias",         "ciclo médio"),
    ])
    by_mes = _by_month(fato, "id_data_abertura", "valor_fechado")
    fig_mes = px.area(by_mes, x="mes", y="valor_fechado", labels={"mes": "", "valor_fechado": td("revenue_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_revenue"))
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
        (td("total_revenue"),  f"R$ {receita:,.0f}",                              f"{n:,} {td('sales')}"),
        (td("avg_ticket"),     f"R$ {fato['valor_liquido'].mean():,.2f}",          td("per_sale")),
        (td("avg_discount"),   f"{fato['desconto_pct'].mean():.1f}%",             td("on_full_price")),
        (td("efficiency"),     f"{(~fato['devolvido']).mean()*100:.1f}%",          "taxa de retenção"),
    ])
    by_mes = _by_month(fato, "id_data", "valor_liquido")
    fig_mes = px.area(by_mes, x="mes", y="valor_liquido", labels={"mes": "", "valor_liquido": td("revenue_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_revenue"))
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
        (td("total_volume"),   f"R$ {investimento:,.0f}",                             f"{n:,} campanhas/dia"),
        (td("efficiency"),     f"{fato['ctr_pct'].mean():.2f}%",                      "CTR médio"),
        (td("avg_value"),      f"R$ {fato['cpc'].mean():,.2f}",                       "CPC médio"),
        (td("score"),          f"{conv['roas'].mean():.2f}x",                         "ROAS médio"),
    ])
    by_mes = _by_month(fato, "id_data", "investimento")
    fig_mes = px.area(by_mes, x="mes", y="investimento", labels={"mes": "", "investimento": td("cost_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_costs"))
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
        (td("total_revenue"),     f"US$ {receita:,.0f}",                               f"{n:,} registros"),
        (td("total_production"),  f"{fato['vol_oleo_bbl'].sum():,.0f} bbl",             "óleo total"),
        (td("efficiency"),        f"{fato['eficiencia_pct'].mean():.1f}%",              td("global_efficiency")),
        (td("avg_cost"),          f"US$ {custo['lifting_cost_bbl'].mean():,.2f}",       "lifting cost/bbl"),
    ])
    by_mes = _by_month(fato, "id_data", "receita_usd")
    fig_mes = px.area(by_mes, x="mes", y="receita_usd", labels={"mes": "", "receita_usd": "Receita (US$)"})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_revenue"))
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
        (td("total_volume"),   f"R$ {pago:,.0f}",                                  f"{n:,} despesas"),
        (td("efficiency"),     f"{fato['execucao_pct'].mean():.1f}%",              "execução orçamentária"),
        (td("avg_value"),      f"R$ {fato['valor_empenhado'].sum():,.0f}",         "total empenhado"),
        (td("score"),          f"R$ {fato['valor_liquidado'].sum():,.0f}",         "total liquidado"),
    ])
    by_mes = _by_month(fato, "id_data", "valor_pago")
    fig_mes = px.area(by_mes, x="mes", y="valor_pago", labels={"mes": "", "valor_pago": td("volume_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_volume"))
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
        (td("total_revenue"),    f"R$ {receita:,.0f}",                               f"{n:,} lotes"),
        (td("total_production"), f"{fato['volume_produzido_kg'].sum():,.0f} kg",      td("production_sub")),
        (td("efficiency"),       f"{100 - fato['indice_refugo_pct'].mean():.1f}%",   "aproveitamento"),
        (td("avg_cost"),         f"R$ {fato['custo_producao'].mean():,.2f}",          "custo médio/lote"),
    ])
    by_mes = _by_month(fato, "id_data", "receita")
    fig_mes = px.area(by_mes, x="mes", y="receita", labels={"mes": "", "receita": td("revenue_brl")})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, td("monthly_revenue"))
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
