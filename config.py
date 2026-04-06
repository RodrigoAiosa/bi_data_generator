from generators import (
    gerar_varejo, gerar_financeiro, gerar_saude, gerar_tecnologia,
    gerar_educacao, gerar_logistica, gerar_energia, gerar_telecom,
    gerar_industria, gerar_agronegocio, gerar_hotelaria, gerar_streaming   # NOVOS
)

SETORES = {
    "🛒 Varejo": gerar_varejo,
    "💰 Financeiro": gerar_financeiro,
    "🏥 Saúde": gerar_saude,
    "💻 Tecnologia": gerar_tecnologia,
    "📚 Educação": gerar_educacao,
    "🚚 Logística": gerar_logistica,
    "⚡ Energia": gerar_energia,
    "📡 Telecom": gerar_telecom,
    "🏭 Indústria": gerar_industria,
    "🌾 Agronegócio": gerar_agronegocio,
    "🏨 Hotelaria": gerar_hotelaria,             # NOVO
    "🎬 Streaming": gerar_streaming              # NOVO
}

SETORES_INFO = [
    ("🛒", "Varejo", "Vendas, clientes, produtos e filiais"),
    ("💰", "Financeiro", "Transações bancárias, contas e agências"),
    ("🏥", "Saúde", "Atendimentos, pacientes, médicos e procedimentos"),
    ("💻", "Tecnologia", "Contratos SaaS, clientes e planos"),
    ("📚", "Educação", "Matrículas, alunos, cursos e instrutores"),
    ("🚚", "Logística", "Entregas, transportadoras, rotas e clientes"),
    ("⚡", "Energia", "Consumo, medidores, subestações e tarifas"),
    ("📡", "Telecom", "Chamadas, assinantes, planos e torres"),
    ("🏭", "Indústria", "Produção, máquinas, insumos e operadores"),
    ("🌾", "Agronegócio", "Safras, culturas, propriedades e insumos"),
    ("🏨", "Hotelaria", "Reservas, hóspedes, hotéis, quartos e canais"),      # NOVO
    ("🎬", "Streaming", "Plays, assinantes, conteúdos, artistas")             # NOVO
]
