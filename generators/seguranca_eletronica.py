"""generators/seguranca_eletronica.py — Setor Segurança Eletrônica & Monitoramento."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

TIPOS_CLIENTE = ["Residencial", "Comercial", "Industrial"]
PLANOS = ["Básico", "Intermediário", "Premium"]
TIPOS_EVENTO = ["Invasão", "Incêndio", "Pânico", "Falso Alarme"]


def gerar_seguranca_eletronica(n, start, end):
    n = max(int(n), 1)

    n_central = min(max(n // 300, 3), 40)
    dim_central = pd.DataFrame({
        "id_central":        new_ids(n_central),
        "cidade":            fake_pool(fake, "city", n_central),
        "uf":                fake_pool(fake, "state_abbr", n_central),
    })

    n_cliente = min(max(n // 4, 200), 20000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "id_central":        random.choices(dim_central["id_central"].tolist(), k=n_cliente),
        "tipo":              random.choices(TIPOS_CLIENTE, weights=[60, 30, 10], k=n_cliente),
        "plano":             random.choices(PLANOS, weights=[45, 35, 20], k=n_cliente),
    })

    fato_alarme = pd.DataFrame({
        "id_alarme":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "tipo_evento":       random.choices(TIPOS_EVENTO, weights=[15, 5, 5, 75], k=n),
        "tempo_resposta_min": rng.integers(1, 45, n),
        "deslocamento_viatura": random.choices([True, False], weights=[25, 75], k=n),
    })

    return {
        "DimCentral": dim_central,
        "DimCliente": dim_cliente,
        "FatoAlarme": fato_alarme,
        "dCalendario": dcalendario(start, end),
    }
