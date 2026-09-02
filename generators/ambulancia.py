"""generators/ambulancia.py — Setor Ambulância & Remoção."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

TIPOS_AMBULANCIA = ["Básica", "UTI Móvel", "Resgate", "Neonatal"]
TIPOS_OCORRENCIA = ["Trauma", "Cardíaco", "Respiratório", "Obstétrico", "Remoção Programada", "Clínico Geral"]
GRAVIDADE        = ["Baixa", "Média", "Alta", "Crítica"]
DESFECHOS        = ["Atendido no Local", "Removido ao Hospital", "Óbito", "Recusa de Atendimento"]
TIPOS_MANUTENCAO = ["Preventiva", "Corretiva", "Revisão de Equipamentos", "Troca de Pneus"]


def gerar_ambulancia(n, start, end):
    n = max(int(n), 1)

    n_ambulancia = min(max(n // 80, 5), 120)
    dim_ambulancia = pd.DataFrame({
        "id_ambulancia":     new_ids(n_ambulancia),
        "placa":             fake_pool(fake, "license_plate", n_ambulancia),
        "tipo":              random.choices(TIPOS_AMBULANCIA, weights=[45, 30, 20, 5], k=n_ambulancia),
        "ano_fabricacao":    rng.integers(2010, 2025, n_ambulancia),
        "status":            random.choices(["Ativa", "Em Manutenção", "Baixada"], weights=[85, 12, 3], k=n_ambulancia),
    })

    n_paramedico = min(max(n // 50, 8), 300)
    dim_paramedico = pd.DataFrame({
        "id_paramedico":     new_ids(n_paramedico),
        "nome":              fake_pool(fake, "name", n_paramedico),
        "funcao":            random.choices(["Socorrista", "Enfermeiro", "Médico", "Condutor"], weights=[35, 30, 15, 20], k=n_paramedico),
        "anos_experiencia":  rng.integers(1, 30, n_paramedico),
    })

    gravidade = random.choices(GRAVIDADE, weights=[30, 35, 25, 10], k=n)
    fato_chamado = pd.DataFrame({
        "id_chamado":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_ambulancia":     random.choices(dim_ambulancia["id_ambulancia"].tolist(), k=n),
        "id_paramedico":     random.choices(dim_paramedico["id_paramedico"].tolist(), k=n),
        "tipo_ocorrencia":   random.choices(TIPOS_OCORRENCIA, k=n),
        "gravidade":         gravidade,
        "tempo_resposta_min": rng.integers(4, 45, n),
        "distancia_km":      rng.uniform(1, 60, n).round(1),
        "desfecho":          random.choices(DESFECHOS, weights=[35, 50, 5, 10], k=n),
        "valor_cobrado":     rng.uniform(150, 3500, n).round(2),
    })

    n_manut = int(n_ambulancia * 3.5)
    fato_manutencao = pd.DataFrame({
        "id_manutencao":     new_ids(n_manut),
        "id_data":           rand_dates(start, end, n_manut),
        "id_ambulancia":     random.choices(dim_ambulancia["id_ambulancia"].tolist(), k=n_manut),
        "tipo_manutencao":   random.choices(TIPOS_MANUTENCAO, weights=[45, 30, 15, 10], k=n_manut),
        "custo":             rng.uniform(80, 6000, n_manut).round(2),
        "tempo_parado_h":    rng.uniform(1, 72, n_manut).round(1),
    })

    return {
        "DimAmbulancia": dim_ambulancia,
        "DimParamedico": dim_paramedico,
        "FatoChamado": fato_chamado,
        "FatoManutencaoFrota": fato_manutencao,
        "dCalendario": dcalendario(start, end),
    }
