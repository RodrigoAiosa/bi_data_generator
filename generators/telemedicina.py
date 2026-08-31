"""generators/telemedicina.py — Setor Telemedicina."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

ESPECIALIDADES = ["Clínico Geral", "Psiquiatria", "Dermatologia", "Cardiologia", "Endocrinologia",
                   "Pediatria", "Ginecologia", "Nutrição", "Psicologia"]
PLATAFORMAS = ["App Mobile", "Web", "WhatsApp Integrado"]
STATUS_CONSULTA = ["Realizada", "Cancelada", "Paciente Não Compareceu", "Reagendada"]
TIPOS_MEDICAMENTO = ["Antibiótico", "Anti-inflamatório", "Antialérgico", "Antidepressivo",
                      "Anti-hipertensivo", "Hipoglicemiante", "Analgésico"]


def gerar_telemedicina(n, start, end):
    n = max(int(n), 1)

    n_medico = min(max(n // 60, 20), 2500)
    dim_medico = pd.DataFrame({
        "id_medico":         new_ids(n_medico),
        "nome":              [fake.name() for _ in range(n_medico)],
        "especialidade":     random.choices(ESPECIALIDADES, k=n_medico),
        "anos_experiencia":  rng.integers(1, 35, n_medico),
        "avaliacao_media":   rng.uniform(3.5, 5.0, n_medico).round(1),
        "ativo":             random.choices([True, False], weights=[88, 12], k=n_medico),
    })

    n_paciente = min(max(n // 3, 200), 40000)
    dim_paciente = pd.DataFrame({
        "id_paciente":       new_ids(n_paciente),
        "nome":              [fake.name() for _ in range(n_paciente)],
        "idade":             rng.integers(1, 95, n_paciente),
        "sexo":              random.choices(["F", "M"], k=n_paciente),
        "uf":                [fake.state_abbr() for _ in range(n_paciente)],
        "plano_assinatura":  random.choices(["Avulso", "Mensal", "Anual", "Corporativo"], weights=[30, 35, 15, 20], k=n_paciente),
    })

    status_consulta = random.choices(STATUS_CONSULTA, weights=[75, 10, 8, 7], k=n)
    fato_teleconsulta = pd.DataFrame({
        "id_teleconsulta":   new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_medico":         random.choices(dim_medico["id_medico"].tolist(), k=n),
        "id_paciente":       random.choices(dim_paciente["id_paciente"].tolist(), k=n),
        "plataforma":        random.choices(PLATAFORMAS, weights=[55, 35, 10], k=n),
        "duracao_min":       rng.integers(5, 60, n),
        "status":            status_consulta,
        "avaliacao":         [rng.integers(1, 6) if s == "Realizada" else None for s in status_consulta],
        "valor":             rng.uniform(45, 350, n).round(2),
    })

    n_prescricao = int(n * 0.55)
    fato_prescricao = pd.DataFrame({
        "id_prescricao":     new_ids(n_prescricao),
        "id_data":           rand_dates(start, end, n_prescricao),
        "id_medico":         random.choices(dim_medico["id_medico"].tolist(), k=n_prescricao),
        "id_paciente":       random.choices(dim_paciente["id_paciente"].tolist(), k=n_prescricao),
        "tipo_medicamento":  random.choices(TIPOS_MEDICAMENTO, k=n_prescricao),
        "quantidade_itens":  rng.integers(1, 5, n_prescricao),
        "uso_continuo":      random.choices([True, False], weights=[30, 70], k=n_prescricao),
    })

    return {
        "DimMedico": dim_medico,
        "DimPaciente": dim_paciente,
        "FatoTeleconsulta": fato_teleconsulta,
        "FatoPrescricao": fato_prescricao,
        "dCalendario": dcalendario(start, end),
    }
