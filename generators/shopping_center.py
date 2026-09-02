"""generators/shopping_center.py — Setor Shopping Center & Administração de Malls."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

SEGMENTOS = ["Vestuário", "Alimentação", "Eletrônicos", "Serviços", "Lazer", "Beleza"]


def gerar_shopping_center(n, start, end):
    n = max(int(n), 1)

    n_shopping = min(max(n // 300, 3), 40)
    dim_shopping = pd.DataFrame({
        "id_shopping":       new_ids(n_shopping),
        "cidade":            fake_pool(fake, "city", n_shopping),
        "uf":                fake_pool(fake, "state_abbr", n_shopping),
        "num_lojas":         rng.integers(40, 400, n_shopping),
    })

    n_lojista = min(max(n // 15, 30), 4000)
    dim_lojista = pd.DataFrame({
        "id_lojista":        new_ids(n_lojista),
        "id_shopping":       random.choices(dim_shopping["id_shopping"].tolist(), k=n_lojista),
        "nome_loja":         fake_pool(fake, "company", n_lojista),
        "segmento":          random.choices(SEGMENTOS, k=n_lojista),
    })

    n_aluguel = n_lojista * 3
    fato_aluguel = pd.DataFrame({
        "id_aluguel":        new_ids(n_aluguel),
        "id_data":           rand_dates(start, end, n_aluguel),
        "id_lojista":        random.choices(dim_lojista["id_lojista"].tolist(), k=n_aluguel),
        "valor_aluguel":     rng.uniform(2000, 90000, n_aluguel).round(2),
        "percentual_sobre_vendas": rng.uniform(3, 15, n_aluguel).round(1),
    })

    fato_fluxo = pd.DataFrame({
        "id_fluxo":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_shopping":       random.choices(dim_shopping["id_shopping"].tolist(), k=n),
        "visitantes":        rng.integers(500, 60000, n),
        "ticket_medio":      rng.uniform(30, 400, n).round(2),
    })

    return {
        "DimShopping": dim_shopping,
        "DimLojista": dim_lojista,
        "FatoAluguel": fato_aluguel,
        "FatoFluxoVisitantes": fato_fluxo,
        "dCalendario": dcalendario(start, end),
    }
