"""generators/farmaceutico.py — Setor Farmacêutico."""
import random
from datetime import date

import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CLASSES_TERAPEUTICAS = [
    "Analgésico", "Antibiótico", "Anti-inflamatório", "Antidiabético",
    "Antihipertensivo", "Antidepressivo", "Anticoagulante", "Vitaminas & Suplementos",
    "Dermatológico", "Gastroenterológico", "Respiratório", "Oncológico",
]

TIPOS_PRODUTO = ["Referência", "Genérico", "Similar", "Biológico", "Fitoterápico", "OTC"]

CANAIS_VENDA = ["Farmácia Independente", "Rede de Farmácias", "Hospital", "Clínica", "E-commerce Saúde", "Distribuidora"]

FORMAS_FARMACEUTICAS = ["Comprimido", "Cápsula", "Solução Oral", "Injetável", "Creme/Pomada", "Spray", "Adesivo", "Supositório"]

REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]

REPRESENTANTES = [fake.name() for _ in range(25)]


def gerar_farmaceutico(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    """
    Gera dados do setor Farmacêutico em Star Schema.

    Tabelas: DimProduto, DimCliente, DimRepresentante, DimDistribuidora,
             FatoVenda, FatoEstoque, dCalendario
    """
    if n is None or n <= 0:
        n = 1_000
    n = int(n)

    # ── DimRepresentante ─────────────────────────────────────────────────────
    n_rep = len(REPRESENTANTES)
    dim_representante = pd.DataFrame({
        "id_representante": new_ids(n_rep),
        "nome":             REPRESENTANTES,
        "regiao":           random.choices(REGIOES, k=n_rep),
        "uf":               [fake.state_abbr() for _ in range(n_rep)],
        "meta_trimestral":  rng.uniform(50_000, 500_000, n_rep).round(2),
        "ativo":            random.choices([True, False], weights=[88, 12], k=n_rep),
        "data_admissao":    rand_dates(date(2010, 1, 1), end, n_rep),
    })

    # ── DimProduto ───────────────────────────────────────────────────────────
    n_prod = 80
    dim_produto = pd.DataFrame({
        "id_produto":           new_ids(n_prod),
        "nome_comercial":       [f"{fake.last_name()} {random.choice(['Plus','Max','Neo','Forte','D'])}" for _ in range(n_prod)],
        "principio_ativo":      [fake.last_name() for _ in range(n_prod)],
        "classe_terapeutica":   random.choices(CLASSES_TERAPEUTICAS, k=n_prod),
        "tipo":                 random.choices(TIPOS_PRODUTO, weights=[15, 40, 25, 5, 10, 5], k=n_prod),
        "forma_farmaceutica":   random.choices(FORMAS_FARMACEUTICAS, k=n_prod),
        "concentracao":         [f"{random.choice([10,25,50,100,250,500,1000])}mg" for _ in range(n_prod)],
        "registro_anvisa":      [f"1.{rng.integers(1000,9999)}.{rng.integers(1000,9999)}.{rng.integers(100,999)}-{rng.integers(1,9)}" for _ in range(n_prod)],
        "preco_fabrica":        rng.uniform(5, 2_000, n_prod).round(2),
        "preco_consumidor":     rng.uniform(8, 3_000, n_prod).round(2),
        "necessita_receita":    random.choices([True, False], weights=[55, 45], k=n_prod),
        "controlado":           random.choices([True, False], weights=[20, 80], k=n_prod),
        "ativo":                random.choices([True, False], weights=[90, 10], k=n_prod),
    })

    # ── DimCliente ───────────────────────────────────────────────────────────
    n_cli = min(max(n // 8, 150), 1_000)
    dim_cliente = pd.DataFrame({
        "id_cliente":       new_ids(n_cli),
        "nome":             [fake.company() for _ in range(n_cli)],
        "cnpj":             [fake.cnpj() for _ in range(n_cli)],
        "canal":            random.choices(CANAIS_VENDA, k=n_cli),
        "uf":               [fake.state_abbr() for _ in range(n_cli)],
        "cidade":           [fake.city() for _ in range(n_cli)],
        "regiao":           random.choices(REGIOES, k=n_cli),
        "id_representante": random.choices(dim_representante["id_representante"].tolist(), k=n_cli),
        "data_cadastro":    rand_dates(date(2015, 1, 1), end, n_cli),
        "ativo":            random.choices([True, False], weights=[85, 15], k=n_cli),
    })

    # ── DimDistribuidora ─────────────────────────────────────────────────────
    n_dist = 20
    dim_distribuidora = pd.DataFrame({
        "id_distribuidora": new_ids(n_dist),
        "nome":             [fake.company() for _ in range(n_dist)],
        "uf":               [fake.state_abbr() for _ in range(n_dist)],
        "regiao":           random.choices(REGIOES, k=n_dist),
        "prazo_entrega_d":  rng.integers(1, 10, n_dist),
    })

    # ── FatoVenda ────────────────────────────────────────────────────────────
    fato_venda = pd.DataFrame({
        "id_venda":           new_ids(n),
        "id_data":            rand_dates(start, end, n),
        "id_produto":         random.choices(dim_produto["id_produto"].tolist(), k=n),
        "id_cliente":         random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "id_representante":   random.choices(dim_representante["id_representante"].tolist(), k=n),
        "id_distribuidora":   random.choices(dim_distribuidora["id_distribuidora"].tolist(), k=n),
        "quantidade":         rng.integers(1, 500, n),
        "preco_unitario":     rng.uniform(5, 3_000, n).round(2),
        "desconto_pct":       rng.uniform(0, 30, n).round(1),
        "valor_bruto":        rng.uniform(50, 100_000, n).round(2),
        "valor_liquido":      rng.uniform(40, 95_000, n).round(2),
        "imposto_pct":        rng.uniform(12, 33, n).round(1),
        "margem_pct":         rng.uniform(5, 60, n).round(1),
        "devolvido":          random.choices([True, False], weights=[5, 95], k=n),
    })

    # ── FatoEstoque ──────────────────────────────────────────────────────────
    n_est = int(n * 0.4)
    fato_estoque = pd.DataFrame({
        "id_estoque":         new_ids(n_est),
        "id_data":            rand_dates(start, end, n_est),
        "id_produto":         random.choices(dim_produto["id_produto"].tolist(), k=n_est),
        "id_distribuidora":   random.choices(dim_distribuidora["id_distribuidora"].tolist(), k=n_est),
        "qtd_disponivel":     rng.integers(0, 10_000, n_est),
        "qtd_reservada":      rng.integers(0, 2_000, n_est),
        "dias_cobertura":     rng.integers(0, 90, n_est),
        "lote":               [f"L{rng.integers(10000,99999)}" for _ in range(n_est)],
        "validade":           rand_dates(end, date(end.year + 3, 12, 31), n_est),
        "ruptura":            random.choices([True, False], weights=[8, 92], k=n_est),
    })

    return {
        "DimRepresentante": dim_representante,
        "DimProduto":       dim_produto,
        "DimCliente":       dim_cliente,
        "DimDistribuidora": dim_distribuidora,
        "FatoVenda":        fato_venda,
        "FatoEstoque":      fato_estoque,
        "dCalendario":      dcalendario(start, end),
    }
