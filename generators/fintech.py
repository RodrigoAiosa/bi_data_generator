import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .helpers import new_ids, dcalendario, rand_dates

def gerar_fintech(n_linhas: int, start_date, end_date) -> dict[str, pd.DataFrame]:
    """
    Gera dados do setor de Fintech/Pagamentos (Star Schema)
    
    Tabelas geradas:
    - FatoTransacao: Transações financeiras
    - DimUsuario: Usuários/clientes da fintech
    - DimCartao: Cartões vinculados aos usuários
    - DimComerciante: Estabelecimentos que recebem pagamentos
    - DimDispositivo: Dispositivos usados nas transações
    - DimAntifraude: Níveis de risco e scores
    - dCalendario: Tabela calendário
    """
    # Converte para datetime se necessário
    if isinstance(start_date, str):
        start = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        start = start_date
    
    if isinstance(end_date, str):
        end = datetime.strptime(end_date, "%Y-%m-%d")
    else:
        end = end_date
    
    # ========== DIMENSÕES ==========
    
    # DimUsuario (1000-5000 usuários)
    n_usuarios = min(5000, max(1000, n_linhas // 10))
    usuario_ids = new_ids(n_usuarios, "USR")
    
    # Geração de dados demográficos
    estados = ["SP", "RJ", "MG", "RS", "BA", "PR", "PE", "CE", "SC", "GO", "DF", "ES", "AM", "PA", "MA"]
    
    dim_usuario = pd.DataFrame({
        "sk_usuario": usuario_ids,
        "id_usuario": usuario_ids,
        "nome": [f"Usuário {i+1}" for i in range(n_usuarios)],
        "cpf": [f"{np.random.randint(100,999)}.{np.random.randint(100,999)}.{np.random.randint(100,999)}-{np.random.randint(10,99)}" 
                for _ in range(n_usuarios)],
        "data_nascimento": rand_dates(start - timedelta(days=365*60), start - timedelta(days=365*18), n_usuarios),
        "sexo": np.random.choice(["M", "F", "Prefiro não informar"], n_usuarios, p=[0.48, 0.48, 0.04]),
        "estado": np.random.choice(estados, n_usuarios),
        "cidade": [f"Cidade {np.random.randint(1,50)}" for _ in range(n_usuarios)],
        "renda_mensal": np.random.uniform(1000, 20000, n_usuarios).round(2),
        "score_credito": np.random.randint(300, 1000, n_usuarios),
        "data_cadastro": rand_dates(start - timedelta(days=1095), start, n_usuarios),
        "status_conta": np.random.choice(["Ativa", "Bloqueada", "Suspensa", "Encerrada"], n_usuarios, p=[0.85, 0.08, 0.05, 0.02])
    })
    
    # DimCartao (0.8-1.8 cartões por usuário)
    n_cartoes = int(n_usuarios * np.random.uniform(0.8, 1.8))
    cartao_ids = new_ids(n_cartoes, "CAR")
    
    bandeiras = ["Visa", "Mastercard", "Elo", "American Express", "Hipercard", "Diners"]
    tipos_cartao = ["Débito", "Crédito", "Pré-pago", "Corporate", "Virtual"]
    
    # Associar cartões a usuários (um usuário pode ter múltiplos cartões)
    usuario_cartao = np.random.choice(usuario_ids, n_cartoes)
    
    # Data de validade (2-5 anos a partir da emissão)
    data_emissao = rand_dates(start - timedelta(days=730), start, n_cartoes)
    data_validade = [de + timedelta(days=np.random.randint(730, 1825)) for de in data_emissao]
    
    dim_cartao = pd.DataFrame({
        "sk_cartao": cartao_ids,
        "id_cartao": cartao_ids,
        "sk_usuario": usuario_cartao,
        "bandeira": np.random.choice(bandeiras, n_cartoes, p=[0.32, 0.32, 0.18, 0.08, 0.05, 0.05]),
        "tipo": np.random.choice(tipos_cartao, n_cartoes, p=[0.35, 0.45, 0.1, 0.05, 0.05]),
        "limite": np.random.uniform(500, 50000, n_cartoes).round(2),
        "limite_utilizado": np.random.uniform(0, 1, n_cartoes).round(2),
        "data_emissao": data_emissao,
        "data_validade": data_validade,
        "cvv": [np.random.randint(100, 999) for _ in range(n_cartoes)],
        "ativo": np.random.choice([True, False], n_cartoes, p=[0.88, 0.12]),
        "bloqueado_temporario": np.random.choice([True, False], n_cartoes, p=[0.05, 0.95])
    })
    
    # DimComerciante (200-1000 comerciantes)
    n_comerciantes = min(1000, max(200, n_linhas // 20))
    comerciante_ids = new_ids(n_comerciantes, "COM")
    
    categorias_comercio = [
        "Alimentação", "Varejo", "Serviços", "Transporte", "Saúde", 
        "Educação", "Entretenimento", "Viagem", "Tecnologia", "Beleza",
        "Construção", "Automotivo", "Imobiliário", "Financeiro", "Telecomunicações"
    ]
    
    portes = ["Pequeno", "Médio", "Grande"]
    volumes_venda = ["Baixo", "Médio", "Alto"]
    
    dim_comerciante = pd.DataFrame({
        "sk_comerciante": comerciante_ids,
        "id_comerciante": comerciante_ids,
        "nome_fantasia": [f"Comerciante {i+1}" for i in range(n_comerciantes)],
        "razao_social": [f"Empresa {i+1} LTDA" for i in range(n_comerciantes)],
        "cnpj": [f"{np.random.randint(10,99)}.{np.random.randint(100,999)}.{np.random.randint(100,999)}/{np.random.randint(1000,9999)}-{np.random.randint(10,99)}" 
                 for _ in range(n_comerciantes)],
        "categoria": np.random.choice(categorias_comercio, n_comerciantes),
        "porte": np.random.choice(portes, n_comerciantes, p=[0.5, 0.35, 0.15]),
        "volume_venda_mensal": np.random.choice(volumes_venda, n_comerciantes, p=[0.3, 0.45, 0.25]),
        "cidade": np.random.choice(["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Brasília", "Salvador", 
                                    "Recife", "Porto Alegre", "Curitiba", "Fortaleza", "Manaus"], n_comerciantes),
        "data_cadastro": rand_dates(start - timedelta(days=1095), start, n_comerciantes),
        "status": np.random.choice(["Ativo", "Inativo", "Suspenso"], n_comerciantes, p=[0.85, 0.1, 0.05])
    })
    
    # DimDispositivo
    dispositivos = ["Web - Desktop", "Web - Mobile", "App iOS", "App Android", "API", "POS Físico", "POS Virtual"]
    sistemas = ["Windows", "macOS", "Linux", "iOS", "Android", "Proprietário", "Outro"]
    
    dim_dispositivo = pd.DataFrame({
        "sk_dispositivo": new_ids(len(dispositivos), "DIS"),
        "tipo_dispositivo": dispositivos,
        "sistema_operacional": sistemas,
        "navegador": np.random.choice(["Chrome", "Safari", "Firefox", "Edge", "Outro", "N/A"], len(dispositivos)),
        "versao_app": [f"{np.random.randint(1,5)}.{np.random.randint(0,9)}.{np.random.randint(0,9)}" for _ in range(len(dispositivos))]
    })
    
    # DimAntifraude
    niveis_risco = ["Baixo", "Médio", "Alto", "Crítico"]
    cores_risco = ["Verde", "Amarelo", "Laranja", "Vermelho"]
    
    dim_antifraude = pd.DataFrame({
        "sk_antifraude": new_ids(len(niveis_risco), "RIS"),
        "nivel_risco": niveis_risco,
        "cor_risco": cores_risco,
        "score_minimo": [0, 30, 60, 85],
        "score_maximo": [29, 59, 84, 100],
        "acao_padrao": ["Aprovar automaticamente", "Análise simples", "Análise rigorosa", "Bloquear transação"],
        "tempo_analise_segundos": [1, 30, 300, 600]
    })
    
    # ========== TABELA FATO ==========
    # Gerar transações
    
    datas_transacao = rand_dates(start, end, n_linhas)
    horas = np.random.randint(0, 24, n_linhas)
    minutos = np.random.randint(0, 60, n_linhas)
    segundos = np.random.randint(0, 60, n_linhas)
    data_hora = [datetime.combine(d, datetime.min.time()) + timedelta(hours=h, minutes=m, seconds=s) 
                 for d, h, m, s in zip(datas_transacao, horas, minutos, segundos)]
    
    # Selecionar chaves estrangeiras
    usuario_keys = np.random.choice(dim_usuario["sk_usuario"], n_linhas)
    
    # Selecionar cartão válido para o usuário (apenas cartões ativos)
    cartao_keys = []
    for uk in usuario_keys:
        cartoes_usuario = dim_cartao[(dim_cartao["sk_usuario"] == uk) & (dim_cartao["ativo"] == True)]["sk_cartao"].tolist()
        if cartoes_usuario:
            cartao_keys.append(np.random.choice(cartoes_usuario))
        else:
            cartao_keys.append(np.random.choice(dim_cartao["sk_cartao"]))
    
    comerciante_keys = np.random.choice(dim_comerciante["sk_comerciante"], n_linhas)
    dispositivo_keys = np.random.choice(dim_dispositivo["sk_dispositivo"], n_linhas)
    
    # Distribuição de risco (a maioria das transações é baixo risco)
    risco_keys = np.random.choice(dim_antifraude["sk_antifraude"], n_linhas, p=[0.65, 0.2, 0.1, 0.05])
    
    # Valores da transação
    valor = np.random.uniform(1, 5000, n_linhas).round(2)
    
    # Parcelamento (0 = à vista)
    parcelas = np.random.choice([0, 1, 2, 3, 4, 5, 6, 8, 10, 12], n_linhas, 
                                p=[0.45, 0.2, 0.1, 0.05, 0.04, 0.03, 0.03, 0.04, 0.03, 0.03])
    
    # Juros (apenas para parcelado)
    juros = [round(np.random.uniform(0, 0.06), 3) if p > 1 else 0 for p in parcelas]
    valor_com_juros = [round(v * (1 + j), 2) for v, j in zip(valor, juros)]
    
    # Taxa da máquina (1-5% dependendo do tipo de cartão e bandeira)
    taxa_maquina = np.random.uniform(0.01, 0.05, n_linhas).round(3)
    valor_taxa = [round(v * tm, 2) for v, tm in zip(valor_com_juros, taxa_maquina)]
    
    # Valor líquido para o comerciante
    valor_liquido_comerciante = [round(vcj - vt, 2) for vcj, vt in zip(valor_com_juros, valor_taxa)]
    
    # Cashback para o usuário (0-2%)
    cashback_percent = np.random.uniform(0, 0.02, n_linhas).round(3)
    cashback_valor = [round(v * cp, 2) for v, cp in zip(valor, cashback_percent)]
    
    # Status da transação
    status = np.random.choice(
        ["Aprovada", "Recusada", "Cancelada", "Estornada", "Em análise", "Chargeback"],
        n_linhas,
        p=[0.82, 0.08, 0.03, 0.02, 0.03, 0.02]
    )
    
    # Motivo da recusa (se aplicável)
    motivos_recusa = [
        "Saldo insuficiente", 
        "Cartão bloqueado", 
        "Limite excedido", 
        "Transação suspeita", 
        "Dados incorretos",
        "Cartão vencido",
        "Estabelecimento não autorizado",
        "Valor acima do permitido"
    ]
    motivo_recusa = [np.random.choice(motivos_recusa) if s == "Recusada" else None for s in status]
    
    # Latitude/Longitude da transação (para geolocalização)
    capitais_lat = [-23.5505, -22.9068, -19.9167, -15.7801, -12.9714, -8.0476, -30.0346, -25.4284, -3.7319, -27.5945]
    capitais_lon = [-46.6333, -43.1729, -43.9345, -47.9292, -38.5014, -34.8770, -51.2177, -49.2719, -38.5267, -48.5478]
    
    idx_capital = np.random.randint(0, len(capitais_lat), n_linhas)
    latitude = [capitais_lat[i] + np.random.uniform(-0.5, 0.5) for i in idx_capital]
    longitude = [capitais_lon[i] + np.random.uniform(-0.5, 0.5) for i in idx_capital]
    
    # Tempo de processamento da transação (ms)
    tempo_processamento_ms = np.random.randint(50, 3000, n_linhas)
    
    # Flag de notificação push enviada
    notificacao_enviada = np.random.choice([True, False], n_linhas, p=[0.85, 0.15])
    
    fato_transacao = pd.DataFrame({
        "sk_transacao": new_ids(n_linhas, "TRA"),
        "data_hora": data_hora,
        "ano": [dh.year for dh in data_hora],
        "mes": [dh.month for dh in data_hora],
        "dia_semana": [dh.weekday() for dh in data_hora],
        "hora": [dh.hour for dh in data_hora],
        "valor": valor,
        "parcelas": parcelas,
        "juros_aplicado": juros,
        "valor_com_juros": valor_com_juros,
        "taxa_maquina": taxa_maquina,
        "valor_taxa": valor_taxa,
        "valor_liquido_comerciante": valor_liquido_comerciante,
        "cashback_percent": cashback_percent,
        "cashback_valor": cashback_valor,
        "status": status,
        "motivo_recusa": motivo_recusa,
        "tempo_processamento_ms": tempo_processamento_ms,
        "latitude": [round(lat, 6) for lat in latitude],
        "longitude": [round(lon, 6) for lon in longitude],
        "notificacao_enviada": notificacao_enviada,
        "sk_usuario": usuario_keys,
        "sk_cartao": cartao_keys,
        "sk_comerciante": comerciante_keys,
        "sk_dispositivo": dispositivo_keys,
        "sk_antifraude": risco_keys
    })
    
    return {
        "FatoTransacao": fato_transacao,
        "DimUsuario": dim_usuario,
        "DimCartao": dim_cartao,
        "DimComerciante": dim_comerciante,
        "DimDispositivo": dim_dispositivo,
        "DimAntifraude": dim_antifraude,
        "dCalendario": dcalendario(start, end)
    }
