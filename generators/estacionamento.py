"""generators/estacionamento.py — Setor Estacionamento & Zona Azul."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_ESTACIONAMENTO = ["Rotativo (Rua)", "Zona Azul", "Estacionamento Shopping", "Estacionamento Comercial", "Mensalista"]
TIPOS_PERMANENCIA = ["Hora Avulsa", "Mensalista", "Diária", "Evento"]
TIPOS_INFRACAO = ["Tempo Excedido", "Vaga Irregular", "Sem Pagamento", "Vaga de Idoso/PCD Indevida"]


def gerar_estacionamento(n, start, end):
    n = max(int(n), 1)

    n_estacionamento = min(max(n // 150, 10), 600)
    dim_estacionamento = pd.DataFrame({
        "id_estacionamento": new_ids(n_estacionamento),
        "nome":              [f"Estacionamento {fake.street_name()}" for _ in range(n_estacionamento)],
        "tipo":              random.choices(TIPOS_ESTACIONAMENTO, weights=[35, 25, 20, 15, 5], k=n_estacionamento),
        "vagas_totais":      rng.integers(10, 800, n_estacionamento),
        "uf":                [fake.state_abbr() for _ in range(n_estacionamento)],
    })

    n_cliente = min(max(n // 6, 150), 10000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.name() for _ in range(n_cliente)],
        "mensalista":        random.choices([True, False], weights=[20, 80], k=n_cliente),
    })

    tempo_min = rng.integers(10, 720, n)
    fato_entrada = pd.DataFrame({
        "id_entrada":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_estacionamento": random.choices(dim_estacionamento["id_estacionamento"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "tipo_permanencia":  random.choices(TIPOS_PERMANENCIA, weights=[55, 20, 20, 5], k=n),
        "tempo_permanencia_min": tempo_min,
        "valor_cobrado":     (tempo_min / 60 * rng.uniform(3, 12, n)).round(2),
    })

    n_multa = int(n * 0.06)
    fato_multa = pd.DataFrame({
        "id_multa_estac":    new_ids(n_multa),
        "id_data":           rand_dates(start, end, n_multa),
        "id_estacionamento": random.choices(dim_estacionamento["id_estacionamento"].tolist(), k=n_multa),
        "tipo_infracao":     random.choices(TIPOS_INFRACAO, weights=[45, 30, 20, 5], k=n_multa),
        "valor":             rng.uniform(50, 400, n_multa).round(2),
    })

    return {
        "DimEstacionamento": dim_estacionamento,
        "DimCliente": dim_cliente,
        "FatoEntrada": fato_entrada,
        "FatoMulta": fato_multa,
        "dCalendario": dcalendario(start, end),
    }
