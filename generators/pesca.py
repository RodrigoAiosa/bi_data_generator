"""generators/pesca.py — Setor Pesca & Aquicultura."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

ESPECIES      = ["Tilápia","Salmão","Camarão","Tambaqui","Pintado","Atum","Sardinha","Bacalhau","Robalo","Truta","Pacu","Pirarucu"]
TIPOS_PESCA   = ["Aquicultura","Pesca Extrativista","Pesca Artesanal","Pesca Industrial"]
AMBIENTES     = ["Água Doce","Marinho","Estuário","Lagoa"]
STATUS_LOTE   = ["Em cultivo","Pronto para colheita","Colhido","Perdido"]
DESTINOS      = ["Exportação","Mercado Interno","Indústria","Varejo","Restaurantes"]
CERTIFICACOES = ["GlobalG.A.P","ASC","MSC","Sem certificação"]

def gerar_pesca(n, start, end):
    n = max(int(n), 1)
    n_unid = min(max(n//6,20),150)
    dim_unidade = pd.DataFrame({
        "id_unidade":       new_ids(n_unid),
        "nome":             [f"Piscicultura {fake.last_name()}" for _ in range(n_unid)],
        "tipo":             random.choices(TIPOS_PESCA, weights=[50,20,20,10], k=n_unid),
        "ambiente":         random.choices(AMBIENTES, k=n_unid),
        "uf":               random.choices(["AM","PA","MT","MS","SC","RS","RN","CE","BA","SP"], k=n_unid),
        "area_ha":          rng.uniform(0.5, 500, n_unid).round(1),
        "n_tanques":        rng.integers(1, 100, n_unid),
        "certificacao":     random.choices(CERTIFICACOES, k=n_unid),
        "ativa":            random.choices([True,False], weights=[88,12], k=n_unid),
    })
    n_esp = len(ESPECIES)
    dim_especie = pd.DataFrame({
        "id_especie":       new_ids(n_esp),
        "nome":             ESPECIES,
        "ambiente":         random.choices(AMBIENTES, k=n_esp),
        "ciclo_dias":       rng.integers(60, 730, n_esp),
        "preco_kg":         rng.uniform(8, 120, n_esp).round(2),
        "fcr":              rng.uniform(1.2, 2.5, n_esp).round(2),
    })
    peso = rng.uniform(100, 50_000, n).round(0)
    preco = rng.uniform(8, 120, n).round(2)
    fato_producao = pd.DataFrame({
        "id_producao":      new_ids(n),
        "id_data":          rand_dates(start, end, n),
        "id_unidade":       random.choices(dim_unidade["id_unidade"].tolist(), k=n),
        "id_especie":       random.choices(dim_especie["id_especie"].tolist(), k=n),
        "status_lote":      random.choices(STATUS_LOTE, weights=[40,20,35,5], k=n),
        "peso_kg":          peso,
        "preco_kg":         preco,
        "receita":          (peso * preco).round(2),
        "custo_producao":   rng.uniform(50, 30_000, n).round(2),
        "fcr_real":         rng.uniform(1.2, 3.0, n).round(2),
        "mortalidade_pct":  rng.uniform(0, 20, n).round(1),
        "destino":          random.choices(DESTINOS, k=n),
        "temp_agua_c":      rng.uniform(20, 32, n).round(1),
        "oxigenio_mgL":     rng.uniform(4, 10, n).round(1),
    })
    return {"DimUnidade": dim_unidade, "DimEspecie": dim_especie,
            "FatoProducao": fato_producao, "dCalendario": dcalendario(start, end)}
