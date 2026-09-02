"""generators/limpeza.py — Setor Serviços de Limpeza."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

TIPOS_SERVICO      = ["Limpeza Diária", "Limpeza Pesada", "Pós-Obra", "Vidros e Fachadas", "Jardinagem"]
TIPOS_CONTRATO     = ["Mensal Fixo", "Avulso", "Por Metro Quadrado"]
CATEGORIAS_INSUMO  = ["Produtos de Limpeza", "EPI", "Equipamentos", "Material Descartável"]


def gerar_limpeza(n, start, end):
    n = max(int(n), 1)

    n_funcionario = min(max(n // 15, 20), 3000)
    dim_funcionario = pd.DataFrame({
        "id_funcionario":    new_ids(n_funcionario),
        "nome":              fake_pool(fake, "name", n_funcionario),
        "cargo":             random.choices(["Auxiliar de Limpeza", "Supervisor", "Encarregado"], weights=[80, 15, 5], k=n_funcionario),
        "ativo":             random.choices([True, False], weights=[90, 10], k=n_funcionario),
    })

    n_contrato = min(max(n // 20, 20), 2000)
    dim_contrato = pd.DataFrame({
        "id_contrato":       new_ids(n_contrato),
        "cliente":           fake_pool(fake, "company", n_contrato),
        "tipo_contrato":     random.choices(TIPOS_CONTRATO, weights=[65, 20, 15], k=n_contrato),
        "valor_mensal":      rng.uniform(1500, 60000, n_contrato).round(2),
    })

    tipo_servico = random.choices(TIPOS_SERVICO, weights=[50, 15, 10, 15, 10], k=n)
    fato_atendimento = pd.DataFrame({
        "id_atendimento":    new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_contrato":       random.choices(dim_contrato["id_contrato"].tolist(), k=n),
        "id_funcionario":    random.choices(dim_funcionario["id_funcionario"].tolist(), k=n),
        "tipo_servico":      tipo_servico,
        "horas_trabalhadas": rng.uniform(1, 10, n).round(1),
    })

    n_insumo = int(n * 0.5)
    fato_insumo = pd.DataFrame({
        "id_insumo":         new_ids(n_insumo),
        "id_data":           rand_dates(start, end, n_insumo),
        "id_contrato":       random.choices(dim_contrato["id_contrato"].tolist(), k=n_insumo),
        "categoria_insumo":  random.choices(CATEGORIAS_INSUMO, weights=[45, 20, 20, 15], k=n_insumo),
        "custo":             rng.uniform(20, 3000, n_insumo).round(2),
    })

    return {
        "DimFuncionario": dim_funcionario,
        "DimContrato": dim_contrato,
        "FatoAtendimento": fato_atendimento,
        "FatoInsumo": fato_insumo,
        "dCalendario": dcalendario(start, end),
    }
