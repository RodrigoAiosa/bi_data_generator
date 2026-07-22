"""generators/grafica.py — Setor Gráfica & Comunicação Visual."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

PRODUTOS = ["Cartão de Visita", "Banner", "Adesivo", "Catálogo", "Fachada", "Folder", "Faixa", "Envelope"]
MATERIAIS = ["Papel Couché", "Lona", "Vinil Adesivo", "PVC", "Papel Reciclado", "ACM"]
CATEGORIAS_PRODUTO = ["Impresso", "Sinalização", "Grande Formato"]
SEGMENTOS_CLIENTE = ["Varejo", "Eventos", "Corporativo", "Autônomo", "Órgão Público"]


def gerar_grafica(n, start, end):
    n = max(int(n), 1)

    n_produto = min(max(n // 40, 15), 300)
    dim_produto = pd.DataFrame({
        "id_produto":        new_ids(n_produto),
        "nome":              random.choices(PRODUTOS, k=n_produto),
        "material":          random.choices(MATERIAIS, k=n_produto),
        "categoria":         random.choices(CATEGORIAS_PRODUTO, weights=[45, 25, 30], k=n_produto),
    })

    n_cliente = min(max(n // 6, 100), 8000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.company() if random.random() < 0.6 else fake.name() for _ in range(n_cliente)],
        "segmento":          random.choices(SEGMENTOS_CLIENTE, k=n_cliente),
    })

    qtd = rng.integers(10, 5000, n)
    fato_pedido = pd.DataFrame({
        "id_pedido":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "quantidade":        qtd,
        "valor_total":       (qtd * rng.uniform(0.3, 8, n)).round(2),
        "prazo_entrega_dias": rng.integers(1, 15, n),
        "urgente":           random.choices([True, False], weights=[20, 80], k=n),
    })

    n_prod = int(n * 0.9)
    fato_producao = pd.DataFrame({
        "id_producao_grafica": new_ids(n_prod),
        "id_data":           rand_dates(start, end, n_prod),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n_prod),
        "metros_impressos":  rng.uniform(1, 800, n_prod).round(1),
        "tempo_producao_horas": rng.uniform(0.2, 20, n_prod).round(1),
        "retrabalho":        random.choices([True, False], weights=[8, 92], k=n_prod),
    })

    return {
        "DimProduto": dim_produto,
        "DimCliente": dim_cliente,
        "FatoPedido": fato_pedido,
        "FatoProducao": fato_producao,
        "dCalendario": dcalendario(start, end),
    }
