"""generators/ferrovia_carga.py — Setor Ferrovia de Carga."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_CARGA = ["Minério de Ferro", "Grãos", "Contêiner", "Combustível", "Celulose", "Fertilizante"]
TIPOS_MANUTENCAO = ["Preventiva", "Corretiva", "Preditiva"]
MODELOS_LOCOMOTIVA = ["DASH-9", "AC44i", "SD70", "ES44"]


def gerar_ferrovia_carga(n, start, end):
    n = max(int(n), 1)

    n_locomotiva = min(max(n // 150, 10), 300)
    dim_locomotiva = pd.DataFrame({
        "id_locomotiva":     new_ids(n_locomotiva),
        "modelo":            random.choices(MODELOS_LOCOMOTIVA, k=n_locomotiva),
        "ano_fabricacao":    rng.integers(1995, 2024, n_locomotiva),
        "potencia_hp":       rng.integers(3000, 6000, n_locomotiva),
    })

    n_terminal = min(max(n // 200, 8), 60)
    dim_terminal = pd.DataFrame({
        "id_terminal":       new_ids(n_terminal),
        "nome":              [f"Terminal {fake.city()}" for _ in range(n_terminal)],
        "uf":                [fake.state_abbr() for _ in range(n_terminal)],
    })

    fato_viagem_carga = pd.DataFrame({
        "id_viagem":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_locomotiva":     random.choices(dim_locomotiva["id_locomotiva"].tolist(), k=n),
        "id_terminal":       random.choices(dim_terminal["id_terminal"].tolist(), k=n),
        "tipo_carga":        random.choices(TIPOS_CARGA, weights=[35, 20, 15, 10, 15, 5], k=n),
        "toneladas":         rng.uniform(500, 12000, n).round(1),
        "distancia_km":      rng.uniform(80, 2200, n).round(1),
        "tempo_viagem_h":    rng.uniform(3, 72, n).round(1),
    })

    n_manut = int(n_locomotiva * 4)
    fato_manutencao = pd.DataFrame({
        "id_manutencao":     new_ids(n_manut),
        "id_data":           rand_dates(start, end, n_manut),
        "id_locomotiva":     random.choices(dim_locomotiva["id_locomotiva"].tolist(), k=n_manut),
        "tipo_manutencao":   random.choices(TIPOS_MANUTENCAO, weights=[55, 30, 15], k=n_manut),
        "custo":             rng.uniform(800, 45000, n_manut).round(2),
    })

    return {
        "DimLocomotiva": dim_locomotiva,
        "DimTerminal": dim_terminal,
        "FatoViagemCarga": fato_viagem_carga,
        "FatoManutencao": fato_manutencao,
        "dCalendario": dcalendario(start, end),
    }
