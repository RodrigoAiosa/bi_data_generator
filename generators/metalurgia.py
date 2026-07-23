"""generators/metalurgia.py — Setor Metalurgia & Siderurgia."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_METAL = ["Aço Carbono", "Aço Inox", "Alumínio", "Ferro Fundido", "Cobre", "Zinco"]
PRODUTOS = ["Bobina", "Chapa", "Barra", "Tubo", "Perfil", "Fio-Máquina", "Lingote"]
TIPOS_FORNO = ["Alto-Forno", "Forno Elétrico a Arco", "Forno de Indução"]
TIPOS_DEFEITO = ["Trinca", "Porosidade", "Dimensão Fora de Especificação", "Contaminação", "Nenhum"]


def gerar_metalurgia(n, start, end):
    n = max(int(n), 1)

    n_unidade = min(max(n // 300, 3), 30)
    dim_unidade = pd.DataFrame({
        "id_unidade":        new_ids(n_unidade),
        "nome":              [f"Usina {fake.city()}" for _ in range(n_unidade)],
        "uf":                [fake.state_abbr() for _ in range(n_unidade)],
        "tipo_forno":        random.choices(TIPOS_FORNO, k=n_unidade),
    })

    n_produto = min(max(n // 25, 20), 500)
    dim_produto = pd.DataFrame({
        "id_produto":        new_ids(n_produto),
        "nome":              [f"{random.choice(PRODUTOS)} {random.choice(TIPOS_METAL)}" for _ in range(n_produto)],
        "tipo_metal":        random.choices(TIPOS_METAL, k=n_produto),
        "categoria":         random.choices(PRODUTOS, k=n_produto),
    })

    fato_producao = pd.DataFrame({
        "id_producao":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n),
        "toneladas_produzidas": rng.uniform(5, 4000, n).round(1),
        "consumo_energia_mwh": rng.uniform(2, 800, n).round(1),
        "defeito":           random.choices(TIPOS_DEFEITO, weights=[6, 5, 6, 3, 80], k=n),
    })

    n_venda = int(n * 0.9)
    qtd = rng.uniform(1, 500, n_venda).round(1)
    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n_venda),
        "id_data":           rand_dates(start, end, n_venda),
        "id_unidade":        random.choices(dim_unidade["id_unidade"].tolist(), k=n_venda),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n_venda),
        "toneladas_vendidas": qtd,
        "preco_tonelada":    rng.uniform(2500, 12000, n_venda).round(2),
        "canal":             random.choices(["Indústria Automotiva", "Construção Civil", "Exportação", "Distribuidor"], k=n_venda),
    })

    return {
        "DimUnidade": dim_unidade,
        "DimProduto": dim_produto,
        "FatoProducao": fato_producao,
        "FatoVenda": fato_venda,
        "dCalendario": dcalendario(start, end),
    }
