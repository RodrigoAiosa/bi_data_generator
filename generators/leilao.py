"""generators/leilao.py — Setor Leilão."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS_LOTE = ["Veículo", "Imóvel", "Arte", "Joia", "Maquinário Industrial", "Antiguidade", "Eletrônico"]
CONDICOES = ["Novo", "Usado - Bom Estado", "Usado - Sucata/Avariado", "Recondicionado"]
TIPOS_PESSOA = ["Pessoa Física", "Pessoa Jurídica"]
STATUS_PAGAMENTO = ["Pago", "Pendente", "Inadimplente"]


def gerar_leilao(n, start, end):
    n = max(int(n), 1)

    n_lote = min(max(n // 8, 60), 4000)
    dim_lote = pd.DataFrame({
        "id_lote":           new_ids(n_lote),
        "categoria":         random.choices(CATEGORIAS_LOTE, weights=[35, 15, 10, 10, 15, 10, 5], k=n_lote),
        "valor_avaliacao":   rng.uniform(500, 500000, n_lote).round(2),
        "condicao":          random.choices(CONDICOES, weights=[10, 45, 30, 15], k=n_lote),
    })

    n_arrematante = min(max(n // 5, 150), 12000)
    dim_arrematante = pd.DataFrame({
        "id_arrematante":    new_ids(n_arrematante),
        "nome":              [fake.name() if random.random() < 0.75 else fake.company() for _ in range(n_arrematante)],
        "tipo_pessoa":       random.choices(TIPOS_PESSOA, weights=[75, 25], k=n_arrematante),
        "uf":                [fake.state_abbr() for _ in range(n_arrematante)],
    })

    lote_idx = random.choices(range(n_lote), k=n)
    valor_avaliacao = dim_lote["valor_avaliacao"].to_numpy()[lote_idx]
    fato_lance = pd.DataFrame({
        "id_lance":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_lote":           dim_lote["id_lote"].to_numpy()[lote_idx],
        "id_arrematante":    random.choices(dim_arrematante["id_arrematante"].tolist(), k=n),
        "valor_lance":       (valor_avaliacao * rng.uniform(0.3, 1.3, n)).round(2),
        "vencedor":          random.choices([True, False], weights=[15, 85], k=n),
    })

    n_arrematacao = int(n_lote * 0.85)
    status_pagamento = random.choices(STATUS_PAGAMENTO, weights=[75, 15, 10], k=n_arrematacao)
    valor_final = dim_lote["valor_avaliacao"].to_numpy()[:n_arrematacao] * rng.uniform(0.4, 1.4, n_arrematacao)
    fato_arrematacao = pd.DataFrame({
        "id_arrematacao":    new_ids(n_arrematacao),
        "id_data":           rand_dates(start, end, n_arrematacao),
        "id_lote":           dim_lote["id_lote"].tolist()[:n_arrematacao],
        "id_arrematante":    random.choices(dim_arrematante["id_arrematante"].tolist(), k=n_arrematacao),
        "valor_final":       valor_final.round(2),
        "comissao_leiloeiro": (valor_final * rng.uniform(0.03, 0.08, n_arrematacao)).round(2),
        "status_pagamento":  status_pagamento,
    })

    return {
        "DimLote": dim_lote,
        "DimArrematante": dim_arrematante,
        "FatoLance": fato_lance,
        "FatoArrematacao": fato_arrematacao,
        "dCalendario": dcalendario(start, end),
    }
