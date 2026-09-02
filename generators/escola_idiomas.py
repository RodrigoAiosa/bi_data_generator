"""generators/escola_idiomas.py — Setor Escola de Idiomas."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

IDIOMAS = ["Inglês", "Espanhol", "Francês", "Alemão", "Italiano", "Mandarim"]
NIVEIS = ["Iniciante", "Básico", "Intermediário", "Avançado", "Fluente"]
HABILIDADES = ["Listening", "Speaking", "Reading", "Writing"]
STATUS_MATRICULA = ["Ativa", "Trancada", "Concluída", "Cancelada"]


def gerar_escola_idiomas(n, start, end):
    n = max(int(n), 1)

    n_prof = min(max(n // 70, 6), 90)
    dim_professor = pd.DataFrame({
        "id_professor":      new_ids(n_prof),
        "nome":              fake_pool(fake, "name", n_prof),
        "idioma_principal":  random.choices(IDIOMAS, weights=[50, 20, 10, 8, 7, 5], k=n_prof),
        "anos_experiencia":  rng.integers(1, 20, n_prof),
    })

    n_aluno = min(max(n // 5, 150), 9000)
    dim_aluno = pd.DataFrame({
        "id_aluno":          new_ids(n_aluno),
        "nome":              fake_pool(fake, "name", n_aluno),
        "idade":             rng.integers(6, 70, n_aluno),
        "nivel_atual":       random.choices(NIVEIS, k=n_aluno),
    })

    dim_curso = pd.DataFrame({
        "id_curso":          new_ids(len(IDIOMAS) * len(NIVEIS)),
        "idioma":            [i for i in IDIOMAS for _ in NIVEIS],
        "nivel":             NIVEIS * len(IDIOMAS),
    })

    n_mat = int(n_aluno * 1.3)
    fato_matricula = pd.DataFrame({
        "id_matricula":      new_ids(n_mat),
        "id_data":           rand_dates(start, end, n_mat),
        "id_aluno":          random.choices(dim_aluno["id_aluno"].tolist(), k=n_mat),
        "id_curso":          random.choices(dim_curso["id_curso"].tolist(), k=n_mat),
        "id_professor":      random.choices(dim_professor["id_professor"].tolist(), k=n_mat),
        "valor":             rng.uniform(150, 650, n_mat).round(2),
        "status":            random.choices(STATUS_MATRICULA, weights=[55, 10, 28, 7], k=n_mat),
    })

    fato_avaliacao = pd.DataFrame({
        "id_avaliacao":      new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_aluno":          random.choices(dim_aluno["id_aluno"].tolist(), k=n),
        "habilidade":        random.choices(HABILIDADES, k=n),
        "nota_proficiencia": rng.uniform(0, 10, n).round(1),
    })

    return {
        "DimProfessor": dim_professor,
        "DimAluno": dim_aluno,
        "DimCurso": dim_curso,
        "FatoMatricula": fato_matricula,
        "FatoAvaliacao": fato_avaliacao,
        "dCalendario": dcalendario(start, end),
    }
