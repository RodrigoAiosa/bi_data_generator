"""generators/asilo.py — Setor Asilo & Casa de Repouso."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

GRAUS_DEPENDENCIA = ["Baixo", "Médio", "Alto"]
TIPOS_OCORRENCIA = ["Queda", "Medicação", "Consulta Médica", "Alta", "Internação"]


def gerar_asilo(n, start, end):
    n = max(int(n), 1)

    n_instituicao = min(max(n // 150, 5), 60)
    dim_instituicao = pd.DataFrame({
        "id_instituicao":    new_ids(n_instituicao),
        "nome_instituicao":  [f"Residencial {fake.last_name()}" for _ in range(n_instituicao)],
        "cidade":            [fake.city() for _ in range(n_instituicao)],
        "uf":                [fake.state_abbr() for _ in range(n_instituicao)],
        "capacidade_leitos":  rng.integers(15, 200, n_instituicao),
    })

    n_residente = min(max(n // 4, 100), 8000)
    dim_residente = pd.DataFrame({
        "id_residente":      new_ids(n_residente),
        "id_instituicao":    random.choices(dim_instituicao["id_instituicao"].tolist(), k=n_residente),
        "nome":              [fake.name() for _ in range(n_residente)],
        "idade":             rng.integers(60, 100, n_residente),
        "grau_dependencia":  random.choices(GRAUS_DEPENDENCIA, weights=[40, 40, 20], k=n_residente),
    })

    fato_ocorrencia = pd.DataFrame({
        "id_ocorrencia":     new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_residente":      random.choices(dim_residente["id_residente"].tolist(), k=n),
        "tipo_ocorrencia":   random.choices(TIPOS_OCORRENCIA, weights=[15, 40, 30, 10, 5], k=n),
        "gravidade":         random.choices(["Leve", "Moderada", "Grave"], weights=[60, 30, 10], k=n),
        "custo":             rng.uniform(0, 3500, n).round(2),
    })

    return {
        "DimInstituicao": dim_instituicao,
        "DimResidente": dim_residente,
        "FatoOcorrencia": fato_ocorrencia,
        "dCalendario": dcalendario(start, end),
    }
