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


# ── Tradução dos setores (nome + descrição) ───────────────────────────────────

SETORES_INFO_EN = [
    ("🌾", "Agribusiness",          "Harvests, crops, properties and inputs"),
    ("🍔", "Food & Beverage",        "Production, plants, products and suppliers"),
    ("🏗️", "Construction",          "Projects, costs, materials and suppliers"),
    ("🤝", "CRM",                    "Opportunities, accounts, contacts and sales activities"),
    ("🏪", "E-commerce",             "Orders, customers, products, shipping and payments"),
    ("📚", "Education",              "Enrollments, students, courses and instructors"),
    ("⚡", "Energy",                 "Consumption, meters, substations and tariffs"),
    ("🏟️", "Sports",                "Matches, athletes, clubs and competitions"),
    ("💊", "Pharmaceutical",         "Products, reps, sales and inventory"),
    ("💰", "Financial",              "Banking transactions, accounts and branches"),
    ("🏦", "Fintech",                "Transactions, cards, users, merchants and fraud"),
    ("🏛️", "Government & Public Sector", "Expenditures, revenues, tenders and contracts"),
    ("🏨", "Hospitality",            "Reservations, guests, hotels, rooms and channels"),
    ("🏠", "Real Estate",            "Sales, rentals, properties and agents"),
    ("🏭", "Manufacturing",          "Production, machines, inputs and operators"),
    ("⚖️", "Legal",                  "Cases, lawyers, clients and courts"),
    ("🚚", "Logistics",              "Deliveries, carriers, routes and customers"),
    ("📣", "Digital Marketing",      "Campaigns, channels, performance and conversions"),
    ("⛏️", "Mining",                 "Extractions, mines, minerals and equipment"),
    ("🚗", "Mobility",               "Rides, drivers, passengers, routes and vehicles"),
    ("🛢️", "Oil & Gas",             "Production, wells, platforms and operating costs"),
    ("🏢", "Human Resources",        "Hours worked, employees, projects and roles"),
    ("☁️", "SaaS B2B",              "Subscriptions, MRR, churn, NPS and plans"),
    ("🏥", "Healthcare",             "Visits, patients, physicians and procedures"),
    ("🛡️", "Insurance",             "Policies, insureds, brokers and claims"),
    ("🎬", "Streaming",              "Plays, subscribers, content, artists"),
    ("💻", "Technology",             "SaaS contracts, customers and plans"),
    ("📡", "Telecom",                "Calls, subscribers, plans and towers"),
    ("✈️", "Tourism",                "Trips, packages, agencies and destinations"),
    ("🛒", "Retail",                 "Sales, customers, products and branches"),
]


def get_setores_info():
    """Retorna SETORES_INFO no idioma atual."""
    from config import SETORES_INFO
    return SETORES_INFO_EN if get_lang() == "en" else SETORES_INFO


# ── Textos dos dashboards ─────────────────────────────────────────────────────

