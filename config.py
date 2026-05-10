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
    ("🌾", "Agronegócio",        "Safras, culturas, propriedades e insumos"),
    ("🍔", "Alimentos & Bebidas","Produção, plantas, produtos e fornecedores"),
    ("🏗️", "Construção Civil",  "Obras, custos, materiais e fornecedores"),
    ("🏪", "E-commerce",         "Pedidos, clientes, produtos, fretes e pagamentos"),
    ("📚", "Educação",           "Matrículas, alunos, cursos e instrutores"),
    ("⚡", "Energia",            "Consumo, medidores, subestações e tarifas"),
    ("🏟️", "Esportes",          "Partidas, atletas, clubes e competições"),
    ("💰", "Financeiro",         "Transações bancárias, contas e agências"),
    ("🏦", "Fintech",            "Transações, cartões, usuários, comerciantes e antifraude"),
    ("🏨", "Hotelaria",          "Reservas, hóspedes, hotéis, quartos e canais"),
    ("🏠", "Imobiliário",        "Vendas, aluguéis, imóveis e corretores"),
    ("🏭", "Indústria",          "Produção, máquinas, insumos e operadores"),
    ("⚖️", "Jurídico",          "Processos, advogados, clientes e tribunais"),
    ("🚚", "Logística",          "Entregas, transportadoras, rotas e clientes"),
    ("⛏️", "Mineração",         "Extrações, minas, minerais e equipamentos"),
    ("🚗", "Mobilidade",         "Viagens, motoristas, passageiros, rotas e veículos"),
    ("🏢", "Recursos Humanos",   "Horas trabalhadas, funcionários, projetos e cargos"),
    ("☁️", "SaaS B2B",          "Assinaturas, MRR, churn, NPS e planos"),
    ("🏥", "Saúde",              "Atendimentos, pacientes, médicos e procedimentos"),
    ("🛡️", "Seguros",           "Apólices, segurados, corretores e sinistros"),
    ("🎬", "Streaming",          "Plays, assinantes, conteúdos, artistas"),
    ("💻", "Tecnologia",         "Contratos SaaS, clientes e planos"),
    ("📡", "Telecom",            "Chamadas, assinantes, planos e torres"),
    ("✈️", "Turismo",            "Viagens, pacotes, agências e destinos"),
    ("🛒", "Varejo",             "Vendas, clientes, produtos e filiais"),
]

# Configurações de datas (opcional)
DATE_DEFAULT_START = "2023-01-01"
DATE_DEFAULT_END   = "2023-12-31"
