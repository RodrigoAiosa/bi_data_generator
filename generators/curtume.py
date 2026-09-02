"""generators/curtume.py — Setor Curtume & Couro."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

TIPOS_COURO = ["Bovino", "Caprino", "Suíno", "Ovino"]
ETAPAS = ["Wet Blue", "Crust", "Acabado"]


def gerar_curtume(n, start, end):
    n = max(int(n), 1)

    n_curtume = min(max(n // 300, 3), 40)
    dim_curtume = pd.DataFrame({
        "id_curtume":        new_ids(n_curtume),
        "cidade":            fake_pool(fake, "city", n_curtume),
        "uf":                fake_pool(fake, "state_abbr", n_curtume),
    })

    n_lote = min(max(n // 15, 30), 4000)
    dim_lote = pd.DataFrame({
        "id_lote":           new_ids(n_lote),
        "id_curtume":        random.choices(dim_curtume["id_curtume"].tolist(), k=n_lote),
        "tipo_couro":        random.choices(TIPOS_COURO, weights=[70, 15, 10, 5], k=n_lote),
        "etapa":             random.choices(ETAPAS, k=n_lote),
    })

    fato_processamento = pd.DataFrame({
        "id_processamento":  new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_lote":           random.choices(dim_lote["id_lote"].tolist(), k=n),
        "m2_processados":    rng.integers(20, 3000, n),
        "custo_m2":          rng.uniform(5, 40, n).round(2),
    })

    n_venda = int(n * 0.8)
    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n_venda),
        "id_data":           rand_dates(start, end, n_venda),
        "id_lote":           random.choices(dim_lote["id_lote"].tolist(), k=n_venda),
        "cliente":           fake_pool(fake, "company", n_venda),
        "m2_vendidos":       rng.integers(10, 2000, n_venda),
        "preco_m2":          rng.uniform(10, 80, n_venda).round(2),
    })

    return {
        "DimCurtume": dim_curtume,
        "DimLote": dim_lote,
        "FatoProcessamento": fato_processamento,
        "FatoVenda": fato_venda,
        "dCalendario": dcalendario(start, end),
    }