_DASH: dict[str, dict[str, str]] = {
    # Seções
    "overview":          {"pt": "Visão Geral",            "en": "Overview"},
    "channels":          {"pt": "Canais & Desempenho",    "en": "Channels & Performance"},
    "distribution":      {"pt": "Distribuição & Status",  "en": "Distribution & Status"},
    "results":           {"pt": "Resultados & Convênios", "en": "Results & Health Plans"},
    "segmentation":      {"pt": "Segmentação & NPS",      "en": "Segmentation & NPS"},
    "area_performance":  {"pt": "Área & Desempenho",      "en": "Area & Performance"},
    "carriers_routes":   {"pt": "Transportadoras & Rotas","en": "Carriers & Routes"},
    "tariffs":           {"pt": "Tarifas & Distribuição", "en": "Tariffs & Distribution"},

    # KPI labels — Varejo
    "total_revenue":     {"pt": "Receita Total",          "en": "Total Revenue"},
    "avg_ticket":        {"pt": "Ticket Médio",           "en": "Avg. Ticket"},
    "avg_discount":      {"pt": "Desconto Médio",         "en": "Avg. Discount"},
    "avg_qty":           {"pt": "Qtd. Média/Venda",       "en": "Avg. Qty/Sale"},
    "sales":             {"pt": "vendas",                  "en": "sales"},
    "per_sale":          {"pt": "por venda",               "en": "per sale"},
    "on_full_price":     {"pt": "sobre preço cheio",       "en": "off full price"},
    "units":             {"pt": "unidades",                "en": "units"},

    # KPI labels — Financeiro
    "total_volume":      {"pt": "Volume Total",           "en": "Total Volume"},
    "approval_rate":     {"pt": "Taxa de Aprovação",      "en": "Approval Rate"},
    "avg_value":         {"pt": "Valor Médio",            "en": "Avg. Value"},
    "avg_balance":       {"pt": "Saldo Médio Pós",        "en": "Avg. Post Balance"},
    "transactions":      {"pt": "transações",              "en": "transactions"},
    "approved_tx":       {"pt": "transações aprovadas",   "en": "approved transactions"},
    "per_tx":            {"pt": "por transação",           "en": "per transaction"},
    "after_tx":          {"pt": "após transação",          "en": "after transaction"},

    # KPI labels — Saúde
    "discharge_rate":    {"pt": "Taxa de Alta",           "en": "Discharge Rate"},
    "avg_duration":      {"pt": "Duração Média",          "en": "Avg. Duration"},
    "visits":            {"pt": "atendimentos",            "en": "visits"},
    "of_visits":         {"pt": "dos atendimentos",        "en": "of visits"},
    "per_visit":         {"pt": "por atendimento",         "en": "per visit"},

    # KPI labels — Tecnologia
    "total_mrr":         {"pt": "MRR Total",              "en": "Total MRR"},
    "total_arr":         {"pt": "ARR Total",              "en": "Total ARR"},
    "avg_nps":           {"pt": "NPS Médio",              "en": "Avg. NPS"},
    "churn_rate":        {"pt": "Taxa de Churn",          "en": "Churn Rate"},
    "contracts":         {"pt": "contratos",               "en": "contracts"},
    "arr_sub":           {"pt": "receita anual recorrente","en": "annual recurring revenue"},
    "nps_scale":         {"pt": "de 0 a 10",              "en": "score 0 to 10"},
    "of_contracts":      {"pt": "dos contratos",           "en": "of contracts"},

    # KPI labels — Educação
    "completion_rate":   {"pt": "Taxa de Conclusão",      "en": "Completion Rate"},
    "avg_grade":         {"pt": "Nota Média",             "en": "Avg. Grade"},
    "enrollments":       {"pt": "matrículas",              "en": "enrollments"},
    "of_students":       {"pt": "dos alunos",              "en": "of students"},
    "per_enrollment":    {"pt": "por matrícula",           "en": "per enrollment"},

    # KPI labels — Logística
    "freight_revenue":   {"pt": "Receita de Frete",       "en": "Freight Revenue"},
    "avg_freight":       {"pt": "Frete Médio",            "en": "Avg. Freight"},
    "delivery_rate":     {"pt": "Taxa de Entrega",        "en": "Delivery Rate"},
    "on_time":           {"pt": "Pontualidade",           "en": "On-Time Delivery"},
    "deliveries":        {"pt": "entregas",                "en": "deliveries"},
    "per_delivery":      {"pt": "por entrega",             "en": "per delivery"},
    "completed":         {"pt": "entregas concluídas",     "en": "completed deliveries"},
    "within_deadline":   {"pt": "dentro do prazo",         "en": "within deadline"},

    # KPI labels — Energia
    "total_consumption": {"pt": "Consumo Total",          "en": "Total Consumption"},
    "total_billing":     {"pt": "Faturamento Total",      "en": "Total Billing"},
    "avg_bill":          {"pt": "Fatura Média",           "en": "Avg. Bill"},
    "power_factor":      {"pt": "Fator de Potência",      "en": "Power Factor"},
    "readings":          {"pt": "leituras",                "en": "readings"},
    "all_bills":         {"pt": "todas as faturas",        "en": "all bills"},
    "per_reading":       {"pt": "por leitura",             "en": "per reading"},
    "overall_avg":       {"pt": "média geral",             "en": "overall avg."},

    # Títulos de gráficos — Varejo
    "monthly_revenue":       {"pt": "Receita Mensal",             "en": "Monthly Revenue"},
    "revenue_by_category":   {"pt": "Receita por Categoria",      "en": "Revenue by Category"},
    "revenue_by_channel":    {"pt": "Receita por Canal",          "en": "Revenue by Channel"},
    "top10_sellers":         {"pt": "Top 10 Vendedores",          "en": "Top 10 Sales Reps"},

    # Títulos de gráficos — Financeiro
    "monthly_volume":        {"pt": "Volume Transacionado por Mês","en": "Monthly Transaction Volume"},
    "volume_by_type":        {"pt": "Volume por Tipo de Transação","en": "Volume by Transaction Type"},
    "status_dist":           {"pt": "Distribuição por Status",     "en": "Distribution by Status"},
    "volume_by_product":     {"pt": "Volume por Categoria de Produto","en": "Volume by Product Category"},

    # Títulos de gráficos — Saúde
    "monthly_visits":        {"pt": "Atendimentos por Mês",       "en": "Monthly Visits"},
    "visits_by_specialty":   {"pt": "Atendimentos por Especialidade","en": "Visits by Specialty"},
    "result_dist":           {"pt": "Distribuição por Resultado",  "en": "Distribution by Outcome"},
    "revenue_by_plan":       {"pt": "Receita por Convênio",       "en": "Revenue by Health Plan"},

    # Títulos de gráficos — Tecnologia
    "mrr_by_month":          {"pt": "MRR por Mês",                "en": "MRR by Month"},
    "contracts_by_type":     {"pt": "Contratos por Tipo",         "en": "Contracts by Type"},
    "nps_dist":              {"pt": "Distribuição de NPS",        "en": "NPS Distribution"},
    "mrr_by_segment":        {"pt": "MRR por Segmento de Cliente","en": "MRR by Customer Segment"},

    # Títulos de gráficos — Educação
    "monthly_enrollments":   {"pt": "Matrículas por Mês",         "en": "Monthly Enrollments"},
    "by_modality":           {"pt": "Matrículas por Modalidade",  "en": "Enrollments by Modality"},
    "revenue_by_area":       {"pt": "Receita por Área",           "en": "Revenue by Area"},
    "grade_dist":            {"pt": "Distribuição de Notas Finais","en": "Final Grade Distribution"},

    # Títulos de gráficos — Logística
    "monthly_freight":       {"pt": "Receita de Frete por Mês",   "en": "Monthly Freight Revenue"},
    "delivery_status":       {"pt": "Status das Entregas",        "en": "Delivery Status"},
    "top_carriers":          {"pt": "Top Transportadoras por Receita","en": "Top Carriers by Revenue"},
    "avg_delay_type":        {"pt": "Atraso Médio por Tipo de Transporte","en": "Avg. Delay by Transport Type"},

    # Títulos de gráficos — Energia
    "monthly_consumption":   {"pt": "Consumo Mensal (kWh)",       "en": "Monthly Consumption (kWh)"},
    "consumption_by_class":  {"pt": "Consumo por Classe",         "en": "Consumption by Class"},
    "tariff_evolution":      {"pt": "Evolução da Tarifa Média",   "en": "Avg. Tariff Evolution"},
    "revenue_by_class":      {"pt": "Receita por Classe",         "en": "Revenue by Class"},

    # Títulos de gráficos — Agronegócio
    "top10_crops":           {"pt": "Top 10 Culturas por Produção","en": "Top 10 Crops by Production"},
    "top10_productivity":    {"pt": "Top 10 Culturas por Produtividade","en": "Top 10 Crops by Productivity"},
    "harvest_status":        {"pt": "Status das Safras",          "en": "Harvest Status"},

    # Títulos de gráficos — Turismo
    "revenue_by_country":    {"pt": "Receita por País de Destino","en": "Revenue by Destination Country"},

    # Títulos de gráficos — Imobiliário
    "monthly_business":      {"pt": "Volume Mensal de Negócios",  "en": "Monthly Business Volume"},
    "by_property_type":      {"pt": "Volume por Tipo de Imóvel",  "en": "Volume by Property Type"},

    # Títulos de gráficos — Seguros
    "monthly_premiums":      {"pt": "Prêmios Emitidos por Mês",  "en": "Monthly Premiums Issued"},
    "premiums_by_type":      {"pt": "Prêmios por Tipo de Seguro","en": "Premiums by Insurance Type"},

    # Títulos de gráficos — Construção
    "monthly_costs":         {"pt": "Evolução de Custos Mensais", "en": "Monthly Cost Evolution"},
    "top10_projects":        {"pt": "Top 10 Projetos por Custo",  "en": "Top 10 Projects by Cost"},

    # Axis labels
    "revenue_brl":           {"pt": "Receita (R$)",               "en": "Revenue (BRL)"},
    "volume_brl":            {"pt": "Volume (R$)",                 "en": "Volume (BRL)"},
    "cost_brl":              {"pt": "Custo (R$)",                  "en": "Cost (BRL)"},
    "month":                 {"pt": "Mês",                         "en": "Month"},
    "name":                  {"pt": "Nome",                        "en": "Name"},
    "type":                  {"pt": "Tipo",                        "en": "Type"},
    "status":                {"pt": "Status",                      "en": "Status"},
    "delay_days":            {"pt": "Dias de Atraso Médio",        "en": "Avg. Delay Days"},
    "score":                 {"pt": "Score",                       "en": "Score"},
    "contracts_axis":        {"pt": "Contratos",                   "en": "Contracts"},
    "visits_axis":           {"pt": "Atendimentos",                "en": "Visits"},
    "enrollments_axis":      {"pt": "Matrículas",                  "en": "Enrollments"},
    "calls_axis":            {"pt": "Número de Chamadas",          "en": "Number of Calls"},
    "specialty":             {"pt": "Especialidade",               "en": "Specialty"},
    "category":              {"pt": "Categoria",                   "en": "Category"},
    "class_":                {"pt": "Classe",                      "en": "Class"},
    "modality":              {"pt": "Modalidade",                  "en": "Modality"},
    "area":                  {"pt": "Área",                        "en": "Area"},
    "grade":                 {"pt": "Nota Final",                  "en": "Final Grade"},
    "students":              {"pt": "Alunos",                      "en": "Students"},
    "consumption_kwh":       {"pt": "Consumo (kWh)",               "en": "Consumption (kWh)"},
    "tariff_avg":            {"pt": "Tarifa Média (R$/kWh)",       "en": "Avg. Tariff (BRL/kWh)"},
    "premiums_brl":          {"pt": "Prêmios (R$)",                "en": "Premiums (BRL)"},
    "freight_brl":           {"pt": "Receita (R$)",                "en": "Revenue (BRL)"},
    "production_ton":        {"pt": "Produção (ton)",              "en": "Production (tons)"},
    "productivity_tha":      {"pt": "Produtividade (t/ha)",        "en": "Productivity (t/ha)"},
    "crop":                  {"pt": "Cultura",                     "en": "Crop"},
    "country":               {"pt": "País",                        "en": "Country"},
    "property_type":         {"pt": "Tipo de Imóvel",             "en": "Property Type"},
    "project":               {"pt": "Projeto",                     "en": "Project"},
    "machine":               {"pt": "Máquina",                     "en": "Machine"},
    "qty_produced":          {"pt": "Quantidade Produzida",        "en": "Quantity Produced"},

    # KPI labels — Turismo
    "cancel_rate":           {"pt": "Taxa de Cancelamento",       "en": "Cancellation Rate"},
    "total_passengers":      {"pt": "Total Passageiros",          "en": "Total Passengers"},
    "per_booking":           {"pt": "por reserva",                "en": "per booking"},
    "cancelled_status":      {"pt": "status cancelado",           "en": "cancelled status"},
    "persons":               {"pt": "pessoas",                    "en": "persons"},

    # KPI labels — Imobiliário
    "business_volume":       {"pt": "Volume de Negócios",         "en": "Business Volume"},
    "pct_sales":             {"pt": "% Vendas",                   "en": "% Sales"},
    "avg_area":              {"pt": "Área Média",                 "en": "Avg. Area"},
    "per_contract":          {"pt": "por contrato",               "en": "per contract"},
    "vs_rentals":            {"pt": "vs Aluguéis",                "en": "vs Rentals"},
    "per_property":          {"pt": "por imóvel",                 "en": "per property"},

    # KPI labels — Seguros
    "total_premiums":        {"pt": "Prêmios Totais",             "en": "Total Premiums"},
    "paid_claims":           {"pt": "Indenizações Pago",          "en": "Claims Paid"},
    "loss_ratio":            {"pt": "Loss Ratio",                 "en": "Loss Ratio"},
    "avg_premium":           {"pt": "Prêmio Médio",              "en": "Avg. Premium"},
    "policies":              {"pt": "apólices",                   "en": "policies"},
    "claims_paid":           {"pt": "sinistros pagos",            "en": "claims paid"},
    "sp_ratio":              {"pt": "S/P",                        "en": "S/P ratio"},
    "per_policy":            {"pt": "por apólice",                "en": "per policy"},

    # KPI labels — Construção
    "total_real_cost":       {"pt": "Custo Real Total",           "en": "Total Real Cost"},
    "total_hours":           {"pt": "Total Horas",                "en": "Total Hours"},
    "cost_per_hour":         {"pt": "Custo Médio/Hora",           "en": "Avg. Cost/Hour"},
    "num_projects":          {"pt": "Qtd. Projetos",              "en": "No. of Projects"},
    "cost_entries":          {"pt": "lançamentos",                "en": "cost entries"},
    "labor":                 {"pt": "mão de obra",                "en": "labor"},
    "efficiency":            {"pt": "eficiência",                  "en": "efficiency"},
    "active_projects":       {"pt": "obras ativas",               "en": "active projects"},

    # KPI labels — Indústria
    "total_production":      {"pt": "Produção Total",             "en": "Total Production"},
    "scrap_rate":            {"pt": "Taxa de Refugo",             "en": "Scrap Rate"},
    "avg_oee":               {"pt": "OEE Médio",                  "en": "Avg. OEE"},
    "total_cost":            {"pt": "Custo Total",                "en": "Total Cost"},
    "unit_plural":           {"pt": "unidades",                   "en": "units"},
    "loss":                  {"pt": "perda",                      "en": "loss"},
    "global_efficiency":     {"pt": "eficiência global",          "en": "global efficiency"},
    "production_sub":        {"pt": "produção",                   "en": "production"},
    "production_by_machine": {"pt": "Produção por Máquina",       "en": "Production by Machine"},

    # Telecom KPIs
    "total_calls":           {"pt": "Total Chamadas",             "en": "Total Calls"},
    "avg_duration":          {"pt": "Duração Média",              "en": "Avg. Duration"},
    "total_cost":            {"pt": "Custo Total",                "en": "Total Cost"},
    "avg_data":              {"pt": "Dados MB",                   "en": "Data MB"},
    "avg_quality":           {"pt": "Qualidade Média",            "en": "Avg. Quality"},
    "quality_dbm":           {"pt": "Qualidade dBm",              "en": "Quality dBm"},
    "in_period":             {"pt": "no período",                 "en": "in period"},
    "per_call":              {"pt": "por chamada",                "en": "per call"},
    "billed_calls":          {"pt": "chamadas tarifadas",         "en": "billed calls"},
    "avg_per_call":          {"pt": "médio por chamada",          "en": "avg. per call"},
    "signal_score":          {"pt": "score de sinal",             "en": "signal score"},
    "avg_signal":            {"pt": "sinal médio",                "en": "avg. signal"},
    "daily_calls":           {"pt": "Volume Diário de Chamadas",  "en": "Daily Call Volume"},
    "no_machine_data":       {"pt": "Dados de máquina não disponíveis para esta base.", "en": "Machine data not available for this dataset."},
}


