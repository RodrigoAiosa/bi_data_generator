"""generators/apicultura.py — Setor Apicultura."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_MEL     = ["Silvestre", "Laranjeira", "Eucalipto", "Assa-Peixe", "Aroeira", "Cipó-Uva"]
QUALIDADE     = ["Extra", "Primeira", "Segunda"]
DOENCAS       = ["Nenhuma", "Varroa", "Nosemose", "Cria Pútrida", "Ácaro Traqueal"]
TRATAMENTOS   = ["Nenhum", "Ácido Oxálico", "Timol", "Troca de Rainha", "Reforço Alimentar"]


def gerar_apicultura(n, start, end):
    n = max(int(n), 1)

    n_apiario = min(max(n // 100, 5), 80)
    dim_apiario = pd.DataFrame({
        "id_apiario":        new_ids(n_apiario),
        "localizacao":       [fake.city() for _ in range(n_apiario)],
        "uf":                [fake.state_abbr() for _ in range(n_apiario)],
        "num_colmeias":      rng.integers(10, 200, n_apiario),
        "certificado_organico": random.choices([True, False], weights=[30, 70], k=n_apiario),
    })

    n_colmeia = min(max(n // 10, 50), 6000)
    dim_colmeia = pd.DataFrame({
        "id_colmeia":        new_ids(n_colmeia),
        "id_apiario":        random.choices(dim_apiario["id_apiario"].tolist(), k=n_colmeia),
        "especie_abelha":    random.choices(["Apis Mellifera", "Jataí", "Mandaçaia", "Uruçu"], weights=[55, 25, 12, 8], k=n_colmeia),
        "idade_colmeia_anos": rng.integers(0, 15, n_colmeia),
    })

    fato_colheita = pd.DataFrame({
        "id_colheita":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_apiario":        random.choices(dim_apiario["id_apiario"].tolist(), k=n),
        "tipo_mel":          random.choices(TIPOS_MEL, k=n),
        "quantidade_kg":     rng.uniform(2, 80, n).round(1),
        "qualidade":         random.choices(QUALIDADE, weights=[55, 35, 10], k=n),
        "preco_kg":          rng.uniform(18, 55, n).round(2),
    })

    n_sanidade = int(n_colmeia * 0.6)
    doenca = random.choices(DOENCAS, weights=[65, 15, 8, 7, 5], k=n_sanidade)
    fato_sanidade = pd.DataFrame({
        "id_inspecao":       new_ids(n_sanidade),
        "id_data":           rand_dates(start, end, n_sanidade),
        "id_colmeia":        random.choices(dim_colmeia["id_colmeia"].tolist(), k=n_sanidade),
        "doenca_detectada":  doenca,
        "tratamento":        [random.choice(TRATAMENTOS) if d != "Nenhuma" else "Nenhum" for d in doenca],
        "populacao_estimada": rng.integers(5000, 60000, n_sanidade),
    })

    return {
        "DimApiario": dim_apiario,
        "DimColmeia": dim_colmeia,
        "FatoColheita": fato_colheita,
        "FatoSanidadeColmeia": fato_sanidade,
        "dCalendario": dcalendario(start, end),
    }
