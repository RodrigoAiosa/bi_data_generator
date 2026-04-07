import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .helpers import new_ids, dcalendario, rand_dates

def gerar_mobilidade(n_linhas: int, start_date, end_date) -> dict[str, pd.DataFrame]:
    """
    Gera dados do setor de Mobilidade/Transporte (Star Schema)
    
    Tabelas geradas:
    - FatoViagem: Viagens realizadas
    - DimMotorista: Motoristas cadastrados
    - DimPassageiro: Passageiros/usuários
    - DimVeiculo: Veículos da frota
    - DimRota: Rotas e trajetos
    - DimPagamento: Métodos de pagamento
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
    
    # DimMotorista (200-1000 motoristas)
    n_motoristas = min(1000, max(200, n_linhas // 15))
    motorista_ids = new_ids(n_motoristas, "MOT")
    
    dim_motorista = pd.DataFrame({
        "sk_motorista": motorista_ids,
        "id_motorista": motorista_ids,
        "nome": [f"Motorista {i+1}" for i in range(n_motoristas)],
        "cpf": [f"{np.random.randint(100,999)}.{np.random.randint(100,999)}.{np.random.randint(100,999)}-{np.random.randint(10,99)}" 
                for _ in range(n_motoristas)],
        "cnh": [f"{np.random.randint(10,99)}.{np.random.randint(100,999)}.{np.random.randint(100,999)}" 
                for _ in range(n_motoristas)],
        "categoria_cnh": np.random.choice(["B", "C", "D", "E"], n_motoristas, p=[0.7, 0.15, 0.1, 0.05]),
        "data_contratacao": rand_dates(start - timedelta(days=1095), start, n_motoristas),
        "avaliacao_media": np.random.uniform(3, 5, n_motoristas).round(1),
        "total_viagens": np.random.randint(10, 500, n_motoristas),
        "status": np.random.choice(["Ativo", "Inativo", "Férias", "Bloqueado"], n_motoristas, p=[0.85, 0.08, 0.05, 0.02])
    })
    
    # DimPassageiro (1000-5000 passageiros)
    n_passageiros = min(5000, max(1000, n_linhas // 5))
    passageiro_ids = new_ids(n_passageiros, "PAS")
    
    dim_passageiro = pd.DataFrame({
        "sk_passageiro": passageiro_ids,
        "id_passageiro": passageiro_ids,
        "nome": [f"Passageiro {i+1}" for i in range(n_passageiros)],
        "telefone": [f"({np.random.randint(11,99)}) 9{np.random.randint(1000,9999)}-{np.random.randint(1000,9999)}" 
                     for _ in range(n_passageiros)],
        "email": [f"passageiro{i+1}@email.com" for i in range(n_passageiros)],
        "data_cadastro": rand_dates(start - timedelta(days=365), start, n_passageiros),
        "viagens_totais": np.random.randint(0, 100, n_passageiros),
        "avaliacao_media": np.random.uniform(3, 5, n_passageiros).round(1),
        "tipo_usuario": np.random.choice(["Ocasional", "Frequente", "Corporativo", "Premium"], n_passageiros,
                                          p=[0.5, 0.3, 0.15, 0.05])
    })
    
    # DimVeiculo (100-500 veículos)
    n_veiculos = min(500, max(100, n_linhas // 30))
    veiculo_ids = new_ids(n_veiculos, "VEI")
    
    marcas = ["Fiat", "Volkswagen", "Chevrolet", "Hyundai", "Toyota", "Renault", "Honda", "Ford", "Nissan", "Jeep"]
    modelos = ["Uno", "Gol", "Onix", "HB20", "Corolla", "Kwid", "Civic", "Ka", "Argo", "Creta"]
    tipos = ["Econômico", "Conforto", "Premium", "Van", "Moto", "Executivo", "SUV"]
    cores = ["Branco", "Preto", "Prata", "Vermelho", "Azul", "Cinza", "Verde", "Amarelo"]
    
    dim_veiculo = pd.DataFrame({
        "sk_veiculo": veiculo_ids,
        "placa": [f"{chr(np.random.randint(65,91))}{chr(np.random.randint(65,91))}{chr(np.random.randint(65,91))}-{np.random.randint(1000,9999)}" 
                  for _ in range(n_veiculos)],
        "marca": np.random.choice(marcas, n_veiculos),
        "modelo": np.random.choice(modelos, n_veiculos),
        "ano": np.random.randint(2018, 2025, n_veiculos),
        "cor": np.random.choice(cores, n_veiculos),
        "tipo": np.random.choice(tipos, n_veiculos, p=[0.35, 0.25, 0.1, 0.05, 0.05, 0.1, 0.1]),
        "km_rodados": np.random.randint(10000, 150000, n_veiculos),
        "capacidade": np.random.choice([4, 5, 6, 7, 8, 15], n_veiculos, p=[0.5, 0.3, 0.08, 0.05, 0.04, 0.03]),
        "status": np.random.choice(["Disponível", "Em viagem", "Manutenção", "Aposentado"], n_veiculos,
                                   p=[0.7, 0.2, 0.07, 0.03])
    })
    
    # DimRota (50-200 rotas)
    cidades = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Brasília", "Salvador", 
               "Recife", "Porto Alegre", "Curitiba", "Fortaleza", "Manaus", "Goiânia", "Belém"]
    
    bairros_sp = ["Centro", "Jardins", "Moema", "Brooklin", "Vila Olímpia", "Pinheiros", "Consolação", "Liberdade"]
    bairros_rj = ["Centro", "Copacabana", "Ipanema", "Barra", "Tijuca", "Botafogo", "Flamengo"]
    
    rotas = []
    for i in range(100):
        cidade = np.random.choice(cidades)
        if cidade == "São Paulo":
            origem = np.random.choice(bairros_sp)
            destino = np.random.choice(bairros_sp)
        elif cidade == "Rio de Janeiro":
            origem = np.random.choice(bairros_rj)
            destino = np.random.choice(bairros_rj)
        else:
            origem = f"Bairro {np.random.randint(1,30)}"
            destino = f"Bairro {np.random.randint(1,30)}"
        
        rotas.append({
            "sk_rota": f"ROTA{i+1:03d}",
            "cidade": cidade,
            "origem": origem,
            "destino": destino,
            "distancia_km": round(np.random.uniform(2, 50), 1),
            "tempo_medio_min": np.random.randint(10, 120),
            "nivel_transito": np.random.choice(["Baixo", "Médio", "Alto"], p=[0.3, 0.5, 0.2])
        })
    dim_rota = pd.DataFrame(rotas)
    
    # DimPagamento
    metodos = ["Dinheiro", "Cartão Crédito", "Cartão Débito", "PIX", "Vale Transporte", "App", "Saldo da Conta"]
    
    dim_pagamento = pd.DataFrame({
        "sk_pagamento": new_ids(len(metodos), "PAG"),
        "metodo": metodos,
        "taxa_servico": [0.0, 0.03, 0.03, 0.0, 0.0, 0.05, 0.0],
        "tempo_confirmacao": np.random.choice([1, 2, 3, 5, 10], len(metodos))
    })
    
    # ========== TABELA FATO ==========
    # Gerar viagens
    
    datas_viagem = rand_dates(start, end, n_linhas)
    
    # CORREÇÃO: Converter horas e minutos para inteiros e validar
    horas = np.random.randint(0, 24, n_linhas)
    minutos = np.random.randint(0, 60, n_linhas)
    
    # CORREÇÃO: Garantir que horas e minutos são inteiros e dentro do intervalo válido
    # Esta é a linha que estava causando o erro - agora com validação
    data_hora_inicio = []
    for d, h, m in zip(datas_viagem, horas, minutos):
        # Validar e converter para inteiro
        try:
            h_int = int(h) if h is not None else 0
            m_int = int(m) if m is not None else 0
            
            # Garantir valores dentro do intervalo válido
            h_int = max(0, min(23, h_int))
            m_int = max(0, min(59, m_int))
            
            data_hora_inicio.append(datetime.combine(d, datetime.min.time()) + timedelta(hours=h_int, minutes=m_int))
        except (TypeError, ValueError) as e:
            # Fallback em caso de erro: usar meia-noite
            data_hora_inicio.append(datetime.combine(d, datetime.min.time()))
    
    # Selecionar chaves estrangeiras
    motorista_keys = np.random.choice(dim_motorista["sk_motorista"], n_linhas)
    passageiro_keys = np.random.choice(dim_passageiro["sk_passageiro"], n_linhas)
    veiculo_keys = np.random.choice(dim_veiculo["sk_veiculo"], n_linhas)
    rota_keys = np.random.choice(dim_rota["sk_rota"], n_linhas)
    pagamento_keys = np.random.choice(dim_pagamento["sk_pagamento"], n_linhas)
    
    # Calcular valores
    distancias = dim_rota.set_index("sk_rota")["distancia_km"].to_dict()
    tempos = dim_rota.set_index("sk_rota")["tempo_medio_min"].to_dict()
    
    distancia_km = [distancias.get(rk, 10) for rk in rota_keys]
    tempo_previsto = [tempos.get(rk, 30) for rk in rota_keys]
    
    # Tempo real (com variação)
    tempo_real = [int(t * np.random.uniform(0.8, 1.5)) for t in tempo_previsto]
    data_hora_fim = [dh + timedelta(minutes=tr) for dh, tr in zip(data_hora_inicio, tempo_real)]
    
    # Tarifa base (R$ 2.00 por km + R$ 0.40 por minuto + R$ 2.50 bandeirada)
    bandeirada = 2.50
    valor_base = [bandeirada + (d * 2.0) + (t * 0.4) for d, t in zip(distancia_km, tempo_real)]
    
    # Bandeira (1.0 = normal, 1.2 = bandeira 2, 1.4 = bandeira 3)
    bandeira = np.random.choice([1.0, 1.2, 1.4], n_linhas, p=[0.7, 0.25, 0.05])
    valor_bandeira = [vb * b for vb, b in zip(valor_base, bandeira)]
    
    # Taxa de serviço da plataforma
    taxas = dim_pagamento.set_index("sk_pagamento")["taxa_servico"].to_dict()
    taxa_servico = [vb * taxas.get(pk, 0) for vb, pk in zip(valor_bandeira, pagamento_keys)]
    
    valor_liquido_motorista = [vb - ts for vb, ts in zip(valor_bandeira, taxa_servico)]
    
    # Gorjeta (0-30% do valor)
    gorjeta_percent = np.random.uniform(0, 0.3, n_linhas).round(2)
    gorjeta_valor = [vb * gp for vb, gp in zip(valor_bandeira, gorjeta_percent)]
    
    valor_total = [vb + gv for vb, gv in zip(valor_bandeira, gorjeta_valor)]
    
    # Status da viagem
    status = np.random.choice(["Concluída", "Cancelada pelo motorista", "Cancelada pelo passageiro", 
                               "Em andamento", "Não encontrado"], n_linhas, 
                               p=[0.75, 0.05, 0.08, 0.07, 0.05])
    
    # Avaliação do passageiro (1-5)
    avaliacao_passageiro = [np.random.randint(1, 6) if s == "Concluída" and np.random.random() < 0.7 else None 
                            for s in status]
    
    # Avaliação do motorista (1-5)
    avaliacao_motorista = [np.random.randint(1, 6) if s == "Concluída" and np.random.random() < 0.6 else None 
                           for s in status]
    
    fato_viagem = pd.DataFrame({
        "sk_viagem": new_ids(n_linhas, "VIA"),
        "data_hora_inicio": data_hora_inicio,
        "data_hora_fim": data_hora_fim,
        "distancia_km": [round(d, 1) for d in distancia_km],
        "tempo_previsto_min": tempo_previsto,
        "tempo_real_min": tempo_real,
        "bandeira": bandeira,
        "bandeirada": bandeirada,
        "valor_base": [round(vb, 2) for vb in valor_base],
        "valor_bandeira": [round(vb, 2) for vb in valor_bandeira],
        "taxa_servico": [round(ts, 2) for ts in taxa_servico],
        "gorjeta_percentual": gorjeta_percent,
        "gorjeta_valor": [round(gv, 2) for gv in gorjeta_valor],
        "valor_total": [round(vt, 2) for vt in valor_total],
        "valor_liquido_motorista": [round(vlm, 2) for vlm in valor_liquido_motorista],
        "status": status,
        "avaliacao_passageiro": avaliacao_passageiro,
        "avaliacao_motorista": avaliacao_motorista,
        "sk_motorista": motorista_keys,
        "sk_passageiro": passageiro_keys,
        "sk_veiculo": veiculo_keys,
        "sk_rota": rota_keys,
        "sk_pagamento": pagamento_keys
    })
    
    return {
        "FatoViagem": fato_viagem,
        "DimMotorista": dim_motorista,
        "DimPassageiro": dim_passageiro,
        "DimVeiculo": dim_veiculo,
        "DimRota": dim_rota,
        "DimPagamento": dim_pagamento,
        "dCalendario": dcalendario(start, end)
    }
