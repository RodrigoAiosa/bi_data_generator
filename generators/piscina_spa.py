"""generators/piscina_spa.py — Setor Piscina & Spa (manutenção e serviços)."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_CLIENTE = ["Residencial", "Condomínio", "Hotel/Pousada", "Academia/Clube", "Spa Comercial"]
TIPOS_SERVICO = ["Manutenção Mensal", "Limpeza de Fundo", "Tratamento Químico", "Troca de Areia do Filtro",
                  "Instalação de Aquecimento", "Reforma de Revestimento", "Vistoria Técnica"]
PRODUTOS_QUIMICOS = ["Cloro Granulado", "Cloro Líquido", "Algicida", "Clarificante", "Barrilha", "Redutor de pH"]
STATUS_SERVICO = ["Agendado", "Em Andamento", "Concluído", "Cancelado"]


def gerar_piscina_spa(n, start, end):
    n = max(int(n), 1)

    n_cliente = min(max(n // 8, 100), 6000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              [fake.name() if random.random() < 0.6 else fake.company() for _ in range(n_cliente)],
        "tipo_cliente":      random.choices(TIPOS_CLIENTE, weights=[50, 20, 12, 10, 8], k=n_cliente),
        "uf":                [fake.state_abbr() for _ in range(n_cliente)],
        "volume_piscina_litros": rng.integers(15000, 800000, n_cliente),
    })

    n_tecnico = min(max(n // 100, 8), 300)
    dim_tecnico = pd.DataFrame({
        "id_tecnico":        new_ids(n_tecnico),
        "nome":              [fake.name() for _ in range(n_tecnico)],
        "anos_experiencia":  rng.integers(1, 25, n_tecnico),
    })

    fato_servico = pd.DataFrame({
        "id_servico":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "id_tecnico":        random.choices(dim_tecnico["id_tecnico"].tolist(), k=n),
        "tipo_servico":      random.choices(TIPOS_SERVICO, weights=[45, 15, 20, 8, 5, 4, 3], k=n),
        "valor_servico":     rng.uniform(80, 6000, n).round(2),
        "status":            random.choices(STATUS_SERVICO, weights=[20, 10, 65, 5], k=n),
        "ph_medido":         rng.uniform(6.8, 8.2, n).round(2),
    })

    n_produto = int(n * 1.3)
    fato_consumo_quimico = pd.DataFrame({
        "id_consumo":        new_ids(n_produto),
        "id_data":           rand_dates(start, end, n_produto),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n_produto),
        "produto":           random.choices(PRODUTOS_QUIMICOS, k=n_produto),
        "quantidade_kg":     rng.uniform(0.5, 25, n_produto).round(2),
        "custo":             rng.uniform(15, 800, n_produto).round(2),
    })

    return {
        "DimCliente": dim_cliente,
        "DimTecnico": dim_tecnico,
        "FatoServico": fato_servico,
        "FatoConsumoQuimico": fato_consumo_quimico,
        "dCalendario": dcalendario(start, end),
    }
