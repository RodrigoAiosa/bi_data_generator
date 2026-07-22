"""generators/consultoria.py — Setor Consultoria Empresarial."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

SEGMENTOS = ["Varejo", "Indústria", "Saúde", "Financeiro", "Tecnologia", "Agronegócio", "Educação"]
PORTES = ["Pequena", "Média", "Grande", "Corporação"]
ESPECIALIDADES = ["Estratégia", "Financeira", "Operações", "Recursos Humanos", "Tecnologia", "M&A"]
SENIORIDADE = ["Analista", "Consultor", "Consultor Sênior", "Gerente", "Sócio"]
TIPOS_PROJETO = ["Diagnóstico Organizacional", "Reestruturação", "Due Diligence", "Implementação de Sistema",
                  "Plano Estratégico", "Redução de Custos"]
STATUS_PROJETO = ["Em Diagnóstico", "Em Execução", "Em Validação", "Concluído", "Cancelado"]
STATUS_PAGAMENTO = ["Pago", "Pendente", "Atrasado"]


def gerar_consultoria(n, start, end):
    n = max(int(n), 1)

    n_cliente = min(max(n // 30, 15), 800)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.company() for _ in range(n_cliente)],
        "segmento":          random.choices(SEGMENTOS, k=n_cliente),
        "porte":             random.choices(PORTES, weights=[25, 35, 30, 10], k=n_cliente),
    })

    n_consultor = min(max(n // 60, 10), 200)
    dim_consultor = pd.DataFrame({
        "id_consultor":      new_ids(n_consultor),
        "nome":              [fake.name() for _ in range(n_consultor)],
        "especialidade":     random.choices(ESPECIALIDADES, k=n_consultor),
        "senioridade":       random.choices(SENIORIDADE, weights=[20, 30, 25, 15, 10], k=n_consultor),
    })

    horas_orcadas = rng.integers(40, 1200, n)
    fato_projeto = pd.DataFrame({
        "id_projeto":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "id_consultor":      random.choices(dim_consultor["id_consultor"].tolist(), k=n),
        "tipo_projeto":      random.choices(TIPOS_PROJETO, k=n),
        "horas_orcadas":     horas_orcadas,
        "horas_realizadas":  (horas_orcadas * rng.uniform(0.75, 1.35, n)).round(0),
        "valor_contrato":    rng.uniform(15000, 900000, n).round(2),
        "status":            random.choices(STATUS_PROJETO, weights=[15, 30, 15, 35, 5], k=n),
    })

    n_fatura = int(n * 1.4)
    fato_fatura = pd.DataFrame({
        "id_fatura":         new_ids(n_fatura),
        "id_data":           rand_dates(start, end, n_fatura),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n_fatura),
        "valor":             rng.uniform(5000, 200000, n_fatura).round(2),
        "status_pagamento":  random.choices(STATUS_PAGAMENTO, weights=[75, 15, 10], k=n_fatura),
        "forma_pagamento":   random.choices(["Boleto", "Transferência", "Cartão Corporativo"], k=n_fatura),
    })

    return {
        "DimCliente": dim_cliente,
        "DimConsultor": dim_consultor,
        "FatoProjeto": fato_projeto,
        "FatoFatura": fato_fatura,
        "dCalendario": dcalendario(start, end),
    }
