"""generators/florestal.py — Setor Florestal & Papel & Celulose."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

ESPECIES      = ["Eucalipto","Pinus","Teca","Acácia","Seringueira","Araucária","Cedro","Mogno Africano"]
TIPOS_MANEJO  = ["Corte Raso","Desbaste","Reforma","Plantio","Inventário","Manutenção"]
PRODUTOS      = ["Celulose","Papel Kraft","MDF","Compensado","Carvão Vegetal","Tora","Lenha","Biomassa"]
STATUS_TALHAO = ["Em crescimento","Pronto para colheita","Colhido","Em replantio","Reserva legal"]
CERTIFICACOES = ["FSC","PEFC","Nenhuma","ISO 14001"]

def gerar_florestal(n, start, end):
    n = max(int(n), 1)
    n_faz = min(max(n//10,20),150)
    dim_fazenda = pd.DataFrame({
        "id_fazenda":       new_ids(n_faz),
        "nome":             [f"Fazenda {fake.last_name()}" for _ in range(n_faz)],
        "uf":               random.choices(["MS","MT","GO","SP","MG","BA","PR","SC","RS","PA"], k=n_faz),
        "area_ha":          rng.uniform(100, 50_000, n_faz).round(1),
        "certificacao":     random.choices(CERTIFICACOES, k=n_faz),
        "proprietario":     [fake.company() for _ in range(n_faz)],
        "ativa":            random.choices([True,False], weights=[90,10], k=n_faz),
    })
    n_tal = min(max(n//4,50),500)
    dim_talhao = pd.DataFrame({
        "id_talhao":        new_ids(n_tal),
        "id_fazenda":       random.choices(dim_fazenda["id_fazenda"].tolist(), k=n_tal),
        "especie":          random.choices(ESPECIES, k=n_tal),
        "area_ha":          rng.uniform(5, 500, n_tal).round(1),
        "idade_anos":       rng.uniform(0.5, 25, n_tal).round(1),
        "status":           random.choices(STATUS_TALHAO, k=n_tal),
        "iaf":              rng.uniform(1, 6, n_tal).round(2),
        "icc_m3_ha":        rng.uniform(10, 60, n_tal).round(1),
        "data_plantio":     rand_dates(date(2000,1,1), end, n_tal),
        "rotacao_anos":     rng.integers(5, 20, n_tal),
    })
    vol = rng.uniform(50, 5_000, n).round(1)
    preco_t = rng.uniform(80, 600, n).round(2)
    fato_producao = pd.DataFrame({
        "id_producao":      new_ids(n),
        "id_data":          rand_dates(start, end, n),
        "id_talhao":        random.choices(dim_talhao["id_talhao"].tolist(), k=n),
        "id_fazenda":       random.choices(dim_fazenda["id_fazenda"].tolist(), k=n),
        "tipo_manejo":      random.choices(TIPOS_MANEJO, k=n),
        "produto":          random.choices(PRODUTOS, k=n),
        "volume_m3":        vol,
        "volume_ton":       (vol * rng.uniform(0.4, 0.8, n)).round(1),
        "preco_ton":        preco_t,
        "receita":          (vol * rng.uniform(0.4,0.8,n) * preco_t).round(2),
        "custo_ha":         rng.uniform(500, 8_000, n).round(2),
        "produtividade_map":rng.uniform(20, 60, n).round(1),
        "carbono_ton":      (vol * rng.uniform(0.8, 1.8, n)).round(2),
    })
    return {"DimFazenda": dim_fazenda, "DimTalhao": dim_talhao,
            "FatoProducao": fato_producao, "dCalendario": dcalendario(start, end)}
