"""generators/educacao.py — Setor Educação."""

import random
from datetime import date

import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")


def gerar_educacao(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_alunos      = min(n, 5000)
    n_cursos      = 60
    n_instrutores = 40

    dim_curso = pd.DataFrame({
        "id_curso":    new_ids(n_cursos),
        "nome":        [f"Curso de {fake.word().capitalize()}" for _ in range(n_cursos)],
        "modalidade":  random.choices(["EAD","Presencial","Híbrido"], k=n_cursos),
        "area":        random.choices(["TI","Saúde","Gestão","Direito","Engenharia","Design"], k=n_cursos),
        "carga_horas": random.choices([40,60,80,120,200,360,400], k=n_cursos),
        "valor":       rng.uniform(200, 5000, n_cursos).round(2),
    })

    dim_aluno = pd.DataFrame({
        "id_aluno":     new_ids(n_alunos),
        "nome":         [fake.name()  for _ in range(n_alunos)],
        "cpf":          [fake.cpf()   for _ in range(n_alunos)],
        "email":        [fake.email() for _ in range(n_alunos)],
        "sexo":         random.choices(["M","F","Outro"], weights=[47,50,3], k=n_alunos),
        "uf":           random.choices(["SP","RJ","MG","RS","PR","BA","CE"], k=n_alunos),
        "faixa_etaria": random.choices(["15-17","18-24","25-34","35-44","45+"], k=n_alunos),
    })

    dim_instrutor = pd.DataFrame({
        "id_instrutor": new_ids(n_instrutores),
        "nome":         [fake.name() for _ in range(n_instrutores)],
        "titulacao":    random.choices(["Graduado","Especialista","Mestre","Doutor"], k=n_instrutores),
        "area":         random.choices(["TI","Saúde","Gestão","Direito","Engenharia","Design"], k=n_instrutores),
    })

    fato = pd.DataFrame({
        "id_matricula":    new_ids(n),
        "id_data":         rand_dates(start, end, n),
        "id_aluno":        random.choices(dim_aluno["id_aluno"].tolist(), k=n),
        "id_curso":        random.choices(dim_curso["id_curso"].tolist(), k=n),
        "id_instrutor":    random.choices(dim_instrutor["id_instrutor"].tolist(), k=n),
        "forma_pagamento": random.choices(["Boleto","Cartão","PIX","Financiamento"], k=n),
        "valor_pago":      rng.uniform(200, 5000, n).round(2),
        "nota_final":      rng.uniform(0, 10, n).round(1),
        "concluiu":        random.choices([1, 0], weights=[65, 35], k=n),
        "status":          random.choices(["Ativo","Concluído","Trancado","Cancelado"],
                                          weights=[40,35,15,10], k=n),
    })

    return {
        "DimCurso":      dim_curso,
        "DimAluno":      dim_aluno,
        "DimInstrutor":  dim_instrutor,
        "FatoMatricula": fato,
        "dCalendario":   dcalendario(start, end),
    }
