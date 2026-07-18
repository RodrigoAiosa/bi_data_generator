"""generators/arquitetura.py — Setor Arquitetura & Design de Interiores."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_PROJETO  = ["Residencial","Comercial","Corporativo","Hospitalar","Educacional","Industrial","Urbanismo","Interiores","Paisagismo"]
STATUS_PROJETO = ["Briefing","Anteprojeto","Projeto Executivo","Em obra","Concluído","Suspenso","Cancelado"]
ESTILOS        = ["Moderno","Contemporâneo","Minimalista","Industrial","Rústico","Clássico","Biofílico","Escandinavo"]
SERVICOS       = ["Projeto Arquitetônico","Projeto de Interiores","Compatibilização","Consultoria","Gerenciamento de Obra","Maquete 3D","BIM"]

def gerar_arquitetura(n, start, end):
    n = max(int(n), 1)
    n_arq = min(max(n//15,10),100)
    dim_arquiteto = pd.DataFrame({
        "id_arquiteto":     new_ids(n_arq),
        "nome":             [fake.name() for _ in range(n_arq)],
        "cau":              [f"CAU-A{rng.integers(100000,999999)}" for _ in range(n_arq)],
        "especialidade":    random.choices(TIPOS_PROJETO, k=n_arq),
        "anos_exp":         rng.integers(1, 35, n_arq),
        "valor_hora":       rng.uniform(80, 800, n_arq).round(2),
        "ativo":            random.choices([True,False], weights=[90,10], k=n_arq),
        "cidade":           [fake.city() for _ in range(n_arq)],
        "uf":               [fake.state_abbr() for _ in range(n_arq)],
    })
    n_cli = min(max(n//6,30),300)
    dim_cliente = pd.DataFrame({
        "id_cliente":       new_ids(n_cli),
        "nome":             [fake.name() for _ in range(n_cli)],
        "tipo":             random.choices(["PF","PJ"], weights=[55,45], k=n_cli),
        "segmento":         random.choices(TIPOS_PROJETO, k=n_cli),
        "uf":               [fake.state_abbr() for _ in range(n_cli)],
        "origem":           random.choices(["Indicação","Instagram","Site","Google","LinkedIn"], k=n_cli),
    })
    n_proj = min(max(n//3,40),400)
    area = rng.uniform(30, 20_000, n_proj).round(0)
    valor_m2 = rng.uniform(50, 500, n_proj).round(2)
    dim_projeto = pd.DataFrame({
        "id_projeto":       new_ids(n_proj),
        "id_arquiteto":     random.choices(dim_arquiteto["id_arquiteto"].tolist(), k=n_proj),
        "id_cliente":       random.choices(dim_cliente["id_cliente"].tolist(), k=n_proj),
        "tipo":             random.choices(TIPOS_PROJETO, k=n_proj),
        "estilo":           random.choices(ESTILOS, k=n_proj),
        "status":           random.choices(STATUS_PROJETO, weights=[10,15,20,25,25,3,2], k=n_proj),
        "area_m2":          area,
        "valor_m2":         valor_m2,
        "honorarios":       (area * valor_m2).round(2),
        "data_inicio":      rand_dates(start, end, n_proj),
        "prazo_meses":      rng.integers(1, 36, n_proj),
        "nps":              rng.uniform(0, 100, n_proj).round(1),
    })
    horas = rng.uniform(1, 200, n).round(1)
    valor_h = rng.uniform(80, 800, n).round(2)
    fato_servico = pd.DataFrame({
        "id_servico":       new_ids(n),
        "id_data":          rand_dates(start, end, n),
        "id_projeto":       random.choices(dim_projeto["id_projeto"].tolist(), k=n),
        "id_arquiteto":     random.choices(dim_arquiteto["id_arquiteto"].tolist(), k=n),
        "tipo_servico":     random.choices(SERVICOS, k=n),
        "horas_trabalhadas":horas,
        "valor_hora":       valor_h,
        "valor_total":      (horas * valor_h).round(2),
        "etapa":            random.choices(STATUS_PROJETO, k=n),
        "aprovado_cliente": random.choices([True,False], weights=[88,12], k=n),
        "retrabalho":       random.choices([True,False], weights=[15,85], k=n),
    })
    return {"DimArquiteto": dim_arquiteto, "DimCliente": dim_cliente,
            "DimProjeto": dim_projeto, "FatoServico": fato_servico,
            "dCalendario": dcalendario(start, end)}
