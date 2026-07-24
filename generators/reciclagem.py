"""generators/reciclagem.py — Setor Reciclagem & Gestão de Resíduos."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

MATERIAIS = ["Papel/Papelão", "Plástico", "Vidro", "Metal", "Eletrônico (E-lixo)", "Orgânico"]
ORIGENS = ["Residencial", "Comercial", "Industrial", "Coleta Seletiva Municipal"]
COMPRADORES = ["Indústria de Reciclagem", "Atravessador", "Exportação", "Cooperativa Parceira"]


def gerar_reciclagem(n, start, end):
    n = max(int(n), 1)

    n_material = min(max(n // 400, 6), 20)
    dim_material = pd.DataFrame({
        "id_material":       new_ids(n_material),
        "nome":              random.choices(MATERIAIS, k=n_material),
        "categoria":         random.choices(["Reciclável Seco", "Reciclável Úmido", "Especial"], weights=[70, 15, 15], k=n_material),
    })

    n_cooperativa = min(max(n // 150, 8), 300)
    dim_cooperativa = pd.DataFrame({
        "id_cooperativa":    new_ids(n_cooperativa),
        "nome":              [f"Cooperativa {fake.city()}" for _ in range(n_cooperativa)],
        "uf":                [fake.state_abbr() for _ in range(n_cooperativa)],
        "capacidade_ton_mes": rng.uniform(5, 500, n_cooperativa).round(1),
    })

    fato_coleta = pd.DataFrame({
        "id_coleta":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_material":       random.choices(dim_material["id_material"].tolist(), k=n),
        "id_cooperativa":    random.choices(dim_cooperativa["id_cooperativa"].tolist(), k=n),
        "peso_kg":           rng.uniform(5, 5000, n).round(1),
        "origem":            random.choices(ORIGENS, weights=[35, 30, 20, 15], k=n),
    })

    n_venda = int(n * 0.6)
    peso_kg = rng.uniform(50, 8000, n_venda).round(1)
    fato_venda_material = pd.DataFrame({
        "id_venda_material": new_ids(n_venda),
        "id_data":           rand_dates(start, end, n_venda),
        "id_material":       random.choices(dim_material["id_material"].tolist(), k=n_venda),
        "id_cooperativa":    random.choices(dim_cooperativa["id_cooperativa"].tolist(), k=n_venda),
        "peso_kg":           peso_kg,
        "preco_kg":          rng.uniform(0.1, 8, n_venda).round(2),
        "comprador":         random.choices(COMPRADORES, weights=[40, 20, 15, 25], k=n_venda),
    })

    return {
        "DimMaterial": dim_material,
        "DimCooperativa": dim_cooperativa,
        "FatoColeta": fato_coleta,
        "FatoVendaMaterial": fato_venda_material,
        "dCalendario": dcalendario(start, end),
    }
