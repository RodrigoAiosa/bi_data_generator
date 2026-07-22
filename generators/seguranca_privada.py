"""generators/seguranca_privada.py — Setor Segurança Privada."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

FUNCOES = ["Vigilante", "Porteiro", "Supervisor", "Vigilante Armado", "Operador de Monitoramento"]
TURNOS = ["Diurno 12h", "Noturno 12h", "Comercial 8h", "Plantão 24h"]
CERTIFICACOES = ["Curso de Formação", "Reciclagem em Dia", "Vencida", "Armamento"]
TIPOS_LOCAL = ["Residencial", "Comercial", "Industrial", "Evento", "Condomínio", "Órgão Público"]
TIPOS_POSTO = ["Fixo", "Ronda", "Monitoramento CFTV", "Portaria"]
TIPOS_OCORRENCIA = ["Furto", "Tentativa de Invasão", "Alarme Falso", "Emergência Médica", "Perturbação", "Incêndio"]
GRAVIDADE = ["Baixa", "Média", "Alta"]


def gerar_seguranca_privada(n, start, end):
    n = max(int(n), 1)

    n_vigilante = min(max(n // 40, 15), 1500)
    dim_vigilante = pd.DataFrame({
        "id_vigilante":      new_ids(n_vigilante),
        "nome":              [fake.name() for _ in range(n_vigilante)],
        "funcao":            random.choices(FUNCOES, weights=[40, 20, 12, 18, 10], k=n_vigilante),
        "turno":             random.choices(TURNOS, k=n_vigilante),
        "certificacao":      random.choices(CERTIFICACOES, weights=[35, 45, 10, 10], k=n_vigilante),
    })

    n_cliente = min(max(n // 15, 30), 3000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.company() for _ in range(n_cliente)],
        "tipo_local":        random.choices(TIPOS_LOCAL, k=n_cliente),
        "uf":                [fake.state_abbr() for _ in range(n_cliente)],
    })

    fato_escalacao = pd.DataFrame({
        "id_escalacao":      new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_vigilante":      random.choices(dim_vigilante["id_vigilante"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "horas_trabalhadas": random.choices([8, 12, 24], weights=[35, 55, 10], k=n),
        "tipo_posto":        random.choices(TIPOS_POSTO, k=n),
    })

    n_ocorrencia = int(n * 0.15)
    fato_ocorrencia = pd.DataFrame({
        "id_ocorrencia_seg": new_ids(n_ocorrencia),
        "id_data":           rand_dates(start, end, n_ocorrencia),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n_ocorrencia),
        "tipo_ocorrencia":   random.choices(TIPOS_OCORRENCIA, weights=[20, 15, 30, 15, 15, 5], k=n_ocorrencia),
        "gravidade":         random.choices(GRAVIDADE, weights=[55, 30, 15], k=n_ocorrencia),
        "tempo_resposta_min": rng.integers(1, 45, n_ocorrencia),
    })

    return {
        "DimVigilante": dim_vigilante,
        "DimCliente": dim_cliente,
        "FatoEscalacao": fato_escalacao,
        "FatoOcorrencia": fato_ocorrencia,
        "dCalendario": dcalendario(start, end),
    }
