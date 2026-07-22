"""generators/cinema.py — Setor Cinema & Exibição."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

GENEROS = ["Ação", "Comédia", "Drama", "Terror", "Animação", "Ficção Científica", "Romance", "Documentário"]
CLASSIFICACOES = ["Livre", "10 anos", "12 anos", "14 anos", "16 anos", "18 anos"]
TIPOS_SALA = ["2D", "3D", "IMAX", "VIP"]
CINEMAS = ["Shopping Central", "Shopping Norte", "Shopping Sul", "Downtown", "Praia Mall"]
ITENS_BOMBONIERE = ["Pipoca Grande", "Pipoca Média", "Refrigerante", "Combo Casal", "Chocolate", "Nachos"]


def gerar_cinema(n, start, end):
    n = max(int(n), 1)

    n_filme = min(max(n // 20, 20), 600)
    dim_filme = pd.DataFrame({
        "id_filme":          new_ids(n_filme),
        "titulo":            [fake.catch_phrase() for _ in range(n_filme)],
        "genero":            random.choices(GENEROS, k=n_filme),
        "duracao_min":       rng.integers(80, 180, n_filme),
        "classificacao":     random.choices(CLASSIFICACOES, k=n_filme),
    })

    n_sala = min(max(n // 100, 8), 200)
    dim_sala = pd.DataFrame({
        "id_sala":           new_ids(n_sala),
        "nome":              [f"Sala {i+1}" for i in range(n_sala)],
        "tipo":              random.choices(TIPOS_SALA, weights=[50, 30, 12, 8], k=n_sala),
        "capacidade":        rng.integers(60, 350, n_sala),
        "cinema":            random.choices(CINEMAS, k=n_sala),
    })

    ingressos = rng.integers(5, 300, n)
    fato_sessao = pd.DataFrame({
        "id_sessao":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_filme":          random.choices(dim_filme["id_filme"].tolist(), k=n),
        "id_sala":           random.choices(dim_sala["id_sala"].tolist(), k=n),
        "ingressos_vendidos": ingressos,
        "receita_bilheteria": (ingressos * rng.uniform(18, 55, n)).round(2),
        "ocupacao_pct":      rng.uniform(10, 100, n).round(1),
    })

    n_bomb = int(n * 1.5)
    qtd = rng.integers(1, 5, n_bomb)
    fato_bomboniere = pd.DataFrame({
        "id_bomboniere":     new_ids(n_bomb),
        "id_data":           rand_dates(start, end, n_bomb),
        "id_sala":           random.choices(dim_sala["id_sala"].tolist(), k=n_bomb),
        "item":              random.choices(ITENS_BOMBONIERE, k=n_bomb),
        "quantidade":        qtd,
        "valor_total":       (qtd * rng.uniform(12, 45, n_bomb)).round(2),
    })

    return {
        "DimFilme": dim_filme,
        "DimSala": dim_sala,
        "FatoSessao": fato_sessao,
        "FatoBomboniere": fato_bomboniere,
        "dCalendario": dcalendario(start, end),
    }
