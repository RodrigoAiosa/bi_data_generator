"""generators/auditoria.py — Setor Auditoria & Compliance."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_AUDITORIA = ["Financeira", "Fiscal", "Trabalhista", "Compliance/LGPD", "Operacional", "ESG"]
NIVEL_RISCO     = ["Baixo", "Médio", "Alto", "Crítico"]
SEVERIDADE      = ["Baixa", "Média", "Alta", "Crítica"]
STATUS_CORRECAO = ["Corrigido", "Em Andamento", "Pendente", "Aceito o Risco"]


def gerar_auditoria(n, start, end):
    n = max(int(n), 1)

    n_auditor = min(max(n // 40, 6), 200)
    dim_auditor = pd.DataFrame({
        "id_auditor":        new_ids(n_auditor),
        "nome":              [fake.name() for _ in range(n_auditor)],
        "certificacao":      random.choices(["CPA", "CISA", "CIA", "Nenhuma"], weights=[30, 20, 25, 25], k=n_auditor),
        "senioridade":       random.choices(["Júnior", "Pleno", "Sênior", "Gerente"], weights=[25, 35, 25, 15], k=n_auditor),
    })

    n_cliente = min(max(n // 20, 30), 3000)
    dim_cliente = pd.DataFrame({
        "id_clientepj":      new_ids(n_cliente),
        "razao_social":      [fake.company() for _ in range(n_cliente)],
        "setor_atuacao":     random.choices(["Indústria", "Varejo", "Serviços", "Financeiro", "Tecnologia"], k=n_cliente),
        "porte":             random.choices(["Pequeno", "Médio", "Grande"], weights=[40, 40, 20], k=n_cliente),
    })

    fato_auditoria = pd.DataFrame({
        "id_auditoria":      new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_auditor":        random.choices(dim_auditor["id_auditor"].tolist(), k=n),
        "id_clientepj":      random.choices(dim_cliente["id_clientepj"].tolist(), k=n),
        "tipo_auditoria":    random.choices(TIPOS_AUDITORIA, k=n),
        "risco_identificado": random.choices(NIVEL_RISCO, weights=[40, 35, 18, 7], k=n),
        "horas_trabalhadas": rng.uniform(4, 400, n).round(1),
        "valor_honorario":   rng.uniform(2500, 180000, n).round(2),
    })

    n_naoconf = int(n * 0.7)
    fato_naoconformidade = pd.DataFrame({
        "id_naoconformidade": new_ids(n_naoconf),
        "id_data":           rand_dates(start, end, n_naoconf),
        "id_clientepj":      random.choices(dim_cliente["id_clientepj"].tolist(), k=n_naoconf),
        "severidade":        random.choices(SEVERIDADE, weights=[35, 35, 22, 8], k=n_naoconf),
        "status_correcao":   random.choices(STATUS_CORRECAO, weights=[45, 30, 15, 10], k=n_naoconf),
        "prazo_correcao_dias": rng.integers(5, 180, n_naoconf),
    })

    return {
        "DimAuditor": dim_auditor,
        "DimClientePJ": dim_cliente,
        "FatoAuditoria": fato_auditoria,
        "FatoNaoConformidade": fato_naoconformidade,
        "dCalendario": dcalendario(start, end),
    }
