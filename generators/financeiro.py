"""generators/financeiro.py — Setor Financeiro."""

import random
from datetime import date

import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")


def gerar_financeiro(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_contas   = min(n, 3000)
    n_agencias = 30
    n_produtos = 20

    dim_agencia = pd.DataFrame({
        "id_agencia": new_ids(n_agencias),
        "nome":       [f"Agência {fake.city()}" for _ in range(n_agencias)],
        "codigo":     [f"{rng.integers(1000,9999)}-{rng.integers(0,9)}" for _ in range(n_agencias)],
        "uf":         random.choices(["SP","RJ","MG","RS","PR"], k=n_agencias),
        "tipo":       random.choices(["Física","Digital","Express"], k=n_agencias),
    })

    dim_conta = pd.DataFrame({
        "id_conta":   new_ids(n_contas),
        "titular":    [fake.name() for _ in range(n_contas)],
        "cpf_cnpj":   [fake.cpf()  for _ in range(n_contas)],
        "tipo_conta": random.choices(["Corrente","Poupança","Empresarial","Investimento"], k=n_contas),
        "id_agencia": random.choices(dim_agencia["id_agencia"].tolist(), k=n_contas),
        "segmento":   random.choices(["Varejo","Personnalité","Corporate","Private"], k=n_contas),
    })

    dim_produto = pd.DataFrame({
        "id_produto": new_ids(n_produtos),
        "nome": [
            "CDB","LCI","LCA","Tesouro Direto","Fundo DI","Fundo Multimercado",
            "Cartão Crédito","Cartão Débito","Seguro Vida","Previdência",
            "Financiamento","Empréstimo Pessoal","Consórcio","Câmbio",
            "Conta Corrente","Conta Poupança","PIX","TED","DOC","Cheque",
        ],
        "categoria": (
            ["Investimento"] * 6 + ["Cartão"] * 2 +
            ["Seguro", "Previdência"] + ["Crédito"] * 3 +
            ["Câmbio"] + ["Conta"] * 2 + ["Pagamento"] * 4
        ),
        "taxa_juros": rng.uniform(0.005, 0.15, n_produtos).round(4),
    })

    tipos_transacao = ["Débito","Crédito","TED","DOC","PIX","Saque","Depósito","Investimento"]
    fato = pd.DataFrame({
        "id_transacao": new_ids(n),
        "id_data":      rand_dates(start, end, n),
        "id_conta":     random.choices(dim_conta["id_conta"].tolist(), k=n),
        "id_agencia":   random.choices(dim_agencia["id_agencia"].tolist(), k=n),
        "id_produto":   random.choices(dim_produto["id_produto"].tolist(), k=n),
        "tipo":         random.choices(tipos_transacao, k=n),
        "valor":        rng.uniform(10, 50000, n).round(2),
        "saldo_apos":   rng.uniform(0, 200000, n).round(2),
        "status":       random.choices(["Aprovada","Negada","Pendente"], weights=[85,10,5], k=n),
    })

    return {
        "DimAgencia":    dim_agencia,
        "DimConta":      dim_conta,
        "DimProduto":    dim_produto,
        "FatoTransacao": fato,
        "dCalendario":   dcalendario(start, end),
    }
