"""generators/imobiliario.py — Setor Imobiliário."""

import random
from datetime import date

import numpy as np
import pandas as pd
from faker import Faker

from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

CIDADES = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Florianópolis", "Brasília", "Salvador"]
BAIRROS = {
    "São Paulo": ["Pinheiros", "Moema", "Jardins", "Itaim Bibi", "Vila Madalena"],
    "Rio de Janeiro": ["Ipanema", "Leblon", "Copacabana", "Barra da Tijuca", "Botafogo"],
    "Curitiba": ["Batel", "Bigorrilho", "Centro Cívico", "Santa Felicidade"],
}

def gerar_imobiliario(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_clientes  = min(n, 5000)
    n_imoveis   = min(1000, n // 2 + 100)
    n_corretores = 40
    
    dim_cliente = pd.DataFrame({
        "id_cliente": new_ids(n_clientes),
        "nome":       [fake.name() for _ in range(n_clientes)],
        "cpf":        [fake.cpf() for _ in range(n_clientes)],
        "telefone":   [fake.phone_number() for _ in range(n_clientes)],
        "tipo":       random.choices(["Comprador", "Inquilino", "Investidor"], k=n_clientes)
    })

    tipos_imovel = ["Apartamento", "Casa", "Comercial", "Terreno", "Sobrado"]
    imoveis_lista = []
    for i in range(1, n_imoveis + 1):
        cidade = random.choice(CIDADES)
        bairro = random.choice(BAIRROS.get(cidade, ["Centro", "Bairro Novo", "Vila Real"]))
        imoveis_lista.append({
            "id_imovel": i,
            "tipo":      random.choice(tipos_imovel),
            "cidade":    cidade,
            "bairro":    bairro,
            "quartos":   rng.integers(1, 5),
            "vagas":     rng.integers(0, 3),
            "area_m2":   rng.integers(30, 500),
            "valor_estimado": rng.uniform(200000, 5000000, 1)[0].round(2)
        })
    dim_imovel = pd.DataFrame(imoveis_lista)

    dim_corretor = pd.DataFrame({
        "id_corretor": new_ids(n_corretores),
        "nome":        [fake.name() for _ in range(n_corretores)],
        "creci":       [f"CRECI-{rng.integers(10000, 99999)}" for _ in range(n_corretores)],
        "comissao_pct": rng.uniform(0.02, 0.06, n_corretores).round(3)
    })

    datas = rand_dates(start, end, n)
    imoveis_ids = random.choices(dim_imovel["id_imovel"].tolist(), k=n)
    valores_estimados = [dim_imovel.loc[dim_imovel["id_imovel"] == i, "valor_estimado"].values[0] for i in imoveis_ids]
    
    fato = pd.DataFrame({
        "id_transacao": new_ids(n),
        "id_data":      datas,
        "id_imovel":    imoveis_ids,
        "id_cliente":   random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "id_corretor":  random.choices(dim_corretor["id_corretor"].tolist(), k=n),
        "tipo_negocio": random.choices(["Venda", "Aluguel"], weights=[0.4, 0.6], k=n),
        "valor_final":  [round(v * rng.uniform(0.9, 1.1), 2) for v in valores_estimados],
        "forma_pagamento": random.choices(["Financiamento", "À Vista", "Parcelado"], k=n),
        "status":       random.choices(["Concluído", "Em Negociação", "Cancelado"], weights=[0.7, 0.2, 0.1], k=n)
    })

    return {
        "DimCliente":  dim_cliente,
        "DimImovel":   dim_imovel,
        "DimCorretor": dim_corretor,
        "FatoVendas":  fato,
        "dCalendario": dcalendario(start, end),
    }
