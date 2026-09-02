"""generators/escola_tecnica.py — Setor Escola Técnica & Profissionalizante."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

NOMES_CURSO = ["Mecatrônica", "Enfermagem", "TI & Redes", "Administração", "Eletrotécnica", "Segurança do Trabalho"]


def gerar_escola_tecnica(n, start, end):
    n = max(int(n), 1)

    n_unidade = min(max(n // 200, 4), 60)
    dim_unidade = pd.DataFrame({
        "id_unidade":        new_ids(n_unidade),
        "cidade":            fake_pool(fake, "city", n_unidade),
        "uf":                fake_pool(fake, "state_abbr", n_unidade),
    })

    n_curso = min(max(n // 40, 15), 800)
    dim_curso = pd.DataFrame({
        "id_curso":          new_ids(n_curso),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n_curso),
        "nome_curso":        random.choices(NOMES_CURSO, k=n_curso),
        "carga_horaria":     random.choices([400, 800, 1200, 1600], k=n_curso),
    })

    fato_matricula = pd.DataFrame({
        "id_matricula":      new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_curso":          random.choices(dim_curso["id_curso"].tolist(), k=n),
        "aluno":             fake_pool(fake, "name", n),
        "status":            random.choices(["Ativa", "Concluída", "Evadida"], weights=[45, 40, 15], k=n),
    })

    n_estagio = int(n * 0.4)
    fato_estagio = pd.DataFrame({
        "id_estagio":        new_ids(n_estagio),
        "id_data":           rand_dates(start, end, n_estagio),
        "id_matricula":      random.choices(fato_matricula["id_matricula"].tolist(), k=n_estagio),
        "empresa":           fake_pool(fake, "company", n_estagio),
        "horas_cumpridas":   rng.integers(20, 800, n_estagio),
    })

    return {
        "DimUnidade": dim_unidade,
        "DimCurso": dim_curso,
        "FatoMatricula": fato_matricula,
        "FatoEstagio": fato_estagio,
        "dCalendario": dcalendario(start, end),
    }
