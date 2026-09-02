"""generators/corretora_investimentos.py — Setor Corretora de Investimentos."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

CLASSES_ATIVO = ["Ação", "Fundo Imobiliário", "Renda Fixa", "Tesouro Direto", "ETF", "Criptoativo"]
TIPOS_ORDEM = ["Compra", "Venda"]
PERFIS = ["Conservador", "Moderado", "Arrojado"]
CERTIFICACOES = ["CEA", "CFP", "CPA-10", "CPA-20"]


def gerar_corretora_investimentos(n, start, end):
    n = max(int(n), 1)

    n_assessor = min(max(n // 150, 6), 80)
    dim_assessor = pd.DataFrame({
        "id_assessor":       new_ids(n_assessor),
        "nome":              fake_pool(fake, "name", n_assessor),
        "certificacao":      random.choices(CERTIFICACOES, k=n_assessor),
        "anos_experiencia":  rng.integers(1, 25, n_assessor),
    })

    n_cliente = min(max(n // 6, 100), 8000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              fake_pool(fake, "name", n_cliente),
        "perfil_investidor": random.choices(PERFIS, weights=[40, 40, 20], k=n_cliente),
        "id_assessor":       random.choices(dim_assessor["id_assessor"].tolist(), k=n_cliente),
    })

    n_ativo = min(max(n // 30, 20), 500)
    dim_ativo = pd.DataFrame({
        "id_ativo":          new_ids(n_ativo),
        "ticker":            [fake.lexify(text="????3").upper() for _ in range(n_ativo)],
        "classe_ativo":      random.choices(CLASSES_ATIVO, weights=[30, 15, 25, 10, 15, 5], k=n_ativo),
    })

    fato_ordem = pd.DataFrame({
        "id_ordem":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "id_ativo":          random.choices(dim_ativo["id_ativo"].tolist(), k=n),
        "tipo_ordem":        random.choices(TIPOS_ORDEM, weights=[52, 48], k=n),
        "quantidade":        rng.integers(1, 5000, n),
        "valor":             rng.uniform(50, 100000, n).round(2),
        "taxa_corretagem":   rng.uniform(0, 25, n).round(2),
    })

    n_cart = int(n_cliente * 2)
    fato_carteira = pd.DataFrame({
        "id_posicao":        new_ids(n_cart),
        "id_data":           rand_dates(start, end, n_cart),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n_cart),
        "valor_sob_gestao":  rng.uniform(1000, 2000000, n_cart).round(2),
        "rentabilidade_pct": rng.uniform(-15, 35, n_cart).round(2),
    })

    return {
        "DimAssessor": dim_assessor,
        "DimCliente": dim_cliente,
        "DimAtivo": dim_ativo,
        "FatoOrdem": fato_ordem,
        "FatoCarteira": fato_carteira,
        "dCalendario": dcalendario(start, end),
    }
