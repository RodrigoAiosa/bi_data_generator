"""generators/concessionaria.py — Setor Concessionária de Veículos."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

MARCAS = ["Volkswagen", "Chevrolet", "Fiat", "Toyota", "Hyundai", "Honda", "Jeep", "Renault"]
CATEGORIAS = ["Hatch", "Sedan", "SUV", "Picape", "Utilitário"]
CORES = ["Branco", "Prata", "Preto", "Cinza", "Vermelho", "Azul"]
TIPOS_VENDA = ["Novo", "Seminovo"]
FORMAS_PAGAMENTO = ["À Vista", "Financiado", "Consórcio", "Leasing"]


def gerar_concessionaria(n, start, end):
    n = max(int(n), 1)

    n_veiculo = min(max(n // 8, 40), 2000)
    preco_tabela = rng.uniform(45000, 320000, n_veiculo).round(2)
    dim_veiculo = pd.DataFrame({
        "id_veiculo":        new_ids(n_veiculo),
        "modelo":            [f"{random.choice(MARCAS)} {fake.word().capitalize()}" for _ in range(n_veiculo)],
        "marca":             random.choices(MARCAS, k=n_veiculo),
        "categoria":         random.choices(CATEGORIAS, weights=[25, 25, 30, 15, 5], k=n_veiculo),
        "ano_modelo":        rng.integers(2019, 2027, n_veiculo),
        "cor":               random.choices(CORES, k=n_veiculo),
        "preco_tabela":      preco_tabela,
    })

    n_vendedor = min(max(n // 100, 8), 150)
    dim_vendedor = pd.DataFrame({
        "id_vendedor":       new_ids(n_vendedor),
        "nome":              [fake.name() for _ in range(n_vendedor)],
        "filial":            random.choices([f"Filial {c}" for c in ["Centro","Norte","Sul","Shopping","Zona Leste"]], k=n_vendedor),
        "meta_mensal":       rng.integers(4, 25, n_vendedor),
    })

    tipo_venda = random.choices(TIPOS_VENDA, weights=[45, 55], k=n)
    veic_idx = random.choices(range(n_veiculo), k=n)
    valor_venda = dim_veiculo["preco_tabela"].to_numpy()[veic_idx] * rng.uniform(0.9, 1.05, n)
    fato_venda = pd.DataFrame({
        "id_venda":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_veiculo":        dim_veiculo["id_veiculo"].to_numpy()[veic_idx],
        "id_vendedor":       random.choices(dim_vendedor["id_vendedor"].tolist(), k=n),
        "tipo_venda":        tipo_venda,
        "forma_pagamento":   random.choices(FORMAS_PAGAMENTO, weights=[20, 55, 15, 10], k=n),
        "valor_venda":       valor_venda.round(2),
        "valor_entrada":     (valor_venda * rng.uniform(0.1, 0.4, n)).round(2),
        "comissao":          (valor_venda * rng.uniform(0.02, 0.05, n)).round(2),
        "km_veiculo":        [0 if t == "Novo" else int(rng.integers(5000, 120000)) for t in tipo_venda],
    })

    n_test = int(n * 1.8)
    convertido = random.choices([True, False], weights=[22, 78], k=n_test)
    fato_test_drive = pd.DataFrame({
        "id_test_drive":     new_ids(n_test),
        "id_data":           rand_dates(start, end, n_test),
        "id_veiculo":        random.choices(dim_veiculo["id_veiculo"].tolist(), k=n_test),
        "id_vendedor":       random.choices(dim_vendedor["id_vendedor"].tolist(), k=n_test),
        "convertido_venda":  convertido,
        "duracao_min":       rng.integers(10, 45, n_test),
    })

    return {
        "DimVeiculo": dim_veiculo,
        "DimVendedor": dim_vendedor,
        "FatoVenda": fato_venda,
        "FatoTestDrive": fato_test_drive,
        "dCalendario": dcalendario(start, end),
    }
