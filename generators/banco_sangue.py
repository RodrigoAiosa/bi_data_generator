"""generators/banco_sangue.py — Setor Banco de Sangue & Hemocentro."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_SANGUINEOS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
PESOS_TIPO = [34, 6, 9, 2, 3, 1, 36, 9]


def gerar_banco_sangue(n, start, end):
    n = max(int(n), 1)

    n_unidade = min(max(n // 200, 5), 50)
    dim_unidade = pd.DataFrame({
        "id_unidade":        new_ids(n_unidade),
        "cidade":            [fake.city() for _ in range(n_unidade)],
        "uf":                [fake.state_abbr() for _ in range(n_unidade)],
    })

    n_doador = min(max(n // 3, 200), 15000)
    dim_doador = pd.DataFrame({
        "id_doador":         new_ids(n_doador),
        "nome":              [fake.name() for _ in range(n_doador)],
        "tipo_sanguineo":    random.choices(TIPOS_SANGUINEOS, weights=PESOS_TIPO, k=n_doador),
        "idade":             rng.integers(16, 69, n_doador),
    })

    fato_doacao = pd.DataFrame({
        "id_doacao":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n),
        "id_doador":         random.choices(dim_doador["id_doador"].tolist(), k=n),
        "volume_ml":         random.choices([405, 450, 470], k=n),
        "status":            random.choices(["Apta", "Inapta", "Descartada"], weights=[85, 10, 5], k=n),
    })

    return {
        "DimUnidade": dim_unidade,
        "DimDoador": dim_doador,
        "FatoDoacao": fato_doacao,
        "dCalendario": dcalendario(start, end),
    }
