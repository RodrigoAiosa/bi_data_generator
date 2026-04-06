import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .helpers import new_ids, dcalendario, rand_dates

def gerar_streaming(n_linhas: int, start_date: str, end_date: str) -> dict[str, pd.DataFrame]:
    """
    Gera dados do setor de Streaming (Star Schema)
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    # ========== DIMENSÕES ==========
    
    # DimAssinante (500-2000 assinantes)
    n_assinantes = min(2000, max(500, n_linhas // 20))
    assinante_ids = new_ids(n_assinantes, "ASS")
    
    planos = ["Básico", "Standard", "Premium"]
    idades = np.random.randint(18, 70, n_assinantes)
    cidades = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Brasília", "Salvador", 
               "Recife", "Fortaleza", "Porto Alegre", "Curitiba", "Manaus"]
    
    dim_assinante = pd.DataFrame({
        "sk_assinante": assinante_ids,
        "id_assinante": assinante_ids,
        "nome": [f"Assinante {i+1}" for i in range(n_assinantes)],
        "email": [f"user{i+1}@stream.com" for i in range(n_assinantes)],
        "plano": np.random.choice(planos, n_assinantes, p=[0.4, 0.45, 0.15]),
        "idade": idades,
        "sexo": np.random.choice(["M", "F", "Prefiro não informar"], n_assinantes, p=[0.48, 0.48, 0.04]),
        "cidade": np.random.choice(cidades, n_assinantes),
        "data_adesao": rand_dates(start - timedelta(days=365), start, n_assinantes)
    })
    
    # DimConteudo (100-500 títulos)
    n_conteudos = min(500, max(100, n_linhas // 30))
    conteudo_ids = new_ids(n_conteudos, "CON")
    
    generos = ["Ação", "Comédia", "Drama", "Terror", "Ficção Científica", "Romance", 
               "Documentário", "Animação", "Suspense", "Fantasia"]
    
    dim_conteudo = pd.DataFrame({
        "sk_conteudo": conteudo_ids,
        "id_conteudo": conteudo_ids,
        "titulo": [f"Título {i+1}" for i in range(n_conteudos)],
        "genero": np.random.choice(generos, n_conteudos),
        "duracao_min": np.random.randint(30, 180, n_conteudos),
        "ano_lancamento": np.random.randint(2015, 2025, n_conteudos),
        "classificacao": np.random.choice(["L", "10", "12", "14", "16", "18"], n_conteudos),
        "tipo": np.random.choice(["Filme", "Série"], n_conteudos, p=[0.6, 0.4])
    })
    
    # DimArtista (100-300 artistas)
    n_artistas = min(300, max(100, n_linhas // 50))
    artista_ids = new_ids(n_artistas, "ART")
    
    tipos_artista = ["Ator", "Diretor", "Produtor", "Roteirista"]
    
    dim_artista = pd.DataFrame({
        "sk_artista": artista_ids,
        "nome": [f"Artista {i+1}" for i in range(n_artistas)],
        "tipo": np.random.choice(tipos_artista, n_artistas),
        "nacionalidade": np.random.choice(["Brasileiro", "Americano", "Europeu", "Asiático"], n_artistas)
    })
    
    # DimDispositivo
    dispositivos = ["Smart TV", "Desktop", "Mobile (iOS)", "Mobile (Android)", "Tablet"]
    sistemas = ["Tizen", "Windows", "macOS", "iOS", "Android"]
    
    dim_dispositivo = pd.DataFrame({
        "sk_dispositivo": new_ids(len(dispositivos), "DIS"),
        "tipo": dispositivos,
        "sistema_operacional": sistemas
    })
    
    # ========== TABELA FATO ==========
    # Gerar plays/visualizações
    
    # Relacionamento Conteudo-Artista (muitos-para-muitos simplificado)
    # Para cada play, escolher 1-3 artistas envolvidos
    artista_ids_list = dim_artista["sk_artista"].tolist()
    
    # Selecionar chaves
    assinante_keys = np.random.choice(dim_assinante["sk_assinante"], n_linhas)
    conteudo_keys = np.random.choice(dim_conteudo["sk_conteudo"], n_linhas)
    dispositivo_keys = np.random.choice(dim_dispositivo["sk_dispositivo"], n_linhas)
    
    # Horários de reprodução
    horas = np.random.randint(0, 24, n_linhas)
    minutos = np.random.randint(0, 60, n_linhas)
    datas_play = rand_dates(start, end, n_linhas)
    
    # Calcular minutos assistidos (baseado na duração do conteúdo)
    duracao_dict = dim_conteudo.set_index("sk_conteudo")["duracao_min"].to_dict()
    duracao_conteudo = [duracao_dict[ck] for ck in conteudo_keys]
    minutos_assistidos = [int(d * np.random.uniform(0.1, 1.0)) for d in duracao_conteudo]
    completude = [1 if ma == dc else 0 for ma, dc in zip(minutos_assistidos, duracao_conteudo)]
    
    # Avaliação (1-5 estrelas, apenas 30% dos plays avaliam)
    avaliacao = [np.random.randint(1, 6) if np.random.random() < 0.3 else None for _ in range(n_linhas)]
    
    fato_streaming = pd.DataFrame({
        "sk_play": new_ids(n_linhas, "PLY"),
        "data_hora": [datetime.combine(d, datetime.min.time()) + timedelta(hours=h, minutes=m) 
                      for d, h, m in zip(datas_play, horas, minutos)],
        "minutos_assistidos": minutos_assistidos,
        "duracao_conteudo": duracao_conteudo,
        "completude": completude,
        "avaliacao": avaliacao,
        "pausou": np.random.choice([True, False], n_linhas, p=[0.3, 0.7]),
        "sk_assinante": assinante_keys,
        "sk_conteudo": conteudo_keys,
        "sk_dispositivo": dispositivo_keys
    })
    
    # Tabela ponte Conteudo-Artista
    conteudo_artista = []
    for ck in conteudo_ids:
        n_artistas_ck = np.random.randint(1, 4)
        artistas_ck = np.random.choice(artista_ids_list, n_artistas_ck, replace=False)
        for ak in artistas_ck:
            conteudo_artista.append({
                "sk_conteudo": ck,
                "sk_artista": ak
            })
    bridge_conteudo_artista = pd.DataFrame(conteudo_artista)
    
    return {
        "FatoStreaming": fato_streaming,
        "DimAssinante": dim_assinante,
        "DimConteudo": dim_conteudo,
        "DimArtista": dim_artista,
        "DimDispositivo": dim_dispositivo,
        "BridgeConteudoArtista": bridge_conteudo_artista,
        "dCalendario": dcalendario(start, end)
    }
