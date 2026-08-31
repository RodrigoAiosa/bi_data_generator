"""generators/artesanato.py — Setor Artesanato."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS = ["Cerâmica", "Tricô & Crochê", "Madeira", "Bijuteria", "Tecido & Bordado", "Vidro & Resina"]
CANAIS     = ["Feira", "Loja Física", "E-commerce Próprio", "Marketplace", "Encomenda Direta"]


def gerar_artesanato(n, start, end):
    n = max(int(n), 1)

    n_artesao = min(max(n // 60, 8), 500)
    dim_artesao = pd.DataFrame({
        "id_artesao":        new_ids(n_artesao),
        "nome":              [fake.name() for _ in range(n_artesao)],
        "especialidade":     random.choices(CATEGORIAS, k=n_artesao),
        "anos_atividade":    rng.integers(1, 40, n_artesao),
    })

    n_produto = min(max(n // 15, 30), 3000)
    custo_material = rng.uniform(3, 120, n_produto).round(2)
    dim_produto = pd.DataFrame({
        "id_produto":        new_ids(n_produto),
        "categoria":         random.choices(CATEGORIAS, k=n_produto),
        "custo_material":    custo_material,
        "preco_venda":       (custo_material * rng.uniform(1.8, 4.0, n_produto)).round(2),
    })

    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_artesao":        random.choices(dim_artesao["id_artesao"].tolist(), k=n),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n),
        "canal":             random.choices(CANAIS, weights=[25, 15, 25, 25, 10], k=n),
        "quantidade":        rng.integers(1, 8, n),
        "valor":             rng.uniform(15, 900, n).round(2),
    })

    n_producao = int(n_artesao * 8)
    fato_producao = pd.DataFrame({
        "id_producao":       new_ids(n_producao),
        "id_data":           rand_dates(start, end, n_producao),
        "id_artesao":        random.choices(dim_artesao["id_artesao"].tolist(), k=n_producao),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n_producao),
        "tempo_producao_h":  rng.uniform(0.5, 40, n_producao).round(1),
        "quantidade_produzida": rng.integers(1, 20, n_producao),
    })

    return {
        "DimArtesao": dim_artesao,
        "DimProduto": dim_produto,
        "FatoVenda": fato_venda,
        "FatoProducao": fato_producao,
        "dCalendario": dcalendario(start, end),
    }
