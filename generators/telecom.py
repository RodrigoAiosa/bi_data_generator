"""generators/telecom.py — Setor Telecom."""

import random
from datetime import date

import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")


def gerar_telecom(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_assinantes = min(n, 5000)
    n_planos     = 20
    n_torres     = 50

    dim_plano = pd.DataFrame({
        "id_plano": new_ids(n_planos),
        "nome": [
            f"Plano {p} {d}"
            for p, d in zip(
                random.choices(["Básico","Plus","Max","Ultra","Ilimitado"], k=n_planos),
                random.choices(["Móvel","Fixo","Combo","Empresarial"], k=n_planos),
            )
        ],
        "tipo":         random.choices(["Pré-pago","Pós-pago","Controle","Empresarial"], k=n_planos),
        "dados_gb":     random.choices([5,10,15,20,30,50,100,0], k=n_planos),
        "valor_mensal": rng.uniform(29.9, 299.9, n_planos).round(2),
    })

    dim_torre = pd.DataFrame({
        "id_torre":          new_ids(n_torres),
        "codigo":            [f"ERB-{rng.integers(1000,9999)}" for _ in range(n_torres)],
        "tecnologia":        random.choices(["2G","3G","4G","5G"], weights=[5,10,60,25], k=n_torres),
        "uf":                random.choices(["SP","RJ","MG","RS","PR","BA"], k=n_torres),
        "capacidade_canais": rng.integers(50, 500, n_torres),
    })

    dim_assinante = pd.DataFrame({
        "id_assinante": new_ids(n_assinantes),
        "nome":         [fake.name() for _ in range(n_assinantes)],
        "cpf":          [fake.cpf()  for _ in range(n_assinantes)],
        "ddd":          [str(random.choice([11,21,31,41,51,61,71,81,85,91])) for _ in range(n_assinantes)],
        "id_plano":     random.choices(dim_plano["id_plano"].tolist(), k=n_assinantes),
        "uf":           random.choices(["SP","RJ","MG","RS","PR","BA"], k=n_assinantes),
    })

    fato = pd.DataFrame({
        "id_chamada":    new_ids(n),
        "id_data":       rand_dates(start, end, n),
        "id_assinante":  random.choices(dim_assinante["id_assinante"].tolist(), k=n),
        "id_plano":      random.choices(dim_plano["id_plano"].tolist(), k=n),
        "id_torre":      random.choices(dim_torre["id_torre"].tolist(), k=n),
        "tipo":          random.choices(["Voz","SMS","Dados","VoIP","Roaming"], k=n),
        "duracao_seg":   rng.integers(0, 3600, n),
        "dados_mb":      rng.uniform(0, 2000, n).round(2),
        "valor_cobrado": rng.uniform(0, 50, n).round(2),
        "qualidade_dbm": rng.integers(-110, -60, n),
    })

    return {
        "DimPlano":     dim_plano,
        "DimTorre":     dim_torre,
        "DimAssinante": dim_assinante,
        "FatoChamada":  fato,
        "dCalendario":  dcalendario(start, end),
    }
