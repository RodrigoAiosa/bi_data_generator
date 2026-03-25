"""
config.py
Mapa de setores e constantes globais da aplicação.
Para adicionar um novo setor: importe o gerador e adicione uma entrada em SETORES.
"""

from generators import (
    gerar_agronegocio,
    gerar_educacao,
    gerar_energia,
    gerar_financeiro,
    gerar_industria,
    gerar_logistica,
    gerar_saude,
    gerar_tecnologia,
    gerar_telecom,
    gerar_varejo,
)

# ── Mapa principal: label (exibido na UI) → função geradora ─────────────────
SETORES: dict = {
    "🛒 Varejo":      gerar_varejo,
    "💰 Financeiro":  gerar_financeiro,
    "🏥 Saúde":       gerar_saude,
    "💻 Tecnologia":  gerar_tecnologia,
    "📚 Educação":    gerar_educacao,
    "🚚 Logística":   gerar_logistica,
    "⚡ Energia":      gerar_energia,
    "📡 Telecom":     gerar_telecom,
    "🏭 Indústria":   gerar_industria,
    "🌾 Agronegócio": gerar_agronegocio,
}

# ── Metadados dos setores (usados nos flip-cards da tela inicial) ────────────
SETORES_INFO: list[tuple[str, str, str]] = [
    ("🛒", "Varejo",      "Vendas, clientes, produtos, vendedores, filiais e geografia"),
    ("💰", "Financeiro",  "Transações, contas, agências e produtos bancários"),
    ("🏥", "Saúde",       "Atendimentos, pacientes, médicos, procedimentos e unidades"),
    ("💻", "Tecnologia",  "Contratos SaaS, MRR, ARR, NPS, clientes e agentes"),
    ("📚", "Educação",    "Matrículas, alunos, cursos, instrutores e notas"),
    ("🚚", "Logística",   "Entregas, rotas, transportadoras, peso, frete e SLA"),
    ("⚡",  "Energia",     "Leituras de consumo kWh, medidores, subestações e faturas"),
    ("📡", "Telecom",     "Chamadas, assinantes, planos, torres e qualidade de sinal"),
    ("🏭", "Indústria",   "Ordens de produção, máquinas, OEE, refugo e operadores"),
    ("🌾", "Agronegócio", "Safras, culturas, propriedades, produtividade e clima"),
]

# ── Configurações da página Streamlit ────────────────────────────────────────
PAGE_CONFIG = dict(
    page_title="BI Data Generator PRO",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Limites do slider ─────────────────────────────────────────────────────────
SLIDER_MIN  = 1_000
SLIDER_MAX  = 10_000
SLIDER_STEP = 500
SLIDER_DEFAULT = 5_000
