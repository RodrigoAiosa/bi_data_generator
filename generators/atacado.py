"""generators/atacado.py — Setor Atacado & Atacarejo."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

CATEGORIAS = ["Mercearia", "Bebidas", "Limpeza", "Higiene", "Hortifruti", "Frios & Laticínios"]
UNIDADES_VENDA = ["Caixa", "Fardo", "Pallet", "Unidade"]


def gerar_atacado(n, start, end):
    n = max(int(n), 1)

    n_loja = min(max(n // 300, 5), 60)
    dim_loja = pd.DataFrame({
        "id_loja":           new_ids(n_loja),
        "cidade":            fake_pool(fake, "city", n_loja),
        "uf":                fake_pool(fake, "state_abbr", n_loja),
        "tipo_loja":         random.choices(["Atacarejo", "Distribuidor B2B"], weights=[65, 35], k=n_loja),
    })

    n_produto = min(max(n // 20, 100), 6000)
    dim_produto = pd.DataFrame({
        "id_produto":        new_ids(n_produto),
        "nome_produto":      [fake.word().capitalize() for _ in range(n_produto)],
        "categoria":         random.choices(CATEGORIAS, k=n_produto),
        "unidade_venda":     random.choices(UNIDADES_VENDA, k=n_produto),
    })

    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_loja":           random.choices(dim_loja["id_loja"].tolist(), k=n),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n),
        "cnpj_cliente":      fake_pool(fake, "cnpj", n),
        "quantidade":        rng.integers(1, 200, n),
        "valor_total":       rng.uniform(20, 12000, n).round(2),
    })

    return {
        "DimLoja": dim_loja,
        "DimProduto": dim_produto,
        "FatoVenda": fato_venda,
        "dCalendario": dcalendario(start, end),
    }
