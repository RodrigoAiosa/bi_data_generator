"""generators/portabilidade_claro.py — Setor Migração IN/OUT (Portabilidade) — Claro Brasil.

Modela o fluxo de portabilidade numérica da operadora Claro:
  • Migração IN  -> cliente sai de uma operadora concorrente e entra na Claro
  • Migração OUT -> cliente sai da Claro e migra para uma operadora concorrente

Cada evento de migração está associado a um serviço/produto Claro (plano
pós-pago, pré-pago, controle, fibra, TV, combo, M2M etc.), permitindo analisar
saldo líquido de portabilidade, motivos de saída/entrada, canais e receita
em risco (OUT) x receita conquistada (IN).
"""

import random
from datetime import date

import numpy as np
import pandas as pd

from .helpers import dcalendario, get_faker, new_ids, rand_dates, rng

OPERADORAS_CONCORRENTES = ["Vivo", "TIM", "Oi", "Algar Telecom", "Surf Telecom", "Correios Celular"]

CANAIS = [
    "Loja Própria", "Loja Autorizada", "App Minha Claro",
    "Central de Atendimento", "Site Claro", "Porta a Porta", "Parceiro/Correspondente",
]

MOTIVOS_OUT = [
    "Preço mais competitivo no concorrente",
    "Qualidade de sinal / cobertura",
    "Atendimento ao cliente insatisfatório",
    "Oferta de fidelidade do concorrente",
    "Combo (fixo+móvel) mais vantajoso",
    "Mudança de endereço sem cobertura Claro",
    "Insatisfação com velocidade de internet",
    "Cancelamento por não uso do serviço",
]

MOTIVOS_IN = [
    "Melhor oferta comercial Claro",
    "Indicação de amigo/familiar",
    "Melhor cobertura 4G/5G Claro",
    "Promoção de portabilidade Claro",
    "Combo Claro mais vantajoso",
    "Melhor atendimento Claro",
    "Ação de loja/parceiro Claro",
    "Insatisfação com operadora anterior",
]

STATUS_PORTABILIDADE = ["Concluída", "Em Processamento", "Cancelada pelo Cliente", "Rejeitada pela Anatel"]

CATEGORIAS_SERVICO = [
    "Pós-pago Móvel", "Pré-pago Móvel", "Controle",
    "Fibra / Banda Larga", "TV por Assinatura", "Combo Fixo+Móvel", "Empresarial/M2M",
]

NOMES_SERVICO = {
    "Pós-pago Móvel":       ["Claro Pós Família", "Claro Pós Individual", "Claro Pós Ilimitado"],
    "Pré-pago Móvel":       ["Claro Pré Fácil", "Claro Pré Turbo", "Claro Pré Recarga Digital"],
    "Controle":             ["Claro Controle Essencial", "Claro Controle Plus", "Claro Controle Família"],
    "Fibra / Banda Larga":  ["Claro Residencial Fibra 300MB", "Claro Residencial Fibra 500MB", "Claro Net Fibra 1GB"],
    "TV por Assinatura":    ["Claro TV+ Light", "Claro TV+ Full", "Claro Box TV"],
    "Combo Fixo+Móvel":     ["Claro Combo Família", "Claro Combo Total", "Claro Combo Fibra+Móvel"],
    "Empresarial/M2M":      ["Claro Flex Empresarial", "Claro M2M Conectado", "Claro Corporate Data"],
}

FAIXA_PRECO = {
    "Pós-pago Móvel":      (69.9, 249.9),
    "Pré-pago Móvel":      (14.9, 59.9),
    "Controle":            (39.9, 119.9),
    "Fibra / Banda Larga": (79.9, 199.9),
    "TV por Assinatura":   (49.9, 179.9),
    "Combo Fixo+Móvel":    (119.9, 349.9),
    "Empresarial/M2M":     (29.9, 899.9),
}

UFS = ["SP", "RJ", "MG", "RS", "PR", "BA", "SC", "PE", "CE", "GO", "DF", "AM", "PA"]

REGIAO_POR_UF = {
    "SP": "Sudeste", "RJ": "Sudeste", "MG": "Sudeste",
    "RS": "Sul", "PR": "Sul", "SC": "Sul",
    "BA": "Nordeste", "PE": "Nordeste", "CE": "Nordeste",
    "GO": "Centro-Oeste", "DF": "Centro-Oeste",
    "AM": "Norte", "PA": "Norte",
}


