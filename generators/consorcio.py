"""generators/consorcio.py — Setor Consórcios."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

BENS = ["Veículo", "Imóvel", "Serviço", "Moto", "Caminhão"]
STATUS_PAGAMENTO = ["Pago", "Pendente", "Atrasado", "Quitado Antecipado"]
TIPOS_CONTEMPLACAO = ["Sorteio", "Lance Livre", "Lance Fixo", "Lance Embutido"]
TIPOS_PESSOA = ["Pessoa Física", "Pessoa Jurídica"]


def gerar_consorcio(n, start, end):
    n = max(int(n), 1)

    n_grupo = min(max(n // 50, 15), 800)
    dim_grupo = pd.DataFrame({
        "id_grupo":          new_ids(n_grupo),
        "bem":               random.choices(BENS, weights=[40, 30, 15, 10, 5], k=n_grupo),
        "prazo_meses":       random.choices([60, 80, 100, 120, 180], k=n_grupo),
        "valor_credito":     rng.uniform(15000, 800000, n_grupo).round(2),
        "taxa_administracao_pct": rng.uniform(12, 22, n_grupo).round(2),
    })

    n_cotista = min(max(n // 5, 200), 15000)
    dim_cotista = pd.DataFrame({
        "id_cotista":        new_ids(n_cotista),
        "nome":              [fake.name() if random.random() < 0.75 else fake.company() for _ in range(n_cotista)],
        "uf":                [fake.state_abbr() for _ in range(n_cotista)],
        "tipo_pessoa":       random.choices(TIPOS_PESSOA, weights=[75, 25], k=n_cotista),
    })

    grupo_idx = random.choices(range(n_grupo), k=n)
    valor_credito = dim_grupo["valor_credito"].to_numpy()[grupo_idx]
    prazo = dim_grupo["prazo_meses"].to_numpy()[grupo_idx]
    status_pagamento = random.choices(STATUS_PAGAMENTO, weights=[70, 12, 10, 8], k=n)
    fato_parcela = pd.DataFrame({
        "id_parcela":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_grupo":          dim_grupo["id_grupo"].to_numpy()[grupo_idx],
        "id_cotista":        random.choices(dim_cotista["id_cotista"].tolist(), k=n),
        "valor_parcela":     (valor_credito / prazo * rng.uniform(1.05, 1.25, n)).round(2),
        "status_pagamento":  status_pagamento,
        "inadimplente":      [s == "Atrasado" for s in status_pagamento],
    })

    n_contemplacao = int(n_grupo * 3)
    tipo_contemplacao = random.choices(TIPOS_CONTEMPLACAO, weights=[35, 30, 20, 15], k=n_contemplacao)
    fato_contemplacao = pd.DataFrame({
        "id_contemplacao":   new_ids(n_contemplacao),
        "id_data":           rand_dates(start, end, n_contemplacao),
        "id_grupo":          random.choices(dim_grupo["id_grupo"].tolist(), k=n_contemplacao),
        "id_cotista":        random.choices(dim_cotista["id_cotista"].tolist(), k=n_contemplacao),
        "tipo":              tipo_contemplacao,
        "valor_lance":       [round(rng.uniform(0, 40000), 2) if t != "Sorteio" else 0.0 for t in tipo_contemplacao],
        "mes_contemplado":   rng.integers(1, 180, n_contemplacao),
    })

    return {
        "DimGrupo": dim_grupo,
        "DimCotista": dim_cotista,
        "FatoParcela": fato_parcela,
        "FatoContemplacao": fato_contemplacao,
        "dCalendario": dcalendario(start, end),
    }
