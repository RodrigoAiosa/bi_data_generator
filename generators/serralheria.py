"""generators/serralheria.py — Setor Serralheria."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS_PRODUTO = ["Portão", "Grade de Proteção", "Corrimão", "Esquadria de Alumínio", "Estrutura Metálica", "Escada"]
STATUS_PEDIDO      = ["Orçamento", "Aprovado", "Em Produção", "Entregue", "Cancelado"]
MATERIAIS          = ["Ferro", "Alumínio", "Aço Inox", "Aço Carbono"]


def gerar_serralheria(n, start, end):
    n = max(int(n), 1)

    n_cliente = min(max(n // 8, 100), 8000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.name() if random.random() < 0.7 else fake.company() for _ in range(n_cliente)],
        "uf":                [fake.state_abbr() for _ in range(n_cliente)],
    })

    n_produto = min(max(n // 25, 20), 400)
    dim_produto = pd.DataFrame({
        "id_produto":        new_ids(n_produto),
        "categoria":         random.choices(CATEGORIAS_PRODUTO, k=n_produto),
        "material":          random.choices(MATERIAIS, weights=[35, 30, 15, 20], k=n_produto),
        "preco_base":        rng.uniform(250, 12000, n_produto).round(2),
    })

    produto_idx = random.choices(range(n_produto), k=n)
    preco_base = dim_produto["preco_base"].to_numpy()[produto_idx]
    status_pedido = random.choices(STATUS_PEDIDO, weights=[20, 25, 25, 25, 5], k=n)
    fato_pedido = pd.DataFrame({
        "id_pedido":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "id_produto":        dim_produto["id_produto"].to_numpy()[produto_idx],
        "valor":             (preco_base * rng.uniform(0.9, 1.6, n)).round(2),
        "prazo_dias":        rng.integers(3, 45, n),
        "status":            status_pedido,
    })

    n_producao = int(n * 0.9)
    fato_producao = pd.DataFrame({
        "id_producao":       new_ids(n_producao),
        "id_data":           rand_dates(start, end, n_producao),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n_producao),
        "tempo_producao_h":  rng.uniform(1, 80, n_producao).round(1),
        "custo_material":    rng.uniform(80, 6000, n_producao).round(2),
    })

    return {
        "DimCliente": dim_cliente,
        "DimProduto": dim_produto,
        "FatoPedido": fato_pedido,
        "FatoProducao": fato_producao,
        "dCalendario": dcalendario(start, end),
    }
