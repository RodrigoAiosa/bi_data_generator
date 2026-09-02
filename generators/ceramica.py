"""generators/ceramica.py — Setor Cerâmica & Revestimentos."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

TIPOS_PRODUTO = ["Piso", "Azulejo", "Porcelanato", "Telha"]
ACABAMENTOS = ["Fosco", "Polido", "Acetinado", "Natural"]


def gerar_ceramica(n, start, end):
    n = max(int(n), 1)

    n_fabrica = min(max(n // 300, 3), 40)
    dim_fabrica = pd.DataFrame({
        "id_fabrica":        new_ids(n_fabrica),
        "cidade":            fake_pool(fake, "city", n_fabrica),
        "uf":                fake_pool(fake, "state_abbr", n_fabrica),
    })

    n_linha = min(max(n // 30, 20), 2000)
    dim_linha = pd.DataFrame({
        "id_linha":          new_ids(n_linha),
        "id_fabrica":        random.choices(dim_fabrica["id_fabrica"].tolist(), k=n_linha),
        "tipo_produto":      random.choices(TIPOS_PRODUTO, k=n_linha),
        "acabamento":        random.choices(ACABAMENTOS, k=n_linha),
    })

    fato_producao = pd.DataFrame({
        "id_producao":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_linha":          random.choices(dim_linha["id_linha"].tolist(), k=n),
        "m2_produzidos":     rng.integers(100, 15000, n),
        "custo_m2":          rng.uniform(8, 60, n).round(2),
    })

    n_venda = int(n * 1.2)
    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n_venda),
        "id_data":           rand_dates(start, end, n_venda),
        "id_linha":          random.choices(dim_linha["id_linha"].tolist(), k=n_venda),
        "cliente":           fake_pool(fake, "company", n_venda),
        "m2_vendidos":       rng.integers(20, 8000, n_venda),
        "preco_m2":          rng.uniform(15, 120, n_venda).round(2),
    })

    return {
        "DimFabrica": dim_fabrica,
        "DimLinhaProduto": dim_linha,
        "FatoProducao": fato_producao,
        "FatoVenda": fato_venda,
        "dCalendario": dcalendario(start, end),
    }