def td(key: str, **kwargs) -> str:
    """Tradução para textos de dashboard."""
    lang = get_lang()
    text = _DASH.get(key, {}).get(lang, _DASH.get(key, {}).get("pt", key))
    if kwargs:
        text = text.format(**kwargs)
    return text


# Mapeamento nome EN → nome PT para o dispatcher de dashboards
SECTOR_NAME_MAP: dict[str, str] = {
    "Agribusiness":           "Agronegócio",
    "Food & Beverage":        "Alimentos & Bebidas",
    "Construction":           "Construção Civil",
    "CRM":                    "CRM",
    "E-commerce":             "E-commerce",
    "Education":              "Educação",
    "Energy":                 "Energia",
    "Sports":                 "Esportes",
    "Pharmaceutical":         "Farmacêutico",
    "Financial":              "Financeiro",
    "Fintech":                "Fintech",
    "Government & Public Sector": "Governo & Setor Público",
    "Hospitality":            "Hotelaria",
    "Real Estate":            "Imobiliário",
    "Manufacturing":          "Indústria",
    "Legal":                  "Jurídico",
    "Logistics":              "Logística",
    "Digital Marketing":      "Marketing Digital",
    "Mining":                 "Mineração",
    "Mobility":               "Mobilidade",
    "Oil & Gas":              "Petróleo & Gás",
    "Human Resources":        "Recursos Humanos",
    "SaaS B2B":               "SaaS B2B",
    "Healthcare":             "Saúde",
    "Insurance":              "Seguros",
    "Streaming":              "Streaming",
    "Technology":             "Tecnologia",
    "Telecom":                "Telecom",
    "Tourism":                "Turismo",
    "Retail":                 "Varejo",
}


