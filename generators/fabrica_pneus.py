"""generators/fabrica_pneus.py — Setor Fábrica de Pneus & Borracha."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS = ["Passeio", "Caminhão", "Moto", "SUV", "Agrícola"]
AROS = [13, 14, 15, 16, 17, 18, 20, 22]


def gerar_fabrica_pneus(n, start, end):
    n = max(int(n), 1)

    n_fabrica = min(max(n // 400, 3), 30)
    dim_fabrica = pd.DataFrame({
        "id_fabrica":        new_ids(n_fabrica),
        "cidade":            [fake.city() for _ in range(n_fabrica)],
        "uf":                [fake.state_abbr() for _ in range(n_fabrica)],
    })

    n_modelo = min(max(n // 30, 15), 1500)
    dim_modelo = pd.DataFrame({
        "id_modelo":         new_ids(n_modelo),
        "id_fabrica":        random.choices(dim_fabrica["id_fabrica"].tolist(), k=n_modelo),
        "categoria":         random.choices(CATEGORIAS, k=n_modelo),
        "aro":               random.choices(AROS, k=n_modelo),
    })

    fato_producao = pd.DataFrame({
        "id_producao":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_modelo":         random.choices(dim_modelo["id_modelo"].tolist(), k=n),
        "unidades_produzidas": rng.integers(100, 15000, n),
        "custo_unitario":    rng.uniform(60, 900, n).round(2),
    })

    n_venda = int(n * 1.2)
    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n_venda),
        "id_data":           rand_dates(start, end, n_venda),
        "id_modelo":         random.choices(dim_modelo["id_modelo"].tolist(), k=n_venda),
        "canal":             random.choices(["Revenda", "Montadora", "Exportação"], weights=[55, 30, 15], k=n_venda),
        "unidades_vendidas": rng.integers(1, 3000, n_venda),
        "preco_unitario":    rng.uniform(150, 2500, n_venda).round(2),
    })

    return {
        "DimFabrica": dim_fabrica,
        "DimModelo": dim_modelo,
        "FatoProducao": fato_producao,
        "FatoVenda": fato_venda,
        "dCalendario": dcalendario(start, end),
    }
