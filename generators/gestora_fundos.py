"""generators/gestora_fundos.py — Setor Gestora de Fundos & Asset Management."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_FUNDO = ["Renda Fixa", "Multimercado", "Ações", "Cambial", "Imobiliário"]
PERFIS = ["Conservador", "Moderado", "Arrojado"]


def gerar_gestora_fundos(n, start, end):
    n = max(int(n), 1)

    n_gestora = min(max(n // 500, 3), 30)
    dim_gestora = pd.DataFrame({
        "id_gestora":        new_ids(n_gestora),
        "nome_gestora":      [fake.company() for _ in range(n_gestora)],
    })

    n_fundo = min(max(n // 50, 10), 400)
    dim_fundo = pd.DataFrame({
        "id_fundo":          new_ids(n_fundo),
        "id_gestora":        random.choices(dim_gestora["id_gestora"].tolist(), k=n_fundo),
        "nome_fundo":        [f"Fundo {fake.word().capitalize()} {random.choice(TIPOS_FUNDO)}" for _ in range(n_fundo)],
        "tipo":              random.choices(TIPOS_FUNDO, k=n_fundo),
        "taxa_administracao_pct": rng.uniform(0.3, 3.5, n_fundo).round(2),
    })

    n_cotista = min(max(n // 3, 200), 15000)
    dim_cotista = pd.DataFrame({
        "id_cotista":        new_ids(n_cotista),
        "nome":              [fake.name() for _ in range(n_cotista)],
        "perfil":            random.choices(PERFIS, weights=[35, 40, 25], k=n_cotista),
    })

    fato_movimentacao = pd.DataFrame({
        "id_movimentacao":   new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_fundo":          random.choices(dim_fundo["id_fundo"].tolist(), k=n),
        "id_cotista":        random.choices(dim_cotista["id_cotista"].tolist(), k=n),
        "tipo_operacao":     random.choices(["Aplicação", "Resgate"], weights=[60, 40], k=n),
        "valor":             rng.uniform(500, 500000, n).round(2),
        "cota_valor":        rng.uniform(1, 500, n).round(4),
    })

    return {
        "DimGestora": dim_gestora,
        "DimFundo": dim_fundo,
        "DimCotista": dim_cotista,
        "FatoMovimentacao": fato_movimentacao,
        "dCalendario": dcalendario(start, end),
    }
