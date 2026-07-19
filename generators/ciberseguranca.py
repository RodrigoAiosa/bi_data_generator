"""generators/ciberseguranca.py — Setor Cibersegurança (SOC / Segurança da Informação)."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_ATIVO   = ["Servidor", "Endpoint", "Firewall", "Banco de Dados", "API Gateway",
                  "Cloud Storage", "Rede Interna", "Aplicação Web"]
CRITICIDADE   = ["Baixa", "Média", "Alta", "Crítica"]
AMBIENTES     = ["Produção", "Homologação", "Desenvolvimento", "DR"]
TIPOS_ATAQUE  = ["Phishing", "Ransomware", "DDoS", "SQL Injection", "Brute Force",
                  "Malware", "Insider Threat", "Zero-Day", "Man-in-the-Middle", "Credential Stuffing"]
SEVERIDADES   = ["Baixa", "Média", "Alta", "Crítica"]
STATUS_INCID  = ["Aberto", "Em Investigação", "Contido", "Resolvido", "Falso Positivo"]
CATEGORIAS_VULN = ["Configuração Incorreta", "Software Desatualizado", "Falha de Autenticação",
                    "Exposição de Dados", "Falha de Criptografia", "Permissão Excessiva"]
STATUS_CORRECAO = ["Pendente", "Em Correção", "Corrigida", "Aceita como Risco"]


def gerar_ciberseguranca(n, start, end):
    n = max(int(n), 1)

    n_ativo = min(max(n // 30, 30), 2000)
    dim_ativo = pd.DataFrame({
        "id_ativo":          new_ids(n_ativo),
        "nome":              [f"{random.choice(TIPOS_ATIVO)}-{fake.word().upper()}{rng.integers(100,999)}" for _ in range(n_ativo)],
        "tipo":              random.choices(TIPOS_ATIVO, k=n_ativo),
        "criticidade":       random.choices(CRITICIDADE, weights=[30, 35, 25, 10], k=n_ativo),
        "ambiente":          random.choices(AMBIENTES, weights=[50, 20, 20, 10], k=n_ativo),
        "sistema_operacional": random.choices(["Linux", "Windows Server", "Windows", "macOS", "N/A"], k=n_ativo),
        "exposto_internet":  random.choices([True, False], weights=[30, 70], k=n_ativo),
    })

    n_analista = min(max(n // 200, 5), 60)
    dim_analista = pd.DataFrame({
        "id_analista":       new_ids(n_analista),
        "nome":              [fake.name() for _ in range(n_analista)],
        "nivel":             random.choices(["N1", "N2", "N3", "Especialista"], weights=[35, 30, 20, 15], k=n_analista),
        "turno":             random.choices(["Manhã", "Tarde", "Noite", "Plantão 24h"], k=n_analista),
        "certificacoes":     random.choices(["CEH", "CISSP", "Security+", "OSCP", "Nenhuma"], k=n_analista),
    })

    severidade = random.choices(SEVERIDADES, weights=[25, 35, 28, 12], k=n)
    status_incidente = random.choices(STATUS_INCID, weights=[15, 20, 15, 45, 5], k=n)
    tempo_resposta = rng.integers(2, 480, n)
    fato_incidente = pd.DataFrame({
        "id_incidente":      new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_ativo":          random.choices(dim_ativo["id_ativo"].tolist(), k=n),
        "id_analista":       random.choices(dim_analista["id_analista"].tolist(), k=n),
        "tipo_ataque":       random.choices(TIPOS_ATAQUE, k=n),
        "severidade":        severidade,
        "status":            status_incidente,
        "tempo_resposta_min": tempo_resposta,
        "tempo_resolucao_min": tempo_resposta + rng.integers(10, 2000, n),
        "sla_cumprido":      random.choices([True, False], weights=[80, 20], k=n),
        "custo_estimado":    rng.uniform(200, 250000, n).round(2),
        "dados_vazados":     random.choices([True, False], weights=[8, 92], k=n),
    })

    n_vuln = int(n * 0.6)
    dias_aberto = rng.integers(0, 365, n_vuln)
    fato_vulnerabilidade = pd.DataFrame({
        "id_vulnerabilidade": new_ids(n_vuln),
        "id_data":           rand_dates(start, end, n_vuln),
        "id_ativo":          random.choices(dim_ativo["id_ativo"].tolist(), k=n_vuln),
        "cve":               [f"CVE-{rng.integers(2018,2027)}-{rng.integers(1000,99999)}" for _ in range(n_vuln)],
        "cvss_score":        rng.uniform(1.0, 10.0, n_vuln).round(1),
        "categoria":         random.choices(CATEGORIAS_VULN, k=n_vuln),
        "status_correcao":   random.choices(STATUS_CORRECAO, weights=[25, 25, 40, 10], k=n_vuln),
        "dias_em_aberto":    dias_aberto,
        "explorada":         random.choices([True, False], weights=[6, 94], k=n_vuln),
    })

    return {
        "DimAtivo": dim_ativo,
        "DimAnalista": dim_analista,
        "FatoIncidente": fato_incidente,
        "FatoVulnerabilidade": fato_vulnerabilidade,
        "dCalendario": dcalendario(start, end),
    }
