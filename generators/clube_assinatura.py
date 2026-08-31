"""generators/clube_assinatura.py — Setor Clube de Assinaturas."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TEMAS_CAIXA   = ["Beleza", "Livros", "Café Especial", "Vinhos", "Pet", "Fitness", "Games"]
PLANOS        = ["Mensal", "Trimestral", "Semestral", "Anual"]
STATUS_ASSINATURA = ["Ativa", "Cancelada", "Pendente", "Pausada"]
STATUS_ENTREGA = ["Entregue", "Em Trânsito", "Atrasada", "Extraviada"]


def gerar_clube_assinatura(n, start, end):
    n = max(int(n), 1)

    n_caixa = min(max(n // 80, 5), 60)
    dim_caixa = pd.DataFrame({
        "id_caixa":          new_ids(n_caixa),
        "tema":              random.choices(TEMAS_CAIXA, k=n_caixa),
        "valor_base":        rng.uniform(39.9, 249.9, n_caixa).round(2),
    })

    n_assinante = min(max(n // 3, 200), 30000)
    dim_assinante = pd.DataFrame({
        "id_assinante":      new_ids(n_assinante),
        "nome":              [fake.name() for _ in range(n_assinante)],
        "uf":                [fake.state_abbr() for _ in range(n_assinante)],
    })

    status_assinatura = random.choices(STATUS_ASSINATURA, weights=[65, 20, 8, 7], k=n)
    fato_assinatura = pd.DataFrame({
        "id_assinatura":     new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_assinante":      random.choices(dim_assinante["id_assinante"].tolist(), k=n),
        "id_caixa":          random.choices(dim_caixa["id_caixa"].tolist(), k=n),
        "plano":             random.choices(PLANOS, weights=[50, 20, 15, 15], k=n),
        "ciclo_cobranca":    rng.integers(1, 12, n),
        "status":            status_assinatura,
        "valor":             rng.uniform(29.9, 299.9, n).round(2),
        "churn":             [s == "Cancelada" for s in status_assinatura],
    })

    n_envio = int(n * 0.9)
    fato_envio = pd.DataFrame({
        "id_envio":          new_ids(n_envio),
        "id_data":           rand_dates(start, end, n_envio),
        "id_assinante":      random.choices(dim_assinante["id_assinante"].tolist(), k=n_envio),
        "id_caixa":          random.choices(dim_caixa["id_caixa"].tolist(), k=n_envio),
        "status_entrega":    random.choices(STATUS_ENTREGA, weights=[80, 12, 6, 2], k=n_envio),
        "avaliacao":         rng.integers(1, 5, n_envio),
    })

    return {
        "DimCaixa": dim_caixa,
        "DimAssinante": dim_assinante,
        "FatoAssinatura": fato_assinatura,
        "FatoEnvio": fato_envio,
        "dCalendario": dcalendario(start, end),
    }
