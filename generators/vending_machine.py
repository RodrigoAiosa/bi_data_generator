"""generators/vending_machine.py — Setor Vending Machine & Autoatendimento."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_LOCALIZACAO = ["Escritório Corporativo", "Shopping Center", "Hospital", "Universidade", "Academia", "Estação de Transporte"]
CATEGORIAS_PRODUTO = ["Snack", "Bebida Gelada", "Café/Bebida Quente", "Doce", "Salgado", "Produto Saudável"]
FORMAS_PAGAMENTO = ["Cartão de Crédito", "Cartão de Débito", "Pix", "Aproximação/NFC", "Cédula/Moeda"]


def gerar_vending_machine(n, start, end):
    n = max(int(n), 1)

    n_maquina = min(max(n // 30, 20), 3000)
    dim_maquina = pd.DataFrame({
        "id_maquina":        new_ids(n_maquina),
        "localizacao":       random.choices(TIPOS_LOCALIZACAO, k=n_maquina),
        "cidade":            [fake.city() for _ in range(n_maquina)],
        "capacidade_itens":  rng.integers(30, 200, n_maquina),
        "aceita_pagamento_digital": random.choices([True, False], weights=[80, 20], k=n_maquina),
        "instalada_em":      rand_dates(start, end, n_maquina),
    })

    n_produto = min(max(n // 100, 15), 300)
    custo = rng.uniform(0.8, 6.0, n_produto).round(2)
    dim_produto = pd.DataFrame({
        "id_produto":        new_ids(n_produto),
        "nome":              [fake.word().capitalize() for _ in range(n_produto)],
        "categoria":         random.choices(CATEGORIAS_PRODUTO, k=n_produto),
        "custo":             custo,
        "preco_venda":       (custo * rng.uniform(1.8, 3.5, n_produto)).round(2),
    })

    prod_idx = random.choices(range(n_produto), k=n)
    preco_unit = dim_produto["preco_venda"].to_numpy()[prod_idx]
    qtd = rng.integers(1, 4, n)
    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_maquina":        random.choices(dim_maquina["id_maquina"].tolist(), k=n),
        "id_produto":        dim_produto["id_produto"].to_numpy()[prod_idx],
        "quantidade":        qtd,
        "valor_total":       (qtd * preco_unit).round(2),
        "forma_pagamento":   random.choices(FORMAS_PAGAMENTO, weights=[25, 20, 30, 15, 10], k=n),
    })

    n_reposicao = int(n_maquina * 40)
    fato_reposicao = pd.DataFrame({
        "id_reposicao":      new_ids(n_reposicao),
        "id_data":           rand_dates(start, end, n_reposicao),
        "id_maquina":        random.choices(dim_maquina["id_maquina"].tolist(), k=n_reposicao),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n_reposicao),
        "quantidade_reposta": rng.integers(5, 60, n_reposicao),
        "custo_reposicao":   rng.uniform(20, 400, n_reposicao).round(2),
        "itens_vencidos_retirados": rng.integers(0, 10, n_reposicao),
    })

    return {
        "DimMaquina": dim_maquina,
        "DimProduto": dim_produto,
        "FatoVenda": fato_venda,
        "FatoReposicao": fato_reposicao,
        "dCalendario": dcalendario(start, end),
    }
