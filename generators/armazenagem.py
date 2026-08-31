"""generators/armazenagem.py — Setor Armazenagem & Self Storage."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TAMANHOS_BOX     = ["3m²", "6m²", "9m²", "12m²", "20m²"]
STATUS_CONTRATO  = ["Ativo", "Encerrado", "Inadimplente", "Cancelado"]
TIPOS_OCORRENCIA = ["Atraso de Pagamento", "Furto", "Infiltração", "Solicitação de Acesso", "Dano Estrutural"]


def gerar_armazenagem(n, start, end):
    n = max(int(n), 1)

    n_unidade = min(max(n // 150, 4), 60)
    dim_unidade = pd.DataFrame({
        "id_unidade":        new_ids(n_unidade),
        "cidade":            [fake.city() for _ in range(n_unidade)],
        "uf":                [fake.state_abbr() for _ in range(n_unidade)],
        "capacidade_boxes":  rng.integers(80, 800, n_unidade),
    })

    n_box = min(max(n // 4, 100), 15000)
    dim_box = pd.DataFrame({
        "id_box":            new_ids(n_box),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n_box),
        "tamanho":           random.choices(TAMANHOS_BOX, weights=[30, 30, 20, 12, 8], k=n_box),
        "climatizado":       random.choices([True, False], weights=[25, 75], k=n_box),
    })

    n_cliente = min(max(n // 3, 150), 20000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.name() for _ in range(n_cliente)],
        "tipo_cliente":      random.choices(["Pessoa Física", "Pessoa Jurídica"], weights=[65, 35], k=n_cliente),
    })

    status = random.choices(STATUS_CONTRATO, weights=[70, 15, 10, 5], k=n)
    fato_contrato = pd.DataFrame({
        "id_contrato":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_box":            random.choices(dim_box["id_box"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "valor_mensal":      rng.uniform(89, 1200, n).round(2),
        "duracao_meses":     rng.integers(1, 36, n),
        "status":            status,
        "inadimplente":      [s == "Inadimplente" for s in status],
    })

    n_ocorrencia = int(n_box * 0.15)
    fato_ocorrencia = pd.DataFrame({
        "id_ocorrencia":     new_ids(n_ocorrencia),
        "id_data":           rand_dates(start, end, n_ocorrencia),
        "id_box":            random.choices(dim_box["id_box"].tolist(), k=n_ocorrencia),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n_ocorrencia),
        "tipo_ocorrencia":   random.choices(TIPOS_OCORRENCIA, weights=[45, 5, 10, 35, 5], k=n_ocorrencia),
        "resolvida":         random.choices([True, False], weights=[85, 15], k=n_ocorrencia),
    })

    return {
        "DimUnidade": dim_unidade,
        "DimBox": dim_box,
        "DimCliente": dim_cliente,
        "FatoContrato": fato_contrato,
        "FatoOcorrencia": fato_ocorrencia,
        "dCalendario": dcalendario(start, end),
    }
