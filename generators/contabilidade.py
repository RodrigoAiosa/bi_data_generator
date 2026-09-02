"""generators/contabilidade.py — Setor Contabilidade."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

REGIMES = ["Simples Nacional", "Lucro Presumido", "Lucro Real", "MEI"]
TIPOS_SERVICO = ["Fechamento Contábil", "Folha de Pagamento", "Imposto de Renda",
                  "Abertura de Empresa", "Consultoria Tributária", "Escrituração Fiscal"]
SETORES_CLIENTE = ["Comércio", "Serviços", "Indústria", "Agronegócio", "Tecnologia"]
STATUS_PAGAMENTO = ["Pago", "Pendente", "Atrasado"]
ESPECIALIDADES = ["Tributário", "Trabalhista", "Societário", "Financeiro", "Contábil Geral"]


def gerar_contabilidade(n, start, end):
    n = max(int(n), 1)

    n_contador = min(max(n // 80, 5), 60)
    dim_contador = pd.DataFrame({
        "id_contador":       new_ids(n_contador),
        "nome":              fake_pool(fake, "name", n_contador),
        "especialidade":     random.choices(ESPECIALIDADES, k=n_contador),
        "anos_experiencia":  rng.integers(1, 30, n_contador),
    })

    n_cliente = min(max(n // 8, 40), 3000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "razao_social":      fake_pool(fake, "company", n_cliente),
        "regime_tributario": random.choices(REGIMES, weights=[55, 25, 10, 10], k=n_cliente),
        "setor_atividade":   random.choices(SETORES_CLIENTE, k=n_cliente),
        "ativo":             random.choices([True, False], weights=[88, 12], k=n_cliente),
    })

    fato_servico = pd.DataFrame({
        "id_servico":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_contador":       random.choices(dim_contador["id_contador"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "tipo_servico":      random.choices(TIPOS_SERVICO, weights=[30, 25, 15, 5, 10, 15], k=n),
        "prazo_cumprido":    random.choices([True, False], weights=[90, 10], k=n),
    })

    n_hon = int(n_cliente * 3.5)
    fato_honorario = pd.DataFrame({
        "id_honorario":      new_ids(n_hon),
        "id_data":           rand_dates(start, end, n_hon),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n_hon),
        "valor":             rng.uniform(150, 4500, n_hon).round(2),
        "status_pagamento":  random.choices(STATUS_PAGAMENTO, weights=[80, 14, 6], k=n_hon),
    })

    return {
        "DimContador": dim_contador,
        "DimCliente": dim_cliente,
        "FatoServico": fato_servico,
        "FatoHonorario": fato_honorario,
        "dCalendario": dcalendario(start, end),
    }
