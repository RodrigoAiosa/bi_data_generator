"""generators/governo.py — Setor Público & Governo."""
import random
from datetime import date

import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

ESFERAS = ["Federal", "Estadual", "Municipal"]
PODERES = ["Executivo", "Legislativo", "Judiciário", "Ministério Público"]
AREAS_GOVERNO = [
    "Saúde", "Educação", "Segurança Pública", "Infraestrutura", "Assistência Social",
    "Meio Ambiente", "Agricultura", "Ciência & Tecnologia", "Cultura", "Esporte",
    "Fazenda", "Planejamento", "Trabalho", "Transporte", "Habitação",
]
MODALIDADES_LICITACAO = [
    "Pregão Eletrônico", "Pregão Presencial", "Concorrência", "Tomada de Preços",
    "Convite", "Concurso", "Leilão", "Dispensa", "Inexigibilidade",
]
SITUACOES_CONTRATO = ["Vigente", "Encerrado", "Suspenso", "Rescindido", "Em Renovação"]
TIPOS_DESPESA = [
    "Pessoal & Encargos", "Custeio", "Investimento", "Transferência",
    "Serviço da Dívida", "Reserva de Contingência",
]
FONTES_RECEITA = [
    "Impostos", "Taxas", "Contribuições", "Transferências Federais",
    "Transferências Estaduais", "Outras Receitas",
]
UFS = ["SP", "RJ", "MG", "RS", "BA", "PR", "PE", "CE", "SC", "GO",
       "DF", "ES", "AM", "PA", "MA", "MS", "MT", "PB", "RN", "AL"]


