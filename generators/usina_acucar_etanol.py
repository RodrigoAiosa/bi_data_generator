"""generators/usina_acucar_etanol.py — Setor Usina de Açúcar & Etanol."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

VARIEDADES_CANA = ["RB92579", "RB867515", "RB966928", "SP81-3250", "CTC4", "CTC9001"]
TIPOS_PRODUTO = ["Açúcar Cristal", "Açúcar VHP", "Etanol Hidratado", "Etanol Anidro", "Bagaço para Bioenergia", "Melaço"]
DESTINOS_VENDA = ["Mercado Interno", "Exportação", "Distribuidora de Combustível", "Cogeração Própria"]


def gerar_usina_acucar_etanol(n, start, end):
    n = max(int(n), 1)

    n_usina = min(max(n // 800, 2), 25)
    dim_usina = pd.DataFrame({
        "id_usina":          new_ids(n_usina),
        "nome":              [f"Usina {fake.last_name()}" for _ in range(n_usina)],
        "uf":                [fake.state_abbr() for _ in range(n_usina)],
        "capacidade_moagem_ton_dia": rng.integers(3000, 40000, n_usina),
        "ano_inicio_operacao": rng.integers(1970, 2020, n_usina),
    })

    n_talhao = min(max(n // 20, 40), 4000)
    area_ha = rng.uniform(5, 250, n_talhao).round(1)
    dim_talhao = pd.DataFrame({
        "id_talhao":         new_ids(n_talhao),
        "id_usina":          random.choices(dim_usina["id_usina"].tolist(), k=n_talhao),
        "variedade_cana":    random.choices(VARIEDADES_CANA, k=n_talhao),
        "area_ha":           area_ha,
        "numero_corte":      rng.integers(1, 6, n_talhao),
        "irrigado":          random.choices([True, False], weights=[20, 80], k=n_talhao),
    })

    ton_cana = rng.uniform(20, 400, n).round(1)
    fato_moagem = pd.DataFrame({
        "id_moagem":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_usina":          random.choices(dim_usina["id_usina"].tolist(), k=n),
        "id_talhao":         random.choices(dim_talhao["id_talhao"].tolist(), k=n),
        "toneladas_cana":    ton_cana,
        "atr_kg_ton":        rng.uniform(110, 160, n).round(1),
        "rendimento_pct":    rng.uniform(78, 95, n).round(1),
        "chuva_mm":          rng.uniform(0, 40, n).round(1),
    })

    n_prod = int(n * 0.6)
    tipo_produto = random.choices(TIPOS_PRODUTO, weights=[25, 20, 25, 15, 10, 5], k=n_prod)
    fato_producao = pd.DataFrame({
        "id_producao":       new_ids(n_prod),
        "id_data":           rand_dates(start, end, n_prod),
        "id_usina":          random.choices(dim_usina["id_usina"].tolist(), k=n_prod),
        "tipo_produto":      tipo_produto,
        "volume":            rng.uniform(500, 50000, n_prod).round(1),
        "destino_venda":     random.choices(DESTINOS_VENDA, weights=[40, 25, 25, 10], k=n_prod),
        "preco_unitario":    rng.uniform(1.8, 4.5, n_prod).round(3),
    })

    return {
        "DimUsina": dim_usina,
        "DimTalhao": dim_talhao,
        "FatoMoagem": fato_moagem,
        "FatoProducao": fato_producao,
        "dCalendario": dcalendario(start, end),
    }
