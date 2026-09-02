"""generators/creche.py — Setor Creche & Educação Infantil."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

FAIXAS_ETARIAS = ["Berçário", "Maternal", "Jardim I", "Jardim II"]
TURNOS = ["Manhã", "Tarde", "Integral"]


def gerar_creche(n, start, end):
    n = max(int(n), 1)

    n_unidade = min(max(n // 200, 4), 60)
    dim_unidade = pd.DataFrame({
        "id_unidade":        new_ids(n_unidade),
        "cidade":            fake_pool(fake, "city", n_unidade),
        "uf":                fake_pool(fake, "state_abbr", n_unidade),
        "capacidade":        rng.integers(30, 400, n_unidade),
    })

    n_turma = min(max(n // 20, 20), 2000)
    dim_turma = pd.DataFrame({
        "id_turma":          new_ids(n_turma),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n_turma),
        "faixa_etaria":      random.choices(FAIXAS_ETARIAS, k=n_turma),
        "turno":             random.choices(TURNOS, weights=[30, 25, 45], k=n_turma),
    })

    fato_matricula = pd.DataFrame({
        "id_matricula":      new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_turma":          random.choices(dim_turma["id_turma"].tolist(), k=n),
        "crianca":           fake_pool(fake, "first_name", n),
        "status":            random.choices(["Ativa", "Trancada", "Cancelada"], weights=[85, 8, 7], k=n),
    })

    n_mens = n * 6
    fato_mensalidade = pd.DataFrame({
        "id_mensalidade":    new_ids(n_mens),
        "id_data":           rand_dates(start, end, n_mens),
        "id_matricula":      random.choices(fato_matricula["id_matricula"].tolist(), k=n_mens),
        "valor":             rng.uniform(400, 3500, n_mens).round(2),
        "status_pagamento":  random.choices(["Pago", "Atrasado"], weights=[90, 10], k=n_mens),
    })

    return {
        "DimUnidade": dim_unidade,
        "DimTurma": dim_turma,
        "FatoMatricula": fato_matricula,
        "FatoMensalidade": fato_mensalidade,
        "dCalendario": dcalendario(start, end),
    }
