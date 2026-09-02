"""generators/agencia_cambio.py — Setor Agência de Câmbio."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

MOEDAS = ["USD", "EUR", "GBP", "ARS", "CLP", "JPY", "CAD", "CHF"]
COTACAO_BASE = {"USD": 5.10, "EUR": 5.55, "GBP": 6.40, "ARS": 0.006, "CLP": 0.0055, "JPY": 0.034, "CAD": 3.75, "CHF": 5.70}
TIPOS_OPERACAO = ["Compra", "Venda"]
FINALIDADES = ["Viagem", "Remessa Internacional", "Comércio Exterior", "Investimento", "Estudo no Exterior"]


def gerar_agencia_cambio(n, start, end):
    n = max(int(n), 1)

    n_agencia = min(max(n // 200, 5), 120)
    dim_agencia = pd.DataFrame({
        "id_agencia":        new_ids(n_agencia),
        "nome":              [f"Casa de Câmbio {fake.last_name()}" for _ in range(n_agencia)],
        "cidade":            fake_pool(fake, "city", n_agencia),
        "uf":                fake_pool(fake, "state_abbr", n_agencia),
        "tipo":              random.choices(["Loja Física", "Aeroporto", "Digital"], weights=[55, 20, 25], k=n_agencia),
    })

    dim_moeda = pd.DataFrame({
        "id_moeda":          new_ids(len(MOEDAS)),
        "codigo":            MOEDAS,
        "cotacao_referencia": [COTACAO_BASE[m] for m in MOEDAS],
    })

    tipo_op = random.choices(TIPOS_OPERACAO, weights=[55, 45], k=n)
    moeda_idx = random.choices(range(len(MOEDAS)), k=n)
    codigo_moeda = [MOEDAS[i] for i in moeda_idx]
    cotacao = [round(COTACAO_BASE[c] * rng.uniform(0.96, 1.04), 4) for c in codigo_moeda]
    valor_moeda_estrangeira = rng.uniform(50, 20000, n).round(2)
    fato_operacao = pd.DataFrame({
        "id_operacao":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_agencia":        random.choices(dim_agencia["id_agencia"].tolist(), k=n),
        "id_moeda":          dim_moeda["id_moeda"].to_numpy()[moeda_idx],
        "tipo_operacao":     tipo_op,
        "finalidade":        random.choices(FINALIDADES, weights=[45, 20, 15, 10, 10], k=n),
        "valor_moeda_estrangeira": valor_moeda_estrangeira,
        "cotacao_aplicada":  cotacao,
        "valor_reais":       (valor_moeda_estrangeira * cotacao).round(2),
        "taxa_servico":      rng.uniform(1, 5, n).round(2),
    })

    n_fechamento = min(max(n // 30, 60), 20000)
    fato_fechamento = pd.DataFrame({
        "id_fechamento":     new_ids(n_fechamento),
        "id_data":           rand_dates(start, end, n_fechamento),
        "id_agencia":        random.choices(dim_agencia["id_agencia"].tolist(), k=n_fechamento),
        "saldo_inicial_reais": rng.uniform(5000, 500000, n_fechamento).round(2),
        "total_operacoes_dia": rng.integers(1, 120, n_fechamento),
        "divergencia_caixa": rng.uniform(-200, 200, n_fechamento).round(2),
    })

    return {
        "DimAgencia": dim_agencia,
        "DimMoeda": dim_moeda,
        "FatoOperacao": fato_operacao,
        "FatoFechamentoCaixa": fato_fechamento,
        "dCalendario": dcalendario(start, end),
    }
