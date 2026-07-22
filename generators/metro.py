"""generators/metro.py — Setor Metrô & Trem Urbano."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

ZONAS = ["Centro", "Norte", "Sul", "Leste", "Oeste"]
CORES_LINHA = ["Azul", "Vermelha", "Verde", "Amarela", "Prata", "Lilás"]
TIPOS_TARIFA = ["Integral", "Estudante", "Idoso (Gratuidade)", "Vale-Transporte", "Bilhete Único"]
TIPOS_OCORRENCIA = ["Atraso", "Falha Técnica", "Superlotação", "Interdição de Estação", "Problema de Sinalização"]


def gerar_metro(n, start, end):
    n = max(int(n), 1)

    n_linha = min(max(n // 3000, 3), 12)
    dim_linha = pd.DataFrame({
        "id_linha":          new_ids(n_linha),
        "nome":              [f"Linha {c}" for c in random.sample(CORES_LINHA * 2, n_linha)],
        "extensao_km":       rng.uniform(8, 45, n_linha).round(1),
        "cor":               random.choices(CORES_LINHA, k=n_linha),
    })

    n_estacao = min(max(n // 200, 15), 300)
    dim_estacao = pd.DataFrame({
        "id_estacao":        new_ids(n_estacao),
        "nome":              [f"Estação {fake.street_name()}" for _ in range(n_estacao)],
        "linha":             random.choices(dim_linha["id_linha"].tolist(), k=n_estacao),
        "zona":              random.choices(ZONAS, k=n_estacao),
    })

    fato_validacao = pd.DataFrame({
        "id_validacao":      new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_estacao":        random.choices(dim_estacao["id_estacao"].tolist(), k=n),
        "id_linha":          random.choices(dim_linha["id_linha"].tolist(), k=n),
        "tipo_tarifa":       random.choices(TIPOS_TARIFA, weights=[45, 20, 15, 15, 5], k=n),
        "horario_pico":      random.choices([True, False], weights=[40, 60], k=n),
    })

    n_ocorrencia = int(n_linha * 400)
    fato_ocorrencia = pd.DataFrame({
        "id_ocorrencia_metro": new_ids(n_ocorrencia),
        "id_data":           rand_dates(start, end, n_ocorrencia),
        "id_linha":          random.choices(dim_linha["id_linha"].tolist(), k=n_ocorrencia),
        "tipo_ocorrencia":   random.choices(TIPOS_OCORRENCIA, weights=[40, 20, 20, 10, 10], k=n_ocorrencia),
        "tempo_impacto_min": rng.integers(2, 90, n_ocorrencia),
    })

    return {
        "DimLinha": dim_linha,
        "DimEstacao": dim_estacao,
        "FatoValidacao": fato_validacao,
        "FatoOcorrencia": fato_ocorrencia,
        "dCalendario": dcalendario(start, end),
    }
