"""generators/pet.py — Setor Pet Shop & Veterinária."""

import random
from datetime import date

import pandas as pd

from .helpers import dcalendario, get_faker, new_ids, rand_dates, rng

ESPECIES = ["Cão", "Gato", "Ave", "Roedor", "Réptil", "Peixe"]
RACAS = {
    "Cão":     ["SRD (Vira-lata)", "Labrador", "Poodle", "Bulldog Francês", "Golden Retriever", "Shih Tzu", "Pinscher"],
    "Gato":    ["SRD (Vira-lata)", "Siamês", "Persa", "Maine Coon", "Angorá"],
    "Ave":     ["Calopsita", "Periquito", "Papagaio"],
    "Roedor":  ["Hamster", "Coelho", "Porquinho-da-Índia"],
    "Réptil":  ["Jabuti", "Iguana", "Gecko"],
    "Peixe":   ["Betta", "Kinguio", "Tetra"],
}
PORTES = ["Pequeno", "Médio", "Grande"]

CATEGORIAS_SERVICO = ["Consulta", "Vacina", "Banho & Tosa", "Cirurgia", "Exame Laboratorial", "Internação", "Produto/Ração"]
NOMES_SERVICO = {
    "Consulta":            ["Consulta Clínica Geral", "Consulta Dermatológica", "Consulta Ortopédica"],
    "Vacina":              ["V10 Múltipla", "Antirrábica", "Giárdia", "Gripe Canina"],
    "Banho & Tosa":        ["Banho Simples", "Banho + Tosa Higiênica", "Tosa na Máquina", "Hidratação"],
    "Cirurgia":            ["Castração", "Cirurgia Ortopédica", "Remoção de Tumor"],
    "Exame Laboratorial":  ["Hemograma Completo", "Raio-X", "Ultrassom", "Exame de Urina"],
    "Internação":          ["Internação 24h", "Internação com Monitoramento"],
    "Produto/Ração":       ["Ração Premium 15kg", "Ração Filhote 3kg", "Areia Higiênica", "Brinquedo Interativo"],
}
FAIXA_PRECO = {
    "Consulta": (80, 250), "Vacina": (60, 180), "Banho & Tosa": (50, 150),
    "Cirurgia": (350, 2800), "Exame Laboratorial": (70, 600),
    "Internação": (200, 1500), "Produto/Ração": (30, 320),
}
FORMAS_PAGAMENTO = ["Cartão de Crédito", "Pix", "Dinheiro", "Cartão de Débito", "Plano de Saúde Pet"]
UFS = ["SP", "RJ", "MG", "RS", "PR", "BA", "SC", "PE", "CE", "GO"]


def gerar_pet(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    fake = get_faker()

    n_tutores = min(max(n // 3, 200), 4000)
    n_pets    = min(int(n_tutores * 1.3), 5000)

    # ── DimTutor ─────────────────────────────────────────────────────────────
    dim_tutor = pd.DataFrame({
        "id_tutor": new_ids(n_tutores),
        "nome":     [fake.name() for _ in range(n_tutores)],
        "cpf":      [fake.cpf() for _ in range(n_tutores)],
        "uf":       random.choices(UFS, k=n_tutores),
        "cidade":   [fake.city() for _ in range(n_tutores)],
    })

    # ── DimPet ───────────────────────────────────────────────────────────────
    especies_pet = random.choices(ESPECIES, weights=[45, 35, 8, 6, 3, 3], k=n_pets)
    dim_pet = pd.DataFrame({
        "id_pet":      new_ids(n_pets),
        "nome_pet":    [fake.first_name() for _ in range(n_pets)],
        "especie":     especies_pet,
        "raca":        [random.choice(RACAS[e]) for e in especies_pet],
        "porte":       random.choices(PORTES, weights=[40, 40, 20], k=n_pets),
        "idade_anos":  rng.integers(0, 18, n_pets),
        "id_tutor":    random.choices(dim_tutor["id_tutor"].tolist(), k=n_pets),
        "castrado":    random.choices([True, False], weights=[60, 40], k=n_pets),
    })

    # ── DimServico ───────────────────────────────────────────────────────────
    categorias_srv, nomes_srv, precos_srv = [], [], []
    for cat in CATEGORIAS_SERVICO:
        for nome in NOMES_SERVICO[cat]:
            categorias_srv.append(cat)
            nomes_srv.append(nome)
            lo, hi = FAIXA_PRECO[cat]
            precos_srv.append(round(rng.uniform(lo, hi), 2))

    dim_servico = pd.DataFrame({
        "id_servico":   new_ids(len(nomes_srv)),
        "nome_servico": nomes_srv,
        "categoria":    categorias_srv,
        "valor_base":   precos_srv,
    })

    # ── FatoAtendimento ──────────────────────────────────────────────────────
    ids_servico = random.choices(dim_servico["id_servico"].tolist(), k=n)
    servico_map = dim_servico.set_index("id_servico")[["valor_base", "categoria"]]
    categoria_evento = servico_map.loc[ids_servico, "categoria"].to_numpy()
    valor_base = servico_map.loc[ids_servico, "valor_base"].to_numpy()
    variacao = rng.uniform(0.85, 1.25, n)

    fato = pd.DataFrame({
        "id_atendimento":    new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_pet":            random.choices(dim_pet["id_pet"].tolist(), k=n),
        "id_servico":        ids_servico,
        "categoria_servico": categoria_evento,
        "veterinario":       [fake.name() for _ in range(n)],
        "valor_cobrado":     (valor_base * variacao).round(2),
        "forma_pagamento":   random.choices(FORMAS_PAGAMENTO, weights=[40, 30, 10, 15, 5], k=n),
        "retorno_necessario":random.choices([True, False], weights=[25, 75], k=n),
        "nota_avaliacao":    rng.integers(1, 6, n),
    })

    return {
        "DimTutor":         dim_tutor,
        "DimPet":           dim_pet,
        "DimServico":       dim_servico,
        "FatoAtendimento":  fato,
        "dCalendario":      dcalendario(start, end),
    }
