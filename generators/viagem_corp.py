"""generators/viagem_corp.py — Setor Viagens Corporativas & Travel Management."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_VIAGEM   = ["Nacional","Internacional"]
MOTIVOS        = ["Reunião de Negócios","Treinamento","Congresso","Visita Técnica","Comercial","Projeto"]
CLASSES_AEREO  = ["Econômica","Executiva","Primeira Classe"]
CATEGORIAS_HTL = ["Econômico","Standard","Superior","Luxo","Apart-Hotel"]
CIAS_AEREAS    = ["LATAM","Gol","Azul","American Airlines","TAP","Air France","Emirates","Copa Airlines"]
STATUS_VIAGEM  = ["Aprovada","Realizada","Cancelada","Em andamento","Pendente aprovação"]
POLITICA       = ["Dentro da política","Fora da política","Exceção aprovada"]
DEPARTAMENTOS  = ["Comercial","TI","RH","Financeiro","Operações","Diretoria","Marketing","Projetos"]

def gerar_viagem_corp(n, start, end):
    n = max(int(n), 1)
    n_viaj = min(max(n//5,50),500)
    dim_viajante = pd.DataFrame({
        "id_viajante":      new_ids(n_viaj),
        "nome":             [fake.name() for _ in range(n_viaj)],
        "departamento":     random.choices(DEPARTAMENTOS, k=n_viaj),
        "cargo":            random.choices(["Analista","Gerente","Diretor","VP","C-Level","Coordenador"], k=n_viaj),
        "empresa":          [fake.company() for _ in range(n_viaj)],
        "limite_diaria":    rng.uniform(150, 800, n_viaj).round(2),
        "cartao_corp":      random.choices([True,False], weights=[70,30], k=n_viaj),
        "ativo":            random.choices([True,False], weights=[90,10], k=n_viaj),
    })
    n_dest = 60
    dim_destino = pd.DataFrame({
        "id_destino":       new_ids(n_dest),
        "cidade":           [fake.city() for _ in range(n_dest)],
        "pais":             random.choices(["Brasil","EUA","Portugal","Argentina","Chile","Alemanha","UK","França","Colômbia"], k=n_dest),
        "tipo":             random.choices(TIPOS_VIAGEM, weights=[65,35], k=n_dest),
        "fuso_dif":         rng.integers(-5, 5, n_dest),
        "custo_medio_htl":  rng.uniform(150, 1_200, n_dest).round(2),
    })
    dias = rng.integers(1, 15, n)
    diaria = rng.uniform(150, 800, n).round(2)
    aereo = rng.uniform(300, 8_000, n).round(2)
    htl = (dias * rng.uniform(150, 1_200, n)).round(2)
    fato_viagem = pd.DataFrame({
        "id_viagem":        new_ids(n),
        "id_data":          rand_dates(start, end, n),
        "id_viajante":      random.choices(dim_viajante["id_viajante"].tolist(), k=n),
        "id_destino":       random.choices(dim_destino["id_destino"].tolist(), k=n),
        "motivo":           random.choices(MOTIVOS, k=n),
        "status":           random.choices(STATUS_VIAGEM, weights=[10,65,10,10,5], k=n),
        "classe_aereo":     random.choices(CLASSES_AEREO, weights=[70,25,5], k=n),
        "categoria_hotel":  random.choices(CATEGORIAS_HTL, k=n),
        "dias_viagem":      dias,
        "valor_aereo":      aereo,
        "valor_hotel":      htl,
        "valor_diarias":    (dias * diaria).round(2),
        "outras_despesas":  rng.uniform(0, 1_000, n).round(2),
        "custo_total":      (aereo + htl + dias*diaria).round(2),
        "politica":         random.choices(POLITICA, weights=[75,15,10], k=n),
        "antecedencia_dias":rng.integers(0, 60, n),
        "cia_aerea":        random.choices(CIAS_AEREAS, k=n),
        "nps_viajante":     rng.uniform(0, 100, n).round(1),
    })
    return {"DimViajante": dim_viajante, "DimDestino": dim_destino,
            "FatoViagem": fato_viagem, "dCalendario": dcalendario(start, end)}
