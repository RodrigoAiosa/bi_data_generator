"""generators/cosmeticos.py — Setor Cosméticos & Fábrica de Cosméticos."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS = ["Skincare", "Maquiagem", "Perfumaria", "Capilar", "Higiene Pessoal"]
PUBLICOS = ["Feminino", "Masculino", "Unissex"]
CANAIS = ["Distribuidor", "E-commerce", "Farmácia", "Loja Própria"]


def gerar_cosmeticos(n, start, end):
    n = max(int(n), 1)

    n_fabrica = min(max(n // 300, 3), 40)
    dim_fabrica = pd.DataFrame({
        "id_fabrica":        new_ids(n_fabrica),
        "cidade":            [fake.city() for _ in range(n_fabrica)],
        "uf":                [fake.state_abbr() for _ in range(n_fabrica)],
    })

    n_linha = min(max(n // 20, 20), 3000)
    dim_linha = pd.DataFrame({
        "id_linha":          new_ids(n_linha),
        "id_fabrica":        random.choices(dim_fabrica["id_fabrica"].tolist(), k=n_linha),
        "categoria":         random.choices(CATEGORIAS, k=n_linha),
        "publico":           random.choices(PUBLICOS, weights=[55, 20, 25], k=n_linha),
    })

    fato_producao = pd.DataFrame({
        "id_lote_producao":  new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_linha":          random.choices(dim_linha["id_linha"].tolist(), k=n),
        "unidades_produzidas": rng.integers(200, 40000, n),
        "custo_unitario":    rng.uniform(2, 45, n).round(2),
    })

    n_venda = int(n * 1.4)
    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n_venda),
        "id_data":           rand_dates(start, end, n_venda),
        "id_linha":          random.choices(dim_linha["id_linha"].tolist(), k=n_venda),
        "canal":             random.choices(CANAIS, k=n_venda),
        "unidades_vendidas": rng.integers(1, 2000, n_venda),
        "preco_unitario":    rng.uniform(8, 250, n_venda).round(2),
    })

    return {
        "DimFabrica": dim_fabrica,
        "DimLinhaProduto": dim_linha,
        "FatoProducao": fato_producao,
        "FatoVenda": fato_venda,
        "dCalendario": dcalendario(start, end),
    }
