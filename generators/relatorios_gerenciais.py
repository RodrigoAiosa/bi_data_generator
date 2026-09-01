"""
generators/relatorios_gerenciais.py

Gera, genericamente para QUALQUER setor, um conjunto de views SQL de
"Relatórios Gerenciais" (KPIs executivos, evolução mensal/anual, %MoM/%YoY,
distribuição por categoria e ranking por dimensão) — no mesmo espírito do
script de exemplo entregue manualmente para o setor Home Care, mas deduzido
automaticamente a partir das tabelas (Fato*/Dim*/dCalendario) e das colunas
de fato geradas para o setor selecionado.

Não depende de conhecimento fixo sobre nenhum setor específico: tudo é
inferido a partir dos DataFrames recebidos (nomes de tabela, nomes de
coluna, dtype e, quando necessário, cardinalidade real dos dados).
"""

from __future__ import annotations

import pandas as pd

# ── Listas de prioridade para heurísticas ────────────────────────────────────
_MEASURE_KEYWORDS = [
    "valor_total", "valor", "custo", "preco", "receita", "faturamento",
    "lucro", "margem", "saldo", "montante", "quantidade", "qtd",
    "duracao", "score", "nota", "avaliacao", "taxa", "desconto", "frete",
    "salario", "honorario", "comissao", "km", "peso", "distancia",
    "horas", "dias", "tempo", "completude",
]

_CATEGORICAL_KEYWORDS = [
    "tipo", "status", "categoria", "canal", "genero", "sexo", "gravidade",
    "turno", "plano", "modalidade", "forma_pagamento", "segmento",
    "classificacao", "nivel", "regiao", "uf", "estado", "prioridade",
    "situacao", "origem", "destino",
]

_CATEGORICAL_EXCLUDE_KEYWORDS = [
    "nome", "email", "cpf", "cnpj", "cnh", "placa", "endereco",
    "observacao", "descricao", "url", "telefone", "cep", "senha", "token",
    "id_", "sk_",
]

_DATE_COL_PRIORITY = [
    "id_data", "data_venda", "data_pedido", "data_transacao", "data_hora",
    "data_registro", "data_reserva", "data_ocorrencia", "data_atendimento",
    "data_hora_inicio", "data_criacao", "data_compra", "data",
]

_DATE_COL_DEPRIORIZE = ["validade", "vencimento", "nascimento", "expira"]

_DESCRITIVA_EXCLUDE = [
    "email", "cpf", "cnpj", "cnh", "placa", "endereco", "observacao",
    "descricao", "url", "telefone", "cep", "senha", "token",
]

_PERFORMER_KEYWORDS = [
    "vendedor", "profissional", "funcionario", "motorista", "atendente",
    "consultor", "medico", "enfermeiro", "professor", "instrutor",
    "tecnico", "colaborador", "corretor", "advogado", "agente",
    "barbeiro", "cabeleireiro", "garcom", "coach", "vet", "prestador",
]

MAX_MEASURES_KPI = 3
MAX_MEASURES_EVOLUCAO = 3
MAX_MEASURES_MOMYOY = 2
MAX_CATEGORICAS = 2
MAX_DIMS_RANKING = 2
MAX_FATO_TABELAS = 3


# ── Identificadores por dialeto (mesma convenção do sql_generator.py) ────────
def _tbl(name: str, dialect: str) -> str:
    if dialect == "sqlserver":
        return f"[dbo].[{name}]"
    if dialect == "mysql":
        return f"`{name}`"
    return name  # postgresql: sem aspas, igual ao gerar_sql() existente


def _col(name: str, dialect: str) -> str:
    if dialect == "sqlserver":
        return f"[{name}]"
    if dialect == "mysql":
        return f"`{name}`"
    return name


def _view_name(dialect: str, name: str) -> str:
    if dialect == "sqlserver":
        return f"[dbo].[{name}]"
    if dialect == "mysql":
        return f"`{name}`"
    return name


