"""generators/logistica_urbana.py — Setor Logística Urbana & Last Mile."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

TIPOS_VEICULO  = ["Moto","Bicicleta Cargo","Van","Micro-ônibus","Caminhão Leve","Drône","Patinete Cargo"]
STATUS_ENTREGA = ["Em rota","Entregue","Tentativa falha","Devolvido","Extraviado","Aguardando retirada"]
MOTIVOS_FALHA  = ["Destinatário ausente","Endereço não encontrado","Acesso negado","Recusado","Chuva/Trânsito"]
JANELAS        = ["8h-12h","12h-18h","18h-22h","Manhã","Tarde","Noite","Same-day","Next-day"]
SEGMENTOS      = ["E-commerce","Farmácias","Restaurantes","Supermercados","B2B","Documentos","Eletrônicos"]
HUBS           = [f"Hub {fake.city()}" for _ in range(15)]

def gerar_logistica_urbana(n, start, end):
    n = max(int(n), 1)
    n_entg = min(max(n//5,30),250)
    dim_entregador = pd.DataFrame({
        "id_entregador":    new_ids(n_entg),
        "nome":             [fake.name() for _ in range(n_entg)],
        "tipo_veiculo":     random.choices(TIPOS_VEICULO, weights=[40,10,25,5,10,5,5], k=n_entg),
        "hub":              random.choices(HUBS, k=n_entg),
        "uf":               [fake.state_abbr() for _ in range(n_entg)],
        "avaliacao_media":  rng.uniform(3.0, 5.0, n_entg).round(2),
        "entregas_total":   rng.integers(10, 10_000, n_entg),
        "taxa_sucesso_pct": rng.uniform(75, 99, n_entg).round(1),
        "ativo":            random.choices([True,False], weights=[85,15], k=n_entg),
    })
    n_cli = min(max(n//8,30),200)
    dim_cliente = pd.DataFrame({
        "id_cliente":       new_ids(n_cli),
        "nome":             [fake.company() for _ in range(n_cli)],
        "segmento":         random.choices(SEGMENTOS, k=n_cli),
        "uf":               [fake.state_abbr() for _ in range(n_cli)],
        "cidade":           [fake.city() for _ in range(n_cli)],
        "sla_horas":        random.choices([1, 2, 4, 8, 24, 48], k=n_cli),
        "volume_mensal":    rng.integers(50, 50_000, n_cli),
    })
    status = random.choices(STATUS_ENTREGA, weights=[10,65,12,8,2,3], k=n)
    falha  = [s in ["Tentativa falha","Devolvido","Extraviado"] for s in status]
    fato_entrega = pd.DataFrame({
        "id_entrega":       new_ids(n),
        "id_data":          rand_dates(start, end, n),
        "id_entregador":    random.choices(dim_entregador["id_entregador"].tolist(), k=n),
        "id_cliente":       random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "status":           status,
        "janela_entrega":   random.choices(JANELAS, k=n),
        "falha":            falha,
        "motivo_falha":     [random.choice(MOTIVOS_FALHA) if f else "N/A" for f in falha],
        "distancia_km":     rng.uniform(0.5, 50, n).round(1),
        "tempo_rota_min":   rng.uniform(5, 180, n).round(0),
        "peso_kg":          rng.uniform(0.1, 50, n).round(1),
        "valor_frete":      rng.uniform(3, 80, n).round(2),
        "dentro_sla":       random.choices([True,False], weights=[82,18], k=n),
        "avaliacao":        [round(rng.uniform(1,5),1) if s=="Entregue" else None for s in status],
        "tentativas":       rng.integers(1, 4, n),
    })
    return {"DimEntregador": dim_entregador, "DimCliente": dim_cliente,
            "FatoEntrega": fato_entrega, "dCalendario": dcalendario(start, end)}
