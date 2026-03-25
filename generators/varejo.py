"""generators/varejo.py — Setor Varejo."""

import random
from datetime import date

import numpy as np
import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

ESTADOS = ["SP", "RJ", "MG", "RS", "PR", "SC", "BA", "CE", "PE", "GO"]
REGIOES = {
    "SP": "Sudeste", "RJ": "Sudeste", "MG": "Sudeste",
    "RS": "Sul",     "PR": "Sul",     "SC": "Sul",
    "BA": "Nordeste","CE": "Nordeste","PE": "Nordeste",
    "GO": "Centro-Oeste",
}


def gerar_varejo(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_clientes   = min(n, 5000)
    n_produtos   = min(500, n // 5 + 50)
    n_vendedores = 50
    n_filiais    = 10

    dim_geo = pd.DataFrame({
        "id_geo": new_ids(len(ESTADOS)),
        "estado": ESTADOS,
        "regiao": [REGIOES[e] for e in ESTADOS],
    })

    dim_cliente = pd.DataFrame({
        "id_cliente": new_ids(n_clientes),
        "nome":       [fake.name()  for _ in range(n_clientes)],
        "cpf":        [fake.cpf()   for _ in range(n_clientes)],
        "email":      [fake.email() for _ in range(n_clientes)],
        "segmento":   random.choices(["Pessoa Física", "Pessoa Jurídica", "Premium"], k=n_clientes),
        "cidade":     [fake.city()  for _ in range(n_clientes)],
        "uf":         random.choices(ESTADOS, k=n_clientes),
    })

    categorias = ["Eletrônicos","Vestuário","Alimentos","Móveis","Esporte","Beleza","Brinquedos"]
    dim_produto = pd.DataFrame({
        "id_produto": new_ids(n_produtos),
        "nome":       [f"Produto {fake.word().capitalize()} {i}" for i in range(1, n_produtos + 1)],
        "sku":        [f"SKU-{rng.integers(10000, 99999)}" for _ in range(n_produtos)],
        "categoria":  random.choices(categorias, k=n_produtos),
        "preco_unit": rng.uniform(10, 2000, n_produtos).round(2),
        "custo_unit": rng.uniform(5,  1000, n_produtos).round(2),
    })

    dim_vendedor = pd.DataFrame({
        "id_vendedor": new_ids(n_vendedores),
        "nome":        [fake.name() for _ in range(n_vendedores)],
        "cpf":         [fake.cpf()  for _ in range(n_vendedores)],
        "regiao":      random.choices(list(REGIOES.values()), k=n_vendedores),
        "meta_mensal": rng.integers(10000, 80000, n_vendedores),
    })

    dim_filial = pd.DataFrame({
        "id_filial": new_ids(n_filiais),
        "nome":      [f"Filial {fake.city()}" for _ in range(n_filiais)],
        "uf":        random.choices(ESTADOS, k=n_filiais),
        "id_geo":    random.choices(dim_geo["id_geo"].tolist(), k=n_filiais),
        "tipo":      random.choices(["Loja Física", "E-commerce", "Outlet"], k=n_filiais),
    })

    datas    = rand_dates(start, end, n)
    qtds     = rng.integers(1, 20, n)
    produtos = random.choices(dim_produto["id_produto"].tolist(), k=n)
    precos   = [dim_produto.loc[dim_produto["id_produto"] == p, "preco_unit"].values[0] for p in produtos]
    descontos = rng.uniform(0, 0.3, n)

    fato = pd.DataFrame({
        "id_venda":    new_ids(n),
        "id_data":     datas,
        "id_cliente":  random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "id_produto":  produtos,
        "id_vendedor": random.choices(dim_vendedor["id_vendedor"].tolist(), k=n),
        "id_filial":   random.choices(dim_filial["id_filial"].tolist(), k=n),
        "quantidade":  qtds,
        "valor_unit":  [round(p, 2) for p in precos],
        "desconto":    descontos.round(3),
        "valor_total": [round(q * p * (1 - d), 2) for q, p, d in zip(qtds, precos, descontos)],
        "canal":       random.choices(["Loja", "Online", "Telefone"], k=n),
    })

    return {
        "DimCliente":   dim_cliente,
        "DimProduto":   dim_produto,
        "DimVendedor":  dim_vendedor,
        "DimFilial":    dim_filial,
        "DimGeografia": dim_geo,
        "FatoVendas":   fato,
        "dCalendario":  dcalendario(start, end),
    }
