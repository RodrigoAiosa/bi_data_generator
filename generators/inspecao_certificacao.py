"""generators/inspecao_certificacao.py — Setor Inspeção & Certificação."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

AREAS_ATUACAO = ["Qualidade", "Segurança", "Meio Ambiente", "Alimentos"]
CERTIFICACOES = ["ISO 9001", "ISO 14001", "ISO 45001", "HACCP", "FSSC 22000"]
RESULTADOS = ["Aprovado", "Reprovado", "Com Ressalvas"]


def gerar_inspecao_certificacao(n, start, end):
    n = max(int(n), 1)

    n_inspetor = min(max(n // 100, 8), 300)
    dim_inspetor = pd.DataFrame({
        "id_inspetor":       new_ids(n_inspetor),
        "nome":              [fake.name() for _ in range(n_inspetor)],
        "area_atuacao":      random.choices(AREAS_ATUACAO, k=n_inspetor),
    })

    n_empresa_cliente = min(max(n // 5, 200), 15000)
    dim_empresa_cliente = pd.DataFrame({
        "id_empresa_cliente": new_ids(n_empresa_cliente),
        "nome_empresa":      [fake.company() for _ in range(n_empresa_cliente)],
        "setor":             random.choices(["Indústria", "Serviços", "Alimentos", "Construção"], k=n_empresa_cliente),
    })

    fato_auditoria = pd.DataFrame({
        "id_auditoria":      new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_inspetor":       random.choices(dim_inspetor["id_inspetor"].tolist(), k=n),
        "id_empresa_cliente": random.choices(dim_empresa_cliente["id_empresa_cliente"].tolist(), k=n),
        "tipo_certificacao": random.choices(CERTIFICACOES, k=n),
        "resultado":         random.choices(RESULTADOS, weights=[65, 10, 25], k=n),
        "nao_conformidades": rng.integers(0, 15, n),
    })

    return {
        "DimInspetor": dim_inspetor,
        "DimEmpresaCliente": dim_empresa_cliente,
        "FatoAuditoria": fato_auditoria,
        "dCalendario": dcalendario(start, end),
    }
