"""generators/plano_saude.py — Setor Operadora de Plano de Saúde."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

TIPOS_PLANO       = ["Individual", "Familiar", "Empresarial", "Adesão"]
FAIXAS_COPART     = ["Sem Coparticipação", "Coparticipação Parcial", "Coparticipação Total"]
ESPECIALIDADES    = ["Clínico Geral", "Cardiologia", "Ortopedia", "Pediatria", "Ginecologia",
                      "Dermatologia", "Psiquiatria", "Oftalmologia"]
STATUS_AUTORIZACAO = ["Aprovada", "Negada", "Em Análise", "Pendente de Documentação"]
STATUS_PAGAMENTO  = ["Pago", "Pendente", "Atrasado", "Cancelado"]


def gerar_plano_saude(n, start, end):
    n = max(int(n), 1)

    n_plano = min(max(n // 200, 6), 40)
    dim_plano = pd.DataFrame({
        "id_plano":          new_ids(n_plano),
        "tipo":              random.choices(TIPOS_PLANO, weights=[30, 25, 35, 10], k=n_plano),
        "coparticipacao":    random.choices(FAIXAS_COPART, weights=[35, 45, 20], k=n_plano),
        "valor_mensalidade_base": rng.uniform(180, 2200, n_plano).round(2),
        "abrangencia":       random.choices(["Nacional", "Estadual", "Regional"], weights=[40, 35, 25], k=n_plano),
    })

    n_prestador = min(max(n // 30, 40), 3000)
    dim_prestador = pd.DataFrame({
        "id_prestador":      new_ids(n_prestador),
        "nome":              [f"{fake.last_name()} {random.choice(['Hospital', 'Clínica', 'Laboratório', 'Consultório'])}" for _ in range(n_prestador)],
        "especialidade":     random.choices(ESPECIALIDADES, k=n_prestador),
        "uf":                fake_pool(fake, "state_abbr", n_prestador),
        "credenciado_desde": rng.integers(2005, 2024, n_prestador),
    })

    n_beneficiario = min(max(n // 4, 300), 20000)
    dim_beneficiario = pd.DataFrame({
        "id_beneficiario":   new_ids(n_beneficiario),
        "nome":              fake_pool(fake, "name", n_beneficiario),
        "idade":             rng.integers(0, 95, n_beneficiario),
        "sexo":              random.choices(["F", "M"], k=n_beneficiario),
        "id_plano":          random.choices(dim_plano["id_plano"].tolist(), k=n_beneficiario),
        "uf":                fake_pool(fake, "state_abbr", n_beneficiario),
        "ativo":             random.choices([True, False], weights=[88, 12], k=n_beneficiario),
    })

    status_aut = random.choices(STATUS_AUTORIZACAO, weights=[62, 13, 18, 7], k=n)
    fato_autorizacao = pd.DataFrame({
        "id_autorizacao":    new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_beneficiario":   random.choices(dim_beneficiario["id_beneficiario"].tolist(), k=n),
        "id_prestador":      random.choices(dim_prestador["id_prestador"].tolist(), k=n),
        "especialidade":     random.choices(ESPECIALIDADES, k=n),
        "status":            status_aut,
        "valor_procedimento": rng.uniform(50, 8500, n).round(2),
        "negada":            [s == "Negada" for s in status_aut],
    })

    n_mensalidade = int(n_beneficiario * 1.3)
    status_mensalidade = random.choices(STATUS_PAGAMENTO, weights=[80, 10, 7, 3], k=n_mensalidade)
    fato_mensalidade = pd.DataFrame({
        "id_mensalidade":    new_ids(n_mensalidade),
        "id_data":           rand_dates(start, end, n_mensalidade),
        "id_beneficiario":   random.choices(dim_beneficiario["id_beneficiario"].tolist(), k=n_mensalidade),
        "id_plano":          random.choices(dim_plano["id_plano"].tolist(), k=n_mensalidade),
        "valor":             rng.uniform(180, 2500, n_mensalidade).round(2),
        "status_pagamento":  status_mensalidade,
        "inadimplente":      [s in ("Pendente", "Atrasado") for s in status_mensalidade],
    })

    return {
        "DimBeneficiario": dim_beneficiario,
        "DimPlano": dim_plano,
        "DimPrestador": dim_prestador,
        "FatoAutorizacao": fato_autorizacao,
        "FatoMensalidade": fato_mensalidade,
        "dCalendario": dcalendario(start, end),
    }