def gerar_portabilidade_claro(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    fake = get_faker()

    n_servicos   = min(len(CATEGORIAS_SERVICO) * 3, 21)
    n_operadoras = len(OPERADORAS_CONCORRENTES) + 1  # + Claro
    n_clientes   = min(n, 8000)

    # ── DimOperadora ─────────────────────────────────────────────────────────
    dim_operadora = pd.DataFrame({
        "id_operadora": new_ids(n_operadoras),
        "nome_operadora": ["Claro"] + OPERADORAS_CONCORRENTES,
        "tipo": ["Operadora Foco"] + ["Concorrente"] * len(OPERADORAS_CONCORRENTES),
    })
    id_claro = int(dim_operadora.loc[dim_operadora["nome_operadora"] == "Claro", "id_operadora"].iloc[0])

    # ── DimServico (produtos Claro) ──────────────────────────────────────────
    categorias_srv = []
    nomes_srv = []
    precos_srv = []
    for cat in CATEGORIAS_SERVICO:
        for nome in NOMES_SERVICO[cat]:
            categorias_srv.append(cat)
            nomes_srv.append(nome)
            lo, hi = FAIXA_PRECO[cat]
            precos_srv.append(round(rng.uniform(lo, hi), 2))

    dim_servico = pd.DataFrame({
        "id_servico":     new_ids(len(nomes_srv)),
        "nome_servico":   nomes_srv,
        "categoria":      categorias_srv,
        "valor_mensal":   precos_srv,
    })

    # ── DimCliente ───────────────────────────────────────────────────────────
    dim_cliente = pd.DataFrame({
        "id_cliente":    new_ids(n_clientes),
        "nome":          [fake.name() for _ in range(n_clientes)],
        "cpf":           [fake.cpf() for _ in range(n_clientes)],
        "uf":            random.choices(UFS, k=n_clientes),
        "faixa_etaria":  random.choices(
            ["18-24", "25-34", "35-44", "45-59", "60+"],
            weights=[15, 30, 25, 20, 10], k=n_clientes,
        ),
    })
    dim_cliente["regiao"] = dim_cliente["uf"].map(REGIAO_POR_UF)

    # ── FatoMigracao ─────────────────────────────────────────────────────────
    direcao = random.choices(["IN", "OUT"], weights=[52, 48], k=n)  # leve saldo positivo p/ Claro

    ids_cliente     = random.choices(dim_cliente["id_cliente"].tolist(), k=n)
    ids_servico     = random.choices(dim_servico["id_servico"].tolist(), k=n)
    operadoras_cc   = random.choices(OPERADORAS_CONCORRENTES, k=n)  # operadora contraparte (não-Claro)
    canais          = random.choices(CANAIS, weights=[20, 15, 25, 15, 15, 5, 5], k=n)
    status          = random.choices(STATUS_PORTABILIDADE, weights=[78, 10, 8, 4], k=n)

    motivo = [
        random.choice(MOTIVOS_OUT) if d == "OUT" else random.choice(MOTIVOS_IN)
        for d in direcao
    ]

    # Operadora de origem / destino conforme a direção do fluxo
    operadora_origem = [
        oc if d == "IN" else "Claro"
        for d, oc in zip(direcao, operadoras_cc)
    ]
    operadora_destino = [
        "Claro" if d == "IN" else oc
        for d, oc in zip(direcao, operadoras_cc)
    ]

    servico_map = dim_servico.set_index("id_servico")[["valor_mensal", "categoria"]]
    valor_servico = servico_map.loc[ids_servico, "valor_mensal"].to_numpy()
    categoria_servico = servico_map.loc[ids_servico, "categoria"].to_numpy()

    cliente_map = dim_cliente.set_index("id_cliente")[["uf", "regiao"]]
    uf_evento = cliente_map.loc[ids_cliente, "uf"].to_numpy()
    regiao_evento = cliente_map.loc[ids_cliente, "regiao"].to_numpy()

    tempo_permanencia_dias = rng.integers(30, 2600, n)  # tempo na operadora de origem antes da portabilidade
    nota_satisfacao = rng.integers(1, 11, n)            # 1-10, pesquisa pós-portabilidade

    fato = pd.DataFrame({
        "id_migracao":            new_ids(n),
        "id_data":                rand_dates(start, end, n),
        "direcao":                direcao,
        "id_cliente":             ids_cliente,
        "id_servico":             ids_servico,
        "categoria_servico":      categoria_servico,
        "operadora_origem":       operadora_origem,
        "operadora_destino":      operadora_destino,
        "canal":                  canais,
        "motivo":                 motivo,
        "status_portabilidade":   status,
        "uf":                     uf_evento,
        "regiao":                 regiao_evento,
        "valor_mensal_servico":   valor_servico.round(2),
        "tempo_permanencia_dias": tempo_permanencia_dias,
        "nota_satisfacao":        nota_satisfacao,
    })

    # Receita: positiva quando é IN (ganho de receita recorrente), negativa quando OUT (perda)
    fato["receita_liquida_mensal"] = np.where(
        fato["direcao"].eq("IN"), fato["valor_mensal_servico"], -fato["valor_mensal_servico"]
    ).round(2)

    return {
        "DimOperadora": dim_operadora,
        "DimServico":   dim_servico,
        "DimCliente":   dim_cliente,
        "FatoMigracao": fato,
        "dCalendario":  dcalendario(start, end),
    }
