"""generators/cervejaria.py — Setor Cervejaria Artesanal."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

ESTILOS = ["IPA", "Pilsen", "Weiss", "Stout", "APA", "Session IPA", "Lager", "Red Ale"]
TIPOS_PONTO_VENDA = ["Bar", "Distribuidora", "Loja Própria", "Supermercado", "E-commerce"]


def gerar_cervejaria(n, start, end):
    n = max(int(n), 1)

    n_cerveja = min(max(n // 100, 6), 150)
    dim_cerveja = pd.DataFrame({
        "id_cerveja":        new_ids(n_cerveja),
        "estilo":            random.choices(ESTILOS, k=n_cerveja),
        "teor_alcoolico_pct": rng.uniform(3.5, 9.5, n_cerveja).round(1),
        "ibu":               rng.integers(10, 90, n_cerveja),
    })

    n_ponto = min(max(n // 40, 10), 800)
    dim_ponto_venda = pd.DataFrame({
        "id_pontovenda":     new_ids(n_ponto),
        "tipo":              random.choices(TIPOS_PONTO_VENDA, weights=[35, 25, 10, 20, 10], k=n_ponto),
        "cidade":            [fake.city() for _ in range(n_ponto)],
    })

    n_lote = min(max(n // 5, 100), 20000)
    fato_producao_lote = pd.DataFrame({
        "id_lote":           new_ids(n_lote),
        "id_data":           rand_dates(start, end, n_lote),
        "id_cerveja":        random.choices(dim_cerveja["id_cerveja"].tolist(), k=n_lote),
        "volume_litros":     rng.uniform(200, 8000, n_lote).round(0),
        "custo":             rng.uniform(800, 25000, n_lote).round(2),
        "aprovado_qualidade": random.choices([True, False], weights=[95, 5], k=n_lote),
    })

    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_cerveja":        random.choices(dim_cerveja["id_cerveja"].tolist(), k=n),
        "id_pontovenda":     random.choices(dim_ponto_venda["id_pontovenda"].tolist(), k=n),
        "quantidade_litros": rng.uniform(5, 500, n).round(1),
        "valor":             rng.uniform(30, 4500, n).round(2),
    })

    return {
        "DimCerveja": dim_cerveja,
        "DimPontoVenda": dim_ponto_venda,
        "FatoProducaoLote": fato_producao_lote,
        "FatoVenda": fato_venda,
        "dCalendario": dcalendario(start, end),
    }
