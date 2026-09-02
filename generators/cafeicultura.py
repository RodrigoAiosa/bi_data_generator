"""generators/cafeicultura.py — Setor Cafeicultura & Torrefação."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

VARIEDADES = ["Arábica", "Robusta", "Bourbon", "Catuaí", "Mundo Novo"]
QUALIDADES = ["Tradicional", "Superior", "Gourmet", "Especial"]
PONTOS_TORRA = ["Clara", "Média", "Escura"]


def gerar_cafeicultura(n, start, end):
    n = max(int(n), 1)

    n_fazenda = min(max(n // 100, 5), 80)
    dim_fazenda = pd.DataFrame({
        "id_fazenda":        new_ids(n_fazenda),
        "cidade":            fake_pool(fake, "city", n_fazenda),
        "uf":                fake_pool(fake, "state_abbr", n_fazenda),
        "area_ha":           rng.uniform(5, 500, n_fazenda).round(1),
    })

    n_lote = min(max(n // 8, 30), 3000)
    dim_lote = pd.DataFrame({
        "id_lote":           new_ids(n_lote),
        "id_fazenda":        random.choices(dim_fazenda["id_fazenda"].tolist(), k=n_lote),
        "variedade":         random.choices(VARIEDADES, k=n_lote),
    })

    fato_colheita = pd.DataFrame({
        "id_colheita":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_lote":           random.choices(dim_lote["id_lote"].tolist(), k=n),
        "sacas_60kg":        rng.integers(5, 800, n),
        "qualidade":         random.choices(QUALIDADES, weights=[30, 35, 20, 15], k=n),
    })

    n_torra = int(n * 0.7)
    fato_torrefacao = pd.DataFrame({
        "id_torra":          new_ids(n_torra),
        "id_data":           rand_dates(start, end, n_torra),
        "id_lote":           random.choices(dim_lote["id_lote"].tolist(), k=n_torra),
        "ponto_torra":       random.choices(PONTOS_TORRA, k=n_torra),
        "kg_torrado":        rng.uniform(20, 3000, n_torra).round(1),
        "preco_kg":          rng.uniform(18, 90, n_torra).round(2),
    })

    return {
        "DimFazenda": dim_fazenda,
        "DimLote": dim_lote,
        "FatoColheita": fato_colheita,
        "FatoTorrefacao": fato_torrefacao,
        "dCalendario": dcalendario(start, end),
    }
