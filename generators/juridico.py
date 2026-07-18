"""generators/juridico.py — Setor Jurídico / LegalTech."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

AREAS_DIREITO = [
    "Trabalhista", "Tributário", "Cível", "Criminal", "Empresarial",
    "Previdenciário", "Administrativo", "Ambiental", "Família e Sucessões",
    "Propriedade Intelectual", "Contratos", "Regulatório", "Digital",
    "Imobiliário", "Consumidor",
]

TRIBUNAIS = [
    "TJSP", "TJRJ", "TJMG", "TJRS", "TJPR", "TJSC", "TJBA",
    "STJ", "STF", "TST", "TRF1", "TRF2", "TRF3", "TRF4", "TRF5",
    "TRT2", "TRT15", "CARF", "CADE",
]

STATUS_PROCESSO = ["Em Andamento", "Sentenciado", "Acordo", "Arquivado", "Recurso", "Transitado em Julgado"]

TIPOS_CLIENTE = ["Pessoa Física", "Pequena Empresa", "Média Empresa", "Grande Empresa", "Governo"]


def gerar_juridico(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_advogados = min(n // 10 + 20, 200)
    n_clientes  = min(n // 3 + 50, 600)
    n_tribunais = len(TRIBUNAIS)

    dim_advogado = pd.DataFrame({
        "id_advogado":   new_ids(n_advogados),
        "nome":          [fake.name() for _ in range(n_advogados)],
        "oab":           [f"{fake.state_abbr()}{fake.random_int(10000, 999999)}" for _ in range(n_advogados)],
        "especialidade": random.choices(AREAS_DIREITO, k=n_advogados),
        "senioridade":   random.choices(["Júnior", "Pleno", "Sênior", "Sócio"], weights=[25, 30, 30, 15], k=n_advogados),
        "valor_hora":    rng.uniform(80, 2500, n_advogados).round(2),
        "taxa_exito_pct":rng.uniform(30, 95, n_advogados).round(1),
    })

    dim_cliente = pd.DataFrame({
        "id_cliente":    new_ids(n_clientes),
        "nome":          [fake.company() if random.random() > 0.4 else fake.name() for _ in range(n_clientes)],
        "tipo":          random.choices(TIPOS_CLIENTE, k=n_clientes),
        "cpf_cnpj":      [fake.cnpj() if random.random() > 0.4 else fake.cpf() for _ in range(n_clientes)],
        "uf":            [fake.state_abbr() for _ in range(n_clientes)],
        "segmento":      random.choices(["Varejo", "Indústria", "Serviços", "Agro", "Saúde", "Financeiro", "Outro"], k=n_clientes),
        "canal_entrada": random.choices(["Indicação", "Marketing Digital", "Parceria", "Prospecção Ativa"], k=n_clientes),
    })

    dim_tribunal = pd.DataFrame({
        "id_tribunal": new_ids(n_tribunais),
        "sigla":       TRIBUNAIS,
        "tipo":        random.choices(["Estadual", "Federal", "Superior", "Trabalhista", "Administrativo"], k=n_tribunais),
        "uf":          [fake.state_abbr() for _ in range(n_tribunais)],
        "instancia":   random.choices(["1ª Instância", "2ª Instância", "Superior"], k=n_tribunais),
    })

    horas_trab = rng.uniform(1, 500, n).round(1)

    fato = pd.DataFrame({
        "id_processo":         new_ids(n),
        "id_data":             rand_dates(start, end, n),
        "id_advogado":         random.choices(dim_advogado["id_advogado"].tolist(), k=n),
        "id_cliente":          random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "id_tribunal":         random.choices(dim_tribunal["id_tribunal"].tolist(), k=n),
        "numero_processo":     [fake.bothify("####-##.####.#.##.####") for _ in range(n)],
        "area_direito":        random.choices(AREAS_DIREITO, k=n),
        "valor_causa":         rng.uniform(1000, 50000000, n).round(2),
        "horas_trabalhadas":   horas_trab,
        "honorarios":          (horas_trab * rng.uniform(80, 2500, n)).round(2),
        "honorarios_exito_pct":rng.uniform(0, 30, n).round(2),
        "duracao_dias":        rng.integers(1, 3650, n),
        "n_audiencias":        rng.integers(0, 20, n),
        "n_peticoes":          rng.integers(1, 50, n),
        "resultado_favoravel": random.choices([True, False], weights=[55, 45], k=n),
        "status":              random.choices(STATUS_PROCESSO, weights=[35, 20, 15, 10, 15, 5], k=n),
    })

    return {
        "DimAdvogado":  dim_advogado,
        "DimCliente":   dim_cliente,
        "DimTribunal":  dim_tribunal,
        "FatoProcesso": fato,
        "dCalendario":  dcalendario(start, end),
    }
