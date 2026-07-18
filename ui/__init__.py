"""ui/__init__.py — Re-exporta os componentes de interface."""

from .dashboard import render_dashboard
from .estado_inicial import render_estado_inicial
from .hero import render_hero
from .resultado import render_resultado
from .sidebar import render_sidebar

__all__ = [
    "render_hero",
    "render_sidebar",
    "render_estado_inicial",
    "render_resultado",
    "render_dashboard",
]
