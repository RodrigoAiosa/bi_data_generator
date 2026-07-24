"""generators/joalheria.py — Setor Joalheria & Relojoaria."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS = ["Anel", "Colar", "Brinco", "Pulseira", "Relógio", "Aliança"]
MATERIAIS = ["Ouro 18k", "Prata 925", "Aço Inoxidável", "Platina", "Ouro Rosé"]
TIPOS_CLIENTE = ["Varejo", "Atacado"]
FORMAS_PAGAMENTO = ["À Vista", "Cartão de Crédito Parcelado", "Pix", "Crediário Próprio"]
TIPOS_SERVICO = ["Conserto", "Troca de Bateria", "Polimento", "Ajuste de Tamanho", "Gravação Personalizada"]


def gerar_joalheria(n, start, end):
    n = max(int(n), 1)

    n_produto = min(max(n // 20, 30), 2000)
    dim_produto = pd.DataFrame({
        "id_produto":        new_ids(n_produto),
        "nome":              [f"{random.choice(CATEGORIAS)} {random.choice(MATERIAIS)}" for _ in range(n_produto)],
        "categoria":         random.choices(CATEGORIAS, k=n_produto),
        "material":          random.choices(MATERIAIS, k=n_produto),
        "preco":             rng.uniform(80, 45000, n_produto).round(2),
    })

    n_cliente = min(max(n // 6, 100), 8000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.name() for _ in range(n_cliente)],
        "uf":                [fake.state_abbr() for _ in range(n_cliente)],
        "tipo_cliente":      random.choices(TIPOS_CLIENTE, weights=[85, 15], k=n_cliente),
    })

    qtd = rng.integers(1, 3, n)
    produto_idx = random.choices(range(n_produto), k=n)
    preco_unit = dim_produto["preco"].to_numpy()[produto_idx]
    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_produto":        dim_produto["id_produto"].to_numpy()[produto_idx],
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "quantidade":        qtd,
        "valor_total":       (qtd * preco_unit).round(2),
        "forma_pagamento":   random.choices(FORMAS_PAGAMENTO, weights=[25, 40, 25, 10], k=n),
    })

    n_assist = int(n * 0.25)
    fato_assistencia = pd.DataFrame({
        "id_assistencia":    new_ids(n_assist),
        "id_data":           rand_dates(start, end, n_assist),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n_assist),
        "tipo_servico":      random.choices(TIPOS_SERVICO, k=n_assist),
        "valor_servico":     rng.uniform(15, 800, n_assist).round(2),
    })

    return {
        "DimProduto": dim_produto,
        "DimCliente": dim_cliente,
        "FatoVenda": fato_venda,
        "FatoAssistencia": fato_assistencia,
        "dCalendario": dcalendario(start, end),
    }
