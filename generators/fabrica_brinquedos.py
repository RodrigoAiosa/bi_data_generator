"""generators/fabrica_brinquedos.py — Setor Fábrica de Brinquedos."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

CATEGORIAS = ["Pelúcia", "Eletrônico", "Educativo", "Boneca", "Veículo", "Jogo de Tabuleiro"]
FAIXAS_ETARIAS = ["0-2 anos", "3-5 anos", "6-9 anos", "10+ anos"]


def gerar_fabrica_brinquedos(n, start, end):
    n = max(int(n), 1)

    n_fabrica = min(max(n // 300, 3), 40)
    dim_fabrica = pd.DataFrame({
        "id_fabrica":        new_ids(n_fabrica),
        "cidade":            fake_pool(fake, "city", n_fabrica),
        "uf":                fake_pool(fake, "state_abbr", n_fabrica),
    })

    n_linha = min(max(n // 25, 20), 2500)
    dim_linha = pd.DataFrame({
        "id_linha":          new_ids(n_linha),
        "id_fabrica":        random.choices(dim_fabrica["id_fabrica"].tolist(), k=n_linha),
        "categoria":         random.choices(CATEGORIAS, k=n_linha),
        "faixa_etaria":      random.choices(FAIXAS_ETARIAS, k=n_linha),
    })

    fato_producao = pd.DataFrame({
        "id_producao":       new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_linha":          random.choices(dim_linha["id_linha"].tolist(), k=n),
        "unidades_produzidas": rng.integers(100, 20000, n),
        "custo_unitario":    rng.uniform(3, 90, n).round(2),
    })

    n_pedido = int(n * 1.1)
    fato_pedido = pd.DataFrame({
        "id_pedido":         new_ids(n_pedido),
        "id_data":           rand_dates(start, end, n_pedido),
        "id_linha":          random.choices(dim_linha["id_linha"].tolist(), k=n_pedido),
        "loja_cliente":      fake_pool(fake, "company", n_pedido),
        "unidades_pedidas":  rng.integers(5, 3000, n_pedido),
        "valor_total":       rng.uniform(100, 80000, n_pedido).round(2),
    })

    return {
        "DimFabrica": dim_fabrica,
        "DimLinha": dim_linha,
        "FatoProducao": fato_producao,
        "FatoPedido": fato_pedido,
        "dCalendario": dcalendario(start, end),
    }
