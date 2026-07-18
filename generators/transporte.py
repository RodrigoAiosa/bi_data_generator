"""generators/transporte.py — Setor Transporte (Transportadora / Frota)."""
import random
from datetime import date, timedelta

import numpy as np
import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

# ── Domínios ─────────────────────────────────────────────────────────────────

MARCAS_CAMINHAO = ["Volvo", "Scania", "Mercedes-Benz", "Iveco", "DAF", "MAN", "Ford"]
MODELOS = {
    "Volvo":        ["FH 540", "FH 460", "FM 370", "FMX 500"],
    "Scania":       ["R 450", "R 500", "S 500", "G 360"],
    "Mercedes-Benz":["Actros 2651", "Axor 2644", "Atego 2430"],
    "Iveco":        ["Hi-Way 570S", "Stralis 480"],
    "DAF":          ["XF 530", "CF 480"],
    "MAN":          ["TGX 29.540", "TGS 26.440"],
    "Ford":         ["Cargo 2429", "Cargo 1932"],
}
TIPOS_VEICULO = ["Cavalo Mecânico", "Truck", "Toco", "Van Carga", "Bitrem", "Rodotrem"]
STATUS_VIAGEM  = ["Em execução", "Em trânsito", "Aguardando carga/descarga", "Concluída", "Atrasada", "Cancelada"]
TIPOS_CARGA    = ["Granel Sólido", "Granel Líquido", "Carga Geral", "Frigorificada", "Perigosa", "Contêiner", "Viva", "Indivisível"]
TIPOS_MANUTENCAO = ["Preventiva", "Corretiva", "Preditiva"]
SERVICOS_MANUTENCAO = [
    "Troca de óleo", "Revisão 40k", "Revisão 80k", "Revisão 120k",
    "Pastilhas de freio", "Filtro de ar", "Filtro de combustível",
    "Troca de pneu", "Alinhamento e balanceamento", "Troca de correia",
    "Manutenção elétrica", "Troca de bateria", "Reparo de câmbio",
    "Borracharia", "Funilaria e pintura", "Troca de amortecedor",
]
STATUS_MANUTENCAO = ["Concluída", "Em andamento", "Agendada", "Cancelada"]
POSTOS_COMBUSTIVEL = [f"Posto {fake.last_name()}" for _ in range(30)]
TIPO_COMBUSTIVEL = ["Diesel S10", "Diesel S500", "Arla 32"]
MOTIVOS_ATRASO = ["Trânsito", "Problema mecânico", "Acidente", "Fiscalização", "Chuva/Condições climáticas", "Atraso na carga", "N/A"]
TIPOS_DESPESA  = ["Pedágio", "Alimentação", "Hospedagem", "Manutenção emergencial", "Multa", "Lavagem", "Outros"]
TIPOS_RECEITA  = ["Frete", "Adiantamento", "Ajuste de frete", "Devolução de despesa"]
BANCOS         = ["Banco do Brasil", "Bradesco", "Itaú", "Santander", "Caixa", "Sicoob", "Sicredi"]
MOTORISTAS     = [fake.name() for _ in range(40)]
CLIENTES       = [fake.company() for _ in range(60)]
CIDADES_BR = [
    ("São Paulo", "SP"), ("Campinas", "SP"), ("Santos", "SP"), ("Ribeirão Preto", "SP"),
    ("Rio de Janeiro", "RJ"), ("Belo Horizonte", "MG"), ("Uberlândia", "MG"),
    ("Curitiba", "PR"), ("Londrina", "PR"), ("Maringá", "PR"),
    ("Porto Alegre", "RS"), ("Caxias do Sul", "RS"),
    ("Florianópolis", "SC"), ("Joinville", "SC"),
    ("Salvador", "BA"), ("Feira de Santana", "BA"),
    ("Fortaleza", "CE"), ("Recife", "PE"), ("Manaus", "AM"),
    ("Goiânia", "GO"), ("Brasília", "DF"), ("Cuiabá", "MT"),
    ("Campo Grande", "MS"), ("Belém", "PA"), ("Vitória", "ES"),
]


