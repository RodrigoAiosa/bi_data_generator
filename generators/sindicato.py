"""generators/sindicato.py — Setor Sindicato & Associação de Classe."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

CATEGORIAS_PROFISSIONAIS = ["Metalúrgicos", "Comerciários", "Bancários", "Professores",
                             "Rodoviários", "Saúde", "Tecnologia da Informação"]
STATUS_PAGAMENTO   = ["Pago", "Pendente", "Atrasado", "Isento"]
TIPOS_BENEFICIO    = ["Assistência Jurídica", "Convênio Médico", "Curso Profissionalizante",
                       "Colônia de Férias", "Assistência Odontológica"]


def gerar_sindicato(n, start, end):
    n = max(int(n), 1)

    n_categoria = min(max(n // 400, 4), len(CATEGORIAS_PROFISSIONAIS))
    dim_categoria = pd.DataFrame({
        "id_categoria":      new_ids(n_categoria),
        "nome":              CATEGORIAS_PROFISSIONAIS[:n_categoria],
        "valor_mensalidade_base": rng.uniform(15, 90, n_categoria).round(2),
    })

    n_associado = min(max(n // 6, 200), 15000)
    dim_associado = pd.DataFrame({
        "id_associado":      new_ids(n_associado),
        "nome":              fake_pool(fake, "name", n_associado),
        "id_categoria":      random.choices(dim_categoria["id_categoria"].tolist(), k=n_associado),
        "uf":                fake_pool(fake, "state_abbr", n_associado),
        "ano_filiacao":      rng.integers(1995, 2024, n_associado),
        "ativo":             random.choices([True, False], weights=[85, 15], k=n_associado),
    })

    status_contribuicao = random.choices(STATUS_PAGAMENTO, weights=[72, 12, 10, 6], k=n)
    fato_contribuicao = pd.DataFrame({
        "id_contribuicao":   new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_associado":      random.choices(dim_associado["id_associado"].tolist(), k=n),
        "valor":             rng.uniform(15, 120, n).round(2),
        "status_pagamento":  status_contribuicao,
        "inadimplente":      [s == "Atrasado" for s in status_contribuicao],
    })

    n_servico = int(n * 0.3)
    fato_servico = pd.DataFrame({
        "id_servico":        new_ids(n_servico),
        "id_data":           rand_dates(start, end, n_servico),
        "id_associado":      random.choices(dim_associado["id_associado"].tolist(), k=n_servico),
        "tipo_beneficio":    random.choices(TIPOS_BENEFICIO, k=n_servico),
        "utilizacoes":       rng.integers(1, 5, n_servico),
    })

    return {
        "DimAssociado": dim_associado,
        "DimCategoriaProfissional": dim_categoria,
        "FatoContribuicao": fato_contribuicao,
        "FatoServico": fato_servico,
        "dCalendario": dcalendario(start, end),
    }
