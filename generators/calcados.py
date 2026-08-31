"""generators/calcados.py — Setor Calçados."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS = ["Esportivo", "Social", "Casual", "Infantil", "Bota"]
MATERIAIS = ["Couro", "Sintético", "Tecido", "Borracha"]
CANAIS = ["Loja Própria", "Atacado", "E-commerce", "Exportação"]


def gerar_calcados(n, start, end):
    n = max(int(n), 1)

    n_fabrica = min(max(n // 300, 3), 40)
    dim_fabrica = pd.DataFrame({
        "id_fabrica":        new_ids(n_fabrica),
        "cidade":            [fake.city() for _ in range(n_fabrica)],
        "uf":                [fake.state_abbr() for _ in range(n_fabrica)],
    })

    n_modelo = min(max(n // 20, 30), 3000)
    dim_modelo = pd.DataFrame({
        "id_modelo":         new_ids(n_modelo),
        "id_fabrica":        random.choices(dim_fabrica["id_fabrica"].tolist(), k=n_modelo),
        "categoria":         random.choices(CATEGORIAS, k=n_modelo),
        "material":          random.choices(MATERIAIS, k=n_modelo),
    })

    fato_producao = pd.DataFrame({
        "id_producao":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_modelo":         random.choices(dim_modelo["id_modelo"].tolist(), k=n),
        "pares_produzidos":  rng.integers(50, 5000, n),
        "custo_unitario":    rng.uniform(15, 180, n).round(2),
    })

    n_venda = int(n * 1.3)
    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n_venda),
        "id_data":           rand_dates(start, end, n_venda),
        "id_modelo":         random.choices(dim_modelo["id_modelo"].tolist(), k=n_venda),
        "canal":             random.choices(CANAIS, weights=[30, 35, 25, 10], k=n_venda),
        "pares_vendidos":    rng.integers(1, 500, n_venda),
        "preco_unitario":    rng.uniform(40, 600, n_venda).round(2),
    })

    return {
        "DimFabrica": dim_fabrica,
        "DimModelo": dim_modelo,
        "FatoProducao": fato_producao,
        "FatoVenda": fato_venda,
        "dCalendario": dcalendario(start, end),
    }
