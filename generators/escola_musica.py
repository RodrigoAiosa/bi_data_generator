"""generators/escola_musica.py — Setor Escola de Música."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

INSTRUMENTOS = ["Violão", "Piano", "Bateria", "Violino", "Canto", "Guitarra", "Flauta", "Baixo"]
CATEGORIAS_INSTRUMENTO = ["Cordas", "Teclas", "Percussão", "Cordas", "Voz", "Cordas", "Sopro", "Cordas"]
STATUS_MATRICULA = ["Ativa", "Trancada", "Concluída", "Cancelada"]


def gerar_escola_musica(n, start, end):
    n = max(int(n), 1)

    n_prof = min(max(n // 60, 6), 80)
    dim_professor = pd.DataFrame({
        "id_professor":          new_ids(n_prof),
        "nome":                  fake_pool(fake, "name", n_prof),
        "instrumento_principal": random.choices(INSTRUMENTOS, k=n_prof),
        "anos_experiencia":      rng.integers(1, 25, n_prof),
    })

    n_aluno = min(max(n // 4, 100), 8000)
    dim_aluno = pd.DataFrame({
        "id_aluno":          new_ids(n_aluno),
        "nome":              fake_pool(fake, "name", n_aluno),
        "idade":             rng.integers(5, 75, n_aluno),
    })

    dim_instrumento = pd.DataFrame({
        "id_instrumento":    new_ids(len(INSTRUMENTOS)),
        "instrumento":       INSTRUMENTOS,
        "categoria":         CATEGORIAS_INSTRUMENTO,
    })

    fato_aula = pd.DataFrame({
        "id_aula":           new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_aluno":          random.choices(dim_aluno["id_aluno"].tolist(), k=n),
        "id_professor":      random.choices(dim_professor["id_professor"].tolist(), k=n),
        "id_instrumento":    random.choices(dim_instrumento["id_instrumento"].tolist(), k=n),
        "duracao_min":       random.choices([30, 45, 60], weights=[30, 40, 30], k=n),
        "presenca":          random.choices([True, False], weights=[88, 12], k=n),
    })

    n_mat = int(n_aluno * 1.2)
    fato_matricula = pd.DataFrame({
        "id_matricula":      new_ids(n_mat),
        "id_data":           rand_dates(start, end, n_mat),
        "id_aluno":          random.choices(dim_aluno["id_aluno"].tolist(), k=n_mat),
        "id_instrumento":    random.choices(dim_instrumento["id_instrumento"].tolist(), k=n_mat),
        "valor_mensalidade": rng.uniform(120, 550, n_mat).round(2),
        "status":            random.choices(STATUS_MATRICULA, weights=[60, 8, 22, 10], k=n_mat),
    })

    return {
        "DimProfessor": dim_professor,
        "DimAluno": dim_aluno,
        "DimInstrumento": dim_instrumento,
        "FatoAula": fato_aula,
        "FatoMatricula": fato_matricula,
        "dCalendario": dcalendario(start, end),
    }
