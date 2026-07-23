"""generators/terceiro_setor.py — Setor Terceiro Setor & ONGs."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

AREAS_ATUACAO = ["Educação", "Saúde", "Meio Ambiente", "Assistência Social", "Direitos Humanos", "Cultura"]
TIPOS_DOADOR = ["Pessoa Física", "Pessoa Jurídica", "Fundação", "Governo"]
TIPOS_DOACAO = ["Pontual", "Recorrente Mensal", "Patrocínio de Projeto", "Doação em Espécie"]
TIPOS_PROJETO = ["Capacitação Profissional", "Reforço Escolar", "Distribuição de Alimentos",
                  "Plantio e Reflorestamento", "Campanha de Conscientização", "Atendimento Jurídico Gratuito"]
STATUS_PROJETO = ["Planejado", "Em Execução", "Concluído", "Suspenso"]


def gerar_terceiro_setor(n, start, end):
    n = max(int(n), 1)

    n_projeto = min(max(n // 50, 15), 500)
    dim_projeto = pd.DataFrame({
        "id_projeto":        new_ids(n_projeto),
        "nome":              [f"Projeto {fake.catch_phrase()}" for _ in range(n_projeto)],
        "area_atuacao":      random.choices(AREAS_ATUACAO, k=n_projeto),
        "tipo_projeto":      random.choices(TIPOS_PROJETO, k=n_projeto),
        "meta_beneficiados": rng.integers(20, 5000, n_projeto),
    })

    n_doador = min(max(n // 4, 150), 10000)
    dim_doador = pd.DataFrame({
        "id_doador":         new_ids(n_doador),
        "nome":              [fake.name() if random.random() < 0.7 else fake.company() for _ in range(n_doador)],
        "tipo_doador":       random.choices(TIPOS_DOADOR, weights=[55, 30, 10, 5], k=n_doador),
        "uf":                [fake.state_abbr() for _ in range(n_doador)],
    })

    fato_doacao = pd.DataFrame({
        "id_doacao":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_doador":         random.choices(dim_doador["id_doador"].tolist(), k=n),
        "id_projeto":        random.choices(dim_projeto["id_projeto"].tolist(), k=n),
        "tipo_doacao":       random.choices(TIPOS_DOACAO, weights=[40, 35, 15, 10], k=n),
        "valor":             rng.uniform(20, 50000, n).round(2),
    })

    n_execucao = int(n_projeto * 4)
    fato_execucao = pd.DataFrame({
        "id_execucao":       new_ids(n_execucao),
        "id_data":           rand_dates(start, end, n_execucao),
        "id_projeto":        random.choices(dim_projeto["id_projeto"].tolist(), k=n_execucao),
        "status":            random.choices(STATUS_PROJETO, weights=[15, 55, 25, 5], k=n_execucao),
        "beneficiados_mes":  rng.integers(5, 800, n_execucao),
        "custo_execucao":    rng.uniform(500, 60000, n_execucao).round(2),
    })

    return {
        "DimProjeto": dim_projeto,
        "DimDoador": dim_doador,
        "FatoDoacao": fato_doacao,
        "FatoExecucao": fato_execucao,
        "dCalendario": dcalendario(start, end),
    }
