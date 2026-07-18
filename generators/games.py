"""generators/games.py — Setor Games & eSports."""

import random
from datetime import date

import pandas as pd

from .helpers import dcalendario, get_faker, new_ids, rand_dates, rng

JOGOS = [
    ("Valor Tático",       "FPS Tático",     ["PC", "Console"]),
    ("Arena Legends",      "MOBA",           ["PC"]),
    ("Battle Royale Zero", "Battle Royale",  ["PC", "Console", "Mobile"]),
    ("Reinos Perdidos",    "RPG",            ["PC", "Console"]),
    ("Liga Virtual",       "Esportes",       ["Console", "Mobile"]),
    ("Puzzle Mundi",       "Puzzle",         ["Mobile"]),
    ("Corrida Extrema",    "Corrida",        ["PC", "Console"]),
    ("Estratégia Total",   "Estratégia",     ["PC"]),
]
PUBLISHERS = ["NovaGames Studio", "Pixel Forge", "Horizon Interactive", "Byte Dragon", "Quantum Play"]

PAISES = ["Brasil", "Argentina", "Portugal", "Estados Unidos", "México", "Chile", "Colômbia"]
TIPOS_CONTA = ["Free", "Premium", "Battle Pass"]
TIPOS_EVENTO = ["Casual", "Ranqueada", "Torneio Oficial", "Evento Sazonal"]
RESULTADOS = ["Vitória", "Derrota", "Empate"]


def gerar_games(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    fake = get_faker()

    n_jogos     = len(JOGOS)
    n_jogadores = min(n, 10000)

    # ── DimJogo ──────────────────────────────────────────────────────────────
    dim_jogo = pd.DataFrame({
        "id_jogo":      new_ids(n_jogos),
        "nome_jogo":    [j[0] for j in JOGOS],
        "genero":       [j[1] for j in JOGOS],
        "plataformas":  [", ".join(j[2]) for j in JOGOS],
        "publisher":    random.choices(PUBLISHERS, k=n_jogos),
        "ano_lancamento": rng.integers(2015, 2026, n_jogos),
    })

    # ── DimJogador ───────────────────────────────────────────────────────────
    dim_jogador = pd.DataFrame({
        "id_jogador":       new_ids(n_jogadores),
        "nickname":         [fake.user_name() for _ in range(n_jogadores)],
        "pais":             random.choices(PAISES, weights=[55, 8, 6, 12, 8, 6, 5], k=n_jogadores),
        "faixa_etaria":     random.choices(
            ["13-17", "18-24", "25-34", "35-44", "45+"], weights=[10, 35, 32, 16, 7], k=n_jogadores
        ),
        "tipo_conta":       random.choices(TIPOS_CONTA, weights=[60, 30, 10], k=n_jogadores),
        "rank_competitivo": random.choices(
            ["Bronze", "Prata", "Ouro", "Platina", "Diamante", "Mestre"],
            weights=[20, 25, 25, 15, 10, 5], k=n_jogadores,
        ),
    })

    # ── FatoSessao ───────────────────────────────────────────────────────────
    ids_jogo = random.choices(dim_jogo["id_jogo"].tolist(), k=n)
    plataformas_jogo = dim_jogo.set_index("id_jogo")["plataformas"]
    plataforma_sessao = [random.choice(plataformas_jogo.loc[j].split(", ")) for j in ids_jogo]

    tipo_evento = random.choices(TIPOS_EVENTO, weights=[45, 35, 10, 10], k=n)
    gastou_loja = rng.random(n) < 0.22  # ~22% das sessões geram compra in-game

    fato = pd.DataFrame({
        "id_sessao":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_jogo":           ids_jogo,
        "id_jogador":        random.choices(dim_jogador["id_jogador"].tolist(), k=n),
        "plataforma":        plataforma_sessao,
        "tipo_evento":       tipo_evento,
        "duracao_min":       rng.integers(5, 180, n),
        "resultado":         random.choices(RESULTADOS, weights=[45, 45, 10], k=n),
        "kills":             rng.integers(0, 40, n),
        "mortes":            rng.integers(0, 40, n),
        "valor_gasto_loja":  (gastou_loja * rng.uniform(4.9, 249.9, n)).round(2),
        "moeda_virtual_ganha": rng.integers(0, 500, n),
        "premiacao_torneio": [
            round(rng.uniform(500, 50000), 2) if te == "Torneio Oficial" and random.random() < 0.15 else 0.0
            for te in tipo_evento
        ],
        "nota_experiencia":  rng.integers(1, 6, n),
    })

    return {
        "DimJogo":     dim_jogo,
        "DimJogador":  dim_jogador,
        "FatoSessao":  fato,
        "dCalendario": dcalendario(start, end),
    }
