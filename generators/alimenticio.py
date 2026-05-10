"""generators/alimenticio.py — Setor Indústria de Alimentos & Bebidas."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS_PRODUTO = [
    "Carne Bovina", "Carne Suína", "Frango", "Laticínio", "Embutido",
    "Bebida Alcoólica", "Bebida Não-Alcoólica", "Snack", "Massa", "Conserva",
    "Óleo & Gordura", "Açúcar & Doce", "Café & Chá", "Condimento", "Congelado",
    "Sorvete", "Pão & Biscoito", "Fruta Processada", "Ração Animal", "Suplemento",
]

UFS_PLANTAS = ["SP", "PR", "RS", "SC", "GO", "MG", "MT", "MS", "BA", "RJ"]

CERTIFICACOES = ["ISO 22000", "FSSC 22000", "BRC", "IFS", "HACCP", "Orgânico", "Kosher", "Halal"]


def gerar_alimenticio(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_plantas    = min(n // 5 + 30, 200)
    n_produtos   = 80
    n_fornecedores = 60

    dim_produto = pd.DataFrame({
        "id_produto":      new_ids(n_produtos),
        "nome":            [f"{random.choice(CATEGORIAS_PRODUTO)} {fake.word().capitalize()}" for _ in range(n_produtos)],
        "categoria":       random.choices(CATEGORIAS_PRODUTO, k=n_produtos),
        "sku":             [fake.bothify("??-####-??").upper() for _ in range(n_produtos)],
        "peso_kg":         rng.uniform(0.1, 25, n_produtos).round(3),
        "validade_dias":   rng.integers(7, 730, n_produtos),
        "temp_conservacao":random.choices(["Ambiente", "Refrigerado", "Congelado"], weights=[40, 35, 25], k=n_produtos),
        "preco_kg":        rng.uniform(2, 500, n_produtos).round(2),
    })

    dim_planta = pd.DataFrame({
        "id_planta":    new_ids(n_plantas),
        "nome":         [f"Planta {fake.city()}" for _ in range(n_plantas)],
        "empresa":      [fake.company() for _ in range(n_plantas)],
        "cnpj":         [fake.cnpj() for _ in range(n_plantas)],
        "uf":           random.choices(UFS_PLANTAS, k=n_plantas),
        "capacidade_ton_dia": rng.uniform(10, 5000, n_plantas).round(1),
        "n_funcionarios":     rng.integers(20, 5000, n_plantas),
        "certificacao": [random.choice(CERTIFICACOES) for _ in range(n_plantas)],
        "tipo":         random.choices(["Frigorífico", "Laticínio", "Bebidas", "Processados", "Grãos"], k=n_plantas),
    })

    dim_fornecedor = pd.DataFrame({
        "id_fornecedor":   new_ids(n_fornecedores),
        "nome":            [fake.company() for _ in range(n_fornecedores)],
        "cnpj":            [fake.cnpj() for _ in range(n_fornecedores)],
        "tipo_materia":    random.choices(["Grão", "Proteína Animal", "Vegetal", "Embalagem", "Aditivo"], k=n_fornecedores),
        "uf":              random.choices(UFS_PLANTAS, k=n_fornecedores),
        "prazo_entrega_d": rng.integers(1, 30, n_fornecedores),
        "avaliacao":       rng.uniform(1, 5, n_fornecedores).round(1),
    })

    volume_prod = rng.uniform(0.5, 200, n).round(2)

    fato = pd.DataFrame({
        "id_producao":        new_ids(n),
        "id_data":            rand_dates(start, end, n),
        "id_planta":          random.choices(dim_planta["id_planta"].tolist(), k=n),
        "id_produto":         random.choices(dim_produto["id_produto"].tolist(), k=n),
        "id_fornecedor":      random.choices(dim_fornecedor["id_fornecedor"].tolist(), k=n),
        "lote":               [fake.bothify("L-#####-????").upper() for _ in range(n)],
        "volume_produzido_kg":volume_prod,
        "volume_refugo_kg":   (volume_prod * rng.uniform(0, 0.15, n)).round(2),
        "indice_refugo_pct":  rng.uniform(0, 15, n).round(2),
        "custo_materia_prima":rng.uniform(100, 500000, n).round(2),
        "custo_producao":     rng.uniform(200, 800000, n).round(2),
        "receita":            rng.uniform(500, 1500000, n).round(2),
        "temperatura_proc_c": rng.uniform(-25, 200, n).round(1),
        "horas_maquina":      rng.uniform(1, 24, n).round(1),
        "conformidade_anvisa":random.choices([True, False], weights=[92, 8], k=n),
        "status":             random.choices(["Concluído", "Em Processo", "Pausado", "Recall"], weights=[70, 20, 8, 2], k=n),
    })

    return {
        "DimProduto":    dim_produto,
        "DimPlanta":     dim_planta,
        "DimFornecedor": dim_fornecedor,
        "FatoProducao":  fato,
        "dCalendario":   dcalendario(start, end),
    }
