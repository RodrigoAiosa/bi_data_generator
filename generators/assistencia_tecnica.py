"""generators/assistencia_tecnica.py — Setor Assistência Técnica de Eletrônicos."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS_APARELHO = ["Smartphone", "Notebook", "Tablet", "TV", "Console de Videogame", "Smartwatch"]
MARCAS = ["Samsung", "Apple", "Motorola", "LG", "Xiaomi", "Dell", "Lenovo", "Sony"]
TIPOS_DEFEITO = ["Tela Quebrada", "Não Liga", "Bateria", "Problema de Software", "Placa-Mãe", "Conector de Carga", "Água/Líquido"]
STATUS_REPARO = ["Em Diagnóstico", "Aguardando Peça", "Em Reparo", "Concluído", "Sem Reparo (Irrecuperável)", "Entregue"]
GARANTIA = ["Dentro da Garantia", "Fora da Garantia"]


def gerar_assistencia_tecnica(n, start, end):
    n = max(int(n), 1)

    n_tecnico = min(max(n // 60, 10), 300)
    dim_tecnico = pd.DataFrame({
        "id_tecnico":        new_ids(n_tecnico),
        "nome":              [fake.name() for _ in range(n_tecnico)],
        "especialidade":     random.choices(CATEGORIAS_APARELHO, k=n_tecnico),
        "anos_experiencia":  rng.integers(1, 20, n_tecnico),
    })

    n_cliente = min(max(n // 3, 200), 15000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.name() for _ in range(n_cliente)],
        "uf":                [fake.state_abbr() for _ in range(n_cliente)],
    })

    status_reparo = random.choices(STATUS_REPARO, weights=[15, 15, 20, 30, 8, 12], k=n)
    garantia = random.choices(GARANTIA, weights=[30, 70], k=n)
    fato_ordem_servico = pd.DataFrame({
        "id_ordem_servico":  new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_tecnico":        random.choices(dim_tecnico["id_tecnico"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "categoria_aparelho": random.choices(CATEGORIAS_APARELHO, k=n),
        "marca":             random.choices(MARCAS, k=n),
        "tipo_defeito":      random.choices(TIPOS_DEFEITO, k=n),
        "garantia":          garantia,
        "valor_orcado":      [0.0 if g == "Dentro da Garantia" else round(rng.uniform(80, 3500), 2) for g in garantia],
        "status":            status_reparo,
        "tempo_reparo_dias": rng.integers(1, 30, n),
    })

    n_peca = int(n * 0.6)
    fato_peca_utilizada = pd.DataFrame({
        "id_peca_utilizada": new_ids(n_peca),
        "id_data":           rand_dates(start, end, n_peca),
        "id_tecnico":        random.choices(dim_tecnico["id_tecnico"].tolist(), k=n_peca),
        "categoria_aparelho": random.choices(CATEGORIAS_APARELHO, k=n_peca),
        "custo_peca":        rng.uniform(20, 1800, n_peca).round(2),
        "peca_original":     random.choices([True, False], weights=[55, 45], k=n_peca),
    })

    return {
        "DimTecnico": dim_tecnico,
        "DimCliente": dim_cliente,
        "FatoOrdemServico": fato_ordem_servico,
        "FatoPecaUtilizada": fato_peca_utilizada,
        "dCalendario": dcalendario(start, end),
    }
