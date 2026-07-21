"""generators/agencia_publicidade.py — Setor Agência de Publicidade."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

SEGMENTOS = ["Varejo", "Saúde", "Educação", "Tecnologia", "Alimentos", "Moda", "Financeiro", "Automotivo"]
PORTES = ["Pequena", "Média", "Grande", "Corporação"]
FUNCOES = ["Redator", "Diretor de Arte", "Mídia", "Social Media", "Atendimento", "Planejamento", "Produtor Audiovisual"]
SENIORIDADE = ["Júnior", "Pleno", "Sênior", "Head"]
TIPOS_PROJETO = ["Campanha Institucional", "Branding", "Social Media", "Mídia Paga", "Ativação de Marca", "Produção de Vídeo"]
STATUS_PROJETO = ["Em Briefing", "Em Produção", "Em Aprovação", "Entregue", "Cancelado"]
CANAIS_MIDIA = ["Meta Ads", "Google Ads", "TikTok Ads", "TV Aberta", "Rádio", "OOH (Mídia Exterior)", "LinkedIn Ads"]


def gerar_agencia_publicidade(n, start, end):
    n = max(int(n), 1)

    n_cliente = min(max(n // 40, 15), 800)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [f"{fake.company()}" for _ in range(n_cliente)],
        "segmento":          random.choices(SEGMENTOS, k=n_cliente),
        "porte":             random.choices(PORTES, weights=[30, 35, 25, 10], k=n_cliente),
        "uf":                [fake.state_abbr() for _ in range(n_cliente)],
    })

    n_equipe = min(max(n // 80, 10), 150)
    dim_equipe = pd.DataFrame({
        "id_profissional":   new_ids(n_equipe),
        "nome":              [fake.name() for _ in range(n_equipe)],
        "funcao":            random.choices(FUNCOES, k=n_equipe),
        "senioridade":       random.choices(SENIORIDADE, weights=[30, 35, 25, 10], k=n_equipe),
    })

    horas_orcadas = rng.integers(20, 800, n)
    status_projeto = random.choices(STATUS_PROJETO, weights=[15, 30, 15, 35, 5], k=n)
    fato_projeto = pd.DataFrame({
        "id_projeto":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "id_profissional":   random.choices(dim_equipe["id_profissional"].tolist(), k=n),
        "tipo_projeto":       random.choices(TIPOS_PROJETO, k=n),
        "horas_orcadas":     horas_orcadas,
        "horas_realizadas":  (horas_orcadas * rng.uniform(0.7, 1.4, n)).round(0),
        "valor_contrato":    rng.uniform(3000, 250000, n).round(2),
        "status":            status_projeto,
        "estourou_horas":    None,
    })
    fato_projeto["estourou_horas"] = fato_projeto["horas_realizadas"] > fato_projeto["horas_orcadas"]

    n_campanha = int(n * 0.7)
    impressoes = rng.integers(1000, 5_000_000, n_campanha)
    fato_campanha = pd.DataFrame({
        "id_campanha":       new_ids(n_campanha),
        "id_data":           rand_dates(start, end, n_campanha),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n_campanha),
        "canal":             random.choices(CANAIS_MIDIA, k=n_campanha),
        "investimento":      rng.uniform(300, 80000, n_campanha).round(2),
        "impressoes":        impressoes,
        "cliques":           (impressoes * rng.uniform(0.005, 0.06, n_campanha)).round(0).astype(int),
        "conversoes":        rng.integers(0, 500, n_campanha),
    })

    return {
        "DimCliente": dim_cliente,
        "DimEquipe": dim_equipe,
        "FatoProjeto": fato_projeto,
        "FatoCampanhaMidia": fato_campanha,
        "dCalendario": dcalendario(start, end),
    }
