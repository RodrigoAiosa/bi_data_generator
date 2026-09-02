"""generators/biocombustiveis.py — Setor Biocombustíveis."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

MATERIAS_PRIMA = ["Cana-de-Açúcar", "Soja", "Milho", "Óleo Reciclado", "Sebo Animal"]
TIPOS_COMBUSTIVEL = ["Etanol Hidratado", "Etanol Anidro", "Biodiesel B100", "Bioquerosene"]
TIPOS_CLIENTE  = ["Distribuidora", "Indústria", "Posto Revendedor", "Exportação"]


def gerar_biocombustiveis(n, start, end):
    n = max(int(n), 1)

    n_usina = min(max(n // 150, 3), 40)
    dim_usina = pd.DataFrame({
        "id_usina":          new_ids(n_usina),
        "cidade":            fake_pool(fake, "city", n_usina),
        "uf":                fake_pool(fake, "state_abbr", n_usina),
        "capacidade_litros_dia": rng.integers(50000, 2000000, n_usina),
    })

    dim_materiaprima = pd.DataFrame({
        "id_materiaprima":   new_ids(len(MATERIAS_PRIMA)),
        "nome":              MATERIAS_PRIMA,
    })

    n_producao = min(max(n, 200), 40000)
    fato_producao = pd.DataFrame({
        "id_producao":       new_ids(n_producao),
        "id_data":           rand_dates(start, end, n_producao),
        "id_usina":          random.choices(dim_usina["id_usina"].tolist(), k=n_producao),
        "id_materiaprima":   random.choices(dim_materiaprima["id_materiaprima"].tolist(), k=n_producao),
        "tipo_combustivel":  random.choices(TIPOS_COMBUSTIVEL, weights=[45, 25, 25, 5], k=n_producao),
        "volume_litros":     rng.uniform(5000, 500000, n_producao).round(0),
        "rendimento_pct":    rng.uniform(65, 95, n_producao).round(1),
    })

    n_venda = int(n_producao * 0.8)
    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n_venda),
        "id_data":           rand_dates(start, end, n_venda),
        "id_usina":          random.choices(dim_usina["id_usina"].tolist(), k=n_venda),
        "tipo_cliente":      random.choices(TIPOS_CLIENTE, weights=[45, 20, 20, 15], k=n_venda),
        "volume_litros":     rng.uniform(1000, 300000, n_venda).round(0),
        "preco_litro":       rng.uniform(2.2, 5.8, n_venda).round(3),
    })

    return {
        "DimUsina": dim_usina,
        "DimMateriaPrima": dim_materiaprima,
        "FatoProducao": fato_producao,
        "FatoVenda": fato_venda,
        "dCalendario": dcalendario(start, end),
    }
