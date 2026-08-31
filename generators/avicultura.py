"""generators/avicultura.py — Setor Avicultura."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_AVE = ["Corte", "Postura"]
CAUSAS_MORTALIDADE = ["Doença", "Calor", "Estresse", "Predador", "Outra"]


def gerar_avicultura(n, start, end):
    n = max(int(n), 1)

    n_granja = min(max(n // 100, 5), 100)
    dim_granja = pd.DataFrame({
        "id_granja":         new_ids(n_granja),
        "cidade":            [fake.city() for _ in range(n_granja)],
        "uf":                [fake.state_abbr() for _ in range(n_granja)],
        "capacidade_aves":   rng.integers(5000, 200000, n_granja),
    })

    n_lote = min(max(n // 8, 50), 5000)
    dim_lote = pd.DataFrame({
        "id_lote":           new_ids(n_lote),
        "id_granja":         random.choices(dim_granja["id_granja"].tolist(), k=n_lote),
        "tipo_ave":          random.choices(TIPOS_AVE, weights=[65, 35], k=n_lote),
        "idade_semanas":     rng.integers(1, 80, n_lote),
    })

    fato_producao = pd.DataFrame({
        "id_producao":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_lote":           random.choices(dim_lote["id_lote"].tolist(), k=n),
        "tipo_produto":      random.choices(["Ovo", "Carne"], weights=[45, 55], k=n),
        "quantidade_kg":     rng.uniform(50, 8000, n).round(1),
        "preco_kg":          rng.uniform(3, 12, n).round(2),
    })

    n_mort = int(n_lote * 2)
    fato_mortalidade = pd.DataFrame({
        "id_mortalidade":    new_ids(n_mort),
        "id_data":           rand_dates(start, end, n_mort),
        "id_lote":           random.choices(dim_lote["id_lote"].tolist(), k=n_mort),
        "aves_mortas":       rng.integers(1, 300, n_mort),
        "causa":             random.choices(CAUSAS_MORTALIDADE, weights=[35, 25, 15, 10, 15], k=n_mort),
    })

    return {
        "DimGranja": dim_granja,
        "DimLote": dim_lote,
        "FatoProducao": fato_producao,
        "FatoMortalidade": fato_mortalidade,
        "dCalendario": dcalendario(start, end),
    }
