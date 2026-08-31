"""generators/bike_sharing.py — Setor Aluguel de Bicicletas & Bike Sharing."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_PLANO = ["Avulso", "Mensal", "Anual"]


def gerar_bike_sharing(n, start, end):
    n = max(int(n), 1)

    n_estacao = min(max(n // 100, 8), 500)
    dim_estacao = pd.DataFrame({
        "id_estacao":        new_ids(n_estacao),
        "cidade":            [fake.city() for _ in range(n_estacao)],
        "uf":                [fake.state_abbr() for _ in range(n_estacao)],
        "capacidade_docas":  rng.integers(8, 40, n_estacao),
    })

    n_bicicleta = min(max(n // 8, 100), 8000)
    dim_bicicleta = pd.DataFrame({
        "id_bicicleta":      new_ids(n_bicicleta),
        "tipo":              random.choices(["Convencional", "Elétrica"], weights=[70, 30], k=n_bicicleta),
        "status":            random.choices(["Disponível", "Em Uso", "Manutenção"], weights=[70, 20, 10], k=n_bicicleta),
    })

    fato_corrida = pd.DataFrame({
        "id_corrida":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_estacao":        random.choices(dim_estacao["id_estacao"].tolist(), k=n),
        "id_bicicleta":      random.choices(dim_bicicleta["id_bicicleta"].tolist(), k=n),
        "duracao_min":       rng.integers(3, 120, n),
        "distancia_km":      rng.uniform(0.3, 25, n).round(1),
        "tipo_plano":        random.choices(TIPOS_PLANO, weights=[50, 35, 15], k=n),
    })

    return {
        "DimEstacao": dim_estacao,
        "DimBicicleta": dim_bicicleta,
        "FatoCorrida": fato_corrida,
        "dCalendario": dcalendario(start, end),
    }
