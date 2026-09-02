"""generators/porto.py — Setor Porto & Terminal Portuário."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

TIPOS_NAVIO      = ["Contêiner", "Granel Sólido", "Granel Líquido", "Petroleiro", "Ro-Ro", "Cargueiro Geral"]
TIPOS_CARGA      = ["Contêiner", "Minério", "Grãos", "Combustível", "Veículos", "Carga Geral"]
STATUS_ATRACACAO = ["Concluída", "Em Andamento", "Aguardando Berço", "Cancelada"]


def gerar_porto(n, start, end):
    n = max(int(n), 1)

    n_terminal = min(max(n // 300, 3), 25)
    dim_terminal = pd.DataFrame({
        "id_terminal":       new_ids(n_terminal),
        "nome":              [f"Terminal {fake.city()}" for _ in range(n_terminal)],
        "uf":                fake_pool(fake, "state_abbr", n_terminal),
        "num_beracos":       rng.integers(1, 8, n_terminal),
        "capacidade_teu_ano": rng.integers(50000, 2000000, n_terminal),
    })

    n_navio = min(max(n // 15, 40), 3000)
    dim_navio = pd.DataFrame({
        "id_navio":          new_ids(n_navio),
        "nome":              [f"MV {fake.last_name()}" for _ in range(n_navio)],
        "tipo":              random.choices(TIPOS_NAVIO, weights=[35, 20, 15, 10, 10, 10], k=n_navio),
        "bandeira":          fake_pool(fake, "country", n_navio),
        "capacidade_dwt":    rng.integers(5000, 300000, n_navio),
    })

    status_atracacao = random.choices(STATUS_ATRACACAO, weights=[70, 15, 10, 5], k=n)
    fato_atracacao = pd.DataFrame({
        "id_atracacao":      new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_terminal":       random.choices(dim_terminal["id_terminal"].tolist(), k=n),
        "id_navio":          random.choices(dim_navio["id_navio"].tolist(), k=n),
        "tipo_carga":        random.choices(TIPOS_CARGA, weights=[35, 15, 15, 15, 10, 10], k=n),
        "tempo_atracado_h":  rng.uniform(4, 96, n).round(1),
        "status":            status_atracacao,
    })

    n_movimentacao = int(n * 1.6)
    fato_movimentacao = pd.DataFrame({
        "id_movimentacao":   new_ids(n_movimentacao),
        "id_data":           rand_dates(start, end, n_movimentacao),
        "id_terminal":       random.choices(dim_terminal["id_terminal"].tolist(), k=n_movimentacao),
        "id_navio":          random.choices(dim_navio["id_navio"].tolist(), k=n_movimentacao),
        "tipo_carga":        random.choices(TIPOS_CARGA, weights=[35, 15, 15, 15, 10, 10], k=n_movimentacao),
        "toneladas":         rng.uniform(50, 45000, n_movimentacao).round(1),
        "teus":              rng.integers(0, 3500, n_movimentacao),
        "valor_tarifa":      rng.uniform(800, 180000, n_movimentacao).round(2),
    })

    return {
        "DimTerminal": dim_terminal,
        "DimNavio": dim_navio,
        "FatoAtracacao": fato_atracacao,
        "FatoMovimentacaoCarga": fato_movimentacao,
        "dCalendario": dcalendario(start, end),
    }
