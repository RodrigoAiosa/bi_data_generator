"""generators/blockchain.py — Setor Blockchain & Criptomoedas."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

MOEDAS = ["Bitcoin", "Ethereum", "Solana", "Cardano", "Polygon", "USDT", "USDC", "BNB", "Avalanche"]
CATEGORIAS_MOEDA = ["Layer 1", "Stablecoin", "Token de Utilidade", "Meme Coin"]
NIVEIS_KYC = ["Não Verificado", "Básico", "Intermediário", "Avançado"]
TIPOS_TRANSACAO = ["Compra", "Venda", "Swap", "Staking", "Transferência"]
TIPOS_CARTEIRA = ["Hot Wallet", "Cold Wallet", "Custodial (Exchange)"]


def gerar_blockchain(n, start, end):
    n = max(int(n), 1)

    n_moeda = min(max(n // 300, 5), 30)
    dim_moeda = pd.DataFrame({
        "id_moeda":          new_ids(n_moeda),
        "nome":              random.choices(MOEDAS, k=n_moeda),
        "categoria":         random.choices(CATEGORIAS_MOEDA, weights=[40, 25, 25, 10], k=n_moeda),
        "ano_lancamento":    rng.integers(2009, 2024, n_moeda),
    })

    n_usuario = min(max(n // 6, 200), 15000)
    dim_usuario = pd.DataFrame({
        "id_usuario":        new_ids(n_usuario),
        "nome":              [fake.name() for _ in range(n_usuario)],
        "nivel_kyc":         random.choices(NIVEIS_KYC, weights=[10, 30, 40, 20], k=n_usuario),
        "uf":                [fake.state_abbr() for _ in range(n_usuario)],
    })

    fato_transacao = pd.DataFrame({
        "id_transacao":      new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_moeda":          random.choices(dim_moeda["id_moeda"].tolist(), k=n),
        "id_usuario":        random.choices(dim_usuario["id_usuario"].tolist(), k=n),
        "tipo":              random.choices(TIPOS_TRANSACAO, weights=[30, 25, 20, 15, 10], k=n),
        "quantidade":        rng.uniform(0.0001, 50, n).round(6),
        "valor_usd":         rng.uniform(5, 80000, n).round(2),
        "taxa":              rng.uniform(0.5, 45, n).round(2),
    })

    n_carteira = int(n * 0.5)
    fato_carteira = pd.DataFrame({
        "id_carteira_fato":  new_ids(n_carteira),
        "id_data":           rand_dates(start, end, n_carteira),
        "id_usuario":        random.choices(dim_usuario["id_usuario"].tolist(), k=n_carteira),
        "id_moeda":          random.choices(dim_moeda["id_moeda"].tolist(), k=n_carteira),
        "saldo":             rng.uniform(0, 15000, n_carteira).round(6),
        "tipo_carteira":     random.choices(TIPOS_CARTEIRA, weights=[45, 15, 40], k=n_carteira),
    })

    return {
        "DimMoeda": dim_moeda,
        "DimUsuario": dim_usuario,
        "FatoTransacao": fato_transacao,
        "FatoCarteira": fato_carteira,
        "dCalendario": dcalendario(start, end),
    }
