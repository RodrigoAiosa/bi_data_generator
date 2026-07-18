"""generators/tecnologia.py — Setor Tecnologia / SaaS."""

import random
from datetime import date

import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

PLANOS = ["Starter", "Basic", "Pro", "Business", "Enterprise"]


def gerar_tecnologia(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_clientes = min(n, 2000)
    n_produtos = 30
    n_agentes  = 60

    dim_produto = pd.DataFrame({
        "id_produto": new_ids(n_produtos),
        "nome":       [f"{fake.word().capitalize()} {p}" for p in random.choices(PLANOS, k=n_produtos)],
        "categoria":  random.choices(["SaaS","Licença","Suporte","Consultoria","Infraestrutura"], k=n_produtos),
        "plano":      random.choices(PLANOS, k=n_produtos),
        "mrr":        rng.uniform(99, 9999, n_produtos).round(2),
    })

    dim_cliente = pd.DataFrame({
        "id_cliente": new_ids(n_clientes),
        "empresa":    [fake.company() for _ in range(n_clientes)],
        "cnpj":       [fake.cnpj()   for _ in range(n_clientes)],
        "setor":      random.choices(["Varejo","Indústria","Serviços","Saúde","Financeiro"], k=n_clientes),
        "tamanho":    random.choices(["MEI","ME","EPP","Médio","Grande"], k=n_clientes),
        "uf":         random.choices(["SP","RJ","MG","RS","PR"], k=n_clientes),
    })

    dim_agente = pd.DataFrame({
        "id_agente": new_ids(n_agentes),
        "nome":      [fake.name() for _ in range(n_agentes)],
        "area":      random.choices(["Comercial","CS","Suporte N1","Suporte N2","Implantação"], k=n_agentes),
        "nivel":     random.choices(["Jr","Pl","Sr"], k=n_agentes),
    })

    fato = pd.DataFrame({
        "id_contrato": new_ids(n),
        "id_data":     rand_dates(start, end, n),
        "id_cliente":  random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "id_produto":  random.choices(dim_produto["id_produto"].tolist(), k=n),
        "id_agente":   random.choices(dim_agente["id_agente"].tolist(), k=n),
        "tipo":        random.choices(["Novo","Renovação","Upgrade","Downgrade","Churn"], k=n),
        "valor_mrr":   rng.uniform(99, 9999, n).round(2),
        "arr":         rng.uniform(1188, 119988, n).round(2),
        "nps":         rng.integers(0, 11, n),
        "status":      random.choices(["Ativo","Cancelado","Trial","Suspenso"], weights=[70,15,10,5], k=n),
    })

    return {
        "DimProduto":   dim_produto,
        "DimCliente":   dim_cliente,
        "DimAgente":    dim_agente,
        "FatoContrato": fato,
        "dCalendario":  dcalendario(start, end),
    }
