"""generators/delivery.py — Setor Delivery de Comida."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

CATEGORIAS_REST = ["Lanches", "Pizza", "Comida Japonesa", "Comida Brasileira", "Doces & Sobremesas", "Saudável", "Açaí"]
FORMAS_PAGAMENTO = ["Cartão de Crédito", "Cartão de Débito", "Pix", "Dinheiro", "Vale-Refeição"]
STATUS_PEDIDO = ["Entregue", "Cancelado", "Em Rota", "Preparando"]
VEICULOS = ["Moto", "Bicicleta", "Carro"]


def gerar_delivery(n, start, end):
    n = max(int(n), 1)

    n_rest = min(max(n // 40, 20), 3000)
    dim_restaurante = pd.DataFrame({
        "id_restaurante":    new_ids(n_rest),
        "nome":              fake_pool(fake, "company", n_rest),
        "categoria":         random.choices(CATEGORIAS_REST, k=n_rest),
        "avaliacao":         rng.uniform(3.0, 5.0, n_rest).round(1),
    })

    n_entregador = min(max(n // 25, 15), 4000)
    dim_entregador = pd.DataFrame({
        "id_entregador":     new_ids(n_entregador),
        "nome":              fake_pool(fake, "name", n_entregador),
        "veiculo":           random.choices(VEICULOS, weights=[70, 25, 5], k=n_entregador),
        "avaliacao":         rng.uniform(3.5, 5.0, n_entregador).round(1),
    })

    fato_pedido = pd.DataFrame({
        "id_pedido":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_restaurante":    random.choices(dim_restaurante["id_restaurante"].tolist(), k=n),
        "id_entregador":     random.choices(dim_entregador["id_entregador"].tolist(), k=n),
        "valor":             rng.uniform(18, 220, n).round(2),
        "tempo_entrega_min": rng.integers(12, 90, n),
        "avaliacao":         rng.integers(1, 6, n),
        "forma_pagamento":   random.choices(FORMAS_PAGAMENTO, weights=[35, 20, 30, 5, 10], k=n),
        "status":            random.choices(STATUS_PEDIDO, weights=[80, 8, 7, 5], k=n),
    })

    n_pag = int(n_entregador * 8)
    fato_pagamento_entregador = pd.DataFrame({
        "id_pagamento":      new_ids(n_pag),
        "id_data":           rand_dates(start, end, n_pag),
        "id_entregador":     random.choices(dim_entregador["id_entregador"].tolist(), k=n_pag),
        "valor_repasse":     rng.uniform(5, 35, n_pag).round(2),
        "gorjeta":           rng.uniform(0, 15, n_pag).round(2),
    })

    return {
        "DimRestaurante": dim_restaurante,
        "DimEntregador": dim_entregador,
        "FatoPedido": fato_pedido,
        "FatoPagamentoEntregador": fato_pagamento_entregador,
        "dCalendario": dcalendario(start, end),
    }
