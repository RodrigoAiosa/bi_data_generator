"""generators/petroleo.py — Setor Petróleo & Gás."""
import random
from datetime import date

import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_POCO = ["Exploratório", "Produtor", "Injetor", "Abandonado", "Suspenso"]
FASES_POCO = ["Perfuração", "Completação", "Produção", "Manutenção", "Desativado"]
TIPOS_FLUIDO = ["Óleo Leve", "Óleo Médio", "Óleo Pesado", "Gás Natural", "Gás Associado", "Condensado"]
BACIAS = ["Santos", "Campos", "Espírito Santo", "Potiguar", "Recôncavo", "Solimões", "Parnaíba"]
PLATAFORMAS = [f"P-{i}" for i in random.sample(range(10, 99), 15)]
OPERADORAS = ["Petrobras", "Shell", "TotalEnergies", "Equinor", "BP", "Repsol", "Chevron"]
TIPOS_CUSTO = ["Lifting", "CAPEX Perfuração", "CAPEX Completação", "OPEX Manutenção",
               "Logística Marítima", "Royalties", "PARTICIPAÇÃO ESPECIAL", "Seguro"]


def gerar_petroleo(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    """
    Gera dados do setor Petróleo & Gás em Star Schema.

    Tabelas: DimPoco, DimPlataforma, DimBacia, DimOperadora,
             FatoProducao, FatoCusto, dCalendario
    """
    if n is None or n <= 0:
        n = 1_000
    n = int(n)

    # ── DimOperadora ─────────────────────────────────────────────────────────
    n_op = len(OPERADORAS)
    dim_operadora = pd.DataFrame({
        "id_operadora":     new_ids(n_op),
        "nome":             OPERADORAS,
        "pais_sede":        ["Brasil", "Países Baixos", "França", "Noruega", "Reino Unido", "Espanha", "EUA"],
        "participacao_pct": rng.uniform(10, 100, n_op).round(1),
        "desde_ano":        rng.integers(1960, 2010, n_op),
    })

    # ── DimBacia ─────────────────────────────────────────────────────────────
    n_bac = len(BACIAS)
    dim_bacia = pd.DataFrame({
        "id_bacia":         new_ids(n_bac),
        "nome":             BACIAS,
        "tipo":             random.choices(["Offshore", "Onshore"], weights=[65, 35], k=n_bac),
        "uf":               ["SP", "RJ", "ES", "RN", "BA", "AM", "MA"],
        "area_km2":         rng.uniform(5_000, 200_000, n_bac).round(0),
        "profundidade_max_m": rng.uniform(100, 3_000, n_bac).round(0),
    })

    # ── DimPlataforma ────────────────────────────────────────────────────────
    n_plat = len(PLATAFORMAS)
    dim_plataforma = pd.DataFrame({
        "id_plataforma":    new_ids(n_plat),
        "nome":             PLATAFORMAS,
        "tipo":             random.choices(["FPSO", "Semi-submersível", "Fixa", "TLP", "Spar"], k=n_plat),
        "id_bacia":         random.choices(dim_bacia["id_bacia"].tolist(), k=n_plat),
        "id_operadora":     random.choices(dim_operadora["id_operadora"].tolist(), k=n_plat),
        "capacidade_bbl_d": rng.integers(10_000, 300_000, n_plat),
        "ano_instalacao":   rng.integers(1975, 2022, n_plat),
        "ativa":            random.choices([True, False], weights=[85, 15], k=n_plat),
    })

    # ── DimPoço ──────────────────────────────────────────────────────────────
    n_poco = min(max(n // 5, 100), 800)
    dim_poco = pd.DataFrame({
        "id_poco":          new_ids(n_poco),
        "nome":             [f"{random.choice(BACIAS[:3])[:3].upper()}-{rng.integers(1,999):03d}" for _ in range(n_poco)],
        "tipo":             random.choices(TIPOS_POCO, weights=[15, 50, 20, 10, 5], k=n_poco),
        "fase":             random.choices(FASES_POCO, k=n_poco),
        "tipo_fluido":      random.choices(TIPOS_FLUIDO, k=n_poco),
        "id_plataforma":    random.choices(dim_plataforma["id_plataforma"].tolist(), k=n_poco),
        "id_bacia":         random.choices(dim_bacia["id_bacia"].tolist(), k=n_poco),
        "profundidade_m":   rng.uniform(500, 7_000, n_poco).round(0),
        "lamina_agua_m":    rng.uniform(0, 3_000, n_poco).round(0),
        "data_perfuracao":  rand_dates(date(1990, 1, 1), end, n_poco),
        "ativo":            random.choices([True, False], weights=[70, 30], k=n_poco),
    })

    # ── FatoProducao ─────────────────────────────────────────────────────────
    fato_producao = pd.DataFrame({
        "id_producao":      new_ids(n),
        "id_data":          rand_dates(start, end, n),
        "id_poco":          random.choices(dim_poco["id_poco"].tolist(), k=n),
        "id_plataforma":    random.choices(dim_plataforma["id_plataforma"].tolist(), k=n),
        "id_operadora":     random.choices(dim_operadora["id_operadora"].tolist(), k=n),
        "vol_oleo_bbl":     rng.uniform(0, 50_000, n).round(0),
        "vol_gas_mm3":      rng.uniform(0, 5_000, n).round(1),
        "vol_agua_bbl":     rng.uniform(0, 30_000, n).round(0),
        "grau_api":         rng.uniform(10, 45, n).round(1),
        "bsw_pct":          rng.uniform(0, 90, n).round(1),   # Basic Sediment & Water
        "gor_m3m3":         rng.uniform(10, 500, n).round(1), # Gas-Oil Ratio
        "preco_bbl_usd":    rng.uniform(40, 120, n).round(2),
        "receita_usd":      rng.uniform(10_000, 5_000_000, n).round(2),
        "horas_producao":   rng.uniform(0, 24, n).round(1),
        "eficiencia_pct":   rng.uniform(60, 100, n).round(1),
        "parada_programada": random.choices([True, False], weights=[15, 85], k=n),
    })

    # ── FatoCusto ────────────────────────────────────────────────────────────
    n_custo = int(n * 0.5)
    fato_custo = pd.DataFrame({
        "id_custo":         new_ids(n_custo),
        "id_data":          rand_dates(start, end, n_custo),
        "id_poco":          random.choices(dim_poco["id_poco"].tolist(), k=n_custo),
        "id_plataforma":    random.choices(dim_plataforma["id_plataforma"].tolist(), k=n_custo),
        "id_operadora":     random.choices(dim_operadora["id_operadora"].tolist(), k=n_custo),
        "tipo_custo":       random.choices(TIPOS_CUSTO, k=n_custo),
        "valor_usd":        rng.uniform(10_000, 10_000_000, n_custo).round(2),
        "lifting_cost_bbl": rng.uniform(5, 40, n_custo).round(2),
        "capex":            random.choices([True, False], weights=[30, 70], k=n_custo),
        "opex":             random.choices([True, False], weights=[70, 30], k=n_custo),
    })

    return {
        "DimOperadora":   dim_operadora,
        "DimBacia":       dim_bacia,
        "DimPlataforma":  dim_plataforma,
        "DimPoco":        dim_poco,
        "FatoProducao":   fato_producao,
        "FatoCusto":      fato_custo,
        "dCalendario":    dcalendario(start, end),
    }
