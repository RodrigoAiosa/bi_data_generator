"""generators/condominio.py — Setor Condomínio & Facilities."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_COND    = ["Residencial Horizontal","Residencial Vertical","Comercial","Misto","Industrial"]
TIPOS_AREA    = ["Academia","Piscina","Salão de Festas","Quadra","Churrasqueira","Coworking","Playground"]
TIPOS_OCORR   = ["Barulho","Vazamento","Segurança","Estacionamento","Animais","Obra","Limpeza","Manutenção"]
STATUS_OCORR  = ["Aberta","Em andamento","Encerrada","Cancelada"]
TIPOS_DESPESA = ["Folha de Pagamento","Energia","Água","Seguro","Manutenção","Limpeza","Vigilância","Administração"]
FORNECEDORES  = [fake.company() for _ in range(30)]

def gerar_condominio(n, start, end):
    n = max(int(n), 1)
    n_cond = min(max(n//15,10),80)
    dim_condominio = pd.DataFrame({
        "id_condominio":    new_ids(n_cond),
        "nome":             [f"Cond. {fake.last_name()}" for _ in range(n_cond)],
        "tipo":             random.choices(TIPOS_COND, k=n_cond),
        "uf":               [fake.state_abbr() for _ in range(n_cond)],
        "cidade":           [fake.city() for _ in range(n_cond)],
        "n_unidades":       rng.integers(20, 600, n_cond),
        "area_total_m2":    rng.uniform(500, 50_000, n_cond).round(0),
        "fundo_reserva":    rng.uniform(10_000, 500_000, n_cond).round(2),
        "taxa_condominio":  rng.uniform(300, 3_000, n_cond).round(2),
        "adm_empresa":      [fake.company() for _ in range(n_cond)],
    })
    n_unid = min(max(n//3,50),1000)
    dim_unidade = pd.DataFrame({
        "id_unidade":       new_ids(n_unid),
        "id_condominio":    random.choices(dim_condominio["id_condominio"].tolist(), k=n_unid),
        "bloco":            [f"Bloco {random.choice('ABCDEFGH')}" for _ in range(n_unid)],
        "numero":           rng.integers(1, 300, n_unid),
        "tipo":             random.choices(["Apartamento","Casa","Sala Comercial","Loja"], k=n_unid),
        "proprietario":     [fake.name() for _ in range(n_unid)],
        "morador":          [fake.name() for _ in range(n_unid)],
        "area_m2":          rng.uniform(30, 400, n_unid).round(0),
        "ocupado":          random.choices([True,False], weights=[85,15], k=n_unid),
    })
    fato_cota = pd.DataFrame({
        "id_cota":          new_ids(n),
        "id_data":          rand_dates(start, end, n),
        "id_unidade":       random.choices(dim_unidade["id_unidade"].tolist(), k=n),
        "id_condominio":    random.choices(dim_condominio["id_condominio"].tolist(), k=n),
        "valor_cota":       rng.uniform(300, 3_000, n).round(2),
        "valor_extra":      rng.uniform(0, 500, n).round(2),
        "pago":             random.choices([True,False], weights=[88,12], k=n),
        "data_pagamento":   rand_dates(start, end, n),
        "multa":            rng.uniform(0, 300, n).round(2),
        "inadimplente":     random.choices([True,False], weights=[12,88], k=n),
    })
    n_ocorr = int(n * 0.3)
    fato_ocorrencia = pd.DataFrame({
        "id_ocorrencia":    new_ids(n_ocorr),
        "id_data":          rand_dates(start, end, n_ocorr),
        "id_unidade":       random.choices(dim_unidade["id_unidade"].tolist(), k=n_ocorr),
        "id_condominio":    random.choices(dim_condominio["id_condominio"].tolist(), k=n_ocorr),
        "tipo":             random.choices(TIPOS_OCORR, k=n_ocorr),
        "status":           random.choices(STATUS_OCORR, weights=[20,30,45,5], k=n_ocorr),
        "prioridade":       random.choices(["Alta","Média","Baixa"], weights=[15,50,35], k=n_ocorr),
        "tempo_resolucao_h":rng.uniform(0.5, 720, n_ocorr).round(1),
    })
    n_desp = int(n * 0.4)
    fato_despesa = pd.DataFrame({
        "id_despesa":       new_ids(n_desp),
        "id_data":          rand_dates(start, end, n_desp),
        "id_condominio":    random.choices(dim_condominio["id_condominio"].tolist(), k=n_desp),
        "tipo_despesa":     random.choices(TIPOS_DESPESA, k=n_desp),
        "fornecedor":       random.choices(FORNECEDORES, k=n_desp),
        "valor":            rng.uniform(200, 80_000, n_desp).round(2),
        "aprovado":         random.choices([True,False], weights=[90,10], k=n_desp),
    })
    return {"DimCondominio": dim_condominio, "DimUnidade": dim_unidade,
            "FatoCota": fato_cota, "FatoOcorrencia": fato_ocorrencia,
            "FatoDespesa": fato_despesa, "dCalendario": dcalendario(start, end)}
