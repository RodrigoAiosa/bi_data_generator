"""generators/pecuaria.py — Setor Pecuária."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_CRIACAO = ["Corte", "Leite", "Misto"]
RACAS = ["Nelore", "Angus", "Girolando", "Brahman", "Holandesa", "Gir", "Hereford"]
CATEGORIAS_ANIMAL = ["Bezerro", "Novilho", "Boi Gordo", "Vaca", "Touro"]
TIPOS_MANEJO = ["Vacinação", "Pesagem", "Reprodução", "Venda", "Descorna", "Vermifugação"]


def gerar_pecuaria(n, start, end):
    n = max(int(n), 1)

    n_fazenda = min(max(n // 100, 10), 400)
    dim_fazenda = pd.DataFrame({
        "id_fazenda":        new_ids(n_fazenda),
        "nome":              [f"Fazenda {fake.last_name()}" for _ in range(n_fazenda)],
        "uf":                [fake.state_abbr() for _ in range(n_fazenda)],
        "area_ha":           rng.uniform(50, 15000, n_fazenda).round(1),
        "tipo_criacao":      random.choices(TIPOS_CRIACAO, weights=[50, 25, 25], k=n_fazenda),
    })

    n_lote = min(max(n // 20, 30), 3000)
    dim_lote = pd.DataFrame({
        "id_lote":           new_ids(n_lote),
        "raca":              random.choices(RACAS, k=n_lote),
        "categoria":         random.choices(CATEGORIAS_ANIMAL, weights=[25, 25, 25, 20, 5], k=n_lote),
        "peso_medio_kg":     rng.uniform(80, 650, n_lote).round(1),
    })

    fato_manejo = pd.DataFrame({
        "id_manejo":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_fazenda":        random.choices(dim_fazenda["id_fazenda"].tolist(), k=n),
        "id_lote":           random.choices(dim_lote["id_lote"].tolist(), k=n),
        "tipo_manejo":       random.choices(TIPOS_MANEJO, k=n),
        "quantidade_animais": rng.integers(1, 500, n),
        "custo":             rng.uniform(50, 15000, n).round(2),
    })

    n_prod = int(n * 0.8)
    fato_producao = pd.DataFrame({
        "id_producao":       new_ids(n_prod),
        "id_data":           rand_dates(start, end, n_prod),
        "id_fazenda":        random.choices(dim_fazenda["id_fazenda"].tolist(), k=n_prod),
        "id_lote":           random.choices(dim_lote["id_lote"].tolist(), k=n_prod),
        "producao_leite_litros": rng.uniform(0, 25000, n_prod).round(1),
        "ganho_peso_kg":     rng.uniform(-5, 45, n_prod).round(1),
        "mortalidade":       rng.integers(0, 10, n_prod),
        "receita":           rng.uniform(0, 180000, n_prod).round(2),
    })

    return {
        "DimFazenda": dim_fazenda,
        "DimLote": dim_lote,
        "FatoManejo": fato_manejo,
        "FatoProducao": fato_producao,
        "dCalendario": dcalendario(start, end),
    }
