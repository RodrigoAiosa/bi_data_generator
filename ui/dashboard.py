# ── 🌾 AGRONEGÓCIO ────────────────────────────────────────────────────────────
def _dash_agronegocio(tabelas: dict[str, pd.DataFrame]) -> None:
    fato = tabelas["FatoSafra"]
    cultura = tabelas["DimCultura"]
    prop = tabelas["DimPropriedade"]

    # Verificação robusta de colunas disponíveis
    area_col = None
    for col in ['area_plantada_ha', 'area_plantada', 'area_ha']:
        if col in fato.columns:
            area_col = col
            break
    
    custo_col = None
    for col in ['custo_total', 'custo_ha', 'custo']:
        if col in fato.columns:
            custo_col = col
            break
    
    # Cálculo das métricas
    receita = fato["receita"].sum()
    producao = fato["producao_ton"].sum()
    n_safras = len(fato)
    
    area_total = fato[area_col].sum() if area_col else 0
    produtividade = producao / area_total if area_total > 0 else 0
    
    custo_total = fato[custo_col].sum() if custo_col else 0
    custo_medio = custo_total / n_safras if n_safras > 0 else 0

    _section("Visão Geral")
    _kpi_row([
        ("Receita Total", f"R$ {receita:,.0f}", f"{n_safras:,} safras"),
        ("Produção Total", f"{producao:,.0f} t", "toneladas colhidas"),
        ("Produtividade", f"{produtividade:.2f} t/ha", "média por hectare"),
        ("Custo Médio", f"R$ {custo_medio:,.2f}", "por safra"),
    ])

    # Receita por mês
    fato2 = fato.copy()
    fato2["mes"] = pd.to_datetime(fato2["id_data"]).dt.to_period("M").astype(str)
    by_mes = fato2.groupby("mes")["receita"].sum().reset_index()
    fig_mes = px.area(by_mes, x="mes", y="receita",
                      labels={"mes": "", "receita": "Receita (R$)"})
    fig_mes.update_traces(line_color=_ACCENT, fillcolor="rgba(167,139,250,0.15)")
    _base_layout(fig_mes, "Receita Mensal")

    # Top culturas por produção
    merged = fato.merge(cultura[["id_cultura","nome"]], on="id_cultura")
    by_cult = merged.groupby("nome")["producao_ton"].sum().reset_index().sort_values("producao_ton").tail(10)
    fig_cult = px.bar(by_cult, x="producao_ton", y="nome", orientation="h",
                      labels={"producao_ton": "Produção (ton)", "nome": ""},
                      color="producao_ton", color_continuous_scale=["#6d28d9","#a78bfa"])
    fig_cult.update_layout(coloraxis_showscale=False)
    _base_layout(fig_cult, "Top 10 Culturas por Produção")

    _chart_row([(fig_mes, 3), (fig_cult, 2)])

    # Produtividade por cultura
    by_prod = merged.groupby("nome")["produtividade_tha"].mean().reset_index().sort_values("produtividade_tha", ascending=False).head(10)
    fig_prod = px.bar(by_prod, x="produtividade_tha", y="nome", orientation="h",
                      labels={"produtividade_tha": "Produtividade (t/ha)", "nome": ""},
                      color="produtividade_tha", color_continuous_scale=["#a78bfa","#c4b5fd","#ddd6fe"])
    fig_prod.update_layout(coloraxis_showscale=False)
    _base_layout(fig_prod, "Top 10 Culturas por Produtividade")

    # Status das safras
    by_status = fato["status"].value_counts().reset_index()
    fig_status = px.pie(by_status, names="status", values="count",
                        hole=0.55, color_discrete_sequence=_PALETTE)
    fig_status.update_traces(textfont_color="#e2e8f0")
    _base_layout(fig_status, "Status das Safras")

    _chart_row([(fig_prod, 2), (fig_status, 1)])
