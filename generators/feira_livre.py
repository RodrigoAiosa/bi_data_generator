"""generators/feira_livre.py — Setor Feira Livre & Mercado Municipal."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

CATEGORIAS_FEIRANTE = ["Hortifruti", "Carnes", "Peixes", "Artesanato", "Roupas", "Comidas Prontas", "Flores"]
FEIRAS               = ["Feira Central", "Feira do Bairro Norte", "Feira Orgânica", "Feira Noturna", "Feira do Produtor"]
FORMAS_PAGAMENTO     = ["Dinheiro", "Pix", "Cartão de Débito", "Cartão de Crédito"]
STATUS_PAGAMENTO_OCUPACAO = ["Pago", "Pendente", "Isento"]


def gerar_feira_livre(n, start, end):
    n = max(int(n), 1)

    n_feirante = min(max(n // 40, 20), 800)
    dim_feirante = pd.DataFrame({
        "id_feirante":       new_ids(n_feirante),
        "nome":              fake_pool(fake, "name", n_feirante),
        "categoria":         random.choices(CATEGORIAS_FEIRANTE, k=n_feirante),
        "anos_atuacao":      rng.integers(1, 35, n_feirante),
    })

    n_banca = min(max(n // 30, 25), 1000)
    dim_banca = pd.DataFrame({
        "id_banca":          new_ids(n_banca),
        "numero_banca":      rng.integers(1, 300, n_banca),
        "feira":             random.choices(FEIRAS, k=n_banca),
        "tamanho_m2":        rng.uniform(2, 20, n_banca).round(1),
    })

    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_feirante":       random.choices(dim_feirante["id_feirante"].tolist(), k=n),
        "id_banca":          random.choices(dim_banca["id_banca"].tolist(), k=n),
        "valor":             rng.uniform(5, 300, n).round(2),
        "quantidade_itens":  rng.integers(1, 20, n),
        "forma_pagamento":   random.choices(FORMAS_PAGAMENTO, weights=[55, 30, 10, 5], k=n),
    })

    n_ocupacao = min(max(n // 5, 50), 20000)
    fato_ocupacao = pd.DataFrame({
        "id_ocupacao":       new_ids(n_ocupacao),
        "id_data":           rand_dates(start, end, n_ocupacao),
        "id_feirante":       random.choices(dim_feirante["id_feirante"].tolist(), k=n_ocupacao),
        "id_banca":          random.choices(dim_banca["id_banca"].tolist(), k=n_ocupacao),
        "taxa_paga":         rng.uniform(15, 120, n_ocupacao).round(2),
        "status_pagamento":  random.choices(STATUS_PAGAMENTO_OCUPACAO, weights=[80, 15, 5], k=n_ocupacao),
    })

    return {
        "DimFeirante": dim_feirante,
        "DimBanca": dim_banca,
        "FatoVenda": fato_venda,
        "FatoOcupacao": fato_ocupacao,
        "dCalendario": dcalendario(start, end),
    }
