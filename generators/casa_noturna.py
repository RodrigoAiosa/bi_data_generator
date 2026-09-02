"""generators/casa_noturna.py — Setor Casa Noturna & Casa de Shows."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

GENEROS_MUSICAIS = ["Sertanejo", "Eletrônica", "Pagode", "Rock", "Funk", "MPB"]
TIPOS_INGRESSO = ["Pista", "Camarote", "VIP"]
ITENS_BAR = ["Cerveja", "Drink", "Refrigerante", "Água", "Petisco"]


def gerar_casa_noturna(n, start, end):
    n = max(int(n), 1)

    n_casa = min(max(n // 300, 3), 40)
    dim_casa = pd.DataFrame({
        "id_casa":           new_ids(n_casa),
        "cidade":            fake_pool(fake, "city", n_casa),
        "uf":                fake_pool(fake, "state_abbr", n_casa),
        "capacidade":        rng.integers(200, 5000, n_casa),
    })

    n_evento = min(max(n // 15, 30), 4000)
    dim_evento = pd.DataFrame({
        "id_evento":         new_ids(n_evento),
        "id_casa":           random.choices(dim_casa["id_casa"].tolist(), k=n_evento),
        "nome_evento":       [f"Noite {fake.word().capitalize()}" for _ in range(n_evento)],
        "genero_musical":    random.choices(GENEROS_MUSICAIS, k=n_evento),
    })

    fato_ingresso = pd.DataFrame({
        "id_ingresso":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_evento":         random.choices(dim_evento["id_evento"].tolist(), k=n),
        "tipo_ingresso":     random.choices(TIPOS_INGRESSO, weights=[60, 25, 15], k=n),
        "valor":             rng.uniform(30, 800, n).round(2),
    })

    n_consumo = int(n * 1.8)
    fato_consumo_bar = pd.DataFrame({
        "id_consumo":        new_ids(n_consumo),
        "id_data":           rand_dates(start, end, n_consumo),
        "id_evento":         random.choices(dim_evento["id_evento"].tolist(), k=n_consumo),
        "item":              random.choices(ITENS_BAR, k=n_consumo),
        "valor":             rng.uniform(8, 90, n_consumo).round(2),
    })

    return {
        "DimCasa": dim_casa,
        "DimEvento": dim_evento,
        "FatoIngresso": fato_ingresso,
        "FatoConsumoBar": fato_consumo_bar,
        "dCalendario": dcalendario(start, end),
    }
