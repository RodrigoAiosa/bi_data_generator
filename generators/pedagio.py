"""generators/pedagio.py — Setor Pedágio & Concessão Rodoviária."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS_VEICULO = ["Passeio", "Caminhão", "Moto", "Ônibus"]
FORMAS_PAGAMENTO = ["Dinheiro", "Tag Eletrônica", "Cartão"]


def gerar_pedagio(n, start, end):
    n = max(int(n), 1)

    n_concessionaria = min(max(n // 500, 3), 25)
    dim_concessionaria = pd.DataFrame({
        "id_concessionaria": new_ids(n_concessionaria),
        "nome_concessionaria": [fake.company() for _ in range(n_concessionaria)],
        "rodovia":           [f"BR-{rng.integers(10, 500)}" for _ in range(n_concessionaria)],
    })

    n_praca = min(max(n // 100, 5), 200)
    dim_praca = pd.DataFrame({
        "id_praca":          new_ids(n_praca),
        "id_concessionaria": random.choices(dim_concessionaria["id_concessionaria"].tolist(), k=n_praca),
        "km":                rng.integers(1, 800, n_praca),
        "uf":                [fake.state_abbr() for _ in range(n_praca)],
    })

    fato_passagem = pd.DataFrame({
        "id_passagem":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_praca":          random.choices(dim_praca["id_praca"].tolist(), k=n),
        "categoria_veiculo": random.choices(CATEGORIAS_VEICULO, weights=[65, 15, 15, 5], k=n),
        "valor_tarifa":      rng.uniform(4, 60, n).round(2),
        "forma_pagamento":   random.choices(FORMAS_PAGAMENTO, weights=[15, 65, 20], k=n),
    })

    return {
        "DimConcessionaria": dim_concessionaria,
        "DimPraca": dim_praca,
        "FatoPassagem": fato_passagem,
        "dCalendario": dcalendario(start, end),
    }
