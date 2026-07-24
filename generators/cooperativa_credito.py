"""generators/cooperativa_credito.py — Setor Cooperativa de Crédito."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_PESSOA = ["Pessoa Física", "Pessoa Jurídica"]
PRODUTOS = ["Conta Corrente", "Empréstimo Pessoal", "CDB", "Consórcio Interno", "Financiamento Rural", "Seguro de Vida"]
CATEGORIAS_PRODUTO = ["Conta", "Crédito", "Investimento", "Seguro"]
TIPOS_OPERACAO = ["Depósito", "Saque", "Contratação de Empréstimo", "Aplicação", "Resgate"]


def gerar_cooperativa_credito(n, start, end):
    n = max(int(n), 1)

    n_cooperado = min(max(n // 5, 200), 20000)
    dim_cooperado = pd.DataFrame({
        "id_cooperado":      new_ids(n_cooperado),
        "nome":              [fake.name() if random.random() < 0.85 else fake.company() for _ in range(n_cooperado)],
        "tipo_pessoa":       random.choices(TIPOS_PESSOA, weights=[85, 15], k=n_cooperado),
        "uf":                [fake.state_abbr() for _ in range(n_cooperado)],
        "tempo_associacao_anos": rng.integers(0, 30, n_cooperado),
    })

    n_produto = min(max(n // 500, 6), 40)
    dim_produto = pd.DataFrame({
        "id_produto":        new_ids(n_produto),
        "nome":              random.choices(PRODUTOS, k=n_produto),
        "categoria":         random.choices(CATEGORIAS_PRODUTO, k=n_produto),
    })

    fato_operacao = pd.DataFrame({
        "id_operacao":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_cooperado":      random.choices(dim_cooperado["id_cooperado"].tolist(), k=n),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n),
        "tipo":              random.choices(TIPOS_OPERACAO, weights=[30, 20, 20, 20, 10], k=n),
        "valor":             rng.uniform(50, 250000, n).round(2),
    })

    n_sobra = int(n_cooperado * 0.7)
    fato_sobra = pd.DataFrame({
        "id_sobra":          new_ids(n_sobra),
        "id_data":           rand_dates(start, end, n_sobra),
        "id_cooperado":      random.choices(dim_cooperado["id_cooperado"].tolist(), k=n_sobra),
        "valor_distribuido": rng.uniform(20, 8000, n_sobra).round(2),
        "percentual_participacao": rng.uniform(0.01, 5, n_sobra).round(3),
    })

    return {
        "DimCooperado": dim_cooperado,
        "DimProduto": dim_produto,
        "FatoOperacao": fato_operacao,
        "FatoSobra": fato_sobra,
        "dCalendario": dcalendario(start, end),
    }
