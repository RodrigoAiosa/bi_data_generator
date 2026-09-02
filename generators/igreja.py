"""generators/igreja.py — Setor Igreja & Templos Religiosos."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

STATUS_MEMBRO       = ["Ativo", "Inativo", "Visitante"]
MINISTERIOS         = ["Louvor", "Jovens", "Ação Social", "Crianças (Kids)",
                        "Casais", "Evangelismo", "Intercessão", "Mídia"]
TIPOS_CONTRIBUICAO  = ["Dízimo", "Oferta", "Campanha", "Missões"]
FORMAS_PAGAMENTO     = ["Dinheiro", "Pix", "Cartão de Crédito", "Transferência"]
TIPOS_CULTO         = ["Culto Domingo Manhã", "Culto Domingo Noite", "Culto de Oração",
                        "Célula", "Evento Especial"]


def gerar_igreja(n, start, end):
    n = max(int(n), 1)

    n_membro = min(max(n // 5, 100), 8000)
    dim_membro = pd.DataFrame({
        "id_membro":         new_ids(n_membro),
        "nome":              fake_pool(fake, "name", n_membro),
        "idade":             rng.integers(5, 90, n_membro),
        "sexo":              random.choices(["F", "M"], k=n_membro),
        "tempo_membresia_anos": rng.integers(0, 40, n_membro),
        "status":            random.choices(STATUS_MEMBRO, weights=[65, 15, 20], k=n_membro),
    })

    n_ministerio = min(max(n // 300, len(MINISTERIOS)), len(MINISTERIOS) * 3)
    dim_ministerio = pd.DataFrame({
        "id_ministerio":     new_ids(n_ministerio),
        "nome_ministerio":   random.choices(MINISTERIOS, k=n_ministerio),
        "lider":             fake_pool(fake, "name", n_ministerio),
    })

    fato_dizimo = pd.DataFrame({
        "id_registro":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_membro":         random.choices(dim_membro["id_membro"].tolist(), k=n),
        "tipo":              random.choices(TIPOS_CONTRIBUICAO, weights=[55, 30, 10, 5], k=n),
        "valor":             rng.uniform(10, 1500, n).round(2),
        "forma_pagamento":   random.choices(FORMAS_PAGAMENTO, weights=[20, 45, 15, 20], k=n),
    })

    n_evento = int(n // 3) or 1
    fato_evento = pd.DataFrame({
        "id_participacao":   new_ids(n_evento),
        "id_data":           rand_dates(start, end, n_evento),
        "id_ministerio":     random.choices(dim_ministerio["id_ministerio"].tolist(), k=n_evento),
        "tipo_culto":        random.choices(TIPOS_CULTO, k=n_evento),
        "presencas":         rng.integers(10, 900, n_evento),
    })

    return {
        "DimMembro": dim_membro,
        "DimMinisterio": dim_ministerio,
        "FatoDizimo": fato_dizimo,
        "FatoEvento": fato_evento,
        "dCalendario": dcalendario(start, end),
    }
