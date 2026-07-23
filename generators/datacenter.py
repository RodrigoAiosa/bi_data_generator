"""generators/datacenter.py — Setor Data Center & Cloud Hosting."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_INSTANCIA = ["VM Compartilhada", "VM Dedicada", "Bare Metal", "Kubernetes Cluster", "Serverless"]
REGIOES = ["São Paulo", "Rio de Janeiro", "Fortaleza", "Virginia (US)", "Frankfurt (EU)"]
TIPOS_RECURSO = ["Computação (vCPU/h)", "Armazenamento (GB/mês)", "Tráfego de Rede (GB)", "Backup", "IP Dedicado"]
STATUS_INCIDENTE = ["Resolvido", "Em Investigação", "Monitorando", "Fechado sem Impacto"]
SEVERIDADE = ["SEV1 - Crítico", "SEV2 - Alto", "SEV3 - Médio", "SEV4 - Baixo"]


def gerar_datacenter(n, start, end):
    n = max(int(n), 1)

    n_cliente = min(max(n // 10, 80), 5000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.company() for _ in range(n_cliente)],
        "plano":             random.choices(["Starter", "Business", "Enterprise", "Enterprise Plus"], weights=[35, 30, 25, 10], k=n_cliente),
        "uf":                [fake.state_abbr() for _ in range(n_cliente)],
    })

    n_instancia = min(max(n // 5, 150), 12000)
    dim_instancia = pd.DataFrame({
        "id_instancia":      new_ids(n_instancia),
        "tipo":              random.choices(TIPOS_INSTANCIA, weights=[35, 20, 10, 25, 10], k=n_instancia),
        "regiao":            random.choices(REGIOES, weights=[35, 20, 10, 20, 15], k=n_instancia),
        "vcpus":             random.choices([1, 2, 4, 8, 16, 32], weights=[25, 25, 20, 15, 10, 5], k=n_instancia),
        "memoria_gb":        random.choices([2, 4, 8, 16, 32, 64], weights=[25, 25, 20, 15, 10, 5], k=n_instancia),
    })

    fato_consumo = pd.DataFrame({
        "id_consumo":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "id_instancia":      random.choices(dim_instancia["id_instancia"].tolist(), k=n),
        "tipo_recurso":      random.choices(TIPOS_RECURSO, weights=[45, 25, 20, 6, 4], k=n),
        "quantidade_consumida": rng.uniform(1, 5000, n).round(2),
        "custo_usd":         rng.uniform(0.5, 3500, n).round(2),
        "uptime_pct":        rng.uniform(95, 100, n).round(3),
    })

    n_incidente = int(n * 0.05)
    fato_incidente = pd.DataFrame({
        "id_incidente":      new_ids(n_incidente),
        "id_data":           rand_dates(start, end, n_incidente),
        "id_instancia":      random.choices(dim_instancia["id_instancia"].tolist(), k=n_incidente),
        "severidade":        random.choices(SEVERIDADE, weights=[8, 22, 40, 30], k=n_incidente),
        "status":            random.choices(STATUS_INCIDENTE, weights=[55, 15, 10, 20], k=n_incidente),
        "tempo_indisponibilidade_min": rng.integers(0, 480, n_incidente),
        "clientes_afetados": rng.integers(0, 500, n_incidente),
    })

    return {
        "DimCliente": dim_cliente,
        "DimInstancia": dim_instancia,
        "FatoConsumo": fato_consumo,
        "FatoIncidente": fato_incidente,
        "dCalendario": dcalendario(start, end),
    }
