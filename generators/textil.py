"""generators/textil.py — Setor Têxtil & Confecção."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

FIBRAS        = ["Algodão","Poliéster","Viscose","Nylon","Lã","Seda","Linho","Elastano","Acrílico","Modal"]
PROCESSOS     = ["Fiação","Tecelagem","Malharia","Tinturaria","Estamparia","Acabamento","Corte e Costura"]
TIPOS_PRODUTO = ["Fio","Tecido Plano","Malha","Linha","Não-Tecido","Confeccionado"]
CLIENTES_TIPO = ["Confecção","Atacado","Varejista","Exportação","Industria Automotiva","Cama/Mesa/Banho"]
CERTIFICACOES = ["OEKO-TEX","GOTS","BCI","Nenhuma","ISO 9001"]

def gerar_textil(n, start, end):
    n = max(int(n), 1)
    n_maq = min(max(n//8,20),150)
    dim_maquina = pd.DataFrame({
        "id_maquina":       new_ids(n_maq),
        "nome":             [f"Máquina {fake.last_name()}-{rng.integers(100,999)}" for _ in range(n_maq)],
        "tipo":             random.choices(PROCESSOS, k=n_maq),
        "fabricante":       random.choices(["Picanol","Stäubli","Rieter","Truetzschler","Groz-Beckert"], k=n_maq),
        "ano_fabr":         rng.integers(1995, 2023, n_maq),
        "capacidade_dia":   rng.uniform(100, 5_000, n_maq).round(0),
        "eficiencia_meta":  rng.uniform(75, 95, n_maq).round(1),
        "ativa":            random.choices([True,False], weights=[88,12], k=n_maq),
    })
    n_prod = min(max(n//6,50),400)
    dim_produto = pd.DataFrame({
        "id_produto":       new_ids(n_prod),
        "descricao":        [f"{random.choice(FIBRAS)} {random.choice(TIPOS_PRODUTO)}" for _ in range(n_prod)],
        "tipo":             random.choices(TIPOS_PRODUTO, k=n_prod),
        "fibra_principal":  random.choices(FIBRAS, k=n_prod),
        "gramatura_gm2":    rng.uniform(80, 500, n_prod).round(0),
        "certificacao":     random.choices(CERTIFICACOES, k=n_prod),
        "preco_kg":         rng.uniform(10, 120, n_prod).round(2),
    })
    n_cli = min(max(n//6,30),200)
    dim_cliente = pd.DataFrame({
        "id_cliente":       new_ids(n_cli),
        "nome":             [fake.company() for _ in range(n_cli)],
        "tipo":             random.choices(CLIENTES_TIPO, k=n_cli),
        "uf":               [fake.state_abbr() for _ in range(n_cli)],
        "exporta":          random.choices([True,False], weights=[25,75], k=n_cli),
    })
    vol = rng.uniform(100, 50_000, n).round(0)
    preco = rng.uniform(10, 120, n).round(2)
    fato_producao = pd.DataFrame({
        "id_producao":      new_ids(n),
        "id_data":          rand_dates(start, end, n),
        "id_maquina":       random.choices(dim_maquina["id_maquina"].tolist(), k=n),
        "id_produto":       random.choices(dim_produto["id_produto"].tolist(), k=n),
        "id_cliente":       random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "processo":         random.choices(PROCESSOS, k=n),
        "volume_kg":        vol,
        "preco_kg":         preco,
        "receita":          (vol * preco).round(2),
        "custo_producao":   rng.uniform(500, 1_500_000, n).round(2),
        "eficiencia_pct":   rng.uniform(60, 98, n).round(1),
        "refugo_pct":       rng.uniform(0, 10, n).round(1),
        "horas_maquina":    rng.uniform(1, 720, n).round(1),
        "parada_h":         rng.uniform(0, 48, n).round(1),
    })
    return {"DimMaquina": dim_maquina, "DimProduto": dim_produto, "DimCliente": dim_cliente,
            "FatoProducao": fato_producao, "dCalendario": dcalendario(start, end)}
