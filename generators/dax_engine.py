"""
generators/dax_engine.py — DAX Sandbox: avalia um subconjunto pedagógico de
DAX de verdade contra os DataFrames gerados pelo app.

Não é um motor de DAX completo (isso é o trabalho de anos do próprio motor
do Power BI/Analysis Services). É um subconjunto deliberadamente pequeno,
mas real: as funções e padrões mais comuns usados em sala de aula e no
PL-300 — SUM, AVERAGE, MIN, MAX, COUNTROWS, DISTINCTCOUNT, DIVIDE e
CALCULATE com filtros (inclusive filtros em tabelas Dim relacionadas via
FK) — calculados de verdade em cima dos dados reais, não apenas formatados
como texto.

Uso:
    valor, passos = avaliar_medida("DIVIDE(SUM(FatoVendas[valor_total]), COUNTROWS(FatoVendas))", tabelas)
"""

from __future__ import annotations

import re

import pandas as pd

_REF_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_ ]*)\[([^\]]+)\]$")
_NUM_RE = re.compile(r"^-?\d+(\.\d+)?$")
_FILTRO_RE = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_ ]*)\[([^\]]+)\]\s*(<>|!=|>=|<=|==|=|>|<)\s*(.+?)\s*$"
)

_FUNCOES_AGREGACAO = {"SUM", "AVERAGE", "MIN", "MAX"}
_FUNCOES_CONHECIDAS = _FUNCOES_AGREGACAO | {"COUNTROWS", "DISTINCTCOUNT", "DIVIDE", "CALCULATE"}


class DaxError(ValueError):
    """Erro amigável de avaliação de DAX (sintaxe não suportada ou dado inválido)."""


# ── Utilidades de parsing (respeitando parênteses e aspas aninhadas) ─────────
def _split_args(s: str) -> list[str]:
    """Divide os argumentos de uma chamada de função pela vírgula de nível 0."""
    resultado = _tokenizar(s, ",")
    return [s] if resultado is None else resultado[0]


def _tokenizar(expr: str, operadores_alvo: str) -> tuple[list[str], list[str]] | None:
    """Divide expr nos operadores de `operadores_alvo` que estão no nível 0 de
    parênteses/aspas, tratando +/- unário corretamente (não divide quando o
    sinal é unário, ex.: '-5' ou 'SUM(...) * -1'). Retorna (fatores, operadores)
    com len(fatores) == len(operadores) + 1, ou None se expr é um fator único
    (nenhum operador de nível 0 encontrado)."""
    fatores, operadores = [], []
    atual, profundidade, em_aspas = "", 0, False
    i = 0
    while i < len(expr):
        c = expr[i]
        if c in "\"'":
            em_aspas = not em_aspas
            atual += c
        elif em_aspas:
            atual += c
        elif c == "(":
            profundidade += 1
            atual += c
        elif c == ")":
            profundidade -= 1
            atual += c
        elif profundidade == 0 and c in operadores_alvo:
            anterior = atual.strip()
            eh_unario = c in "+-" and (anterior == "" or anterior[-1] in "(+-*/,")
            if eh_unario:
                atual += c
            else:
                fatores.append(atual)
                operadores.append(c)
                atual = ""
        else:
            atual += c
        i += 1
    fatores.append(atual)
    if not operadores:
        return None
    return fatores, operadores


def _remove_parenteses_externos(s: str) -> str:
    s = s.strip()
    if s.startswith("(") and s.endswith(")"):
        profundidade = 0
        for i, c in enumerate(s):
            if c == "(":
                profundidade += 1
            elif c == ")":
                profundidade -= 1
                if profundidade == 0 and i < len(s) - 1:
                    return s  # fechou antes do final -> não é um par externo só
        return _remove_parenteses_externos(s[1:-1])
    return s


