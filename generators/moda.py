"""generators/moda.py — Setor Moda & Vestuário."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS    = ["Feminino","Masculino","Infantil","Íntimo","Esportivo","Praia","Jeanswear","Cama/Mesa/Banho"]
COLECOES      = ["Verão","Inverno","Primavera-Verão","Outono-Inverno","Cápsula","Colaboração"]
CANAIS        = ["Loja Própria","Multimarca","E-commerce","Marketplace","Atacado","Pop-up"]
TAMANHOS      = ["PP","P","M","G","GG","XGG","36","38","40","42","44","46"]
MATERIAIS     = ["Algodão","Poliéster","Viscose","Linho","Denim","Seda","Modal","Neoprene","Couro"]
ESTILOS       = ["Casual","Social","Esportivo","Festa","Praia","Streetwear","Boho","Clássico"]

def gerar_moda(n, start, end):
    n = max(int(n), 1)
    n_prod = min(max(n//6,100),800)
    dim_produto = pd.DataFrame({
        "id_produto":   new_ids(n_prod),
        "nome":         [f"{random.choice(ESTILOS)} {fake.word().capitalize()}" for _ in range(n_prod)],
        "categoria":    random.choices(CATEGORIAS, k=n_prod),
        "colecao":      random.choices(COLECOES, k=n_prod),
        "material":     random.choices(MATERIAIS, k=n_prod),
        "custo":        rng.uniform(15, 300, n_prod).round(2),
        "preco_venda":  rng.uniform(50, 900, n_prod).round(2),
        "margem_pct":   rng.uniform(30, 75, n_prod).round(1),
        "ativo":        random.choices([True,False], weights=[85,15], k=n_prod),
    })
    n_loja = min(max(n//20,20),100)
    dim_loja = pd.DataFrame({
        "id_loja":      new_ids(n_loja),
        "nome":         [f"Loja {fake.city()}" for _ in range(n_loja)],
        "canal":        random.choices(CANAIS, k=n_loja),
        "uf":           [fake.state_abbr() for _ in range(n_loja)],
        "cidade":       [fake.city() for _ in range(n_loja)],
        "area_m2":      rng.uniform(30, 500, n_loja).round(0),
        "meta_mensal":  rng.uniform(20_000, 500_000, n_loja).round(2),
        "ativa":        random.choices([True,False], weights=[90,10], k=n_loja),
    })
    qtd = rng.integers(1, 20, n)
    preco = rng.uniform(50, 900, n).round(2)
    fato_venda = pd.DataFrame({
        "id_venda":     new_ids(n),
        "id_data":      rand_dates(start, end, n),
        "id_produto":   random.choices(dim_produto["id_produto"].tolist(), k=n),
        "id_loja":      random.choices(dim_loja["id_loja"].tolist(), k=n),
        "tamanho":      random.choices(TAMANHOS, k=n),
        "canal":        random.choices(CANAIS, k=n),
        "quantidade":   qtd,
        "preco_unitario": preco,
        "desconto_pct": rng.uniform(0, 50, n).round(1),
        "valor_total":  (qtd * preco).round(2),
        "devolucao":    random.choices([True,False], weights=[12,88], k=n),
        "forma_pagto":  random.choices(["Cartão Crédito","Cartão Débito","PIX","Dinheiro","Boleto"], k=n),
    })
    n_est = int(n * 0.3)
    fato_estoque = pd.DataFrame({
        "id_estoque":   new_ids(n_est),
        "id_data":      rand_dates(start, end, n_est),
        "id_produto":   random.choices(dim_produto["id_produto"].tolist(), k=n_est),
        "id_loja":      random.choices(dim_loja["id_loja"].tolist(), k=n_est),
        "tamanho":      random.choices(TAMANHOS, k=n_est),
        "qtd_disponivel": rng.integers(0, 200, n_est),
        "qtd_minima":   rng.integers(5, 30, n_est),
        "ruptura":      random.choices([True,False], weights=[10,90], k=n_est),
        "giro_dias":    rng.integers(5, 120, n_est),
    })
    return {"DimProduto": dim_produto, "DimLoja": dim_loja,
            "FatoVenda": fato_venda, "FatoEstoque": fato_estoque,
            "dCalendario": dcalendario(start, end)}
