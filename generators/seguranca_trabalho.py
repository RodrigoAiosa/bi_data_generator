"""generators/seguranca_trabalho.py — Setor Segurança do Trabalho & SESMT."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

TIPOS_EXAME = ["Admissional", "Periódico", "Demissional", "Mudança de Função"]
RESULTADOS_EXAME = ["Apto", "Apto com Restrições", "Inapto"]
NORMAS = ["NR-6", "NR-10", "NR-12", "NR-33", "NR-35"]


def gerar_seguranca_trabalho(n, start, end):
    n = max(int(n), 1)

    n_empresa_cliente = min(max(n // 100, 8), 800)
    dim_empresa_cliente = pd.DataFrame({
        "id_empresa_cliente": new_ids(n_empresa_cliente),
        "nome":              fake_pool(fake, "company", n_empresa_cliente),
        "setor":             random.choices(["Indústria", "Construção", "Serviços", "Logística"], k=n_empresa_cliente),
    })

    n_funcionario = min(max(n // 4, 300), 20000)
    dim_funcionario = pd.DataFrame({
        "id_funcionario":    new_ids(n_funcionario),
        "id_empresa_cliente": random.choices(dim_empresa_cliente["id_empresa_cliente"].tolist(), k=n_funcionario),
        "cargo":             fake_pool(fake, "job", n_funcionario),
    })

    fato_exame = pd.DataFrame({
        "id_exame":          new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_funcionario":    random.choices(dim_funcionario["id_funcionario"].tolist(), k=n),
        "tipo_exame":        random.choices(TIPOS_EXAME, weights=[35, 45, 15, 5], k=n),
        "resultado":         random.choices(RESULTADOS_EXAME, weights=[85, 12, 3], k=n),
    })

    n_treino = int(n * 0.5)
    fato_treinamento = pd.DataFrame({
        "id_treinamento":    new_ids(n_treino),
        "id_data":           rand_dates(start, end, n_treino),
        "id_empresa_cliente": random.choices(dim_empresa_cliente["id_empresa_cliente"].tolist(), k=n_treino),
        "norma":             random.choices(NORMAS, k=n_treino),
        "participantes":     rng.integers(3, 80, n_treino),
        "carga_horaria":     random.choices([4, 8, 16, 40], k=n_treino),
    })

    return {
        "DimEmpresaCliente": dim_empresa_cliente,
        "DimFuncionario": dim_funcionario,
        "FatoExame": fato_exame,
        "FatoTreinamento": fato_treinamento,
        "dCalendario": dcalendario(start, end),
    }
