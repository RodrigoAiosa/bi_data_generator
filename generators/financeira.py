"""generators/financeira.py — Setor Financeira & Crédito Pessoal."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

TIPOS_CREDITO = ["Consignado", "Pessoal", "Cheque Especial", "Financiamento de Veículo"]


def gerar_financeira(n, start, end):
    n = max(int(n), 1)

    n_agencia = min(max(n // 200, 4), 60)
    dim_agencia = pd.DataFrame({
        "id_agencia":        new_ids(n_agencia),
        "cidade":            fake_pool(fake, "city", n_agencia),
        "uf":                fake_pool(fake, "state_abbr", n_agencia),
    })

    n_cliente = min(max(n // 4, 200), 20000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              fake_pool(fake, "name", n_cliente),
        "score_credito":     rng.integers(300, 1000, n_cliente),
    })

    fato_contrato = pd.DataFrame({
        "id_contrato":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_agencia":        random.choices(dim_agencia["id_agencia"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "tipo_credito":      random.choices(TIPOS_CREDITO, weights=[40, 30, 15, 15], k=n),
        "valor_contratado":  rng.uniform(500, 80000, n).round(2),
        "taxa_juros_mes":    rng.uniform(1.2, 12, n).round(2),
        "num_parcelas":      random.choices([6, 12, 18, 24, 36, 48], k=n),
    })

    n_parcela = n * 4
    fato_parcela = pd.DataFrame({
        "id_parcela":        new_ids(n_parcela),
        "id_data":           rand_dates(start, end, n_parcela),
        "id_contrato":       random.choices(fato_contrato["id_contrato"].tolist(), k=n_parcela),
        "valor_parcela":     rng.uniform(50, 4000, n_parcela).round(2),
        "status_pagamento":  random.choices(["Pago", "Em Aberto", "Inadimplente"], weights=[75, 15, 10], k=n_parcela),
    })

    return {
        "DimAgencia": dim_agencia,
        "DimCliente": dim_cliente,
        "FatoContrato": fato_contrato,
        "FatoParcela": fato_parcela,
        "dCalendario": dcalendario(start, end),
    }
