import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .helpers import new_ids, dcalendario, rand_dates

def gerar_mobilidade(n_linhas: int, start_date: str, end_date: str) -> dict[str, pd.DataFrame]:
    """
    Gera dados do setor de Mobilidade/Transporte (Star Schema)
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    # ========== DIMENSÕES ==========
    
    # DimMotorista (200-1000 motoristas)
    n_motoristas = min(1000, max(200, n_linhas // 15))
    motorista_ids = new_ids(n_motoristas, "MOT")
    
    dim_motorista = pd.DataFrame({
        "sk_motorista": motorista_ids,
        "id_motorista": motorista_ids,
        "nome": [f"Motorista {i+1}" for i in range(n_motoristas)],
        "cnh": [f"{np.random.randint(10,99)}.{np.random.randint(100,999)}.{np.random.randint(100,999)}" 
                for _ in range(n_motoristas)],
        "categoria_cnh": np.random.choice(["B", "C", "D", "E"], n_motoristas, p=[0.7, 0.15, 0.1, 0.05]),
        "data_contratacao": rand_dates(start - timedelta(days=1095), start, n_motoristas),
        "avaliacao_media": np.random.uniform(3, 5, n_motoristas).round(1)
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
        "viagens_totais": np.random.randint(0, 100, n_passageiros)
    })
    
    # DimVeiculo (100-500 veículos)
    n_veiculos = min(500, max(100, n_linhas // 30))
    veiculo_ids = new_ids(n_veiculos, "VEI")
    
    marcas = ["Fiat", "Volkswagen", "Chevrolet", "Hyundai", "Toyota", "Renault", "Honda", "Ford"]
    modelos = ["Uno", "Gol", "Onix", "HB20", "Corolla", "Kwid", "Civic", "Ka"]
    tipos = ["Econômico", "Conforto", "Premium", "Van", "Moto"]
    
    dim_veiculo = pd.DataFrame({
        "sk_veiculo": veiculo_ids,
        "placa": [f"{chr(np.random.randint(65,91))}{chr(np.random.randint(65,91))}{chr(np.random.randint(65,91))}-{np.random.randint(1000,9999)}" 
                  for _ in range(n_veiculos)],
        "marca": np.random.choice(marcas, n_veiculos),
        "modelo": np.random.choice(modelos, n_veiculos),
        "ano": np.random.randint(2018, 2025, n_veiculos),
        "tipo": np.random.choice(tipos, n_veiculos, p=[0.5, 0.3, 0.1, 0.05, 0.05]),
        "km_rodados": np.random.randint(10000, 150000, n_veiculos)
    })
    
    # DimRota
    cidades = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Brasília", "Salvador", 
               "Recife", "Porto Alegre", "Curitiba", "Fortaleza", "Manaus"]
    
    rotas = []
    for i in range(30):
        origem = np.random.choice(cidades)
        destino = np.random.choice([c for c in cidades if c != origem])
        rotas.append({
            "sk_rota": f"ROTA{i+1:03d}",
            "origem": origem,
            "destino": destino,
            "distancia_km": np.random.randint(5, 500),
            "tempo_medio_min": np.random.randint(15, 480)
        })
    dim_rota = pd.DataFrame(rotas)
    
    # DimPagamento
    metodos = ["Dinheiro", "Cartão", "PIX", "Vale Transporte", "App"]
    
    dim_pagamento = pd.DataFrame({
        "sk_pagamento": new_ids(len(metodos), "PAG"),
        "metodo": metodos,
        "taxa_servico": [0.0, 0.03, 0.0, 0.0, 0.05]
    })
    
    # ========== TABELA FATO ==========
    # Gerar viagens
    
    datas_viagem = rand_dates(start, end, n_linhas)
    horas = np.random.randint(0, 24, n_linhas)
    data_hora = [datetime.combine(d, datetime.min.time()) + timedelta(hours=h) 
                 for d, h in zip(datas_viagem, horas)]
    
    # Selecionar chaves estrangeiras
    motorista_keys = np.random.choice(dim_motorista["sk_motorista"], n_linhas)
    passageiro_keys = np.random.choice(dim_passageiro["sk_passageiro"], n_linhas)
    veiculo_keys = np.random.choice(dim_veiculo["sk_veiculo"], n_linhas)
    rota_keys = np.random.choice(dim_rota["sk_rota"], n_linhas)
    pagamento_keys = np.random.choice(dim_pagamento["sk_pagamento"], n_linhas)
    
    # Calcular valores
    distancias = dim_rota.set_index("sk_rota")["distancia_km"].to_dict()
    tempos = dim_rota.set_index("sk_rota")["tempo_medio_min"].to_dict()
    
    distancia_km = [distancias[rk] for rk in rota_keys]
    tempo_viagem = [tempos[rk] for rk in rota_keys]
    
    # Tarifa base (R$ 2.50 por km + R$ 0.50 por minuto)
    valor_base = [d * 2.5 + t * 0.5 for d, t in zip(distancia_km, tempo_viagem)]
    
    # Bandeira (1.0 = normal, 1.2 = bandeira 2)
    bandeira = np.random.choice([1.0, 1.2], n_linhas, p=[0.7, 0.3])
    valor_bandeira = [vb * b for vb, b in zip(valor_base, bandeira)]
    
    # Taxa de serviço da plataforma
    taxas = dim_pagamento.set_index("sk_pagamento")["taxa_servico"].to_dict()
    taxa_servico = [vb * taxas[pk] for vb, pk in zip(valor_bandeira, pagamento_keys)]
    
    valor_liquido_motorista = [vb - ts for vb, ts in zip(valor_bandeira, taxa_servico)]
    
    # Status da viagem
    status = np.random.choice(["Concluída", "Cancelada", "Em andamento"], n_linhas, p=[0.85, 0.1, 0.05])
    
    # Avaliação do passageiro (1-5)
    avaliacao_passageiro = [np.random.randint(1, 6) if s == "Concluída" and np.random.random() < 0.7 else None 
                            for s in status]
    
    fato_viagem = pd.DataFrame({
        "sk_viagem": new_ids(n_linhas, "VIA"),
        "data_hora_inicio": data_hora,
        "data_hora_fim": [dh + timedelta(minutes=t) for dh, t in zip(data_hora, tempo_viagem)],
        "distancia_km": distancia_km,
        "tempo_minutos": tempo_viagem,
        "bandeira": bandeira,
        "valor_bruto": valor_bandeira,
        "taxa_plataforma": taxa_servico,
        "valor_liquido_motorista": valor_liquido_motorista,
        "status": status,
        "avaliacao_passageiro": avaliacao_passageiro,
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
