"""generators/frigorifico.py — Setor Frigorífico & Processamento de Carnes."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

ESPECIES = ["Bovino", "Suíno", "Aves", "Ovino"]
TIPOS_CORTE = ["Dianteiro", "Traseiro", "Costela", "Filé", "Picanha", "Linguiça", "Peito", "Coxa e Sobrecoxa"]
CATEGORIAS_PRODUTO = ["In Natura", "Processado", "Embutido", "Congelado"]
CANAIS_VENDA = ["Atacado", "Varejo", "Exportação", "Food Service"]


def gerar_frigorifico(n, start, end):
    n = max(int(n), 1)

    n_unidade = min(max(n // 300, 3), 40)
    dim_unidade = pd.DataFrame({
        "id_unidade":        new_ids(n_unidade),
        "nome":              [f"Unidade {fake.city()}" for _ in range(n_unidade)],
        "uf":                [fake.state_abbr() for _ in range(n_unidade)],
        "capacidade_abate_dia": rng.integers(200, 8000, n_unidade),
    })

    n_produto = min(max(n // 25, 20), 500)
    dim_produto = pd.DataFrame({
        "id_produto":        new_ids(n_produto),
        "nome":              [f"{random.choice(TIPOS_CORTE)} {random.choice(['Resfriado','Congelado','Temperado'])}" for _ in range(n_produto)],
        "tipo_corte":        random.choices(TIPOS_CORTE, k=n_produto),
        "especie":           random.choices(ESPECIES, weights=[40, 30, 25, 5], k=n_produto),
        "categoria":         random.choices(CATEGORIAS_PRODUTO, k=n_produto),
    })

    especie_abate = random.choices(ESPECIES, weights=[40, 30, 25, 5], k=n)
    qtd_animais = rng.integers(10, 3000, n)
    fato_abate = pd.DataFrame({
        "id_abate":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n),
        "especie":           especie_abate,
        "quantidade_animais": qtd_animais,
        "peso_total_kg":     (qtd_animais * rng.uniform(15, 550, n)).round(1),
        "rendimento_pct":    rng.uniform(48, 78, n).round(1),
    })

    n_venda = int(n * 1.3)
    qtd_kg = rng.uniform(10, 8000, n_venda).round(1)
    preco_kg = rng.uniform(4, 55, n_venda).round(2)
    fato_venda = pd.DataFrame({
        "id_venda_prod":     new_ids(n_venda),
        "id_data":           rand_dates(start, end, n_venda),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n_venda),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n_venda),
        "quantidade_kg":     qtd_kg,
        "preco_kg":          preco_kg,
        "valor_total":       (qtd_kg * preco_kg).round(2),
        "canal":             random.choices(CANAIS_VENDA, weights=[35, 30, 20, 15], k=n_venda),
    })

    return {
        "DimUnidade": dim_unidade,
        "DimProduto": dim_produto,
        "FatoAbate": fato_abate,
        "FatoVenda": fato_venda,
        "dCalendario": dcalendario(start, end),
    }
