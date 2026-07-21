"""generators/homecare.py — Setor Home Care (Assistência Domiciliar à Saúde)."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

PLANOS_SAUDE = ["Particular", "Amil", "Bradesco Saúde", "SulAmérica", "Unimed", "Porto Seguro Saúde"]
GRAU_DEPENDENCIA = ["Baixo", "Médio", "Alto"]
FUNCOES = ["Enfermeiro", "Técnico de Enfermagem", "Fisioterapeuta", "Cuidador", "Médico", "Nutricionista"]
TURNOS = ["Manhã", "Tarde", "Noite", "Plantão 12h", "Plantão 24h"]
TIPOS_VISITA = ["Curativo", "Fisioterapia", "Consulta Médica", "Administração de Medicamento", "Avaliação Nutricional", "Cuidados Gerais"]
TIPOS_OCORRENCIA = ["Queda", "Intercorrência Clínica", "Internação", "Óbito", "Reação a Medicamento"]
GRAVIDADE = ["Leve", "Moderada", "Grave"]


def gerar_homecare(n, start, end):
    n = max(int(n), 1)

    n_paciente = min(max(n // 8, 100), 5000)
    dim_paciente = pd.DataFrame({
        "id_paciente":       new_ids(n_paciente),
        "nome":              [fake.name() for _ in range(n_paciente)],
        "idade":             rng.integers(0, 100, n_paciente),
        "uf":                [fake.state_abbr() for _ in range(n_paciente)],
        "plano_saude":       random.choices(PLANOS_SAUDE, weights=[15, 20, 18, 15, 20, 12], k=n_paciente),
        "grau_dependencia":  random.choices(GRAU_DEPENDENCIA, weights=[35, 40, 25], k=n_paciente),
    })

    n_profissional = min(max(n // 60, 15), 400)
    dim_profissional = pd.DataFrame({
        "id_profissional":   new_ids(n_profissional),
        "nome":              [fake.name() for _ in range(n_profissional)],
        "funcao":            random.choices(FUNCOES, weights=[20, 20, 20, 25, 8, 7], k=n_profissional),
        "turno":             random.choices(TURNOS, k=n_profissional),
    })

    fato_visita = pd.DataFrame({
        "id_visita":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_paciente":       random.choices(dim_paciente["id_paciente"].tolist(), k=n),
        "id_profissional":   random.choices(dim_profissional["id_profissional"].tolist(), k=n),
        "tipo_visita":       random.choices(TIPOS_VISITA, k=n),
        "duracao_min":       random.choices([30, 45, 60, 90, 120], k=n),
        "procedimentos_realizados": rng.integers(1, 6, n),
        "custo":             rng.uniform(80, 1200, n).round(2),
    })

    n_ocorrencia = int(n_paciente * 0.3)
    hospitalizacao = random.choices([True, False], weights=[20, 80], k=n_ocorrencia)
    fato_ocorrencia = pd.DataFrame({
        "id_ocorrencia":     new_ids(n_ocorrencia),
        "id_data":           rand_dates(start, end, n_ocorrencia),
        "id_paciente":       random.choices(dim_paciente["id_paciente"].tolist(), k=n_ocorrencia),
        "tipo_ocorrencia":   random.choices(TIPOS_OCORRENCIA, weights=[30, 35, 20, 5, 10], k=n_ocorrencia),
        "gravidade":         random.choices(GRAVIDADE, weights=[50, 35, 15], k=n_ocorrencia),
        "hospitalizacao":    hospitalizacao,
    })

    return {
        "DimPaciente": dim_paciente,
        "DimProfissional": dim_profissional,
        "FatoVisita": fato_visita,
        "FatoOcorrencia": fato_ocorrencia,
        "dCalendario": dcalendario(start, end),
    }
