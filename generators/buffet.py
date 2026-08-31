"""generators/buffet.py — Setor Buffet & Cerimonial."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_EVENTO   = ["Casamento", "Formatura", "Aniversário", "Corporativo", "Debutante", "Batizado"]
TIPOS_CARDAPIO = ["Coquetel", "Jantar Completo", "Almoço Executivo", "Finger Food", "Churrasco"]
STATUS_EVENTO  = ["Confirmado", "Realizado", "Cancelado", "Orçamento"]
CATEGORIAS_FORNECEDOR = ["Decoração", "Som & Iluminação", "Fotografia", "Cerimonial", "Doces & Bolo"]


def gerar_buffet(n, start, end):
    n = max(int(n), 1)

    n_buffet = min(max(n // 100, 3), 40)
    dim_buffet = pd.DataFrame({
        "id_buffet":         new_ids(n_buffet),
        "nome_salao":        [f"Espaço {fake.last_name()}" for _ in range(n_buffet)],
        "capacidade_pessoas": rng.integers(50, 1000, n_buffet),
    })

    n_cardapio = min(max(n // 50, 5), 200)
    dim_cardapio = pd.DataFrame({
        "id_cardapio":       new_ids(n_cardapio),
        "tipo":              random.choices(TIPOS_CARDAPIO, k=n_cardapio),
        "preco_por_pessoa":  rng.uniform(45, 480, n_cardapio).round(2),
    })

    status = random.choices(STATUS_EVENTO, weights=[35, 45, 10, 10], k=n)
    fato_evento = pd.DataFrame({
        "id_evento":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_buffet":         random.choices(dim_buffet["id_buffet"].tolist(), k=n),
        "id_cardapio":       random.choices(dim_cardapio["id_cardapio"].tolist(), k=n),
        "tipo_evento":       random.choices(TIPOS_EVENTO, k=n),
        "num_convidados":    rng.integers(20, 800, n),
        "valor_total":       rng.uniform(3000, 250000, n).round(2),
        "status":            status,
    })

    n_fornecedor = int(n * 1.8)
    fato_fornecedor = pd.DataFrame({
        "id_item_fornecedor": new_ids(n_fornecedor),
        "id_data":           rand_dates(start, end, n_fornecedor),
        "id_buffet":         random.choices(dim_buffet["id_buffet"].tolist(), k=n_fornecedor),
        "categoria":         random.choices(CATEGORIAS_FORNECEDOR, k=n_fornecedor),
        "custo":             rng.uniform(300, 25000, n_fornecedor).round(2),
    })

    return {
        "DimBuffet": dim_buffet,
        "DimCardapio": dim_cardapio,
        "FatoEvento": fato_evento,
        "FatoFornecedor": fato_fornecedor,
        "dCalendario": dcalendario(start, end),
    }