def _drop_e_create(dialect: str, view_name: str) -> tuple[str, str]:
    """Retorna (bloco_drop, abre_create) — GO/; ficam a cargo de quem monta o corpo."""
    if dialect == "sqlserver":
        drop = (
            f"IF OBJECT_ID(N'dbo.{view_name}', 'V') IS NOT NULL DROP VIEW dbo.{view_name};\nGO"
        )
        create = f"CREATE VIEW {_view_name(dialect, view_name)} AS"
        return drop, create
    # postgresql e mysql: CREATE OR REPLACE VIEW dispensa o DROP explícito
    create = f"CREATE OR REPLACE VIEW {_view_name(dialect, view_name)} AS"
    return "", create


def _sep_view(sep: str, titulo: str) -> list[str]:
    return [f"-- {sep}", f"-- {titulo}", f"-- {sep}"]


def _sem_prefixo(tname: str, prefixo: str) -> str:
    return tname[len(prefixo):] if tname.startswith(prefixo) else tname


# ── Detecção de colunas ───────────────────────────────────────────────────────
def _colunas_medida(df: pd.DataFrame) -> list[str]:
    candidatas = [
        c for c in df.columns
        if pd.api.types.is_numeric_dtype(df[c])
        and not pd.api.types.is_bool_dtype(df[c])
        and not c.lower().startswith(("id_", "sk_"))
    ]

    def prioridade(col: str) -> int:
        cl = col.lower()
        for i, kw in enumerate(_MEASURE_KEYWORDS):
            if kw in cl:
                return i
        return 999

    candidatas.sort(key=prioridade)
    return candidatas


def _colunas_categoricas(df: pd.DataFrame) -> list[str]:
    candidatas = []
    for c in df.columns:
        cl = c.lower()
        if any(kw in cl for kw in _CATEGORICAL_EXCLUDE_KEYWORDS):
            continue
        if not pd.api.types.is_string_dtype(df[c]):
            continue
        try:
            nunique = df[c].nunique(dropna=True)
        except Exception:
            continue
        if 2 <= nunique <= 30:
            candidatas.append(c)

    def prioridade(col: str) -> int:
        cl = col.lower()
        for i, kw in enumerate(_CATEGORICAL_KEYWORDS):
            if kw in cl:
                return i
        return 999

    candidatas.sort(key=prioridade)
    return candidatas


def _coluna_data(df: pd.DataFrame) -> str | None:
    cols_lower = {c.lower(): c for c in df.columns}
    for candidato in _DATE_COL_PRIORITY:
        if candidato in cols_lower:
            return cols_lower[candidato]
    # fallback: qualquer coluna contendo "data", evitando as de baixa prioridade
    genericas = [c for c in df.columns if "data" in c.lower()]
    boas = [c for c in genericas if not any(p in c.lower() for p in _DATE_COL_DEPRIORIZE)]
    if boas:
        return boas[0]
    if genericas:
        return genericas[0]
    return None


def _colunas_descritivas_dim(df: pd.DataFrame, pk_col: str, limite: int = 2) -> list[str]:
    out = []
    for c in df.columns:
        if c == pk_col:
            continue
        cl = c.lower()
        if any(kw in cl for kw in _DESCRITIVA_EXCLUDE):
            continue
        if pd.api.types.is_string_dtype(df[c]):
            out.append(c)
        if len(out) >= limite:
            break
    return out


def _detectar_fks_para_dims(fato_df: pd.DataFrame, fato_nome: str, tabelas: dict[str, pd.DataFrame]) -> list[tuple[str, str, str]]:
    """
    Retorna lista de (coluna_fk_no_fato, nome_tabela_dim, coluna_pk_na_dim).
    Prioriza correspondência EXATA entre o nome da coluna do Fato e o nome
    da PK da dimensão (ex.: id_profissional == id_profissional) — mais
    confiável do que comparar com o nome da tabela, que pode não ter nada a
    ver com o nome da própria coluna-chave (ex.: a dimensão "Equipe" é
    identificada por "id_profissional", não por "id_equipe"). Só cai na
    heurística de sufixo por nome de tabela se não achar por nome exato.
    """
    resultado = []
    dim_tables = {n: d for n, d in tabelas.items() if n.startswith("Dim")}
    pk_fato = fato_df.columns[0]
    fk_cols = [
        c for c in fato_df.columns
        if c.lower().startswith(("id_", "sk_")) and c != pk_fato
    ]
    for col in fk_cols:
        melhor = None

        for dim_nome, dim_df in dim_tables.items():
            if dim_df.columns[0].lower() == col.lower():
                melhor = dim_nome
                break

        if melhor is None:
            sufixo = col.split("_", 1)[1] if "_" in col else col[3:]
            for dim_nome, dim_df in dim_tables.items():
                dim_sem_prefixo = dim_nome[3:].lower()  # remove "Dim"
                if sufixo.lower() in dim_sem_prefixo or dim_sem_prefixo in sufixo.lower():
                    melhor = dim_nome
                    break

        if melhor:
            pk_dim = dim_tables[melhor].columns[0]
            resultado.append((col, melhor, pk_dim))
    return resultado


