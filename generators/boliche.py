"""generators/boliche.py — Setor Boliche & Diversão Familiar."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")


def gerar_boliche(n, start, end):
    n = max(int(n), 1)

    n_unidade = min(max(n // 300, 3), 40)
    dim_unidade = pd.DataFrame({
        "id_unidade":        new_ids(n_unidade),
        "cidade":            fake_pool(fake, "city", n_unidade),
        "uf":                fake_pool(fake, "state_abbr", n_unidade),
        "num_pistas":        rng.integers(4, 24, n_unidade),
    })

    n_pista = min(max(n // 15, 20), 800)
    dim_pista = pd.DataFrame({
        "id_pista":          new_ids(n_pista),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n_pista),
        "numero_pista":      rng.integers(1, 25, n_pista),
    })

    fato_partida = pd.DataFrame({
        "id_partida":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_pista":          random.choices(dim_pista["id_pista"].tolist(), k=n),
        "cliente":           fake_pool(fake, "name", n),
        "num_jogadores":     rng.integers(1, 8, n),
        "pontuacao_media":   rng.integers(50, 250, n),
        "valor":             rng.uniform(30, 300, n).round(2),
    })

    return {
        "DimUnidade": dim_unidade,
        "DimPista": dim_pista,
        "FatoPartida": fato_partida,
        "dCalendario": dcalendario(start, end),
    }
