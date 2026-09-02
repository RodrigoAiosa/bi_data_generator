"""generators/autoescola.py — Setor Autoescola."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

CATEGORIAS_CNH = ["A", "B", "AB", "C", "D", "E"]


def gerar_autoescola(n, start, end):
    n = max(int(n), 1)

    n_unidade = min(max(n // 200, 3), 40)
    dim_unidade = pd.DataFrame({
        "id_unidade":        new_ids(n_unidade),
        "cidade":            fake_pool(fake, "city", n_unidade),
        "uf":                fake_pool(fake, "state_abbr", n_unidade),
    })

    n_instrutor = min(max(n // 40, 10), 800)
    dim_instrutor = pd.DataFrame({
        "id_instrutor":      new_ids(n_instrutor),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n_instrutor),
        "nome":              fake_pool(fake, "name", n_instrutor),
        "categoria_habilitacao": random.choices(CATEGORIAS_CNH, k=n_instrutor),
    })

    fato_aula = pd.DataFrame({
        "id_aula":           new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_instrutor":      random.choices(dim_instrutor["id_instrutor"].tolist(), k=n),
        "tipo_aula":         random.choices(["Teórica", "Prática"], weights=[30, 70], k=n),
        "aluno":             fake_pool(fake, "name", n),
        "duracao_min":       random.choices([50, 60, 90], k=n),
        "valor":             rng.uniform(60, 220, n).round(2),
    })

    n_exame = int(n * 0.3)
    aprovado = random.choices([True, False], weights=[70, 30], k=n_exame)
    fato_exame = pd.DataFrame({
        "id_exame":          new_ids(n_exame),
        "id_data":           rand_dates(start, end, n_exame),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n_exame),
        "tipo_exame":        random.choices(["Teórico", "Prático"], k=n_exame),
        "aprovado":          aprovado,
        "tentativa":         rng.integers(1, 4, n_exame),
    })

    return {
        "DimUnidade": dim_unidade,
        "DimInstrutor": dim_instrutor,
        "FatoAula": fato_aula,
        "FatoExame": fato_exame,
        "dCalendario": dcalendario(start, end),
    }