def _prioridade_dim_performer(dim_nome: str) -> int:
    cl = dim_nome.lower()
    for i, kw in enumerate(_PERFORMER_KEYWORDS):
        if kw in cl:
            return i
    return 999


# ── Views ─────────────────────────────────────────────────────────────────────
def _view_kpis(dialect: str, sep: str, fato_nome: str, fato_df: pd.DataFrame,
               dim_tables: dict[str, pd.DataFrame], medidas: list[str]) -> str:
    sufixo = _sem_prefixo(fato_nome, "Fato")
    view_name = f"vw_KPIsGerenciais_{sufixo}"
    linhas = _sep_view(sep, f"KPIs GERENCIAIS — visão executiva ({sufixo})")
    drop, create = _drop_e_create(dialect, view_name)
    if drop:
        linhas.append(drop)
    linhas.append(create)

    selects = []
    for dim_nome, dim_df in list(dim_tables.items())[:6]:
        sufixo_dim = _sem_prefixo(dim_nome, "Dim")
        selects.append(
            f"    (SELECT COUNT(*) FROM {_tbl(dim_nome, dialect)}) AS Total{sufixo_dim}"
        )
    selects.append(
        f"    (SELECT COUNT(*) FROM {_tbl(fato_nome, dialect)}) AS Total{sufixo}"
    )
    for m in medidas[:MAX_MEASURES_KPI]:
        selects.append(
            f"    (SELECT SUM({_col(m, dialect)}) FROM {_tbl(fato_nome, dialect)}) AS Soma_{m}"
        )
        selects.append(
            f"    (SELECT CAST(AVG(CAST({_col(m, dialect)} AS FLOAT)) AS DECIMAL(18,2)) "
            f"FROM {_tbl(fato_nome, dialect)}) AS Media_{m}"
        )
    linhas.append("SELECT\n" + ",\n".join(selects) + ";")
    if dialect == "sqlserver":
        linhas.append("GO")
    linhas.append("")
    return "\n".join(linhas)


def _view_evolucao_mensal(dialect: str, sep: str, fato_nome: str, date_col: str,
                           fato_pk: str, medidas: list[str]) -> str:
    sufixo = _sem_prefixo(fato_nome, "Fato")
    view_name = f"vw_EvolucaoMensal_{sufixo}"
    linhas = _sep_view(sep, f"EVOLUÇÃO MENSAL — {sufixo}")
    drop, create = _drop_e_create(dialect, view_name)
    if drop:
        linhas.append(drop)
    linhas.append(create)

    selects = [
        "    c.IdMesAno", "    c.MesAno", "    c.Ano", "    c.Mes",
        f"    COUNT(f.{_col(fato_pk, dialect)}) AS QtdRegistros",
    ]
    for m in medidas[:MAX_MEASURES_EVOLUCAO]:
        selects.append(f"    SUM(f.{_col(m, dialect)}) AS Soma_{m}")
        selects.append(
            f"    CAST(AVG(CAST(f.{_col(m, dialect)} AS FLOAT)) AS DECIMAL(18,2)) AS Media_{m}"
        )
    linhas.append("SELECT\n" + ",\n".join(selects))
    linhas.append(f"FROM {_tbl('dCalendario', dialect)} c")
    linhas.append(
        f"JOIN {_tbl(fato_nome, dialect)} f "
        f"ON CAST(f.{_col(date_col, dialect)} AS DATE) = c.Data"
    )
    linhas.append("GROUP BY c.IdMesAno, c.MesAno, c.Ano, c.Mes;")
    if dialect == "sqlserver":
        linhas.append("GO")
    linhas.append("")
    return "\n".join(linhas)


