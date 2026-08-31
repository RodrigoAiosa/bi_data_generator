"""generators/fisioterapia.py — Setor Fisioterapia & Reabilitação."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

ESPECIALIDADES = ["Ortopédica", "Neurológica", "Respiratória", "Esportiva", "Pediátrica"]
TIPOS_TRATAMENTO = ["RPG", "Pilates Clínico", "Cinesioterapia", "Eletroterapia", "Hidroterapia"]


def gerar_fisioterapia(n, start, end):
    n = max(int(n), 1)

    n_clinica = min(max(n // 150, 5), 80)
    dim_clinica = pd.DataFrame({
        "id_clinica":        new_ids(n_clinica),
        "cidade":            [fake.city() for _ in range(n_clinica)],
        "uf":                [fake.state_abbr() for _ in range(n_clinica)],
    })

    n_fisio = min(max(n // 30, 15), 1500)
    dim_fisioterapeuta = pd.DataFrame({
        "id_fisioterapeuta": new_ids(n_fisio),
        "id_clinica":        random.choices(dim_clinica["id_clinica"].tolist(), k=n_fisio),
        "nome":              [fake.name() for _ in range(n_fisio)],
        "especialidade":     random.choices(ESPECIALIDADES, k=n_fisio),
    })

    fato_sessao = pd.DataFrame({
        "id_sessao":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_fisioterapeuta": random.choices(dim_fisioterapeuta["id_fisioterapeuta"].tolist(), k=n),
        "paciente":          [fake.name() for _ in range(n)],
        "tipo_tratamento":   random.choices(TIPOS_TRATAMENTO, k=n),
        "valor":             rng.uniform(60, 350, n).round(2),
        "convenio":          random.choices([True, False], weights=[60, 40], k=n),
    })

    return {
        "DimClinica": dim_clinica,
        "DimFisioterapeuta": dim_fisioterapeuta,
        "FatoSessao": fato_sessao,
        "dCalendario": dcalendario(start, end),
    }
