"""generators/comercio_exterior.py — Setor Comércio Exterior."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

PAISES = ["China", "Estados Unidos", "Alemanha", "Argentina", "Índia", "Japão",
          "México", "Chile", "Países Baixos", "Coreia do Sul", "Itália", "Reino Unido"]
CATEGORIAS_PRODUTO = ["Eletrônicos", "Máquinas e Equipamentos", "Autopeças", "Têxteis",
                       "Químicos", "Commodities Agrícolas", "Bens de Consumo", "Metais"]
INCOTERMS = ["FOB", "CIF", "EXW", "DDP", "FCA", "CFR"]
MODAIS = ["Marítimo", "Aéreo", "Rodoviário", "Ferroviário"]
STATUS_DESEMBARACO = ["Liberado", "Em Conferência", "Retido", "Canal Verde", "Canal Amarelo", "Canal Vermelho"]


def gerar_comercio_exterior(n, start, end):
    n = max(int(n), 1)

    n_produto = min(max(n // 25, 25), 500)
    dim_produto = pd.DataFrame({
        "id_produto":        new_ids(n_produto),
        "nome_produto":      [fake.word().capitalize() for _ in range(n_produto)],
        "categoria":         random.choices(CATEGORIAS_PRODUTO, k=n_produto),
        "ncm":               [f"{rng.integers(1000,9999)}.{rng.integers(10,99)}.{rng.integers(10,99)}" for _ in range(n_produto)],
        "peso_unitario_kg":  rng.uniform(0.1, 500, n_produto).round(2),
    })

    dim_pais = pd.DataFrame({
        "id_pais":               new_ids(len(PAISES)),
        "pais":                  PAISES,
        "modal_predominante":    random.choices(MODAIS, weights=[55, 15, 25, 5], k=len(PAISES)),
    })

    fato_importacao = pd.DataFrame({
        "id_importacao":        new_ids(n),
        "id_data":              rand_dates(start, end, n),
        "id_produto":           random.choices(dim_produto["id_produto"].tolist(), k=n),
        "id_pais":              random.choices(dim_pais["id_pais"].tolist(), k=n),
        "modal":                random.choices(MODAIS, weights=[45, 20, 30, 5], k=n),
        "incoterm":             random.choices(INCOTERMS, k=n),
        "valor_fob_usd":        rng.uniform(500, 250000, n).round(2),
        "valor_impostos_reais": rng.uniform(200, 180000, n).round(2),
        "peso_liquido_kg":      rng.uniform(10, 20000, n).round(1),
        "status_desembaraco":   random.choices(STATUS_DESEMBARACO, weights=[55, 15, 5, 10, 10, 5], k=n),
    })

    n_exp = int(n * 0.55)
    fato_exportacao = pd.DataFrame({
        "id_exportacao":     new_ids(n_exp),
        "id_data":           rand_dates(start, end, n_exp),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n_exp),
        "id_pais":           random.choices(dim_pais["id_pais"].tolist(), k=n_exp),
        "modal":             random.choices(MODAIS, weights=[60, 15, 20, 5], k=n_exp),
        "valor_fob_usd":     rng.uniform(500, 300000, n_exp).round(2),
        "peso_liquido_kg":   rng.uniform(10, 25000, n_exp).round(1),
    })

    return {
        "DimProduto": dim_produto,
        "DimPais": dim_pais,
        "FatoImportacao": fato_importacao,
        "FatoExportacao": fato_exportacao,
        "dCalendario": dcalendario(start, end),
    }
