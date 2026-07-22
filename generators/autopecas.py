"""generators/autopecas.py — Setor Autopeças & Oficina Mecânica."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS_PECA = ["Motor", "Suspensão", "Freios", "Elétrica", "Carroceria", "Transmissão", "Arrefecimento"]
MARCAS_PECA = ["Bosch", "Continental", "NGK", "Cofap", "Fras-le", "Original", "Nakata"]
TIPOS_VEICULO = ["Hatch", "Sedan", "SUV", "Picape", "Utilitário"]
CANAIS_VENDA = ["Balcão", "Online", "Oficina Própria"]
TIPOS_SERVICO = ["Revisão", "Troca de Óleo", "Alinhamento e Balanceamento", "Diagnóstico Eletrônico",
                  "Troca de Freios", "Suspensão", "Ar-Condicionado"]


def gerar_autopecas(n, start, end):
    n = max(int(n), 1)

    n_peca = min(max(n // 15, 40), 3000)
    dim_peca = pd.DataFrame({
        "id_peca":           new_ids(n_peca),
        "nome":              [f"{random.choice(CATEGORIAS_PECA)} {fake.word().capitalize()}" for _ in range(n_peca)],
        "categoria":         random.choices(CATEGORIAS_PECA, k=n_peca),
        "marca":             random.choices(MARCAS_PECA, k=n_peca),
        "preco":             rng.uniform(15, 3500, n_peca).round(2),
    })

    n_cliente = min(max(n // 4, 150), 15000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.name() for _ in range(n_cliente)],
        "tipo_veiculo":      random.choices(TIPOS_VEICULO, k=n_cliente),
        "uf":                [fake.state_abbr() for _ in range(n_cliente)],
    })

    qtd = rng.integers(1, 8, n)
    peca_idx = random.choices(range(n_peca), k=n)
    preco_unit = dim_peca["preco"].to_numpy()[peca_idx]
    fato_venda = pd.DataFrame({
        "id_venda_peca":     new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_peca":           dim_peca["id_peca"].to_numpy()[peca_idx],
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "quantidade":        qtd,
        "valor_total":       (qtd * preco_unit).round(2),
        "canal":             random.choices(CANAIS_VENDA, weights=[40, 30, 30], k=n),
    })

    n_servico = int(n * 0.7)
    fato_servico = pd.DataFrame({
        "id_servico":        new_ids(n_servico),
        "id_data":           rand_dates(start, end, n_servico),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n_servico),
        "tipo_servico":      random.choices(TIPOS_SERVICO, k=n_servico),
        "valor_mao_obra":    rng.uniform(50, 800, n_servico).round(2),
        "valor_pecas":       rng.uniform(0, 2500, n_servico).round(2),
        "tempo_horas":       rng.uniform(0.5, 8, n_servico).round(1),
    })

    return {
        "DimPeca": dim_peca,
        "DimCliente": dim_cliente,
        "FatoVenda": fato_venda,
        "FatoServico": fato_servico,
        "dCalendario": dcalendario(start, end),
    }
