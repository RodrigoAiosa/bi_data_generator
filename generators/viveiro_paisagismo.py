"""generators/viveiro_paisagismo.py — Setor Viveiro & Paisagismo."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

CATEGORIAS_PLANTA = ["Árvore Ornamental", "Arbusto", "Forração", "Palmeira", "Suculenta", "Grama em Placas", "Muda Frutífera"]
CANAIS_VENDA = ["Loja Física", "Online", "Paisagista Parceiro", "Atacado para Construtoras"]
STATUS_PROJETO = ["Orçamento Enviado", "Aprovado", "Em Execução", "Concluído", "Cancelado"]
TIPOS_PROJETO = ["Jardim Residencial", "Área Corporativa", "Condomínio", "Praça Pública", "Telhado Verde"]


def gerar_viveiro_paisagismo(n, start, end):
    n = max(int(n), 1)

    n_planta = min(max(n // 40, 30), 1500)
    custo = rng.uniform(4, 250, n_planta).round(2)
    dim_planta = pd.DataFrame({
        "id_planta":         new_ids(n_planta),
        "nome":              [fake.word().capitalize() for _ in range(n_planta)],
        "categoria":         random.choices(CATEGORIAS_PLANTA, k=n_planta),
        "custo":             custo,
        "preco_venda":       (custo * rng.uniform(1.6, 3.2, n_planta)).round(2),
        "exige_sol_pleno":   random.choices([True, False], weights=[60, 40], k=n_planta),
    })

    n_cliente = min(max(n // 8, 100), 20000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              fake_pool(fake, "name", n_cliente),
        "tipo_cliente":      random.choices(["Pessoa Física", "Empresa", "Construtora", "Paisagista"], weights=[55, 20, 15, 10], k=n_cliente),
        "cidade":            fake_pool(fake, "city", n_cliente),
    })

    planta_idx = random.choices(range(n_planta), k=n)
    preco_unit = dim_planta["preco_venda"].to_numpy()[planta_idx]
    qtd = rng.integers(1, 30, n)
    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_planta":         dim_planta["id_planta"].to_numpy()[planta_idx],
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "quantidade":        qtd,
        "valor_total":       (qtd * preco_unit).round(2),
        "canal":             random.choices(CANAIS_VENDA, weights=[35, 20, 25, 20], k=n),
    })

    n_projeto = min(max(n_cliente // 6, 30), 3000)
    status_proj = random.choices(STATUS_PROJETO, weights=[20, 15, 20, 40, 5], k=n_projeto)
    fato_projeto = pd.DataFrame({
        "id_projeto":        new_ids(n_projeto),
        "id_data":           rand_dates(start, end, n_projeto),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n_projeto),
        "tipo_projeto":      random.choices(TIPOS_PROJETO, k=n_projeto),
        "area_m2":           rng.uniform(15, 5000, n_projeto).round(1),
        "valor_orcamento":   rng.uniform(2500, 350000, n_projeto).round(2),
        "status":            status_proj,
        "prazo_execucao_dias": rng.integers(3, 180, n_projeto),
    })

    return {
        "DimPlanta": dim_planta,
        "DimCliente": dim_cliente,
        "FatoVenda": fato_venda,
        "FatoProjetoPaisagismo": fato_projeto,
        "dCalendario": dcalendario(start, end),
    }
