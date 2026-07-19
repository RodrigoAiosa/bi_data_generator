"""generators/restaurante.py — Setor Restaurantes & Food Service."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS_PRATO = ["Entrada", "Prato Principal", "Sobremesa", "Bebida", "Petisco", "Combo"]
TIPOS_UNIDADE    = ["Salão", "Food Truck", "Delivery Only", "Fast-Food", "Praça de Alimentação"]
CANAIS           = ["Salão", "Delivery App", "Delivery Próprio", "Retirada", "Drive-Thru"]
STATUS_RESERVA   = ["Confirmada", "Cancelada", "Compareceu", "No-Show"]


def gerar_restaurante(n, start, end):
    n = max(int(n), 1)

    n_prato = min(max(n // 15, 20), 400)
    custo = rng.uniform(3, 60, n_prato).round(2)
    fator_markup = rng.uniform(1.8, 4.0, n_prato)
    dim_prato = pd.DataFrame({
        "id_prato":          new_ids(n_prato),
        "nome":              [f"{fake.word().capitalize()} {random.choice(['ao Molho','Grelhado','na Chapa','Especial','da Casa'])}" for _ in range(n_prato)],
        "categoria":         random.choices(CATEGORIAS_PRATO, k=n_prato),
        "custo":             custo,
        "preco_venda":       (custo * fator_markup).round(2),
        "vegetariano":       random.choices([True, False], weights=[25, 75], k=n_prato),
        "tempo_preparo_min": rng.integers(5, 60, n_prato),
        "ativo":             random.choices([True, False], weights=[90, 10], k=n_prato),
    })

    n_unidade = min(max(n // 400, 3), 60)
    dim_unidade = pd.DataFrame({
        "id_unidade":        new_ids(n_unidade),
        "nome":              [f"Unidade {fake.city()}" for _ in range(n_unidade)],
        "tipo":              random.choices(TIPOS_UNIDADE, k=n_unidade),
        "uf":                [fake.state_abbr() for _ in range(n_unidade)],
        "cidade":            [fake.city() for _ in range(n_unidade)],
        "capacidade_mesas":  rng.integers(0, 60, n_unidade),
        "avaliacao":         rng.uniform(3.0, 5.0, n_unidade).round(1),
    })

    qtd = rng.integers(1, 6, n)
    prato_idx = random.choices(range(n_prato), k=n)
    preco_unit = dim_prato["preco_venda"].to_numpy()[prato_idx]
    fato_pedido = pd.DataFrame({
        "id_pedido":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_prato":          dim_prato["id_prato"].to_numpy()[prato_idx],
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n),
        "canal":             random.choices(CANAIS, weights=[35, 30, 15, 15, 5], k=n),
        "quantidade":        qtd,
        "preco_unitario":    preco_unit.round(2),
        "valor_total":       (qtd * preco_unit).round(2),
        "gorjeta":           rng.uniform(0, 25, n).round(2),
        "avaliacao_pedido":  rng.integers(1, 6, n),
        "tempo_entrega_min": [rng.integers(15, 90) if random.random() < 0.5 else None for _ in range(n)],
    })

    n_res = int(n_unidade * 300)
    status_res = random.choices(STATUS_RESERVA, weights=[35, 10, 45, 10], k=n_res)
    fato_reserva = pd.DataFrame({
        "id_reserva":        new_ids(n_res),
        "id_data":           rand_dates(start, end, n_res),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n_res),
        "numero_pessoas":    rng.integers(1, 12, n_res),
        "horario":           random.choices(["Almoço", "Jantar", "Brunch"], weights=[45, 45, 10], k=n_res),
        "status":            status_res,
        "no_show":           [s == "No-Show" for s in status_res],
    })

    return {
        "DimPrato": dim_prato,
        "DimUnidade": dim_unidade,
        "FatoPedido": fato_pedido,
        "FatoReserva": fato_reserva,
        "dCalendario": dcalendario(start, end),
    }
