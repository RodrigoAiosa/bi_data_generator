"""generators/motoboy.py — Setor Motoboy & App de Transporte."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_VEICULO      = ["Moto 125cc", "Moto 160cc", "Scooter Elétrica"]
TIPOS_CLIENTE      = ["Pessoa Física", "Loja Parceira", "Restaurante", "Farmácia"]
TIPOS_SERVICO      = ["Entrega Rápida", "Entrega Agendada", "Corrida de Passageiro", "Documentos"]


def gerar_motoboy(n, start, end):
    n = max(int(n), 1)

    n_motociclista = min(max(n // 60, 10), 3000)
    dim_motociclista = pd.DataFrame({
        "id_motociclista":   new_ids(n_motociclista),
        "nome":              [fake.name() for _ in range(n_motociclista)],
        "tipo_veiculo":      random.choices(TIPOS_VEICULO, weights=[55, 35, 10], k=n_motociclista),
        "anos_experiencia":  rng.integers(0, 20, n_motociclista),
    })

    n_cliente = min(max(n // 10, 100), 8000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome_cliente":      [fake.name() if random.random() < 0.5 else fake.company() for _ in range(n_cliente)],
        "tipo_cliente":      random.choices(TIPOS_CLIENTE, weights=[35, 25, 25, 15], k=n_cliente),
    })

    fato_corrida = pd.DataFrame({
        "id_corrida":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_motociclista":   random.choices(dim_motociclista["id_motociclista"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "tipo_servico":      random.choices(TIPOS_SERVICO, weights=[50, 20, 20, 10], k=n),
        "distancia_km":      rng.uniform(0.5, 35, n).round(1),
        "valor":             rng.uniform(6, 120, n).round(2),
        "tempo_min":         rng.integers(5, 90, n),
        "avaliacao":         rng.integers(1, 6, n),
    })

    return {
        "DimMotociclista": dim_motociclista,
        "DimCliente": dim_cliente,
        "FatoCorrida": fato_corrida,
        "dCalendario": dcalendario(start, end),
    }