def gerar_transporte(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    """
    Gera dados do setor de Transporte / Frota em Star Schema.

    Tabelas
    -------
    DimVeiculo       : Frota de veículos (caminhões)
    DimMotorista     : Motoristas cadastrados
    DimCliente       : Clientes / embarcadores
    DimRota          : Rotas entre cidades
    DimPosto         : Postos de abastecimento
    FatoViagem       : Viagens realizadas (core do negócio)
    FatoAbastecimento: Abastecimentos por veículo
    FatoManutencao   : Manutenções preventivas e corretivas
    FatoDespesa      : Despesas operacionais por viagem
    dCalendario      : Tabela calendário
    """
    if n is None or n <= 0:
        n = 1_000
    n = int(n)

    # ── DimVeiculo ────────────────────────────────────────────────────────────
    n_veic = min(max(n // 20, 20), 200)
    marcas = random.choices(MARCAS_CAMINHAO, k=n_veic)
    modelos = [random.choice(MODELOS[m]) for m in marcas]
    dim_veiculo = pd.DataFrame({
        "id_veiculo":       new_ids(n_veic),
        "placa":            [f"{fake.random_letter()}{fake.random_letter()}{fake.random_letter()}-{rng.integers(1000,9999)}" for _ in range(n_veic)],
        "marca":            marcas,
        "modelo":           modelos,
        "tipo":             random.choices(TIPOS_VEICULO, k=n_veic),
        "ano_fabricacao":   rng.integers(2010, 2024, n_veic),
        "km_atual":         rng.integers(50_000, 800_000, n_veic),
        "capacidade_ton":   rng.uniform(5, 45, n_veic).round(1),
        "consumo_medio_kmL":rng.uniform(2.0, 4.5, n_veic).round(2),
        "ativo":            random.choices([True, False], weights=[88, 12], k=n_veic),
        "data_aquisicao":   rand_dates(date(2010, 1, 1), end, n_veic),
        "valor_aquisicao":  rng.uniform(150_000, 600_000, n_veic).round(2),
        "seguradora":       [fake.company() for _ in range(n_veic)],
        "vencimento_seguro":rand_dates(end, date(end.year + 2, 12, 31), n_veic),
    })

    # ── DimMotorista ─────────────────────────────────────────────────────────
    n_mot = len(MOTORISTAS)
    dim_motorista = pd.DataFrame({
        "id_motorista":     new_ids(n_mot),
        "nome":             MOTORISTAS,
        "cpf":              [fake.cpf() for _ in range(n_mot)],
        "cnh":              [f"{rng.integers(10000000, 99999999)}" for _ in range(n_mot)],
        "categoria_cnh":    random.choices(["C", "D", "E"], weights=[20, 30, 50], k=n_mot),
        "vencimento_cnh":   rand_dates(end, date(end.year + 5, 12, 31), n_mot),
        "telefone":         [fake.phone_number() for _ in range(n_mot)],
        "uf_base":          [random.choice(CIDADES_BR)[1] for _ in range(n_mot)],
        "ativo":            random.choices([True, False], weights=[85, 15], k=n_mot),
        "data_admissao":    rand_dates(date(2010, 1, 1), end, n_mot),
        "avaliacao_media":  rng.uniform(3.0, 5.0, n_mot).round(2),
        "viagens_total":    rng.integers(10, 500, n_mot),
        "km_total":         rng.integers(10_000, 1_000_000, n_mot),
    })

    # ── DimCliente ────────────────────────────────────────────────────────────
    n_cli = len(CLIENTES)
    dim_cliente = pd.DataFrame({
        "id_cliente":       new_ids(n_cli),
        "razao_social":     CLIENTES,
        "cnpj":             [fake.cnpj() for _ in range(n_cli)],
        "segmento":         random.choices(["Varejo", "Indústria", "Agronegócio", "Construção", "Alimentício", "Químico", "Farmacêutico"], k=n_cli),
        "uf":               [random.choice(CIDADES_BR)[1] for _ in range(n_cli)],
        "cidade":           [random.choice(CIDADES_BR)[0] for _ in range(n_cli)],
        "limite_credito":   rng.uniform(10_000, 500_000, n_cli).round(2),
        "prazo_pagamento_d":random.choices([7, 14, 21, 28, 30, 45, 60], k=n_cli),
        "ativo":            random.choices([True, False], weights=[85, 15], k=n_cli),
        "data_cadastro":    rand_dates(date(2015, 1, 1), end, n_cli),
    })

    # ── DimRota ──────────────────────────────────────────────────────────────
    n_rot = 80
    origens  = [random.choice(CIDADES_BR) for _ in range(n_rot)]
    destinos = [random.choice(CIDADES_BR) for _ in range(n_rot)]
    dim_rota = pd.DataFrame({
        "id_rota":          new_ids(n_rot),
        "cidade_origem":    [o[0] for o in origens],
        "uf_origem":        [o[1] for o in origens],
        "cidade_destino":   [d[0] for d in destinos],
        "uf_destino":       [d[1] for d in destinos],
        "distancia_km":     rng.uniform(50, 3_500, n_rot).round(0),
        "pedagio_estimado": rng.uniform(50, 800, n_rot).round(2),
        "tempo_estimado_h": rng.uniform(1, 48, n_rot).round(1),
        "tipo_estrada":     random.choices(["Rodovia Federal", "Rodovia Estadual", "Mista"], k=n_rot),
    })

    # ── DimPosto ─────────────────────────────────────────────────────────────
    n_pos = len(POSTOS_COMBUSTIVEL)
    dim_posto = pd.DataFrame({
        "id_posto":         new_ids(n_pos),
        "nome":             POSTOS_COMBUSTIVEL,
        "bandeira":         random.choices(["Ipiranga", "Shell", "Petrobras", "Raízen", "Independente"], k=n_pos),
        "uf":               [random.choice(CIDADES_BR)[1] for _ in range(n_pos)],
        "cidade":           [random.choice(CIDADES_BR)[0] for _ in range(n_pos)],
        "conveniado":       random.choices([True, False], weights=[60, 40], k=n_pos),
    })

    # ── FatoViagem ───────────────────────────────────────────────────────────
    status_list   = random.choices(STATUS_VIAGEM, weights=[15, 25, 10, 40, 8, 2], k=n)
    concluida     = [s == "Concluída" for s in status_list]
    atrasada      = [s == "Atrasada"  for s in status_list]
    datas_inicio  = rand_dates(start, end, n)
    distancias    = rng.uniform(50, 3_500, n).round(0)
    frete_ton     = rng.uniform(80, 400, n)
    peso_ton      = rng.uniform(1, 45, n).round(1)
    valor_frete   = (frete_ton * peso_ton).round(2)
    custo_op      = (valor_frete * rng.uniform(0.45, 0.80, n)).round(2)
    lucro         = (valor_frete - custo_op).round(2)
    rentabilidade = (lucro / valor_frete * 100).round(2)

    fato_viagem = pd.DataFrame({
        "id_viagem":            new_ids(n),
        "id_data_inicio":       datas_inicio,
        "id_data_fim":          [d + timedelta(days=int(rng.integers(0, 5))) for d in datas_inicio],
        "id_veiculo":           random.choices(dim_veiculo["id_veiculo"].tolist(), k=n),
        "id_motorista":         random.choices(dim_motorista["id_motorista"].tolist(), k=n),
        "id_cliente":           random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "id_rota":              random.choices(dim_rota["id_rota"].tolist(), k=n),
        "status":               status_list,
        "tipo_carga":           random.choices(TIPOS_CARGA, k=n),
        "peso_ton":             peso_ton,
        "distancia_km":         distancias,
        "valor_frete":          valor_frete,
        "custo_operacional":    custo_op,
        "lucro":                lucro,
        "rentabilidade_pct":    rentabilidade,
        "pedagio":              rng.uniform(50, 800, n).round(2),
        "adiantamento":         rng.uniform(0, valor_frete * 0.5).round(2),
        "saldo_acerto":         (valor_frete - rng.uniform(0, valor_frete * 0.5, n)).round(2),
        "km_rodados":           distancias * rng.uniform(0.95, 1.05, n),
        "tempo_viagem_h":       rng.uniform(1, 72, n).round(1),
        "concluida":            concluida,
        "atrasada":             atrasada,
        "motivo_atraso":        ["N/A" if not a else random.choice(MOTIVOS_ATRASO[:-1]) for a in atrasada],
        "avaliacao_cliente":    [round(rng.uniform(3, 5), 1) if c else None for c in concluida],
        "acerto_realizado":     random.choices([True, False], weights=[70, 30], k=n),
        "nota_fiscal":          [f"NF-{rng.integers(100000, 999999)}" for _ in range(n)],
    })

    # ── FatoAbastecimento ────────────────────────────────────────────────────
    n_abast = int(n * 1.2)
    litros  = rng.uniform(50, 400, n_abast).round(1)
    preco_L = rng.uniform(5.50, 7.50, n_abast).round(3)
    fato_abastecimento = pd.DataFrame({
        "id_abastecimento":     new_ids(n_abast),
        "id_data":              rand_dates(start, end, n_abast),
        "id_veiculo":           random.choices(dim_veiculo["id_veiculo"].tolist(), k=n_abast),
        "id_motorista":         random.choices(dim_motorista["id_motorista"].tolist(), k=n_abast),
        "id_posto":             random.choices(dim_posto["id_posto"].tolist(), k=n_abast),
        "id_viagem":            random.choices(fato_viagem["id_viagem"].tolist(), k=n_abast),
        "tipo_combustivel":     random.choices(TIPO_COMBUSTIVEL, weights=[70, 25, 5], k=n_abast),
        "litros":               litros,
        "preco_litro":          preco_L,
        "valor_total":          (litros * preco_L).round(2),
        "km_momento":           rng.integers(50_000, 800_000, n_abast),
        "consumo_kmL":          rng.uniform(1.8, 4.8, n_abast).round(2),
        "desvio_consumo_pct":   rng.uniform(-20, 20, n_abast).round(1),
        "pagamento":            random.choices(["Cartão Frota", "Dinheiro", "PIX", "Convênio"], weights=[55, 20, 15, 10], k=n_abast),
        "aprovado":             random.choices([True, False], weights=[92, 8], k=n_abast),
    })

    # ── FatoManutencao ────────────────────────────────────────────────────────
    n_man = int(n * 0.4)
    fato_manutencao = pd.DataFrame({
        "id_manutencao":        new_ids(n_man),
        "id_data":              rand_dates(start, end, n_man),
        "id_veiculo":           random.choices(dim_veiculo["id_veiculo"].tolist(), k=n_man),
        "tipo":                 random.choices(TIPOS_MANUTENCAO, weights=[60, 35, 5], k=n_man),
        "servico":              random.choices(SERVICOS_MANUTENCAO, k=n_man),
        "status":               random.choices(STATUS_MANUTENCAO, weights=[70, 10, 15, 5], k=n_man),
        "km_veiculo":           rng.integers(50_000, 800_000, n_man),
        "km_proximo_servico":   rng.integers(50_000, 850_000, n_man),
        "custo_pecas":          rng.uniform(0, 15_000, n_man).round(2),
        "custo_mao_obra":       rng.uniform(100, 3_000, n_man).round(2),
        "custo_total":          rng.uniform(100, 18_000, n_man).round(2),
        "oficina":              [fake.company() for _ in range(n_man)],
        "tempo_parado_h":       rng.uniform(1, 120, n_man).round(1),
        "garantia_dias":        rng.integers(0, 365, n_man),
        "preventiva":           [t == "Preventiva" for t in random.choices(TIPOS_MANUTENCAO, weights=[60, 35, 5], k=n_man)],
    })

    # ── FatoDespesa ──────────────────────────────────────────────────────────
    n_desp = int(n * 0.8)
    fato_despesa = pd.DataFrame({
        "id_despesa":           new_ids(n_desp),
        "id_data":              rand_dates(start, end, n_desp),
        "id_viagem":            random.choices(fato_viagem["id_viagem"].tolist(), k=n_desp),
        "id_motorista":         random.choices(dim_motorista["id_motorista"].tolist(), k=n_desp),
        "id_veiculo":           random.choices(dim_veiculo["id_veiculo"].tolist(), k=n_desp),
        "tipo_despesa":         random.choices(TIPOS_DESPESA, weights=[30, 25, 15, 15, 5, 5, 5], k=n_desp),
        "valor":                rng.uniform(10, 2_000, n_desp).round(2),
        "aprovado":             random.choices([True, False], weights=[85, 15], k=n_desp),
        "comprovante":          random.choices([True, False], weights=[80, 20], k=n_desp),
        "banco":                random.choices(BANCOS, k=n_desp),
        "reembolsado":          random.choices([True, False], weights=[75, 25], k=n_desp),
    })

    return {
        "DimVeiculo":           dim_veiculo,
        "DimMotorista":         dim_motorista,
        "DimCliente":           dim_cliente,
        "DimRota":              dim_rota,
        "DimPosto":             dim_posto,
        "FatoViagem":           fato_viagem,
        "FatoAbastecimento":    fato_abastecimento,
        "FatoManutencao":       fato_manutencao,
        "FatoDespesa":          fato_despesa,
        "dCalendario":          dcalendario(start, end),
    }
