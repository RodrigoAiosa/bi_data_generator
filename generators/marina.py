"""generators/marina.py — Setor Marina & Náutica."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_EMBARCACAO = ["Lancha", "Veleiro", "Jet Ski", "Iate"]
SERVICOS = ["Abastecimento", "Manutenção", "Nenhum"]


def gerar_marina(n, start, end):
    n = max(int(n), 1)

    n_marina = min(max(n // 200, 3), 40)
    dim_marina = pd.DataFrame({
        "id_marina":         new_ids(n_marina),
        "cidade":            [fake.city() for _ in range(n_marina)],
        "uf":                [fake.state_abbr() for _ in range(n_marina)],
        "num_vagas":         rng.integers(20, 500, n_marina),
    })

    n_embarcacao = min(max(n // 10, 50), 6000)
    dim_embarcacao = pd.DataFrame({
        "id_embarcacao":     new_ids(n_embarcacao),
        "id_marina":         random.choices(dim_marina["id_marina"].tolist(), k=n_embarcacao),
        "tipo":              random.choices(TIPOS_EMBARCACAO, weights=[40, 20, 25, 15], k=n_embarcacao),
        "comprimento_pes":   rng.integers(12, 90, n_embarcacao),
    })

    fato_atracacao = pd.DataFrame({
        "id_atracacao":      new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_embarcacao":     random.choices(dim_embarcacao["id_embarcacao"].tolist(), k=n),
        "dias_atracado":     rng.integers(1, 60, n),
        "valor_diaria":      rng.uniform(50, 1200, n).round(2),
        "servico_adicional": random.choices(SERVICOS, weights=[35, 25, 40], k=n),
    })

    return {
        "DimMarina": dim_marina,
        "DimEmbarcacao": dim_embarcacao,
        "FatoAtracacao": fato_atracacao,
        "dCalendario": dcalendario(start, end),
    }
