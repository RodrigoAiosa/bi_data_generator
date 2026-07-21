"""generators/coworking.py — Setor Coworking & Espaços Compartilhados."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_ESPACO = ["Estação Fixa", "Estação Flex", "Sala Privativa", "Sala de Reunião", "Auditório"]
TIPOS_PESSOA = ["Pessoa Física", "Pessoa Jurídica"]
SEGMENTOS_CLIENTE = ["Startup", "Freelancer", "Consultoria", "Tecnologia", "Advocacia", "Marketing", "Corporativo"]
PLANOS = ["Day Pass", "Mensal Flex", "Mensal Fixo", "Sala Privativa", "Corporativo Multi-Posto"]
STATUS_ASSINATURA = ["Ativo", "Cancelado", "Suspenso", "Inadimplente"]


def gerar_coworking(n, start, end):
    n = max(int(n), 1)

    n_espaco = min(max(n // 40, 10), 500)
    dim_espaco = pd.DataFrame({
        "id_espaco":         new_ids(n_espaco),
        "nome":              [f"{random.choice(TIPOS_ESPACO)} {rng.integers(1,300)}" for _ in range(n_espaco)],
        "tipo":              random.choices(TIPOS_ESPACO, weights=[35, 30, 20, 10, 5], k=n_espaco),
        "capacidade":        rng.integers(1, 40, n_espaco),
        "unidade":           random.choices([f"Unidade {c}" for c in ["Paulista","Faria Lima","Centro","Berrini","Pinheiros"]], k=n_espaco),
    })

    n_cliente = min(max(n // 5, 150), 10000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.name() if random.random() < 0.4 else fake.company() for _ in range(n_cliente)],
        "tipo_pessoa":       random.choices(TIPOS_PESSOA, weights=[40, 60], k=n_cliente),
        "segmento":          random.choices(SEGMENTOS_CLIENTE, k=n_cliente),
    })

    fato_reserva = pd.DataFrame({
        "id_reserva":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_espaco":         random.choices(dim_espaco["id_espaco"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "horas_reservadas":  random.choices([1, 2, 4, 8], weights=[20, 25, 25, 30], k=n),
        "valor":             rng.uniform(20, 1500, n).round(2),
        "no_show":           random.choices([True, False], weights=[8, 92], k=n),
    })

    n_assinatura = int(n_cliente * 0.6)
    status_assinatura = random.choices(STATUS_ASSINATURA, weights=[70, 12, 8, 10], k=n_assinatura)
    fato_assinatura = pd.DataFrame({
        "id_assinatura":     new_ids(n_assinatura),
        "id_data":           rand_dates(start, end, n_assinatura),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n_assinatura),
        "plano":             random.choices(PLANOS, weights=[15, 30, 25, 20, 10], k=n_assinatura),
        "valor_mensal":      rng.uniform(150, 8000, n_assinatura).round(2),
        "status":            status_assinatura,
        "meses_ativos":      rng.integers(1, 48, n_assinatura),
    })

    return {
        "DimEspaco": dim_espaco,
        "DimCliente": dim_cliente,
        "FatoReserva": fato_reserva,
        "FatoAssinatura": fato_assinatura,
        "dCalendario": dcalendario(start, end),
    }
