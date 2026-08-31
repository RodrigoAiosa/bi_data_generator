"""generators/agua_mineral.py — Setor Água Mineral & Envasamento."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_LINHA = ["Com Gás", "Sem Gás", "Saborizada"]
EMBALAGENS = ["Garrafa 500ml", "Garrafa 1,5L", "Galão 20L", "Copo 200ml"]


def gerar_agua_mineral(n, start, end):
    n = max(int(n), 1)

    n_fonte = min(max(n // 300, 3), 40)
    dim_fonte = pd.DataFrame({
        "id_fonte":          new_ids(n_fonte),
        "cidade":            [fake.city() for _ in range(n_fonte)],
        "uf":                [fake.state_abbr() for _ in range(n_fonte)],
    })

    n_linha = min(max(n // 25, 15), 1500)
    dim_linha = pd.DataFrame({
        "id_linha":          new_ids(n_linha),
        "id_fonte":          random.choices(dim_fonte["id_fonte"].tolist(), k=n_linha),
        "tipo":              random.choices(TIPOS_LINHA, weights=[25, 60, 15], k=n_linha),
        "embalagem":         random.choices(EMBALAGENS, k=n_linha),
    })

    fato_producao = pd.DataFrame({
        "id_producao":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_linha":          random.choices(dim_linha["id_linha"].tolist(), k=n),
        "unidades_produzidas": rng.integers(500, 100000, n),
        "custo_unitario":    rng.uniform(0.3, 8, n).round(2),
    })

    n_dist = int(n * 1.2)
    fato_distribuicao = pd.DataFrame({
        "id_distribuicao":   new_ids(n_dist),
        "id_data":           rand_dates(start, end, n_dist),
        "id_linha":          random.choices(dim_linha["id_linha"].tolist(), k=n_dist),
        "cliente":           [fake.company() for _ in range(n_dist)],
        "unidades_distribuidas": rng.integers(50, 50000, n_dist),
        "valor_total":       rng.uniform(80, 40000, n_dist).round(2),
    })

    return {
        "DimFonte": dim_fonte,
        "DimLinha": dim_linha,
        "FatoProducao": fato_producao,
        "FatoDistribuicao": fato_distribuicao,
        "dCalendario": dcalendario(start, end),
    }
