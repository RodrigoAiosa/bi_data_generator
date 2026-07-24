"""generators/correios.py — Setor Correios & Encomendas."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_AGENCIA = ["Própria", "Franquia"]
SERVICOS = ["SEDEX", "PAC", "Carta Registrada", "Encomenda Internacional", "Mini Envios", "SEDEX 10"]
MODALIDADES = ["Nacional", "Internacional"]
STATUS_ENVIO = ["Postado", "Em Trânsito", "Saiu para Entrega", "Entregue", "Devolvido", "Extraviado"]
TIPOS_OCORRENCIA = ["Extravio", "Atraso", "Avaria", "Devolução ao Remetente", "Endereço Incorreto"]


def gerar_correios(n, start, end):
    n = max(int(n), 1)

    n_agencia = min(max(n // 200, 15), 800)
    dim_agencia = pd.DataFrame({
        "id_agencia":        new_ids(n_agencia),
        "nome":              [f"Agência {fake.city()}" for _ in range(n_agencia)],
        "uf":                [fake.state_abbr() for _ in range(n_agencia)],
        "cidade":            [fake.city() for _ in range(n_agencia)],
        "tipo":              random.choices(TIPOS_AGENCIA, weights=[55, 45], k=n_agencia),
    })

    n_servico = min(max(n // 500, 5), 20)
    dim_servico = pd.DataFrame({
        "id_servico":        new_ids(n_servico),
        "nome":              random.choices(SERVICOS, k=n_servico),
        "prazo_dias":        rng.integers(1, 15, n_servico),
        "modalidade":        random.choices(MODALIDADES, weights=[85, 15], k=n_servico),
    })

    status_envio = random.choices(STATUS_ENVIO, weights=[10, 20, 10, 50, 6, 4], k=n)
    fato_envio = pd.DataFrame({
        "id_envio":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_agencia":        random.choices(dim_agencia["id_agencia"].tolist(), k=n),
        "id_servico":        random.choices(dim_servico["id_servico"].tolist(), k=n),
        "peso_kg":           rng.uniform(0.1, 30, n).round(2),
        "valor_frete":       rng.uniform(8, 450, n).round(2),
        "distancia_km":      rng.uniform(5, 4000, n).round(1),
        "status":            status_envio,
        "entregue_no_prazo": [s == "Entregue" and random.random() < 0.85 for s in status_envio],
    })

    n_ocorrencia = int(n * 0.08)
    fato_ocorrencia = pd.DataFrame({
        "id_ocorrencia":     new_ids(n_ocorrencia),
        "id_data":           rand_dates(start, end, n_ocorrencia),
        "id_agencia":        random.choices(dim_agencia["id_agencia"].tolist(), k=n_ocorrencia),
        "tipo_ocorrencia":   random.choices(TIPOS_OCORRENCIA, weights=[15, 40, 15, 20, 10], k=n_ocorrencia),
        "valor_indenizacao": rng.uniform(0, 3000, n_ocorrencia).round(2),
    })

    return {
        "DimAgencia": dim_agencia,
        "DimServico": dim_servico,
        "FatoEnvio": fato_envio,
        "FatoOcorrencia": fato_ocorrencia,
        "dCalendario": dcalendario(start, end),
    }
