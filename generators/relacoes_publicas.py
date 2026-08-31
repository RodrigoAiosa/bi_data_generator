"""generators/relacoes_publicas.py — Setor Relações Públicas."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_VEICULO    = ["Jornal", "TV", "Rádio", "Portal de Notícias", "Influenciador Digital", "Revista"]
TIPOS_CONTRATO   = ["Mensal (Fee Fixo)", "Por Projeto", "Por Evento"]
SENTIMENTOS      = ["Positivo", "Neutro", "Negativo"]


def gerar_relacoes_publicas(n, start, end):
    n = max(int(n), 1)

    n_cliente = min(max(n // 60, 15), 800)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.company() for _ in range(n_cliente)],
        "segmento":          random.choices(["Varejo", "Tecnologia", "Alimentício", "Financeiro", "Saúde", "Governo"], k=n_cliente),
    })

    n_veiculo = min(max(n // 30, 30), 1500)
    dim_veiculo = pd.DataFrame({
        "id_veiculo":        new_ids(n_veiculo),
        "nome":              [f"{fake.last_name()} {random.choice(['News', 'Notícias', 'Digital', 'Press'])}" for _ in range(n_veiculo)],
        "tipo":              random.choices(TIPOS_VEICULO, weights=[20, 10, 10, 30, 25, 5], k=n_veiculo),
        "alcance_medio":     rng.integers(1000, 5000000, n_veiculo),
    })

    n_assessoria = int(n * 0.35)
    fato_assessoria = pd.DataFrame({
        "id_assessoria":     new_ids(n_assessoria),
        "id_data":           rand_dates(start, end, n_assessoria),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n_assessoria),
        "tipo_contrato":     random.choices(TIPOS_CONTRATO, weights=[60, 30, 10], k=n_assessoria),
        "valor":             rng.uniform(3000, 90000, n_assessoria).round(2),
    })

    sentimento = random.choices(SENTIMENTOS, weights=[45, 40, 15], k=n)
    fato_clipping = pd.DataFrame({
        "id_clipping":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "id_veiculo":        random.choices(dim_veiculo["id_veiculo"].tolist(), k=n),
        "sentimento":        sentimento,
        "alcance_estimado":  rng.integers(500, 4000000, n),
        "valor_midiatico_estimado": rng.uniform(200, 120000, n).round(2),
    })

    return {
        "DimCliente": dim_cliente,
        "DimVeiculo": dim_veiculo,
        "FatoAssessoria": fato_assessoria,
        "FatoClipping": fato_clipping,
        "dCalendario": dcalendario(start, end),
    }
