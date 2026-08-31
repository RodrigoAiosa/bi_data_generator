"""generators/resseguradora.py — Setor Resseguradora."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

RAMOS = ["Automóvel", "Vida", "Patrimonial", "Rural", "Responsabilidade Civil"]


def gerar_resseguradora(n, start, end):
    n = max(int(n), 1)

    n_seguradora = min(max(n // 200, 5), 100)
    dim_seguradora = pd.DataFrame({
        "id_seguradora":     new_ids(n_seguradora),
        "nome_seguradora":   [fake.company() for _ in range(n_seguradora)],
    })

    n_tratado = min(max(n // 30, 15), 1500)
    dim_tratado = pd.DataFrame({
        "id_tratado":        new_ids(n_tratado),
        "id_seguradora":     random.choices(dim_seguradora["id_seguradora"].tolist(), k=n_tratado),
        "ramo":              random.choices(RAMOS, k=n_tratado),
        "percentual_cessao": rng.uniform(10, 90, n_tratado).round(1),
    })

    fato_sinistro = pd.DataFrame({
        "id_sinistro":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_tratado":        random.choices(dim_tratado["id_tratado"].tolist(), k=n),
        "valor_sinistro_original": rng.uniform(2000, 5000000, n).round(2),
        "valor_ressegurado": rng.uniform(500, 4000000, n).round(2),
        "status":            random.choices(["Em Análise", "Pago", "Negado"], weights=[30, 60, 10], k=n),
    })

    return {
        "DimSeguradoraCedente": dim_seguradora,
        "DimTratado": dim_tratado,
        "FatoSinistro": fato_sinistro,
        "dCalendario": dcalendario(start, end),
    }
