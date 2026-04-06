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
from .hotelaria import gerar_hotelaria          # NOVO
from .streaming import gerar_streaming          # NOVO

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
    "gerar_hotelaria",                           # NOVO
    "gerar_streaming"                            # NOVO
]