def resolve_sector_name(nome: str) -> str:
    """Converte nome EN para PT se necessário (para o dispatcher de dashboards)."""
    return SECTOR_NAME_MAP.get(nome, nome)


# ── Traduções do Dashboard ────────────────────────────────────────────────────

_DASH_STRINGS: dict[str, dict[str, str]] = {
    # Seções
    "overview":           {"pt": "Visão Geral",          "en": "Overview"},
    "channels":           {"pt": "Canais",                "en": "Channels"},
    "distribution":       {"pt": "Distribuição",          "en": "Distribution"},
    "results":            {"pt": "Resultados",            "en": "Results"},
    "segmentation":       {"pt": "Segmentação",           "en": "Segmentation"},
    "area_performance":   {"pt": "Performance por Área",  "en": "Area Performance"},
    "carriers_routes":    {"pt": "Transportadoras & Rotas","en": "Carriers & Routes"},
    "tariffs":            {"pt": "Tarifas",               "en": "Tariffs"},

    # KPI labels
    "total_revenue":      {"pt": "RECEITA TOTAL",         "en": "TOTAL REVENUE"},
    "total_volume":       {"pt": "VOLUME TOTAL",          "en": "TOTAL VOLUME"},
    "total_premiums":     {"pt": "PRÊMIOS TOTAIS",        "en": "TOTAL PREMIUMS"},
    "total_production":   {"pt": "PRODUÇÃO TOTAL",        "en": "TOTAL PRODUCTION"},
    "total_consumption":  {"pt": "CONSUMO TOTAL",         "en": "TOTAL CONSUMPTION"},
    "total_mrr":          {"pt": "MRR TOTAL",             "en": "TOTAL MRR"},
    "total_real_cost":    {"pt": "CUSTO REAL TOTAL",      "en": "TOTAL REAL COST"},
    "avg_ticket":         {"pt": "TICKET MÉDIO",          "en": "AVG TICKET"},
    "avg_value":          {"pt": "VALOR MÉDIO",           "en": "AVG VALUE"},
    "avg_cost":           {"pt": "CUSTO MÉDIO",           "en": "AVG COST"},
    "avg_discount":       {"pt": "DESCONTO MÉDIO",        "en": "AVG DISCOUNT"},
    "avg_qty":            {"pt": "QTD MÉDIA",             "en": "AVG QTY"},
    "avg_delay_type":     {"pt": "ATRASO MÉDIO / TIPO",   "en": "AVG DELAY / TYPE"},
    "avg_per_call":       {"pt": "DURAÇÃO MÉDIA",         "en": "AVG DURATION"},
    "avg_signal":         {"pt": "SINAL MÉDIO",           "en": "AVG SIGNAL"},
    "approval_rate":      {"pt": "TAXA APROVAÇÃO",        "en": "APPROVAL RATE"},
    "discharge_rate":     {"pt": "TAXA DE ALTA",          "en": "DISCHARGE RATE"},
    "global_efficiency":  {"pt": "EFICIÊNCIA GLOBAL",     "en": "GLOBAL EFFICIENCY"},
    "efficiency":         {"pt": "EFICIÊNCIA",            "en": "EFFICIENCY"},
    "productivity":       {"pt": "PRODUTIVIDADE",         "en": "PRODUCTIVITY"},
    "nps_scale":          {"pt": "NPS MÉDIO",             "en": "AVG NPS"},
    "arr_sub":            {"pt": "ARR / ASSINANTE",       "en": "ARR / SUBSCRIBER"},
    "sp_ratio":           {"pt": "SINISTRO / PRÊMIO",     "en": "LOSS RATIO"},
    "claims_paid":        {"pt": "SINISTROS PAGOS",       "en": "CLAIMS PAID"},
    "score":              {"pt": "SCORE",                 "en": "SCORE"},
    "signal_score":       {"pt": "SCORE DE SINAL",        "en": "SIGNAL SCORE"},
    "business_volume":    {"pt": "VOLUME DE NEGÓCIOS",    "en": "BUSINESS VOLUME"},
    "freight_revenue":    {"pt": "RECEITA DE FRETE",      "en": "FREIGHT REVENUE"},

    # KPI sub-labels
    "sales":              {"pt": "vendas",                "en": "sales"},
    "transactions":       {"pt": "transações",            "en": "transactions"},
    "visits":             {"pt": "atendimentos",          "en": "visits"},
    "enrollments":        {"pt": "matrículas",            "en": "enrollments"},
    "students":           {"pt": "alunos",                "en": "students"},
    "persons":            {"pt": "pessoas",               "en": "persons"},
    "units":              {"pt": "unidades",              "en": "units"},
    "contracts_axis":     {"pt": "contratos",             "en": "contracts"},
    "billed_calls":       {"pt": "chamadas faturadas",    "en": "billed calls"},
    "daily_calls":        {"pt": "chamadas / dia",        "en": "calls / day"},
    "in_period":          {"pt": "no período",            "en": "in period"},
    "of_contracts":       {"pt": "dos contratos",         "en": "of contracts"},
    "of_students":        {"pt": "dos alunos",            "en": "of students"},
    "of_visits":          {"pt": "dos atendimentos",      "en": "of visits"},
    "per_sale":           {"pt": "por venda",             "en": "per sale"},
    "per_tx":             {"pt": "por transação",         "en": "per transaction"},
    "per_visit":          {"pt": "por atendimento",       "en": "per visit"},
    "per_enrollment":     {"pt": "por matrícula",         "en": "per enrollment"},
    "per_booking":        {"pt": "por reserva",           "en": "per booking"},
    "per_delivery":       {"pt": "por entrega",           "en": "per delivery"},
    "per_contract":       {"pt": "por contrato",          "en": "per contract"},
    "per_policy":         {"pt": "por apólice",           "en": "per policy"},
    "per_property":       {"pt": "por imóvel",            "en": "per property"},
    "per_reading":        {"pt": "por leitura",           "en": "per reading"},
    "per_call":           {"pt": "por chamada",           "en": "per call"},
    "after_tx":           {"pt": "após transação",        "en": "after transaction"},
    "approved_tx":        {"pt": "tx aprovadas",          "en": "approved tx"},
    "on_full_price":      {"pt": "sobre preço cheio",     "en": "on full price"},
    "within_deadline":    {"pt": "no prazo",              "en": "on time"},
    "completed":          {"pt": "concluídos",            "en": "completed"},
    "cancelled_status":   {"pt": "cancelados",            "en": "cancelled"},
    "all_bills":          {"pt": "todas as faturas",      "en": "all bills"},
    "production_sub":     {"pt": "toneladas colhidas",    "en": "harvested tons"},
    "overall_avg":        {"pt": "média geral",           "en": "overall avg"},
    "loss":               {"pt": "perda",                 "en": "loss"},
    "labor":              {"pt": "mão de obra",           "en": "labor"},
    "active_projects":    {"pt": "projetos ativos",       "en": "active projects"},
    "vs_rentals":         {"pt": "vs aluguéis",           "en": "vs rentals"},

    # Eixos e títulos de gráficos
    "revenue_brl":        {"pt": "Receita (R$)",          "en": "Revenue (R$)"},
    "volume_brl":         {"pt": "Volume (R$)",           "en": "Volume (R$)"},
    "premiums_brl":       {"pt": "Prêmios (R$)",          "en": "Premiums (R$)"},
    "cost_brl":           {"pt": "Custo (R$)",            "en": "Cost (R$)"},
    "calls_axis":         {"pt": "Chamadas",              "en": "Calls"},
    "visits_axis":        {"pt": "Atendimentos",          "en": "Visits"},
    "enrollments_axis":   {"pt": "Matrículas",            "en": "Enrollments"},
    "consumption_kwh":    {"pt": "Consumo (kWh)",         "en": "Consumption (kWh)"},
    "specialty":          {"pt": "Especialidade",         "en": "Specialty"},
    "class_":             {"pt": "Classe",                "en": "Class"},
    "area":               {"pt": "Área",                  "en": "Area"},
    "country":            {"pt": "País",                  "en": "Country"},
    "crop":               {"pt": "Cultura",               "en": "Crop"},
    "machine":            {"pt": "Máquina",               "en": "Machine"},
    "project":            {"pt": "Projeto",               "en": "Project"},
    "unit_plural":        {"pt": "unidades",              "en": "units"},

    # Títulos de gráficos
    "monthly_revenue":        {"pt": "Receita Mensal",             "en": "Monthly Revenue"},
    "monthly_volume":         {"pt": "Volume Mensal",              "en": "Monthly Volume"},
    "monthly_visits":         {"pt": "Atendimentos Mensais",       "en": "Monthly Visits"},
    "monthly_enrollments":    {"pt": "Matrículas Mensais",         "en": "Monthly Enrollments"},
    "monthly_consumption":    {"pt": "Consumo Mensal",             "en": "Monthly Consumption"},
    "monthly_premiums":       {"pt": "Prêmios Mensais",            "en": "Monthly Premiums"},
    "monthly_costs":          {"pt": "Custos Mensais",             "en": "Monthly Costs"},
    "monthly_freight":        {"pt": "Frete Mensal",               "en": "Monthly Freight"},
    "monthly_business":       {"pt": "Negócios Mensais",           "en": "Monthly Business"},
    "mrr_by_month":           {"pt": "MRR por Mês",                "en": "MRR by Month"},
    "mrr_by_segment":         {"pt": "MRR por Segmento",           "en": "MRR by Segment"},
    "revenue_by_category":    {"pt": "Top 10 Categorias por Receita","en": "Top 10 Categories by Revenue"},
    "revenue_by_channel":     {"pt": "Receita por Canal",          "en": "Revenue by Channel"},
    "revenue_by_class":       {"pt": "Receita por Classe",         "en": "Revenue by Class"},
    "revenue_by_area":        {"pt": "Receita por Área",           "en": "Revenue by Area"},
    "revenue_by_plan":        {"pt": "Receita por Plano",          "en": "Revenue by Plan"},
    "revenue_by_country":     {"pt": "Receita por País",           "en": "Revenue by Country"},
    "volume_by_type":         {"pt": "Volume por Tipo",            "en": "Volume by Type"},
    "volume_by_product":      {"pt": "Volume por Produto",         "en": "Volume by Product"},
    "premiums_by_type":       {"pt": "Prêmios por Tipo",           "en": "Premiums by Type"},
    "contracts_by_type":      {"pt": "Contratos por Tipo",         "en": "Contracts by Type"},
    "consumption_by_class":   {"pt": "Consumo por Classe",         "en": "Consumption by Class"},
    "visits_by_specialty":    {"pt": "Atendimentos por Especialidade","en":"Visits by Specialty"},
    "status_dist":            {"pt": "Distribuição por Status",    "en": "Status Distribution"},
    "result_dist":            {"pt": "Distribuição por Resultado", "en": "Result Distribution"},
    "grade_dist":             {"pt": "Distribuição de Notas",      "en": "Grade Distribution"},
    "nps_dist":               {"pt": "Distribuição NPS",           "en": "NPS Distribution"},
    "harvest_status":         {"pt": "Status das Safras",          "en": "Harvest Status"},
    "delivery_status":        {"pt": "Status de Entregas",         "en": "Delivery Status"},
    "tariff_avg":             {"pt": "Tarifa Média por Classe",    "en": "Avg Tariff by Class"},
    "tariff_evolution":       {"pt": "Evolução da Tarifa",         "en": "Tariff Evolution"},
    "top10_sellers":          {"pt": "Top 10 Vendedores",          "en": "Top 10 Sellers"},
    "top10_crops":            {"pt": "Top 10 Culturas por Produção","en": "Top 10 Crops by Production"},
    "top10_productivity":     {"pt": "Top 10 Produtividade",       "en": "Top 10 Productivity"},
    "top10_projects":         {"pt": "Top 10 Projetos",            "en": "Top 10 Projects"},
    "top_carriers":           {"pt": "Top Transportadoras",        "en": "Top Carriers"},
    "production_by_machine":  {"pt": "Produção por Máquina",       "en": "Production by Machine"},
    "no_machine_data":        {"pt": "Sem dados de máquinas",      "en": "No machine data"},
    "by_modality":            {"pt": "Por Modalidade",             "en": "By Modality"},
    "by_property_type":       {"pt": "Por Tipo de Imóvel",         "en": "By Property Type"},
    "delay_days":             {"pt": "Dias de Atraso",             "en": "Delay Days"},
}


