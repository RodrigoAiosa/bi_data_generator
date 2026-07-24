"""
generators/case_negocio.py: gera um case de negócio fictício para acompanhar a base.

Transforma a base gerada em um exercício com objetivo: em vez de só entregar
tabelas soltas, entrega um problema de negócio fictício pra resolver, que se
adapta conforme o modo anomalia / deriva temporal estejam ativos ou não.
"""
import random
from faker import Faker

fake_pt = Faker("pt_BR")
fake_en = Faker("en_US")

_GATILHOS_NORMAL_PT = [
    "a diretoria quer entender os principais fatores por trás do desempenho de {kpi} nos últimos meses",
    "o board pediu um panorama completo de {kpi} antes da reunião trimestral",
    "a área comercial precisa de um raio-x de {kpi} para redefinir metas do próximo trimestre",
    "o novo CEO quer, já na primeira semana, um retrato claro de como {kpi} vem se comportando",
]
_GATILHOS_ANOMALIA_PT = [
    "algo estranho aconteceu com {kpi} em um período específico, e ninguém na empresa sabe explicar por quê",
    "a margem de alguns registros despencou de forma repentina, e o financeiro está pressionando por respostas",
    "um recorte do período fugiu completamente do padrão histórico de {kpi}, e a diretoria suspeita de erro operacional",
    "poucos registros aparecem com valores muito fora da curva, e ninguém sabe se é erro de sistema ou fraude",
]
_GATILHOS_DRIFT_PT = [
    "um segmento específico vem ganhando espaço aos poucos, silenciosamente, e a empresa só percebeu agora",
    "a composição interna dos dados mudou gradualmente ao longo do período, sem nenhum evento único que explique",
]
_DESAFIO_PT = (
    "Seu desafio: usar os dados gerados para construir uma análise que explique o que está acontecendo "
    "e apresente uma recomendação clara para a diretoria."
)

_GATILHOS_NORMAL_EN = [
    "leadership wants to understand the key drivers behind {kpi} over the last few months",
    "the board asked for a full overview of {kpi} before the quarterly meeting",
    "the sales team needs a deep dive into {kpi} to redefine next quarter's targets",
    "the new CEO wants, in the first week, a clear picture of how {kpi} has been behaving",
]
_GATILHOS_ANOMALIA_EN = [
    "something odd happened to {kpi} during a specific period, and nobody in the company can explain why",
    "margins on some records dropped suddenly, and finance is pushing for answers",
    "one stretch of the period completely broke from the historical pattern of {kpi}, and leadership suspects an operational error",
    "a handful of records show values way outside the normal range, and nobody knows if it's a system error or fraud",
]
_GATILHOS_DRIFT_EN = [
    "one specific segment has been quietly gaining ground, and the company only just noticed",
    "the underlying composition of the data shifted gradually over the period, with no single event that explains it",
]
_DESAFIO_EN = (
    "Your challenge: use the generated data to build an analysis that explains what's happening "
    "and present a clear recommendation to leadership."
)


def gerar_case_negocio(nome_setor: str, kpi_label: str, lang: str = "pt",
                        anomalia_ativa: bool = False, drift_ativo: bool = False) -> str:
    """
    Gera um parágrafo de case de negócio fictício, adaptado ao setor e ao
    modo ativo (anomalia / deriva temporal / nenhum dos dois).
    """
    setor_txt = nome_setor.split(" ", 1)[1] if " " in nome_setor else nome_setor

    if lang == "en":
        empresa = fake_en.company()
        if drift_ativo:
            gatilho = random.choice(_GATILHOS_DRIFT_EN)
        elif anomalia_ativa:
            gatilho = random.choice(_GATILHOS_ANOMALIA_EN)
        else:
            gatilho = random.choice(_GATILHOS_NORMAL_EN)
        gatilho = gatilho.format(kpi=kpi_label)
        return (
            f"You've just been hired as a BI Analyst at **{empresa}**, a company in the "
            f"**{setor_txt}** sector. In your first week, {gatilho}. {_DESAFIO_EN}"
        )

    empresa = fake_pt.company()
    if drift_ativo:
        gatilho = random.choice(_GATILHOS_DRIFT_PT)
    elif anomalia_ativa:
        gatilho = random.choice(_GATILHOS_ANOMALIA_PT)
    else:
        gatilho = random.choice(_GATILHOS_NORMAL_PT)
    gatilho = gatilho.format(kpi=kpi_label)
    return (
        f"Você acaba de ser contratado(a) como Analista de BI na **{empresa}**, uma empresa do setor de "
        f"**{setor_txt}**. Na sua primeira semana, {gatilho}. {_DESAFIO_PT}"
    )


def detectar_kpi_label(tabelas: dict) -> str:
    """Acha a coluna numérica mais provável de ser o KPI principal, formatada como rótulo."""
    fato_key = next((k for k in tabelas if k.startswith("Fato")), None)
    if not fato_key:
        return "desempenho geral"
    fato = tabelas[fato_key]
    num_cols = fato.select_dtypes(include="number").columns.tolist()
    if not num_cols:
        return "desempenho geral"
    val_col = next(
        (c for c in num_cols if any(k in c.lower() for k in ["valor", "receita", "preco", "preço", "total", "mrr"])),
        num_cols[0],
    )
    return val_col.replace("_", " ").title()
