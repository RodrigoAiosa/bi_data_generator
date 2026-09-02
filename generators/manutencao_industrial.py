"""generators/manutencao_industrial.py — Setor Manutenção Industrial."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

ESPECIALIDADES     = ["Elétrica", "Mecânica", "Hidráulica", "Automação", "Caldeiraria"]
SEGMENTOS_INDUSTRIAIS = ["Metalurgia", "Alimentício", "Automotivo", "Químico", "Têxtil", "Papel & Celulose"]
TIPOS_MANUTENCAO   = ["Preventiva", "Corretiva", "Preditiva"]
STATUS_OS          = ["Concluída", "Em Andamento", "Aberta", "Cancelada"]
CATEGORIAS_PECA    = ["Rolamento", "Correia", "Sensor", "Válvula", "Motor Elétrico", "Filtro"]


def gerar_manutencao_industrial(n, start, end):
    n = max(int(n), 1)

    n_tecnico = min(max(n // 60, 8), 400)
    dim_tecnico = pd.DataFrame({
        "id_tecnico":        new_ids(n_tecnico),
        "nome":              fake_pool(fake, "name", n_tecnico),
        "especialidade":     random.choices(ESPECIALIDADES, k=n_tecnico),
        "anos_experiencia":  rng.integers(1, 30, n_tecnico),
    })

    n_cliente = min(max(n // 30, 15), 1500)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome_cliente":      fake_pool(fake, "company", n_cliente),
        "segmento_industrial": random.choices(SEGMENTOS_INDUSTRIAIS, k=n_cliente),
    })

    fato_os = pd.DataFrame({
        "id_os":             new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_tecnico":        random.choices(dim_tecnico["id_tecnico"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "tipo_manutencao":   random.choices(TIPOS_MANUTENCAO, weights=[50, 35, 15], k=n),
        "tempo_parado_h":    rng.uniform(0.5, 72, n).round(1),
        "custo":             rng.uniform(150, 45000, n).round(2),
        "status":            random.choices(STATUS_OS, weights=[70, 15, 10, 5], k=n),
    })

    n_peca = int(n * 0.6)
    fato_peca = pd.DataFrame({
        "id_peca_uso":       new_ids(n_peca),
        "id_data":           rand_dates(start, end, n_peca),
        "id_tecnico":        random.choices(dim_tecnico["id_tecnico"].tolist(), k=n_peca),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n_peca),
        "categoria_peca":    random.choices(CATEGORIAS_PECA, k=n_peca),
        "quantidade":        rng.integers(1, 10, n_peca),
        "custo":             rng.uniform(20, 8000, n_peca).round(2),
    })

    return {
        "DimTecnico": dim_tecnico,
        "DimCliente": dim_cliente,
        "FatoOrdemServico": fato_os,
        "FatoPeca": fato_peca,
        "dCalendario": dcalendario(start, end),
    }
