"""generators/locadora.py — Setor Locação de Veículos (Rent-a-Car)."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS   = ["Econômico", "Compacto", "Intermediário", "SUV", "Executivo", "Utilitário", "Elétrico"]
MODELOS      = ["HB20", "Onix", "Kwid", "Polo", "T-Cross", "Compass", "Corolla", "Civic", "Kicks", "Tracker"]
STATUS_VEIC  = ["Disponível", "Locado", "Manutenção", "Baixado"]
FILIAIS      = ["Aeroporto", "Centro", "Shopping", "Rodoviária", "Zona Sul", "Zona Norte"]
TIPOS_INFRACAO = ["Excesso de Velocidade", "Estacionamento Irregular", "Avanço de Sinal",
                   "Uso de Celular", "Faixa Exclusiva", "Documentação"]
STATUS_LOCACAO = ["Confirmada", "Em Andamento", "Finalizada", "Cancelada"]


def gerar_locadora(n, start, end):
    n = max(int(n), 1)

    n_veiculo = min(max(n // 20, 40), 3000)
    dim_veiculo = pd.DataFrame({
        "id_veiculo":        new_ids(n_veiculo),
        "modelo":            random.choices(MODELOS, k=n_veiculo),
        "categoria":         random.choices(CATEGORIAS, weights=[25, 20, 20, 15, 10, 7, 3], k=n_veiculo),
        "ano_fabricacao":    rng.integers(2019, 2027, n_veiculo),
        "placa":             [f"{fake.lexify('???').upper()}{rng.integers(1000,9999)}" for _ in range(n_veiculo)],
        "km_rodado":         rng.integers(0, 150000, n_veiculo),
        "status":            random.choices(STATUS_VEIC, weights=[45, 40, 12, 3], k=n_veiculo),
    })

    n_cliente = min(max(n // 6, 100), 12000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.name() for _ in range(n_cliente)],
        "tipo_cliente":      random.choices(["Pessoa Física", "Pessoa Jurídica"], weights=[75, 25], k=n_cliente),
        "uf":                [fake.state_abbr() for _ in range(n_cliente)],
        "cidade":            [fake.city() for _ in range(n_cliente)],
        "score_credito":     rng.integers(300, 1000, n_cliente),
        "cliente_frequente":  random.choices([True, False], weights=[30, 70], k=n_cliente),
    })

    dias_locados = rng.integers(1, 30, n)
    valor_diaria = rng.uniform(80, 900, n).round(2)
    protecao = random.choices([True, False], weights=[55, 45], k=n)
    fato_locacao = pd.DataFrame({
        "id_locacao":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_veiculo":        random.choices(dim_veiculo["id_veiculo"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "filial_retirada":   random.choices(FILIAIS, k=n),
        "filial_devolucao":  random.choices(FILIAIS, k=n),
        "dias_locados":      dias_locados,
        "valor_diaria":      valor_diaria,
        "valor_total":       (dias_locados * valor_diaria).round(2),
        "protecao_contratada": protecao,
        "km_percorrido":     rng.integers(20, 3000, n),
        "status":            random.choices(STATUS_LOCACAO, weights=[15, 20, 60, 5], k=n),
    })

    n_multa = int(n * 0.08)
    fato_multa = pd.DataFrame({
        "id_multa":          new_ids(n_multa),
        "id_data":           rand_dates(start, end, n_multa),
        "id_veiculo":        random.choices(dim_veiculo["id_veiculo"].tolist(), k=n_multa),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n_multa),
        "tipo_infracao":     random.choices(TIPOS_INFRACAO, k=n_multa),
        "valor":             rng.uniform(88, 2000, n_multa).round(2),
        "pago":              random.choices([True, False], weights=[70, 30], k=n_multa),
        "pontos_cnh":        random.choices([3, 4, 5, 7], k=n_multa),
    })

    return {
        "DimVeiculo": dim_veiculo,
        "DimCliente": dim_cliente,
        "FatoLocacao": fato_locacao,
        "FatoMulta": fato_multa,
        "dCalendario": dcalendario(start, end),
    }
