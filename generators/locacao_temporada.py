"""generators/locacao_temporada.py — Setor Locação por Temporada."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_IMOVEL = ["Apartamento", "Casa", "Chalé", "Studio", "Cobertura", "Casa de Praia"]
CATEGORIAS_AVALIACAO = ["Limpeza", "Localização", "Comunicação", "Custo-Benefício", "Precisão do Anúncio"]


def gerar_locacao_temporada(n, start, end):
    n = max(int(n), 1)

    n_imovel = min(max(n // 12, 30), 3000)
    dim_imovel = pd.DataFrame({
        "id_imovel":         new_ids(n_imovel),
        "tipo":              random.choices(TIPOS_IMOVEL, weights=[30, 25, 15, 15, 10, 5], k=n_imovel),
        "uf":                [fake.state_abbr() for _ in range(n_imovel)],
        "cidade":            [fake.city() for _ in range(n_imovel)],
        "capacidade":        rng.integers(1, 12, n_imovel),
        "diaria_base":       rng.uniform(90, 1800, n_imovel).round(2),
    })

    n_hospede = min(max(n // 4, 150), 12000)
    dim_hospede = pd.DataFrame({
        "id_hospede":        new_ids(n_hospede),
        "nome":              [fake.name() for _ in range(n_hospede)],
        "uf":                [fake.state_abbr() for _ in range(n_hospede)],
        "avaliacao_media":   rng.uniform(3.0, 5.0, n_hospede).round(1),
    })

    noites = rng.integers(1, 21, n)
    imovel_idx = random.choices(range(n_imovel), k=n)
    diaria = dim_imovel["diaria_base"].to_numpy()[imovel_idx] * rng.uniform(0.85, 1.5, n)
    cancelada = random.choices([True, False], weights=[10, 90], k=n)
    fato_reserva = pd.DataFrame({
        "id_reserva":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_imovel":         dim_imovel["id_imovel"].to_numpy()[imovel_idx],
        "id_hospede":        random.choices(dim_hospede["id_hospede"].tolist(), k=n),
        "noites":            noites,
        "valor_diaria":      diaria.round(2),
        "valor_total":       (noites * diaria).round(2),
        "taxa_limpeza":      rng.uniform(30, 250, n).round(2),
        "cancelada":         cancelada,
    })

    n_aval = int(n * 0.6)
    fato_avaliacao = pd.DataFrame({
        "id_avaliacao_temp": new_ids(n_aval),
        "id_data":           rand_dates(start, end, n_aval),
        "id_imovel":         random.choices(dim_imovel["id_imovel"].tolist(), k=n_aval),
        "id_hospede":        random.choices(dim_hospede["id_hospede"].tolist(), k=n_aval),
        "nota":              rng.uniform(1, 5, n_aval).round(1),
        "categoria":         random.choices(CATEGORIAS_AVALIACAO, k=n_aval),
    })

    return {
        "DimImovel": dim_imovel,
        "DimHospede": dim_hospede,
        "FatoReserva": fato_reserva,
        "FatoAvaliacao": fato_avaliacao,
        "dCalendario": dcalendario(start, end),
    }
