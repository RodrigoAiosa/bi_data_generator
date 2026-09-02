"""generators/barbearia.py — Setor Barbearia."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

SERVICOS         = ["Corte", "Barba", "Corte + Barba", "Sobrancelha", "Coloração", "Corte Infantil"]
FORMAS_PAGAMENTO = ["Pix", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"]
PLANOS_CLUBE     = ["Mensal Básico", "Mensal Premium", "Trimestral"]
STATUS_ASSINATURA = ["Ativa", "Cancelada", "Suspensa"]


def gerar_barbearia(n, start, end):
    n = max(int(n), 1)

    n_unidade = min(max(n // 200, 3), 50)
    dim_unidade = pd.DataFrame({
        "id_unidade":        new_ids(n_unidade),
        "cidade":            fake_pool(fake, "city", n_unidade),
        "bairro":            fake_pool(fake, "neighborhood", n_unidade),
    })

    n_barbeiro = min(max(n // 30, 8), 400)
    dim_barbeiro = pd.DataFrame({
        "id_barbeiro":       new_ids(n_barbeiro),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n_barbeiro),
        "nome":              fake_pool(fake, "name_male", n_barbeiro),
        "anos_experiencia":  rng.integers(1, 25, n_barbeiro),
        "avaliacao":         rng.uniform(3.5, 5.0, n_barbeiro).round(1),
    })

    fato_atendimento = pd.DataFrame({
        "id_atendimento":    new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_barbeiro":       random.choices(dim_barbeiro["id_barbeiro"].tolist(), k=n),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n),
        "servico":           random.choices(SERVICOS, weights=[30, 15, 30, 10, 5, 10], k=n),
        "valor":             rng.uniform(25, 150, n).round(2),
        "forma_pagamento":   random.choices(FORMAS_PAGAMENTO, weights=[45, 30, 15, 10], k=n),
        "avaliacao_cliente": rng.integers(1, 5, n),
    })

    n_assinatura = min(max(n // 8, 100), 8000)
    fato_assinatura = pd.DataFrame({
        "id_assinatura":     new_ids(n_assinatura),
        "id_data":           rand_dates(start, end, n_assinatura),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n_assinatura),
        "plano":             random.choices(PLANOS_CLUBE, weights=[50, 30, 20], k=n_assinatura),
        "valor_mensal":      rng.uniform(69, 249, n_assinatura).round(2),
        "status":            random.choices(STATUS_ASSINATURA, weights=[75, 18, 7], k=n_assinatura),
    })

    return {
        "DimUnidade": dim_unidade,
        "DimBarbeiro": dim_barbeiro,
        "FatoAtendimento": fato_atendimento,
        "FatoAssinatura": fato_assinatura,
        "dCalendario": dcalendario(start, end),
    }
