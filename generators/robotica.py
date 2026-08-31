"""generators/robotica.py — Setor Robótica & Automação Industrial."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_ROBO = ["Braço Robótico", "AGV", "Cobot", "Robô de Solda", "Robô de Pintura"]
SETORES_INDUSTRIAIS = ["Automotivo", "Alimentício", "Metalurgia", "Eletrônicos", "Farmacêutico"]


def gerar_robotica(n, start, end):
    n = max(int(n), 1)

    n_fabrica_cliente = min(max(n // 100, 8), 800)
    dim_fabrica_cliente = pd.DataFrame({
        "id_fabrica_cliente": new_ids(n_fabrica_cliente),
        "nome":              [fake.company() for _ in range(n_fabrica_cliente)],
        "setor_industrial":  random.choices(SETORES_INDUSTRIAIS, k=n_fabrica_cliente),
    })

    n_robo = min(max(n // 30, 15), 1500)
    dim_robo = pd.DataFrame({
        "id_robo":           new_ids(n_robo),
        "tipo":              random.choices(TIPOS_ROBO, k=n_robo),
        "fabricante":        random.choices(["ABB", "Kuka", "Fanuc", "Yaskawa", "Universal Robots"], k=n_robo),
    })

    fato_projeto = pd.DataFrame({
        "id_projeto":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_fabrica_cliente": random.choices(dim_fabrica_cliente["id_fabrica_cliente"].tolist(), k=n),
        "id_robo":           random.choices(dim_robo["id_robo"].tolist(), k=n),
        "valor_investimento": rng.uniform(50000, 4000000, n).round(2),
        "ganho_produtividade_pct": rng.uniform(5, 60, n).round(1),
    })

    return {
        "DimFabricaCliente": dim_fabrica_cliente,
        "DimRobo": dim_robo,
        "FatoProjetoAutomacao": fato_projeto,
        "dCalendario": dcalendario(start, end),
    }
