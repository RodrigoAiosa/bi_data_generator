"""generators/distribuidora_bebidas.py — Setor Distribuidora de Bebidas."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

CATEGORIAS = ["Cerveja", "Refrigerante", "Água", "Energético", "Destilado", "Suco"]


def gerar_distribuidora_bebidas(n, start, end):
    n = max(int(n), 1)

    n_centro = min(max(n // 300, 3), 40)
    dim_centro = pd.DataFrame({
        "id_centro":         new_ids(n_centro),
        "cidade":            fake_pool(fake, "city", n_centro),
        "uf":                fake_pool(fake, "state_abbr", n_centro),
    })

    n_marca = min(max(n // 40, 15), 500)
    dim_marca = pd.DataFrame({
        "id_marca":          new_ids(n_marca),
        "nome_marca":        fake_pool(fake, "company", n_marca),
        "categoria":         random.choices(CATEGORIAS, k=n_marca),
    })

    fato_pedido = pd.DataFrame({
        "id_pedido":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_centro":         random.choices(dim_centro["id_centro"].tolist(), k=n),
        "id_marca":          random.choices(dim_marca["id_marca"].tolist(), k=n),
        "cliente":           fake_pool(fake, "company", n),
        "caixas":            rng.integers(1, 400, n),
        "valor_total":       rng.uniform(50, 25000, n).round(2),
    })

    return {
        "DimCentroDistribuicao": dim_centro,
        "DimMarca": dim_marca,
        "FatoPedido": fato_pedido,
        "dCalendario": dcalendario(start, end),
    }
