"""generators/funeraria.py — Setor Funerária & Serviços Funerários."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

SERVICOS = ["Sepultamento", "Cremação", "Translado", "Jazigo Perpétuo", "Plano Funerário Preventivo",
             "Ornamentação", "Velório Completo", "Exumação"]
CATEGORIAS_SERVICO = ["Básico", "Intermediário", "Premium"]
TIPOS_CONTRATACAO = ["Imediato", "Plano Preventivo"]
FORMAS_PAGAMENTO = ["À Vista", "Cartão de Crédito", "Financiado Seguradora", "Boleto Parcelado"]
STATUS_PLANO = ["Ativo", "Cancelado", "Inadimplente", "Utilizado"]


def gerar_funeraria(n, start, end):
    n = max(int(n), 1)

    n_servico = min(max(n // 100, 8), 60)
    dim_servico = pd.DataFrame({
        "id_servico":        new_ids(n_servico),
        "nome":              random.choices(SERVICOS, k=n_servico),
        "categoria":         random.choices(CATEGORIAS_SERVICO, weights=[45, 35, 20], k=n_servico),
        "valor_base":        rng.uniform(800, 25000, n_servico).round(2),
    })

    n_cliente = min(max(n // 3, 150), 12000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.name() for _ in range(n_cliente)],
        "uf":                [fake.state_abbr() for _ in range(n_cliente)],
        "cidade":            [fake.city() for _ in range(n_cliente)],
        "tipo_contratacao":  random.choices(TIPOS_CONTRATACAO, weights=[55, 45], k=n_cliente),
    })

    valor_servico = rng.uniform(800, 30000, n).round(2)
    fato_atendimento = pd.DataFrame({
        "id_atendimento":    new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_servico":        random.choices(dim_servico["id_servico"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "forma_pagamento":   random.choices(FORMAS_PAGAMENTO, weights=[30, 25, 25, 20], k=n),
        "valor_total":       valor_servico,
        "urgente":           random.choices([True, False], weights=[60, 40], k=n),
        "seguradora_envolvida": random.choices([True, False], weights=[35, 65], k=n),
    })

    n_plano = int(n_cliente * 0.4)
    status_plano = random.choices(STATUS_PLANO, weights=[60, 10, 15, 15], k=n_plano)
    fato_plano = pd.DataFrame({
        "id_plano_fato":     new_ids(n_plano),
        "id_data":           rand_dates(start, end, n_plano),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n_plano),
        "mensalidade":       rng.uniform(35, 350, n_plano).round(2),
        "dependentes_inclusos": rng.integers(0, 6, n_plano),
        "status":            status_plano,
        "meses_contratado":  rng.integers(1, 120, n_plano),
        "inadimplente":      [s == "Inadimplente" for s in status_plano],
    })

    return {
        "DimServico": dim_servico,
        "DimCliente": dim_cliente,
        "FatoAtendimento": fato_atendimento,
        "FatoPlano": fato_plano,
        "dCalendario": dcalendario(start, end),
    }
