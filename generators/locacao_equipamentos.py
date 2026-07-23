"""generators/locacao_equipamentos.py — Setor Locação de Equipamentos."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS_EQUIP = ["Betoneira", "Andaime", "Gerador", "Compactador de Solo", "Plataforma Elevatória",
                     "Furadeira Industrial", "Compressor de Ar", "Guincho"]
STATUS_EQUIP = ["Disponível", "Locado", "Em Manutenção", "Baixado"]
SEGMENTOS_CLIENTE = ["Construção Civil", "Eventos", "Indústria", "Pessoa Física", "Prefeitura"]
TIPOS_MANUTENCAO = ["Preventiva", "Corretiva", "Revisão Programada"]


def gerar_locacao_equipamentos(n, start, end):
    n = max(int(n), 1)

    n_equipamento = min(max(n // 20, 30), 2000)
    dim_equipamento = pd.DataFrame({
        "id_equipamento":    new_ids(n_equipamento),
        "nome":              [f"{random.choice(CATEGORIAS_EQUIP)} {fake.word().capitalize()}{rng.integers(100,999)}" for _ in range(n_equipamento)],
        "categoria":         random.choices(CATEGORIAS_EQUIP, k=n_equipamento),
        "valor_diaria":      rng.uniform(40, 1200, n_equipamento).round(2),
        "status":            random.choices(STATUS_EQUIP, weights=[40, 45, 12, 3], k=n_equipamento),
    })

    n_cliente = min(max(n // 8, 100), 8000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.company() if random.random() < 0.7 else fake.name() for _ in range(n_cliente)],
        "segmento":          random.choices(SEGMENTOS_CLIENTE, k=n_cliente),
        "uf":                [fake.state_abbr() for _ in range(n_cliente)],
    })

    dias = rng.integers(1, 60, n)
    equip_idx = random.choices(range(n_equipamento), k=n)
    diaria = dim_equipamento["valor_diaria"].to_numpy()[equip_idx]
    fato_locacao = pd.DataFrame({
        "id_locacao":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_equipamento":    dim_equipamento["id_equipamento"].to_numpy()[equip_idx],
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "dias_locados":      dias,
        "valor_diaria":      diaria.round(2),
        "valor_total":       (dias * diaria).round(2),
        "seguro_contratado": random.choices([True, False], weights=[40, 60], k=n),
        "devolvido_com_avaria": random.choices([True, False], weights=[7, 93], k=n),
    })

    n_manutencao = int(n_equipamento * 1.5)
    fato_manutencao = pd.DataFrame({
        "id_manutencao":     new_ids(n_manutencao),
        "id_data":           rand_dates(start, end, n_manutencao),
        "id_equipamento":    random.choices(dim_equipamento["id_equipamento"].tolist(), k=n_manutencao),
        "tipo_manutencao":   random.choices(TIPOS_MANUTENCAO, weights=[50, 35, 15], k=n_manutencao),
        "custo":             rng.uniform(50, 5000, n_manutencao).round(2),
        "dias_parado":       rng.integers(1, 15, n_manutencao),
    })

    return {
        "DimEquipamento": dim_equipamento,
        "DimCliente": dim_cliente,
        "FatoLocacao": fato_locacao,
        "FatoManutencao": fato_manutencao,
        "dCalendario": dcalendario(start, end),
    }
