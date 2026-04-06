import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .helpers import new_ids, dcalendario, rand_dates

def gerar_hotelaria(n_linhas: int, start_date: str, end_date: str) -> dict[str, pd.DataFrame]:
    """
    Gera dados do setor de Hotelaria (Star Schema)
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    # ========== DIMENSÕES ==========
    
    # DimHospede (100-500 hóspedes)
    n_hospedes = min(500, max(100, n_linhas // 10))
    hospede_ids = new_ids(n_hospedes, "HOS")
    
    tipos_hospede = ["Corporativo", "Lazer", "Família", "Casual"]
    cidades = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Brasília", "Salvador", 
               "Recife", "Fortaleza", "Porto Alegre", "Curitiba", "Manaus"]
    
    dim_hospede = pd.DataFrame({
        "sk_hospede": hospede_ids,
        "id_hospede": hospede_ids,
        "nome": [f"Hóspede {i+1}" for i in range(n_hospedes)],
        "cpf": [f"{np.random.randint(100,999)}.{np.random.randint(100,999)}.{np.random.randint(100,999)}-{np.random.randint(10,99)}" 
                for _ in range(n_hospedes)],
        "email": [f"hospede{i+1}@email.com" for i in range(n_hospedes)],
        "telefone": [f"({np.random.randint(11,99)}) 9{np.random.randint(1000,9999)}-{np.random.randint(1000,9999)}" 
                     for _ in range(n_hospedes)],
        "cidade": np.random.choice(cidades, n_hospedes),
        "tipo_hospede": np.random.choice(tipos_hospede, n_hospedes),
        "primeira_visita": np.random.choice([True, False], n_hospedes, p=[0.3, 0.7])
    })
    
    # DimHotel (20-50 hotéis)
    n_hoteis = min(50, max(20, n_linhas // 100))
    hotel_ids = new_ids(n_hoteis, "HOT")
    
    categorias = ["3 estrelas", "4 estrelas", "5 estrelas"]
    cidades_hoteis = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Brasília", "Salvador", "Recife"]
    
    dim_hotel = pd.DataFrame({
        "sk_hotel": hotel_ids,
        "id_hotel": hotel_ids,
        "nome": [f"Hotel {chr(65+i)}" for i in range(n_hoteis)],
        "categoria": np.random.choice(categorias, n_hoteis, p=[0.3, 0.5, 0.2]),
        "cidade": np.random.choice(cidades_hoteis, n_hoteis),
        "bairro": [f"Bairro {np.random.randint(1,20)}" for _ in range(n_hoteis)],
        "total_quartos": np.random.randint(30, 200, n_hoteis)
    })
    
    # DimQuarto (10-30 quartos por hotel)
    quartos = []
    for hotel_id in hotel_ids:
        n_quartos = np.random.randint(10, 30)
        tipos_quarto = ["Standard", "Luxo", "Suíte"]
        for i in range(n_quartos):
            quartos.append({
                "sk_quarto": f"{hotel_id}_Q{i+1:03d}",
                "id_quarto": f"{i+1:03d}",
                "sk_hotel": hotel_id,
                "tipo_quarto": np.random.choice(tipos_quarto, p=[0.6, 0.3, 0.1]),
                "capacidade": np.random.choice([1,2,3,4], p=[0.1,0.6,0.2,0.1]),
                "andar": np.random.randint(1, 15),
                "vista": np.random.choice(["Cidade", "Mar", "Montanha", "Jardim"], p=[0.5,0.2,0.1,0.2])
            })
    dim_quarto = pd.DataFrame(quartos)
    
    # DimCanal
    canais = ["Booking.com", "Expedia", "Decolar", "Direto", "Agência", "Hotéis.com"]
    comissoes = [0.15, 0.12, 0.10, 0.0, 0.08, 0.12]
    
    dim_canal = pd.DataFrame({
        "sk_canal": new_ids(len(canais), "CAN"),
        "nome_canal": canais,
        "taxa_comissao": comissoes
    })
    
    # ========== TABELA FATO ==========
    # Gerar reservas
    datas = rand_dates(start, end, n_linhas)
    dias_estadia = np.random.randint(1, 15, n_linhas)
    data_checkout = [d + timedelta(days=de) for d, de in zip(datas, dias_estadia)]
    
    # Selecionar chaves estrangeiras
    hospede_keys = np.random.choice(dim_hospede["sk_hospede"], n_linhas)
    hotel_keys = np.random.choice(dim_hotel["sk_hotel"], n_linhas)
    quarto_keys = np.random.choice(dim_quarto["sk_quarto"], n_linhas)
    canal_keys = np.random.choice(dim_canal["sk_canal"], n_linhas)
    
    # Calcular valor (diária * dias)
    diaria_base = np.random.uniform(150, 800, n_linhas)
    
    # Ajuste por tipo de quarto
    tipo_ajuste = dim_quarto.set_index("sk_quarto")["tipo_quarto"].to_dict()
    ajustes = {"Standard": 1.0, "Luxo": 1.8, "Suíte": 2.5}
    diaria = [diaria_base[i] * ajustes[tipo_ajuste[q]] for i, q in enumerate(quarto_keys)]
    
    valor_total = diaria * dias_estadia
    
    # Status da reserva
    status = np.random.choice(
        ["Confirmada", "Cancelada", "No-show", "Finalizada"],
        n_linhas,
        p=[0.6, 0.15, 0.05, 0.2]
    )
    
    fato_reserva = pd.DataFrame({
        "sk_reserva": new_ids(n_linhas, "RES"),
        "data_reserva": datas,
        "data_checkin": datas,
        "data_checkout": data_checkout,
        "dias_estadia": dias_estadia,
        "diaria": diaria,
        "valor_total": valor_total,
        "status": status,
        "sk_hospede": hospede_keys,
        "sk_hotel": hotel_keys,
        "sk_quarto": quarto_keys,
        "sk_canal": canal_keys
    })
    
    return {
        "FatoReserva": fato_reserva,
        "DimHospede": dim_hospede,
        "DimHotel": dim_hotel,
        "DimQuarto": dim_quarto,
        "DimCanal": dim_canal,
        "dCalendario": dcalendario(start, end)
    }
