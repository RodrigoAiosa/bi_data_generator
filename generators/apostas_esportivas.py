"""generators/apostas_esportivas.py — Setor Apostas Esportivas & iGaming."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

NIVEIS_VIP = ["Bronze", "Prata", "Ouro", "Platina", "Diamante"]
ESPORTES = ["Futebol", "Basquete", "Tênis", "eSports", "Vôlei", "MMA", "Fórmula 1"]
CAMPEONATOS = ["Brasileirão", "Champions League", "NBA", "Libertadores", "ATP Tour", "UFC", "Copa do Mundo"]
TIPOS_APOSTA = ["Simples", "Múltipla", "Ao Vivo", "Sistema"]
RESULTADOS_APOSTA = ["Ganhou", "Perdeu", "Cancelada", "Reembolsada"]
TIPOS_TRANSACAO = ["Depósito", "Saque", "Bônus", "Cashback"]
METODOS_PAGAMENTO = ["Pix", "Cartão de Crédito", "Boleto", "Carteira Digital"]


def gerar_apostas_esportivas(n, start, end):
    n = max(int(n), 1)

    n_jogador = min(max(n // 6, 200), 20000)
    dim_jogador = pd.DataFrame({
        "id_jogador":        new_ids(n_jogador),
        "nome":              [fake.name() for _ in range(n_jogador)],
        "idade":             rng.integers(18, 75, n_jogador),
        "uf":                [fake.state_abbr() for _ in range(n_jogador)],
        "nivel_vip":         random.choices(NIVEIS_VIP, weights=[45, 25, 15, 10, 5], k=n_jogador),
    })

    n_evento = min(max(n // 15, 50), 4000)
    dim_evento = pd.DataFrame({
        "id_evento_esportivo": new_ids(n_evento),
        "esporte":           random.choices(ESPORTES, weights=[45, 15, 10, 12, 8, 5, 5], k=n_evento),
        "campeonato":        random.choices(CAMPEONATOS, k=n_evento),
        "data_evento":       rand_dates(start, end, n_evento),
    })

    valor_apostado = rng.uniform(5, 5000, n).round(2)
    odd = rng.uniform(1.1, 12.0, n).round(2)
    resultado = random.choices(RESULTADOS_APOSTA, weights=[42, 48, 6, 4], k=n)
    fato_aposta = pd.DataFrame({
        "id_aposta":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_jogador":        random.choices(dim_jogador["id_jogador"].tolist(), k=n),
        "id_evento_esportivo": random.choices(dim_evento["id_evento_esportivo"].tolist(), k=n),
        "tipo_aposta":       random.choices(TIPOS_APOSTA, weights=[45, 30, 20, 5], k=n),
        "valor_apostado":    valor_apostado,
        "odd":               odd,
        "resultado":         resultado,
        "valor_retorno":     [round(v * o, 2) if r == "Ganhou" else 0.0 for v, o, r in zip(valor_apostado, odd, resultado)],
    })

    n_transacao = int(n * 0.6)
    fato_transacao = pd.DataFrame({
        "id_transacao":      new_ids(n_transacao),
        "id_data":           rand_dates(start, end, n_transacao),
        "id_jogador":        random.choices(dim_jogador["id_jogador"].tolist(), k=n_transacao),
        "tipo":              random.choices(TIPOS_TRANSACAO, weights=[45, 35, 15, 5], k=n_transacao),
        "valor":             rng.uniform(10, 8000, n_transacao).round(2),
        "metodo_pagamento":  random.choices(METODOS_PAGAMENTO, weights=[55, 25, 10, 10], k=n_transacao),
    })

    return {
        "DimJogador": dim_jogador,
        "DimEvento": dim_evento,
        "FatoAposta": fato_aposta,
        "FatoTransacao": fato_transacao,
        "dCalendario": dcalendario(start, end),
    }
