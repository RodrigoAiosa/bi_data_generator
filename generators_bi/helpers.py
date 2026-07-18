"""
generators_bi/helpers.py
Funções utilitárias compartilhadas por todos os geradores de dados por setor.
"""

import io
import zipfile
from datetime import date, timedelta

import numpy as np
import pandas as pd

rng = np.random.default_rng()

MESES = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
          7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}


def new_ids(n: int) -> list:
    """IDs sequenciais 1..n — usados como chave primária das dimensões."""
    return list(range(1, n + 1))


def rand_dates(start: date, end: date, n: int) -> list:
    """n datas aleatórias uniformemente distribuídas entre start e end."""
    delta = (end - start).days
    delta = max(delta, 1)
    return [start + timedelta(days=int(d)) for d in rng.integers(0, delta + 1, n)]


def dcalendario(start: date, end: date) -> pd.DataFrame:
    """Tabela calendário (dimensão de datas), compatível com Time Intelligence."""
    days = pd.date_range(start=start, end=end, freq="D")
    df = pd.DataFrame({"Data": days})
    df["Ano"] = df["Data"].dt.year
    df["Mes"] = df["Data"].dt.month
    df["Trimestre"] = df["Data"].dt.quarter
    df["MesAno"] = df["Mes"].map(MESES) + "/" + df["Ano"].astype(str).str[-2:]
    df["IdMesAno"] = df["Ano"] * 100 + df["Mes"]
    df["DiaSemana"] = df["Data"].dt.day_name()
    df["Data"] = df["Data"].dt.date
    return df


def to_zip(tabelas: dict) -> bytes:
    """Empacota um dicionário {nome_tabela: DataFrame} em um ZIP de CSVs."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for nome, df in tabelas.items():
            csv_buf = io.StringIO()
            df.to_csv(csv_buf, index=False)
            zf.writestr(f"{nome}.csv", csv_buf.getvalue())
    return buf.getvalue()
