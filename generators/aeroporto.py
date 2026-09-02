"""generators/aeroporto.py — Setor Aeroporto & Operações Aeroportuárias."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

TIPOS_OPERACAO = ["Pouso", "Decolagem"]


def gerar_aeroporto(n, start, end):
    n = max(int(n), 1)

    n_aeroporto = min(max(n // 200, 5), 40)
    dim_aeroporto = pd.DataFrame({
        "id_aeroporto":      new_ids(n_aeroporto),
        "nome_aeroporto":    [f"Aeroporto de {fake.city()}" for _ in range(n_aeroporto)],
        "cidade":            fake_pool(fake, "city", n_aeroporto),
        "uf":                fake_pool(fake, "state_abbr", n_aeroporto),
        "num_terminais":     rng.integers(1, 6, n_aeroporto),
    })

    n_companhia = min(max(n // 300, 6), 30)
    dim_companhia = pd.DataFrame({
        "id_companhia":      new_ids(n_companhia),
        "nome_companhia":    fake_pool(fake, "company", n_companhia),
        "pais_origem":       random.choices(["Brasil", "EUA", "Chile", "Argentina", "Portugal", "Panamá"], k=n_companhia),
    })

    fato_voo = pd.DataFrame({
        "id_voo":            new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_aeroporto":      random.choices(dim_aeroporto["id_aeroporto"].tolist(), k=n),
        "id_companhia":      random.choices(dim_companhia["id_companhia"].tolist(), k=n),
        "tipo_operacao":     random.choices(TIPOS_OPERACAO, k=n),
        "passageiros":       rng.integers(20, 400, n),
        "atraso_min":        rng.integers(0, 180, n),
        "taxa_aeroportuaria": rng.uniform(50, 5000, n).round(2),
    })

    return {
        "DimAeroporto": dim_aeroporto,
        "DimCompanhiaAerea": dim_companhia,
        "FatoVoo": fato_voo,
        "dCalendario": dcalendario(start, end),
    }
