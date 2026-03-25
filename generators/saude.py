"""generators/saude.py — Setor Saúde."""

import random
from datetime import date

import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

ESPECIALIDADES = [
    "Clínica Geral","Cardiologia","Ortopedia","Pediatria","Ginecologia",
    "Neurologia","Oncologia","Dermatologia","Psiquiatria","Oftalmologia",
]


def gerar_saude(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_pacientes = min(n, 3000)
    n_medicos   = 80
    n_proc      = 40
    n_unidades  = 15

    dim_unidade = pd.DataFrame({
        "id_unidade": new_ids(n_unidades),
        "nome":       [f"Unidade {fake.city()}" for _ in range(n_unidades)],
        "tipo":       random.choices(["Hospital","UPA","Clínica","AME","CAPS"], k=n_unidades),
        "uf":         random.choices(["SP","RJ","MG","RS","PR"], k=n_unidades),
        "leitos":     rng.integers(20, 400, n_unidades),
    })

    dim_medico = pd.DataFrame({
        "id_medico":     new_ids(n_medicos),
        "nome":          [f"Dr(a). {fake.name()}" for _ in range(n_medicos)],
        "crm":           [f"CRM/{random.choice(['SP','RJ','MG'])}-{rng.integers(10000,99999)}"
                          for _ in range(n_medicos)],
        "especialidade": random.choices(ESPECIALIDADES, k=n_medicos),
        "id_unidade":    random.choices(dim_unidade["id_unidade"].tolist(), k=n_medicos),
    })

    dim_procedimento = pd.DataFrame({
        "id_proc":   new_ids(n_proc),
        "nome":      [f"Procedimento {fake.word().capitalize()}" for _ in range(n_proc)],
        "cid":       [f"J{rng.integers(10,99)}.{rng.integers(0,9)}" for _ in range(n_proc)],
        "categoria": random.choices(["Consulta","Exame","Cirurgia","Internação","Terapia"], k=n_proc),
        "valor_sus": rng.uniform(20, 5000, n_proc).round(2),
    })

    dim_paciente = pd.DataFrame({
        "id_paciente": new_ids(n_pacientes),
        "nome":        [fake.name() for _ in range(n_pacientes)],
        "cpf":         [fake.cpf()  for _ in range(n_pacientes)],
        "sexo":        random.choices(["M","F"], k=n_pacientes),
        "idade":       rng.integers(0, 100, n_pacientes),
        "convenio":    random.choices(["SUS","Unimed","Bradesco Saúde","Amil","Particular"], k=n_pacientes),
    })

    fato = pd.DataFrame({
        "id_atendimento": new_ids(n),
        "id_data":        rand_dates(start, end, n),
        "id_paciente":    random.choices(dim_paciente["id_paciente"].tolist(), k=n),
        "id_medico":      random.choices(dim_medico["id_medico"].tolist(), k=n),
        "id_proc":        random.choices(dim_procedimento["id_proc"].tolist(), k=n),
        "id_unidade":     random.choices(dim_unidade["id_unidade"].tolist(), k=n),
        "duracao_min":    rng.integers(15, 300, n),
        "valor_cobrado":  rng.uniform(50, 8000, n).round(2),
        "resultado":      random.choices(
            ["Alta","Internado","Em acompanhamento","Óbito"],
            weights=[70, 15, 12, 3], k=n,
        ),
    })

    return {
        "DimUnidade":      dim_unidade,
        "DimMedico":       dim_medico,
        "DimProcedimento": dim_procedimento,
        "DimPaciente":     dim_paciente,
        "FatoAtendimento": fato,
        "dCalendario":     dcalendario(start, end),
    }
