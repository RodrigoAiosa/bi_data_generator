"""generators/zoologico.py — Setor Zoológico & Aquário."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CLASSES_ANIMAL = ["Mamífero", "Ave", "Réptil", "Peixe", "Anfíbio", "Invertebrado"]
CATEGORIAS_INGRESSO = ["Inteira", "Meia-Entrada", "Criança", "Idoso", "Gratuito (PCD)", "Passe Anual"]
CANAIS_VENDA = ["Bilheteria", "Site Oficial", "Aplicativo de Ingressos", "Escola/Excursão"]
TIPOS_MANEJO = ["Alimentação", "Consulta Veterinária", "Enriquecimento Ambiental", "Procedimento Cirúrgico", "Vacinação"]


def gerar_zoologico(n, start, end):
    n = max(int(n), 1)

    n_recinto = min(max(n // 300, 8), 150)
    dim_recinto = pd.DataFrame({
        "id_recinto":        new_ids(n_recinto),
        "nome":              [f"Recinto {fake.word().capitalize()}" for _ in range(n_recinto)],
        "bioma":             random.choices(["Savana Africana", "Floresta Tropical", "Pantanal", "Cerrado", "Recife de Corais", "Mata Atlântica"], k=n_recinto),
        "area_m2":           rng.uniform(50, 8000, n_recinto).round(1),
    })

    n_animal = min(max(n // 40, 40), 3000)
    dim_animal = pd.DataFrame({
        "id_animal":         new_ids(n_animal),
        "id_recinto":        random.choices(dim_recinto["id_recinto"].tolist(), k=n_animal),
        "especie":           [fake.word().capitalize() for _ in range(n_animal)],
        "classe":            random.choices(CLASSES_ANIMAL, weights=[25, 30, 15, 15, 10, 5], k=n_animal),
        "idade_anos":        rng.integers(0, 60, n_animal),
        "em_risco_extincao": random.choices([True, False], weights=[20, 80], k=n_animal),
    })

    categoria_ing = random.choices(CATEGORIAS_INGRESSO, weights=[45, 20, 15, 10, 5, 5], k=n)
    valor_base = {"Inteira": 80, "Meia-Entrada": 40, "Criança": 30, "Idoso": 0, "Gratuito (PCD)": 0, "Passe Anual": 350}
    fato_ingresso = pd.DataFrame({
        "id_ingresso":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "categoria_ingresso": categoria_ing,
        "canal_venda":       random.choices(CANAIS_VENDA, weights=[40, 30, 20, 10], k=n),
        "valor":             [round(valor_base[c] * rng.uniform(0.9, 1.15), 2) for c in categoria_ing],
        "visitou_aquario":   random.choices([True, False], weights=[65, 35], k=n),
    })

    n_manejo = int(n_animal * 6)
    fato_manejo = pd.DataFrame({
        "id_manejo":         new_ids(n_manejo),
        "id_data":           rand_dates(start, end, n_manejo),
        "id_animal":         random.choices(dim_animal["id_animal"].tolist(), k=n_manejo),
        "tipo_manejo":       random.choices(TIPOS_MANEJO, weights=[45, 25, 15, 5, 10], k=n_manejo),
        "custo":             rng.uniform(10, 3500, n_manejo).round(2),
        "duracao_min":       rng.integers(5, 240, n_manejo),
    })

    return {
        "DimRecinto": dim_recinto,
        "DimAnimal": dim_animal,
        "FatoIngresso": fato_ingresso,
        "FatoManejo": fato_manejo,
        "dCalendario": dcalendario(start, end),
    }
