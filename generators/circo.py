"""generators/circo.py — Setor Circo & Espetáculos Itinerantes."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")


def gerar_circo(n, start, end):
    n = max(int(n), 1)

    n_trupe = min(max(n // 500, 3), 30)
    dim_trupe = pd.DataFrame({
        "id_trupe":          new_ids(n_trupe),
        "nome_trupe":        [f"Circo {fake.last_name()}" for _ in range(n_trupe)],
        "num_artistas":      rng.integers(8, 60, n_trupe),
    })

    n_cidade_turne = min(max(n // 20, 20), 3000)
    dim_cidade_turne = pd.DataFrame({
        "id_cidade_turne":   new_ids(n_cidade_turne),
        "id_trupe":          random.choices(dim_trupe["id_trupe"].tolist(), k=n_cidade_turne),
        "cidade":            fake_pool(fake, "city", n_cidade_turne),
        "uf":                fake_pool(fake, "state_abbr", n_cidade_turne),
    })

    fato_sessao = pd.DataFrame({
        "id_sessao":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_cidade_turne":   random.choices(dim_cidade_turne["id_cidade_turne"].tolist(), k=n),
        "publico":           rng.integers(30, 2000, n),
        "taxa_ocupacao_pct": rng.uniform(20, 100, n).round(1),
        "receita_ingressos": rng.uniform(500, 60000, n).round(2),
    })

    return {
        "DimTrupe": dim_trupe,
        "DimCidadeTurne": dim_cidade_turne,
        "FatoSessao": fato_sessao,
        "dCalendario": dcalendario(start, end),
    }
