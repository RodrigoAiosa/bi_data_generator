"""generators/parque_diversoes.py — Setor Parque de Diversões."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_BRINQUEDO    = ["Radical", "Infantil", "Aquático", "Família", "Show/Atração"]
CATEGORIAS_INGRESSO = ["Inteira", "Meia-Entrada", "Passe Anual", "Combo Família", "Cortesia"]
CANAIS_VENDA       = ["Bilheteria", "Site Oficial", "Agência de Turismo", "Parceiro"]


def gerar_parque_diversoes(n, start, end):
    n = max(int(n), 1)

    n_brinquedo = min(max(n // 300, 8), 60)
    dim_brinquedo = pd.DataFrame({
        "id_brinquedo":      new_ids(n_brinquedo),
        "nome":              [f"Atração {fake.first_name()}" for _ in range(n_brinquedo)],
        "tipo":              random.choices(TIPOS_BRINQUEDO, weights=[25, 30, 15, 20, 10], k=n_brinquedo),
        "capacidade_por_ciclo": rng.integers(2, 60, n_brinquedo),
        "altura_minima_cm":  random.choices([0, 100, 120, 140, 160], weights=[30, 25, 20, 15, 10], k=n_brinquedo),
    })

    n_ingresso_tipo = len(CATEGORIAS_INGRESSO)
    dim_ingresso = pd.DataFrame({
        "id_ingresso":       new_ids(n_ingresso_tipo),
        "categoria":         CATEGORIAS_INGRESSO,
        "valor_base":        [220.0, 110.0, 890.0, 680.0, 0.0],
    })

    ingresso_idx = random.choices(range(n_ingresso_tipo), k=n)
    valor_base = dim_ingresso["valor_base"].to_numpy()[ingresso_idx]
    fato_ingresso = pd.DataFrame({
        "id_venda_ingresso": new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_ingresso":       dim_ingresso["id_ingresso"].to_numpy()[ingresso_idx],
        "canal_venda":       random.choices(CANAIS_VENDA, weights=[40, 35, 15, 10], k=n),
        "valor":             (valor_base * rng.uniform(0.9, 1.15, n)).round(2),
    })

    n_uso = int(n * 2.5)
    fato_uso_brinquedo = pd.DataFrame({
        "id_uso":            new_ids(n_uso),
        "id_data":           rand_dates(start, end, n_uso),
        "id_brinquedo":      random.choices(dim_brinquedo["id_brinquedo"].tolist(), k=n_uso),
        "tempo_fila_min":    rng.integers(0, 90, n_uso),
        "satisfacao":        rng.integers(1, 6, n_uso),
    })

    return {
        "DimBrinquedo": dim_brinquedo,
        "DimIngresso": dim_ingresso,
        "FatoIngresso": fato_ingresso,
        "FatoUsoBrinquedo": fato_uso_brinquedo,
        "dCalendario": dcalendario(start, end),
    }
