"""generators/cerealista.py — Setor Cerealista & Armazém de Grãos."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

GRAOS = ["Soja", "Milho", "Trigo", "Arroz", "Sorgo"]
CLASSIFICACOES = ["Tipo 1", "Tipo 2", "Tipo 3", "Fora de Tipo"]


def gerar_cerealista(n, start, end):
    n = max(int(n), 1)

    n_armazem = min(max(n // 150, 5), 60)
    dim_armazem = pd.DataFrame({
        "id_armazem":        new_ids(n_armazem),
        "cidade":            [fake.city() for _ in range(n_armazem)],
        "uf":                [fake.state_abbr() for _ in range(n_armazem)],
        "capacidade_toneladas": rng.integers(1000, 80000, n_armazem),
    })

    n_produtor = min(max(n // 5, 100), 12000)
    dim_produtor = pd.DataFrame({
        "id_produtor":       new_ids(n_produtor),
        "nome_produtor":     [fake.company() for _ in range(n_produtor)],
        "uf":                [fake.state_abbr() for _ in range(n_produtor)],
    })

    fato_recebimento = pd.DataFrame({
        "id_recebimento":    new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_armazem":        random.choices(dim_armazem["id_armazem"].tolist(), k=n),
        "id_produtor":       random.choices(dim_produtor["id_produtor"].tolist(), k=n),
        "grao":              random.choices(GRAOS, weights=[40, 30, 15, 10, 5], k=n),
        "toneladas":         rng.uniform(1, 500, n).round(2),
        "umidade_pct":       rng.uniform(10, 22, n).round(1),
        "classificacao":     random.choices(CLASSIFICACOES, weights=[45, 35, 15, 5], k=n),
    })

    return {
        "DimArmazem": dim_armazem,
        "DimProdutor": dim_produtor,
        "FatoRecebimento": fato_recebimento,
        "dCalendario": dcalendario(start, end),
    }
