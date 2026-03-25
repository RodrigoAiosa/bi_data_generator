"""generators/energia.py — Setor Energia."""

import random
from datetime import date

import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")


def gerar_energia(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_consumidores = min(n, 5000)
    n_medidores    = min(n, 5000)
    n_subestacoes  = 20

    dim_subestacao = pd.DataFrame({
        "id_subestacao": new_ids(n_subestacoes),
        "nome":          [f"SE {fake.city()}" for _ in range(n_subestacoes)],
        "tensao_kv":     random.choices([13.8, 34.5, 69, 138, 230, 440], k=n_subestacoes),
        "uf":            random.choices(["SP","MG","RJ","RS","PR"], k=n_subestacoes),
    })

    dim_consumidor = pd.DataFrame({
        "id_consumidor": new_ids(n_consumidores),
        "nome":          [fake.name() for _ in range(n_consumidores)],
        "cpf_cnpj":      [fake.cpf()  for _ in range(n_consumidores)],
        "classe":        random.choices(
            ["Residencial","Comercial","Industrial","Rural","Poder Público"],
            weights=[55, 25, 10, 5, 5], k=n_consumidores,
        ),
        "subclasse": random.choices(["Normal","BT","AT","MT"], k=n_consumidores),
        "uf":        random.choices(["SP","MG","RJ","RS","PR"], k=n_consumidores),
    })

    dim_medidor = pd.DataFrame({
        "id_medidor":    new_ids(n_medidores),
        "serial":        [f"MED{rng.integers(100000,999999)}" for _ in range(n_medidores)],
        "modelo":        random.choices(["LANDIS+GYR","ELSTER","ITRON","SCHNEIDER"], k=n_medidores),
        "id_consumidor": random.choices(dim_consumidor["id_consumidor"].tolist(), k=n_medidores),
        "id_subestacao": random.choices(dim_subestacao["id_subestacao"].tolist(), k=n_medidores),
    })

    consumo = rng.uniform(50, 5000, n).round(2)
    tarifa  = rng.uniform(0.6, 1.5, n)

    fato = pd.DataFrame({
        "id_leitura":     new_ids(n),
        "id_data":        rand_dates(start, end, n),
        "id_medidor":     random.choices(dim_medidor["id_medidor"].tolist(), k=n),
        "id_consumidor":  random.choices(dim_consumidor["id_consumidor"].tolist(), k=n),
        "id_subestacao":  random.choices(dim_subestacao["id_subestacao"].tolist(), k=n),
        "consumo_kwh":    consumo,
        "demanda_kw":     rng.uniform(5, 500, n).round(2),
        "tarifa_kwh":     tarifa.round(4),
        "valor_fatura":   (consumo * tarifa).round(2),
        "tensao_v":       rng.uniform(210, 240, n).round(1),
        "fator_potencia": rng.uniform(0.85, 1.0, n).round(3),
    })

    return {
        "DimSubestacao": dim_subestacao,
        "DimConsumidor": dim_consumidor,
        "DimMedidor":    dim_medidor,
        "FatoConsumo":   fato,
        "dCalendario":   dcalendario(start, end),
    }
