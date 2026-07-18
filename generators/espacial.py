"""generators/espacial.py — Setor Espacial & Tecnologia Aeroespacial."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_MISSAO   = ["Satélite Comercial","Satélite Científico","Sonda Espacial","Tripulada","Suborbital","Reabastecimento ISS","Constelação"]
STATUS_MISSAO  = ["Planejada","Em desenvolvimento","Lançada","Operacional","Encerrada","Falhou"]
ORBITAS        = ["LEO","MEO","GEO","HEO","SSO","Lunar","Interplanetária"]
PROPULSORES    = ["Kerolox","Methalox","Hidrolox","Sólido","Iônico","Nuclear"]
SEGMENTOS      = ["Governo","Defesa","Comercial","Científico","Turismo Espacial"]
LANCADORES     = ["Falcon 9","Falcon Heavy","Ariane 6","Soyuz","PSLV","Vulcan","New Glenn","VLM-1"]
FABRICANTES    = ["SpaceX","Boeing","Airbus","Embraer Defense","AEB","Thales Alenia","Northrop Grumman","AVIO"]

def gerar_espacial(n, start, end):
    n = max(int(n), 1)
    n_miss = min(max(n//4,20),200)
    dim_missao = pd.DataFrame({
        "id_missao":        new_ids(n_miss),
        "nome":             [f"Mission-{rng.integers(1000,9999)}" for _ in range(n_miss)],
        "tipo":             random.choices(TIPOS_MISSAO, k=n_miss),
        "status":           random.choices(STATUS_MISSAO, weights=[15,20,10,35,15,5], k=n_miss),
        "orbita":           random.choices(ORBITAS, k=n_miss),
        "segmento":         random.choices(SEGMENTOS, k=n_miss),
        "lancador":         random.choices(LANCADORES, k=n_miss),
        "fabricante":       random.choices(FABRICANTES, k=n_miss),
        "orcamento_mi":     rng.uniform(5, 10_000, n_miss).round(1),
        "data_lancamento":  rand_dates(start, end, n_miss),
        "duracao_anos":     rng.uniform(0.5, 20, n_miss).round(1),
        "massa_kg":         rng.uniform(10, 10_000, n_miss).round(0),
        "altitude_km":      rng.uniform(200, 36_000, n_miss).round(0),
        "sucesso":          random.choices([True,False], weights=[88,12], k=n_miss),
    })
    n_comp = min(max(n//5,30),250)
    dim_componente = pd.DataFrame({
        "id_componente":    new_ids(n_comp),
        "nome":             [f"{fake.word().upper()}-{rng.integers(100,999)}" for _ in range(n_comp)],
        "subsistema":       random.choices(["Propulsão","Estrutura","Energia","Comunicação","AOCS","Payload","TCS"], k=n_comp),
        "fabricante":       random.choices(FABRICANTES, k=n_comp),
        "massa_kg":         rng.uniform(0.1, 2_000, n_comp).round(2),
        "custo_mi":         rng.uniform(0.01, 500, n_comp).round(2),
        "trl":              rng.integers(1, 9, n_comp),
        "qualificado":      random.choices([True,False], weights=[70,30], k=n_comp),
    })
    custo = rng.uniform(1_000_000, 5_000_000_000, n).round(2)
    fato_operacao = pd.DataFrame({
        "id_operacao":      new_ids(n),
        "id_data":          rand_dates(start, end, n),
        "id_missao":        random.choices(dim_missao["id_missao"].tolist(), k=n),
        "id_componente":    random.choices(dim_componente["id_componente"].tolist(), k=n),
        "custo_realizado":  custo,
        "custo_orcado":     (custo * rng.uniform(0.7, 1.4, n)).round(2),
        "horas_engenharia": rng.uniform(10, 50_000, n).round(0),
        "testes_realizados":rng.integers(0, 500, n),
        "anomalias":        rng.integers(0, 50, n),
        "disponibilidade_pct": rng.uniform(85, 99.99, n).round(2),
        "dados_coletados_gb":  rng.uniform(0, 100_000, n).round(1),
        "receita_servicos": rng.uniform(0, 2_000_000_000, n).round(2),
    })
    return {"DimMissao": dim_missao, "DimComponente": dim_componente,
            "FatoOperacao": fato_operacao, "dCalendario": dcalendario(start, end)}
