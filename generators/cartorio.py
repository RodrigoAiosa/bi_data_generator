"""generators/cartorio.py — Setor Cartório & Serviços Notariais."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_ATO = ["Escritura Pública", "Procuração", "Reconhecimento de Firma", "Autenticação de Documento",
              "Registro de Imóvel", "Certidão de Nascimento", "Certidão de Casamento", "Certidão de Óbito",
              "Ata Notarial", "Testamento"]
CATEGORIAS_ATO = ["Notas", "Registro Civil", "Registro de Imóveis", "Protesto"]
TIPOS_PESSOA = ["Pessoa Física", "Pessoa Jurídica"]
FORMAS_PAGAMENTO = ["Dinheiro", "Cartão de Débito", "Cartão de Crédito", "Pix"]


def gerar_cartorio(n, start, end):
    n = max(int(n), 1)

    n_tabeliao = min(max(n // 200, 5), 80)
    dim_tabeliao = pd.DataFrame({
        "id_tabeliao":       new_ids(n_tabeliao),
        "nome":              [f"{random.choice(['Dr.','Dra.'])} {fake.name()}" for _ in range(n_tabeliao)],
        "cartorio":          random.choices([f"{i+1}º Ofício de Notas" for i in range(15)], k=n_tabeliao),
        "anos_atuacao":      rng.integers(1, 35, n_tabeliao),
    })

    n_cliente = min(max(n // 3, 200), 20000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.name() if random.random() < 0.8 else fake.company() for _ in range(n_cliente)],
        "tipo_pessoa":       random.choices(TIPOS_PESSOA, weights=[80, 20], k=n_cliente),
        "uf":                [fake.state_abbr() for _ in range(n_cliente)],
    })

    tipo_ato = random.choices(TIPOS_ATO, k=n)
    fato_ato = pd.DataFrame({
        "id_ato":            new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_tabeliao":       random.choices(dim_tabeliao["id_tabeliao"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "tipo_ato":          tipo_ato,
        "categoria":         [random.choice(CATEGORIAS_ATO) for _ in tipo_ato],
        "valor_emolumento":  rng.uniform(15, 4500, n).round(2),
        "forma_pagamento":   random.choices(FORMAS_PAGAMENTO, weights=[15, 25, 25, 35], k=n),
        "tempo_atendimento_min": rng.integers(5, 90, n),
    })

    n_protesto = int(n * 0.1)
    fato_protesto = pd.DataFrame({
        "id_protesto":       new_ids(n_protesto),
        "id_data":           rand_dates(start, end, n_protesto),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n_protesto),
        "valor_titulo":      rng.uniform(200, 80000, n_protesto).round(2),
        "quitado":           random.choices([True, False], weights=[55, 45], k=n_protesto),
        "dias_em_aberto":    rng.integers(1, 365, n_protesto),
    })

    return {
        "DimTabeliao": dim_tabeliao,
        "DimCliente": dim_cliente,
        "FatoAto": fato_ato,
        "FatoProtesto": fato_protesto,
        "dCalendario": dcalendario(start, end),
    }
