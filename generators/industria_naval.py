"""generators/industria_naval.py — Setor Indústria Naval."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

TIPOS_EMBARCACAO   = ["Cargueiro", "Petroleiro", "Rebocador", "Plataforma", "Pesqueiro", "Balsa"]
ETAPAS_CONSTRUCAO  = ["Projeto", "Corte de Chapas", "Montagem do Casco", "Lançamento", "Acabamento"]
TIPOS_DOCAGEM      = ["Docagem Programada", "Reparo Emergencial", "Inspeção Classificadora", "Pintura de Casco"]


def gerar_industria_naval(n, start, end):
    n = max(int(n), 1)

    n_estaleiro = min(max(n // 500, 3), 20)
    dim_estaleiro = pd.DataFrame({
        "id_estaleiro":      new_ids(n_estaleiro),
        "nome_estaleiro":    [f"Estaleiro {fake.city()}" for _ in range(n_estaleiro)],
        "cidade":            fake_pool(fake, "city", n_estaleiro),
        "capacidade_docas":  rng.integers(1, 8, n_estaleiro),
    })

    n_embarcacao = min(max(n // 60, 15), 600)
    dim_embarcacao = pd.DataFrame({
        "id_embarcacao":     new_ids(n_embarcacao),
        "nome_projeto":      [f"Projeto {fake.word().capitalize()}-{i}" for i in range(1, n_embarcacao + 1)],
        "tipo":              random.choices(TIPOS_EMBARCACAO, k=n_embarcacao),
        "id_estaleiro":      random.choices(dim_estaleiro["id_estaleiro"].tolist(), k=n_embarcacao),
    })

    fato_etapa = pd.DataFrame({
        "id_etapa":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_estaleiro":      random.choices(dim_estaleiro["id_estaleiro"].tolist(), k=n),
        "id_embarcacao":     random.choices(dim_embarcacao["id_embarcacao"].tolist(), k=n),
        "etapa":             random.choices(ETAPAS_CONSTRUCAO, k=n),
        "percentual_concluido": rng.uniform(1, 100, n).round(1),
        "custo":             rng.uniform(50000, 8_000_000, n).round(2),
    })

    n_manutencao = int(n * 0.25)
    fato_manutencao = pd.DataFrame({
        "id_manutencao":     new_ids(n_manutencao),
        "id_data":           rand_dates(start, end, n_manutencao),
        "id_estaleiro":      random.choices(dim_estaleiro["id_estaleiro"].tolist(), k=n_manutencao),
        "id_embarcacao":     random.choices(dim_embarcacao["id_embarcacao"].tolist(), k=n_manutencao),
        "tipo_docagem":      random.choices(TIPOS_DOCAGEM, k=n_manutencao),
        "custo":             rng.uniform(20000, 1_500_000, n_manutencao).round(2),
        "dias_parado":       rng.integers(1, 90, n_manutencao),
    })

    return {
        "DimEstaleiro": dim_estaleiro,
        "DimEmbarcacao": dim_embarcacao,
        "FatoEtapaConstrucao": fato_etapa,
        "FatoManutencao": fato_manutencao,
        "dCalendario": dcalendario(start, end),
    }
