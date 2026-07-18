"""generators/industria.py — Setor Indústria."""

import random
from datetime import date

import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")


def gerar_industria(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_maquinas   = 30
    n_insumos    = 60
    n_produtos   = 40
    n_operadores = 50

    dim_maquina = pd.DataFrame({
        "id_maquina":   new_ids(n_maquinas),
        "nome":         [f"Máquina {fake.word().upper()}-{i}" for i in range(1, n_maquinas + 1)],
        "tipo":         random.choices(["Torno","Fresadora","Prensa","Injetora","CNC","Soldadora","Estampadora"], k=n_maquinas),
        "linha":        random.choices(["Linha A","Linha B","Linha C","Linha D"], k=n_maquinas),
        "capacidade_h": rng.integers(100, 2000, n_maquinas),
        "ano_fab":      rng.integers(2000, 2023, n_maquinas),
    })

    dim_insumo = pd.DataFrame({
        "id_insumo":  new_ids(n_insumos),
        "nome":       [f"Insumo {fake.word().capitalize()}" for _ in range(n_insumos)],
        "tipo":       random.choices(["Matéria-Prima","Embalagem","Componente","Químico","Combustível"], k=n_insumos),
        "unidade":    random.choices(["kg","ton","litro","unidade","metro"], k=n_insumos),
        "custo_unit": rng.uniform(1, 500, n_insumos).round(2),
    })

    dim_produto = pd.DataFrame({
        "id_produto":  new_ids(n_produtos),
        "nome":        [f"Produto {fake.word().upper()}-{i}" for i in range(1, n_produtos + 1)],
        "familia":     random.choices(["Família A","Família B","Família C"], k=n_produtos),
        "peso_kg":     rng.uniform(0.1, 100, n_produtos).round(2),
        "preco_venda": rng.uniform(50, 10000, n_produtos).round(2),
    })

    dim_operador = pd.DataFrame({
        "id_operador": new_ids(n_operadores),
        "nome":        [fake.name() for _ in range(n_operadores)],
        "turno":       random.choices(["Manhã","Tarde","Noite"], k=n_operadores),
        "nivel":       random.choices(["Operador I","Operador II","Técnico","Supervisor"], k=n_operadores),
    })

    qtd = rng.integers(1, 500, n)
    fato = pd.DataFrame({
        "id_ordem":        new_ids(n),
        "id_data":         rand_dates(start, end, n),
        "id_maquina":      random.choices(dim_maquina["id_maquina"].tolist(), k=n),
        "id_insumo":       random.choices(dim_insumo["id_insumo"].tolist(), k=n),
        "id_produto":      random.choices(dim_produto["id_produto"].tolist(), k=n),
        "id_operador":     random.choices(dim_operador["id_operador"].tolist(), k=n),
        "quantidade":      qtd,
        "tempo_ciclo_min": rng.uniform(1, 480, n).round(1),
        "refugo_pct":      rng.uniform(0, 0.15, n).round(4),
        "custo_producao":  rng.uniform(100, 50000, n).round(2),
        "oee":             rng.uniform(0.5, 0.98, n).round(3),
        "turno":           random.choices(["Manhã","Tarde","Noite"], k=n),
    })

    return {
        "DimMaquina":   dim_maquina,
        "DimInsumo":    dim_insumo,
        "DimProduto":   dim_produto,
        "DimOperador":  dim_operador,
        "FatoProducao": fato,
        "dCalendario":  dcalendario(start, end),
    }
