import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .helpers import new_ids, dcalendario, rand_dates

def gerar_fintech(n_linhas: int, start_date: str, end_date: str) -> dict[str, pd.DataFrame]:
    """
    Gera dados do setor de Fintech/Pagamentos (Star Schema)
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    # ========== DIMENSÕES ==========
    
    # DimUsuario (1000-5000 usuários)
    n_usuarios = min(5000, max(1000, n_linhas // 10))
    usuario_ids = new_ids(n_usuarios, "USR")
    
    dim_usuario = pd.DataFrame({
        "sk_usuario": usuario_ids,
        "id_usuario": usuario_ids,
        "nome": [f"Usuário {i+1}" for i in range(n_usuarios)],
        "cpf": [f"{np.random.randint(100,999)}.{np.random.randint(100,999)}.{np.random.randint(100,999)}-{np.random.randint(10,99)}" 
                for _ in range(n_usuarios)],
        "data_nascimento": rand_dates(start - timedelta(days=365*60), start - timedelta(days=365*18), n_usuarios),
        "renda_mensal": np.random.uniform(1000, 20000, n_usuarios).round(2),
        "score_credito": np.random.randint(300, 1000, n_usuarios),
        "data_cadastro": rand_dates(start - timedelta(days=1095), start, n_usuarios)
    })
    
    # DimCartao (0.5-2 cartões por usuário)
    n_cartoes = int(n_usuarios * np.random.uniform(0.8, 1.5))
    cartao_ids = new_ids(n_cartoes, "CAR")
    
    bandeiras = ["Visa", "Mastercard", "Elo", "American Express", "Hipercard"]
    tipos_cartao = ["Débito", "Crédito", "Pré-pago", "Corporate"]
    
    # Associar cartões a usuários
    usuario_cartao = np.random.choice(usuario_ids, n_cartoes)
    
    dim_cartao = pd.DataFrame({
        "sk_cartao": cartao_ids,
        "id_cartao": cartao_ids,
        "sk_usuario": usuario_cartao,
        "bandeira": np.random.choice(bandeiras, n_cartoes, p=[0.35, 0.35, 0.15, 0.1, 0.05]),
        "tipo": np.random.choice(tipos_cartao, n_cartoes, p=[0.4, 0.45, 0.1, 0.05]),
        "limite": np.random.uniform(500, 50000, n_cartoes).round(2),
        "data_emissao": rand_dates(start - timedelta(days=730), start, n_cartoes),
        "ativo": np.random.choice([True, False], n_cartoes, p=[0.9, 0.1])
    })
    
    # DimComerciante (200-1000 comerciantes)
    n_comerciantes = min(1000, max(200, n_linhas // 20))
    comerciante_ids = new_ids(n_comerciantes, "COM")
    
    categorias_comercio = ["Alimentação", "Varejo", "Serviços", "Transporte", "Saúde", 
                          "Educação", "Entretenimento", "Viagem", "Tecnologia", "Beleza"]
    
    dim_comerciante = pd.DataFrame({
        "sk_comerciante": comerciante_ids,
        "id_comerciante": comerciante_ids,
        "nome_fantasia": [f"Comerciante {i+1}" for i in range(n_comerciantes)],
        "cnpj": [f"{np.random.randint(10,99)}.{np.random.randint(100,999)}.{np.random.randint(100,999)}/{np.random.randint(1000,9999)}-{np.random.randint(10,99)}" 
                 for _ in range(n_comerciantes)],
        "categoria": np.random.choice(categorias_comercio, n_comerciantes),
        "cidade": np.random.choice(["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Brasília", "Salvador"], n_comerciantes),
        "data_cadastro": rand_dates(start - timedelta(days=1095), start, n_comerciantes)
    })
    
    # DimDispositivo
    dispositivos = ["Web", "App iOS", "App Android", "API", "POS"]
    
    dim_dispositivo = pd.DataFrame({
        "sk_dispositivo": new_ids(len(dispositivos), "DIS"),
        "tipo": dispositivos,
        "navegador": np.random.choice(["Chrome", "Safari", "Firefox", "Edge", "Outro"], len(dispositivos))
    })
    
    # DimAntifraude
    niveis_risco = ["Baixo", "Médio", "Alto", "Crítico"]
    
    dim_antifraude = pd.DataFrame({
        "sk_antifraude": new_ids(len(niveis_risco), "RIS"),
        "nivel_risco": niveis_risco,
        "score_limite": [30, 60, 80, 100],
        "acao_padrao": ["Aprovar", "Analisar", "Bloquear", "Rejeitar"]
    })
    
    # ========== TABELA FATO ==========
    # Gerar transações
    
    datas_transacao = rand_dates(start, end, n_linhas)
    horas = np.random.randint(0, 24, n_linhas)
    minutos = np.random.randint(0, 60, n_linhas)
    data_hora = [datetime.combine(d, datetime.min.time()) + timedelta(hours=h, minutes=m) 
                 for d, h, m in zip(datas_transacao, horas, minutos)]
    
    # Selecionar chaves estrangeiras
    # Usuário pode ter múltiplos cartões
    usuario_keys = np.random.choice(dim_usuario["sk_usuario"], n_linhas)
    
    # Selecionar cartão válido para o usuário
    cartao_keys = []
    for uk in usuario_keys:
        cartoes_usuario = dim_cartao[dim_cartao["sk_usuario"] == uk]["sk_cartao"].tolist()
        if cartoes_usuario:
            cartao_keys.append(np.random.choice(cartoes_usuario))
        else:
            cartao_keys.append(np.random.choice(dim_cartao["sk_cartao"]))
    
    comerciante_keys = np.random.choice(dim_comerciante["sk_comerciante"], n_linhas)
    dispositivo_keys = np.random.choice(dim_dispositivo["sk_dispositivo"], n_linhas)
    risco_keys = np.random.choice(dim_antifraude["sk_antifraude"], n_linhas, p=[0.6, 0.25, 0.1, 0.05])
    
    # Valores da transação
    valor = np.random.uniform(1, 5000, n_linhas).round(2)
    
    # Parcelamento (0 = à vista)
    parcelas = np.random.choice([0, 1, 2, 3, 4, 5, 6, 8, 10, 12], n_linhas, p=[0.5, 0.2, 0.1, 0.05, 0.04, 0.03, 0.03, 0.02, 0.02, 0.01])
    
    # Juros (apenas para parcelado)
    juros = [np.random.uniform(0, 0.05) if p > 1 else 0 for p in parcelas]
    valor_com_juros = [v * (1 + j) for v, j in zip(valor, juros)]
    
    # Taxa
