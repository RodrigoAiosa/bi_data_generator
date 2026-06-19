from generators import (
    gerar_varejo, gerar_financeiro, gerar_saude, gerar_tecnologia,
    gerar_educacao, gerar_logistica, gerar_energia, gerar_telecom,
    gerar_industria, gerar_agronegocio, gerar_hotelaria, gerar_streaming,
    gerar_ecommerce, gerar_rh, gerar_mobilidade, gerar_fintech,
    gerar_turismo, gerar_imobiliario, gerar_seguros, gerar_construcao,
    gerar_mineracao, gerar_alimenticio, gerar_juridico, gerar_esportes,
    gerar_saas_b2b, gerar_crm, gerar_farmaceutico, gerar_marketing,
    gerar_petroleo, gerar_governo
)

# Configuração da página Streamlit
PAGE_CONFIG = {
    "page_title": "BI Data Generator PRO",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Configurações do slider de linhas
SLIDER_MIN = 100
SLIDER_MAX = 100000
SLIDER_DEFAULT = 5000
SLIDER_STEP = 100

# Dicionário de setores disponíveis (30 setores) — ordem alfabética
SETORES = {
    "🌾 Agronegócio":         gerar_agronegocio,
    "🍔 Alimentos & Bebidas": gerar_alimenticio,
    "🏗️ Construção Civil":   gerar_construcao,
    "🤝 CRM":                 gerar_crm,
    "🏪 E-commerce":          gerar_ecommerce,
    "📚 Educação":            gerar_educacao,
    "⚡ Energia":             gerar_energia,
    "🏟️ Esportes":           gerar_esportes,
    "💊 Farmacêutico":        gerar_farmaceutico,
    "💰 Financeiro":          gerar_financeiro,
    "🏦 Fintech":             gerar_fintech,
    "🏛️ Governo & Setor Público": gerar_governo,
    "🏨 Hotelaria":           gerar_hotelaria,
    "🏠 Imobiliário":         gerar_imobiliario,
    "🏭 Indústria":           gerar_industria,
    "⚖️ Jurídico":           gerar_juridico,
    "🚚 Logística":           gerar_logistica,
    "📣 Marketing Digital":   gerar_marketing,
    "⛏️ Mineração":          gerar_mineracao,
    "🚗 Mobilidade":          gerar_mobilidade,
    "🛢️ Petróleo & Gás":     gerar_petroleo,
    "🏢 Recursos Humanos":    gerar_rh,
    "☁️ SaaS B2B":           gerar_saas_b2b,
    "🏥 Saúde":               gerar_saude,
    "🛡️ Seguros":            gerar_seguros,
    "🎬 Streaming":           gerar_streaming,
    "💻 Tecnologia":          gerar_tecnologia,
    "📡 Telecom":             gerar_telecom,
    "✈️ Turismo":             gerar_turismo,
    "🛒 Varejo":              gerar_varejo,
}

# Informações para os flip-cards da tela inicial (30 setores) — ordem alfabética
SETORES_INFO = [
    ("🌾", "Agronegócio",           "Safras, culturas, propriedades e insumos"),
    ("🍔", "Alimentos & Bebidas",   "Produção, plantas, produtos e fornecedores"),
    ("🏗️", "Construção Civil",     "Obras, custos, materiais e fornecedores"),
    ("🤝", "CRM",                   "Oportunidades, contas, contatos e atividades comerciais"),
    ("🏪", "E-commerce",            "Pedidos, clientes, produtos, fretes e pagamentos"),
    ("📚", "Educação",              "Matrículas, alunos, cursos e instrutores"),
    ("⚡", "Energia",               "Consumo, medidores, subestações e tarifas"),
    ("🏟️", "Esportes",             "Partidas, atletas, clubes e competições"),
    ("💊", "Farmacêutico",          "Produtos, representantes, vendas e estoque"),
    ("💰", "Financeiro",            "Transações bancárias, contas e agências"),
    ("🏦", "Fintech",               "Transações, cartões, usuários, comerciantes e antifraude"),
    ("🏛️", "Governo & Setor Público", "Despesas, receitas, licitações e contratos"),
    ("🏨", "Hotelaria",             "Reservas, hóspedes, hotéis, quartos e canais"),
    ("🏠", "Imobiliário",           "Vendas, aluguéis, imóveis e corretores"),
    ("🏭", "Indústria",             "Produção, máquinas, insumos e operadores"),
    ("⚖️", "Jurídico",             "Processos, advogados, clientes e tribunais"),
    ("🚚", "Logística",             "Entregas, transportadoras, rotas e clientes"),
    ("📣", "Marketing Digital",     "Campanhas, canais, performance e conversões"),
    ("⛏️", "Mineração",            "Extrações, minas, minerais e equipamentos"),
    ("🚗", "Mobilidade",            "Viagens, motoristas, passageiros, rotas e veículos"),
    ("🛢️", "Petróleo & Gás",       "Produção, poços, plataformas e custos operacionais"),
    ("🏢", "Recursos Humanos",      "Horas trabalhadas, funcionários, projetos e cargos"),
    ("☁️", "SaaS B2B",             "Assinaturas, MRR, churn, NPS e planos"),
    ("🏥", "Saúde",                 "Atendimentos, pacientes, médicos e procedimentos"),
    ("🛡️", "Seguros",              "Apólices, segurados, corretores e sinistros"),
    ("🎬", "Streaming",             "Plays, assinantes, conteúdos, artistas"),
    ("💻", "Tecnologia",            "Contratos SaaS, clientes e planos"),
    ("📡", "Telecom",               "Chamadas, assinantes, planos e torres"),
    ("✈️", "Turismo",               "Viagens, pacotes, agências e destinos"),
    ("🛒", "Varejo",                "Vendas, clientes, produtos e filiais"),
]

# Configurações de datas (opcional)
DATE_DEFAULT_START = "2023-01-01"
DATE_DEFAULT_END   = "2023-12-31"
