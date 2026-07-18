from generators import (
    gerar_varejo, gerar_financeiro, gerar_saude, gerar_tecnologia,
    gerar_educacao, gerar_logistica, gerar_energia, gerar_telecom,
    gerar_industria, gerar_agronegocio, gerar_hotelaria, gerar_streaming,
    gerar_ecommerce, gerar_rh, gerar_mobilidade, gerar_fintech,
    gerar_turismo, gerar_imobiliario, gerar_seguros, gerar_construcao,
    gerar_mineracao, gerar_alimenticio, gerar_juridico, gerar_esportes,
    gerar_saas_b2b, gerar_crm, gerar_farmaceutico, gerar_marketing,
    gerar_petroleo, gerar_governo, gerar_portabilidade_claro,
    gerar_aviacao, gerar_pet, gerar_games, gerar_saneamento, gerar_transporte,
    gerar_moda, gerar_eventos, gerar_laboratorio, gerar_franquias, gerar_condominio,
    gerar_saude_mental, gerar_florestal, gerar_startup, gerar_audiovisual, gerar_pesca,
    gerar_textil, gerar_arquitetura, gerar_viagem_corp, gerar_espacial, gerar_beleza,
    gerar_logistica_urbana,
    # ═══════ NOVOS SETORES ═══════
    gerar_agtech, gerar_economia_circular, gerar_biotecnologia
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

# ═══════════════════════════════════════════════════════════════
# Dicionário de setores disponíveis (55 setores) — ordem alfabética
# ═══════════════════════════════════════════════════════════════
SETORES = {
    "🌱 AgTech":                      gerar_agtech,
    "🌾 Agronegócio":                 gerar_agronegocio,
    "🍔 Alimentos & Bebidas":         gerar_alimenticio,
    "🏛️ Arquitetura & Design":        gerar_arquitetura,
    "🎬 Audiovisual & Produtora":     gerar_audiovisual,
    "✈️ Aviação Civil":               gerar_aviacao,
    "💄 Beleza & Estética":           gerar_beleza,
    "🧬 Biotecnologia":               gerar_biotecnologia,
    "🏢 Condomínio & Facilities":     gerar_condominio,
    "🏗️ Construção Civil":            gerar_construcao,
    "🤝 CRM":                         gerar_crm,
    "♻️ Economia Circular":           gerar_economia_circular,
    "🏪 E-commerce":                  gerar_ecommerce,
    "📚 Educação":                    gerar_educacao,
    "⚡ Energia":                     gerar_energia,
    "🚀 Espacial & Aeroespacial":     gerar_espacial,
    "🏟️ Esportes":                   gerar_esportes,
    "🎉 Eventos & Entretenimento":    gerar_eventos,
    "💊 Farmacêutico":                gerar_farmaceutico,
    "💰 Financeiro":                  gerar_financeiro,
    "🏦 Fintech":                     gerar_fintech,
    "🌲 Florestal & Papel":           gerar_florestal,
    "🏷️ Franquias":                  gerar_franquias,
    "🎮 Games & eSports":             gerar_games,
    "🏛️ Governo & Setor Público":    gerar_governo,
    "🏨 Hotelaria":                   gerar_hotelaria,
    "🏠 Imobiliário":                 gerar_imobiliario,
    "🏭 Indústria":                   gerar_industria,
    "⚖️ Jurídico":                   gerar_juridico,
    "🔬 Laboratório & Diagnóstico":   gerar_laboratorio,
    "🚚 Logística":                   gerar_logistica,
    "🚴 Logística Urbana":            gerar_logistica_urbana,
    "📣 Marketing Digital":           gerar_marketing,
    "📲 Migração Claro Brasil (Portabilidade)": gerar_portabilidade_claro,
    "⛏️ Mineração":                  gerar_mineracao,
    "🚗 Mobilidade":                  gerar_mobilidade,
    "👗 Moda & Vestuário":            gerar_moda,
    "🐟 Pesca & Aquicultura":         gerar_pesca,
    "🐾 Pet & Veterinária":           gerar_pet,
    "🛢️ Petróleo & Gás":             gerar_petroleo,
    "🏢 Recursos Humanos":            gerar_rh,
    "☁️ SaaS B2B":                   gerar_saas_b2b,
    "💧 Saneamento & Água":           gerar_saneamento,
    "🏥 Saúde":                       gerar_saude,
    "🧠 Saúde Mental":                gerar_saude_mental,
    "🛡️ Seguros":                    gerar_seguros,
    "🦄 Startups & Venture Capital":  gerar_startup,
    "🎬 Streaming":                   gerar_streaming,
    "💻 Tecnologia":                  gerar_tecnologia,
    "📡 Telecom":                     gerar_telecom,
    "🧵 Têxtil & Confecção":          gerar_textil,
    "🚛 Transporte":                  gerar_transporte,
    "✈️ Turismo":                     gerar_turismo,
    "🛒 Varejo":                      gerar_varejo,
    "✈️ Viagens Corporativas":        gerar_viagem_corp,
}

# ═══════════════════════════════════════════════════════════════
# Informações para os flip-cards da tela inicial (55 setores) — ordem alfabética
# ═══════════════════════════════════════════════════════════════
SETORES_INFO = [
    ("🌱", "AgTech",                      "Sensores IoT, drones, monitoramento e agricultura de precisão"),
    ("🌾", "Agronegócio",                 "Safras, culturas, propriedades e insumos"),
    ("🍔", "Alimentos & Bebidas",         "Produção, plantas, produtos e fornecedores"),
    ("🏛️", "Arquitetura & Design",       "Projetos, serviços, honorários e gestão de obras"),
    ("🎬", "Audiovisual & Produtora",     "Produções, orçamentos, recursos e bilheteria"),
    ("✈️", "Aviação Civil",               "Voos, passageiros, aeronaves e aeroportos"),
    ("💄", "Beleza & Estética",           "Vendas, serviços, agenda e salões parceiros"),
    ("🧬", "Biotecnologia",               "Genômica, CRISPR, pesquisa e experimentos laboratoriais"),
    ("🏢", "Condomínio & Facilities",     "Cotas, despesas, ocorrências e manutenção"),
    ("🏗️", "Construção Civil",           "Obras, custos, materiais e fornecedores"),
    ("🤝", "CRM",                         "Oportunidades, contas, contatos e atividades comerciais"),
    ("♻️", "Economia Circular",           "Reciclagem, logística reversa, créditos de carbono e ESG"),
    ("🏪", "E-commerce",                  "Pedidos, clientes, produtos, fretes e pagamentos"),
    ("📚", "Educação",                    "Matrículas, alunos, cursos e instrutores"),
    ("⚡", "Energia",                     "Consumo, medidores, subestações e tarifas"),
    ("🚀", "Espacial & Aeroespacial",     "Missões, satélites, lançamentos e operações"),
    ("🏟️", "Esportes",                   "Partidas, atletas, clubes e competições"),
    ("🎉", "Eventos & Entretenimento",    "Ingressos, fornecedores, receitas e NPS"),
    ("💊", "Farmacêutico",                "Produtos, representantes, vendas e estoque"),
    ("💰", "Financeiro",                  "Transações bancárias, contas e agências"),
    ("🏦", "Fintech",                     "Transações, cartões, usuários, comerciantes e antifraude"),
    ("🌲", "Florestal & Papel",           "Talhões, espécies, colheita e carbono"),
    ("🏷️", "Franquias",                  "Unidades, royalties, taxas e faturamento"),
    ("🎮", "Games & eSports",             "Partidas, jogadores, jogos e monetização in-game"),
    ("🏛️", "Governo & Setor Público",    "Despesas, receitas, licitações e contratos"),
    ("🏨", "Hotelaria",                   "Reservas, hóspedes, hotéis, quartos e canais"),
    ("🏠", "Imobiliário",                 "Vendas, aluguéis, imóveis e corretores"),
    ("🏭", "Indústria",                   "Produção, máquinas, insumos e operadores"),
    ("⚖️", "Jurídico",                   "Processos, advogados, clientes e tribunais"),
    ("🔬", "Laboratório & Diagnóstico",   "Exames, pacientes, laudos e convênios"),
    ("🚚", "Logística",                   "Entregas, transportadoras, rotas e clientes"),
    ("🚴", "Logística Urbana",            "Entregas last mile, entregadores e SLA"),
    ("📣", "Marketing Digital",           "Campanhas, canais, performance e conversões"),
    ("📲", "Migração Claro Brasil (Portabilidade)", "Migrações IN/OUT, serviços, operadoras e motivos de portabilidade"),
    ("⛏️", "Mineração",                  "Extrações, minas, minerais e equipamentos"),
    ("🚗", "Mobilidade",                  "Viagens, motoristas, passageiros, rotas e veículos"),
    ("👗", "Moda & Vestuário",            "Coleções, vendas, estoque e devoluções"),
    ("🐟", "Pesca & Aquicultura",         "Espécies, produção, qualidade e biomassa"),
    ("🐾", "Pet & Veterinária",           "Atendimentos, pets, tutores e serviços veterinários"),
    ("🛢️", "Petróleo & Gás",             "Produção, poços, plataformas e custos operacionais"),
    ("🏢", "Recursos Humanos",            "Horas trabalhadas, funcionários, projetos e cargos"),
    ("☁️", "SaaS B2B",                   "Assinaturas, MRR, churn, NPS e planos"),
    ("💧", "Saneamento & Água",           "Consumo, faturas, estações de tratamento e ligações"),
    ("🏥", "Saúde",                       "Atendimentos, pacientes, médicos e procedimentos"),
    ("🧠", "Saúde Mental",                "Sessões, profissionais, pacientes e diagnósticos"),
    ("🛡️", "Seguros",                    "Apólices, segurados, corretores e sinistros"),
    ("🦄", "Startups & Venture Capital",  "Rodadas, valuations, MRR e métricas de crescimento"),
    ("🎬", "Streaming",                   "Plays, assinantes, conteúdos, artistas"),
    ("💻", "Tecnologia",                  "Contratos SaaS, clientes e planos"),
    ("📡", "Telecom",                     "Chamadas, assinantes, planos e torres"),
    ("🧵", "Têxtil & Confecção",          "Fibras, produção, eficiência e clientes"),
    ("🚛", "Transporte",                  "Viagens, frota, combustível, manutenção e rentabilidade"),
    ("✈️", "Turismo",                     "Viagens, pacotes, agências e destinos"),
    ("🛒", "Varejo",                      "Vendas, clientes, produtos e filiais"),
    ("✈️", "Viagens Corporativas",        "Viajantes, custos, política de viagem e SLA"),
]

# Configurações de datas (opcional)
DATE_DEFAULT_START = "2023-01-01"
DATE_DEFAULT_END   = "2023-12-31"
