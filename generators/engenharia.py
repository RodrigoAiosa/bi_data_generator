"""generators/engenharia.py — Setor Engenharia & Projetos."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

ESPECIALIDADES = ["Civil", "Elétrica", "Mecânica", "Hidráulica", "Estrutural"]
TIPOS_PROJETO = ["Residencial", "Comercial", "Industrial", "Infraestrutura"]


def gerar_engenharia(n, start, end):
    n = max(int(n), 1)

    n_escritorio = min(max(n // 200, 3), 50)
    dim_escritorio = pd.DataFrame({
        "id_escritorio":     new_ids(n_escritorio),
        "cidade":            fake_pool(fake, "city", n_escritorio),
        "uf":                fake_pool(fake, "state_abbr", n_escritorio),
    })

    n_engenheiro = min(max(n // 20, 15), 1500)
    dim_engenheiro = pd.DataFrame({
        "id_engenheiro":     new_ids(n_engenheiro),
        "id_escritorio":     random.choices(dim_escritorio["id_escritorio"].tolist(), k=n_engenheiro),
        "nome":              fake_pool(fake, "name", n_engenheiro),
        "especialidade":     random.choices(ESPECIALIDADES, k=n_engenheiro),
    })

    fato_projeto = pd.DataFrame({
        "id_projeto":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_engenheiro":     random.choices(dim_engenheiro["id_engenheiro"].tolist(), k=n),
        "cliente":           fake_pool(fake, "company", n),
        "tipo_projeto":      random.choices(TIPOS_PROJETO, k=n),
        "valor_contrato":    rng.uniform(8000, 1500000, n).round(2),
        "prazo_dias":        rng.integers(15, 720, n),
    })

    return {
        "DimEscritorio": dim_escritorio,
        "DimEngenheiro": dim_engenheiro,
        "FatoProjeto": fato_projeto,
        "dCalendario": dcalendario(start, end),
    }
