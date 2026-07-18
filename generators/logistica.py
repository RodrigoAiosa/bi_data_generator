"""generators/logistica.py — Setor Logística."""

import random
from datetime import date

import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

UFS = ["SP","RJ","MG","RS","PR","SC","BA","CE","PE","GO"]


def gerar_logistica(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_trans    = 20
    n_clientes = min(n, 2000)
    n_rotas    = 50

    dim_transportadora = pd.DataFrame({
        "id_transportadora": new_ids(n_trans),
        "nome":              [f"Transportadora {fake.last_name()}" for _ in range(n_trans)],
        "cnpj":              [fake.cnpj() for _ in range(n_trans)],
        "tipo":              random.choices(["Rodoviário","Aéreo","Marítimo","Expresso"], k=n_trans),
        "uf_sede":           random.choices(UFS, k=n_trans),
    })

    dim_rota = pd.DataFrame({
        "id_rota":      new_ids(n_rotas),
        "origem_uf":    random.choices(UFS, k=n_rotas),
        "destino_uf":   random.choices(UFS, k=n_rotas),
        "distancia_km": rng.integers(50, 4000, n_rotas),
        "prazo_dias":   rng.integers(1, 15, n_rotas),
    })

    dim_cliente = pd.DataFrame({
        "id_cliente": new_ids(n_clientes),
        "empresa":    [fake.company() for _ in range(n_clientes)],
        "cnpj":       [fake.cnpj()   for _ in range(n_clientes)],
        "segmento":   random.choices(["Varejo","Indústria","E-commerce","Atacado"], k=n_clientes),
        "uf":         random.choices(UFS, k=n_clientes),
    })

    fato = pd.DataFrame({
        "id_entrega":        new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_transportadora": random.choices(dim_transportadora["id_transportadora"].tolist(), k=n),
        "id_rota":           random.choices(dim_rota["id_rota"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "peso_kg":           rng.uniform(0.1, 2000, n).round(2),
        "volume_m3":         rng.uniform(0.01, 50, n).round(3),
        "valor_frete":       rng.uniform(15, 5000, n).round(2),
        "prazo_acordado":    rng.integers(1, 15, n),
        "dias_entregue":     rng.integers(1, 20, n),
        "status":            random.choices(
            ["Entregue","Em trânsito","Atrasado","Devolvido"],
            weights=[65, 20, 10, 5], k=n,
        ),
    })

    return {
        "DimTransportadora": dim_transportadora,
        "DimRota":           dim_rota,
        "DimCliente":        dim_cliente,
        "FatoEntrega":       fato,
        "dCalendario":       dcalendario(start, end),
    }
