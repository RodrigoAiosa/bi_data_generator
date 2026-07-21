"""generators/ensino_superior.py — Setor Ensino Superior (Universidades e Faculdades)."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

GRAUS = ["Bacharelado", "Licenciatura", "Tecnólogo", "Pós-graduação Lato Sensu", "Mestrado"]
AREAS = ["Exatas", "Humanas", "Saúde", "Biológicas", "Engenharias", "Negócios", "Linguagens"]
FORMA_INGRESSO = ["Vestibular", "ENEM", "Transferência", "Segunda Graduação", "Convênio Empresa"]
FINANCIAMENTO = ["Nenhum", "FIES", "Prouni", "Financiamento Próprio", "Bolsa Convênio"]
STATUS_MATRICULA = ["Ativo", "Trancado", "Formado", "Evadido"]
DISCIPLINAS = ["Cálculo I", "Algoritmos", "Contabilidade Geral", "Fisiologia", "Direito Civil",
                "Estatística", "Marketing", "Redes de Computadores", "Anatomia", "Metodologia Científica"]


def gerar_ensino_superior(n, start, end):
    n = max(int(n), 1)

    n_curso = min(max(n // 150, 8), 80)
    dim_curso = pd.DataFrame({
        "id_curso":          new_ids(n_curso),
        "nome":              [f"{random.choice(['Administração','Direito','Engenharia Civil','Psicologia','Enfermagem','Ciência da Computação','Pedagogia','Arquitetura','Medicina Veterinária','Contabilidade'])}" for _ in range(n_curso)],
        "grau":              random.choices(GRAUS, weights=[45, 15, 20, 12, 8], k=n_curso),
        "area":              random.choices(AREAS, k=n_curso),
        "duracao_semestres": random.choices([4, 6, 8, 10], weights=[15, 25, 45, 15], k=n_curso),
        "mensalidade":       rng.uniform(300, 3500, n_curso).round(2),
    })

    n_aluno = min(max(n // 3, 200), 15000)
    dim_aluno = pd.DataFrame({
        "id_aluno":          new_ids(n_aluno),
        "nome":              [fake.name() for _ in range(n_aluno)],
        "sexo":              random.choices(["F", "M"], k=n_aluno),
        "idade":             rng.integers(17, 55, n_aluno),
        "uf":                [fake.state_abbr() for _ in range(n_aluno)],
        "cidade":            [fake.city() for _ in range(n_aluno)],
        "forma_ingresso":    random.choices(FORMA_INGRESSO, weights=[35, 40, 10, 8, 7], k=n_aluno),
        "bolsista":          random.choices([True, False], weights=[25, 75], k=n_aluno),
    })

    status_matricula = random.choices(STATUS_MATRICULA, weights=[65, 8, 18, 9], k=n)
    fato_matricula = pd.DataFrame({
        "id_matricula":      new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_aluno":          random.choices(dim_aluno["id_aluno"].tolist(), k=n),
        "id_curso":          random.choices(dim_curso["id_curso"].tolist(), k=n),
        "semestre_atual":    rng.integers(1, 10, n),
        "status":            status_matricula,
        "cr_periodo":        rng.uniform(4.0, 10.0, n).round(2),
        "financiamento":     random.choices(FINANCIAMENTO, weights=[40, 25, 20, 10, 5], k=n),
        "evadido":           [s == "Evadido" for s in status_matricula],
    })

    n_disc = int(n * 2.5)
    aprovado = random.choices([True, False], weights=[82, 18], k=n_disc)
    fato_disciplina = pd.DataFrame({
        "id_disciplina_fato": new_ids(n_disc),
        "id_data":           rand_dates(start, end, n_disc),
        "id_aluno":          random.choices(dim_aluno["id_aluno"].tolist(), k=n_disc),
        "id_curso":          random.choices(dim_curso["id_curso"].tolist(), k=n_disc),
        "nome_disciplina":   random.choices(DISCIPLINAS, k=n_disc),
        "nota":              rng.uniform(0, 10, n_disc).round(1),
        "frequencia_pct":    rng.uniform(40, 100, n_disc).round(1),
        "aprovado":          aprovado,
    })

    return {
        "DimCurso": dim_curso,
        "DimAluno": dim_aluno,
        "FatoMatricula": fato_matricula,
        "FatoDisciplina": fato_disciplina,
        "dCalendario": dcalendario(start, end),
    }
