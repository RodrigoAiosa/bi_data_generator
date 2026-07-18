"""generators/crm.py — Setor CRM (Customer Relationship Management)."""
import random
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

# ── Listas de domínio ────────────────────────────────────────────────────────

ESTAGIOS_FUNIL = [
    "Prospecto",
    "Qualificado",
    "Proposta Enviada",
    "Negociação",
    "Fechado Ganho",
    "Fechado Perdido",
]

MOTIVOS_PERDA = [
    "Preço",
    "Concorrente",
    "Sem Orçamento",
    "Timing Inadequado",
    "Falta de Fit",
    "Sem Resposta",
    "N/A",
]

CANAIS_ORIGEM = [
    "Inbound - Site",
    "Inbound - Blog",
    "Outbound - Cold Email",
    "Outbound - Cold Call",
    "Indicação Cliente",
    "Parceiro",
    "Evento / Feira",
    "Redes Sociais",
    "Anúncio Pago",
    "Webinar",
]

TIPOS_ATIVIDADE = [
    "Ligação",
    "E-mail Enviado",
    "E-mail Recebido",
    "Reunião Presencial",
    "Reunião Online",
    "Demo / Apresentação",
    "Proposta Enviada",
    "Follow-up",
    "WhatsApp",
    "Visita Técnica",
]

RESULTADOS_ATIVIDADE = [
    "Concluído",
    "Sem Resposta",
    "Reagendado",
    "Cancelado",
    "Em Andamento",
]

SEGMENTOS = [
    "Pequena Empresa",
    "Média Empresa",
    "Grande Empresa",
    "Enterprise",
    "Startup",
    "Governo",
    "Terceiro Setor",
]

SETORES = [
    "Tecnologia",
    "Varejo",
    "Saúde",
    "Financeiro",
    "Indústria",
    "Logística",
    "Educação",
    "Agronegócio",
    "Construção",
    "Serviços",
    "Telecomunicações",
    "Energia",
]

CARGOS_DECISOR = [
    "CEO",
    "CFO",
    "CTO",
    "Diretor Comercial",
    "Diretor de TI",
    "Gerente de Compras",
    "Coordenador de Projetos",
    "Sócio-Proprietário",
]

TIPOS_CONTA = ["Cliente Ativo", "Cliente Inativo", "Prospect", "Parceiro", "Concorrente"]

PRIORIDADES = ["Alta", "Média", "Baixa"]

VENDEDORES = [fake.name() for _ in range(20)]
EQUIPES = ["Comercial Sul", "Comercial Norte", "Comercial Centro-Oeste", "Comercial Nordeste", "Key Accounts", "SMB"]


# ── Função principal ─────────────────────────────────────────────────────────

