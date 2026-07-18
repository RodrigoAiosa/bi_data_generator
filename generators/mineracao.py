"""generators/mineracao.py — Setor Mineração."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

MINERAIS = [
    "Minério de Ferro", "Ouro", "Bauxita", "Cobre", "Nióbio",
    "Manganês", "Caulim", "Fosfato", "Potássio", "Zinco",
    "Chumbo", "Estanho", "Cromo", "Níquel", "Lítio",
    "Diamante", "Esmeralda", "Calcário", "Grafita", "Silício",
]

UFS_MINERACAO = ["PA", "MG", "MT", "GO", "BA", "AM", "RO", "AP", "RS", "SP"]

METODOS_EXTRACAO = ["Lavra a Céu Aberto", "Lavra Subterrânea", "Garimpo", "Dragagem", "In Situ"]


def gerar_mineracao(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_minas      = min(n // 5 + 30, 300)
    n_minerais   = 20
    n_equip      = 50

    dim_mineral = pd.DataFrame({
        "id_mineral":   new_ids(n_minerais),
        "nome":         MINERAIS,
        "tipo":         random.choices(["Metálico", "Não-Metálico", "Energético", "Gema"], k=n_minerais),
        "unidade":      random.choices(["ton", "g", "kg", "m³"], k=n_minerais),
        "preco_unit":   rng.uniform(50, 250000, n_minerais).round(2),
        "pureza_min":   rng.uniform(0.30, 0.99, n_minerais).round(3),
    })

    dim_mina = pd.DataFrame({
        "id_mina":        new_ids(n_minas),
        "nome":           [f"Mina {fake.last_name()} {fake.random_int(1, 99)}" for _ in range(n_minas)],
        "empresa":        [fake.company() for _ in range(n_minas)],
        "cnpj":           [fake.cnpj() for _ in range(n_minas)],
        "uf":             random.choices(UFS_MINERACAO, k=n_minas),
        "municipio":      [fake.city() for _ in range(n_minas)],
        "profundidade_m": rng.uniform(0, 3000, n_minas).round(0),
        "area_ha":        rng.uniform(5, 20000, n_minas).round(1),
        "status_licenca": random.choices(["Ativa", "Suspensa", "Em Renovação", "Encerrada"], weights=[60, 15, 20, 5], k=n_minas),
        "metodo":         random.choices(METODOS_EXTRACAO, k=n_minas),
    })

    dim_equipamento = pd.DataFrame({
        "id_equipamento": new_ids(n_equip),
        "tipo":           random.choices(["Escavadeira", "Caminhão Fora-de-Estrada", "Britador", "Peneira Vibratória", "Draga", "Perfuratriz"], k=n_equip),
        "fabricante":     random.choices(["Caterpillar", "Komatsu", "Volvo", "Liebherr", "Sandvik"], k=n_equip),
        "ano_fabricacao": rng.integers(2000, 2024, n_equip),
        "custo_hora":     rng.uniform(100, 5000, n_equip).round(2),
        "capacidade_ton": rng.uniform(10, 400, n_equip).round(1),
    })

    volume_extraido = rng.uniform(10, 50000, n).round(2)

    fato = pd.DataFrame({
        "id_extracao":          new_ids(n),
        "id_data":              rand_dates(start, end, n),
        "id_mina":              random.choices(dim_mina["id_mina"].tolist(), k=n),
        "id_mineral":           random.choices(dim_mineral["id_mineral"].tolist(), k=n),
        "id_equipamento":       random.choices(dim_equipamento["id_equipamento"].tolist(), k=n),
        "volume_extraido_ton":  volume_extraido,
        "teor_mineral_pct":     rng.uniform(0.01, 0.95, n).round(4),
        "horas_operacao":       rng.uniform(1, 24, n).round(1),
        "custo_operacional":    rng.uniform(5000, 2000000, n).round(2),
        "receita":              (volume_extraido * rng.uniform(50, 250000, n)).round(2),
        "consumo_agua_m3":      rng.uniform(10, 50000, n).round(1),
        "emissao_co2_ton":      rng.uniform(0.5, 5000, n).round(2),
        "indice_seguranca":     rng.uniform(0, 10, n).round(2),
        "acidentes":            rng.integers(0, 5, n),
        "status":               random.choices(["Concluída", "Em Andamento", "Paralisada", "Planejada"], weights=[55, 30, 10, 5], k=n),
    })

    return {
        "DimMineral":     dim_mineral,
        "DimMina":        dim_mina,
        "DimEquipamento": dim_equipamento,
        "FatoExtracao":   fato,
        "dCalendario":    dcalendario(start, end),
    }
