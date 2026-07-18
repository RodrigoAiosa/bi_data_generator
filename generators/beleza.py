"""generators/beleza.py — Setor Beleza, Cosméticos & Estética."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CATEGORIAS    = ["Skincare","Maquiagem","Cabelo","Corpo","Perfumaria","Unhas","Masculino","Infantil","Orgânico"]
CANAIS        = ["Salão Parceiro","E-commerce Próprio","Marketplace","Loja Física","Revendedor","Assinatura"]
SERVICOS      = ["Coloração","Corte","Tratamento Capilar","Limpeza de Pele","Manicure","Design de Sobrancelha",
                 "Depilação","Extensão de Cílios","Massagem","Maquiagem Social"]
STATUS_AG     = ["Confirmado","Cancelado","Realizado","Faltou","Remarcado"]
CERTIFICACOES = ["ANVISA","Vegano","Cruelty-Free","Orgânico","Dermatologicamente Testado"]

def gerar_beleza(n, start, end):
    n = max(int(n), 1)
    n_prod = min(max(n//6,80),600)
    dim_produto = pd.DataFrame({
        "id_produto":       new_ids(n_prod),
        "nome":             [f"{fake.last_name()} {random.choice(['Sérum','Creme','Óleo','Shampoo','Máscara','Gel'])}" for _ in range(n_prod)],
        "categoria":        random.choices(CATEGORIAS, k=n_prod),
        "marca":            [fake.company() for _ in range(n_prod)],
        "custo":            rng.uniform(5, 200, n_prod).round(2),
        "preco_venda":      rng.uniform(20, 800, n_prod).round(2),
        "certificacao":     random.choices(CERTIFICACOES, k=n_prod),
        "vegano":           random.choices([True,False], weights=[45,55], k=n_prod),
        "ativo":            random.choices([True,False], weights=[88,12], k=n_prod),
    })
    n_sal = min(max(n//10,20),150)
    dim_salao = pd.DataFrame({
        "id_salao":         new_ids(n_sal),
        "nome":             [f"Studio {fake.last_name()}" for _ in range(n_sal)],
        "tipo":             random.choices(["Salão Completo","Barbearia","Clínica Estética","Nail Design","Hair Bar"], k=n_sal),
        "uf":               [fake.state_abbr() for _ in range(n_sal)],
        "cidade":           [fake.city() for _ in range(n_sal)],
        "n_profissionais":  rng.integers(1, 30, n_sal),
        "avaliacao":        rng.uniform(3.0, 5.0, n_sal).round(1),
        "ativo":            random.choices([True,False], weights=[90,10], k=n_sal),
    })
    qtd = rng.integers(1, 10, n)
    preco = rng.uniform(20, 800, n).round(2)
    fato_venda = pd.DataFrame({
        "id_venda":         new_ids(n),
        "id_data":          rand_dates(start, end, n),
        "id_produto":       random.choices(dim_produto["id_produto"].tolist(), k=n),
        "id_salao":         random.choices(dim_salao["id_salao"].tolist(), k=n),
        "canal":            random.choices(CANAIS, k=n),
        "quantidade":       qtd,
        "preco_unitario":   preco,
        "desconto_pct":     rng.uniform(0, 40, n).round(1),
        "valor_total":      (qtd * preco).round(2),
        "devolucao":        random.choices([True,False], weights=[8,92], k=n),
        "assinante":        random.choices([True,False], weights=[25,75], k=n),
    })
    n_ag = int(n * 0.6)
    status_ag = random.choices(STATUS_AG, weights=[10,10,70,5,5], k=n_ag)
    fato_agenda = pd.DataFrame({
        "id_agenda":        new_ids(n_ag),
        "id_data":          rand_dates(start, end, n_ag),
        "id_salao":         random.choices(dim_salao["id_salao"].tolist(), k=n_ag),
        "servico":          random.choices(SERVICOS, k=n_ag),
        "status":           status_ag,
        "valor_servico":    rng.uniform(30, 600, n_ag).round(2),
        "duracao_min":      random.choices([30,45,60,90,120], k=n_ag),
        "recorrente":       random.choices([True,False], weights=[40,60], k=n_ag),
        "avaliacao":        [round(rng.uniform(3,5),1) if s == "Realizado" else None for s in status_ag],
    })
    return {"DimProduto": dim_produto, "DimSalao": dim_salao,
            "FatoVenda": fato_venda, "FatoAgenda": fato_agenda,
            "dCalendario": dcalendario(start, end)}
