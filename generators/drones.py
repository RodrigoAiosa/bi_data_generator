"""generators/drones.py — Setor Drones & Serviços Aéreos."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_USO = ["Agrícola", "Inspeção Industrial", "Mapeamento", "Entrega", "Filmagem", "Segurança"]
SEGMENTOS_CLIENTE = ["Agronegócio", "Construção Civil", "Mídia", "Energia", "Varejo", "Governo"]
TIPOS_SERVICO = ["Pulverização", "Inspeção de Torres", "Levantamento Topográfico", "Entrega Expressa",
                  "Filmagem Aérea", "Monitoramento de Perímetro"]
STATUS_MISSAO = ["Concluída", "Em Andamento", "Cancelada", "Abortada (Clima)"]
TIPOS_MANUTENCAO = ["Preventiva", "Corretiva", "Troca de Bateria", "Calibração de Sensor"]


def gerar_drones(n, start, end):
    n = max(int(n), 1)

    n_drone = min(max(n // 30, 15), 800)
    dim_drone = pd.DataFrame({
        "id_drone":          new_ids(n_drone),
        "modelo":            [f"{random.choice(['DJI','Sensefly','Parrot','XMobots','Quantix'])} {fake.word().capitalize()}{rng.integers(100,999)}" for _ in range(n_drone)],
        "tipo_uso":          random.choices(TIPOS_USO, k=n_drone),
        "autonomia_min":     rng.integers(15, 90, n_drone),
    })

    n_cliente = min(max(n // 25, 20), 2000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.company() for _ in range(n_cliente)],
        "segmento":          random.choices(SEGMENTOS_CLIENTE, k=n_cliente),
        "uf":                [fake.state_abbr() for _ in range(n_cliente)],
    })

    status_missao = random.choices(STATUS_MISSAO, weights=[75, 10, 8, 7], k=n)
    fato_missao = pd.DataFrame({
        "id_missao":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_drone":          random.choices(dim_drone["id_drone"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "tipo_servico":      random.choices(TIPOS_SERVICO, k=n),
        "area_coberta_ha":   rng.uniform(1, 800, n).round(1),
        "duracao_min":       rng.integers(10, 240, n),
        "valor_cobrado":     rng.uniform(200, 45000, n).round(2),
        "status":            status_missao,
    })

    n_manut = int(n_drone * 2)
    fato_manutencao = pd.DataFrame({
        "id_manutencao":     new_ids(n_manut),
        "id_data":           rand_dates(start, end, n_manut),
        "id_drone":          random.choices(dim_drone["id_drone"].tolist(), k=n_manut),
        "tipo_manutencao":   random.choices(TIPOS_MANUTENCAO, weights=[40, 25, 25, 10], k=n_manut),
        "custo":             rng.uniform(50, 12000, n_manut).round(2),
        "horas_parado":      rng.uniform(1, 120, n_manut).round(1),
    })

    return {
        "DimDrone": dim_drone,
        "DimCliente": dim_cliente,
        "FatoMissao": fato_missao,
        "FatoManutencao": fato_manutencao,
        "dCalendario": dcalendario(start, end),
    }
