"""generators/taxi_aereo.py — Setor Táxi Aéreo & Aviação Executiva."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_AERONAVE = ["Jato Executivo Leve", "Jato Executivo Médio", "Jato Executivo Grande", "Helicóptero", "Turboélice"]
FABRICANTES = ["Embraer", "Cessna", "Bombardier", "Gulfstream", "Airbus Helicopters", "Robinson"]
TIPOS_CLIENTE = ["Corporativo", "Particular", "Fretamento Pontual", "Multipropriedade de Cota"]
MOTIVOS_VOO = ["Reunião de Negócios", "Turismo", "Emergência Médica", "Evento", "Transporte de Executivos"]
TIPOS_MANUTENCAO = ["Preventiva Programada", "Corretiva", "Revisão de Motor", "Inspeção Anual", "Troca de Componente"]


def gerar_taxi_aereo(n, start, end):
    n = max(int(n), 1)

    n_aeronave = min(max(n // 200, 4), 80)
    dim_aeronave = pd.DataFrame({
        "id_aeronave":       new_ids(n_aeronave),
        "modelo":            [f"{random.choice(FABRICANTES)} {fake.word().capitalize()}" for _ in range(n_aeronave)],
        "tipo":              random.choices(TIPOS_AERONAVE, weights=[30, 25, 15, 25, 5], k=n_aeronave),
        "capacidade_passageiros": rng.integers(2, 16, n_aeronave),
        "ano_fabricacao":    rng.integers(1998, 2025, n_aeronave),
        "horas_totais_voo":  rng.integers(200, 18000, n_aeronave),
    })

    n_piloto = min(max(n // 150, 6), 120)
    dim_piloto = pd.DataFrame({
        "id_piloto":         new_ids(n_piloto),
        "nome":              [fake.name() for _ in range(n_piloto)],
        "horas_certificadas": rng.integers(500, 15000, n_piloto),
        "categoria":         random.choices(["Comandante", "Copiloto"], weights=[55, 45], k=n_piloto),
        "ativo":             random.choices([True, False], weights=[92, 8], k=n_piloto),
    })

    dist_km = rng.uniform(80, 3500, n)
    fato_voo = pd.DataFrame({
        "id_voo":            new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_aeronave":       random.choices(dim_aeronave["id_aeronave"].tolist(), k=n),
        "id_piloto":         random.choices(dim_piloto["id_piloto"].tolist(), k=n),
        "origem":            [fake.city() for _ in range(n)],
        "destino":           [fake.city() for _ in range(n)],
        "distancia_km":      dist_km.round(1),
        "horas_voo":         (dist_km / rng.uniform(350, 700, n)).round(2),
        "tipo_cliente":      random.choices(TIPOS_CLIENTE, weights=[45, 25, 20, 10], k=n),
        "motivo":            random.choices(MOTIVOS_VOO, weights=[40, 20, 5, 15, 20], k=n),
        "numero_passageiros": rng.integers(1, 12, n),
        "valor":             rng.uniform(6000, 180000, n).round(2),
    })

    n_manut = int(n_aeronave * 25)
    fato_manutencao = pd.DataFrame({
        "id_manutencao":     new_ids(n_manut),
        "id_data":           rand_dates(start, end, n_manut),
        "id_aeronave":       random.choices(dim_aeronave["id_aeronave"].tolist(), k=n_manut),
        "tipo_manutencao":   random.choices(TIPOS_MANUTENCAO, weights=[40, 20, 10, 20, 10], k=n_manut),
        "custo":             rng.uniform(1500, 250000, n_manut).round(2),
        "horas_paralisada":  rng.integers(2, 720, n_manut),
    })

    return {
        "DimAeronave": dim_aeronave,
        "DimPiloto": dim_piloto,
        "FatoVoo": fato_voo,
        "FatoManutencao": fato_manutencao,
        "dCalendario": dcalendario(start, end),
    }
