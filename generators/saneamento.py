"""generators/saneamento.py — Setor Saneamento & Água."""

import random
from datetime import date

import pandas as pd

from .helpers import dcalendario, get_faker, new_ids, rand_dates, rng

UFS = ["SP", "RJ", "MG", "RS", "PR", "BA", "SC", "PE", "CE", "GO", "AM", "PA"]
TIPOS_LIGACAO = ["Residencial", "Comercial", "Industrial", "Público"]
STATUS_PAGAMENTO = ["Pago", "Em Aberto", "Vencido", "Parcelado"]
TIPOS_ESTACAO = ["ETA - Estação de Tratamento de Água", "ETE - Estação de Tratamento de Esgoto"]


def gerar_saneamento(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    fake = get_faker()

    n_estacoes = 40
    n_imoveis  = min(n, 9000)

    # ── DimEstacao ───────────────────────────────────────────────────────────
    dim_estacao = pd.DataFrame({
        "id_estacao":          new_ids(n_estacoes),
        "nome":                [f"Estação {fake.city()}" for _ in range(n_estacoes)],
        "tipo":                random.choices(TIPOS_ESTACAO, k=n_estacoes),
        "uf":                  random.choices(UFS, k=n_estacoes),
        "capacidade_m3_dia":   rng.integers(500, 50000, n_estacoes),
        "ano_operacao":        rng.integers(1970, 2023, n_estacoes),
    })

    # ── DimImovel ────────────────────────────────────────────────────────────
    dim_imovel = pd.DataFrame({
        "id_imovel":       new_ids(n_imoveis),
        "tipo_ligacao":    random.choices(TIPOS_LIGACAO, weights=[70, 20, 7, 3], k=n_imoveis),
        "uf":              random.choices(UFS, k=n_imoveis),
        "cidade":          [fake.city() for _ in range(n_imoveis)],
        "possui_esgoto":   random.choices([True, False], weights=[78, 22], k=n_imoveis),
        "hidrometro_digital": random.choices([True, False], weights=[35, 65], k=n_imoveis),
    })

    # ── FatoConsumo (leituras mensais/faturas) ──────────────────────────────
    ids_imovel = random.choices(dim_imovel["id_imovel"].tolist(), k=n)
    imovel_map = dim_imovel.set_index("id_imovel")[["tipo_ligacao", "uf"]]
    tipo_ligacao_evento = imovel_map.loc[ids_imovel, "tipo_ligacao"].to_numpy()

    base_consumo = {
        "Residencial": (5, 25), "Comercial": (10, 80),
        "Industrial": (50, 900), "Público": (20, 300),
    }
    consumo_agua_m3 = [round(rng.uniform(*base_consumo[t]), 2) for t in tipo_ligacao_evento]
    volume_esgoto_m3 = [round(c * rng.uniform(0.7, 0.95), 2) for c in consumo_agua_m3]

    tarifa_m3 = rng.uniform(3.5, 12.9, n).round(2)
    valor_fatura = [round(c * t * rng.uniform(1.0, 1.3), 2) for c, t in zip(consumo_agua_m3, tarifa_m3)]  # inclui taxa de esgoto/serviço

    fato = pd.DataFrame({
        "id_leitura":         new_ids(n),
        "id_data":            rand_dates(start, end, n),
        "id_imovel":          ids_imovel,
        "id_estacao":         random.choices(dim_estacao["id_estacao"].tolist(), k=n),
        "tipo_ligacao":       tipo_ligacao_evento,
        "consumo_agua_m3":    consumo_agua_m3,
        "volume_esgoto_m3":   volume_esgoto_m3,
        "tarifa_m3":          tarifa_m3,
        "valor_fatura":       valor_fatura,
        "status_pagamento":   random.choices(STATUS_PAGAMENTO, weights=[68, 15, 12, 5], k=n),
        "indice_perdas_pct":  rng.uniform(8, 42, n).round(2),
        "qualidade_agua_score": rng.integers(60, 100, n),
    })

    return {
        "DimEstacao":  dim_estacao,
        "DimImovel":   dim_imovel,
        "FatoConsumo": fato,
        "dCalendario": dcalendario(start, end),
    }
