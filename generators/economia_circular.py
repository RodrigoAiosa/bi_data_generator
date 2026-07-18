# generators/economia_circular.py
"""generators/economia_circular.py — Setor Economia Circular & Reciclagem."""

import random
from datetime import date

import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

MATERIAIS_RECICLAVEIS = [
    "PET", "PEAD", "PEBD", "PP", "PS", "PVC", "Vidro Âmbar", "Vidro Verde",
    "Vidro Transparente", "Papelão", "Papel Kraft", "Jornal", "Alumínio",
    "Aço", "Cobre", "Resíduo Orgânico", "Borracha", "Têxtil", "Eletrônicos"
]

CATEGORIAS_MATERIAL = ["Plástico", "Vidro", "Papel", "Metal", "Orgânico", "Outros"]
TIPOS_COLETA = ["Porta a Porta", "Ponto de Entrega", "Cooperativa", "Coleta Seletiva", "Empresa Parceira"]
STATUS_DESTINACAO = ["Reciclado", "Reutilizado", "Compostagem", "Aterro Sanitário", "Incineração"]
UFS_BRASIL = ["SP", "RJ", "MG", "RS", "PR", "SC", "BA", "PE", "CE", "GO", "DF", "MT", "MS", "AM", "PA"]

def gerar_economia_circular(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_coletas = min(n // 2 + 20, 300)
    n_materiais = len(MATERIAIS_RECICLAVEIS)
    n_parceiros = min(n // 3 + 15, 100)
    n_rotas = min(n // 5 + 10, 80)

    # ── DimMaterial ──────────────────────────────────────────
    dim_material = pd.DataFrame({
        "id_material": new_ids(n_materiais),
        "nome": MATERIAIS_RECICLAVEIS,
        "categoria": random.choices(CATEGORIAS_MATERIAL, k=n_materiais),
        "valor_kg": rng.uniform(0.1, 15, n_materiais).round(2),
        "periculosidade": random.choices(["Baixa", "Média", "Alta"], weights=[70, 20, 10], k=n_materiais),
        "tempo_decomposicao_anos": rng.uniform(1, 1000, n_materiais).round(0),
        "potencial_reciclagem_pct": rng.uniform(30, 95, n_materiais).round(1),
    })

    # ── DimParceiro ──────────────────────────────────────────
    dim_parceiro = pd.DataFrame({
        "id_parceiro": new_ids(n_parceiros),
        "nome": [f"{fake.company()}" for _ in range(n_parceiros)],
        "cnpj": [fake.cnpj() for _ in range(n_parceiros)],
        "segmento": random.choices(["Comércio", "Indústria", "Condomínio", "Eventos", "Órgão Público", "Agronegócio"], k=n_parceiros),
        "uf": random.choices(UFS_BRASIL, k=n_parceiros),
        "volume_mensal_kg": rng.uniform(100, 100000, n_parceiros).round(0),
        "certificacao_ambiental": random.choices([True, False], weights=[30, 70], k=n_parceiros),
        "data_inicio_parceria": rand_dates(start, end, n_parceiros),
    })

    # ── DimColetor ──────────────────────────────────────────
    n_coletor = max(5, min(n // 10, 50))
    dim_coletor = pd.DataFrame({
        "id_coletor": new_ids(n_coletor),
        "nome": [fake.name() for _ in range(n_coletor)],
        "tipo": random.choices(["Cooperativa", "Empresa Privada", "Associação", "Iniciativa Comunitária"], k=n_coletor),
        "capacidade_kg_dia": rng.integers(100, 5000, n_coletor),
        "uf": random.choices(UFS_BRASIL, k=n_coletor),
        "avaliacao": rng.uniform(2, 5, n_coletor).round(1),
    })

    # ── DimRota ─────────────────────────────────────────────
    dim_rota = pd.DataFrame({
        "id_rota": new_ids(n_rotas),
        "nome": [f"Rota {fake.city()}-{fake.city()}" for _ in range(n_rotas)],
        "distancia_km": rng.uniform(1, 200, n_rotas).round(1),
        "tempo_estimado_h": rng.uniform(0.5, 8, n_rotas).round(1),
        "custo_km": rng.uniform(0.5, 3, n_rotas).round(2),
        "tipo_veiculo": random.choices(["Caminhão", "Van", "Coleta Seletiva", "Caminhão", "Elétrico"], k=n_rotas),
    })

    # ── FatoColeta ──────────────────────────────────────────
    quantidade_kg = rng.uniform(5, 5000, n).round(2)
    fato = pd.DataFrame({
        "id_coleta": new_ids(n),
        "id_data": rand_dates(start, end, n),
        "id_material": random.choices(dim_material["id_material"].tolist(), k=n),
        "id_parceiro": random.choices(dim_parceiro["id_parceiro"].tolist(), k=n),
        "id_coletor": random.choices(dim_coletor["id_coletor"].tolist(), k=n),
        "id_rota": random.choices(dim_rota["id_rota"].tolist(), k=n),
        "tipo_coleta": random.choices(TIPOS_COLETA, weights=[35, 25, 20, 15, 5], k=n),
        "quantidade_kg": quantidade_kg,
        "valor_receita": (quantidade_kg * rng.uniform(0.1, 12, n)).round(2),
        "custo_coleta": (quantidade_kg * rng.uniform(0.05, 5, n)).round(2),
        "destinacao": random.choices(STATUS_DESTINACAO, weights=[60, 15, 10, 10, 5], k=n),
        "creditos_carbono_kgco2": rng.uniform(0, 50, n).round(2),
        "contaminacao_pct": rng.uniform(0, 30, n).round(1),
        "tempo_coleta_min": rng.integers(5, 240, n),
        "nps_parceiro": rng.integers(1, 11, n),
    })

    return {
        "DimMaterial": dim_material,
        "DimParceiro": dim_parceiro,
        "DimColetor": dim_coletor,
        "DimRota": dim_rota,
        "FatoColeta": fato,
        "dCalendario": dcalendario(start, end),
    }
