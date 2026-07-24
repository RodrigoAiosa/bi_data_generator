"""generators/marcenaria.py — Setor Marcenaria & Móveis Planejados."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_AMBIENTE = ["Cozinha", "Quarto", "Sala", "Escritório", "Closet", "Banheiro", "Área Externa"]
MATERIAIS = ["MDF", "MDP", "Madeira Maciça", "Compensado"]
TIPOS_CLIENTE = ["Residencial", "Comercial"]
STATUS_CONTRATO = ["Em Projeto", "Em Produção", "Em Instalação", "Concluído", "Cancelado"]


def gerar_marcenaria(n, start, end):
    n = max(int(n), 1)

    n_projeto = min(max(n // 8, 60), 3000)
    dim_projeto = pd.DataFrame({
        "id_projeto":        new_ids(n_projeto),
        "tipo_ambiente":     random.choices(TIPOS_AMBIENTE, k=n_projeto),
        "material":          random.choices(MATERIAIS, weights=[50, 30, 15, 5], k=n_projeto),
        "metragem_m2":       rng.uniform(2, 45, n_projeto).round(1),
    })

    n_cliente = min(max(n // 6, 100), 8000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.name() if random.random() < 0.75 else fake.company() for _ in range(n_cliente)],
        "uf":                [fake.state_abbr() for _ in range(n_cliente)],
        "tipo_cliente":      random.choices(TIPOS_CLIENTE, weights=[75, 25], k=n_cliente),
    })

    fato_contrato = pd.DataFrame({
        "id_contrato":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_projeto":        random.choices(dim_projeto["id_projeto"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "valor_contrato":    rng.uniform(1500, 120000, n).round(2),
        "prazo_entrega_dias": rng.integers(15, 120, n),
        "status":            random.choices(STATUS_CONTRATO, weights=[15, 25, 20, 35, 5], k=n),
    })

    n_producao = int(n * 0.9)
    fato_producao = pd.DataFrame({
        "id_producao":       new_ids(n_producao),
        "id_data":           rand_dates(start, end, n_producao),
        "id_projeto":        random.choices(dim_projeto["id_projeto"].tolist(), k=n_producao),
        "horas_producao":    rng.uniform(4, 200, n_producao).round(1),
        "custo_material":    rng.uniform(300, 40000, n_producao).round(2),
        "retrabalho":        random.choices([True, False], weights=[10, 90], k=n_producao),
    })

    return {
        "DimProjeto": dim_projeto,
        "DimCliente": dim_cliente,
        "FatoContrato": fato_contrato,
        "FatoProducao": fato_producao,
        "dCalendario": dcalendario(start, end),
    }
