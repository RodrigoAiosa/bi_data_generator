"""generators/seguros.py — Setor Seguros."""

import random
from datetime import date

import numpy as np
import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_SEGURO = ["Auto", "Vida", "Residencial", "Saúde", "Viagem", "Empresarial"]
SEGURADORAS = ["Seguros Brasil", "Porto Seguro", "SulAmérica", "Bradesco Seguros", "Liberty Seguros"]

def gerar_seguros(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_segurados = min(n, 5000)
    n_corretores = 50
    n_planos = 30
    
    dim_segurado = pd.DataFrame({
        "id_segurado": new_ids(n_segurados),
        "nome":        [fake.name() for _ in range(n_segurados)],
        "cpf":         [fake.cpf() for _ in range(n_segurados)],
        "idade":       rng.integers(18, 85, n_segurados),
        "sexo":        random.choices(["M", "F"], k=n_segurados),
        "cidade":      [fake.city() for _ in range(n_segurados)],
        "uf":          random.choices(["SP", "RJ", "MG", "RS", "PR", "SC", "BA", "CE", "PE", "GO"], k=n_segurados)
    })

    dim_corretor = pd.DataFrame({
        "id_corretor": new_ids(n_corretores),
        "nome":        [fake.name() for _ in range(n_corretores)],
        "registro_susep": [f"SUSEP-{rng.integers(100000, 999999)}" for _ in range(n_corretores)],
        "agencia":     [f"Agência {fake.company()}" for _ in range(n_corretores)]
    })

    dim_plano = pd.DataFrame({
        "id_plano": new_ids(n_planos),
        "nome":     [f"Plano {fake.word().capitalize()} {i}" for i in range(1, n_planos + 1)],
        "tipo":     random.choices(TIPOS_SEGURO, k=n_planos),
        "cobertura_max": rng.uniform(50000, 2000000, n_planos).round(2),
        "franquia":      rng.uniform(500, 5000, n_planos).round(2)
    })

    datas = rand_dates(start, end, n)
    planos_ids = random.choices(dim_plano["id_plano"].tolist(), k=n)
    coberturas = [dim_plano.loc[dim_plano["id_plano"] == p, "cobertura_max"].values[0] for p in planos_ids]
    
    fato = pd.DataFrame({
        "id_apolice":  new_ids(n),
        "id_data":     datas,
        "id_segurado": random.choices(dim_segurado["id_segurado"].tolist(), k=n),
        "id_corretor": random.choices(dim_corretor["id_corretor"].tolist(), k=n),
        "id_plano":    planos_ids,
        "valor_premio": [round(c * rng.uniform(0.01, 0.05), 2) for c in coberturas],
        "status":      random.choices(["Ativa", "Cancelada", "Inadimplente", "Vencida"], weights=[0.8, 0.05, 0.05, 0.1], k=n),
        "sinistros_ocorridos": rng.integers(0, 3, n),
        "valor_indenizacao": [round(c * rng.uniform(0, 0.5) if random.random() < 0.1 else 0, 2) for c in coberturas]
    })

    return {
        "DimSegurado": dim_segurado,
        "DimCorretor": dim_corretor,
        "DimPlano":    dim_plano,
        "FatoApolices": fato,
        "dCalendario": dcalendario(start, end),
    }
