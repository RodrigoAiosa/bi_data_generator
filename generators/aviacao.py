"""generators/aviacao.py — Setor Aviação Civil (Companhias Aéreas)."""

import random
from datetime import date

import pandas as pd

from .helpers import dcalendario, get_faker, new_ids, rand_dates, rng

MODELOS_AERONAVE = [
    ("Airbus A320",   180), ("Airbus A321",   220), ("Boeing 737-800", 189),
    ("Boeing 737 MAX 8", 178), ("Embraer E195", 118), ("ATR 72", 70),
]

AEROPORTOS = [
    ("GRU", "São Paulo",      "SP", "Internacional"),
    ("CGH", "São Paulo",      "SP", "Doméstico"),
    ("SDU", "Rio de Janeiro", "RJ", "Doméstico"),
    ("GIG", "Rio de Janeiro", "RJ", "Internacional"),
    ("BSB", "Brasília",       "DF", "Internacional"),
    ("CNF", "Belo Horizonte", "MG", "Internacional"),
    ("SSA", "Salvador",       "BA", "Internacional"),
    ("REC", "Recife",         "PE", "Internacional"),
    ("POA", "Porto Alegre",   "RS", "Internacional"),
    ("CWB", "Curitiba",       "PR", "Doméstico"),
    ("FOR", "Fortaleza",      "CE", "Internacional"),
    ("MAO", "Manaus",         "AM", "Internacional"),
    ("BEL", "Belém",          "PA", "Doméstico"),
    ("VCP", "Campinas",       "SP", "Internacional"),
]

CLASSES_CABINE = ["Econômica", "Econômica Premium", "Executiva", "Primeira Classe"]
STATUS_VOO = ["No Horário", "Atrasado", "Cancelado", "Antecipado"]
MOTIVOS_ATRASO = [
    "Condições climáticas", "Tráfego aéreo / slot", "Manutenção não programada",
    "Conexão de tripulação", "Atraso operacional em aeroporto anterior", "Sem atraso",
]
FORMAS_PAGAMENTO = ["Cartão de Crédito", "Boleto", "Pix", "Milhas", "Débito"]


def gerar_aviacao(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    fake = get_faker()

    n_aeronaves   = 60
    n_passageiros = min(n, 8000)

    # ── DimAeronave ──────────────────────────────────────────────────────────
    modelos = random.choices(MODELOS_AERONAVE, k=n_aeronaves)
    dim_aeronave = pd.DataFrame({
        "id_aeronave":       new_ids(n_aeronaves),
        "modelo":            [m[0] for m in modelos],
        "capacidade_assentos": [m[1] for m in modelos],
        "ano_fabricacao":    rng.integers(2005, 2024, n_aeronaves),
        "prefixo":           [f"PR-{rng.integers(1000,9999)}" for _ in range(n_aeronaves)],
    })

    # ── DimAeroporto ─────────────────────────────────────────────────────────
    dim_aeroporto = pd.DataFrame({
        "id_aeroporto": new_ids(len(AEROPORTOS)),
        "codigo_iata":  [a[0] for a in AEROPORTOS],
        "cidade":       [a[1] for a in AEROPORTOS],
        "uf":           [a[2] for a in AEROPORTOS],
        "tipo":         [a[3] for a in AEROPORTOS],
    })

    # ── DimPassageiro ────────────────────────────────────────────────────────
    dim_passageiro = pd.DataFrame({
        "id_passageiro":       new_ids(n_passageiros),
        "nome":                [fake.name() for _ in range(n_passageiros)],
        "cpf":                 [fake.cpf() for _ in range(n_passageiros)],
        "programa_fidelidade": random.choices([True, False], weights=[35, 65], k=n_passageiros),
        "categoria_fidelidade":random.choices(
            ["Nenhuma", "Prata", "Ouro", "Diamante"], weights=[65, 20, 10, 5], k=n_passageiros
        ),
    })

    # ── FatoBilhete ──────────────────────────────────────────────────────────
    ids_aeroporto = dim_aeroporto["id_aeroporto"].tolist()
    origem  = random.choices(ids_aeroporto, k=n)
    destino = []
    for o in origem:
        opcoes = [a for a in ids_aeroporto if a != o]
        destino.append(random.choice(opcoes))

    status = random.choices(STATUS_VOO, weights=[70, 18, 6, 6], k=n)
    atraso_min = [
        int(rng.integers(15, 240)) if s == "Atrasado" else (0 if s != "Antecipado" else -int(rng.integers(5, 20)))
        for s in status
    ]
    motivo_atraso = [
        random.choice(MOTIVOS_ATRASO[:-1]) if s == "Atrasado" else "Sem atraso"
        for s in status
    ]

    fato = pd.DataFrame({
        "id_bilhete":       new_ids(n),
        "id_data":          rand_dates(start, end, n),
        "numero_voo":       [f"AA{rng.integers(1000,9999)}" for _ in range(n)],
        "id_aeronave":      random.choices(dim_aeronave["id_aeronave"].tolist(), k=n),
        "id_aeroporto_origem":  origem,
        "id_aeroporto_destino": destino,
        "id_passageiro":    random.choices(dim_passageiro["id_passageiro"].tolist(), k=n),
        "classe_cabine":    random.choices(CLASSES_CABINE, weights=[70, 12, 15, 3], k=n),
        "distancia_km":     rng.integers(150, 4000, n),
        "duracao_min":      rng.integers(45, 420, n),
        "valor_passagem":   rng.uniform(180, 4500, n).round(2),
        "bagagem_despachada_kg": rng.uniform(0, 32, n).round(1),
        "status_voo":       status,
        "atraso_min":       atraso_min,
        "motivo_atraso":    motivo_atraso,
        "forma_pagamento":  random.choices(FORMAS_PAGAMENTO, weights=[45, 10, 30, 10, 5], k=n),
        "nota_satisfacao":  rng.integers(1, 11, n),
    })

    return {
        "DimAeronave":   dim_aeronave,
        "DimAeroporto":  dim_aeroporto,
        "DimPassageiro": dim_passageiro,
        "FatoBilhete":   fato,
        "dCalendario":   dcalendario(start, end),
    }
