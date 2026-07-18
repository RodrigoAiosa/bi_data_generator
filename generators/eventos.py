"""generators/eventos.py — Setor Eventos & Entretenimento."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_EVENTO  = ["Show Musical","Festival","Congresso","Feira","Casamento","Formatura","Corporativo","Esportivo","Teatro","Stand-up"]
LOCAIS        = ["Buffet","Arena","Teatro","Hotel","Centro de Convenções","Espaço ao Ar Livre","Clube","Estádio"]
STATUS_EVENTO = ["Confirmado","Cancelado","Realizado","Adiado","Em captação"]
FORNECEDORES  = ["Buffet","Som e Iluminação","Fotografia","Decoração","Segurança","Transporte","Estande","AV/TI"]

def gerar_eventos(n, start, end):
    n = max(int(n), 1)
    n_ev = min(max(n//4,50),500)
    dim_evento = pd.DataFrame({
        "id_evento":    new_ids(n_ev),
        "nome":         [f"{random.choice(TIPOS_EVENTO)} {fake.last_name()}" for _ in range(n_ev)],
        "tipo":         random.choices(TIPOS_EVENTO, k=n_ev),
        "local":        random.choices(LOCAIS, k=n_ev),
        "uf":           [fake.state_abbr() for _ in range(n_ev)],
        "cidade":       [fake.city() for _ in range(n_ev)],
        "data_evento":  rand_dates(start, end, n_ev),
        "capacidade":   rng.integers(50, 80_000, n_ev),
        "status":       random.choices(STATUS_EVENTO, weights=[30,5,55,5,5], k=n_ev),
        "orcamento":    rng.uniform(5_000, 5_000_000, n_ev).round(2),
    })
    n_cli = min(max(n//8,40),300)
    dim_cliente = pd.DataFrame({
        "id_cliente":   new_ids(n_cli),
        "nome":         [fake.company() for _ in range(n_cli)],
        "tipo":         random.choices(["PF","PJ"], weights=[40,60], k=n_cli),
        "uf":           [fake.state_abbr() for _ in range(n_cli)],
        "segmento":     random.choices(["Corporativo","Social","Musical","Esportivo","Educacional"], k=n_cli),
    })
    receita = rng.uniform(5_000, 2_000_000, n).round(2)
    custo   = (receita * rng.uniform(0.40, 0.80, n)).round(2)
    fato_evento = pd.DataFrame({
        "id_fato":          new_ids(n),
        "id_data":          rand_dates(start, end, n),
        "id_evento":        random.choices(dim_evento["id_evento"].tolist(), k=n),
        "id_cliente":       random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "ingressos_vendidos": rng.integers(10, 80_000, n),
        "receita_total":    receita,
        "custo_total":      custo,
        "lucro":            (receita - custo).round(2),
        "margem_pct":       ((receita-custo)/receita*100).round(1),
        "nps":              rng.uniform(0, 100, n).round(1),
        "cancelado":        random.choices([True,False], weights=[5,95], k=n),
        "canal_venda":      random.choices(["Online","Bilheteria","Agência","Corporativo"], k=n),
    })
    n_forn = int(n * 0.5)
    fato_fornecedor = pd.DataFrame({
        "id_forn_fato":     new_ids(n_forn),
        "id_data":          rand_dates(start, end, n_forn),
        "id_evento":        random.choices(dim_evento["id_evento"].tolist(), k=n_forn),
        "tipo_fornecedor":  random.choices(FORNECEDORES, k=n_forn),
        "valor_contratado": rng.uniform(500, 200_000, n_forn).round(2),
        "pago":             random.choices([True,False], weights=[75,25], k=n_forn),
    })
    return {"DimEvento": dim_evento, "DimCliente": dim_cliente,
            "FatoEvento": fato_evento, "FatoFornecedor": fato_fornecedor,
            "dCalendario": dcalendario(start, end)}
