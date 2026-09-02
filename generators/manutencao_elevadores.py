"""generators/manutencao_elevadores.py — Setor Manutenção de Elevadores."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

TIPOS_CHAMADO = ["Manutenção Preventiva", "Manutenção Corretiva", "Emergência"]
MODELOS = ["Passageiro", "Carga", "Panorâmico", "Plataforma"]


def gerar_manutencao_elevadores(n, start, end):
    n = max(int(n), 1)

    n_tecnico = min(max(n // 60, 10), 1000)
    dim_tecnico = pd.DataFrame({
        "id_tecnico":        new_ids(n_tecnico),
        "nome":              fake_pool(fake, "name", n_tecnico),
        "regiao":            fake_pool(fake, "state_abbr", n_tecnico),
    })

    n_elevador = min(max(n // 5, 200), 20000)
    dim_elevador = pd.DataFrame({
        "id_elevador":       new_ids(n_elevador),
        "predio":            fake_pool(fake, "street_name", n_elevador),
        "cidade":            fake_pool(fake, "city", n_elevador),
        "uf":                fake_pool(fake, "state_abbr", n_elevador),
        "modelo":            random.choices(MODELOS, weights=[70, 15, 10, 5], k=n_elevador),
    })

    fato_chamado = pd.DataFrame({
        "id_chamado":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_tecnico":        random.choices(dim_tecnico["id_tecnico"].tolist(), k=n),
        "id_elevador":       random.choices(dim_elevador["id_elevador"].tolist(), k=n),
        "tipo_chamado":      random.choices(TIPOS_CHAMADO, weights=[55, 35, 10], k=n),
        "tempo_atendimento_min": rng.integers(15, 300, n),
        "valor":             rng.uniform(100, 8000, n).round(2),
    })

    return {
        "DimTecnico": dim_tecnico,
        "DimElevador": dim_elevador,
        "FatoChamado": fato_chamado,
        "dCalendario": dcalendario(start, end),
    }
