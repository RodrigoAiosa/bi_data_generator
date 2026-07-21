"""generators/editora.py — Setor Editora & Publicação."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

GENEROS = ["Ficção", "Não-Ficção", "Autoajuda", "Infantil", "Acadêmico", "Romance", "Negócios", "Biografia"]
FORMATOS = ["Físico", "E-book", "Audiobook"]
CANAIS = ["Livraria Física", "E-commerce Próprio", "Marketplace", "Distribuidor", "Venda Direta Autor"]
TIPOS_CANAL = ["Varejo", "Digital", "Atacado"]


def gerar_editora(n, start, end):
    n = max(int(n), 1)

    n_livro = min(max(n // 20, 30), 3000)
    preco = rng.uniform(19.9, 149.9, n_livro).round(2)
    dim_livro = pd.DataFrame({
        "id_livro":          new_ids(n_livro),
        "titulo":            [f"{fake.catch_phrase()}" for _ in range(n_livro)],
        "genero":            random.choices(GENEROS, k=n_livro),
        "autor":             [fake.name() for _ in range(n_livro)],
        "formato":           random.choices(FORMATOS, weights=[45, 40, 15], k=n_livro),
        "preco":             preco,
    })

    n_canal = min(max(n // 300, 5), 30)
    dim_canal = pd.DataFrame({
        "id_canal":          new_ids(n_canal),
        "nome":              random.choices(CANAIS, k=n_canal),
        "tipo":              random.choices(TIPOS_CANAL, k=n_canal),
    })

    qtd = rng.integers(1, 20, n)
    livro_idx = random.choices(range(n_livro), k=n)
    preco_unit = dim_livro["preco"].to_numpy()[livro_idx]
    valor_total = qtd * preco_unit
    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_livro":          dim_livro["id_livro"].to_numpy()[livro_idx],
        "id_canal":          random.choices(dim_canal["id_canal"].tolist(), k=n),
        "quantidade":        qtd,
        "valor_total":       valor_total.round(2),
        "royalties_autor":   (valor_total * rng.uniform(0.06, 0.15, n)).round(2),
    })

    n_estoque = int(n_livro * 3)
    qtd_impressa = rng.integers(500, 50000, n_estoque)
    fato_estoque = pd.DataFrame({
        "id_estoque_fato":   new_ids(n_estoque),
        "id_data":           rand_dates(start, end, n_estoque),
        "id_livro":          random.choices(dim_livro["id_livro"].tolist(), k=n_estoque),
        "quantidade_impressa": qtd_impressa,
        "quantidade_disponivel": (qtd_impressa * rng.uniform(0.05, 0.9, n_estoque)).round(0).astype(int),
        "devolucoes":        rng.integers(0, 500, n_estoque),
    })

    return {
        "DimLivro": dim_livro,
        "DimCanalVenda": dim_canal,
        "FatoVenda": fato_venda,
        "FatoEstoque": fato_estoque,
        "dCalendario": dcalendario(start, end),
    }
