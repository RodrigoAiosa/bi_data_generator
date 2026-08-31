"""generators/impressao_3d.py — Setor Impressão 3D & Prototipagem."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TECNOLOGIAS = ["FDM", "SLA", "SLS", "DLP"]
MATERIAIS = ["PLA", "ABS", "Resina", "Nylon", "PETG"]


def gerar_impressao_3d(n, start, end):
    n = max(int(n), 1)

    n_empresa = min(max(n // 200, 4), 60)
    dim_empresa = pd.DataFrame({
        "id_empresa":        new_ids(n_empresa),
        "cidade":            [fake.city() for _ in range(n_empresa)],
        "uf":                [fake.state_abbr() for _ in range(n_empresa)],
    })

    n_impressora = min(max(n // 20, 15), 1200)
    dim_impressora = pd.DataFrame({
        "id_impressora":     new_ids(n_impressora),
        "id_empresa":        random.choices(dim_empresa["id_empresa"].tolist(), k=n_impressora),
        "tecnologia":        random.choices(TECNOLOGIAS, k=n_impressora),
        "material_padrao":   random.choices(MATERIAIS, k=n_impressora),
    })

    fato_pedido = pd.DataFrame({
        "id_pedido":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_impressora":     random.choices(dim_impressora["id_impressora"].tolist(), k=n),
        "cliente":           [fake.name() for _ in range(n)],
        "tempo_impressao_h": rng.uniform(0.5, 60, n).round(1),
        "gramas_material":   rng.integers(5, 3000, n),
        "valor":             rng.uniform(20, 2500, n).round(2),
    })

    return {
        "DimEmpresa": dim_empresa,
        "DimImpressora": dim_impressora,
        "FatoPedido": fato_pedido,
        "dCalendario": dcalendario(start, end),
    }