def _view_evolucao_anual(dialect: str, sep: str, fato_nome: str, date_col: str,
                          fato_pk: str, medidas: list[str]) -> str:
    sufixo = _sem_prefixo(fato_nome, "Fato")
    view_name = f"vw_EvolucaoAnual_{sufixo}"
    linhas = _sep_view(sep, f"EVOLUÇÃO ANUAL — {sufixo}")
    drop, create = _drop_e_create(dialect, view_name)
    if drop:
        linhas.append(drop)
    linhas.append(create)

    selects = ["    c.Ano", f"    COUNT(f.{_col(fato_pk, dialect)}) AS QtdRegistros"]
    for m in medidas[:MAX_MEASURES_EVOLUCAO]:
        selects.append(f"    SUM(f.{_col(m, dialect)}) AS Soma_{m}")
    linhas.append("SELECT\n" + ",\n".join(selects))
    linhas.append(f"FROM {_tbl('dCalendario', dialect)} c")
    linhas.append(
        f"JOIN {_tbl(fato_nome, dialect)} f "
        f"ON CAST(f.{_col(date_col, dialect)} AS DATE) = c.Data"
    )
    linhas.append("GROUP BY c.Ano;")
    if dialect == "sqlserver":
        linhas.append("GO")
    linhas.append("")
    return "\n".join(linhas)


def _view_mom_yoy(dialect: str, sep: str, fato_nome: str, date_col: str,
                   fato_pk: str, medidas: list[str]) -> str:
    sufixo = _sem_prefixo(fato_nome, "Fato")
    view_name = f"vw_IndicadoresMoMYoY_{sufixo}"
    linhas = _sep_view(sep, f"INDICADORES COM %MoM e %YoY — {sufixo}")
    linhas.append("-- MoM = variação vs. mês imediatamente anterior (LAG 1)")
    linhas.append("-- YoY = variação vs. mesmo mês do ano anterior (LAG 12)")
    linhas.append("-- ATENÇÃO: assume série mensal contínua (sem meses ausentes na base).")
    drop, create = _drop_e_create(dialect, view_name)
    if drop:
        linhas.append(drop)
    linhas.append(create)

    medidas_mom = medidas[:MAX_MEASURES_MOMYOY]

    # CTE base: agregação mensal
    base_selects = [
        "    c.IdMesAno, c.MesAno, c.Ano, c.Mes",
        f"    COUNT(f.{_col(fato_pk, dialect)}) AS QtdRegistros",
    ]
    for m in medidas_mom:
        base_selects.append(f"    SUM(f.{_col(m, dialect)}) AS Soma_{m}")

    linhas.append("WITH Base AS (")
    linhas.append("    SELECT")
    linhas.append(",\n".join(f"    {s}" for s in base_selects))
    linhas.append(f"    FROM {_tbl('dCalendario', dialect)} c")
    linhas.append(
        f"    JOIN {_tbl(fato_nome, dialect)} f "
        f"ON CAST(f.{_col(date_col, dialect)} AS DATE) = c.Data"
    )
    linhas.append("    GROUP BY c.IdMesAno, c.MesAno, c.Ano, c.Mes")
    linhas.append(")")

    final_selects = ["    IdMesAno, MesAno, Ano, Mes, QtdRegistros"]
    for m in medidas_mom:
        final_selects.append(f"    Soma_{m}")

    def _lag_pct(campo: str, lag: int, sufixo_pct: str) -> list[str]:
        return [
            f"    LAG({campo}, {lag}) OVER (ORDER BY IdMesAno) AS {campo}_{sufixo_pct}",
            f"    CAST((CAST({campo} AS FLOAT) - LAG({campo}, {lag}) OVER (ORDER BY IdMesAno))\n"
            f"        / NULLIF(LAG({campo}, {lag}) OVER (ORDER BY IdMesAno), 0) * 100 "
            f"AS DECIMAL(18,2)) AS {campo}_{sufixo_pct}_Pct",
        ]

    for campo in ["QtdRegistros"] + [f"Soma_{m}" for m in medidas_mom]:
        final_selects.extend(_lag_pct(campo, 1, "MesAnt"))
    for campo in ["QtdRegistros"] + [f"Soma_{m}" for m in medidas_mom]:
        final_selects.extend(_lag_pct(campo, 12, "AnoAnt"))

    linhas.append("SELECT\n" + ",\n".join(final_selects))
    linhas.append("FROM Base;")
    if dialect == "sqlserver":
        linhas.append("GO")
    linhas.append("")
    return "\n".join(linhas)


