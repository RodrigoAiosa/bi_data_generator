"""generators/franquias.py — Setor Franquias."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

SEGMENTOS     = ["Alimentação","Saúde/Beleza","Educação","Serviços","Vestuário","Pet","Tecnologia","Limpeza","Varejo Especializado"]
STATUS_UNID   = ["Ativa","Inadimplente","Em implantação","Encerrada","Suspensa"]
TIPOS_TAXA    = ["Royalty","Fundo de Marketing","Taxa Inicial","Taxa de Treinamento","Taxa Renovação"]

def gerar_franquias(n, start, end):
    n = max(int(n), 1)
    n_marc = 10
    dim_marca = pd.DataFrame({
        "id_marca":         new_ids(n_marc),
        "nome":             [fake.company() for _ in range(n_marc)],
        "segmento":         random.choices(SEGMENTOS, k=n_marc),
        "taxa_inicial":     rng.uniform(30_000, 500_000, n_marc).round(2),
        "royalty_pct":      rng.uniform(3, 10, n_marc).round(1),
        "mktg_pct":         rng.uniform(1, 4, n_marc).round(1),
        "total_unidades":   rng.integers(10, 800, n_marc),
        "fundacao_ano":     rng.integers(1990, 2020, n_marc),
    })
    n_unid = min(max(n//5,50),600)
    dim_unidade = pd.DataFrame({
        "id_unidade":       new_ids(n_unid),
        "id_marca":         random.choices(dim_marca["id_marca"].tolist(), k=n_unid),
        "franqueado":       [fake.name() for _ in range(n_unid)],
        "cnpj":             [fake.cnpj() for _ in range(n_unid)],
        "uf":               [fake.state_abbr() for _ in range(n_unid)],
        "cidade":           [fake.city() for _ in range(n_unid)],
        "status":           random.choices(STATUS_UNID, weights=[80,8,5,5,2], k=n_unid),
        "data_abertura":    rand_dates(date(2005,1,1), end, n_unid),
        "investimento_ini": rng.uniform(80_000, 600_000, n_unid).round(2),
        "area_m2":          rng.uniform(20, 300, n_unid).round(0),
    })
    fat = rng.uniform(20_000, 500_000, n).round(2)
    fato_desempenho = pd.DataFrame({
        "id_desempenho":    new_ids(n),
        "id_data":          rand_dates(start, end, n),
        "id_unidade":       random.choices(dim_unidade["id_unidade"].tolist(), k=n),
        "id_marca":         random.choices(dim_marca["id_marca"].tolist(), k=n),
        "faturamento":      fat,
        "royalty_valor":    (fat * rng.uniform(0.03, 0.10, n)).round(2),
        "mktg_valor":       (fat * rng.uniform(0.01, 0.04, n)).round(2),
        "custo_operacional":rng.uniform(10_000, 300_000, n).round(2),
        "lucro_liquido":    rng.uniform(-10_000, 200_000, n).round(2),
        "satisfacao_nps":   rng.uniform(0, 100, n).round(1),
        "inadimplente":     random.choices([True,False], weights=[8,92], k=n),
        "meta_atingida":    random.choices([True,False], weights=[65,35], k=n),
    })
    fato_taxa = pd.DataFrame({
        "id_taxa":          new_ids(int(n*0.4)),
        "id_data":          rand_dates(start, end, int(n*0.4)),
        "id_unidade":       random.choices(dim_unidade["id_unidade"].tolist(), k=int(n*0.4)),
        "tipo_taxa":        random.choices(TIPOS_TAXA, k=int(n*0.4)),
        "valor":            rng.uniform(500, 50_000, int(n*0.4)).round(2),
        "pago":             random.choices([True,False], weights=[88,12], k=int(n*0.4)),
        "vencimento":       rand_dates(start, end, int(n*0.4)),
    })
    return {"DimMarca": dim_marca, "DimUnidade": dim_unidade,
            "FatoDesempenho": fato_desempenho, "FatoTaxa": fato_taxa,
            "dCalendario": dcalendario(start, end)}
