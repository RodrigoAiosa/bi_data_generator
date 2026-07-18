# generators/agtech.py
"""generators/agtech.py — Setor AgTech (Tecnologia Agrícola)."""

import random
from datetime import date

import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_SENSOR = [
    "Umidade do Solo", "Temperatura", "PH", "Condutividade Elétrica",
    "Nitrogênio", "Fósforo", "Potássio", "Umidade do Ar", "Luminosidade",
    "Velocidade do Vento", "Chuva", "NDVI (Satélite)"
]

STATUS_SENSOR = ["Ativo", "Em Manutenção", "Falha", "Inativo"]
CULTURAS_AGTECH = ["Soja", "Milho", "Algodão", "Café", "Cana", "Trigo", "Laranja", "Uva"]
RECOMENDACOES = [
    "Irrigar", "Adubar com N", "Aplicar defensivo", "Colher", "Não irrigar",
    "Aumentar monitoramento", "Pulverizar fungicida", "Controlar pragas"
]

def gerar_agtech(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_fazendas = min(n // 3 + 10, 80)
    n_sensores = min(n // 2 + 20, 200)
    n_talhoes = min(n // 2 + 30, 300)
    n_drones = min(n // 20 + 5, 30)

    # ── DimFazenda ──────────────────────────────────────────
    dim_fazenda = pd.DataFrame({
        "id_fazenda": new_ids(n_fazendas),
        "nome": [f"Fazenda {fake.last_name()}" for _ in range(n_fazendas)],
        "area_ha": rng.uniform(50, 50000, n_fazendas).round(1),
        "uf": random.choices(["MT", "MS", "GO", "PR", "RS", "SC", "MG", "BA", "PI", "MA"], k=n_fazendas),
        "cultura_principal": random.choices(CULTURAS_AGTECH, k=n_fazendas),
        "tem_irrigacao": random.choices([True, False], weights=[60, 40], k=n_fazendas),
        "ano_adesao": rng.integers(2018, 2025, n_fazendas),
    })

    # ── DimTalhao ───────────────────────────────────────────
    dim_talhao = pd.DataFrame({
        "id_talhao": new_ids(n_talhoes),
        "id_fazenda": random.choices(dim_fazenda["id_fazenda"].tolist(), k=n_talhoes),
        "nome": [f"Talhão {chr(65+i)}" for i in range(n_talhoes)],
        "area_ha": rng.uniform(1, 500, n_talhoes).round(1),
        "cultura": random.choices(CULTURAS_AGTECH, k=n_talhoes),
        "data_plantio": rand_dates(start, end, n_talhoes),
    })

    # ── DimSensor ───────────────────────────────────────────
    dim_sensor = pd.DataFrame({
        "id_sensor": new_ids(n_sensores),
        "tipo": random.choices(TIPOS_SENSOR, k=n_sensores),
        "modelo": [f"{fake.word().capitalize()}-{rng.integers(100,999)}" for _ in range(n_sensores)],
        "precisao_pct": rng.uniform(90, 99.9, n_sensores).round(1),
        "status": random.choices(STATUS_SENSOR, weights=[75, 12, 10, 3], k=n_sensores),
        "data_instalacao": rand_dates(start, end, n_sensores),
        "id_talhao": random.choices(dim_talhao["id_talhao"].tolist(), k=n_sensores),
    })

    # ── DimDrone ────────────────────────────────────────────
    dim_drone = pd.DataFrame({
        "id_drone": new_ids(n_drones),
        "modelo": [f"AgroDrone {rng.integers(100,999)}" for _ in range(n_drones)],
        "autonomia_min": rng.integers(20, 120, n_drones),
        "sensor_embarcado": random.choices(["NDVI", "RGB", "Multiespectral", "LIDAR", "Termal"], k=n_drones),
        "status": random.choices(["Operacional", "Manutenção", "Em voo", "Inativo"], weights=[60, 15, 20, 5], k=n_drones),
    })

    # ── FatoMonitoramento ──────────────────────────────────
    valor_lido = rng.uniform(0, 100, n).round(2)
    
    # 🔧 CORREÇÃO: Criar a lista de drones com None de forma correta
    drone_ids = dim_drone["id_drone"].tolist()
    drone_population = drone_ids + [None]
    # Pesos: 15% para cada drone (distribuído igualmente) + 85% para None
    drone_weights = [15 / len(drone_ids)] * len(drone_ids) + [85]
    
    fato = pd.DataFrame({
        "id_monitoramento": new_ids(n),
        "id_data": rand_dates(start, end, n),
        "id_talhao": random.choices(dim_talhao["id_talhao"].tolist(), k=n),
        "id_sensor": random.choices(dim_sensor["id_sensor"].tolist(), k=n),
        "id_drone": random.choices(drone_population, weights=drone_weights, k=n),
        "valor_lido": valor_lido,
        "unidade": random.choices(["%", "°C", "pH", "µS/cm", "mg/kg", "mmol", "Pa"], k=n),
        "valor_esperado": (valor_lido * rng.uniform(0.85, 1.15, n)).round(2),
        "anomalia_detectada": random.choices([True, False], weights=[8, 92], k=n),
        "recomendacao": random.choices(RECOMENDACOES + [None], weights=[15]*8 + [5], k=n),
        "data_hora_leitura": rand_dates(start, end, n),
        "custo_operacional": rng.uniform(0.5, 500, n).round(2),
        "produtividade_estimada_tha": rng.uniform(20, 120, n).round(1),
        "tempo_analise_seg": rng.integers(1, 300, n),
    })

    return {
        "DimFazenda": dim_fazenda,
        "DimTalhao": dim_talhao,
        "DimSensor": dim_sensor,
        "DimDrone": dim_drone,
        "FatoMonitoramento": fato,
        "dCalendario": dcalendario(start, end),
    }
