"""generators/academia.py — Setor Academia & Fitness."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

PLANOS        = ["Mensal", "Trimestral", "Semestral", "Anual", "Diária Avulsa"]
OBJETIVOS     = ["Emagrecimento", "Hipertrofia", "Condicionamento", "Reabilitação",
                  "Performance Esportiva", "Bem-estar"]
MODALIDADES   = ["Musculação", "Funcional", "Spinning", "Crossfit", "Pilates",
                  "Natação", "Yoga", "Lutas", "Dança", "HIIT"]
ESPECIALIDADES_PT = ["Musculação", "Funcional", "Emagrecimento", "Reabilitação",
                      "Crossfit", "Idosos", "Nutrição Esportiva"]
STATUS_PAGAMENTO = ["Pago", "Pendente", "Atrasado", "Cancelado"]


def gerar_academia(n, start, end):
    n = max(int(n), 1)

    n_instrutor = min(max(n // 100, 6), 90)
    dim_instrutor = pd.DataFrame({
        "id_instrutor":      new_ids(n_instrutor),
        "nome":              [fake.name() for _ in range(n_instrutor)],
        "especialidade":     random.choices(ESPECIALIDADES_PT, k=n_instrutor),
        "anos_experiencia":  rng.integers(1, 25, n_instrutor),
        "avaliacao":         rng.uniform(3.5, 5.0, n_instrutor).round(1),
        "ativo":             random.choices([True, False], weights=[90, 10], k=n_instrutor),
    })

    n_aluno = min(max(n // 5, 150), 10000)
    dim_aluno = pd.DataFrame({
        "id_aluno":          new_ids(n_aluno),
        "nome":              [fake.name() for _ in range(n_aluno)],
        "idade":             rng.integers(14, 80, n_aluno),
        "sexo":              random.choices(["F", "M"], k=n_aluno),
        "plano":             random.choices(PLANOS, weights=[40, 20, 15, 15, 10], k=n_aluno),
        "objetivo":          random.choices(OBJETIVOS, k=n_aluno),
        "uf":                [fake.state_abbr() for _ in range(n_aluno)],
        "cidade":            [fake.city() for _ in range(n_aluno)],
        "ativo":             random.choices([True, False], weights=[78, 22], k=n_aluno),
    })

    fato_checkin = pd.DataFrame({
        "id_checkin":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_aluno":          random.choices(dim_aluno["id_aluno"].tolist(), k=n),
        "modalidade":        random.choices(MODALIDADES, k=n),
        "unidade":           random.choices([f"Unidade {c}" for c in ["Centro","Norte","Sul","Shopping","Praia"]], k=n),
        "horario":           random.choices(["Manhã", "Tarde", "Noite"], weights=[35,30,35], k=n),
        "duracao_min":       random.choices([30, 45, 60, 75, 90, 120], k=n),
        "usou_personal":     random.choices([True, False], weights=[22, 78], k=n),
    })

    n_pag = int(n_aluno * 1.4)
    valor_plano = rng.uniform(59.9, 349.9, n_pag).round(2)
    status_pag = random.choices(STATUS_PAGAMENTO, weights=[75, 12, 9, 4], k=n_pag)
    fato_pagamento = pd.DataFrame({
        "id_pagamento":      new_ids(n_pag),
        "id_data":           rand_dates(start, end, n_pag),
        "id_aluno":          random.choices(dim_aluno["id_aluno"].tolist(), k=n_pag),
        "valor_plano":       valor_plano,
        "desconto_pct":      rng.uniform(0, 30, n_pag).round(1),
        "status_pagamento":  status_pag,
        "forma_pagamento":   random.choices(["Cartão Crédito", "Cartão Débito", "Pix", "Boleto"], k=n_pag),
        "inadimplente":      [s in ("Pendente", "Atrasado") for s in status_pag],
    })

    n_aval = int(n_aluno * 0.5)
    fato_avaliacao = pd.DataFrame({
        "id_avaliacao":      new_ids(n_aval),
        "id_data":           rand_dates(start, end, n_aval),
        "id_aluno":          random.choices(dim_aluno["id_aluno"].tolist(), k=n_aval),
        "id_instrutor":      random.choices(dim_instrutor["id_instrutor"].tolist(), k=n_aval),
        "peso_kg":           rng.uniform(45, 130, n_aval).round(1),
        "percentual_gordura": rng.uniform(8, 40, n_aval).round(1),
        "massa_magra_kg":    rng.uniform(30, 90, n_aval).round(1),
        "imc":               rng.uniform(17, 38, n_aval).round(1),
    })

    return {
        "DimInstrutor": dim_instrutor,
        "DimAluno": dim_aluno,
        "FatoCheckin": fato_checkin,
        "FatoPagamento": fato_pagamento,
        "FatoAvaliacaoFisica": fato_avaliacao,
        "dCalendario": dcalendario(start, end),
    }
