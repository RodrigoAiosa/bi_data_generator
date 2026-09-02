"""generators/estadio.py — Setor Estádio & Arena."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

TIPOS_EVENTO = ["Jogo de Futebol", "Show", "Feira", "Evento Corporativo"]
SETORES_ARENA = ["Arquibancada", "Cadeira", "Camarote", "Pista"]


def gerar_estadio(n, start, end):
    n = max(int(n), 1)

    n_arena = min(max(n // 300, 3), 40)
    dim_arena = pd.DataFrame({
        "id_arena":          new_ids(n_arena),
        "cidade":            fake_pool(fake, "city", n_arena),
        "uf":                fake_pool(fake, "state_abbr", n_arena),
        "capacidade":        rng.integers(5000, 80000, n_arena),
    })

    n_evento = min(max(n // 15, 20), 3000)
    dim_evento = pd.DataFrame({
        "id_evento":         new_ids(n_evento),
        "id_arena":          random.choices(dim_arena["id_arena"].tolist(), k=n_evento),
        "tipo_evento":       random.choices(TIPOS_EVENTO, weights=[40, 35, 15, 10], k=n_evento),
    })

    fato_ingresso = pd.DataFrame({
        "id_ingresso":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_evento":         random.choices(dim_evento["id_evento"].tolist(), k=n),
        "setor":             random.choices(SETORES_ARENA, weights=[45, 30, 15, 10], k=n),
        "valor":             rng.uniform(30, 1500, n).round(2),
    })

    return {
        "DimArena": dim_arena,
        "DimEvento": dim_evento,
        "FatoIngresso": fato_ingresso,
        "dCalendario": dcalendario(start, end),
    }
