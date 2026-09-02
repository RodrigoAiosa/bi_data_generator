"""generators/vidracaria.py — Setor Vidraçaria & Fábrica de Vidros."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

TIPOS_PRODUTO = ["Vidro Temperado", "Espelho", "Box de Banheiro", "Janela", "Fachada"]


def gerar_vidracaria(n, start, end):
    n = max(int(n), 1)

    n_fabrica = min(max(n // 250, 3), 40)
    dim_fabrica = pd.DataFrame({
        "id_fabrica":        new_ids(n_fabrica),
        "cidade":            fake_pool(fake, "city", n_fabrica),
        "uf":                fake_pool(fake, "state_abbr", n_fabrica),
    })

    n_produto = min(max(n // 25, 15), 2000)
    dim_produto = pd.DataFrame({
        "id_produto":        new_ids(n_produto),
        "id_fabrica":        random.choices(dim_fabrica["id_fabrica"].tolist(), k=n_produto),
        "tipo":              random.choices(TIPOS_PRODUTO, k=n_produto),
        "espessura_mm":      random.choices([4, 6, 8, 10, 12], k=n_produto),
    })

    fato_pedido = pd.DataFrame({
        "id_pedido":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n),
        "cliente":           fake_pool(fake, "name", n),
        "m2":                rng.uniform(0.5, 40, n).round(2),
        "valor_total":       rng.uniform(150, 15000, n).round(2),
        "instalacao_inclusa": random.choices([True, False], weights=[55, 45], k=n),
    })

    return {
        "DimFabrica": dim_fabrica,
        "DimProduto": dim_produto,
        "FatoPedido": fato_pedido,
        "dCalendario": dcalendario(start, end),
    }
