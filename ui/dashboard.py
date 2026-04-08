"""
ui/dashboard.py
Dashboard com KPIs e gráficos interativos por setor.
Cada setor tem sua própria função de renderização.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Tema Plotly compatível com o design da aplicação ────────────────────────
_BG        = "rgba(0,0,0,0)"
_PAPER     = "rgba(0,0,0,0)"
_GRID      = "rgba(167,139,250,0.08)"
_TEXT      = "#7b8ba8"
_ACCENT    = "#a78bfa"
_PALETTE   = ["#a78bfa","#7c3aed","#c4b5fd","#6d28d9","#ddd6fe","#4c1d95","#ede9fe"]

def _base_layout(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(
        paper_bgcolor=_PAPER,
        plot_bgcolor=_BG,
        font=dict(family="DM Sans, sans-serif", color=_TEXT, size=12),
        title=dict(text=title, font=dict(color="#e2e8f0", size=14, family="Syne, sans-serif"), x=0.01),
        margin=dict(l=16, r=16, t=40 if title else 16, b=16),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=_TEXT)),
        colorway=_PALETTE,
    )
    fig.update_xaxes(gridcolor=_GRID, zeroline=False, tickfont=dict(color=_TEXT))
    fig.update_yaxes(gridcolor=_GRID, zeroline=False, tickfont=dict(color=_TEXT))
    return fig


# ── Helper: cartão de métrica estilizado ─────────────────────────────────────
def _metric(label: str, value: str, sub: str = "", delta: str = "") -> str:
    delta_html = (
        f'<span style="font-size:0.78rem;color:#4ade80;margin-top:4px;display:block;">'
        f'▲ {delta}</span>'
        if delta else ""
    )
    sub_html = (
        f'<span class="stat-sublabel">{sub}</span>'
        if sub else ""
    )
    return f"""
    <div class="stat-card">
        <span class="stat-number">{value}</span>
        <span class="stat-label">{label}</span>
        {sub_html}{delta_html}
    </div>"""


def _kpi_row(metrics: list[tuple]) -> None:
    """Renderiza uma linha de cartões KPI. Cada item: (label, value, sub?, delta?)."""
    cols = st.columns(len(metrics))
    for col, args in zip(cols, metrics):
        with col:
            st.markdown(_metric(*args), unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:32px'></div>", unsafe_allow_html=True)


def _chart_row(figs: list[tuple[go.Figure, int]]) -> None:
    """Renderiza uma linha de gráficos. Cada item: (fig, col_weight)."""
    weights = [w for _, w in figs]
    cols = st.columns(weights)
    for col, (fig, _) in zip(cols, figs):
        with col:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _section(title: str) -> None:
    st.markdown(f'<h3 class="section-header">{title}</h3>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
#  DASHBOARDS POR SETOR
# ════════════════════════════════════════════════════════════════════════════

# ── 🛒 VAREJO ────────────────────────────────────────────────────────────────
def _dash_varejo(tabelas: dict[str, pd.DataFrame]) -> None:
    fato    = tabelas["FatoVendas"]
    produto = tabelas["DimProduto"]
    vendedor= tabelas["DimVendedor"]

    receita      = fato["valor_total"].sum()
    ticket_medio = fato["valor_total"].mean()
    n_vendas     = len(fato)
    desconto_med = fato["desconto"].mean() * 100

    _section("Visão Geral")
    _kpi_row([
        ("Receita Total",   f"R$ {receita:,.0f}",        f"{n_vendas:,} vendas"),
        ("Ticket Médio",    f"R$ {ticket_medio:,.2f}",   "por venda"),
        ("Desconto Médio",  f"{desconto_med:.1f}%",      "sobre preço cheio"),
        ("Qtd. Média/Venda",f"{fato['quantidade'].mean():.1f}", "unidades"),
    ])

    # Vendas por mês
    fato2 = fato.copy()
    fato2["mes"] = pd.to_datetime(fato2["id_data"]).dt.to_period("M").astype(str)
    by_mes = fato2.groupby("mes")["valor_total"].sum().reset_index()
    fig_mes = px.area(by_mes, x="mes", y="valor_total",
                      labels={"mes": "", "valor_total": "Receita (R$)"})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, "Receita Mensal")

    # Vendas por categoria
    merged = fato.merge(produto[["id_produto","categoria"]], on="id_produto")
    by_cat = merged.groupby("categoria")["valor_total"].sum().reset_index().sort_values("valor_total")
    fig_cat = px.bar(by_cat, x="valor_total", y="categoria", orientation="h",
                     labels={"valor_total": "Receita (R$)", "categoria": ""})
    fig_cat.update_traces(marker_color=_ACCENT)
    _base_layout(fig_cat, "Receita por Categoria")

    _section("Canais & Desempenho")
    _chart_row([(fig_mes, 3), (fig_cat, 2)])

    # Canal de venda
    by_canal = fato.groupby("canal")["valor_total"].sum().reset_index()
    fig_canal = px.pie(by_canal, names="canal", values="valor_total",
                       hole=0.55, color_discrete_sequence=_PALETTE)
    fig_canal.update_traces(textfont_color="#e2e8f0")
    _base_layout(fig_canal, "Receita por Canal")

    # Top 10 vendedores
    top_vend = (fato.groupby("id_vendedor")["valor_total"].sum()
                .reset_index().sort_values("valor_total", ascending=False).head(10))
    top_vend = top_vend.merge(vendedor[["id_vendedor","nome"]], on="id_vendedor")
    fig_vend = px.bar(top_vend, x="valor_total", y="nome", orientation="h",
                      labels={"valor_total": "Receita (R$)", "nome": ""},
                      color="valor_total", color_continuous_scale=["#6d28d9","#a78bfa","#c4b5fd"])
    fig_vend.update_layout(coloraxis_showscale=False)
    _base_layout(fig_vend, "Top 10 Vendedores")

    _chart_row([(fig_canal, 1), (fig_vend, 2)])


# ── 💰 FINANCEIRO ─────────────────────────────────────────────────────────────
def _dash_financeiro(tabelas: dict[str, pd.DataFrame]) -> None:
    fato    = tabelas["FatoTransacao"]
    produto = tabelas["DimProduto"]

    vol_total   = fato["valor"].sum()
    aprovadas   = (fato["status"] == "Aprovada").mean() * 100
    valor_medio = fato["valor"].mean()
    n_trans     = len(fato)

    _section("Visão Geral")
    _kpi_row([
        ("Volume Total",       f"R$ {vol_total:,.0f}",   f"{n_trans:,} transações"),
        ("Taxa de Aprovação",  f"{aprovadas:.1f}%",       "transações aprovadas"),
        ("Valor Médio",        f"R$ {valor_medio:,.2f}",  "por transação"),
        ("Saldo Médio Pós",    f"R$ {fato['saldo_apos'].mean():,.0f}", "após transação"),
    ])

    # Volume por mês
    fato2 = fato.copy()
    fato2["mes"] = pd.to_datetime(fato2["id_data"]).dt.to_period("M").astype(str)
    by_mes = fato2.groupby("mes")["valor"].sum().reset_index()
    fig_mes = px.area(by_mes, x="mes", y="valor",
                      labels={"mes": "", "valor": "Volume (R$)"})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, "Volume Transacionado por Mês")

    # Por tipo de transação
    by_tipo = fato.groupby("tipo")["valor"].sum().reset_index().sort_values("valor")
    fig_tipo = px.bar(by_tipo, x="valor", y="tipo", orientation="h",
                      labels={"valor": "Volume (R$)", "tipo": ""},
                      color="valor", color_continuous_scale=["#6d28d9","#a78bfa"])
    fig_tipo.update_layout(coloraxis_showscale=False)
    _base_layout(fig_tipo, "Volume por Tipo de Transação")

    _section("Distribuição & Status")
    _chart_row([(fig_mes, 3), (fig_tipo, 2)])

    # Status
    by_status = fato["status"].value_counts().reset_index()
    fig_status = px.pie(by_status, names="status", values="count",
                        hole=0.55, color_discrete_sequence=_PALETTE)
    fig_status.update_traces(textfont_color="#e2e8f0")
    _base_layout(fig_status, "Distribuição por Status")

    # Por categoria de produto
    merged = fato.merge(produto[["id_produto","categoria"]], on="id_produto")
    by_cat = merged.groupby("categoria")["valor"].sum().reset_index().sort_values("valor", ascending=False)
    fig_cat = px.bar(by_cat, x="categoria", y="valor",
                     labels={"valor": "Volume (R$)", "categoria": ""},
                     color="valor", color_continuous_scale=["#6d28d9","#a78bfa","#c4b5fd"])
    fig_cat.update_layout(coloraxis_showscale=False)
    _base_layout(fig_cat, "Volume por Categoria de Produto")

    _chart_row([(fig_status, 1), (fig_cat, 2)])


# ── 🏥 SAÚDE ──────────────────────────────────────────────────────────────────
def _dash_saude(tabelas: dict[str, pd.DataFrame]) -> None:
    fato    = tabelas["FatoAtendimento"]
    medico  = tabelas["DimMedico"]
    paciente= tabelas["DimPaciente"]

    receita      = fato["valor_cobrado"].sum()
    duracao_med  = fato["duracao_min"].mean()
    n_atend      = len(fato)
    tx_alta      = (fato["resultado"] == "Alta").mean() * 100

    _section("Visão Geral")
    _kpi_row([
        ("Receita Total",       f"R$ {receita:,.0f}",      f"{n_atend:,} atendimentos"),
        ("Taxa de Alta",        f"{tx_alta:.1f}%",          "dos atendimentos"),
        ("Duração Média",       f"{duracao_med:.0f} min",   "por atendimento"),
        ("Valor Médio",         f"R$ {fato['valor_cobrado'].mean():,.2f}", "por atendimento"),
    ])

    # Atendimentos por mês
    fato2 = fato.copy()
    fato2["mes"] = pd.to_datetime(fato2["id_data"]).dt.to_period("M").astype(str)
    by_mes = fato2.groupby("mes").size().reset_index(name="count")
    fig_mes = px.area(by_mes, x="mes", y="count",
                      labels={"mes": "", "count": "Atendimentos"})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, "Atendimentos por Mês")

    # Por especialidade
    merged = fato.merge(medico[["id_medico","especialidade"]], on="id_medico")
    by_esp = merged.groupby("especialidade").size().reset_index(name="count").sort_values("count")
    fig_esp = px.bar(by_esp, x="count", y="especialidade", orientation="h",
                     labels={"count": "Atendimentos", "especialidade": ""},
                     color="count", color_continuous_scale=["#6d28d9","#a78bfa"])
    fig_esp.update_layout(coloraxis_showscale=False)
    _base_layout(fig_esp, "Atendimentos por Especialidade")

    _section("Resultados & Convênios")
    _chart_row([(fig_mes, 3), (fig_esp, 2)])

    # Por resultado
    by_res = fato["resultado"].value_counts().reset_index()
    fig_res = px.pie(by_res, names="resultado", values="count",
                     hole=0.55, color_discrete_sequence=_PALETTE)
    fig_res.update_traces(textfont_color="#e2e8f0")
    _base_layout(fig_res, "Distribuição por Resultado")

    merged2 = fato.merge(paciente[["id_paciente","convenio"]], on="id_paciente")
    by_conv = merged2.groupby("convenio")["valor_cobrado"].sum().reset_index().sort_values("valor_cobrado", ascending=False)
    fig_conv = px.bar(by_conv, x="convenio", y="valor_cobrado",
                      labels={"valor_cobrado": "Receita (R$)", "convenio": ""},
                      color="valor_cobrado", color_continuous_scale=["#6d28d9","#a78bfa","#c4b5fd"])
    fig_conv.update_layout(coloraxis_showscale=False)
    _base_layout(fig_conv, "Receita por Convênio")

    _chart_row([(fig_res, 1), (fig_conv, 2)])


# ── 💻 TECNOLOGIA ─────────────────────────────────────────────────────────────
def _dash_tecnologia(tabelas: dict[str, pd.DataFrame]) -> None:
    fato    = tabelas["FatoContrato"]
    cliente = tabelas["DimCliente"]

    mrr_total = fato["valor_mrr"].sum()
    arr_total = fato["arr"].sum()
    nps_medio = fato["nps"].mean()
    churn_tx  = (fato["tipo"] == "Churn").mean() * 100

    _section("Visão Geral")
    _kpi_row([
        ("MRR Total",    f"R$ {mrr_total:,.0f}",   f"{len(fato):,} contratos"),
        ("ARR Total",    f"R$ {arr_total:,.0f}",   "receita anual recorrente"),
        ("NPS Médio",    f"{nps_medio:.1f}",         "de 0 a 10"),
        ("Taxa de Churn",f"{churn_tx:.1f}%",          "dos contratos"),
    ])

    # MRR por mês
    fato2 = fato.copy()
    fato2["mes"] = pd.to_datetime(fato2["id_data"]).dt.to_period("M").astype(str)
    by_mes = fato2.groupby("mes")["valor_mrr"].sum().reset_index()
    fig_mes = px.area(by_mes, x="mes", y="valor_mrr",
                      labels={"mes": "", "valor_mrr": "MRR (R$)"})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, "MRR por Mês")

    # Contratos por tipo
    by_tipo = fato["tipo"].value_counts().reset_index()
    fig_tipo = px.pie(by_tipo, names="tipo", values="count",
                      hole=0.55, color_discrete_sequence=_PALETTE)
    fig_tipo.update_traces(textfont_color="#e2e8f0")
    _base_layout(fig_tipo, "Contratos por Tipo")

    _section("Segmentação & NPS")
    _chart_row([(fig_mes, 3), (fig_tipo, 2)])

    # NPS distribution
    nps_dist = fato["nps"].value_counts().sort_index().reset_index()
    colors = ["#ef4444" if v <= 6 else "#f59e0b" if v <= 8 else "#4ade80"
              for v in nps_dist["nps"]]
    fig_nps = go.Figure(go.Bar(
        x=nps_dist["nps"].astype(str), y=nps_dist["count"],
        marker_color=colors,
    ))
    _base_layout(fig_nps, "Distribuição de NPS")
    fig_nps.update_xaxes(title_text="Score")
    fig_nps.update_yaxes(title_text="Contratos")

    # MRR por segmento de cliente
    merged = fato.merge(cliente[["id_cliente","setor"]], on="id_cliente")
    by_seg = merged.groupby("setor")["valor_mrr"].sum().reset_index().sort_values("valor_mrr", ascending=False)
    fig_seg = px.bar(by_seg, x="setor", y="valor_mrr",
                     labels={"valor_mrr": "MRR (R$)", "setor": ""},
                     color="valor_mrr", color_continuous_scale=["#6d28d9","#a78bfa","#c4b5fd"])
    fig_seg.update_layout(coloraxis_showscale=False)
    _base_layout(fig_seg, "MRR por Segmento de Cliente")

    _chart_row([(fig_nps, 2), (fig_seg, 3)])


# ── 📚 EDUCAÇÃO ───────────────────────────────────────────────────────────────
def _dash_educacao(tabelas: dict[str, pd.DataFrame]) -> None:
    fato  = tabelas["FatoMatricula"]
    curso = tabelas["DimCurso"]

    receita      = fato["valor_pago"].sum()
    tx_conclusao = fato["concluiu"].mean() * 100
    nota_media   = fato["nota_final"].mean()
    n_matriculas = len(fato)

    _section("Visão Geral")
    _kpi_row([
        ("Receita Total",     f"R$ {receita:,.0f}",    f"{n_matriculas:,} matrículas"),
        ("Taxa de Conclusão", f"{tx_conclusao:.1f}%",   "dos alunos"),
        ("Nota Média",        f"{nota_media:.2f}",       "de 0 a 10"),
        ("Ticket Médio",      f"R$ {fato['valor_pago'].mean():,.2f}", "por matrícula"),
    ])

    # Matrículas por mês
    fato2 = fato.copy()
    fato2["mes"] = pd.to_datetime(fato2["id_data"]).dt.to_period("M").astype(str)
    by_mes = fato2.groupby("mes").size().reset_index(name="count")
    fig_mes = px.area(by_mes, x="mes", y="count",
                      labels={"mes": "", "count": "Matrículas"})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, "Matrículas por Mês")

    # Por modalidade
    merged = fato.merge(curso[["id_curso","modalidade"]], on="id_curso")
    by_mod = merged.groupby("modalidade").size().reset_index(name="count")
    fig_mod = px.pie(by_mod, names="modalidade", values="count",
                     hole=0.55, color_discrete_sequence=_PALETTE)
    fig_mod.update_traces(textfont_color="#e2e8f0")
    _base_layout(fig_mod, "Matrículas por Modalidade")

    _section("Área & Desempenho")
    _chart_row([(fig_mes, 3), (fig_mod, 2)])

    # Por área do curso
    merged2 = fato.merge(curso[["id_curso","area"]], on="id_curso")
    by_area = merged2.groupby("area")["valor_pago"].sum().reset_index().sort_values("valor_pago")
    fig_area = px.bar(by_area, x="valor_pago", y="area", orientation="h",
                      labels={"valor_pago": "Receita (R$)", "area": ""},
                      color="valor_pago", color_continuous_scale=["#6d28d9","#a78bfa"])
    fig_area.update_layout(coloraxis_showscale=False)
    _base_layout(fig_area, "Receita por Área")

    # Distribuição de notas
    fig_notas = px.histogram(fato, x="nota_final", nbins=20,
                             labels={"nota_final": "Nota Final", "count": "Alunos"},
                             color_discrete_sequence=[_ACCENT])
    _base_layout(fig_notas, "Distribuição de Notas Finais")

    _chart_row([(fig_area, 2), (fig_notas, 3)])


# ── 🚚 LOGÍSTICA ──────────────────────────────────────────────────────────────
def _dash_logistica(tabelas: dict[str, pd.DataFrame]) -> None:
    fato  = tabelas["FatoEntrega"]
    trans = tabelas["DimTransportadora"]

    entregues    = (fato["status"] == "Entregue").mean() * 100
    frete_medio  = fato["valor_frete"].mean()
    frete_total  = fato["valor_frete"].sum()
    pontual      = (fato["dias_entregue"] <= fato["prazo_acordado"]).mean() * 100

    _section("Visão Geral")
    _kpi_row([
        ("Receita de Frete",   f"R$ {frete_total:,.0f}",  f"{len(fato):,} entregas"),
        ("Frete Médio",        f"R$ {frete_medio:,.2f}",   "por entrega"),
        ("Taxa de Entrega",    f"{entregues:.1f}%",         "entregas concluídas"),
        ("Pontualidade",       f"{pontual:.1f}%",           "dentro do prazo"),
    ])

    # Entregas por mês
    fato2 = fato.copy()
    fato2["mes"] = pd.to_datetime(fato2["id_data"]).dt.to_period("M").astype(str)
    by_mes = fato2.groupby("mes")["valor_frete"].sum().reset_index()
    fig_mes = px.area(by_mes, x="mes", y="valor_frete",
                      labels={"mes": "", "valor_frete": "Receita (R$)"})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, "Receita de Frete por Mês")

    # Status
    by_status = fato["status"].value_counts().reset_index()
    fig_status = px.pie(by_status, names="status", values="count",
                        hole=0.55, color_discrete_sequence=_PALETTE)
    fig_status.update_traces(textfont_color="#e2e8f0")
    _base_layout(fig_status, "Status das Entregas")

    _section("Transportadoras & Rotas")
    _chart_row([(fig_mes, 3), (fig_status, 2)])

    # Top transportadoras
    top_trans = (fato.groupby("id_transportadora")["valor_frete"].sum()
                 .reset_index().sort_values("valor_frete", ascending=False).head(10))
    top_trans = top_trans.merge(trans[["id_transportadora","nome"]], on="id_transportadora")
    fig_trans = px.bar(top_trans, x="valor_frete", y="nome", orientation="h",
                       labels={"valor_frete": "Receita (R$)", "nome": ""},
                       color="valor_frete", color_continuous_scale=["#6d28d9","#a78bfa"])
    fig_trans.update_layout(coloraxis_showscale=False)
    _base_layout(fig_trans, "Top Transportadoras por Receita")

    # Atraso médio
    fato["atraso"] = (fato["dias_entregue"] - fato["prazo_acordado"]).clip(lower=0)
    atraso_tipo = fato.merge(trans[["id_transportadora","tipo"]], on="id_transportadora")
    by_tipo = atraso_tipo.groupby("tipo")["atraso"].mean().reset_index()
    fig_atraso = px.bar(by_tipo, x="tipo", y="atraso",
                        labels={"atraso": "Dias de Atraso Médio", "tipo": ""},
                        color="atraso", color_continuous_scale=["#4ade80","#f59e0b","#ef4444"])
    fig_atraso.update_layout(coloraxis_showscale=False)
    _base_layout(fig_atraso, "Atraso Médio por Tipo de Transporte")

    _chart_row([(fig_trans, 3), (fig_atraso, 2)])


# ── ⚡ ENERGIA ────────────────────────────────────────────────────────────────
def _dash_energia(tabelas: dict[str, pd.DataFrame]) -> None:
    fato       = tabelas["FatoConsumo"]
    consumidor = tabelas["DimConsumidor"]

    consumo_total  = fato["consumo_kwh"].sum()
    fatura_media   = fato["valor_fatura"].mean()
    fatura_total   = fato["valor_fatura"].sum()
    fp_medio       = fato["fator_potencia"].mean()

    _section("Visão Geral")
    _kpi_row([
        ("Consumo Total",     f"{consumo_total:,.0f} kWh",  f"{len(fato):,} leituras"),
        ("Faturamento Total", f"R$ {fatura_total:,.0f}",    "todas as faturas"),
        ("Fatura Média",      f"R$ {fatura_media:,.2f}",    "por leitura"),
        ("Fator de Potência", f"{fp_medio:.3f}",             "média geral"),
    ])

    # Consumo por mês
    fato2 = fato.copy()
    fato2["mes"] = pd.to_datetime(fato2["id_data"]).dt.to_period("M").astype(str)
    by_mes = fato2.groupby("mes")["consumo_kwh"].sum().reset_index()
    fig_mes = px.area(by_mes, x="mes", y="consumo_kwh",
                      labels={"mes": "", "consumo_kwh": "Consumo (kWh)"})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, "Consumo Mensal (kWh)")

    # Por classe
    merged = fato.merge(consumidor[["id_consumidor","classe"]], on="id_consumidor")
    by_cls = merged.groupby("classe")["consumo_kwh"].sum().reset_index().sort_values("consumo_kwh")
    fig_cls = px.bar(by_cls, x="consumo_kwh", y="classe", orientation="h",
                     labels={"consumo_kwh": "Consumo (kWh)", "classe": ""},
                     color="consumo_kwh", color_continuous_scale=["#6d28d9","#a78bfa"])
    fig_cls.update_layout(coloraxis_showscale=False)
    _base_layout(fig_cls, "Consumo por Classe")

    _section("Tarifas & Distribuição")
    _chart_row([(fig_mes, 3), (fig_cls, 2)])

    # Tarifa média por mês
    by_mes_tar = fato2.groupby("mes")["tarifa_kwh"].mean().reset_index()
    fig_tar = px.line(by_mes_tar, x="mes", y="tarifa_kwh",
                      labels={"mes": "", "tarifa_kwh": "Tarifa Média (R$/kWh)"},
                      markers=True)
    fig_tar.update_traces(line_color=_ACCENT, marker_color=_ACCENT)
    _base_layout(fig_tar, "Evolução da Tarifa Média")

    # Faturamento por classe
    by_fat = merged.groupby("classe")["valor_fatura"].sum().reset_index().sort_values("valor_fatura", ascending=False)
    fig_fat = px.pie(by_fat, names="classe", values="valor_fatura",
                     hole=0.55, color_discrete_sequence=_PALETTE)
    fig_fat.update_traces(textfont_color="#e2e8f0")
    _base_layout(fig_fat, "Receita por Classe")

    _chart_row([(fig_tar, 3), (fig_fat, 2)])


# ── 📡 TELECOM ────────────────────────────────────────────────────────────────
def _dash_telecom(tabelas: dict[str, pd.DataFrame]) -> None:
    fato = tabelas["FatoChamada"]
    
    _section("Visão Geral")
    _kpi_row([
        ("Total Chamadas", f"{len(fato):,}", "no período"),
        ("Duração Média",  f"{fato['duracao_seg'].mean():.1f}s", "por chamada"),
        ("Custo Total",    f"R$ {fato['custo'].sum():,.2f}", "chamadas tarifadas"),
        ("Qualidade Média", f"{fato['qualidade_sinal'].mean():.1f}/5", "score de sinal"),
    ])

    # Chamadas por dia
    fato2 = fato.copy()
    fato2["dia"] = pd.to_datetime(fato2["id_data"]).dt.date
    by_dia = fato2.groupby("dia").size().reset_index(name="count")
    fig_dia = px.line(by_dia, x="dia", y="count")
    _base_layout(fig_dia, "Volume Diário de Chamadas")
    _chart_row([(fig_dia, 1)])


# ── 🏭 INDÚSTRIA ──────────────────────────────────────────────────────────────
def _dash_industria(tabelas: dict[str, pd.DataFrame]) -> None:
    fato = tabelas["FatoProducao"]
    
    _section("Visão Geral")
    _kpi_row([
        ("Produção Total", f"{fato['qtd_produzida'].sum():,.0f}", "unidades"),
        ("Taxa de Refugo", f"{(fato['qtd_refugo'].sum()/fato['qtd_produzida'].sum()*100):.2f}%", "perda"),
        ("OEE Médio",      f"{fato['oee_pct'].mean():.1f}%", "eficiência global"),
        ("Custo Total",    f"R$ {fato['custo_total'].sum():,.0f}", "produção"),
    ])

    # Produção por máquina
    by_maq = fato.groupby("id_maquina")["qtd_produzida"].sum().reset_index()
    fig_maq = px.bar(by_maq, x="id_maquina", y="qtd_produzida")
    _base_layout(fig_maq, "Produção por Máquina")
    _chart_row([(fig_maq, 1)])


# ── 🌾 AGRONEGÓCIO ────────────────────────────────────────────────────────────
def _dash_agronegocio(tabelas: dict[str, pd.DataFrame]) -> None:
    fato = tabelas["FatoSafra"]
    cultura = tabelas["DimCultura"]
    prop = tabelas["DimPropriedade"]

    receita = fato["receita"].sum()
    producao = fato["producao_ton"].sum()
    n_safras = len(fato)
    produtividade = producao / fato["area_plantada_ha"].sum() if fato["area_plantada_ha"].sum() > 0 else 0

    _section("Visão Geral")
    _kpi_row([
        ("Receita Total", f"R$ {receita:,.0f}", f"{n_safras:,} safras"),
        ("Produção Total", f"{producao:,.0f} t", "toneladas colhidas"),
        ("Produtividade", f"{produtividade:.2f} t/ha", "média por hectare"),
        ("Custo Médio", f"R$ {fato['custo_total'].mean():,.2f}", "por safra"),
    ])

    # Receita por mês
    fato2 = fato.copy()
    fato2["mes"] = pd.to_datetime(fato2["id_data"]).dt.to_period("M").astype(str)
    by_mes = fato2.groupby("mes")["receita"].sum().reset_index()
    fig_mes = px.area(by_mes, x="mes", y="receita")
    _base_layout(fig_mes, "Receita Mensal")

    # Top culturas
    merged = fato.merge(cultura[["id_cultura","nome"]], on="id_cultura")
    by_cult = merged.groupby("nome")["producao_ton"].sum().reset_index().sort_values("producao_ton").tail(10)
    fig_cult = px.bar(by_cult, x="producao_ton", y="nome", orientation="h")
    _base_layout(fig_cult, "Top 10 Culturas por Produção")

    _chart_row([(fig_mes, 3), (fig_cult, 2)])


# ── ✈️ TURISMO ───────────────────────────────────────────────────────────────
def _dash_turismo(tabelas: dict[str, pd.DataFrame]) -> None:
    fato = tabelas["FatoViagens"]
    pacote = tabelas["DimPacote"]
    destino = tabelas["DimDestino"]

    receita = fato["valor_pago"].sum()
    n_viagens = len(fato)
    ticket_medio = fato["valor_pago"].mean()
    tx_cancel = (fato["status"] == "Cancelada").mean() * 100

    _section("Visão Geral")
    _kpi_row([
        ("Receita Total", f"R$ {receita:,.0f}", f"{n_viagens:,} viagens"),
        ("Ticket Médio", f"R$ {ticket_medio:,.2f}", "por reserva"),
        ("Taxa de Cancelamento", f"{tx_cancel:.1f}%", "status cancelado"),
        ("Total Passageiros", f"{fato['passageiros'].sum():,}", "pessoas"),
    ])

    # Receita por mês
    fato2 = fato.copy()
    fato2["mes"] = pd.to_datetime(fato2["id_data"]).dt.to_period("M").astype(str)
    by_mes = fato2.groupby("mes")["valor_pago"].sum().reset_index()
    fig_mes = px.area(by_mes, x="mes", y="valor_pago")
    _base_layout(fig_mes, "Receita Mensal")

    # Por Destino (Top 10)
    merged = fato.merge(destino[["id_destino", "pais"]], on="id_destino")
    by_pais = merged.groupby("pais")["valor_pago"].sum().reset_index().sort_values("valor_pago", ascending=False)
    fig_pais = px.bar(by_pais, x="pais", y="valor_pago", color="valor_pago", color_continuous_scale=_PALETTE)
    fig_pais.update_layout(coloraxis_showscale=False)
    _base_layout(fig_pais, "Receita por País de Destino")

    _chart_row([(fig_mes, 3), (fig_pais, 2)])


# ── 🏠 IMOBILIÁRIO ────────────────────────────────────────────────────────────
def _dash_imobiliario(tabelas: dict[str, pd.DataFrame]) -> None:
    fato = tabelas["FatoVendas"]
    imovel = tabelas["DimImovel"]

    vpv = fato["valor_final"].sum()
    n_trans = len(fato)
    valor_medio = fato["valor_final"].mean()
    tx_venda = (fato["tipo_negocio"] == "Venda").mean() * 100

    _section("Visão Geral")
    _kpi_row([
        ("Volume de Negócios", f"R$ {vpv:,.0f}", f"{n_trans:,} contratos"),
        ("Valor Médio", f"R$ {valor_medio:,.2f}", "por contrato"),
        ("% Vendas", f"{tx_venda:.1f}%", "vs Aluguéis"),
        ("Área Média", f"{imovel['area_m2'].mean():.1f} m²", "por imóvel"),
    ])

    # Volume por mês
    fato2 = fato.copy()
    fato2["mes"] = pd.to_datetime(fato2["id_data"]).dt.to_period("M").astype(str)
    by_mes = fato2.groupby("mes")["valor_final"].sum().reset_index()
    fig_mes = px.area(by_mes, x="mes", y="valor_final")
    _base_layout(fig_mes, "Volume Mensal de Negócios")

    # Por tipo de imóvel
    merged = fato.merge(imovel[["id_imovel", "tipo"]], on="id_imovel")
    by_tipo = merged.groupby("tipo")["valor_final"].sum().reset_index()
    fig_tipo = px.pie(by_tipo, names="tipo", values="valor_final", hole=0.5)
    _base_layout(fig_tipo, "Volume por Tipo de Imóvel")

    _chart_row([(fig_mes, 3), (fig_tipo, 2)])


# ── 🛡️ SEGUROS ────────────────────────────────────────────────────────────────
def _dash_seguros(tabelas: dict[str, pd.DataFrame]) -> None:
    fato = tabelas["FatoApolices"]
    plano = tabelas["DimPlano"]

    premios = fato["valor_premio"].sum()
    indenizacoes = fato["valor_indenizacao"].sum()
    loss_ratio = (indenizacoes / premios * 100) if premios > 0 else 0
    n_apolices = len(fato)

    _section("Visão Geral")
    _kpi_row([
        ("Prêmios Totais", f"R$ {premios:,.0f}", f"{n_apolices:,} apólices"),
        ("Indenizações Pago", f"R$ {indenizacoes:,.0f}", "sinistros pagos"),
        ("Loss Ratio", f"{loss_ratio:.1f}%", "S/P"),
        ("Prêmio Médio", f"R$ {fato['valor_premio'].mean():,.2f}", "por apólice"),
    ])

    # Prêmios por mês
    fato2 = fato.copy()
    fato2["mes"] = pd.to_datetime(fato2["id_data"]).dt.to_period("M").astype(str)
    by_mes = fato2.groupby("mes")["valor_premio"].sum().reset_index()
    fig_mes = px.area(by_mes, x="mes", y="valor_premio")
    _base_layout(fig_mes, "Prêmios Emitidos por Mês")

    # Por Tipo de Seguro
    merged = fato.merge(plano[["id_plano", "tipo"]], on="id_plano")
    by_tipo = merged.groupby("tipo")["valor_premio"].sum().reset_index().sort_values("valor_premio")
    fig_tipo = px.bar(by_tipo, x="valor_premio", y="tipo", orientation="h")
    _base_layout(fig_tipo, "Prêmios por Tipo de Seguro")

    _chart_row([(fig_mes, 3), (fig_tipo, 2)])


# ── 🏗️ CONSTRUÇÃO CIVIL ───────────────────────────────────────────────────────
def _dash_construcao(tabelas: dict[str, pd.DataFrame]) -> None:
    fato = tabelas["FatoCustos"]
    projeto = tabelas["DimProjeto"]

    custo_total = fato["custo_real"].sum()
    horas_total = fato["horas_trabalhadas"].sum()
    n_lancamentos = len(fato)
    custo_hora = custo_total / horas_total if horas_total > 0 else 0

    _section("Visão Geral")
    _kpi_row([
        ("Custo Real Total", f"R$ {custo_total:,.0f}", f"{n_lancamentos:,} lançamentos"),
        ("Total Horas", f"{horas_total:,.0f}h", "mão de obra"),
        ("Custo Médio/Hora", f"R$ {custo_hora:,.2f}", "eficiência"),
        ("Qtd. Projetos", f"{len(projeto)}", "obras ativas"),
    ])

    # Custos por mês
    fato2 = fato.copy()
    fato2["mes"] = pd.to_datetime(fato2["id_data"]).dt.to_period("M").astype(str)
    by_mes = fato2.groupby("mes")["custo_real"].sum().reset_index()
    fig_mes = px.area(by_mes, x="mes", y="custo_real")
    _base_layout(fig_mes, "Evolução de Custos Mensais")

    # Custos por Projeto
    merged = fato.merge(projeto[["id_projeto", "nome"]], on="id_projeto")
    by_proj = merged.groupby("nome")["custo_real"].sum().reset_index().sort_values("custo_real", ascending=False).head(10)
    fig_proj = px.bar(by_proj, x="nome", y="custo_real", color="custo_real", color_continuous_scale=_PALETTE)
    fig_proj.update_layout(coloraxis_showscale=False)
    _base_layout(fig_proj, "Top 10 Projetos por Custo")

    _chart_row([(fig_mes, 3), (fig_proj, 2)])


# ════════════════════════════════════════════════════════════════════════════
#  DISPATCHER — mapeia nome do setor → função de dashboard
# ════════════════════════════════════════════════════════════════════════════
_DASHBOARDS: dict[str, callable] = {
    "Varejo":      _dash_varejo,
    "Financeiro":  _dash_financeiro,
    "Saúde":       _dash_saude,
    "Tecnologia":  _dash_tecnologia,
    "Educação":    _dash_educacao,
    "Logística":   _dash_logistica,
    "Energia":     _dash_energia,
    "Telecom":     _dash_telecom,
    "Indústria":   _dash_industria,
    "Agronegócio": _dash_agronegocio,
    "Turismo":     _dash_turismo,
    "Imobiliário": _dash_imobiliario,
    "Seguros":     _dash_seguros,
    "Construção Civil": _dash_construcao,
}


def render_dashboard(nome: str, tabelas: dict[str, pd.DataFrame]) -> None:
    """
    Ponto de entrada público.
    Recebe o nome do setor (sem emoji) e o dicionário de tabelas geradas.
    """
    fn = _DASHBOARDS.get(nome)
    if fn is None:
        st.warning(f"Dashboard não disponível para o setor '{nome}'.")
        return
    fn(tabelas)
