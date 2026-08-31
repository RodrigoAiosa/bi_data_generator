"""generators/radio_podcast.py — Setor Rádio & Podcast."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

FORMATOS         = ["Rádio FM", "Rádio AM", "Podcast"]
GENEROS          = ["Notícias", "Esportes", "Música", "Entrevista", "Humor", "Educativo", "True Crime"]
PLATAFORMAS      = ["FM/AM", "Spotify", "YouTube", "Apple Podcasts", "Site Próprio"]
CATEGORIAS_ANUNCIANTE = ["Varejo", "Automotivo", "Alimentos", "Serviços Financeiros", "Governo", "Educação"]


def gerar_radio_podcast(n, start, end):
    n = max(int(n), 1)

    n_apresentador = min(max(n // 150, 8), 200)
    dim_apresentador = pd.DataFrame({
        "id_apresentador":   new_ids(n_apresentador),
        "nome":              [fake.name() for _ in range(n_apresentador)],
        "anos_carreira":     rng.integers(1, 30, n_apresentador),
    })

    n_programa = min(max(n // 60, 10), 300)
    dim_programa = pd.DataFrame({
        "id_programa":       new_ids(n_programa),
        "nome":              [f"{random.choice(GENEROS)} {fake.word().capitalize()}" for _ in range(n_programa)],
        "formato":           random.choices(FORMATOS, weights=[40, 15, 45], k=n_programa),
        "genero":            random.choices(GENEROS, k=n_programa),
        "id_apresentador":   random.choices(dim_apresentador["id_apresentador"].tolist(), k=n_programa),
    })

    fato_audiencia = pd.DataFrame({
        "id_audiencia":      new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_programa":       random.choices(dim_programa["id_programa"].tolist(), k=n),
        "plataforma":        random.choices(PLATAFORMAS, weights=[35, 25, 20, 10, 10], k=n),
        "ouvintes_estimados": rng.integers(50, 500000, n),
        "tempo_medio_min":   rng.uniform(3, 90, n).round(1),
    })

    n_anuncio = int(n * 0.4)
    fato_anuncio = pd.DataFrame({
        "id_anuncio":        new_ids(n_anuncio),
        "id_data":           rand_dates(start, end, n_anuncio),
        "id_programa":       random.choices(dim_programa["id_programa"].tolist(), k=n_anuncio),
        "anunciante_categoria": random.choices(CATEGORIAS_ANUNCIANTE, k=n_anuncio),
        "valor_patrocinio":  rng.uniform(300, 45000, n_anuncio).round(2),
        "insercoes":         rng.integers(1, 60, n_anuncio),
    })

    return {
        "DimPrograma": dim_programa,
        "DimApresentador": dim_apresentador,
        "FatoAudiencia": fato_audiencia,
        "FatoAnuncio": fato_anuncio,
        "dCalendario": dcalendario(start, end),
    }
