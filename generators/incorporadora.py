"""generators/incorporadora.py — Setor Incorporadora Imobiliária."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

TIPOS_UNIDADE = ["Studio", "2 Quartos", "3 Quartos", "Cobertura"]
FORMAS_PAGAMENTO = ["À Vista", "Financiado", "Consórcio"]


def gerar_incorporadora(n, start, end):
    n = max(int(n), 1)

    n_empreendimento = min(max(n // 100, 5), 100)
    dim_empreendimento = pd.DataFrame({
        "id_empreendimento": new_ids(n_empreendimento),
        "nome_empreendimento": [f"Residencial {fake.last_name()}" for _ in range(n_empreendimento)],
        "cidade":            fake_pool(fake, "city", n_empreendimento),
        "uf":                fake_pool(fake, "state_abbr", n_empreendimento),
        "num_unidades":      rng.integers(20, 400, n_empreendimento),
    })

    n_unidade = min(max(n // 3, 200), 20000)
    dim_unidade = pd.DataFrame({
        "id_unidade":        new_ids(n_unidade),
        "id_empreendimento": random.choices(dim_empreendimento["id_empreendimento"].tolist(), k=n_unidade),
        "tipo":              random.choices(TIPOS_UNIDADE, weights=[20, 40, 30, 10], k=n_unidade),
        "metragem":          rng.uniform(28, 220, n_unidade).round(1),
    })

    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n),
        "comprador":         fake_pool(fake, "name", n),
        "valor_venda":       rng.uniform(120000, 3500000, n).round(2),
        "forma_pagamento":   random.choices(FORMAS_PAGAMENTO, weights=[15, 65, 20], k=n),
    })

    return {
        "DimEmpreendimento": dim_empreendimento,
        "DimUnidade": dim_unidade,
        "FatoVenda": fato_venda,
        "dCalendario": dcalendario(start, end),
    }
