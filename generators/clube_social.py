"""generators/clube_social.py — Setor Clube Social & Recreativo."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

PLANOS = ["Individual", "Familiar", "Corporativo"]
INSTALACOES = ["Piscina", "Quadra de Tênis", "Salão de Festas", "Academia", "Quadra Poliesportiva"]


def gerar_clube_social(n, start, end):
    n = max(int(n), 1)

    n_clube = min(max(n // 300, 3), 40)
    dim_clube = pd.DataFrame({
        "id_clube":          new_ids(n_clube),
        "cidade":            fake_pool(fake, "city", n_clube),
        "uf":                fake_pool(fake, "state_abbr", n_clube),
        "num_quadras":       rng.integers(2, 20, n_clube),
    })

    n_socio = min(max(n // 4, 200), 20000)
    dim_socio = pd.DataFrame({
        "id_socio":          new_ids(n_socio),
        "id_clube":          random.choices(dim_clube["id_clube"].tolist(), k=n_socio),
        "nome":              fake_pool(fake, "name", n_socio),
        "categoria_plano":   random.choices(PLANOS, weights=[35, 50, 15], k=n_socio),
    })

    fato_uso_instalacao = pd.DataFrame({
        "id_uso":            new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_socio":          random.choices(dim_socio["id_socio"].tolist(), k=n),
        "instalacao":        random.choices(INSTALACOES, k=n),
        "duracao_min":       random.choices([30, 60, 90, 120], k=n),
    })

    n_mens = n_socio * 3
    fato_mensalidade = pd.DataFrame({
        "id_mensalidade":    new_ids(n_mens),
        "id_data":           rand_dates(start, end, n_mens),
        "id_socio":          random.choices(dim_socio["id_socio"].tolist(), k=n_mens),
        "valor":             rng.uniform(80, 1200, n_mens).round(2),
        "status_pagamento":  random.choices(["Pago", "Atrasado"], weights=[88, 12], k=n_mens),
    })

    return {
        "DimClube": dim_clube,
        "DimSocio": dim_socio,
        "FatoUsoInstalacao": fato_uso_instalacao,
        "FatoMensalidade": fato_mensalidade,
        "dCalendario": dcalendario(start, end),
    }
