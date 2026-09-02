"""generators/livraria.py — Setor Livraria."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

GENEROS = ["Romance", "Não-Ficção", "Infantil", "Acadêmico", "Autoajuda", "Quadrinhos"]
CANAIS = ["Loja Física", "E-commerce"]


def gerar_livraria(n, start, end):
    n = max(int(n), 1)

    n_loja = min(max(n // 200, 4), 60)
    dim_loja = pd.DataFrame({
        "id_loja":           new_ids(n_loja),
        "cidade":            fake_pool(fake, "city", n_loja),
        "uf":                fake_pool(fake, "state_abbr", n_loja),
    })

    n_livro = min(max(n // 8, 200), 15000)
    dim_livro = pd.DataFrame({
        "id_livro":          new_ids(n_livro),
        "titulo":            [fake.sentence(nb_words=4).rstrip(".") for _ in range(n_livro)],
        "genero":            random.choices(GENEROS, k=n_livro),
        "preco_capa":        rng.uniform(25, 180, n_livro).round(2),
    })

    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_loja":           random.choices(dim_loja["id_loja"].tolist(), k=n),
        "id_livro":          random.choices(dim_livro["id_livro"].tolist(), k=n),
        "canal":             random.choices(CANAIS, weights=[55, 45], k=n),
        "quantidade":        rng.integers(1, 6, n),
        "valor_total":       rng.uniform(20, 900, n).round(2),
    })

    return {
        "DimLoja": dim_loja,
        "DimLivro": dim_livro,
        "FatoVenda": fato_venda,
        "dCalendario": dcalendario(start, end),
    }
