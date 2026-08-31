"""generators/lavanderia.py — Setor Lavanderia."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_UNIDADE      = ["Industrial", "Self-Service", "Loja de Bairro"]
SEGMENTOS_CLIENTE  = ["Hotel", "Hospital", "Academia", "Pessoa Física", "Restaurante"]
TIPOS_SERVICO      = ["Lavagem Simples", "Lavagem e Passadoria", "Tinturaria", "Lavagem a Seco"]
TIPOS_OCORRENCIA   = ["Peça Danificada", "Atraso", "Extravio", "Reclamação de Qualidade"]
STATUS_RESOLUCAO    = ["Resolvida", "Em Análise", "Reembolsada", "Sem Resolução"]


def gerar_lavanderia(n, start, end):
    n = max(int(n), 1)

    n_unidade = min(max(n // 150, 5), 60)
    dim_unidade = pd.DataFrame({
        "id_unidade":        new_ids(n_unidade),
        "nome_unidade":      [f"Lavanderia {fake.first_name()}" for _ in range(n_unidade)],
        "cidade":            [fake.city() for _ in range(n_unidade)],
        "tipo":              random.choices(TIPOS_UNIDADE, weights=[25, 40, 35], k=n_unidade),
    })

    n_cliente = min(max(n // 8, 100), 6000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome_cliente":      [fake.name() if random.random() < 0.6 else fake.company() for _ in range(n_cliente)],
        "segmento":          random.choices(SEGMENTOS_CLIENTE, weights=[10, 8, 7, 65, 10], k=n_cliente),
    })

    fato_pedido = pd.DataFrame({
        "id_pedido":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "peso_kg":           rng.uniform(1, 40, n).round(1),
        "tipo_servico":      random.choices(TIPOS_SERVICO, weights=[45, 30, 15, 10], k=n),
        "valor":             rng.uniform(15, 450, n).round(2),
        "prazo_cumprido":    random.choices([True, False], weights=[88, 12], k=n),
    })

    n_ocorrencia = int(n * 0.06)
    fato_ocorrencia = pd.DataFrame({
        "id_ocorrencia":     new_ids(n_ocorrencia),
        "id_data":           rand_dates(start, end, n_ocorrencia),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n_ocorrencia),
        "tipo_ocorrencia":   random.choices(TIPOS_OCORRENCIA, k=n_ocorrencia),
        "status_resolucao":  random.choices(STATUS_RESOLUCAO, weights=[55, 20, 15, 10], k=n_ocorrencia),
    })

    return {
        "DimUnidade": dim_unidade,
        "DimClienteB2B": dim_cliente,
        "FatoPedido": fato_pedido,
        "FatoOcorrencia": fato_ocorrencia,
        "dCalendario": dcalendario(start, end),
    }
