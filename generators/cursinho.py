"""generators/cursinho.py — Setor Cursinho Preparatório."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CURSOS = ["Vestibular", "ENEM", "Concurso Público", "Concurso Militar", "OAB"]
DURACOES_CURSO = [12, 8, 10, 10, 6]
DISCIPLINAS = ["Matemática", "Português", "Física", "Química", "Biologia", "História", "Geografia", "Redação"]
STATUS_MATRICULA = ["Ativa", "Trancada", "Concluída", "Cancelada"]


def gerar_cursinho(n, start, end):
    n = max(int(n), 1)

    n_prof = min(max(n // 60, 8), 100)
    dim_professor = pd.DataFrame({
        "id_professor":      new_ids(n_prof),
        "nome":              [fake.name() for _ in range(n_prof)],
        "disciplina":        random.choices(DISCIPLINAS, k=n_prof),
        "avaliacao":         rng.uniform(3.5, 5.0, n_prof).round(1),
    })

    n_aluno = min(max(n // 4, 100), 12000)
    dim_aluno = pd.DataFrame({
        "id_aluno":          new_ids(n_aluno),
        "nome":              [fake.name() for _ in range(n_aluno)],
        "idade":             rng.integers(15, 45, n_aluno),
        "uf":                [fake.state_abbr() for _ in range(n_aluno)],
    })

    dim_curso = pd.DataFrame({
        "id_curso":          new_ids(len(CURSOS)),
        "curso":             CURSOS,
        "duracao_meses":     DURACOES_CURSO,
    })

    n_mat = int(n_aluno * 1.1)
    fato_matricula = pd.DataFrame({
        "id_matricula":      new_ids(n_mat),
        "id_data":           rand_dates(start, end, n_mat),
        "id_aluno":          random.choices(dim_aluno["id_aluno"].tolist(), k=n_mat),
        "id_curso":          random.choices(dim_curso["id_curso"].tolist(), k=n_mat),
        "valor":             rng.uniform(199, 899, n_mat).round(2),
        "status":            random.choices(STATUS_MATRICULA, weights=[60, 8, 25, 7], k=n_mat),
    })

    fato_simulado = pd.DataFrame({
        "id_simulado":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_aluno":          random.choices(dim_aluno["id_aluno"].tolist(), k=n),
        "id_professor":      random.choices(dim_professor["id_professor"].tolist(), k=n),
        "nota":              rng.uniform(300, 1000, n).round(1),
        "acertos_pct":       rng.uniform(20, 98, n).round(1),
    })

    return {
        "DimProfessor": dim_professor,
        "DimAluno": dim_aluno,
        "DimCurso": dim_curso,
        "FatoMatricula": fato_matricula,
        "FatoSimulado": fato_simulado,
        "dCalendario": dcalendario(start, end),
    }
