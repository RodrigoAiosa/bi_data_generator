"""
generators_bi/setores.py
Geradores de dados fictícios por setor de negócio.

Cada gerador retorna um dict {"DimX": DataFrame, ..., "FatoY": DataFrame, "dCalendario": DataFrame}
com integridade referencial garantida: toda chave estrangeira na tabela fato é
amostrada diretamente das chaves primárias existentes nas dimensões.

A tabela fato é sempre limitada a MAX_LINHAS_FATO linhas (padrão: 10.000).
"""

import random
from datetime import date

import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

MAX_LINHAS_FATO = 10_000

fake = Faker("pt_BR")

ESTADOS = ["SP", "RJ", "MG", "RS", "PR", "SC", "BA", "CE", "PE", "GO"]
REGIOES = {
    "SP": "Sudeste", "RJ": "Sudeste", "MG": "Sudeste",
    "RS": "Sul", "PR": "Sul", "SC": "Sul",
    "BA": "Nordeste", "CE": "Nordeste", "PE": "Nordeste",
    "GO": "Centro-Oeste",
}


def _cap(n: int) -> int:
    return max(1, min(n, MAX_LINHAS_FATO))


# ============================================================================
# VAREJO
# ============================================================================
def gerar_varejo(n: int, start: date, end: date) -> dict:
    n = _cap(n)
    n_clientes = min(n, 3000)
    n_produtos = min(300, n // 5 + 30)
    n_vendedores = 40
    n_filiais = 8

    dim_geo = pd.DataFrame({
        "id_geo": new_ids(len(ESTADOS)), "estado": ESTADOS,
        "regiao": [REGIOES[e] for e in ESTADOS],
    })
    dim_cliente = pd.DataFrame({
        "id_cliente": new_ids(n_clientes),
        "nome": [fake.name() for _ in range(n_clientes)],
        "cidade": [fake.city() for _ in range(n_clientes)],
        "uf": random.choices(ESTADOS, k=n_clientes),
        "segmento": random.choices(["Pessoa Física", "Pessoa Jurídica", "Premium"], k=n_clientes),
    })
    categorias = ["Eletrônicos", "Vestuário", "Alimentos", "Móveis", "Esporte", "Beleza"]
    dim_produto = pd.DataFrame({
        "id_produto": new_ids(n_produtos),
        "nome": [f"Produto {fake.word().capitalize()} {i}" for i in range(1, n_produtos + 1)],
        "categoria": random.choices(categorias, k=n_produtos),
        "preco_unit": rng.uniform(10, 2000, n_produtos).round(2),
        "custo_unit": rng.uniform(5, 1000, n_produtos).round(2),
    })
    dim_vendedor = pd.DataFrame({
        "id_vendedor": new_ids(n_vendedores),
        "nome": [fake.name() for _ in range(n_vendedores)],
        "regiao": random.choices(list(REGIOES.values()), k=n_vendedores),
    })
    dim_filial = pd.DataFrame({
        "id_filial": new_ids(n_filiais),
        "nome": [f"Filial {fake.city()}" for _ in range(n_filiais)],
        "uf": random.choices(ESTADOS, k=n_filiais),
        "tipo": random.choices(["Loja Física", "E-commerce", "Outlet"], k=n_filiais),
    })

    datas = rand_dates(start, end, n)
    qtds = rng.integers(1, 20, n)
    produtos = random.choices(dim_produto["id_produto"].tolist(), k=n)
    precos = dim_produto.set_index("id_produto")["preco_unit"].loc[produtos].values
    descontos = rng.uniform(0, 0.3, n)

    fato = pd.DataFrame({
        "id_venda": new_ids(n),
        "data": datas,
        "id_cliente": random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "id_produto": produtos,
        "id_vendedor": random.choices(dim_vendedor["id_vendedor"].tolist(), k=n),
        "id_filial": random.choices(dim_filial["id_filial"].tolist(), k=n),
        "quantidade": qtds,
        "valor_unit": precos.round(2),
        "desconto": descontos.round(3),
        "valor_total": (qtds * precos * (1 - descontos)).round(2),
    })

    return {
        "DimCliente": dim_cliente, "DimProduto": dim_produto, "DimVendedor": dim_vendedor,
        "DimFilial": dim_filial, "DimGeografia": dim_geo,
        "FatoVendas": fato, "dCalendario": dcalendario(start, end),
    }


# ============================================================================
# FINANCEIRO
# ============================================================================
def gerar_financeiro(n: int, start: date, end: date) -> dict:
    n = _cap(n)
    n_clientes = min(n, 2000)
    n_agencias = 25
    n_contas = min(n, 3000)

    dim_agencia = pd.DataFrame({
        "id_agencia": new_ids(n_agencias),
        "nome": [f"Agência {fake.city()}" for _ in range(n_agencias)],
        "uf": random.choices(ESTADOS, k=n_agencias),
    })
    dim_cliente = pd.DataFrame({
        "id_cliente": new_ids(n_clientes),
        "nome": [fake.name() for _ in range(n_clientes)],
        "segmento": random.choices(["Varejo", "Private", "Corporate"], k=n_clientes),
        "score_credito": rng.integers(300, 1000, n_clientes),
    })
    dim_conta = pd.DataFrame({
        "id_conta": new_ids(n_contas),
        "id_cliente": random.choices(dim_cliente["id_cliente"].tolist(), k=n_contas),
        "id_agencia": random.choices(dim_agencia["id_agencia"].tolist(), k=n_contas),
        "tipo_conta": random.choices(["Corrente", "Poupança", "Investimento"], k=n_contas),
    })
    tipos_transacao = ["Depósito", "Saque", "Transferência", "Pagamento", "Investimento"]

    fato = pd.DataFrame({
        "id_transacao": new_ids(n),
        "data": rand_dates(start, end, n),
        "id_conta": random.choices(dim_conta["id_conta"].tolist(), k=n),
        "tipo_transacao": random.choices(tipos_transacao, k=n),
        "valor": rng.uniform(10, 15000, n).round(2),
        "status": random.choices(["Concluída", "Pendente", "Cancelada"], k=n, weights=[85, 10, 5]),
    })

    return {
        "DimCliente": dim_cliente, "DimAgencia": dim_agencia, "DimConta": dim_conta,
        "FatoTransacoes": fato, "dCalendario": dcalendario(start, end),
    }


# ============================================================================
# SAÚDE
# ============================================================================
def gerar_saude(n: int, start: date, end: date) -> dict:
    n = _cap(n)
    n_pacientes = min(n, 2500)
    n_medicos = 60
    n_convenios = 8

    dim_paciente = pd.DataFrame({
        "id_paciente": new_ids(n_pacientes),
        "nome": [fake.name() for _ in range(n_pacientes)],
        "idade": rng.integers(1, 95, n_pacientes),
        "sexo": random.choices(["M", "F"], k=n_pacientes),
    })
    especialidades = ["Cardiologia", "Ortopedia", "Pediatria", "Clínica Geral", "Dermatologia", "Ginecologia"]
    dim_medico = pd.DataFrame({
        "id_medico": new_ids(n_medicos),
        "nome": [f"Dr(a). {fake.name()}" for _ in range(n_medicos)],
        "especialidade": random.choices(especialidades, k=n_medicos),
    })
    dim_convenio = pd.DataFrame({
        "id_convenio": new_ids(n_convenios),
        "nome": [f"Convênio {fake.company()}" for _ in range(n_convenios)],
    })
    tipos_atendimento = ["Consulta", "Exame", "Cirurgia", "Retorno", "Emergência"]

    fato = pd.DataFrame({
        "id_atendimento": new_ids(n),
        "data": rand_dates(start, end, n),
        "id_paciente": random.choices(dim_paciente["id_paciente"].tolist(), k=n),
        "id_medico": random.choices(dim_medico["id_medico"].tolist(), k=n),
        "id_convenio": random.choices(dim_convenio["id_convenio"].tolist(), k=n),
        "tipo_atendimento": random.choices(tipos_atendimento, k=n),
        "valor_procedimento": rng.uniform(80, 5000, n).round(2),
        "duracao_min": rng.integers(10, 180, n),
    })

    return {
        "DimPaciente": dim_paciente, "DimMedico": dim_medico, "DimConvenio": dim_convenio,
        "FatoAtendimentos": fato, "dCalendario": dcalendario(start, end),
    }


# ============================================================================
# E-COMMERCE
# ============================================================================
def gerar_ecommerce(n: int, start: date, end: date) -> dict:
    n = _cap(n)
    n_clientes = min(n, 3000)
    n_produtos = min(400, n // 4 + 40)

    dim_cliente = pd.DataFrame({
        "id_cliente": new_ids(n_clientes),
        "nome": [fake.name() for _ in range(n_clientes)],
        "email": [fake.email() for _ in range(n_clientes)],
        "uf": random.choices(ESTADOS, k=n_clientes),
    })
    categorias = ["Eletrônicos", "Casa", "Moda", "Livros", "Esporte", "Beleza", "Brinquedos"]
    dim_produto = pd.DataFrame({
        "id_produto": new_ids(n_produtos),
        "nome": [f"{fake.word().capitalize()} {i}" for i in range(1, n_produtos + 1)],
        "categoria": random.choices(categorias, k=n_produtos),
        "preco": rng.uniform(15, 1500, n_produtos).round(2),
    })
    dim_pagamento = pd.DataFrame({
        "id_pagamento_tipo": new_ids(4),
        "metodo": ["Cartão de Crédito", "Pix", "Boleto", "Cartão de Débito"],
    })

    fato = pd.DataFrame({
        "id_pedido": new_ids(n),
        "data": rand_dates(start, end, n),
        "id_cliente": random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "id_produto": random.choices(dim_produto["id_produto"].tolist(), k=n),
        "id_pagamento_tipo": random.choices(dim_pagamento["id_pagamento_tipo"].tolist(), k=n),
        "quantidade": rng.integers(1, 6, n),
        "frete": rng.uniform(0, 60, n).round(2),
        "status_pedido": random.choices(
            ["Entregue", "Em trânsito", "Processando", "Cancelado"], k=n, weights=[70, 15, 10, 5]
        ),
    })
    fato["valor_total"] = (
        fato["quantidade"] * fato["id_produto"].map(dim_produto.set_index("id_produto")["preco"]) + fato["frete"]
    ).round(2)

    return {
        "DimCliente": dim_cliente, "DimProduto": dim_produto, "DimPagamento": dim_pagamento,
        "FatoPedidos": fato, "dCalendario": dcalendario(start, end),
    }


# ============================================================================
# LOGÍSTICA
# ============================================================================
def gerar_logistica(n: int, start: date, end: date) -> dict:
    n = _cap(n)
    n_clientes = min(n, 2000)
    n_transportadoras = 15
    n_motoristas = 50

    dim_cliente = pd.DataFrame({
        "id_cliente": new_ids(n_clientes),
        "nome": [fake.company() for _ in range(n_clientes)],
        "uf_destino": random.choices(ESTADOS, k=n_clientes),
    })
    dim_transportadora = pd.DataFrame({
        "id_transportadora": new_ids(n_transportadoras),
        "nome": [fake.company() for _ in range(n_transportadoras)],
    })
    dim_motorista = pd.DataFrame({
        "id_motorista": new_ids(n_motoristas),
        "nome": [fake.name() for _ in range(n_motoristas)],
        "id_transportadora": random.choices(dim_transportadora["id_transportadora"].tolist(), k=n_motoristas),
    })

    fato = pd.DataFrame({
        "id_entrega": new_ids(n),
        "data": rand_dates(start, end, n),
        "id_cliente": random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "id_motorista": random.choices(dim_motorista["id_motorista"].tolist(), k=n),
        "distancia_km": rng.uniform(5, 1200, n).round(1),
        "custo_frete": rng.uniform(20, 800, n).round(2),
        "prazo_dias": rng.integers(1, 15, n),
        "status_entrega": random.choices(
            ["Entregue no Prazo", "Entregue com Atraso", "Em Rota", "Extraviado"], k=n, weights=[70, 15, 12, 3]
        ),
    })

    return {
        "DimCliente": dim_cliente, "DimTransportadora": dim_transportadora, "DimMotorista": dim_motorista,
        "FatoEntregas": fato, "dCalendario": dcalendario(start, end),
    }


# ============================================================================
# EDUCAÇÃO
# ============================================================================
def gerar_educacao(n: int, start: date, end: date) -> dict:
    n = _cap(n)
    n_alunos = min(n, 2500)
    n_cursos = 30
    n_instrutores = 20

    dim_aluno = pd.DataFrame({
        "id_aluno": new_ids(n_alunos),
        "nome": [fake.name() for _ in range(n_alunos)],
        "idade": rng.integers(16, 55, n_alunos),
        "uf": random.choices(ESTADOS, k=n_alunos),
    })
    areas = ["Tecnologia", "Negócios", "Design", "Marketing", "Dados", "Idiomas"]
    dim_curso = pd.DataFrame({
        "id_curso": new_ids(n_cursos),
        "nome": [f"Curso de {fake.word().capitalize()}" for _ in range(n_cursos)],
        "area": random.choices(areas, k=n_cursos),
        "carga_horaria": rng.integers(10, 200, n_cursos),
    })
    dim_instrutor = pd.DataFrame({
        "id_instrutor": new_ids(n_instrutores),
        "nome": [fake.name() for _ in range(n_instrutores)],
    })

    fato = pd.DataFrame({
        "id_matricula": new_ids(n),
        "data_matricula": rand_dates(start, end, n),
        "id_aluno": random.choices(dim_aluno["id_aluno"].tolist(), k=n),
        "id_curso": random.choices(dim_curso["id_curso"].tolist(), k=n),
        "id_instrutor": random.choices(dim_instrutor["id_instrutor"].tolist(), k=n),
        "valor_pago": rng.uniform(50, 2500, n).round(2),
        "percentual_conclusao": rng.uniform(0, 100, n).round(1),
        "nota_final": rng.uniform(0, 10, n).round(1),
    })

    return {
        "DimAluno": dim_aluno, "DimCurso": dim_curso, "DimInstrutor": dim_instrutor,
        "FatoMatriculas": fato, "dCalendario": dcalendario(start, end),
    }


# ============================================================================
# IMOBILIÁRIO
# ============================================================================
def gerar_imobiliario(n: int, start: date, end: date) -> dict:
    n = _cap(n)
    n_corretores = 30
    n_imoveis = min(500, n // 3 + 50)

    dim_corretor = pd.DataFrame({
        "id_corretor": new_ids(n_corretores),
        "nome": [fake.name() for _ in range(n_corretores)],
    })
    tipos_imovel = ["Apartamento", "Casa", "Terreno", "Comercial", "Cobertura"]
    dim_imovel = pd.DataFrame({
        "id_imovel": new_ids(n_imoveis),
        "tipo": random.choices(tipos_imovel, k=n_imoveis),
        "uf": random.choices(ESTADOS, k=n_imoveis),
        "area_m2": rng.uniform(35, 400, n_imoveis).round(1),
        "valor_anuncio": rng.uniform(120_000, 3_000_000, n_imoveis).round(2),
    })

    fato = pd.DataFrame({
        "id_transacao": new_ids(n),
        "data": rand_dates(start, end, n),
        "id_imovel": random.choices(dim_imovel["id_imovel"].tolist(), k=n),
        "id_corretor": random.choices(dim_corretor["id_corretor"].tolist(), k=n),
        "tipo_transacao": random.choices(["Venda", "Aluguel"], k=n, weights=[40, 60]),
        "valor_negociado": rng.uniform(1500, 2_800_000, n).round(2),
        "comissao_pct": rng.uniform(3, 8, n).round(2),
    })

    return {
        "DimCorretor": dim_corretor, "DimImovel": dim_imovel,
        "FatoTransacoes": fato, "dCalendario": dcalendario(start, end),
    }


# ============================================================================
# SAAS B2B
# ============================================================================
def gerar_saas_b2b(n: int, start: date, end: date) -> dict:
    n = _cap(n)
    n_clientes = min(n, 1500)
    n_planos = 4

    dim_cliente = pd.DataFrame({
        "id_cliente": new_ids(n_clientes),
        "nome_empresa": [fake.company() for _ in range(n_clientes)],
        "segmento": random.choices(["Startup", "PME", "Enterprise"], k=n_clientes),
        "uf": random.choices(ESTADOS, k=n_clientes),
    })
    dim_plano = pd.DataFrame({
        "id_plano": new_ids(n_planos),
        "nome_plano": ["Free", "Starter", "Pro", "Enterprise"],
        "mrr_base": [0, 99, 299, 999],
    })

    fato = pd.DataFrame({
        "id_assinatura": new_ids(n),
        "data_evento": rand_dates(start, end, n),
        "id_cliente": random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "id_plano": random.choices(dim_plano["id_plano"].tolist(), k=n),
        "tipo_evento": random.choices(
            ["Nova Assinatura", "Upgrade", "Downgrade", "Churn", "Renovação"], k=n, weights=[20, 15, 10, 10, 45]
        ),
        "mrr": rng.uniform(0, 1500, n).round(2),
        "nps": rng.integers(0, 11, n),
    })

    return {
        "DimCliente": dim_cliente, "DimPlano": dim_plano,
        "FatoAssinaturas": fato, "dCalendario": dcalendario(start, end),
    }


# ============================================================================
# REGISTRO DE SETORES
# ============================================================================
SETORES = {
    "🛒 Varejo": gerar_varejo,
    "💰 Financeiro": gerar_financeiro,
    "🏥 Saúde": gerar_saude,
    "🏪 E-commerce": gerar_ecommerce,
    "🚚 Logística": gerar_logistica,
    "📚 Educação": gerar_educacao,
    "🏠 Imobiliário": gerar_imobiliario,
    "☁️ SaaS B2B": gerar_saas_b2b,
}

# Relacionamentos declarados (para exibir o diagrama/estrela na tela)
# Formato: "NomeSetor": [("FatoX", "coluna_fk", "DimY", "coluna_pk"), ...]
RELACIONAMENTOS = {
    "🛒 Varejo": [
        ("FatoVendas", "id_cliente", "DimCliente", "id_cliente"),
        ("FatoVendas", "id_produto", "DimProduto", "id_produto"),
        ("FatoVendas", "id_vendedor", "DimVendedor", "id_vendedor"),
        ("FatoVendas", "id_filial", "DimFilial", "id_filial"),
    ],
    "💰 Financeiro": [
        ("FatoTransacoes", "id_conta", "DimConta", "id_conta"),
        ("DimConta", "id_cliente", "DimCliente", "id_cliente"),
        ("DimConta", "id_agencia", "DimAgencia", "id_agencia"),
    ],
    "🏥 Saúde": [
        ("FatoAtendimentos", "id_paciente", "DimPaciente", "id_paciente"),
        ("FatoAtendimentos", "id_medico", "DimMedico", "id_medico"),
        ("FatoAtendimentos", "id_convenio", "DimConvenio", "id_convenio"),
    ],
    "🏪 E-commerce": [
        ("FatoPedidos", "id_cliente", "DimCliente", "id_cliente"),
        ("FatoPedidos", "id_produto", "DimProduto", "id_produto"),
        ("FatoPedidos", "id_pagamento_tipo", "DimPagamento", "id_pagamento_tipo"),
    ],
    "🚚 Logística": [
        ("FatoEntregas", "id_cliente", "DimCliente", "id_cliente"),
        ("FatoEntregas", "id_motorista", "DimMotorista", "id_motorista"),
        ("DimMotorista", "id_transportadora", "DimTransportadora", "id_transportadora"),
    ],
    "📚 Educação": [
        ("FatoMatriculas", "id_aluno", "DimAluno", "id_aluno"),
        ("FatoMatriculas", "id_curso", "DimCurso", "id_curso"),
        ("FatoMatriculas", "id_instrutor", "DimInstrutor", "id_instrutor"),
    ],
    "🏠 Imobiliário": [
        ("FatoTransacoes", "id_imovel", "DimImovel", "id_imovel"),
        ("FatoTransacoes", "id_corretor", "DimCorretor", "id_corretor"),
    ],
    "☁️ SaaS B2B": [
        ("FatoAssinaturas", "id_cliente", "DimCliente", "id_cliente"),
        ("FatoAssinaturas", "id_plano", "DimPlano", "id_plano"),
    ],
}
