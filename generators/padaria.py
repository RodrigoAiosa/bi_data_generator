"""generators/padaria.py — Setor Padaria & Confeitaria."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS_PRODUTO = ["Pão", "Doce", "Salgado", "Bolo", "Bebida", "Café da Manhã"]
CANAIS             = ["Balcão", "Delivery App", "Encomenda", "Atacado"]
TIPOS_LOJA         = ["Bairro", "Shopping", "Centro", "Rodoviária"]


def gerar_padaria(n, start, end):
    n = max(int(n), 1)

    n_loja = min(max(n // 200, 5), 60)
    dim_loja = pd.DataFrame({
        "id_loja":           new_ids(n_loja),
        "nome":              [f"Padaria {fake.last_name()}" for _ in range(n_loja)],
        "tipo":              random.choices(TIPOS_LOJA, weights=[45, 20, 25, 10], k=n_loja),
        "cidade":            [fake.city() for _ in range(n_loja)],
        "uf":                [fake.state_abbr() for _ in range(n_loja)],
    })

    n_produto = min(max(n // 30, 25), 500)
    custo = rng.uniform(0.5, 25, n_produto).round(2)
    dim_produto = pd.DataFrame({
        "id_produto":        new_ids(n_produto),
        "categoria":         random.choices(CATEGORIAS_PRODUTO, weights=[30, 25, 20, 10, 10, 5], k=n_produto),
        "custo_unitario":    custo,
        "preco_venda":       (custo * rng.uniform(1.6, 3.2, n_produto)).round(2),
    })

    produto_idx = random.choices(range(n_produto), k=n)
    preco = dim_produto["preco_venda"].to_numpy()[produto_idx]
    quantidade = rng.integers(1, 12, n)
    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_loja":           random.choices(dim_loja["id_loja"].tolist(), k=n),
        "id_produto":        dim_produto["id_produto"].to_numpy()[produto_idx],
        "canal":             random.choices(CANAIS, weights=[55, 20, 15, 10], k=n),
        "quantidade":        quantidade,
        "valor":             (preco * quantidade).round(2),
    })

    n_producao = int(n_loja * 250)
    fato_producao = pd.DataFrame({
        "id_producao":       new_ids(n_producao),
        "id_data":           rand_dates(start, end, n_producao),
        "id_loja":           random.choices(dim_loja["id_loja"].tolist(), k=n_producao),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n_producao),
        "quantidade_produzida": rng.integers(10, 400, n_producao),
        "perda_pct":         rng.uniform(0, 15, n_producao).round(1),
    })

    return {
        "DimLoja": dim_loja,
        "DimProduto": dim_produto,
        "FatoVenda": fato_venda,
        "FatoProducao": fato_producao,
        "dCalendario": dcalendario(start, end),
    }
