"""generators/estudio_tatuagem.py — Setor Estúdio de Tatuagem."""
import random
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng, fake_pool

fake = Faker("pt_BR")

ESTILOS = ["Realismo", "Blackwork", "Old School", "Aquarela", "Fineline", "Oriental", "Geométrico", "Lettering"]
PARTES_CORPO = ["Braço", "Perna", "Costas", "Peito", "Antebraço", "Mão", "Pescoço", "Costela"]
MOTIVOS_RETORNO = ["Retoque de Cor", "Retoque de Linha", "Remoção a Laser", "Cobertura (Cover-up)"]


def gerar_estudio_tatuagem(n, start, end):
    n = max(int(n), 1)

    n_tatuador = min(max(n // 100, 4), 300)
    dim_tatuador = pd.DataFrame({
        "id_tatuador":       new_ids(n_tatuador),
        "nome":              fake_pool(fake, "name", n_tatuador),
        "estilo_principal":  random.choices(ESTILOS, k=n_tatuador),
        "anos_experiencia":  rng.integers(1, 25, n_tatuador),
        "avaliacao_media":   rng.uniform(3.8, 5.0, n_tatuador).round(1),
    })

    n_cliente = min(max(n // 3, 150), 30000)
    dim_cliente = pd.DataFrame({
        "id_cliente":        new_ids(n_cliente),
        "nome":              fake_pool(fake, "name", n_cliente),
        "idade":             rng.integers(18, 70, n_cliente),
        "primeira_tatuagem": random.choices([True, False], weights=[35, 65], k=n_cliente),
    })

    fato_sessao = pd.DataFrame({
        "id_sessao":         new_ids(n),
        "id_data":           rand_dates(start, end, n),
        "id_tatuador":       random.choices(dim_tatuador["id_tatuador"].tolist(), k=n),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n),
        "estilo":            random.choices(ESTILOS, k=n),
        "parte_corpo":       random.choices(PARTES_CORPO, k=n),
        "horas":             rng.uniform(0.5, 8, n).round(1),
        "valor":             rng.uniform(150, 4500, n).round(2),
        "usou_anestesico_topico": random.choices([True, False], weights=[40, 60], k=n),
    })

    n_retorno = int(n * 0.12)
    fato_retorno = pd.DataFrame({
        "id_retorno":        new_ids(n_retorno),
        "id_data":           rand_dates(start, end, n_retorno),
        "id_tatuador":       random.choices(dim_tatuador["id_tatuador"].tolist(), k=n_retorno),
        "id_cliente":        random.choices(dim_cliente["id_cliente"].tolist(), k=n_retorno),
        "motivo":            random.choices(MOTIVOS_RETORNO, weights=[45, 25, 20, 10], k=n_retorno),
        "valor":             rng.uniform(0, 900, n_retorno).round(2),
        "gratuito":          random.choices([True, False], weights=[55, 45], k=n_retorno),
    })

    return {
        "DimTatuador": dim_tatuador,
        "DimCliente": dim_cliente,
        "FatoSessao": fato_sessao,
        "FatoRetorno": fato_retorno,
        "dCalendario": dcalendario(start, end),
    }
