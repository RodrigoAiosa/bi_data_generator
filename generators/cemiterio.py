"""generators/cemiterio.py — Setor Cemitério & Serviços Perpétuos."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

TIPOS_JAZIGO = ["Gaveta", "Capela", "Jardim"]
SERVICOS_MANUTENCAO = ["Limpeza", "Jardinagem", "Reparo", "Pintura"]


def gerar_cemiterio(n, start, end):
    n = max(int(n), 1)

    n_cemiterio = min(max(n // 200, 3), 40)
    dim_cemiterio = pd.DataFrame({
        "id_cemiterio":      new_ids(n_cemiterio),
        "cidade":            fake_pool(fake, "city", n_cemiterio),
        "uf":                fake_pool(fake, "state_abbr", n_cemiterio),
        "num_jazigos":       rng.integers(500, 20000, n_cemiterio),
    })

    n_jazigo = min(max(n // 4, 200), 20000)
    dim_jazigo = pd.DataFrame({
        "id_jazigo":         new_ids(n_jazigo),
        "id_cemiterio":      random.choices(dim_cemiterio["id_cemiterio"].tolist(), k=n_jazigo),
        "tipo_jazigo":       random.choices(TIPOS_JAZIGO, weights=[55, 15, 30], k=n_jazigo),
        "status":            random.choices(["Disponível", "Ocupado"], weights=[35, 65], k=n_jazigo),
    })

    n_sepultamento = int(n * 0.4)
    fato_sepultamento = pd.DataFrame({
        "id_sepultamento":   new_ids(n_sepultamento),
        "id_data":           rand_dates(start, end, n_sepultamento),
        "id_jazigo":         random.choices(dim_jazigo["id_jazigo"].tolist(), k=n_sepultamento),
        "valor_venda":       rng.uniform(3000, 60000, n_sepultamento).round(2),
    })

    fato_manutencao = pd.DataFrame({
        "id_manutencao":     new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_jazigo":         random.choices(dim_jazigo["id_jazigo"].tolist(), k=n),
        "tipo_servico":      random.choices(SERVICOS_MANUTENCAO, k=n),
        "valor":             rng.uniform(50, 900, n).round(2),
    })

    return {
        "DimCemiterio": dim_cemiterio,
        "DimJazigo": dim_jazigo,
        "FatoSepultamento": fato_sepultamento,
        "FatoManutencao": fato_manutencao,
        "dCalendario": dcalendario(start, end),
    }
