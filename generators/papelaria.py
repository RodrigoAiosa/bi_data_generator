"""generators/papelaria.py — Setor Papelaria & Material Escolar."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS = ["Cadernos", "Canetas e Lápis", "Mochilas", "Papel e Cartolina", "Arte e Pintura",
               "Informática", "Escritório", "Livros Didáticos"]
MARCAS = ["Tilibra", "Faber-Castell", "BIC", "Maped", "Chamex", "Foroni", "Pentel"]
CANAIS_VENDA = ["Loja Física", "E-commerce Próprio", "Marketplace", "Venda Corporativa (B2B)"]
FORMAS_PAGAMENTO = ["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "Pix", "Boleto"]


def gerar_papelaria(n, start, end):
    n = max(int(n), 1)

    n_produto = min(max(n // 15, 40), 2000)
    dim_produto = pd.DataFrame({
        "id_produto":        new_ids(n_produto),
        "nome":              [f"{random.choice(CATEGORIAS)} {fake.word().capitalize()}" for _ in range(n_produto)],
        "categoria":         random.choices(CATEGORIAS, k=n_produto),
        "marca":             random.choices(MARCAS, k=n_produto),
        "preco":             rng.uniform(1.5, 450, n_produto).round(2),
    })

    n_loja = min(max(n // 400, 3), 60)
    dim_loja = pd.DataFrame({
        "id_loja":           new_ids(n_loja),
        "nome":              [f"Loja {fake.city()}" for _ in range(n_loja)],
        "uf":                [fake.state_abbr() for _ in range(n_loja)],
    })

    qtd = rng.integers(1, 30, n)
    produto_idx = random.choices(range(n_produto), k=n)
    preco_unit = dim_produto["preco"].to_numpy()[produto_idx]
    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_produto":        dim_produto["id_produto"].to_numpy()[produto_idx],
        "id_loja":           random.choices(dim_loja["id_loja"].tolist(), k=n),
        "quantidade":        qtd,
        "valor_total":       (qtd * preco_unit).round(2),
        "canal":             random.choices(CANAIS_VENDA, weights=[45, 25, 20, 10], k=n),
        "forma_pagamento":   random.choices(FORMAS_PAGAMENTO, weights=[15, 35, 20, 25, 5], k=n),
    })

    n_estoque = int(n_produto * 2)
    qtd_recebida = rng.integers(50, 5000, n_estoque)
    fato_estoque = pd.DataFrame({
        "id_estoque":        new_ids(n_estoque),
        "id_data":           rand_dates(start, end, n_estoque),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n_estoque),
        "id_loja":           random.choices(dim_loja["id_loja"].tolist(), k=n_estoque),
        "quantidade_recebida": qtd_recebida,
        "quantidade_disponivel": (qtd_recebida * rng.uniform(0.05, 0.95, n_estoque)).round(0).astype(int),
        "avarias":           rng.integers(0, 50, n_estoque),
    })

    return {
        "DimProduto": dim_produto,
        "DimLoja": dim_loja,
        "FatoVenda": fato_venda,
        "FatoEstoque": fato_estoque,
        "dCalendario": dcalendario(start, end),
    }
