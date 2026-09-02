"""generators/multipropriedade.py — Setor Multipropriedade."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

CATEGORIAS_RESORT = ["Praia", "Montanha", "Cidade", "Campo"]
TIPOS_UNIDADE     = ["Studio", "1 Dormitório", "2 Dormitórios", "3 Dormitórios", "Cobertura"]
STATUS_RESERVA    = ["Confirmada", "Utilizada", "Cancelada", "Transferida a Terceiros"]
STATUS_PAGAMENTO  = ["Pago", "Pendente", "Atrasado"]


def gerar_multipropriedade(n, start, end):
    n = max(int(n), 1)

    n_resort = min(max(n // 400, 4), 30)
    dim_resort = pd.DataFrame({
        "id_resort":         new_ids(n_resort),
        "nome":              [f"Resort {fake.city()}" for _ in range(n_resort)],
        "categoria":         random.choices(CATEGORIAS_RESORT, weights=[45, 25, 20, 10], k=n_resort),
        "uf":                fake_pool(fake, "state_abbr", n_resort),
        "estrelas":          random.choices([3, 4, 5], weights=[15, 45, 40], k=n_resort),
    })

    n_unidade = min(max(n // 40, 30), 1200)
    dim_unidade = pd.DataFrame({
        "id_unidade":        new_ids(n_unidade),
        "id_resort":         random.choices(dim_resort["id_resort"].tolist(), k=n_unidade),
        "tipo":              random.choices(TIPOS_UNIDADE, weights=[15, 30, 30, 15, 10], k=n_unidade),
        "capacidade_hospedes": random.choices([2, 4, 6, 8, 10], weights=[15, 35, 25, 15, 10], k=n_unidade),
        "fracoes_totais":    random.choices([12, 13, 26, 52], weights=[40, 30, 20, 10], k=n_unidade),
    })

    n_proprietario = min(max(n // 8, 100), 8000)
    dim_proprietario = pd.DataFrame({
        "id_proprietario":   new_ids(n_proprietario),
        "nome":              fake_pool(fake, "name", n_proprietario),
        "uf":                fake_pool(fake, "state_abbr", n_proprietario),
        "num_fracoes_possuidas": random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5], k=n_proprietario),
        "ano_adesao":        rng.integers(2010, 2024, n_proprietario),
    })

    status_reserva = random.choices(STATUS_RESERVA, weights=[35, 45, 12, 8], k=n)
    fato_reserva = pd.DataFrame({
        "id_reserva":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n),
        "id_proprietario":   random.choices(dim_proprietario["id_proprietario"].tolist(), k=n),
        "semana_ano":        rng.integers(1, 53, n),
        "diarias":           random.choices([3, 4, 5, 6, 7], weights=[10, 15, 20, 15, 40], k=n),
        "status":            status_reserva,
        "valor_diaria":      rng.uniform(280, 2200, n).round(2),
    })

    n_taxa = int(n_proprietario * 1.2)
    status_taxa = random.choices(STATUS_PAGAMENTO, weights=[78, 14, 8], k=n_taxa)
    fato_taxa_manutencao = pd.DataFrame({
        "id_taxa":           new_ids(n_taxa),
        "id_data":           rand_dates(start, end, n_taxa),
        "id_proprietario":   random.choices(dim_proprietario["id_proprietario"].tolist(), k=n_taxa),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n_taxa),
        "valor":             rng.uniform(800, 6500, n_taxa).round(2),
        "status_pagamento":  status_taxa,
        "inadimplente":      [s == "Atrasado" for s in status_taxa],
    })

    return {
        "DimResort": dim_resort,
        "DimUnidadeImovel": dim_unidade,
        "DimProprietario": dim_proprietario,
        "FatoReserva": fato_reserva,
        "FatoTaxaManutencao": fato_taxa_manutencao,
        "dCalendario": dcalendario(start, end),
    }