def _parse_ref(ref: str, tabelas: dict[str, pd.DataFrame]) -> tuple[str, str]:
    m = _REF_RE.match(ref.strip())
    if not m:
        raise DaxError(f"Referência inválida: '{ref}'. Use o formato Tabela[Coluna].")
    tabela, coluna = m.group(1).strip(), m.group(2).strip()
    if tabela not in tabelas:
        raise DaxError(f"Tabela '{tabela}' não existe neste setor.")
    if coluna not in tabelas[tabela].columns:
        raise DaxError(f"Coluna '{coluna}' não existe na tabela '{tabela}'.")
    return tabela, coluna


# ── Detecção de relacionamento FK (mesma heurística usada em relatorios_gerenciais.py) ──
def _detectar_fk(tabela_fato: str, tabela_dim: str, tabelas: dict[str, pd.DataFrame]) -> tuple[str, str] | None:
    """Retorna (coluna_fk_no_fato, coluna_pk_na_dim) se achar uma relação, senão None."""
    if tabela_dim not in tabelas or tabela_fato not in tabelas:
        return None
    dim_df = tabelas[tabela_dim]
    pk_dim = dim_df.columns[0]
    fk_cols = [c for c in tabelas[tabela_fato].columns if c.lower().startswith(("id_", "sk_"))]

    # 1) Prioridade máxima: mesmo nome exato da coluna-chave (ex.:
    # FatoProjeto.id_profissional == DimEquipe.id_profissional) — mais
    # confiável do que comparar com o nome da tabela, que pode não ter
    # nada a ver com o nome da própria coluna-chave.
    for col in fk_cols:
        if col.lower() == pk_dim.lower():
            return col, pk_dim

    # 2) Fallback: heurística de sufixo por nome da tabela.
    sufixo_dim = tabela_dim[3:].lower() if tabela_dim.startswith("Dim") else tabela_dim.lower()
    for col in fk_cols:
        sufixo_col = col.split("_", 1)[1] if "_" in col else col[3:]
        if sufixo_col.lower() in sufixo_dim or sufixo_dim in sufixo_col.lower():
            return col, pk_dim
    return None


def _comparar(serie: pd.Series, operador: str, valor_bruto: str) -> pd.Series:
    valor_bruto = valor_bruto.strip()
    if valor_bruto[:1] in "\"'" and valor_bruto[-1:] in "\"'":
        valor: object = valor_bruto[1:-1]
    elif _NUM_RE.match(valor_bruto):
        valor = float(valor_bruto)
    else:
        valor = valor_bruto  # trata como texto sem aspas mesmo

    s = serie
    if isinstance(valor, float) and pd.api.types.is_numeric_dtype(s):
        pass
    else:
        s = s.astype(str)
        valor = str(valor)

    if operador in ("=", "=="):
        return s == valor
    if operador in ("<>", "!="):
        return s != valor
    if operador == ">":
        return s > valor
    if operador == "<":
        return s < valor
    if operador == ">=":
        return s >= valor
    if operador == "<=":
        return s <= valor
    raise DaxError(f"Operador não suportado: '{operador}'.")


def _parse_filtro(expr_filtro: str) -> tuple[str, str, str, str]:
    m = _FILTRO_RE.match(expr_filtro.strip())
    if not m:
        raise DaxError(
            f"Filtro '{expr_filtro}' não reconhecido. Use o formato Tabela[Coluna] = \"valor\" "
            f"(operadores aceitos: =, <>, >, <, >=, <=)."
        )
    tabela, coluna, operador, valor = m.groups()
    return tabela.strip(), coluna.strip(), operador, valor