def _view_por_categoria(dialect: str, sep: str, fato_nome: str, categ_col: str,
                         medidas: list[str]) -> str:
    sufixo = _sem_prefixo(fato_nome, "Fato")
    view_name = f"vw_{sufixo}Por_{categ_col}"
    linhas = _sep_view(sep, f"DISTRIBUIÇÃO POR {categ_col.upper()} — {sufixo}")
    drop, create = _drop_e_create(dialect, view_name)
    if drop:
        linhas.append(drop)
    linhas.append(create)

    selects = [f"    {_col(categ_col, dialect)}", "    COUNT(*) AS QtdRegistros"]
    for m in medidas[:2]:
        selects.append(f"    SUM({_col(m, dialect)}) AS Soma_{m}")
        selects.append(
            f"    CAST(AVG(CAST({_col(m, dialect)} AS FLOAT)) AS DECIMAL(18,2)) AS Media_{m}"
        )
    linhas.append("SELECT\n" + ",\n".join(selects))
    linhas.append(f"FROM {_tbl(fato_nome, dialect)}")
    linhas.append(f"GROUP BY {_col(categ_col, dialect)};")
    if dialect == "sqlserver":
        linhas.append("GO")
    linhas.append("")
    return "\n".join(linhas)


def _view_ranking_dim(dialect: str, sep: str, fato_nome: str, fato_pk: str,
                       fk_col: str, dim_nome: str, dim_pk: str,
                       cols_descritivas: list[str], medidas: list[str]) -> str:
    sufixo_dim = _sem_prefixo(dim_nome, "Dim")
    view_name = f"vw_RankingTop20_{sufixo_dim}"
    linhas = _sep_view(sep, f"RANKING TOP 20 — {sufixo_dim} (por volume de registros em {fato_nome})")
    drop, create = _drop_e_create(dialect, view_name)
    if drop:
        linhas.append(drop)
    linhas.append(create)

    cols_d = ", ".join(_col(c, dialect) for c in [dim_pk] + cols_descritivas)
    selects = [f"    d.{_col(dim_pk, dialect)}"]
    for c in cols_descritivas:
        selects.append(f"    d.{_col(c, dialect)}")
    selects.append(f"    COUNT(f.{_col(fato_pk, dialect)}) AS QtdRegistros")
    medida_principal = medidas[0] if medidas else None
    if medida_principal:
        selects.append(f"    SUM(f.{_col(medida_principal, dialect)}) AS Soma_{medida_principal}")

    ordem = f"Soma_{medida_principal}" if medida_principal else "QtdRegistros"
    group_by_cols = ", ".join(f"d.{_col(c, dialect)}" for c in [dim_pk] + cols_descritivas)

    if dialect == "sqlserver":
        linhas.append("SELECT TOP 20\n" + ",\n".join(selects))
    else:
        linhas.append("SELECT\n" + ",\n".join(selects))
    linhas.append(f"FROM {_tbl(dim_nome, dialect)} d")
    linhas.append(
        f"LEFT JOIN {_tbl(fato_nome, dialect)} f ON f.{_col(fk_col, dialect)} = d.{_col(dim_pk, dialect)}"
    )
    linhas.append(f"GROUP BY {group_by_cols}")
    if dialect == "sqlserver":
        linhas.append(f"ORDER BY {ordem} DESC;")
    else:
        linhas.append(f"ORDER BY {ordem} DESC")
        linhas.append("LIMIT 20;")
    if dialect == "sqlserver":
        linhas.append("GO")
    linhas.append("")
    return "\n".join(linhas)


