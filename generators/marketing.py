"""generators/marketing.py — Setor Marketing Digital."""
import random
from datetime import date

import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CANAIS = ["Google Ads", "Meta Ads", "TikTok Ads", "LinkedIn Ads", "Email Marketing",
          "SEO Orgânico", "Influenciador", "Afiliado", "YouTube Ads", "Programático"]

OBJETIVOS = ["Awareness", "Consideração", "Conversão", "Retenção", "Reativação"]

FORMATOS = ["Banner Display", "Vídeo 15s", "Vídeo 30s", "Stories", "Reels",
            "Search Text", "Carrossel", "Native Ad", "Email HTML", "SMS"]

SEGMENTOS_AUDIENCIA = ["18-24", "25-34", "35-44", "45-54", "55+"]

DISPOSITIVOS = ["Mobile", "Desktop", "Tablet"]

SETORES_CLIENTE = ["Varejo", "E-commerce", "Saúde", "Educação", "Financeiro",
                   "Tecnologia", "Imobiliário", "Turismo", "Alimentação", "Moda"]

GESTORES = [fake.name() for _ in range(15)]


def gerar_marketing(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    """
    Gera dados do setor Marketing Digital em Star Schema.

    Tabelas: DimCampanha, DimCanal, DimCliente, DimGestor,
             FatoPerformance, FatoConversao, dCalendario
    """
    if n is None or n <= 0:
        n = 1_000
    n = int(n)

    # ── DimGestor ────────────────────────────────────────────────────────────
    n_gest = len(GESTORES)
    dim_gestor = pd.DataFrame({
        "id_gestor":        new_ids(n_gest),
        "nome":             GESTORES,
        "especialidade":    random.choices(["Performance", "Branding", "CRM", "SEO/SEM", "Social"], k=n_gest),
        "certificacoes":    rng.integers(0, 8, n_gest),
        "ativo":            random.choices([True, False], weights=[87, 13], k=n_gest),
        "data_admissao":    rand_dates(date(2016, 1, 1), end, n_gest),
    })

    # ── DimCanal ─────────────────────────────────────────────────────────────
    n_can = len(CANAIS)
    dim_canal = pd.DataFrame({
        "id_canal":     new_ids(n_can),
        "nome":         CANAIS,
        "tipo":         random.choices(["Pago", "Orgânico", "Owned"], weights=[70, 20, 10], k=n_can),
        "cpm_medio":    rng.uniform(5, 80, n_can).round(2),
        "cpc_medio":    rng.uniform(0.5, 15, n_can).round(2),
        "benchmark_ctr": rng.uniform(0.5, 5, n_can).round(2),
    })

    # ── DimCliente ───────────────────────────────────────────────────────────
    n_cli = min(max(n // 10, 100), 500)
    dim_cliente = pd.DataFrame({
        "id_cliente":       new_ids(n_cli),
        "nome_empresa":     [fake.company() for _ in range(n_cli)],
        "setor":            random.choices(SETORES_CLIENTE, k=n_cli),
        "porte":            random.choices(["PME", "Médio", "Grande", "Enterprise"], weights=[40, 30, 20, 10], k=n_cli),
        "budget_mensal":    rng.uniform(2_000, 500_000, n_cli).round(2),
        "id_gestor":        random.choices(dim_gestor["id_gestor"].tolist(), k=n_cli),
        "data_inicio":      rand_dates(date(2018, 1, 1), end, n_cli),
        "ativo":            random.choices([True, False], weights=[80, 20], k=n_cli),
    })

    # ── DimCampanha ──────────────────────────────────────────────────────────
    n_camp = min(max(n // 4, 200), 2_000)
    dim_campanha = pd.DataFrame({
        "id_campanha":      new_ids(n_camp),
        "nome":             [f"Camp_{fake.word().capitalize()}_{rng.integers(100,999)}" for _ in range(n_camp)],
        "id_cliente":       random.choices(dim_cliente["id_cliente"].tolist(), k=n_camp),
        "id_canal":         random.choices(dim_canal["id_canal"].tolist(), k=n_camp),
        "objetivo":         random.choices(OBJETIVOS, k=n_camp),
        "formato":          random.choices(FORMATOS, k=n_camp),
        "segmento_idade":   random.choices(SEGMENTOS_AUDIENCIA, k=n_camp),
        "budget_total":     rng.uniform(1_000, 200_000, n_camp).round(2),
        "data_inicio":      rand_dates(start, end, n_camp),
        "ativa":            random.choices([True, False], weights=[60, 40], k=n_camp),
    })

    # ── FatoPerformance ──────────────────────────────────────────────────────
    impressoes = rng.integers(100, 5_000_000, n)
    cliques = (impressoes * rng.uniform(0.005, 0.08, n)).astype(int)
    investimento = rng.uniform(50, 50_000, n).round(2)

    fato_performance = pd.DataFrame({
        "id_performance":   new_ids(n),
        "id_data":          rand_dates(start, end, n),
        "id_campanha":      random.choices(dim_campanha["id_campanha"].tolist(), k=n),
        "id_canal":         random.choices(dim_canal["id_canal"].tolist(), k=n),
        "dispositivo":      random.choices(DISPOSITIVOS, weights=[65, 30, 5], k=n),
        "impressoes":       impressoes,
        "cliques":          cliques,
        "ctr_pct":          (cliques / impressoes * 100).round(2),
        "investimento":     investimento,
        "cpm":              (investimento / impressoes * 1000).round(2),
        "cpc":              (investimento / (cliques + 1)).round(2),
        "alcance":          (impressoes * rng.uniform(0.6, 0.95, n)).astype(int),
        "frequencia":       rng.uniform(1, 8, n).round(1),
        "video_views":      rng.integers(0, 500_000, n),
        "engajamentos":     rng.integers(0, 50_000, n),
    })

    # ── FatoConversao ────────────────────────────────────────────────────────
    n_conv = int(n * 0.6)
    receita = rng.uniform(100, 500_000, n_conv).round(2)
    invest_conv = rng.uniform(50, 50_000, n_conv).round(2)

    fato_conversao = pd.DataFrame({
        "id_conversao":     new_ids(n_conv),
        "id_data":          rand_dates(start, end, n_conv),
        "id_campanha":      random.choices(dim_campanha["id_campanha"].tolist(), k=n_conv),
        "id_cliente":       random.choices(dim_cliente["id_cliente"].tolist(), k=n_conv),
        "conversoes":       rng.integers(0, 1_000, n_conv),
        "receita_gerada":   receita,
        "investimento":     invest_conv,
        "roas":             (receita / (invest_conv + 1)).round(2),
        "cpa":              (invest_conv / (rng.integers(1, 100, n_conv))).round(2),
        "taxa_conversao":   rng.uniform(0.5, 15, n_conv).round(2),
        "leads_gerados":    rng.integers(0, 5_000, n_conv),
        "cpl":              rng.uniform(5, 500, n_conv).round(2),
        "roi_pct":          rng.uniform(-20, 400, n_conv).round(1),
    })

    return {
        "DimGestor":        dim_gestor,
        "DimCanal":         dim_canal,
        "DimCliente":       dim_cliente,
        "DimCampanha":      dim_campanha,
        "FatoPerformance":  fato_performance,
        "FatoConversao":    fato_conversao,
        "dCalendario":      dcalendario(start, end),
    }
