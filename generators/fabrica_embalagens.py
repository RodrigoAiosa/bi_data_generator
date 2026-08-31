"""generators/fabrica_embalagens.py — Setor Fábrica de Embalagens."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_EMBALAGEM = ["Caixa de Papelão", "Embalagem Plástica Flexível", "Frasco de Vidro", "Lata Metálica",
                    "Embalagem Cartonada", "Filme Stretch", "Pote Plástico Rígido"]
MATERIAIS = ["Papelão Ondulado", "PET", "Polietileno", "Vidro", "Alumínio", "Papel Cartão"]
SETORES_CLIENTE = ["Alimentício", "Cosmético", "Farmacêutico", "Bebidas", "E-commerce", "Higiene e Limpeza"]


def gerar_fabrica_embalagens(n, start, end):
    n = max(int(n), 1)

    n_produto = min(max(n // 40, 20), 800)
    custo = rng.uniform(0.15, 12, n_produto).round(3)
    dim_produto = pd.DataFrame({
        "id_produto":        new_ids(n_produto),
        "nome":              [f"{random.choice(TIPOS_EMBALAGEM)} {rng.integers(50,2000)}ml" for _ in range(n_produto)],
        "tipo_embalagem":    random.choices(TIPOS_EMBALAGEM, k=n_produto),
        "material":          random.choices(MATERIAIS, k=n_produto),
        "custo_unitario":    custo,
        "preco_unitario":    (custo * rng.uniform(1.4, 2.8, n_produto)).round(3),
        "reciclavel":        random.choices([True, False], weights=[70, 30], k=n_produto),
    })

    n_cliente = min(max(n // 15, 40), 4000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.company() for _ in range(n_cliente)],
        "setor_cliente":     random.choices(SETORES_CLIENTE, k=n_cliente),
        "uf":                [fake.state_abbr() for _ in range(n_cliente)],
    })

    prod_idx = random.choices(range(n_produto), k=n)
    fato_producao = pd.DataFrame({
        "id_producao":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_produto":        dim_produto["id_produto"].to_numpy()[prod_idx],
        "material":          dim_produto["material"].to_numpy()[prod_idx],
        "quantidade_produzida": rng.integers(500, 200000, n),
        "custo_lote":        rng.uniform(300, 180000, n).round(2),
        "taxa_refugo_pct":   rng.uniform(0.1, 8, n).round(2),
    })

    n_pedido = int(n_cliente * 8)
    prod_idx2 = random.choices(range(n_produto), k=n_pedido)
    preco_unit = dim_produto["preco_unitario"].to_numpy()[prod_idx2]
    qtd = rng.integers(1000, 500000, n_pedido)
    fato_pedido = pd.DataFrame({
        "id_pedido":         new_ids(n_pedido),
        "id_data":           rand_dates(start, end, n_pedido),
        "id_produto":        dim_produto["id_produto"].to_numpy()[prod_idx2],
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n_pedido),
        "quantidade":        qtd,
        "valor_total":       (qtd * preco_unit).round(2),
        "prazo_entrega_dias": rng.integers(3, 60, n_pedido),
        "entregue_no_prazo": random.choices([True, False], weights=[85, 15], k=n_pedido),
    })

    return {
        "DimProduto": dim_produto,
        "DimCliente": dim_cliente,
        "FatoProducao": fato_producao,
        "FatoPedido": fato_pedido,
        "dCalendario": dcalendario(start, end),
    }
