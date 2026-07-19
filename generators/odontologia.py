"""generators/odontologia.py — Setor Odontologia (Clínicas Odontológicas)."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

ESPECIALIDADES = ["Clínico Geral", "Ortodontia", "Endodontia", "Periodontia",
                   "Implantodontia", "Odontopediatria", "Prótese", "Cirurgia Bucomaxilo"]
PROCEDIMENTOS  = ["Limpeza", "Restauração", "Canal", "Extração", "Clareamento",
                   "Aparelho Ortodôntico", "Implante", "Prótese Dentária",
                   "Raio-X", "Manutenção de Aparelho"]
CONVENIOS      = ["Particular", "Amil Dental", "OdontoPrev", "Bradesco Dental",
                   "SulAmérica Odonto", "Porto Seguro Dental", "Unimed Odonto"]
STATUS_CONSULTA = ["Confirmada", "Cancelada", "Realizada", "Faltou", "Remarcada"]


def gerar_odontologia(n, start, end):
    n = max(int(n), 1)

    n_dentista = min(max(n // 60, 8), 120)
    dim_dentista = pd.DataFrame({
        "id_dentista":       new_ids(n_dentista),
        "nome":              [f"Dr(a). {fake.name()}" for _ in range(n_dentista)],
        "especialidade":     random.choices(ESPECIALIDADES, k=n_dentista),
        "cro":               [f"CRO-{fake.state_abbr()}{rng.integers(10000,99999)}" for _ in range(n_dentista)],
        "anos_experiencia":  rng.integers(1, 35, n_dentista),
        "avaliacao":         rng.uniform(3.5, 5.0, n_dentista).round(1),
        "ativo":             random.choices([True, False], weights=[92, 8], k=n_dentista),
    })

    n_paciente = min(max(n // 4, 100), 8000)
    dim_paciente = pd.DataFrame({
        "id_paciente":       new_ids(n_paciente),
        "nome":              [fake.name() for _ in range(n_paciente)],
        "idade":             rng.integers(3, 90, n_paciente),
        "sexo":              random.choices(["F", "M"], k=n_paciente),
        "convenio":          random.choices(CONVENIOS, weights=[30,15,15,12,12,8,8], k=n_paciente),
        "uf":                [fake.state_abbr() for _ in range(n_paciente)],
        "cidade":            [fake.city() for _ in range(n_paciente)],
    })

    status_consulta = random.choices(STATUS_CONSULTA, weights=[15, 8, 65, 7, 5], k=n)
    fato_consulta = pd.DataFrame({
        "id_consulta":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_dentista":       random.choices(dim_dentista["id_dentista"].tolist(), k=n),
        "id_paciente":       random.choices(dim_paciente["id_paciente"].tolist(), k=n),
        "status":            status_consulta,
        "duracao_min":       random.choices([20, 30, 45, 60, 90], k=n),
        "primeira_consulta": random.choices([True, False], weights=[20, 80], k=n),
        "faltou":            [s == "Faltou" for s in status_consulta],
    })

    n_proc = int(n * 0.75)
    convenio_cobre = random.choices([True, False], weights=[65, 35], k=n_proc)
    valor_proc = rng.uniform(80, 4500, n_proc).round(2)
    fato_procedimento = pd.DataFrame({
        "id_procedimento":   new_ids(n_proc),
        "id_data":           rand_dates(start, end, n_proc),
        "id_dentista":       random.choices(dim_dentista["id_dentista"].tolist(), k=n_proc),
        "id_paciente":       random.choices(dim_paciente["id_paciente"].tolist(), k=n_proc),
        "procedimento":      random.choices(PROCEDIMENTOS, k=n_proc),
        "valor":             valor_proc,
        "convenio_cobre":    convenio_cobre,
        "valor_coberto":     [round(v * random.uniform(0.5, 1.0), 2) if c else 0.0
                               for v, c in zip(valor_proc, convenio_cobre)],
        "sessoes":           rng.integers(1, 8, n_proc),
        "sucesso":           random.choices([True, False], weights=[95, 5], k=n_proc),
    })

    return {
        "DimDentista": dim_dentista,
        "DimPaciente": dim_paciente,
        "FatoConsulta": fato_consulta,
        "FatoProcedimento": fato_procedimento,
        "dCalendario": dcalendario(start, end),
    }
