"""generators/construcao.py — Setor Construção Civil."""

import random
from datetime import date

import numpy as np
import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_PROJETO = ["Residencial", "Comercial", "Infraestrutura", "Industrial", "Hospitalar"]
STATUS_PROJETO = ["Em Planejamento", "Em Execução", "Finalizado", "Atrasado", "Pausado"]

def gerar_construcao(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_projetos    = min(50, n // 100 + 10)
    n_materiais   = 100
    n_fornecedores = 30
    n_equipes     = 15
    
    dim_projeto = pd.DataFrame({
        "id_projeto": new_ids(n_projetos),
        "nome":       [f"Obra {fake.word().capitalize()} {i}" for i in range(1, n_projetos + 1)],
        "tipo":       random.choices(TIPOS_PROJETO, k=n_projetos),
        "status":     random.choices(STATUS_PROJETO, k=n_projetos),
        "cidade":     [fake.city() for _ in range(n_projetos)],
        "uf":         random.choices(["SP", "RJ", "MG", "RS", "PR", "SC", "BA", "CE", "PE", "GO"], k=n_projetos),
        "orcamento_previsto": rng.uniform(500000, 50000000, n_projetos).round(2)
    })

    dim_material = pd.DataFrame({
        "id_material": new_ids(n_materiais),
        "nome":        [f"Material {fake.word().capitalize()} {i}" for i in range(1, n_materiais + 1)],
        "categoria":   random.choices(["Estrutura", "Acabamento", "Elétrica", "Hidráulica", "Ferramentas"], k=n_materiais),
        "unidade":     random.choices(["kg", "m", "m2", "m3", "unid"], k=n_materiais),
        "preco_unit":  rng.uniform(5, 1000, n_materiais).round(2)
    })

    dim_fornecedor = pd.DataFrame({
        "id_fornecedor": new_ids(n_fornecedores),
        "nome":          [fake.company() for _ in range(n_fornecedores)],
        "cnpj":          [fake.cnpj() for _ in range(n_fornecedores)],
        "cidade":        [fake.city() for _ in range(n_fornecedores)]
    })

    dim_equipe = pd.DataFrame({
        "id_equipe": new_ids(n_equipes),
        "nome":      [f"Equipe {fake.first_name()}" for _ in range(n_equipes)],
        "lider":     [fake.name() for _ in range(n_equipes)],
        "especialidade": random.choices(["Alvenaria", "Elétrica", "Pintura", "Carpintaria", "Hidráulica"], k=n_equipes)
    })

    datas = rand_dates(start, end, n)
    materiais_ids = random.choices(dim_material["id_material"].tolist(), k=n)
    precos_unit = [dim_material.loc[dim_material["id_material"] == m, "preco_unit"].values[0] for m in materiais_ids]
    
    fato = pd.DataFrame({
        "id_consumo":  new_ids(n),
        "id_data":     datas,
        "id_projeto":  random.choices(dim_projeto["id_projeto"].tolist(), k=n),
        "id_material": materiais_ids,
        "id_fornecedor": random.choices(dim_fornecedor["id_fornecedor"].tolist(), k=n),
        "id_equipe":   random.choices(dim_equipe["id_equipe"].tolist(), k=n),
        "quantidade":  rng.uniform(1, 1000, n).round(2),
        "custo_real":  [round(p * rng.uniform(0.95, 1.1), 2) for p in precos_unit],
        "horas_trabalhadas": rng.uniform(4, 100, n).round(1)
    })

    return {
        "DimProjeto":    dim_projeto,
        "DimMaterial":   dim_material,
        "DimFornecedor": dim_fornecedor,
        "DimEquipe":     dim_equipe,
        "FatoCustos":    fato,
        "dCalendario":   dcalendario(start, end),
    }