def gerar_crm(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    """
    Gera dados do setor CRM (Customer Relationship Management) em Star Schema.

    Tabelas geradas
    ---------------
    - DimConta       : Empresas/contas gerenciadas no CRM
    - DimContato     : Pessoas de contato vinculadas às contas
    - DimVendedor    : Equipe comercial responsável
    - DimProduto     : Produtos/serviços ofertados
    - FatoOportunidade : Oportunidades de venda (pipeline e resultados)
    - FatoAtividade  : Interações e atividades registradas no CRM
    - dCalendario    : Tabela calendário

    Parâmetros
    ----------
    n     : Número aproximado de registros nas tabelas fato
    start : Data inicial do período
    end   : Data final do período
    """

    # ── Validação ────────────────────────────────────────────────────────────
    if n is None or n <= 0:
        n = 1_000
    n = int(n)

    for d in (start, end):
        if isinstance(d, str):
            d = datetime.strptime(d, "%Y-%m-%d").date()

    # ── DimVendedor ──────────────────────────────────────────────────────────
    n_vendedores = len(VENDEDORES)
    dim_vendedor = pd.DataFrame({
        "id_vendedor":   new_ids(n_vendedores),
        "nome":          VENDEDORES,
        "equipe":        random.choices(EQUIPES, k=n_vendedores),
        "cargo":         random.choices(["Executivo de Vendas", "SDR", "Account Executive", "Key Account Manager"], k=n_vendedores),
        "uf":            [fake.state_abbr() for _ in range(n_vendedores)],
        "meta_mensal":   rng.uniform(50_000, 500_000, n_vendedores).round(2),
        "ativo":         random.choices([True, False], weights=[90, 10], k=n_vendedores),
        "data_admissao": rand_dates(date(2015, 1, 1), end, n_vendedores),
    })

    # ── DimProduto ───────────────────────────────────────────────────────────
    produtos = [
        ("Software ERP", "Licença", "SaaS"),
        ("Módulo CRM", "Licença", "SaaS"),
        ("Suporte Premium", "Serviço", "Recorrente"),
        ("Consultoria Implantação", "Serviço", "Projeto"),
        ("Treinamento Usuários", "Serviço", "Avulso"),
        ("Integração API", "Serviço", "Projeto"),
        ("Migração de Dados", "Serviço", "Projeto"),
        ("BI & Analytics", "Licença", "SaaS"),
        ("App Mobile", "Licença", "SaaS"),
        ("Armazenamento Cloud", "Infraestrutura", "Recorrente"),
    ]
    n_produtos = len(produtos)
    dim_produto = pd.DataFrame({
        "id_produto":     new_ids(n_produtos),
        "nome":           [p[0] for p in produtos],
        "tipo":           [p[1] for p in produtos],
        "modelo_receita": [p[2] for p in produtos],
        "preco_lista":    rng.uniform(500, 50_000, n_produtos).round(2),
        "margem_pct":     rng.uniform(20, 80, n_produtos).round(1),
        "ativo":          [True] * n_produtos,
    })

    # ── DimConta ─────────────────────────────────────────────────────────────
    n_contas = min(max(n // 5, 200), 2_000)
    dim_conta = pd.DataFrame({
        "id_conta":         new_ids(n_contas),
        "nome_empresa":     [fake.company() for _ in range(n_contas)],
        "cnpj":             [fake.cnpj() for _ in range(n_contas)],
        "setor":            random.choices(SETORES, k=n_contas),
        "segmento":         random.choices(SEGMENTOS, k=n_contas),
        "tipo_conta":       random.choices(TIPOS_CONTA, weights=[40, 10, 35, 10, 5], k=n_contas),
        "uf":               [fake.state_abbr() for _ in range(n_contas)],
        "cidade":           [fake.city() for _ in range(n_contas)],
        "faturamento_anual": rng.uniform(100_000, 500_000_000, n_contas).round(2),
        "n_funcionarios":   rng.integers(1, 50_000, n_contas),
        "id_vendedor_resp": random.choices(dim_vendedor["id_vendedor"].tolist(), k=n_contas),
        "data_cadastro":    rand_dates(date(2018, 1, 1), end, n_contas),
        "score_saude":      rng.uniform(0, 100, n_contas).round(1),
    })

    # ── DimContato ───────────────────────────────────────────────────────────
    n_contatos = min(n_contas * 2, 4_000)
    dim_contato = pd.DataFrame({
        "id_contato":    new_ids(n_contatos),
        "nome":          [fake.name() for _ in range(n_contatos)],
        "cargo":         random.choices(CARGOS_DECISOR, k=n_contatos),
        "email":         [fake.company_email() for _ in range(n_contatos)],
        "telefone":      [fake.phone_number() for _ in range(n_contatos)],
        "id_conta":      random.choices(dim_conta["id_conta"].tolist(), k=n_contatos),
        "decisor":       random.choices([True, False], weights=[30, 70], k=n_contatos),
        "linkedin":      [f"linkedin.com/in/{fake.user_name()}" for _ in range(n_contatos)],
        "data_cadastro": rand_dates(date(2018, 1, 1), end, n_contatos),
        "ativo":         random.choices([True, False], weights=[80, 20], k=n_contatos),
    })

    # ── FatoOportunidade ─────────────────────────────────────────────────────
    n_opor = n
    estagios = random.choices(ESTAGIOS_FUNIL, weights=[20, 18, 15, 12, 20, 15], k=n_opor)
    valor_estimado = rng.uniform(1_000, 1_000_000, n_opor).round(2)
    probabilidade = [
        {"Prospecto": 10, "Qualificado": 30, "Proposta Enviada": 50,
         "Negociação": 70, "Fechado Ganho": 100, "Fechado Perdido": 0}[e]
        for e in estagios
    ]
    ganho = [e == "Fechado Ganho" for e in estagios]
    perdido = [e == "Fechado Perdido" for e in estagios]

    fato_oportunidade = pd.DataFrame({
        "id_oportunidade":   new_ids(n_opor),
        "id_data_abertura":  rand_dates(start, end, n_opor),
        "id_conta":          random.choices(dim_conta["id_conta"].tolist(), k=n_opor),
        "id_contato":        random.choices(dim_contato["id_contato"].tolist(), k=n_opor),
        "id_vendedor":       random.choices(dim_vendedor["id_vendedor"].tolist(), k=n_opor),
        "id_produto":        random.choices(dim_produto["id_produto"].tolist(), k=n_opor),
        "estagio":           estagios,
        "canal_origem":      random.choices(CANAIS_ORIGEM, k=n_opor),
        "valor_estimado":    valor_estimado,
        "valor_fechado":     [v if g else 0 for v, g in zip(valor_estimado, ganho)],
        "desconto_pct":      rng.uniform(0, 40, n_opor).round(1),
        "probabilidade_pct": probabilidade,
        "prioridade":        random.choices(PRIORIDADES, weights=[25, 50, 25], k=n_opor),
        "ciclo_vendas_dias": rng.integers(1, 365, n_opor),
        "ganho":             ganho,
        "perdido":           perdido,
        "motivo_perda":      [random.choice(MOTIVOS_PERDA[:-1]) if p else "N/A" for p in perdido],
        "n_atividades":      rng.integers(1, 50, n_opor),
        "score_engajamento": rng.uniform(0, 100, n_opor).round(1),
    })

    # ── FatoAtividade ────────────────────────────────────────────────────────
    n_ativ = int(n * 1.5)
    fato_atividade = pd.DataFrame({
        "id_atividade":    new_ids(n_ativ),
        "id_data":         rand_dates(start, end, n_ativ),
        "id_oportunidade": random.choices(fato_oportunidade["id_oportunidade"].tolist(), k=n_ativ),
        "id_conta":        random.choices(dim_conta["id_conta"].tolist(), k=n_ativ),
        "id_contato":      random.choices(dim_contato["id_contato"].tolist(), k=n_ativ),
        "id_vendedor":     random.choices(dim_vendedor["id_vendedor"].tolist(), k=n_ativ),
        "tipo_atividade":  random.choices(TIPOS_ATIVIDADE, k=n_ativ),
        "resultado":       random.choices(RESULTADOS_ATIVIDADE, weights=[55, 20, 12, 8, 5], k=n_ativ),
        "duracao_min":     rng.integers(5, 120, n_ativ),
        "resposta_cliente": random.choices([True, False], weights=[60, 40], k=n_ativ),
        "agendou_proximo": random.choices([True, False], weights=[45, 55], k=n_ativ),
        "notas":           ["" for _ in range(n_ativ)],  # placeholder; preencha conforme necessidade
    })

    return {
        "DimVendedor":       dim_vendedor,
        "DimProduto":        dim_produto,
        "DimConta":          dim_conta,
        "DimContato":        dim_contato,
        "FatoOportunidade":  fato_oportunidade,
        "FatoAtividade":     fato_atividade,
        "dCalendario":       dcalendario(start, end),
    }
