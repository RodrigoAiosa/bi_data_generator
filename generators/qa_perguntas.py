"""
generators/qa_perguntas.py — catálogo de perguntas da aba "Pergunte aos Dados".

Monta, para o setor/dados já gerados, a lista de perguntas que o motor de
generators/qa_engine.py realmente consegue responder (contagens, totais,
médias, maior/menor, ticket médio, por ano/mês, comparações entre períodos,
rankings por dimensão e por período, filtros por categoria).

Cada pergunta candidata é EXECUTADA no motor antes de entrar na lista: só
ficam as que ele entende e que resolvem para a coluna/dimensão esperada. Assim
quem escolhe na lista nunca cai no "Não consegui entender essa pergunta".
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from generators.qa_engine import (
    _achar_periodos_mencionados,
    _medidas_disponiveis,
    _norm,
    _tabela_calendario,
    _tabelas_dim,
    _tabelas_fato,
    responder_pergunta,
)

MAX_MEDIDAS = 6
MAX_DIMENSOES = 5
MAX_ANOS = 6
MAX_FILTROS_POR_COLUNA = 4
MAX_COLUNAS_FILTRO = 3

CAT_GERAIS = "📋 Visão geral"
CAT_MEDIDAS = "🧮 Totais, médias e extremos"
CAT_PERIODO = "📅 Por período"
CAT_COMPARACAO = "⚖️ Comparações"
CAT_RANKING_PERIODO = "🏆 Qual período teve…"
CAT_RANKING_DIM = "🥇 Quem teve o maior/menor…"
CAT_FILTRO = "🔎 Filtrando por categoria"

_ORDEM = [CAT_GERAIS, CAT_MEDIDAS, CAT_PERIODO, CAT_COMPARACAO,
          CAT_RANKING_PERIODO, CAT_RANKING_DIM, CAT_FILTRO]


@dataclass(frozen=True)
class PerguntaSugerida:
    categoria: str
    texto: str
    esperado: tuple[str, ...] = ()  # trechos que a medida DAX gerada deve conter


def _rotulo(coluna: str) -> str:
    return coluna.replace("_", " ")


def _candidatas(tabelas: dict[str, pd.DataFrame]) -> list[PerguntaSugerida]:
    fatos = _tabelas_fato(tabelas)
    if not fatos:
        return []
    fato = fatos[0]  # o motor responde sobre a primeira fato
    df = tabelas[fato]
    medidas = _medidas_disponiveis(df)[:MAX_MEDIDAS]
    principais = medidas[:2]
    out: list[PerguntaSugerida] = [
        PerguntaSugerida(CAT_GERAIS, "Quantos registros existem?", (f"COUNTROWS({fato})",)),
    ]

    # Totais, médias, maior, menor, ticket médio
    for m in medidas:
        r = _rotulo(m)
        col = f"{fato}[{m}]"
        out += [
            PerguntaSugerida(CAT_MEDIDAS, f"Qual foi o total de {r}?", (f"SUM({col})",)),
            PerguntaSugerida(CAT_MEDIDAS, f"Qual foi a média de {r}?", (f"AVERAGE({col})",)),
            PerguntaSugerida(CAT_MEDIDAS, f"Qual foi o maior valor de {r}?", (f"MAX({col})",)),
            PerguntaSugerida(CAT_MEDIDAS, f"Qual foi o menor valor de {r}?", (f"MIN({col})",)),
        ]
    for m in principais:
        out.append(PerguntaSugerida(CAT_MEDIDAS, f"Qual é o ticket médio de {_rotulo(m)}?",
                                    (f"SUM({fato}[{m}])", f"COUNTROWS({fato})")))

    # Por período (anos e meses realmente existentes)
    cal = _tabela_calendario(tabelas)
    if cal and fato:
        cal_df = tabelas[cal]
        anos = sorted(int(a) for a in cal_df["Ano"].dropna().unique()) if "Ano" in cal_df.columns else []
        # só anos com dados na fato (via coluna de data) — a validação por execução confirma
        anos = anos[:MAX_ANOS]
        for a in anos:
            out.append(PerguntaSugerida(CAT_PERIODO, f"Quantos registros existem em {a}?", (f"COUNTROWS({fato})",)))
            for m in principais:
                out.append(PerguntaSugerida(CAT_PERIODO, f"Qual foi o total de {_rotulo(m)} em {a}?",
                                            (f"SUM({fato}[{m}])",)))
        if principais and "MesAno" in cal_df.columns:
            m = principais[0]
            meses = list(dict.fromkeys(cal_df["MesAno"].dropna().tolist()))[:24]
            for mes in meses:
                out.append(PerguntaSugerida(CAT_PERIODO, f"Qual foi o total de {_rotulo(m)} em {mes}?",
                                            (f"SUM({fato}[{m}])",)))
        # Comparações entre anos consecutivos e mesmo mês em anos diferentes
        if principais:
            m = principais[0]
            for a1, a2 in zip(anos, anos[1:]):
                out.append(PerguntaSugerida(CAT_COMPARACAO, f"Comparar total de {_rotulo(m)} de {a1} vs {a2}",
                                            (f"{fato}[{m}]",)))
            if "MesAno" in cal_df.columns and len(anos) >= 2:
                validos = set(cal_df["MesAno"].dropna())
                for mes in ("Jan", "Jul"):
                    a1, a2 = str(anos[0])[-2:], str(anos[1])[-2:]
                    if f"{mes}/{a1}" in validos and f"{mes}/{a2}" in validos:
                        out.append(PerguntaSugerida(
                            CAT_COMPARACAO,
                            f"Comparar total de {_rotulo(m)} de {mes}/{a1} vs {mes}/{a2}",
                            (f"{fato}[{m}]",)))

        # Ranking por período
        for periodo, colunas in (("mês", "MesAno"), ("trimestre", "Trimestre"),
                                 ("semestre", "Semestre"), ("ano", "Ano")):
            if colunas not in cal_df.columns:
                continue
            for m in principais:
                for sup in ("maior", "menor"):
                    out.append(PerguntaSugerida(
                        CAT_RANKING_PERIODO,
                        f"Qual {periodo} teve o {sup} total de {_rotulo(m)}?", ("__periodo__",)))
            out.append(PerguntaSugerida(CAT_RANKING_PERIODO,
                                        f"Qual {periodo} teve o maior número de registros?", ("__periodo__",)))

    # Ranking por dimensão
    for dim in _tabelas_dim(tabelas)[:MAX_DIMENSOES]:
        nome = dim[3:].lower()
        for m in principais:
            for sup in ("maior", "menor"):
                out.append(PerguntaSugerida(CAT_RANKING_DIM, f"Qual {nome} teve o {sup} total de {_rotulo(m)}?",
                                            (f"{dim}[",)))
            out.append(PerguntaSugerida(CAT_RANKING_DIM, f"Qual {nome} teve a maior média de {_rotulo(m)}?",
                                        (f"{dim}[",)))
        out.append(PerguntaSugerida(CAT_RANKING_DIM, f"Qual {nome} teve o maior número de registros?", (f"{dim}[",)))

    # Filtro por categoria: valores de colunas de texto de baixa cardinalidade
    colunas_filtro = 0
    for nome_tab, tdf in tabelas.items():
        if nome_tab.startswith("d") and not nome_tab.startswith("Dim") and not nome_tab.startswith("Fato"):
            continue  # calendário
        for c in tdf.columns:
            if colunas_filtro >= MAX_COLUNAS_FILTRO:
                break
            cl = c.lower()
            if cl.startswith(("id_", "sk_")) or not pd.api.types.is_string_dtype(tdf[c]):
                continue
            if any(k in cl for k in ["nome", "email", "cpf", "cnpj", "endereco", "descricao",
                                      "url", "telefone", "cep", "senha"]):
                continue
            vals = [str(v) for v in tdf[c].dropna().unique() if len(_norm(str(v))) >= 3]
            if not 2 <= len(vals) <= 20:
                continue
            colunas_filtro += 1
            for v in vals[:MAX_FILTROS_POR_COLUNA]:
                out.append(PerguntaSugerida(CAT_FILTRO, f"Quantos registros existem em {v}?",
                                            (f'{nome_tab}[{c}]="{v}"',)))
                for m in principais[:1]:
                    out.append(PerguntaSugerida(CAT_FILTRO, f"Qual foi o total de {_rotulo(m)} em {v}?",
                                                (f'{nome_tab}[{c}]="{v}"', f"SUM({fato}[{m}])")))
    return out


def _confere(p: PerguntaSugerida, resp, tabelas: dict) -> bool:
    if not resp.entendida:
        return False
    if p.esperado == ("__periodo__",):
        # ranking temporal: a resposta precisa vir agrupada por período (tabela com ≥2 linhas)
        return resp.tabela_resultado is not None and len(resp.tabela_resultado) >= 2
    dax = resp.medida_dax or ""
    return all(trecho in dax for trecho in p.esperado)


def gerar_catalogo(tabelas: dict[str, pd.DataFrame]) -> list[PerguntaSugerida]:
    """Perguntas VALIDADAS (executadas no motor) para os dados do setor, sem
    repetição e agrupadas por categoria."""
    vistas: set[str] = set()
    validas: list[PerguntaSugerida] = []
    for p in _candidatas(tabelas):
        chave = _norm(p.texto)
        if chave in vistas:
            continue
        vistas.add(chave)
        try:
            resp = responder_pergunta(p.texto, tabelas)
        except Exception:
            continue
        if _confere(p, resp, tabelas):
            validas.append(p)
    validas.sort(key=lambda p: _ORDEM.index(p.categoria))
    return validas
