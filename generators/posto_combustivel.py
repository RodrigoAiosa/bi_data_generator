"""generators/posto_combustivel.py — Setor Posto de Combustível & Conveniência."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

BANDEIRAS           = ["Shell", "Ipiranga", "Petrobras", "BR Mania", "Bandeira Branca"]
TIPOS_COMBUSTIVEL   = ["Gasolina Comum", "Gasolina Aditivada", "Etanol", "Diesel S10", "GNV"]
FORMAS_PAGAMENTO     = ["Pix", "Cartão de Crédito", "Cartão de Débito", "Dinheiro", "Frota/Convênio"]
CATEGORIAS_CONVENIENCIA = ["Bebidas", "Snacks", "Cigarros", "Higiene Pessoal", "Alimentação Rápida"]


def gerar_posto_combustivel(n, start, end):
    n = max(int(n), 1)

    n_posto = min(max(n // 200, 5), 50)
    dim_posto = pd.DataFrame({
        "id_posto":          new_ids(n_posto),
        "nome_posto":        [f"Posto {fake.last_name()}" for _ in range(n_posto)],
        "cidade":            fake_pool(fake, "city", n_posto),
        "bandeira":          random.choices(BANDEIRAS, weights=[25, 30, 25, 10, 10], k=n_posto),
    })

    dim_combustivel = pd.DataFrame({
        "id_combustivel":    new_ids(len(TIPOS_COMBUSTIVEL)),
        "tipo_combustivel":  TIPOS_COMBUSTIVEL,
        "preco_litro":       rng.uniform(3.9, 6.8, len(TIPOS_COMBUSTIVEL)).round(2),
    })

    fato_abastecimento = pd.DataFrame({
        "id_abastecimento":  new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_posto":          random.choices(dim_posto["id_posto"].tolist(), k=n),
        "id_combustivel":    random.choices(dim_combustivel["id_combustivel"].tolist(), weights=[35, 10, 30, 20, 5], k=n),
        "litros":            rng.uniform(5, 60, n).round(2),
        "valor_total":       rng.uniform(30, 400, n).round(2),
        "forma_pagamento":   random.choices(FORMAS_PAGAMENTO, weights=[35, 30, 20, 10, 5], k=n),
    })

    n_conveniencia = int(n * 0.4)
    fato_conveniencia = pd.DataFrame({
        "id_venda":          new_ids(n_conveniencia),
        "id_data":           rand_dates(start, end, n_conveniencia),
        "id_posto":          random.choices(dim_posto["id_posto"].tolist(), k=n_conveniencia),
        "categoria_produto": random.choices(CATEGORIAS_CONVENIENCIA, k=n_conveniencia),
        "valor":             rng.uniform(3.5, 89.9, n_conveniencia).round(2),
    })

    return {
        "DimPosto": dim_posto,
        "DimCombustivel": dim_combustivel,
        "FatoAbastecimento": fato_abastecimento,
        "FatoVendaConveniencia": fato_conveniencia,
        "dCalendario": dcalendario(start, end),
    }
