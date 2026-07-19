"""
generators/helpers.py
Funções utilitárias compartilhadas por todos os geradores de dados.
"""

import io
import zipfile
from datetime import date, timedelta

import numpy as np
import pandas as pd

rng = np.random.default_rng()


# ── IDs sequenciais ──────────────────────────────────────────────────────────
def new_ids(n: int, prefix: str = "") -> list[int]:
    return list(range(1, n + 1))


# ── dCalendario (idioma dinâmico) ────────────────────────────────────────────
def dcalendario(start: date, end: date) -> pd.DataFrame:
    """Gera dCalendario compatível com Power Query, no idioma atual."""
    try:
        from i18n import get_lang, MESES
        lang = get_lang()
        meses = MESES[lang]
    except Exception:
        meses = {1:"Jan",2:"Fev",3:"Mar",4:"Abr",5:"Mai",6:"Jun",
                 7:"Jul",8:"Ago",9:"Set",10:"Out",11:"Nov",12:"Dez"}

    days = pd.date_range(start=start, end=end, freq="D")
    df = pd.DataFrame({"Data": days})
    df["Ano"]     = df["Data"].dt.year
    df["Mes"]     = df["Data"].dt.month
    df["MesAno"]  = df["Mes"].map(meses) + "/" + df["Ano"].astype(str).str[-2:]
    df["IdMesAno"] = df["Ano"] * 100 + df["Mes"]
    df["Data"]    = df["Data"].dt.date
    return df


# ── Faker locale dinâmico ────────────────────────────────────────────────────
def get_faker():
    """Retorna instância do Faker no locale do idioma atual."""
    from faker import Faker
    try:
        from i18n import get_lang, FAKER_LOCALE
        locale = FAKER_LOCALE.get(get_lang(), "pt_BR")
    except Exception:
        locale = "pt_BR"
    return Faker(locale)


# ── Datas aleatórias ─────────────────────────────────────────────────────────
def rand_dates(start: date, end: date, n: int) -> list[date]:
    delta = (end - start).days
    return [start + timedelta(days=int(d)) for d in rng.integers(0, delta + 1, n)]


# ── Exportação ZIP ───────────────────────────────────────────────────────────
def to_zip(tables: dict[str, "pd.DataFrame"], extra_files: dict[str, str] | None = None) -> bytes:
    """
    Empacota as tabelas (CSV) em um .zip.

    extra_files: dict opcional {nome_do_arquivo: conteudo_texto} para incluir
    arquivos adicionais no zip (ex.: {"model.tmdl": conteudo_tmdl}).
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, df in tables.items():
            csv_buf = io.StringIO()
            df.to_csv(csv_buf, index=False)
            zf.writestr(f"{name}.csv", csv_buf.getvalue())
        if extra_files:
            for filename, conteudo in extra_files.items():
                zf.writestr(filename, conteudo)
    return buf.getvalue()