def td(key: str, **kwargs) -> str:
    """Traduz uma chave do dashboard para o idioma atual."""
    lang = get_lang()
    text = _DASH_STRINGS.get(key, {}).get(lang, _DASH_STRINGS.get(key, {}).get("pt", key))
    if kwargs:
        text = text.format(**kwargs)
    return text


_SECTOR_NAME_MAP: dict[str, str] = {
    "Agronegócio":          "Agribusiness",
    "Alimentos & Bebidas":  "Food & Beverage",
    "Construção Civil":     "Construction",
    "CRM":                  "CRM",
    "E-commerce":           "E-commerce",
    "Educação":             "Education",
    "Energia":              "Energy",
    "Esportes":             "Sports",
    "Farmacêutico":         "Pharmaceutical",
    "Financeiro":           "Financial",
    "Fintech":              "Fintech",
    "Governo & Setor Público": "Government & Public Sector",
    "Hotelaria":            "Hospitality",
    "Imobiliário":          "Real Estate",
    "Indústria":            "Manufacturing",
    "Jurídico":             "Legal",
    "Logística":            "Logistics",
    "Marketing Digital":    "Digital Marketing",
    "Mineração":            "Mining",
    "Mobilidade":           "Mobility",
    "Petróleo & Gás":       "Oil & Gas",
    "Recursos Humanos":     "Human Resources",
    "SaaS B2B":             "SaaS B2B",
    "Saúde":                "Healthcare",
    "Seguros":              "Insurance",
    "Streaming":            "Streaming",
    "Tecnologia":           "Technology",
    "Telecom":              "Telecom",
    "Turismo":              "Tourism",
    "Varejo":               "Retail",
}


def resolve_sector_name(nome: str) -> str:
    """Traduz o nome do setor para o idioma atual (usado no título do dashboard)."""
    if get_lang() == "en":
        return _SECTOR_NAME_MAP.get(nome, nome)
    return nome
