"""generators/cobranca.py — Setor Cobrança & Recuperação de Crédito."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

TIPOS_DIVIDA = ["Cartão de Crédito", "Empréstimo Pessoal", "Financiamento", "Conta de Consumo"]
CANAIS = ["Telefone", "WhatsApp", "Carta", "App", "E-mail"]
STATUS = ["Quitado", "Em Andamento", "Quebrado"]


def gerar_cobranca(n, start, end):
    n = max(int(n), 1)

    n_carteira = min(max(n // 200, 5), 60)
    dim_carteira = pd.DataFrame({
        "id_carteira":       new_ids(n_carteira),
        "nome_credor":       fake_pool(fake, "company", n_carteira),
        "tipo_divida":       random.choices(TIPOS_DIVIDA, k=n_carteira),
    })

    n_devedor = min(max(n // 3, 300), 20000)
    dim_devedor = pd.DataFrame({
        "id_devedor":        new_ids(n_devedor),
        "id_carteira":       random.choices(dim_carteira["id_carteira"].tolist(), k=n_devedor),
        "nome":              fake_pool(fake, "name", n_devedor),
        "valor_original":    rng.uniform(200, 40000, n_devedor).round(2),
    })

    fato_negociacao = pd.DataFrame({
        "id_negociacao":     new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_devedor":        random.choices(dim_devedor["id_devedor"].tolist(), k=n),
        "canal":             random.choices(CANAIS, k=n),
        "desconto_pct":      rng.uniform(0, 80, n).round(1),
        "valor_acordado":    rng.uniform(100, 30000, n).round(2),
        "status":            random.choices(STATUS, weights=[45, 35, 20], k=n),
    })

    return {
        "DimCarteira": dim_carteira,
        "DimDevedor": dim_devedor,
        "FatoNegociacao": fato_negociacao,
        "dCalendario": dcalendario(start, end),
    }