def gerar_governo(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    """
    Gera dados do setor Público & Governo em Star Schema.

    Tabelas: DimOrgao, DimFornecedor, DimPrograma,
             FatoDespesa, FatoReceita, FatoLicitacao, dCalendario
    """
    if n is None or n <= 0:
        n = 1_000
    n = int(n)

    # ── DimOrgão ─────────────────────────────────────────────────────────────
    n_org = min(max(n // 8, 80), 500)
    dim_orgao = pd.DataFrame({
        "id_orgao":         new_ids(n_org),
        "nome":             [f"{random.choice(['Secretaria', 'Ministério', 'Departamento', 'Autarquia'])} de {fake.word().capitalize()}" for _ in range(n_org)],
        "esfera":           random.choices(ESFERAS, weights=[20, 30, 50], k=n_org),
        "poder":            random.choices(PODERES, weights=[60, 15, 20, 5], k=n_org),
        "area":             random.choices(AREAS_GOVERNO, k=n_org),
        "uf":               random.choices(UFS, k=n_org),
        "cnpj":             [fake.cnpj() for _ in range(n_org)],
        "orcamento_anual":  rng.uniform(1_000_000, 10_000_000_000, n_org).round(2),
        "n_servidores":     rng.integers(10, 50_000, n_org),
    })

    # ── DimFornecedor ────────────────────────────────────────────────────────
    n_forn = min(max(n // 6, 100), 800)
    dim_fornecedor = pd.DataFrame({
        "id_fornecedor":    new_ids(n_forn),
        "nome":             [fake.company() for _ in range(n_forn)],
        "cnpj":             [fake.cnpj() for _ in range(n_forn)],
        "uf":               [fake.state_abbr() for _ in range(n_forn)],
        "porte":            random.choices(["MEI", "ME", "EPP", "Médio", "Grande"], weights=[10, 20, 25, 25, 20], k=n_forn),
        "situacao_cadastral": random.choices(["Regular", "Irregular", "Suspenso"], weights=[85, 10, 5], k=n_forn),
        "data_cadastro":    rand_dates(date(2000, 1, 1), end, n_forn),
    })

    # ── DimPrograma ──────────────────────────────────────────────────────────
    n_prog = 60
    dim_programa = pd.DataFrame({
        "id_programa":      new_ids(n_prog),
        "nome":             [f"Programa {fake.word().capitalize()} {rng.integers(1000,9999)}" for _ in range(n_prog)],
        "area":             random.choices(AREAS_GOVERNO, k=n_prog),
        "esfera":           random.choices(ESFERAS, k=n_prog),
        "meta_beneficiarios": rng.integers(100, 1_000_000, n_prog),
        "orcamento_total":  rng.uniform(100_000, 1_000_000_000, n_prog).round(2),
        "ano_inicio":       rng.integers(2015, 2024, n_prog),
        "ativo":            random.choices([True, False], weights=[75, 25], k=n_prog),
    })

    # ── FatoDespesa ──────────────────────────────────────────────────────────
    fato_despesa = pd.DataFrame({
        "id_despesa":           new_ids(n),
        "id_data":              rand_dates(start, end, n),
        "id_orgao":             random.choices(dim_orgao["id_orgao"].tolist(), k=n),
        "id_programa":          random.choices(dim_programa["id_programa"].tolist(), k=n),
        "id_fornecedor":        random.choices(dim_fornecedor["id_fornecedor"].tolist(), k=n),
        "tipo_despesa":         random.choices(TIPOS_DESPESA, k=n),
        "valor_orcado":         rng.uniform(1_000, 50_000_000, n).round(2),
        "valor_empenhado":      rng.uniform(800, 48_000_000, n).round(2),
        "valor_liquidado":      rng.uniform(500, 45_000_000, n).round(2),
        "valor_pago":           rng.uniform(400, 44_000_000, n).round(2),
        "execucao_pct":         rng.uniform(0, 100, n).round(1),
        "elemento_despesa":     [f"{rng.integers(10,99)}.{rng.integers(10,99)}.{rng.integers(10,99)}" for _ in range(n)],
        "funcao":               random.choices(AREAS_GOVERNO, k=n),
        "restos_a_pagar":       random.choices([True, False], weights=[20, 80], k=n),
    })

    # ── FatoReceita ──────────────────────────────────────────────────────────
    n_rec = int(n * 0.4)
    fato_receita = pd.DataFrame({
        "id_receita":           new_ids(n_rec),
        "id_data":              rand_dates(start, end, n_rec),
        "id_orgao":             random.choices(dim_orgao["id_orgao"].tolist(), k=n_rec),
        "fonte_receita":        random.choices(FONTES_RECEITA, k=n_rec),
        "valor_previsto":       rng.uniform(10_000, 100_000_000, n_rec).round(2),
        "valor_arrecadado":     rng.uniform(8_000, 105_000_000, n_rec).round(2),
        "pct_realizacao":       rng.uniform(50, 130, n_rec).round(1),
        "deducoes":             rng.uniform(0, 5_000_000, n_rec).round(2),
        "receita_liquida":      rng.uniform(5_000, 100_000_000, n_rec).round(2),
    })

    # ── FatoLicitacao ────────────────────────────────────────────────────────
    n_lic = int(n * 0.3)
    situacoes = random.choices(SITUACOES_CONTRATO, weights=[50, 25, 10, 10, 5], k=n_lic)
    fato_licitacao = pd.DataFrame({
        "id_licitacao":         new_ids(n_lic),
        "id_data_abertura":     rand_dates(start, end, n_lic),
        "id_orgao":             random.choices(dim_orgao["id_orgao"].tolist(), k=n_lic),
        "id_fornecedor_venc":   random.choices(dim_fornecedor["id_fornecedor"].tolist(), k=n_lic),
        "modalidade":           random.choices(MODALIDADES_LICITACAO, k=n_lic),
        "objeto":               [f"Aquisição/Contratação de {fake.word()}" for _ in range(n_lic)],
        "valor_estimado":       rng.uniform(10_000, 100_000_000, n_lic).round(2),
        "valor_contratado":     rng.uniform(8_000, 95_000_000, n_lic).round(2),
        "economia_pct":         rng.uniform(0, 40, n_lic).round(1),
        "n_propostas":          rng.integers(1, 30, n_lic),
        "prazo_contrato_meses": rng.integers(1, 60, n_lic),
        "situacao":             situacoes,
        "aditivo":              random.choices([True, False], weights=[25, 75], k=n_lic),
        "valor_aditivo":        [rng.uniform(0, 10_000_000) if a else 0 for a in [s == "Em Renovação" for s in situacoes]],
    })

    return {
        "DimOrgao":       dim_orgao,
        "DimFornecedor":  dim_fornecedor,
        "DimPrograma":    dim_programa,
        "FatoDespesa":    fato_despesa,
        "FatoReceita":    fato_receita,
        "FatoLicitacao":  fato_licitacao,
        "dCalendario":    dcalendario(start, end),
    }
