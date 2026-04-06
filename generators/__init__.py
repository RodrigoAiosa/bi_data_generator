from .varejo import gerar_varejo
from .financeiro import gerar_financeiro
from .saude import gerar_saude
from .tecnologia import gerar_tecnologia
from .educacao import gerar_educacao
from .logistica import gerar_logistica
from .energia import gerar_energia
from .telecom import gerar_telecom
from .industria import gerar_industria
from .agronegocio import gerar_agronegocio
from .hotelaria import gerar_hotelaria
from .streaming import gerar_streaming
from .ecommerce import gerar_ecommerce           # NOVO
from .rh import gerar_rh                         # NOVO
from .mobilidade import gerar_mobilidade         # NOVO
from .fintech import gerar_fintech               # NOVO
from .turismo import gerar_turismo               # ADICIONADO
from .imobiliario import gerar_imobiliario       # ADICIONADO
from .seguros import gerar_seguros               # ADICIONADO
from .construcao import gerar_construcao         # ADICIONADO

__all__ = [
    "gerar_varejo",
    "gerar_financeiro", 
    "gerar_saude",
    "gerar_tecnologia",
    "gerar_educacao",
    "gerar_logistica",
    "gerar_energia",
    "gerar_telecom",
    "gerar_industria",
    "gerar_agronegocio",
    "gerar_hotelaria",
    "gerar_streaming",
    "gerar_ecommerce",      # NOVO
    "gerar_rh",             # NOVO
    "gerar_mobilidade",     # NOVO
    "gerar_fintech",        # NOVO
    "gerar_turismo",        # ADICIONADO
    "gerar_imobiliario",    # ADICIONADO
    "gerar_seguros",        # ADICIONADO
    "gerar_construcao"      # ADICIONADO
]
