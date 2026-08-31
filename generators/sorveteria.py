"""generators/sorveteria.py — Setor Sorveteria & Fábrica de Sorvetes."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS = ["Cremoso", "Sorbet", "Especial", "Diet"]
SABORES = ["Chocolate", "Morango", "Baunilha", "Flocos", "Napolitano", "Maracujá", "Doce de Leite", "Limão"]
CANAIS = ["Loja", "Distribuidor", "Delivery"]


def gerar_sorveteria(n, start, end):
    n = max(int(n), 1)

    n_fabrica = min(max(n // 200, 4), 60)
    dim_fabrica = pd.DataFrame({
        "id_fabrica":        new_ids(n_fabrica),
        "cidade":            [fake.city() for _ in range(n_fabrica)],
        "uf":                [fake.state_abbr() for _ in range(n_fabrica)],
    })

    n_sabor = min(max(n // 30, 20), 1500)
    dim_sabor = pd.DataFrame({
        "id_sabor":          new_ids(n_sabor),
        "id_fabrica":        random.choices(dim_fabrica["id_fabrica"].tolist(), k=n_sabor),
        "categoria":         random.choices(CATEGORIAS, weights=[60, 15, 20, 5], k=n_sabor),
        "nome_sabor":        random.choices(SABORES, k=n_sabor),
    })

    fato_producao = pd.DataFrame({
        "id_producao":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_sabor":          random.choices(dim_sabor["id_sabor"].tolist(), k=n),
        "litros_produzidos": rng.integers(20, 3000, n),
        "custo_litro":       rng.uniform(4, 25, n).round(2),
    })

    n_venda = int(n * 1.3)
    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n_venda),
        "id_data":           rand_dates(start, end, n_venda),
        "id_sabor":          random.choices(dim_sabor["id_sabor"].tolist(), k=n_venda),
        "canal":             random.choices(CANAIS, weights=[55, 25, 20], k=n_venda),
        "unidades_vendidas": rng.integers(1, 300, n_venda),
        "preco_unitario":    rng.uniform(6, 60, n_venda).round(2),
    })

    return {
        "DimFabrica": dim_fabrica,
        "DimSabor": dim_sabor,
        "FatoProducao": fato_producao,
        "FatoVenda": fato_venda,
        "dCalendario": dcalendario(start, end),
    }
