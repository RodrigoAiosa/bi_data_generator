"""generators/transporte_escolar.py — Setor Transporte Escolar."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

TIPOS_VEICULO = ["Van", "Micro-ônibus", "Ônibus", "Kombi Adaptada"]
TURNOS = ["Manhã", "Tarde", "Integral"]
STATUS_PAGAMENTO = ["Pago", "Pendente", "Atrasado", "Cancelado"]
NIVEIS_ENSINO = ["Educação Infantil", "Fundamental I", "Fundamental II", "Ensino Médio"]


def gerar_transporte_escolar(n, start, end):
    n = max(int(n), 1)

    n_veiculo = min(max(n // 250, 4), 90)
    dim_veiculo = pd.DataFrame({
        "id_veiculo":        new_ids(n_veiculo),
        "placa":             fake_pool(fake, "license_plate", n_veiculo),
        "tipo":              random.choices(TIPOS_VEICULO, weights=[45, 30, 15, 10], k=n_veiculo),
        "capacidade_lugares": rng.integers(8, 45, n_veiculo),
        "ano_fabricacao":    rng.integers(2008, 2025, n_veiculo),
    })

    n_motorista = min(max(n // 300, 4), 100)
    dim_motorista = pd.DataFrame({
        "id_motorista":      new_ids(n_motorista),
        "nome":              fake_pool(fake, "name", n_motorista),
        "anos_experiencia":  rng.integers(1, 30, n_motorista),
        "possui_curso_transporte_escolar": random.choices([True, False], weights=[95, 5], k=n_motorista),
    })

    n_aluno = min(max(n // 4, 100), 15000)
    dim_aluno = pd.DataFrame({
        "id_aluno":          new_ids(n_aluno),
        "nome":              fake_pool(fake, "name", n_aluno),
        "nivel_ensino":      random.choices(NIVEIS_ENSINO, weights=[20, 35, 30, 15], k=n_aluno),
        "turno":             random.choices(TURNOS, weights=[45, 40, 15], k=n_aluno),
        "bairro":            fake_pool(fake, "street_name", n_aluno),
        "ativo":             random.choices([True, False], weights=[90, 10], k=n_aluno),
    })

    fato_rota = pd.DataFrame({
        "id_rota":           new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_veiculo":        random.choices(dim_veiculo["id_veiculo"].tolist(), k=n),
        "id_motorista":      random.choices(dim_motorista["id_motorista"].tolist(), k=n),
        "turno":             random.choices(TURNOS, weights=[45, 40, 15], k=n),
        "ocupacao_pct":      rng.uniform(40, 100, n).round(1),
        "pontualidade_min":  rng.integers(-10, 25, n),
        "km_percorridos":    rng.uniform(3, 45, n).round(1),
        "ocorrencia":        random.choices([True, False], weights=[6, 94], k=n),
    })

    n_pag = int(n_aluno * 1.1)
    status_pag = random.choices(STATUS_PAGAMENTO, weights=[78, 12, 7, 3], k=n_pag)
    fato_mensalidade = pd.DataFrame({
        "id_mensalidade":    new_ids(n_pag),
        "id_data":           rand_dates(start, end, n_pag),
        "id_aluno":          random.choices(dim_aluno["id_aluno"].tolist(), k=n_pag),
        "valor":             rng.uniform(180, 650, n_pag).round(2),
        "status_pagamento":  status_pag,
        "forma_pagamento":   random.choices(["Boleto", "Pix", "Cartão de Crédito", "Débito Automático"], k=n_pag),
    })

    return {
        "DimVeiculo": dim_veiculo,
        "DimMotorista": dim_motorista,
        "DimAluno": dim_aluno,
        "FatoRota": fato_rota,
        "FatoMensalidade": fato_mensalidade,
        "dCalendario": dcalendario(start, end),
    }
