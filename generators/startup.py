"""generators/startup.py — Setor Startups & Venture Capital."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

ESTAGIOS      = ["Pre-Seed","Seed","Series A","Series B","Series C","Growth","IPO"]
VERTICAIS     = ["Fintech","Healthtech","Edtech","Agtech","Proptech","Retailtech","Legaltech","HRtech","Insurtech","Deeptech"]
STATUS_STARTUP= ["Ativa","Faliu","Adquirida","IPO","Inativa"]
FUNDOS        = [fake.company()+" Ventures" for _ in range(20)]
METRICAS_SaaS = ["MRR","ARR","Churn","LTV","CAC","NPS","DAU","MAU"]

def gerar_startup(n, start, end):
    n = max(int(n), 1)
    n_st = min(max(n//4,50),400)
    dim_startup = pd.DataFrame({
        "id_startup":       new_ids(n_st),
        "nome":             [fake.company() for _ in range(n_st)],
        "vertical":         random.choices(VERTICAIS, k=n_st),
        "estagio":          random.choices(ESTAGIOS, weights=[20,25,20,15,10,7,3], k=n_st),
        "status":           random.choices(STATUS_STARTUP, weights=[70,8,10,5,7], k=n_st),
        "ano_fundacao":     rng.integers(2010, 2024, n_st),
        "n_fundadores":     rng.integers(1, 5, n_st),
        "n_funcionarios":   rng.integers(1, 500, n_st),
        "sede_uf":          [fake.state_abbr() for _ in range(n_st)],
        "mrr":              rng.uniform(0, 2_000_000, n_st).round(2),
        "arr":              rng.uniform(0, 24_000_000, n_st).round(2),
        "valuation":        rng.uniform(1_000_000, 1_000_000_000, n_st).round(2),
        "runway_meses":     rng.integers(0, 36, n_st),
        "burn_rate":        rng.uniform(10_000, 2_000_000, n_st).round(2),
    })
    n_fundo = len(FUNDOS)
    dim_fundo = pd.DataFrame({
        "id_fundo":         new_ids(n_fundo),
        "nome":             FUNDOS,
        "aum_brl":          rng.uniform(5_000_000, 2_000_000_000, n_fundo).round(2),
        "foco":             random.choices(VERTICAIS, k=n_fundo),
        "estagio_alvo":     random.choices(ESTAGIOS[:4], k=n_fundo),
        "n_portfolios":     rng.integers(5, 80, n_fundo),
    })
    fato_rodada = pd.DataFrame({
        "id_rodada":        new_ids(n),
        "id_data":          rand_dates(start, end, n),
        "id_startup":       random.choices(dim_startup["id_startup"].tolist(), k=n),
        "id_fundo_lider":   random.choices(dim_fundo["id_fundo"].tolist(), k=n),
        "estagio":          random.choices(ESTAGIOS, weights=[20,25,20,15,10,7,3], k=n),
        "valor_captado":    rng.uniform(100_000, 200_000_000, n).round(2),
        "valuation_post":   rng.uniform(500_000, 2_000_000_000, n).round(2),
        "n_investidores":   rng.integers(1, 20, n),
        "equity_cedido_pct":rng.uniform(5, 30, n).round(1),
        "convertida":       random.choices([True,False], weights=[80,20], k=n),
    })
    fato_metrica = pd.DataFrame({
        "id_metrica":       new_ids(int(n*0.8)),
        "id_data":          rand_dates(start, end, int(n*0.8)),
        "id_startup":       random.choices(dim_startup["id_startup"].tolist(), k=int(n*0.8)),
        "mrr":              rng.uniform(0, 2_000_000, int(n*0.8)).round(2),
        "churn_pct":        rng.uniform(0, 15, int(n*0.8)).round(2),
        "cac":              rng.uniform(50, 10_000, int(n*0.8)).round(2),
        "ltv":              rng.uniform(500, 100_000, int(n*0.8)).round(2),
        "nps":              rng.uniform(-100, 100, int(n*0.8)).round(1),
        "mau":              rng.integers(0, 5_000_000, int(n*0.8)),
        "runway_meses":     rng.integers(0, 36, int(n*0.8)),
        "burn_rate":        rng.uniform(10_000, 2_000_000, int(n*0.8)).round(2),
    })
    return {"DimStartup": dim_startup, "DimFundo": dim_fundo,
            "FatoRodada": fato_rodada, "FatoMetrica": fato_metrica,
            "dCalendario": dcalendario(start, end)}
