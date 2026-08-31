"""generators/onibus_intermunicipal.py — Setor Ônibus Intermunicipal & Rodoviária."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")


def gerar_onibus_intermunicipal(n, start, end):
    n = max(int(n), 1)

    n_empresa = min(max(n // 300, 3), 40)
    dim_empresa = pd.DataFrame({
        "id_empresa":        new_ids(n_empresa),
        "nome_empresa":      [fake.company() for _ in range(n_empresa)],
    })

    n_linha = min(max(n // 20, 15), 2000)
    dim_linha = pd.DataFrame({
        "id_linha":          new_ids(n_linha),
        "id_empresa":        random.choices(dim_empresa["id_empresa"].tolist(), k=n_linha),
        "origem":            [fake.city() for _ in range(n_linha)],
        "destino":           [fake.city() for _ in range(n_linha)],
        "distancia_km":      rng.integers(50, 3000, n_linha),
    })

    fato_viagem = pd.DataFrame({
        "id_viagem":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_linha":          random.choices(dim_linha["id_linha"].tolist(), k=n),
        "passageiros":       rng.integers(5, 46, n),
        "ocupacao_pct":      rng.uniform(15, 100, n).round(1),
        "receita":           rng.uniform(300, 15000, n).round(2),
    })

    return {
        "DimEmpresa": dim_empresa,
        "DimLinha": dim_linha,
        "FatoViagem": fato_viagem,
        "dCalendario": dcalendario(start, end),
    }
