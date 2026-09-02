"""generators/floricultura.py — Setor Floricultura."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

CATEGORIAS_PRODUTO = ["Buquê", "Arranjo", "Planta Ornamental", "Cesta de Café da Manhã",
                       "Coroa de Flores", "Orquídea", "Vaso Decorativo"]
CANAIS_VENDA        = ["Loja Física", "Online", "Telefone", "Marketplace de Flores"]
FORMAS_PAGAMENTO     = ["Pix", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"]
OCASIOES             = ["Casamento", "Funeral", "Aniversário", "Dia das Mães",
                         "Formatura", "Dia dos Namorados", "Nascimento", "Corporativo"]
STATUS_ENCOMENDA      = ["Confirmada", "Em Produção", "Entregue", "Cancelada"]


def gerar_floricultura(n, start, end):
    n = max(int(n), 1)

    n_loja = min(max(n // 200, 5), 40)
    dim_loja = pd.DataFrame({
        "id_loja":           new_ids(n_loja),
        "nome_loja":         [f"Floricultura {fake.first_name()}" for _ in range(n_loja)],
        "cidade":            fake_pool(fake, "city", n_loja),
        "uf":                fake_pool(fake, "state_abbr", n_loja),
    })

    n_produto = min(max(n // 25, 25), 400)
    dim_produto = pd.DataFrame({
        "id_produto":        new_ids(n_produto),
        "nome_produto":      [f"{c} {fake.word().capitalize()}" for c in random.choices(CATEGORIAS_PRODUTO, k=n_produto)],
        "categoria":         random.choices(CATEGORIAS_PRODUTO, k=n_produto),
        "preco_base":        rng.uniform(29.9, 349.9, n_produto).round(2),
    })

    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_loja":           random.choices(dim_loja["id_loja"].tolist(), k=n),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n),
        "canal":             random.choices(CANAIS_VENDA, weights=[45, 35, 10, 10], k=n),
        "quantidade":        rng.integers(1, 6, n),
        "valor_total":       rng.uniform(29.9, 899.9, n).round(2),
        "forma_pagamento":   random.choices(FORMAS_PAGAMENTO, weights=[45, 30, 15, 10], k=n),
    })

    n_encomenda = int(n * 0.3)
    fato_encomenda = pd.DataFrame({
        "id_encomenda":      new_ids(n_encomenda),
        "id_data":           rand_dates(start, end, n_encomenda),
        "id_loja":           random.choices(dim_loja["id_loja"].tolist(), k=n_encomenda),
        "ocasiao":           random.choices(OCASIOES, k=n_encomenda),
        "valor":             rng.uniform(89.9, 2499.9, n_encomenda).round(2),
        "status":            random.choices(STATUS_ENCOMENDA, weights=[20, 15, 60, 5], k=n_encomenda),
    })

    return {
        "DimLoja": dim_loja,
        "DimProduto": dim_produto,
        "FatoVenda": fato_venda,
        "FatoEncomenda": fato_encomenda,
        "dCalendario": dcalendario(start, end),
    }
