"""generators/optica.py — Setor Óptica."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS_PRODUTO = ["Armação", "Lente de Grau", "Óculos de Sol", "Lente de Contato", "Acessório"]
MARCAS = ["Ray-Ban", "Oakley", "Chilli Beans", "Zeiss", "Essilor", "Vogue", "Marca Própria"]
TIPOS_EXAME = ["Refração", "Vista Cansada (Presbiopia)", "Adaptação de Lente de Contato", "Triagem Visual"]


def gerar_optica(n, start, end):
    n = max(int(n), 1)

    n_produto = min(max(n // 25, 30), 1500)
    dim_produto = pd.DataFrame({
        "id_produto":        new_ids(n_produto),
        "nome":              [f"{random.choice(MARCAS)} {fake.word().capitalize()}" for _ in range(n_produto)],
        "categoria":         random.choices(CATEGORIAS_PRODUTO, weights=[30, 30, 20, 15, 5], k=n_produto),
        "marca":             random.choices(MARCAS, k=n_produto),
        "preco":             rng.uniform(25, 2500, n_produto).round(2),
    })

    n_cliente = min(max(n // 5, 150), 12000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.name() for _ in range(n_cliente)],
        "idade":             rng.integers(5, 90, n_cliente),
        "uf":                [fake.state_abbr() for _ in range(n_cliente)],
    })

    qtd = rng.integers(1, 4, n)
    produto_idx = random.choices(range(n_produto), k=n)
    preco_unit = dim_produto["preco"].to_numpy()[produto_idx]
    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_produto":        dim_produto["id_produto"].to_numpy()[produto_idx],
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "quantidade":        qtd,
        "valor_total":       (qtd * preco_unit).round(2),
        "convenio_saude":    random.choices([True, False], weights=[35, 65], k=n),
    })

    n_exame = int(n_cliente * 0.6)
    fato_exame = pd.DataFrame({
        "id_exame":          new_ids(n_exame),
        "id_data":           rand_dates(start, end, n_exame),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n_exame),
        "tipo_exame":        random.choices(TIPOS_EXAME, k=n_exame),
        "grau_od":           rng.uniform(-8, 6, n_exame).round(2),
        "grau_oe":           rng.uniform(-8, 6, n_exame).round(2),
    })

    return {
        "DimProduto": dim_produto,
        "DimCliente": dim_cliente,
        "FatoVenda": fato_venda,
        "FatoExame": fato_exame,
        "dCalendario": dcalendario(start, end),
    }
