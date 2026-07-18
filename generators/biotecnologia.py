# generators/biotecnologia.py
"""generators/biotecnologia.py — Setor Biotecnologia & Genômica."""

import random
from datetime import date

import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_PROJETO = [
    "Sequenciamento Genômico", "Terapia Gênica", "Edição CRISPR",
    "Descoberta de Fármacos", "Diagnóstico Molecular", "Biotecnologia Vegetal",
    "Genômica Populacional", "Epigenética", "Proteômica"
]

GENES = [
    "BRCA1", "BRCA2", "TP53", "EGFR", "HER2", "KRAS", "APC", "MYC",
    "PTEN", "RB1", "VHL", "CDKN2A", "PALB2", "CHEK2", "NBN", "CDH1",
    "SMAD4", "FGFR2", "CTNNB1", "PIK3CA"
]

STATUS_EXPERIMENTO = ["Planejado", "Em Andamento", "Concluído", "Falha", "Repetir"]
SEQUENCIADORES = ["Illumina NovaSeq", "Illumina HiSeq", "Oxford Nanopore", "PacBio", "Ion Torrent"]
ESPECIES = ["Humano", "Mus musculus", "Drosophila", "C. elegans", "Zebrafish", "E. coli", "S. cerevisiae"]

def gerar_biotecnologia(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_projetos = min(n // 3 + 15, 100)
    n_cientistas = min(n // 4 + 10, 80)
    n_equipamentos = min(n // 5 + 8, 50)

    # ── DimProjeto ──────────────────────────────────────────
    dim_projeto = pd.DataFrame({
        "id_projeto": new_ids(n_projetos),
        "nome": [f"Projeto {fake.word().capitalize()} {rng.integers(1, 999)}" for _ in range(n_projetos)],
        "tipo": random.choices(TIPOS_PROJETO, k=n_projetos),
        "especie_estudo": random.choices(ESPECIES, k=n_projetos),
        "gene_principal": random.choices(GENES, k=n_projetos),
        "data_inicio": rand_dates(start, end, n_projetos),
        "data_previsao_fim": rand_dates(start, end, n_projetos),
        "orçamento_total": rng.uniform(100000, 10000000, n_projetos).round(2),
        "financiador": random.choices(["CAPES", "CNPq", "FAPESP", "Fulbright", "Wellcome", "NIH", "Privado"], k=n_projetos),
    })

    # ── DimCientista ────────────────────────────────────────
    dim_cientista = pd.DataFrame({
        "id_cientista": new_ids(n_cientistas),
        "nome": [fake.name() for _ in range(n_cientistas)],
        "especialidade": random.choices(["Genética", "Biologia Molecular", "Bioinformática", "Bioquímica", "Imunologia"], k=n_cientistas),
        "titulacao": random.choices(["PhD", "Doutor", "Pós-Doc", "Especialista", "Mestre"], weights=[25, 30, 20, 15, 10], k=n_cientistas),
        "anos_exp": rng.integers(0, 30, n_cientistas),
        "publicacoes": rng.integers(0, 80, n_cientistas),
        "custo_hora": rng.uniform(80, 500, n_cientistas).round(2),
    })

    # ── DimEquipamento ──────────────────────────────────────
    dim_equipamento = pd.DataFrame({
        "id_equipamento": new_ids(n_equipamentos),
        "tipo": random.choices(SEQUENCIADORES + ["Termociclador", "Centrífuga", "Espectrômetro", "Microscópio", "Citômetro"], k=n_equipamentos),
        "modelo": [f"Modelo {rng.integers(100, 999)}{chr(rng.integers(65, 90))}" for _ in range(n_equipamentos)],
        "capacidade_amostras": rng.integers(1, 384, n_equipamentos),
        "precisao_pct": rng.uniform(95, 99.99, n_equipamentos).round(2),
        "custo_operacao_hora": rng.uniform(50, 2000, n_equipamentos).round(2),
        "status": random.choices(["Operacional", "Manutenção", "Calibração", "Inativo"], weights=[75, 15, 7, 3], k=n_equipamentos),
    })

    # ── FatoExperimento ─────────────────────────────────────
    qtd_amostras = rng.integers(1, 1000, n)
    fato = pd.DataFrame({
        "id_experimento": new_ids(n),
        "id_data": rand_dates(start, end, n),
        "id_projeto": random.choices(dim_projeto["id_projeto"].tolist(), k=n),
        "id_cientista": random.choices(dim_cientista["id_cientista"].tolist(), k=n),
        "id_equipamento": random.choices(dim_equipamento["id_equipamento"].tolist(), k=n),
        "gene_estudado": random.choices(GENES, k=n),
        "quantidade_amostras": qtd_amostras,
        "taxa_sucesso_pct": rng.uniform(40, 98, n).round(1),
        "custo_total": (qtd_amostras * rng.uniform(10, 500, n)).round(2),
        "tempo_analise_horas": rng.uniform(0.5, 120, n).round(1),
        "status": random.choices(STATUS_EXPERIMENTO, weights=[10, 30, 45, 10, 5], k=n),
        "mutacao_encontrada": random.choices([True, False], weights=[25, 75], k=n),
        "sequencia_qualidade_pct": rng.uniform(85, 99.9, n).round(1),
        "publicacao_gerada": random.choices([True, False], weights=[15, 85], k=n),
        "replicabilidade": random.choices(["Alta", "Média", "Baixa"], weights=[60, 30, 10], k=n),
    })

    return {
        "DimProjeto": dim_projeto,
        "DimCientista": dim_cientista,
        "DimEquipamento": dim_equipamento,
        "FatoExperimento": fato,
        "dCalendario": dcalendario(start, end),
    }
