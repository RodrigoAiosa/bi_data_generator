"""generators/laboratorio.py — Setor Laboratório & Diagnóstico."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

EXAMES        = ["Hemograma","Glicemia","Colesterol Total","TSH","PCR","Urina I","Creatinina","Cortisol",
                 "Vitamina D","Ferritina","PSA","Beta-HCG","HIV","Hepatite B","Covid-19 PCR","Dengue NS1"]
AREAS         = ["Hematologia","Bioquímica","Imunologia","Microbiologia","Hormônios","Urinálise","Genética","Parasitologia"]
STATUS_EXAME  = ["Coletado","Em análise","Liberado","Pendente de coleta","Cancelado"]
CONVENIOS     = ["Unimed","Bradesco Saúde","SulAmérica","Amil","Porto Seguro","Hapvida","Particular"]
METODOS       = ["Automatizado","Manual","PCR","Imunofluorescência","ELISA","Cultura","Citometria"]

def gerar_laboratorio(n, start, end):
    n = max(int(n), 1)
    n_pac = min(max(n//3,100),2000)
    dim_paciente = pd.DataFrame({
        "id_paciente":  new_ids(n_pac),
        "nome":         [fake.name() for _ in range(n_pac)],
        "cpf":          [fake.cpf() for _ in range(n_pac)],
        "data_nasc":    rand_dates(date(1940,1,1), date(2010,12,31), n_pac),
        "sexo":         random.choices(["M","F"], k=n_pac),
        "convenio":     random.choices(CONVENIOS, k=n_pac),
        "cidade":       [fake.city() for _ in range(n_pac)],
        "uf":           [fake.state_abbr() for _ in range(n_pac)],
    })
    n_exam = len(EXAMES)
    dim_exame = pd.DataFrame({
        "id_exame":     new_ids(n_exam),
        "nome":         EXAMES,
        "area":         random.choices(AREAS, k=n_exam),
        "metodo":       random.choices(METODOS, k=n_exam),
        "prazo_h":      rng.integers(1, 72, n_exam),
        "preco_lista":  rng.uniform(15, 500, n_exam).round(2),
        "requer_jejum": random.choices([True,False], weights=[40,60], k=n_exam),
    })
    status = random.choices(STATUS_EXAME, weights=[5,15,70,5,5], k=n)
    fato_exame = pd.DataFrame({
        "id_resultado":     new_ids(n),
        "id_data":          rand_dates(start, end, n),
        "id_paciente":      random.choices(dim_paciente["id_paciente"].tolist(), k=n),
        "id_exame":         random.choices(dim_exame["id_exame"].tolist(), k=n),
        "convenio":         random.choices(CONVENIOS, k=n),
        "status":           status,
        "valor_cobrado":    rng.uniform(15, 500, n).round(2),
        "valor_convenio":   rng.uniform(10, 400, n).round(2),
        "valor_paciente":   rng.uniform(0, 100, n).round(2),
        "tempo_resposta_h": rng.uniform(0.5, 72, n).round(1),
        "dentro_prazo":     random.choices([True,False], weights=[88,12], k=n),
        "critico":          random.choices([True,False], weights=[5,95], k=n),
        "resultado_normal": random.choices([True,False], weights=[75,25], k=n),
    })
    return {"DimPaciente": dim_paciente, "DimExame": dim_exame,
            "FatoExame": fato_exame, "dCalendario": dcalendario(start, end)}