# ── Função principal ──────────────────────────────────────────────────────────
def gerar_relatorios_gerenciais(nome_setor: str, tabelas: dict[str, pd.DataFrame],
                                 dialect: str = "sqlserver") -> str:
    """
    Gera um script SQL com views de relatórios gerenciais (KPIs, evolução
    mensal/anual, %MoM/%YoY, distribuição por categoria, ranking por
    dimensão), deduzidas automaticamente das tabelas do setor selecionado.

    Requer que as tabelas (CREATE TABLE) e os dados (INSERT) já tenham sido
    criados previamente no banco — este script cria apenas as VIEWs.
    """
    dialect = dialect.lower()
    sep = "-" * 70
    partes: list[str] = []

    partes.append(f"-- {sep}")
    partes.append("-- BI Data Generator PRO — RELATÓRIOS GERENCIAIS (Views)")
    partes.append(f"-- Setor: {nome_setor}")
    partes.append(f"-- Dialeto: {dialect.upper()}")
    partes.append(
        "-- Pré-requisito: execute antes o script de CREATE TABLE + INSERT deste setor."
    )
    partes.append(
        "-- Views geradas automaticamente a partir dos nomes/tipos das colunas —"
    )
    partes.append(
        "-- revise antes de usar em produção, especialmente as colunas escolhidas"
    )
    partes.append("-- como medida principal e como coluna de data.")
    partes.append(f"-- {sep}")
    partes.append("")

    dim_tables = {n: d for n, d in tabelas.items() if n.startswith("Dim")}
    fato_tables = {n: d for n, d in tabelas.items() if n.startswith("Fato")}
    tem_calendario = any(n.startswith("dCal") for n in tabelas)

    if not fato_tables:
        partes.append("-- Nenhuma tabela Fato encontrada neste setor — nada a gerar.")
        return "\n".join(partes)

    for fato_nome, fato_df in list(fato_tables.items())[:MAX_FATO_TABELAS]:
        fato_pk = fato_df.columns[0]
        medidas = _colunas_medida(fato_df)
        categoricas = _colunas_categoricas(fato_df)
        date_col = _coluna_data(fato_df) if tem_calendario else None

        # 1) KPIs gerenciais
        partes.append(_view_kpis(dialect, sep, fato_nome, fato_df, dim_tables, medidas))

        # 2) Evolução mensal / anual / MoM-YoY (só se houver coluna de data e dCalendario)
        if date_col:
            partes.append(_view_evolucao_mensal(dialect, sep, fato_nome, date_col, fato_pk, medidas))
            partes.append(_view_evolucao_anual(dialect, sep, fato_nome, date_col, fato_pk, medidas))
            if medidas or True:
                partes.append(_view_mom_yoy(dialect, sep, fato_nome, date_col, fato_pk, medidas))

        # 3) Distribuição por categoria
        for categ_col in categoricas[:MAX_CATEGORICAS]:
            partes.append(_view_por_categoria(dialect, sep, fato_nome, categ_col, medidas))

        # 4) Ranking por dimensão relacionada
        fks = _detectar_fks_para_dims(fato_df, fato_nome, tabelas)
        if fks:
            fks_ordenados = sorted(fks, key=lambda x: _prioridade_dim_performer(x[1]))
            for fk_col, dim_nome, dim_pk in fks_ordenados[:MAX_DIMS_RANKING]:
                dim_df = dim_tables[dim_nome]
                cols_descritivas = _colunas_descritivas_dim(dim_df, dim_pk)
                partes.append(
                    _view_ranking_dim(
                        dialect, sep, fato_nome, fato_pk, fk_col, dim_nome, dim_pk,
                        cols_descritivas, medidas,
                    )
                )

    partes.append(f"-- {sep}")
    partes.append("-- Script gerado pelo BI Data Generator PRO")
    partes.append("-- github.com/RodrigoAiosa/bi_data_generator")
    partes.append(f"-- {sep}")

    return "\n".join(partes)
