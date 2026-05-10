"""generators/saas_b2b.py — Setor SaaS / Software B2B."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

SEGMENTOS_CLIENTE = [
    "Varejo", "Saúde", "Financeiro", "Logística", "Indústria",
    "Educação", "Agronegócio", "Construção", "Serviços", "Governo",
]

FEATURES = [
    "Dashboard Analytics", "Relatórios Automatizados", "API Pública", "SSO / SAML",
    "Integração ERP", "Módulo RH", "Módulo Financeiro", "App Mobile",
    "Assinatura Eletrônica", "IA Preditiva", "Chatbot Interno", "Multi-tenancy",
    "Backup Automático", "SLA 99.9%", "Suporte 24/7", "White-label",
    "Importação CSV/Excel", "Webhooks", "Auditoria de Logs", "Marketplace de Apps",
]

PLANOS = ["Starter", "Growth", "Business", "Enterprise", "Custom"]

CANAIS_AQUISICAO = ["Inbound", "Outbound SDR", "Parceiro Revendedor", "Indicação", "Evento", "Produto-Led Growth"]

MOTIVOS_CHURN = ["Preço", "Concorrente", "Falta de Feature", "Baixo Uso", "Falência", "N/A"]


def gerar_saas_b2b(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_clientes = min(n // 3 + 100, 1000)
    n_planos   = len(PLANOS)
    n_features = len(FEATURES)

    dim_plano = pd.DataFrame({
        "id_plano":      new_ids(n_planos),
        "nome":          PLANOS,
        "preco_mes":     [99, 499, 1499, 4999, 0],
        "limite_users":  [5, 25, 100, 1000, 999999],
        "limite_storage_gb": [10, 100, 500, 5000, 999999],
        "suporte":       ["Email", "Email+Chat", "Email+Chat+Tel", "Dedicado", "Dedicado"],
        "sla_pct":       [99.0, 99.5, 99.9, 99.95, 99.99],
    })

    dim_feature = pd.DataFrame({
        "id_feature":  new_ids(n_features),
        "nome":        FEATURES,
        "categoria":   random.choices(["Analytics", "Integrações", "Segurança", "Produto", "Suporte"], k=n_features),
        "plano_min":   random.choices(PLANOS, k=n_features),
        "custo_dev":   rng.uniform(5000, 500000, n_features).round(2),
    })

    dim_cliente = pd.DataFrame({
        "id_cliente":      new_ids(n_clientes),
        "nome":            [fake.company() for _ in range(n_clientes)],
        "cnpj":            [fake.cnpj() for _ in range(n_clientes)],
        "segmento":        random.choices(SEGMENTOS_CLIENTE, k=n_clientes),
        "uf":              [fake.state_abbr() for _ in range(n_clientes)],
        "n_funcionarios":  rng.integers(1, 10000, n_clientes),
        "canal_aquisicao": random.choices(CANAIS_AQUISICAO, k=n_clientes),
        "id_plano_atual":  random.choices(PLANOS, k=n_clientes),
        "data_contrato":   rand_dates(date(2018, 1, 1), end, n_clientes),
    })

    mrr = rng.uniform(99, 50000, n).round(2)
    churned = random.choices([True, False], weights=[8, 92], k=n)

    fato = pd.DataFrame({
        "id_assinatura":       new_ids(n),
        "id_data":             rand_dates(start, end, n),
        "id_cliente":          random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "id_plano":            random.choices(dim_plano["id_plano"].tolist(), k=n),
        "mrr":                 mrr,
        "arr":                 (mrr * 12).round(2),
        "upsell_mrr":          rng.uniform(0, 5000, n).round(2),
        "downgrade_mrr":       rng.uniform(0, 2000, n).round(2),
        "n_usuarios_ativos":   rng.integers(1, 1000, n),
        "n_logins_mes":        rng.integers(0, 5000, n),
        "tickets_suporte":     rng.integers(0, 30, n),
        "tempo_resolucao_h":   rng.uniform(0.5, 72, n).round(1),
        "nps":                 rng.integers(-100, 100, n),
        "health_score":        rng.uniform(0, 100, n).round(1),
        "tempo_onboarding_d":  rng.uniform(1, 90, n).round(0),
        "churn":               churned,
        "motivo_churn":        [random.choice(MOTIVOS_CHURN[:-1]) if c else "N/A" for c in churned],
        "ltv":                 (mrr * rng.uniform(6, 60, n)).round(2),
        "cac":                 rng.uniform(200, 20000, n).round(2),
    })

    return {
        "DimPlano":      dim_plano,
        "DimFeature":    dim_feature,
        "DimCliente":    dim_cliente,
        "FatoAssinatura":fato,
        "dCalendario":   dcalendario(start, end),
    }
