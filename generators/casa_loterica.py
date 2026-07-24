"""generators/casa_loterica.py — Setor Casa Lotérica & Correspondente Bancário."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

SERVICOS = ["Loteria", "Pagamento de Contas", "Saque INSS/Bolsa Família", "Recarga de Celular",
             "Correspondente Bancário", "Envio de Dinheiro"]
CATEGORIAS_SERVICO = ["Jogo", "Bancário", "Utilidade"]
MODALIDADES_LOTERIA = ["Mega-Sena", "Lotofácil", "Quina", "Lotomania", "Dupla Sena", "Timemania"]


def gerar_casa_loterica(n, start, end):
    n = max(int(n), 1)

    n_unidade = min(max(n // 100, 10), 500)
    dim_unidade = pd.DataFrame({
        "id_unidade":        new_ids(n_unidade),
        "nome":              [f"Lotérica {fake.last_name()}" for _ in range(n_unidade)],
        "uf":                [fake.state_abbr() for _ in range(n_unidade)],
        "cidade":            [fake.city() for _ in range(n_unidade)],
    })

    n_servico = min(max(n // 300, 6), 15)
    dim_servico = pd.DataFrame({
        "id_servico":        new_ids(n_servico),
        "nome":              random.choices(SERVICOS, k=n_servico),
        "categoria":         random.choices(CATEGORIAS_SERVICO, k=n_servico),
    })

    fato_transacao = pd.DataFrame({
        "id_transacao":      new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n),
        "id_servico":        random.choices(dim_servico["id_servico"].tolist(), k=n),
        "valor":             rng.uniform(5, 3000, n).round(2),
        "comissao":          rng.uniform(0.2, 60, n).round(2),
    })

    n_aposta = int(n * 1.2)
    valor_aposta = rng.uniform(2.5, 200, n_aposta).round(2)
    premiado = random.choices([True, False], weights=[8, 92], k=n_aposta)
    fato_aposta_loteria = pd.DataFrame({
        "id_aposta_loteria": new_ids(n_aposta),
        "id_data":           rand_dates(start, end, n_aposta),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n_aposta),
        "modalidade":        random.choices(MODALIDADES_LOTERIA, weights=[30, 25, 15, 10, 10, 10], k=n_aposta),
        "valor_aposta":      valor_aposta,
        "premiado":          premiado,
        "valor_premio":      [round(rng.uniform(20, 500000), 2) if p else 0.0 for p in premiado],
    })

    return {
        "DimUnidade": dim_unidade,
        "DimServico": dim_servico,
        "FatoTransacao": fato_transacao,
        "FatoApostaLoteria": fato_aposta_loteria,
        "dCalendario": dcalendario(start, end),
    }
