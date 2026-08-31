"""generators/plasticos.py — Setor Plásticos & Fábrica de Plásticos."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS = ["Embalagem Rígida", "Utilidades Domésticas", "Componente Industrial", "Tubos e Conexões"]
RESINAS = ["PET", "PEAD", "PP", "PVC", "PS"]


def gerar_plasticos(n, start, end):
    n = max(int(n), 1)

    n_fabrica = min(max(n // 300, 3), 40)
    dim_fabrica = pd.DataFrame({
        "id_fabrica":        new_ids(n_fabrica),
        "cidade":            [fake.city() for _ in range(n_fabrica)],
        "uf":                [fake.state_abbr() for _ in range(n_fabrica)],
    })

    n_produto = min(max(n // 25, 20), 3000)
    dim_produto = pd.DataFrame({
        "id_produto":        new_ids(n_produto),
        "id_fabrica":        random.choices(dim_fabrica["id_fabrica"].tolist(), k=n_produto),
        "categoria":         random.choices(CATEGORIAS, k=n_produto),
        "resina":            random.choices(RESINAS, k=n_produto),
    })

    fato_producao = pd.DataFrame({
        "id_producao":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n),
        "kg_produzidos":     rng.integers(100, 20000, n),
        "custo_kg":          rng.uniform(3, 18, n).round(2),
    })

    n_venda = int(n * 1.2)
    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n_venda),
        "id_data":           rand_dates(start, end, n_venda),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n_venda),
        "cliente":           [fake.company() for _ in range(n_venda)],
        "kg_vendidos":       rng.integers(50, 15000, n_venda),
        "preco_kg":          rng.uniform(4, 30, n_venda).round(2),
    })

    return {
        "DimFabrica": dim_fabrica,
        "DimProduto": dim_produto,
        "FatoProducao": fato_producao,
        "FatoVenda": fato_venda,
        "dCalendario": dcalendario(start, end),
    }
