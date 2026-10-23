"""
contexto.py: configurações por requisição (idioma e mês de início do ano
fiscal) sem depender de nenhum framework de UI.

Usado pelos geradores (via i18n.get_lang / config.get_mes_fiscal) quando
rodam como função serverless na Vercel. Thread-local: cada requisição tem o
seu próprio valor, sem vazar para a seguinte.
"""
import threading

_local = threading.local()


def definir(lang: str | None = None, mes_fiscal: int | None = None) -> None:
    _local.lang = lang
    _local.mes_fiscal = mes_fiscal


def limpar() -> None:
    definir(None, None)


def lang() -> str | None:
    return getattr(_local, "lang", None)


def mes_fiscal() -> int | None:
    return getattr(_local, "mes_fiscal", None)
