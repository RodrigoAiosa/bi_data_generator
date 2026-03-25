"""generators/__init__.py — Re-exporta todos os geradores."""

from .agronegocio import gerar_agronegocio
from .educacao import gerar_educacao
from .energia import gerar_energia
from .financeiro import gerar_financeiro
from .helpers import dcalendario, new_ids, rand_dates, rng, to_zip
from .industria import gerar_industria
from .logistica import gerar_logistica
from .saude import gerar_saude
from .tecnologia import gerar_tecnologia
from .telecom import gerar_telecom
from .varejo import gerar_varejo

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
    # helpers
    "new_ids",
    "dcalendario",
    "rand_dates",
    "rng",
    "to_zip",
]
