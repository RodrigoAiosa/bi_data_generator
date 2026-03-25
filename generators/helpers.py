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


# ── dCalendario ──────────────────────────────────────────────────────────────
def dcalendario(start: date, end: date) -> pd.DataFrame:
    """Gera dCalendario compatível com o padrão Power Query."""
    meses_pt = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
        5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
    }
    days = pd.date_range(start=start, end=end, freq="D")
    df = pd.DataFrame({"Data": days})
    df["Ano"]    = df["Data"].dt.year
    df["Mes"]    = df["Data"].dt.month
    df["MesAno"] = df["Mes"].map(meses_pt) + "/" + df["Ano"].astype(str).str[-2:]
    df["IdMesAno"] = df["Ano"] * 100 + df["Mes"]
    df["Data"]   = df["Data"].dt.date
    return df


# ── Datas aleatórias ─────────────────────────────────────────────────────────
def rand_dates(start: date, end: date, n: int) -> list[date]:
    delta = (end - start).days
    return [start + timedelta(days=int(d)) for d in rng.integers(0, delta + 1, n)]


# ── Exportação ZIP ───────────────────────────────────────────────────────────
def to_zip(tables: dict[str, "pd.DataFrame"]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, df in tables.items():
            csv_buf = io.StringIO()
            df.to_csv(csv_buf, index=False)
            zf.writestr(f"{name}.csv", csv_buf.getvalue())
    return buf.getvalue()
