"""generators/industria_moveleira.py — Setor Indústria Moveleira."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS_PRODUTO = ["Sofá", "Cama", "Armário", "Mesa", "Cadeira", "Estante", "Guarda-Roupa"]
MATERIAIS          = ["MDF", "Madeira Maciça", "Metal", "Estofado", "Vidro Temperado"]
SETORES_PRODUCAO   = ["Corte", "Montagem", "Pintura", "Estofaria", "Embalagem"]
CANAIS_VENDA        = ["Varejo", "Atacado", "E-commerce", "Loja Própria"]


def gerar_industria_moveleira(n, start, end):
    n = max(int(n), 1)

    n_produto = min(max(n // 40, 20), 500)
    dim_produto = pd.DataFrame({
        "id_produto":        new_ids(n_produto),
        "nome_produto":      [f"{c} {fake.word().capitalize()}" for c in random.choices(CATEGORIAS_PRODUTO, k=n_produto)],
        "categoria":         random.choices(CATEGORIAS_PRODUTO, k=n_produto),
        "material":          random.choices(MATERIAIS, k=n_produto),
        "preco_base":        rng.uniform(199.9, 6999.9, n_produto).round(2),
    })

    n_maquina = min(max(n // 300, 6), 120)
    dim_maquina = pd.DataFrame({
        "id_maquina":        new_ids(n_maquina),
        "nome_maquina":      [f"Máquina {fake.word().capitalize()}-{i}" for i in range(1, n_maquina + 1)],
        "setor_producao":    random.choices(SETORES_PRODUCAO, k=n_maquina),
        "ano_instalacao":    rng.integers(2005, 2025, n_maquina),
    })

    fato_producao = pd.DataFrame({
        "id_producao":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n),
        "id_maquina":        random.choices(dim_maquina["id_maquina"].tolist(), k=n),
        "quantidade_produzida": rng.integers(1, 200, n),
        "tempo_producao_h":  rng.uniform(0.5, 24, n).round(1),
        "custo_unitario":    rng.uniform(80, 3500, n).round(2),
        "taxa_refugo_pct":   rng.uniform(0, 8, n).round(2),
    })

    n_venda = int(n * 0.8)
    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n_venda),
        "id_data":           rand_dates(start, end, n_venda),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n_venda),
        "canal":             random.choices(CANAIS_VENDA, weights=[35, 30, 25, 10], k=n_venda),
        "quantidade":        rng.integers(1, 50, n_venda),
        "valor_total":       rng.uniform(199.9, 45000, n_venda).round(2),
    })

    return {
        "DimProduto": dim_produto,
        "DimMaquina": dim_maquina,
        "FatoProducao": fato_producao,
        "FatoVenda": fato_venda,
        "dCalendario": dcalendario(start, end),
    }
