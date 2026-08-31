"""generators/energia_solar.py — Setor Energia Solar."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_INSTALACAO = ["Residencial", "Comercial", "Industrial", "Rural"]
STATUS_PROJETO = ["Concluído", "Em Instalação", "Em Análise", "Cancelado"]


def gerar_energia_solar(n, start, end):
    n = max(int(n), 1)

    n_cliente = min(max(n // 10, 50), 6000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.name() if random.random() > 0.4 else fake.company() for _ in range(n_cliente)],
        "tipo_instalacao":   random.choices(TIPOS_INSTALACAO, weights=[55, 25, 10, 10], k=n_cliente),
        "uf":                [fake.state_abbr() for _ in range(n_cliente)],
    })

    dim_instalacao = pd.DataFrame({
        "id_instalacao":         new_ids(n_cliente),
        "id_cliente":            dim_cliente["id_cliente"].tolist(),
        "potencia_instalada_kwp": rng.uniform(1.5, 500, n_cliente).round(2),
        "num_paineis":           rng.integers(4, 400, n_cliente),
    })

    fato_geracao = pd.DataFrame({
        "id_geracao":         new_ids(n),
        "id_data":            rand_dates(start, end, n),
        "id_instalacao":      random.choices(dim_instalacao["id_instalacao"].tolist(), k=n),
        "energia_gerada_kwh": rng.uniform(2, 2500, n).round(1),
        "economia_reais":     rng.uniform(5, 3500, n).round(2),
    })

    n_proj = int(n_cliente * 0.3)
    fato_projeto = pd.DataFrame({
        "id_projeto":         new_ids(n_proj),
        "id_data":            rand_dates(start, end, n_proj),
        "id_cliente":         random.choices(dim_cliente["id_cliente"].tolist(), k=n_proj),
        "potencia_kwp":       rng.uniform(1.5, 500, n_proj).round(2),
        "valor_orcamento":    rng.uniform(6000, 900000, n_proj).round(2),
        "status_instalacao":  random.choices(STATUS_PROJETO, weights=[65, 15, 15, 5], k=n_proj),
    })

    return {
        "DimCliente": dim_cliente,
        "DimInstalacao": dim_instalacao,
        "FatoGeracao": fato_geracao,
        "FatoProjeto": fato_projeto,
        "dCalendario": dcalendario(start, end),
    }
