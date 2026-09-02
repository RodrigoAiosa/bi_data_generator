"""generators/agencia_noticias.py — Setor Agência de Notícias."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

EDITORIAS = ["Política", "Economia", "Esportes", "Cultura", "Internacional", "Tecnologia"]
TIPOS_VEICULO = ["Jornal", "TV", "Rádio", "Portal"]
PLANOS = ["Básico", "Premium", "Corporativo"]


def gerar_agencia_noticias(n, start, end):
    n = max(int(n), 1)

    n_jornalista = min(max(n // 50, 10), 300)
    dim_jornalista = pd.DataFrame({
        "id_jornalista":     new_ids(n_jornalista),
        "nome":              fake_pool(fake, "name", n_jornalista),
        "editoria":          random.choices(EDITORIAS, k=n_jornalista),
    })

    n_veiculo = min(max(n // 30, 20), 800)
    dim_veiculo = pd.DataFrame({
        "id_veiculo":        new_ids(n_veiculo),
        "nome_veiculo":      fake_pool(fake, "company", n_veiculo),
        "tipo_veiculo":      random.choices(TIPOS_VEICULO, weights=[35, 15, 15, 35], k=n_veiculo),
        "plano_assinatura":  random.choices(PLANOS, weights=[50, 35, 15], k=n_veiculo),
    })

    fato_materia = pd.DataFrame({
        "id_materia":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_jornalista":     random.choices(dim_jornalista["id_jornalista"].tolist(), k=n),
        "categoria":         random.choices(EDITORIAS, k=n),
        "palavras":          rng.integers(150, 3500, n),
        "valor_licenciamento": rng.uniform(30, 900, n).round(2),
    })

    n_dist = int(n * 1.5)
    fato_distribuicao = pd.DataFrame({
        "id_distribuicao":   new_ids(n_dist),
        "id_data":           rand_dates(start, end, n_dist),
        "id_materia":        random.choices(fato_materia["id_materia"].tolist(), k=n_dist),
        "id_veiculo":        random.choices(dim_veiculo["id_veiculo"].tolist(), k=n_dist),
        "valor_repasse":     rng.uniform(10, 400, n_dist).round(2),
    })

    return {
        "DimJornalista": dim_jornalista,
        "DimVeiculoAssinante": dim_veiculo,
        "FatoMateria": fato_materia,
        "FatoDistribuicao": fato_distribuicao,
        "dCalendario": dcalendario(start, end),
    }
