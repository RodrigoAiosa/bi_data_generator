"""generators/turismo.py — Setor Turismo."""

import random
from datetime import date

import numpy as np
import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

PAISES = ["Brasil", "Argentina", "Chile", "Portugal", "Espanha", "França", "Itália", "EUA", "Japão", "México"]
DESTINOS = {
    "Brasil": ["Rio de Janeiro", "São Paulo", "Salvador", "Gramado", "Fortaleza"],
    "Argentina": ["Buenos Aires", "Bariloche", "Mendoza"],
    "Chile": ["Santiago", "Atacama", "Torres del Paine"],
    "EUA": ["Orlando", "Nova York", "Las Vegas", "Miami"],
    "França": ["Paris", "Nice", "Lyon"],
}

def gerar_turismo(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_viajantes = min(n, 5000)
    n_pacotes   = 50
    n_agencias  = 20
    
    dim_viajante = pd.DataFrame({
        "id_viajante": new_ids(n_viajantes),
        "nome":        [fake.name() for _ in range(n_viajantes)],
        "cpf":         [fake.cpf() for _ in range(n_viajantes)],
        "email":       [fake.email() for _ in range(n_viajantes)],
        "faixa_etaria": random.choices(["18-25", "26-35", "36-50", "51+"], k=n_viajantes),
        "nacionalidade": random.choices(["Brasileira", "Estrangeira"], weights=[0.8, 0.2], k=n_viajantes)
    })

    tipos_pacote = ["Econômico", "Standard", "Luxo", "All Inclusive"]
    dim_pacote = pd.DataFrame({
        "id_pacote": new_ids(n_pacotes),
        "nome":      [f"Pacote {fake.word().capitalize()} {i}" for i in range(1, n_pacotes + 1)],
        "tipo":      random.choices(tipos_pacote, k=n_pacotes),
        "duracao_dias": rng.integers(3, 15, n_pacotes),
        "preco_base": rng.uniform(1000, 15000, n_pacotes).round(2)
    })

    dim_agencia = pd.DataFrame({
        "id_agencia": new_ids(n_agencias),
        "nome":       [f"Agência {fake.company()}" for _ in range(n_agencias)],
        "cidade":     [fake.city() for _ in range(n_agencias)],
        "tipo":       random.choices(["Online", "Física", "Franquia"], k=n_agencias)
    })

    destinos_lista = []
    for pais, cidades in DESTINOS.items():
        for cidade in cidades:
            destinos_lista.append({"cidade": cidade, "pais": pais})
    
    dim_destino = pd.DataFrame(destinos_lista)
    dim_destino["id_destino"] = new_ids(len(dim_destino))

    datas = rand_dates(start, end, n)
    pacotes_ids = random.choices(dim_pacote["id_pacote"].tolist(), k=n)
    precos_base = [dim_pacote.loc[dim_pacote["id_pacote"] == p, "preco_base"].values[0] for p in pacotes_ids]
    
    fato = pd.DataFrame({
        "id_viagem":   new_ids(n),
        "id_data":     datas,
        "id_viajante": random.choices(dim_viajante["id_viajante"].tolist(), k=n),
        "id_pacote":   pacotes_ids,
        "id_agencia":  random.choices(dim_agencia["id_agencia"].tolist(), k=n),
        "id_destino":  random.choices(dim_destino["id_destino"].tolist(), k=n),
        "passageiros": rng.integers(1, 5, n),
        "valor_pago":  [round(p * rng.uniform(0.9, 1.2), 2) for p in precos_base],
        "status":      random.choices(["Confirmada", "Cancelada", "Pendente"], weights=[0.85, 0.05, 0.1], k=n),
        "meio_transporte": random.choices(["Avião", "Ônibus", "Navio"], k=n)
    })

    return {
        "DimViajante": dim_viajante,
        "DimPacote":   dim_pacote,
        "DimAgencia":  dim_agencia,
        "DimDestino":  dim_destino,
        "FatoViagens": fato,
        "dCalendario": dcalendario(start, end),
    }
