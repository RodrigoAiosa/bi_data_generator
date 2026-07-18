"""generators/audiovisual.py — Setor Audiovisual & Produtora."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_PRODUCAO = ["Longa-metragem","Curta","Série","Documentário","Publicidade","Videoclipe","Institucional","Reality","Animação"]
GENEROS        = ["Drama","Comédia","Ação","Terror","Romance","Documentário","Ficção Científica","Suspense"]
PLATAFORMAS    = ["Netflix","Globoplay","Amazon Prime","Disney+","Canal aberto","Cinema","YouTube","SporTV"]
STATUS_PROJ    = ["Em desenvolvimento","Em produção","Pós-produção","Lançado","Cancelado"]
DEPARTAMENTOS  = ["Direção","Roteiro","Fotografia","Arte","Som","Efeitos Especiais","Elenco","Produção Executiva"]

def gerar_audiovisual(n, start, end):
    n = max(int(n), 1)
    n_proj = min(max(n//5,30),300)
    orcamento = rng.uniform(50_000, 50_000_000, n_proj).round(2)
    dim_projeto = pd.DataFrame({
        "id_projeto":       new_ids(n_proj),
        "titulo":           [f"{fake.word().capitalize()} {fake.word().capitalize()}" for _ in range(n_proj)],
        "tipo":             random.choices(TIPOS_PRODUCAO, k=n_proj),
        "genero":           random.choices(GENEROS, k=n_proj),
        "status":           random.choices(STATUS_PROJ, weights=[15,25,20,35,5], k=n_proj),
        "plataforma":       random.choices(PLATAFORMAS, k=n_proj),
        "orcamento":        orcamento,
        "duracao_min":      rng.integers(3, 180, n_proj),
        "data_inicio":      rand_dates(start, end, n_proj),
        "data_entrega":     rand_dates(start, end, n_proj),
        "diretor":          [fake.name() for _ in range(n_proj)],
    })
    n_rec = min(max(n//4,40),300)
    dim_recurso = pd.DataFrame({
        "id_recurso":       new_ids(n_rec),
        "nome":             [fake.name() for _ in range(n_rec)],
        "funcao":           random.choices(DEPARTAMENTOS, k=n_rec),
        "diaria":           rng.uniform(200, 5_000, n_rec).round(2),
        "pj":               random.choices([True,False], weights=[70,30], k=n_rec),
    })
    custo = rng.uniform(10_000, 20_000_000, n).round(2)
    receita = rng.uniform(0, 30_000_000, n).round(2)
    fato_producao = pd.DataFrame({
        "id_producao":      new_ids(n),
        "id_data":          rand_dates(start, end, n),
        "id_projeto":       random.choices(dim_projeto["id_projeto"].tolist(), k=n),
        "departamento":     random.choices(DEPARTAMENTOS, k=n),
        "custo_realizado":  custo,
        "custo_orcado":     (custo * rng.uniform(0.8, 1.3, n)).round(2),
        "horas_producao":   rng.uniform(1, 1000, n).round(1),
        "diarias_filmagem": rng.integers(0, 60, n),
        "views_total":      rng.integers(0, 50_000_000, n),
        "receita":          receita,
        "roi_pct":          ((receita - custo) / (custo + 1) * 100).round(1),
        "premiado":         random.choices([True,False], weights=[10,90], k=n),
    })
    return {"DimProjeto": dim_projeto, "DimRecurso": dim_recurso,
            "FatoProducao": fato_producao, "dCalendario": dcalendario(start, end)}
