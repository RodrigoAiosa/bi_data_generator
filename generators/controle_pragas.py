"""generators/controle_pragas.py — Setor Controle de Pragas & Dedetização."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_PRAGA = ["Cupim", "Baratas", "Ratos", "Formigas", "Pombos", "Percevejos"]


def gerar_controle_pragas(n, start, end):
    n = max(int(n), 1)

    n_tecnico = min(max(n // 40, 10), 800)
    dim_tecnico = pd.DataFrame({
        "id_tecnico":        new_ids(n_tecnico),
        "nome":              [fake.name() for _ in range(n_tecnico)],
        "especialidade":     random.choices(["Urbana", "Agrícola", "Industrial"], weights=[60, 15, 25], k=n_tecnico),
    })

    n_cliente = min(max(n // 3, 200), 20000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.name() for _ in range(n_cliente)],
        "tipo":              random.choices(["Residencial", "Comercial", "Industrial"], weights=[55, 30, 15], k=n_cliente),
    })

    fato_os = pd.DataFrame({
        "id_os":             new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_tecnico":        random.choices(dim_tecnico["id_tecnico"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "tipo_praga":        random.choices(TIPOS_PRAGA, k=n),
        "valor":             rng.uniform(80, 3500, n).round(2),
        "garantia_dias":     random.choices([30, 90, 180, 365], k=n),
    })

    return {
        "DimTecnico": dim_tecnico,
        "DimCliente": dim_cliente,
        "FatoOrdemServico": fato_os,
        "dCalendario": dcalendario(start, end),
    }
