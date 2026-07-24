"""
generators/concept_drift.py: injeta deriva temporal (concept drift) genérica
em qualquer tabela fato, funcionando para qualquer um dos 100 setores.

Diferente do "Modo Anomalias" (mudanças abruptas/pontuais), a deriva aqui é
GRADUAL: uma categoria de uma coluna categórica vai ganhando participação aos
poucos ao longo do período gerado, sem nenhum evento único que explique. É
bom para praticar detecção de tendência/mudança de comportamento, não só outlier.
"""
import random
import numpy as np
import pandas as pd

_PRIORIDADE_COLUNA = ["canal", "categoria", "segmento", "status", "forma_pagamento", "tipo", "plano"]


def injetar_concept_drift(tabelas: dict) -> tuple[dict, list[dict]]:
    tabelas = {k: v.copy() for k, v in tabelas.items()}
    gabarito: list[dict] = []

    fato_key = next((k for k in tabelas if k.startswith("Fato")), None)
    if fato_key is None:
        return tabelas, gabarito

    fato = tabelas[fato_key]
    date_cols = [c for c in fato.columns if "data" in c.lower()]
    if not date_cols:
        return tabelas, gabarito
    date_col = date_cols[0]

    try:
        fato[date_col] = pd.to_datetime(fato[date_col], errors="coerce")
    except Exception:
        return tabelas, gabarito

    cat_cols = [
        c for c in fato.select_dtypes(include="object").columns
        if 2 <= fato[c].nunique() <= 6
    ]
    if not cat_cols:
        tabelas[fato_key] = fato
        return tabelas, gabarito

    col_drift = next(
        (c for c in cat_cols if any(p in c.lower() for p in _PRIORIDADE_COLUNA)),
        cat_cols[0],
    )

    categorias = fato[col_drift].dropna().unique().tolist()
    if len(categorias) < 2:
        tabelas[fato_key] = fato
        return tabelas, gabarito

    cat_ganha = random.choice(categorias)
    cat_perde = random.choice([c for c in categorias if c != cat_ganha])

    datas_validas = fato[date_col].dropna()
    if datas_validas.empty:
        tabelas[fato_key] = fato
        return tabelas, gabarito

    data_min, data_max = datas_validas.min(), datas_validas.max()
    intervalo_dias = max((data_max - data_min).days, 1)

    posicao = ((fato[date_col] - data_min).dt.days.clip(lower=0) / intervalo_dias).fillna(0)

    # Probabilidade de "migrar" para cat_ganha cresce de 5% (início) até 65% (fim)
    prob_flip = 0.05 + posicao * 0.60
    candidatos = fato[col_drift] == cat_perde
    sorteio = np.random.uniform(0, 1, len(fato))
    flip_mask = candidatos & (sorteio < prob_flip)
    fato.loc[flip_mask, col_drift] = cat_ganha

    inicio_mask = posicao <= 0.1
    fim_mask = posicao >= 0.9
    participacao_inicial = round((fato.loc[inicio_mask, col_drift] == cat_ganha).mean() * 100, 1) if inicio_mask.any() else 0.0
    participacao_final = round((fato.loc[fim_mask, col_drift] == cat_ganha).mean() * 100, 1) if fim_mask.any() else 0.0
    inicio_fmt = f"{participacao_inicial}".replace(".", ",")
    final_fmt = f"{participacao_final}".replace(".", ",")

    gabarito.append({
        "tipo": "Deriva Temporal (Concept Drift)",
        "localizacao": f"Coluna '{col_drift}' em {fato_key}",
        "detalhe": (
            f"A categoria '{cat_ganha}' ganhou participação gradualmente ao longo do período "
            f"(de aproximadamente {inicio_fmt}% no início para {final_fmt}% no final), "
            f"tomando espaço principalmente de '{cat_perde}'. A mudança é progressiva, mês a mês, "
            f"não um evento único e pontual como nas anomalias."
        ),
    })

    tabelas[fato_key] = fato
    return tabelas, gabarito
