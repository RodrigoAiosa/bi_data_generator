"""generators/despachante_aduaneiro.py — Setor Despachante Aduaneiro."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")


def gerar_despachante_aduaneiro(n, start, end):
    n = max(int(n), 1)

    n_despachante = min(max(n // 100, 5), 100)
    dim_despachante = pd.DataFrame({
        "id_despachante":    new_ids(n_despachante),
        "nome":              fake_pool(fake, "name", n_despachante),
        "cidade":            fake_pool(fake, "city", n_despachante),
        "uf":                fake_pool(fake, "state_abbr", n_despachante),
    })

    n_cliente = min(max(n // 5, 100), 10000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome_empresa":      fake_pool(fake, "company", n_cliente),
        "tipo":              random.choices(["Importador", "Exportador"], weights=[60, 40], k=n_cliente),
    })

    fato_processo = pd.DataFrame({
        "id_processo":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_despachante":    random.choices(dim_despachante["id_despachante"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "tipo_operacao":     random.choices(["Importação", "Exportação"], weights=[60, 40], k=n),
        "valor_mercadoria":  rng.uniform(2000, 3000000, n).round(2),
        "taxa_servico":      rng.uniform(300, 15000, n).round(2),
        "dias_desembaraco":  rng.integers(1, 25, n),
    })

    return {
        "DimDespachante": dim_despachante,
        "DimCliente": dim_cliente,
        "FatoProcesso": fato_processo,
        "dCalendario": dcalendario(start, end),
    }
