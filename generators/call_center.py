"""generators/call_center.py — Setor Call Center & BPO."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_ATENDIMENTO = ["Receptivo", "Ativo (Telemarketing)", "Chat", "E-mail", "Redes Sociais"]
MOTIVOS_CONTATO = ["Dúvida", "Reclamação", "Cancelamento", "Suporte Técnico", "Vendas", "Cobrança"]
STATUS_CHAMADO = ["Resolvido", "Escalado", "Pendente", "Reaberto"]
NIVEIS_ATENDENTE = ["Júnior", "Pleno", "Sênior", "Supervisor"]


def gerar_call_center(n, start, end):
    n = max(int(n), 1)

    n_atendente = min(max(n // 40, 20), 2000)
    dim_atendente = pd.DataFrame({
        "id_atendente":      new_ids(n_atendente),
        "nome":              [fake.name() for _ in range(n_atendente)],
        "nivel":             random.choices(NIVEIS_ATENDENTE, weights=[40, 35, 15, 10], k=n_atendente),
        "turno":             random.choices(["Manhã", "Tarde", "Noite"], k=n_atendente),
    })

    n_cliente = min(max(n // 4, 200), 20000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.name() for _ in range(n_cliente)],
        "uf":                [fake.state_abbr() for _ in range(n_cliente)],
        "segmento_contratante": random.choices(["Telecom", "Bancos", "Varejo", "Saúde", "Utilities"], k=n_cliente),
    })

    status_chamado = random.choices(STATUS_CHAMADO, weights=[65, 15, 12, 8], k=n)
    fato_atendimento = pd.DataFrame({
        "id_atendimento":    new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_atendente":      random.choices(dim_atendente["id_atendente"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "tipo_atendimento":  random.choices(TIPOS_ATENDIMENTO, weights=[35, 15, 25, 15, 10], k=n),
        "motivo_contato":    random.choices(MOTIVOS_CONTATO, k=n),
        "duracao_min":       rng.integers(1, 45, n),
        "tempo_espera_seg":  rng.integers(0, 900, n),
        "status":            status_chamado,
        "nota_satisfacao":   rng.integers(1, 6, n),
    })

    n_avaliacao = int(n * 0.4)
    fato_avaliacao_qualidade = pd.DataFrame({
        "id_avaliacao_qual": new_ids(n_avaliacao),
        "id_data":           rand_dates(start, end, n_avaliacao),
        "id_atendente":      random.choices(dim_atendente["id_atendente"].tolist(), k=n_avaliacao),
        "aderencia_script_pct": rng.uniform(50, 100, n_avaliacao).round(1),
        "nota_supervisor":   rng.uniform(1, 10, n_avaliacao).round(1),
    })

    return {
        "DimAtendente": dim_atendente,
        "DimCliente": dim_cliente,
        "FatoAtendimento": fato_atendimento,
        "FatoAvaliacaoQualidade": fato_avaliacao_qualidade,
        "dCalendario": dcalendario(start, end),
    }
