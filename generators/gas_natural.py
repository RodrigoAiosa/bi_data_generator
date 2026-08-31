"""generators/gas_natural.py — Setor Gás Natural & Distribuição."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_CLIENTE = ["Residencial", "Comercial", "Industrial"]


def gerar_gas_natural(n, start, end):
    n = max(int(n), 1)

    n_distribuidora = min(max(n // 400, 3), 30)
    dim_distribuidora = pd.DataFrame({
        "id_distribuidora":  new_ids(n_distribuidora),
        "cidade":            [fake.city() for _ in range(n_distribuidora)],
        "uf":                [fake.state_abbr() for _ in range(n_distribuidora)],
    })

    n_ligacao = min(max(n // 3, 300), 25000)
    dim_ligacao = pd.DataFrame({
        "id_ligacao":        new_ids(n_ligacao),
        "id_distribuidora":  random.choices(dim_distribuidora["id_distribuidora"].tolist(), k=n_ligacao),
        "tipo_cliente":      random.choices(TIPOS_CLIENTE, weights=[75, 20, 5], k=n_ligacao),
        "endereco":          [fake.street_address() for _ in range(n_ligacao)],
    })

    fato_consumo = pd.DataFrame({
        "id_consumo":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_ligacao":        random.choices(dim_ligacao["id_ligacao"].tolist(), k=n),
        "m3_consumidos":     rng.uniform(5, 8000, n).round(1),
        "valor_fatura":      rng.uniform(30, 25000, n).round(2),
    })

    return {
        "DimDistribuidora": dim_distribuidora,
        "DimLigacao": dim_ligacao,
        "FatoConsumo": fato_consumo,
        "dCalendario": dcalendario(start, end),
    }
