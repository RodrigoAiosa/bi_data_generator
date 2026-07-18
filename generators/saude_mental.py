"""generators/saude_mental.py — Setor Saúde Mental & Psicologia."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

ESPECIALIDADES  = ["Psicologia Clínica","Psiquiatria","Psicanálise","TCC","EMDR","Terapia de Casal","Psicologia Infantil","Neuropsicologia"]
MODALIDADES     = ["Presencial","Online","Híbrido"]
DIAGNOSTICOS    = ["Ansiedade","Depressão","TDAH","TOC","Burnout","Fobia","Bipolaridade","TEPT","Sem diagnóstico"]
STATUS_SESSAO   = ["Realizada","Faltou","Cancelada","Reagendada"]
CONVENIOS       = ["Particular","Unimed","Bradesco Saúde","SulAmérica","Amil","Vale Saúde"]
PLANOS_ASSIN    = ["Mensal","Trimestral","Semestral","Anual"]

def gerar_saude_mental(n, start, end):
    n = max(int(n), 1)
    n_prof = min(max(n//15,20),200)
    dim_profissional = pd.DataFrame({
        "id_profissional":  new_ids(n_prof),
        "nome":             [fake.name() for _ in range(n_prof)],
        "crp_crm":          [f"CRP-{rng.integers(10000,99999)}" for _ in range(n_prof)],
        "especialidade":    random.choices(ESPECIALIDADES, k=n_prof),
        "modalidade":       random.choices(MODALIDADES, k=n_prof),
        "valor_sessao":     rng.uniform(80, 600, n_prof).round(2),
        "anos_experiencia": rng.integers(1, 30, n_prof),
        "ativo":            random.choices([True,False], weights=[90,10], k=n_prof),
        "cidade":           [fake.city() for _ in range(n_prof)],
        "uf":               [fake.state_abbr() for _ in range(n_prof)],
    })
    n_pac = min(max(n//3,100),2000)
    dim_paciente = pd.DataFrame({
        "id_paciente":      new_ids(n_pac),
        "nome":             [fake.name() for _ in range(n_pac)],
        "data_nasc":        rand_dates(date(1960,1,1), date(2010,12,31), n_pac),
        "sexo":             random.choices(["M","F","Não-binário"], weights=[35,55,10], k=n_pac),
        "diagnostico":      random.choices(DIAGNOSTICOS, k=n_pac),
        "convenio":         random.choices(CONVENIOS, k=n_pac),
        "modalidade_pref":  random.choices(MODALIDADES, k=n_pac),
        "encaminhamento":   random.choices(["Indicação","Busca Online","Médico","RH Empresa","Plataforma"], k=n_pac),
        "ativo":            random.choices([True,False], weights=[80,20], k=n_pac),
        "data_inicio":      rand_dates(date(2018,1,1), end, n_pac),
    })
    status = random.choices(STATUS_SESSAO, weights=[75,10,10,5], k=n)
    fato_sessao = pd.DataFrame({
        "id_sessao":        new_ids(n),
        "id_data":          rand_dates(start, end, n),
        "id_profissional":  random.choices(dim_profissional["id_profissional"].tolist(), k=n),
        "id_paciente":      random.choices(dim_paciente["id_paciente"].tolist(), k=n),
        "status":           status,
        "modalidade":       random.choices(MODALIDADES, k=n),
        "duracao_min":      random.choices([50, 60, 80, 90], k=n),
        "valor_cobrado":    rng.uniform(80, 600, n).round(2),
        "valor_recebido":   rng.uniform(60, 600, n).round(2),
        "n_sessao_paciente":rng.integers(1, 200, n),
        "avaliacao":        rng.uniform(3, 5, n).round(1),
        "faltou":           [s in ["Faltou","Cancelada"] for s in status],
    })
    return {"DimProfissional": dim_profissional, "DimPaciente": dim_paciente,
            "FatoSessao": fato_sessao, "dCalendario": dcalendario(start, end)}
