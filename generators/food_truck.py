"""generators/food_truck.py — Setor Food Truck."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_COZINHA       = ["Hambúrguer", "Comida Mexicana", "Comida Japonesa", "Vegana",
                        "Doces & Sobremesas", "Comida Nordestina", "Pizza", "Espetinhos"]
CATEGORIAS_ITEM     = ["Prato Principal", "Bebida", "Sobremesa", "Combo", "Porção"]
LOCAIS_VENDA        = ["Rua Fixa", "Praça de Eventos", "Feira Gastronômica",
                        "Evento Corporativo (Catering)", "Parque"]
FORMAS_PAGAMENTO     = ["Pix", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"]
TIPOS_EVENTO        = ["Feira Gastronômica", "Festival de Música", "Evento Corporativo", "Feira Livre"]


def gerar_food_truck(n, start, end):
    n = max(int(n), 1)

    n_truck = min(max(n // 150, 5), 60)
    dim_truck = pd.DataFrame({
        "id_truck":          new_ids(n_truck),
        "nome_truck":        [f"Truck {fake.first_name()}" for _ in range(n_truck)],
        "tipo_cozinha":      random.choices(TIPOS_COZINHA, k=n_truck),
        "cidade_base":       [fake.city() for _ in range(n_truck)],
    })

    n_item = min(max(n // 30, 15), 200)
    dim_cardapio = pd.DataFrame({
        "id_item":           new_ids(n_item),
        "nome_item":         [f"{fake.word().capitalize()} {c}" for c in random.choices(CATEGORIAS_ITEM, k=n_item)],
        "categoria":         random.choices(CATEGORIAS_ITEM, k=n_item),
        "preco":             rng.uniform(6.9, 59.9, n_item).round(2),
    })

    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_truck":          random.choices(dim_truck["id_truck"].tolist(), k=n),
        "id_item":           random.choices(dim_cardapio["id_item"].tolist(), k=n),
        "local_venda":       random.choices(LOCAIS_VENDA, weights=[35, 25, 20, 15, 5], k=n),
        "quantidade":        rng.integers(1, 5, n),
        "valor_total":       rng.uniform(6.9, 179.9, n).round(2),
        "forma_pagamento":   random.choices(FORMAS_PAGAMENTO, weights=[50, 25, 15, 10], k=n),
    })

    n_evento = min(max(n_truck * 10, 30), 3000)
    fato_evento = pd.DataFrame({
        "id_evento":         new_ids(n_evento),
        "id_data":           rand_dates(start, end, n_evento),
        "id_truck":          random.choices(dim_truck["id_truck"].tolist(), k=n_evento),
        "tipo_evento":       random.choices(TIPOS_EVENTO, k=n_evento),
        "taxa_participacao": rng.uniform(100, 1200, n_evento).round(2),
        "faturamento_evento": rng.uniform(500, 12000, n_evento).round(2),
    })

    return {
        "DimTruck": dim_truck,
        "DimCardapio": dim_cardapio,
        "FatoVenda": fato_venda,
        "FatoEvento": fato_evento,
        "dCalendario": dcalendario(start, end),
    }
