"""generators/agronegocio.py — Setor Agronegócio."""

import random
from datetime import date

import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CULTURAS_NOMES = [
    "Soja","Milho","Cana-de-açúcar","Algodão","Café","Trigo",
    "Arroz","Feijão","Laranja","Eucalipto","Sorgo","Girassol",
    "Amendoim","Mandioca","Cacau","Mamona","Canola","Aveia","Cevada","Fumo",
]
UFS_AGRO = ["MT","MS","GO","SP","PR","RS","SC","MG","BA","PI"]


def gerar_agronegocio(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_propriedades = min(n // 5 + 50, 500)
    n_culturas     = 20
    n_insumos      = 40

    dim_cultura = pd.DataFrame({
        "id_cultura": new_ids(n_culturas),
        "nome":       CULTURAS_NOMES,
        "tipo":       random.choices(["Grão","Fibra","Fruta","Hortaliça","Energia"], k=n_culturas),
        "ciclo_dias": rng.integers(60, 365, n_culturas),
        "preco_ton":  rng.uniform(500, 8000, n_culturas).round(2),
    })

    dim_propriedade = pd.DataFrame({
        "id_propriedade": new_ids(n_propriedades),
        "nome":           [f"Fazenda {fake.last_name()}" for _ in range(n_propriedades)],
        "cnpj_cpf":       [fake.cpf() for _ in range(n_propriedades)],
        "area_ha":        rng.uniform(10, 50000, n_propriedades).round(1),
        "uf":             random.choices(UFS_AGRO, k=n_propriedades),
        "bioma":          random.choices(["Cerrado","Amazônia","Mata Atlântica","Pampa","Pantanal"], k=n_propriedades),
        "tipo":           random.choices(["Familiar","Empresarial","Cooperativa"], k=n_propriedades),
    })

    dim_insumo = pd.DataFrame({
        "id_insumo":  new_ids(n_insumos),
        "nome":       [f"Insumo {fake.word().capitalize()}" for _ in range(n_insumos)],
        "tipo":       random.choices(["Fertilizante","Defensivo","Semente","Combustível","Irrigação"], k=n_insumos),
        "unidade":    random.choices(["kg","litro","saco","dose"], k=n_insumos),
        "custo_unit": rng.uniform(10, 2000, n_insumos).round(2),
    })

    area_plantada = rng.uniform(5, 5000, n).round(1)
    prod_por_ha   = rng.uniform(1, 10, n).round(2)

    fato = pd.DataFrame({
        "id_safra":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_propriedade":    random.choices(dim_propriedade["id_propriedade"].tolist(), k=n),
        "id_cultura":        random.choices(dim_cultura["id_cultura"].tolist(), k=n),
        "id_insumo":         random.choices(dim_insumo["id_insumo"].tolist(), k=n),
        "area_plantada_ha":  area_plantada,      # ← NOME CORRETO COM _ha
        "produtividade_tha": prod_por_ha,
        "producao_ton":      (area_plantada * prod_por_ha).round(2),
        "custo_ha":          rng.uniform(500, 8000, n).round(2),
        "custo_total":       (area_plantada * rng.uniform(500, 8000, n)).round(2),  # ← NOVA COLUNA
        "receita":           rng.uniform(1000, 500000, n).round(2),
        "indice_chuva_mm":   rng.uniform(0, 300, n).round(1),
        "temperatura_media": rng.uniform(15, 35, n).round(1),
        "status":            random.choices(
            ["Colhida","Em andamento","Planejada","Perdida"],
            weights=[50, 30, 15, 5], k=n,
        ),
    })

    return {
        "DimCultura":     dim_cultura,
        "DimPropriedade": dim_propriedade,
        "DimInsumo":      dim_insumo,
        "FatoSafra":      fato,
        "dCalendario":    dcalendario(start, end),
    }
