"""generators/vinicola.py — Setor Vinícola & Vitivinicultura."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_VINHO = ["Tinto", "Branco", "Rosé", "Espumante"]
UVAS = ["Cabernet Sauvignon", "Merlot", "Chardonnay", "Pinot Noir", "Malbec", "Moscato", "Tannat"]
REGIOES = ["Serra Gaúcha", "Vale dos Vinhedos", "Vale do São Francisco", "Campanha Gaúcha", "Vale do Rio do Peixe"]
CANAIS_VENDA = ["Vinícola (Loja Física)", "Distribuidor", "Exportação", "E-commerce", "Restaurantes"]


def gerar_vinicola(n, start, end):
    n = max(int(n), 1)

    n_vinho = min(max(n // 30, 15), 400)
    dim_vinho = pd.DataFrame({
        "id_vinho":          new_ids(n_vinho),
        "nome":              [f"{random.choice(UVAS)} {rng.integers(2015,2025)}" for _ in range(n_vinho)],
        "tipo":              random.choices(TIPOS_VINHO, weights=[45, 30, 10, 15], k=n_vinho),
        "uva":               random.choices(UVAS, k=n_vinho),
        "safra":             rng.integers(2015, 2025, n_vinho),
        "preco":             rng.uniform(28, 850, n_vinho).round(2),
    })

    n_vinhedo = min(max(n // 150, 5), 60)
    dim_vinhedo = pd.DataFrame({
        "id_vinhedo":        new_ids(n_vinhedo),
        "nome":              [f"Vinhedo {fake.last_name()}" for _ in range(n_vinhedo)],
        "regiao":            random.choices(REGIOES, k=n_vinhedo),
        "area_ha":           rng.uniform(2, 150, n_vinhedo).round(1),
        "altitude_m":        rng.integers(400, 1200, n_vinhedo),
    })

    fato_producao = pd.DataFrame({
        "id_producao":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_vinhedo":        random.choices(dim_vinhedo["id_vinhedo"].tolist(), k=n),
        "id_vinho":          random.choices(dim_vinho["id_vinho"].tolist(), k=n),
        "litros_produzidos": rng.uniform(200, 60000, n).round(1),
        "qualidade_uva":     rng.uniform(60, 100, n).round(1),
        "rendimento_ha":     rng.uniform(3000, 12000, n).round(1),
    })

    n_venda = int(n * 1.2)
    qtd = rng.integers(1, 24, n_venda)
    venda_idx = random.choices(range(n_vinho), k=n_venda)
    preco_unit = dim_vinho["preco"].to_numpy()[venda_idx]
    fato_venda = pd.DataFrame({
        "id_venda_vinho":    new_ids(n_venda),
        "id_data":           rand_dates(start, end, n_venda),
        "id_vinho":          dim_vinho["id_vinho"].to_numpy()[venda_idx],
        "quantidade_garrafas": qtd,
        "valor_total":       (qtd * preco_unit).round(2),
        "canal":             random.choices(CANAIS_VENDA, weights=[25, 30, 15, 20, 10], k=n_venda),
    })

    return {
        "DimVinho": dim_vinho,
        "DimVinhedo": dim_vinhedo,
        "FatoProducao": fato_producao,
        "FatoVenda": fato_venda,
        "dCalendario": dcalendario(start, end),
    }
