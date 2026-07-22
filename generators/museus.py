"""generators/museus.py — Setor Museus & Cultura."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_EXPO = ["Permanente", "Temporária", "Itinerante"]
CATEGORIAS_EXPO = ["Arte", "História", "Ciência", "Tecnologia", "Antropologia", "Fotografia"]
FAIXAS_ETARIAS = ["Criança", "Jovem", "Adulto", "Idoso"]
TIPOS_INGRESSO = ["Inteira", "Meia-Entrada", "Gratuita", "Visitante Sócio"]
TIPOS_EVENTO = ["Palestra", "Oficina", "Visita Guiada", "Lançamento", "Concerto"]


def gerar_museus(n, start, end):
    n = max(int(n), 1)

    n_exposicao = min(max(n // 100, 10), 200)
    dim_exposicao = pd.DataFrame({
        "id_exposicao":      new_ids(n_exposicao),
        "nome":              [f"{fake.catch_phrase()}" for _ in range(n_exposicao)],
        "tipo":              random.choices(TIPOS_EXPO, weights=[45, 40, 15], k=n_exposicao),
        "categoria":         random.choices(CATEGORIAS_EXPO, k=n_exposicao),
    })

    n_visitante = min(max(n // 3, 200), 20000)
    dim_visitante = pd.DataFrame({
        "id_visitante":      new_ids(n_visitante),
        "faixa_etaria":      random.choices(FAIXAS_ETARIAS, weights=[15, 30, 40, 15], k=n_visitante),
        "tipo_ingresso":     random.choices(TIPOS_INGRESSO, weights=[45, 30, 15, 10], k=n_visitante),
        "uf":                [fake.state_abbr() for _ in range(n_visitante)],
    })

    fato_visita = pd.DataFrame({
        "id_visita":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_exposicao":      random.choices(dim_exposicao["id_exposicao"].tolist(), k=n),
        "id_visitante":      random.choices(dim_visitante["id_visitante"].tolist(), k=n),
        "valor_ingresso":    rng.uniform(0, 60, n).round(2),
        "tempo_permanencia_min": rng.integers(15, 240, n),
        "avaliacao":         rng.integers(1, 6, n),
    })

    n_evento = int(n_exposicao * 3)
    fato_evento = pd.DataFrame({
        "id_evento_cult":    new_ids(n_evento),
        "id_data":           rand_dates(start, end, n_evento),
        "id_exposicao":      random.choices(dim_exposicao["id_exposicao"].tolist(), k=n_evento),
        "tipo_evento":       random.choices(TIPOS_EVENTO, k=n_evento),
        "publico":           rng.integers(5, 500, n_evento),
        "receita":           rng.uniform(0, 15000, n_evento).round(2),
    })

    return {
        "DimExposicao": dim_exposicao,
        "DimVisitante": dim_visitante,
        "FatoVisita": fato_visita,
        "FatoEvento": fato_evento,
        "dCalendario": dcalendario(start, end),
    }
