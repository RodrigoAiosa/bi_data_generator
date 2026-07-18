"""generators/esportes.py — Setor Esportes & Entretenimento Esportivo."""
import random
from datetime import date
import pandas as pd
from faker import Faker
from .helpers import dcalendario, new_ids, rand_dates, rng

fake = Faker("pt_BR")

MODALIDADES = [
    "Futebol", "Vôlei", "Basquete", "Natação", "Atletismo",
    "Tênis", "MMA", "Ciclismo", "Futsal", "Handebol",
    "Beachvolei", "Surfe", "Judô", "Boxe", "eSports",
    "Automobilismo", "Rugby", "Skate", "Ginástica", "Remo",
]

POSICOES_FUTEBOL = [
    "Goleiro", "Lateral Direito", "Lateral Esquerdo", "Zagueiro",
    "Volante", "Meia", "Ponta Direita", "Ponta Esquerda", "Centroavante",
]

COMPETICOES = [
    "Campeonato Brasileiro Série A", "Copa do Brasil", "Copa Libertadores",
    "Campeonato Paulista", "Campeonato Carioca", "NBB", "Superliga Vôlei",
    "Liga Nacional Futsal", "Circuito Brasileiro Tênis", "UFC Brasil",
]

UFS_CLUBES = ["SP", "RJ", "MG", "RS", "PR", "SC", "BA", "PE", "CE", "GO"]


def gerar_esportes(n: int, start: date, end: date) -> dict[str, pd.DataFrame]:
    n_atletas    = min(n // 3 + 50, 800)
    n_clubes     = min(n // 8 + 20, 150)
    n_competicoes = len(COMPETICOES)

    dim_atleta = pd.DataFrame({
        "id_atleta":     new_ids(n_atletas),
        "nome":          [fake.name() for _ in range(n_atletas)],
        "cpf":           [fake.cpf() for _ in range(n_atletas)],
        "nascimento":    rand_dates(date(1980, 1, 1), date(2006, 12, 31), n_atletas),
        "nacionalidade": random.choices(["Brasileira", "Argentina", "Uruguaia", "Colombiana", "Portuguesa", "Outra"], weights=[70, 10, 5, 5, 5, 5], k=n_atletas),
        "modalidade":    random.choices(MODALIDADES, k=n_atletas),
        "posicao":       random.choices(POSICOES_FUTEBOL + ["N/A"], k=n_atletas),
        "salario_mes":   rng.uniform(1500, 5000000, n_atletas).round(2),
        "valor_mercado": rng.uniform(10000, 200000000, n_atletas).round(2),
        "rating":        rng.uniform(40, 99, n_atletas).round(1),
    })

    dim_clube = pd.DataFrame({
        "id_clube":       new_ids(n_clubes),
        "nome":           [f"Clube {fake.last_name()} {fake.random_int(1, 99)}" for _ in range(n_clubes)],
        "uf":             random.choices(UFS_CLUBES, k=n_clubes),
        "cidade":         [fake.city() for _ in range(n_clubes)],
        "fundacao_ano":   rng.integers(1900, 2010, n_clubes),
        "n_socios":       rng.integers(500, 150000, n_clubes),
        "estadio_cap":    rng.integers(1000, 80000, n_clubes),
        "receita_anual":  rng.uniform(500000, 2000000000, n_clubes).round(2),
        "divisao":        random.choices(["Série A", "Série B", "Série C", "Série D", "Regional"], k=n_clubes),
    })

    dim_competicao = pd.DataFrame({
        "id_competicao": new_ids(n_competicoes),
        "nome":          COMPETICOES,
        "modalidade":    random.choices(MODALIDADES, k=n_competicoes),
        "tipo":          random.choices(["Nacional", "Estadual", "Internacional", "Mundial"], k=n_competicoes),
        "n_times":       rng.integers(8, 64, n_competicoes),
        "premio_total":  rng.uniform(100000, 200000000, n_competicoes).round(2),
    })

    publico = rng.integers(0, 80000, n)
    gols_casa = rng.integers(0, 7, n)
    gols_fora = rng.integers(0, 7, n)

    fato = pd.DataFrame({
        "id_partida":         new_ids(n),
        "id_data":            rand_dates(start, end, n),
        "id_clube_casa":      random.choices(dim_clube["id_clube"].tolist(), k=n),
        "id_clube_fora":      random.choices(dim_clube["id_clube"].tolist(), k=n),
        "id_competicao":      random.choices(dim_competicao["id_competicao"].tolist(), k=n),
        "gols_casa":          gols_casa,
        "gols_fora":          gols_fora,
        "resultado":          ["Casa" if g > f else ("Fora" if f > g else "Empate") for g, f in zip(gols_casa, gols_fora)],
        "publico":            publico,
        "receita_bilheteria": (publico * rng.uniform(20, 300, n)).round(2),
        "receita_tv":         rng.uniform(50000, 10000000, n).round(2),
        "receita_patrocinio": rng.uniform(10000, 5000000, n).round(2),
        "cartoes_amarelos":   rng.integers(0, 8, n),
        "cartoes_vermelhos":  rng.integers(0, 3, n),
        "escanteios":         rng.integers(0, 20, n),
        "fase":               random.choices(["Fase de Grupos", "Oitavas", "Quartas", "Semifinal", "Final", "Rodada"], k=n),
    })

    return {
        "DimAtleta":     dim_atleta,
        "DimClube":      dim_clube,
        "DimCompeticao": dim_competicao,
        "FatoPartida":   fato,
        "dCalendario":   dcalendario(start, end),
    }
