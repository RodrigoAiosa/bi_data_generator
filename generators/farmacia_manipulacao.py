"""generators/farmacia_manipulacao.py — Setor Farmácia de Manipulação."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

FORMAS_FARMACEUTICAS = ["Cápsula", "Pomada", "Xarope", "Creme", "Gel", "Sachê", "Solução Tópica"]
PRINCIPIOS_ATIVOS = ["Melatonina", "Minoxidil", "Vitamina D3", "Colágeno", "Ácido Hialurônico",
                      "Progesterona", "Complexo B", "Cafeína"]
STATUS_PEDIDO = ["Entregue", "Em Manipulação", "Aguardando Retirada", "Cancelado"]
ESPECIALIDADES = ["Manipulação Estética", "Nutracêuticos", "Veterinária", "Homeopatia"]


def gerar_farmacia_manipulacao(n, start, end):
    n = max(int(n), 1)

    n_farmaceutico = min(max(n // 100, 5), 60)
    dim_farmaceutico = pd.DataFrame({
        "id_farmaceutico":   new_ids(n_farmaceutico),
        "nome":              [fake.name() for _ in range(n_farmaceutico)],
        "especialidade":     random.choices(ESPECIALIDADES, k=n_farmaceutico),
    })

    n_cliente = min(max(n // 6, 80), 6000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.name() for _ in range(n_cliente)],
        "idade":             rng.integers(1, 95, n_cliente),
    })

    fato_formula = pd.DataFrame({
        "id_formula":         new_ids(n),
        "id_data":            rand_dates(start, end, n),
        "id_cliente":         random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "id_farmaceutico":    random.choices(dim_farmaceutico["id_farmaceutico"].tolist(), k=n),
        "forma_farmaceutica": random.choices(FORMAS_FARMACEUTICAS, k=n),
        "principio_ativo":    random.choices(PRINCIPIOS_ATIVOS, k=n),
        "valor":              rng.uniform(25, 480, n).round(2),
        "status_pedido":      random.choices(STATUS_PEDIDO, weights=[70, 15, 10, 5], k=n),
    })

    n_insumo = int(n * 1.6)
    fato_insumo = pd.DataFrame({
        "id_insumo_uso":      new_ids(n_insumo),
        "id_data":            rand_dates(start, end, n_insumo),
        "principio_ativo":    random.choices(PRINCIPIOS_ATIVOS, k=n_insumo),
        "quantidade_usada_g": rng.uniform(0.5, 500, n_insumo).round(2),
        "custo":              rng.uniform(2, 300, n_insumo).round(2),
    })

    return {
        "DimFarmaceutico": dim_farmaceutico,
        "DimCliente": dim_cliente,
        "FatoFormula": fato_formula,
        "FatoInsumo": fato_insumo,
        "dCalendario": dcalendario(start, end),
    }