def _aplicar_filtros(df: pd.DataFrame, tabela_nome: str, filtros: list[tuple[str, str, str, str]],
                      tabelas: dict[str, pd.DataFrame], passos: list[str]) -> pd.DataFrame:
    if not filtros:
        return df
    mask = pd.Series(True, index=df.index)
    for (ftabela, fcoluna, operador, fvalor) in filtros:
        if ftabela == tabela_nome:
            if fcoluna not in df.columns:
                raise DaxError(f"Coluna '{fcoluna}' não existe na tabela '{ftabela}'.")
            mask &= _comparar(df[fcoluna], operador, fvalor)
            passos.append(f"Filtro aplicado direto em {ftabela}[{fcoluna}] {operador} {fvalor}")
        else:
            fk = _detectar_fk(tabela_nome, ftabela, tabelas)
            if fk is None:
                raise DaxError(
                    f"Não encontrei um relacionamento entre '{tabela_nome}' e '{ftabela}' "
                    f"para aplicar esse filtro (CALCULATE cruzando tabelas requer uma FK detectável)."
                )
            fk_col, pk_dim = fk
            dim_df = tabelas[ftabela]
            if fcoluna not in dim_df.columns:
                raise DaxError(f"Coluna '{fcoluna}' não existe na tabela '{ftabela}'.")
            validos = set(dim_df.loc[_comparar(dim_df[fcoluna], operador, fvalor), pk_dim])
            mask &= df[fk_col].isin(validos)
            passos.append(
                f"Filtro cruzado: {ftabela}[{fcoluna}] {operador} {fvalor} "
                f"→ via {tabela_nome}[{fk_col}] = {ftabela}[{pk_dim}]"
            )
    return df[mask]


# ── Parser recursivo (precedência: + - < * /  < função/parênteses/literal) ──
def _avaliar(expr: str, tabelas: dict[str, pd.DataFrame], filtros: list, passos: list) -> float:
    expr = _remove_parenteses_externos(expr)

    resultado = _tokenizar(expr, "+-")
    if resultado is not None:
        fatores, operadores = resultado
        acumulado = _avaliar_termo(fatores[0], tabelas, filtros, passos)
        for op, fator in zip(operadores, fatores[1:]):
            valor = _avaliar_termo(fator, tabelas, filtros, passos)
            acumulado = acumulado + valor if op == "+" else acumulado - valor
        return acumulado

    return _avaliar_termo(expr, tabelas, filtros, passos)


def _avaliar_termo(expr: str, tabelas: dict, filtros: list, passos: list) -> float:
    expr = _remove_parenteses_externos(expr)

    resultado = _tokenizar(expr, "*/")
    if resultado is not None:
        fatores, operadores = resultado
        acumulado = _avaliar_fator(fatores[0], tabelas, filtros, passos)
        for op, fator in zip(operadores, fatores[1:]):
            valor = _avaliar_fator(fator, tabelas, filtros, passos)
            if op == "*":
                acumulado *= valor
            else:
                if valor == 0:
                    raise DaxError("Divisão por zero (use DIVIDE() em vez de '/' para evitar isso).")
                acumulado /= valor
        return acumulado

    return _avaliar_fator(expr, tabelas, filtros, passos)


