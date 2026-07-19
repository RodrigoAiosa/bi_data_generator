"""styles/__init__.py"""

from .css import inject_css

try:
    from .seo import inject_seo
except Exception:
    def inject_seo(lang: str = "pt") -> None:
        pass  # seo.py não encontrado — SEO desabilitado

__all__ = ["inject_css", "inject_seo"]
