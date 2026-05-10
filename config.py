from generators import (
    gerar_varejo, gerar_financeiro, gerar_saude, gerar_tecnologia,
    gerar_educacao, gerar_logistica, gerar_energia, gerar_telecom,
    gerar_industria, gerar_agronegocio, gerar_hotelaria, gerar_streaming,
    gerar_ecommerce, gerar_rh, gerar_mobilidade, gerar_fintech,
    gerar_turismo, gerar_imobiliario, gerar_seguros, gerar_construcao,
    gerar_mineracao, gerar_alimenticio, gerar_juridico, gerar_esportes,
    gerar_saas_b2b
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

# Dicionário de setores disponíveis (25 setores)
SETORES = {
    # — Originais —
    "🛒 Varejo":              gerar_varejo,
    "💰 Financeiro":          gerar_financeiro,
    "🏥 Saúde":               gerar_saude,
    "💻 Tecnologia":          gerar_tecnologia,
    "📚 Educação":            gerar_educacao,
    "🚚 Logística":           gerar_logistica,
    "⚡ Energia":             gerar_energia,
    "📡 Telecom":             gerar_telecom,
    "🏭 Indústria":           gerar_industria,
    "🌾 Agronegócio":         gerar_agronegocio,
    "🏨 Hotelaria":           gerar_hotelaria,
    "🎬 Streaming":           gerar_streaming,
    "🏪 E-commerce":          gerar_ecommerce,
    "🏢 Recursos Humanos":    gerar_rh,
    "🚗 Mobilidade":          gerar_mobilidade,
    "🏦 Fintech":             gerar_fintech,
    "✈️ Turismo":             gerar_turismo,
    "🏠 Imobiliário":         gerar_imobiliario,
    "🛡️ Seguros":            gerar_seguros,
    "🏗️ Construção Civil":   gerar_construcao,
    # — Novos —
    "⛏️ Mineração":          gerar_mineracao,
    "🍔 Alimentos & Bebidas": gerar_alimenticio,
    "⚖️ Jurídico":           gerar_juridico,
    "🏟️ Esportes":           gerar_esportes,
    "☁️ SaaS B2B":           gerar_saas_b2b,
}

# Informações para os flip-cards da tela inicial (25 setores)
SETORES_INFO = [
    # — Originais —
    ("🛒", "Varejo",             "Vendas, clientes, produtos e filiais"),
    ("💰", "Financeiro",         "Transações bancárias, contas e agências"),
    ("🏥", "Saúde",              "Atendimentos, pacientes, médicos e procedimentos"),
    ("💻", "Tecnologia",         "Contratos SaaS, clientes e planos"),
    ("📚", "Educação",           "Matrículas, alunos, cursos e instrutores"),
    ("🚚", "Logística",          "Entregas, transportadoras, rotas e clientes"),
    ("⚡", "Energia",            "Consumo, medidores, subestações e tarifas"),
    ("📡", "Telecom",            "Chamadas, assinantes, planos e torres"),
    ("🏭", "Indústria",          "Produção, máquinas, insumos e operadores"),
    ("🌾", "Agronegócio",        "Safras, culturas, propriedades e insumos"),
    ("🏨", "Hotelaria",          "Reservas, hóspedes, hotéis, quartos e canais"),
    ("🎬", "Streaming",          "Plays, assinantes, conteúdos, artistas"),
    ("🏪", "E-commerce",         "Pedidos, clientes, produtos, fretes e pagamentos"),
    ("🏢", "Recursos Humanos",   "Horas trabalhadas, funcionários, projetos e cargos"),
    ("🚗", "Mobilidade",         "Viagens, motoristas, passageiros, rotas e veículos"),
    ("🏦", "Fintech",            "Transações, cartões, usuários, comerciantes e antifraude"),
    ("✈️", "Turismo",            "Viagens, pacotes, agências e destinos"),
    ("🏠", "Imobiliário",        "Vendas, aluguéis, imóveis e corretores"),
    ("🛡️", "Seguros",           "Apólices, segurados, corretores e sinistros"),
    ("🏗️", "Construção Civil",  "Obras, custos, materiais e fornecedores"),
    # — Novos —
    ("⛏️", "Mineração",         "Extrações, minas, minerais e equipamentos"),
    ("🍔", "Alimentos & Bebidas","Produção, plantas, produtos e fornecedores"),
    ("⚖️", "Jurídico",          "Processos, advogados, clientes e tribunais"),
    ("🏟️", "Esportes",          "Partidas, atletas, clubes e competições"),
    ("☁️", "SaaS B2B",          "Assinaturas, MRR, churn, NPS e planos"),
]

# Configurações de datas (opcional)
DATE_DEFAULT_START = "2023-01-01"
DATE_DEFAULT_END   = "2023-12-31"