def _avaliar_fator(expr: str, tabelas: dict[str, pd.DataFrame], filtros: list, passos: list) -> float:
    expr = _remove_parenteses_externos(expr.strip())

    if expr.startswith("-"):
        return -_avaliar_fator(expr[1:], tabelas, filtros, passos)
    if expr.startswith("+"):
        return _avaliar_fator(expr[1:], tabelas, filtros, passos)

    if _NUM_RE.match(expr):
        return float(expr)

    m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)\s*$", expr, re.S)
    if not m:
        raise DaxError(f"Não entendi a expressão: '{expr}'.")
    nome_fn, dentro = m.group(1).upper(), m.group(2)
    # confirma que o '(' do nome da função fecha exatamente no fim (chamada de nível único)
    profundidade = 0
    idx_abre = expr.index("(")
    for i, c in enumerate(expr[idx_abre:]):
        if c == "(":
            profundidade += 1
        elif c == ")":
            profundidade -= 1
            if profundidade == 0 and idx_abre + i != len(expr) - 1:
                raise DaxError(f"Não entendi a expressão: '{expr}'.")

    if nome_fn not in _FUNCOES_CONHECIDAS:
        raise DaxError(
            f"Função '{nome_fn}' não é suportada neste sandbox. "
            f"Suportadas: {', '.join(sorted(_FUNCOES_CONHECIDAS))}."
        )

    args = _split_args(dentro)

    if nome_fn in _FUNCOES_AGREGACAO:
        tabela, coluna = _parse_ref(args[0], tabelas)
        df = _aplicar_filtros(tabelas[tabela], tabela, filtros, tabelas, passos)
        serie = df[coluna]
        if not pd.api.types.is_numeric_dtype(serie):
            raise DaxError(f"{nome_fn} precisa de uma coluna numérica; '{tabela}[{coluna}]' não é.")
        if nome_fn == "SUM":
            valor = float(serie.sum())
        elif nome_fn == "AVERAGE":
            valor = float(serie.mean()) if len(serie) else 0.0
        elif nome_fn == "MIN":
            valor = float(serie.min()) if len(serie) else 0.0
        else:
            valor = float(serie.max()) if len(serie) else 0.0
        passos.append(f"{nome_fn}({tabela}[{coluna}]) sobre {len(df):,} linha(s) → {valor:,.4f}")
        return valor

    if nome_fn == "COUNTROWS":
        tabela = args[0].strip()
        if tabela not in tabelas:
            raise DaxError(f"Tabela '{tabela}' não existe neste setor.")
        df = _aplicar_filtros(tabelas[tabela], tabela, filtros, tabelas, passos)
        valor = float(len(df))
        passos.append(f"COUNTROWS({tabela}) → {valor:,.0f} linha(s)")
        return valor

    if nome_fn == "DISTINCTCOUNT":
        tabela, coluna = _parse_ref(args[0], tabelas)
        df = _aplicar_filtros(tabelas[tabela], tabela, filtros, tabelas, passos)
        valor = float(df[coluna].nunique())
        passos.append(f"DISTINCTCOUNT({tabela}[{coluna}]) → {valor:,.0f} valor(es) distinto(s)")
        return valor

    if nome_fn == "DIVIDE":
        if len(args) < 2:
            raise DaxError("DIVIDE precisa de pelo menos 2 argumentos: DIVIDE(numerador, denominador, [alternativo]).")
        numerador = _avaliar(args[0], tabelas, filtros, passos)
        denominador = _avaliar(args[1], tabelas, filtros, passos)
        if denominador == 0:
            alt = _avaliar(args[2], tabelas, filtros, passos) if len(args) > 2 else 0.0
            passos.append(f"DIVIDE: denominador é 0 → retornou o valor alternativo ({alt:,.4f})")
            return alt
        valor = numerador / denominador
        passos.append(f"DIVIDE({numerador:,.4f}, {denominador:,.4f}) → {valor:,.4f}")
        return valor

    if nome_fn == "CALCULATE":
        if len(args) < 1:
            raise DaxError("CALCULATE precisa de uma expressão e pelo menos um filtro.")
        novos_filtros = [_parse_filtro(a) for a in args[1:]]
        return _avaliar(args[0], tabelas, filtros + novos_filtros, passos)

    raise DaxError(f"Função '{nome_fn}' reconhecida mas ainda não implementada.")


def avaliar_medida(expressao: str, tabelas: dict[str, pd.DataFrame]) -> tuple[float, list[str], str]:
    """
    Avalia uma medida DAX (subconjunto pedagógico) contra os dados reais.

    Aceita tanto "NomeMedida = EXPRESSÃO" quanto só "EXPRESSÃO".
    Retorna (valor_calculado, passos_explicativos, nome_da_medida).
    Levanta DaxError com mensagem amigável em caso de sintaxe não suportada.
    """
    expressao = expressao.strip()
    nome_medida = "Resultado"
    if "=" in expressao.split("(")[0]:
        possivel_nome, resto = expressao.split("=", 1)
        if re.match(r"^[A-Za-z_][A-Za-z0-9_ ]*$", possivel_nome.strip()):
            nome_medida = possivel_nome.strip()
            expressao = resto.strip()

    if not expressao:
        raise DaxError("Escreva uma expressão DAX para avaliar.")

    passos: list[str] = []
    valor = _avaliar(expressao, tabelas, [], passos)
    return valor, passos, nome_medida
