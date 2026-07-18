"""generators/sql_generator.py — Gera scripts DDL SQL a partir das tabelas do setor."""

from datetime import date, datetime
import pandas as pd

# Mapeamento de dtype pandas → tipo SQL (compatível com SQL Server, PostgreSQL e MySQL)
_DTYPE_SQL = {
    "int64":          {"sqlserver": "BIGINT",       "postgresql": "BIGINT",   "mysql": "BIGINT"},
    "int32":          {"sqlserver": "INT",           "postgresql": "INTEGER",  "mysql": "INT"},
    "float64":        {"sqlserver": "DECIMAL(18,2)", "postgresql": "NUMERIC(18,2)", "mysql": "DECIMAL(18,2)"},
    "float32":        {"sqlserver": "DECIMAL(10,2)", "postgresql": "NUMERIC(10,2)", "mysql": "DECIMAL(10,2)"},
    "bool":           {"sqlserver": "BIT",           "postgresql": "BOOLEAN",  "mysql": "TINYINT(1)"},
    "object":         {"sqlserver": "NVARCHAR(255)", "postgresql": "VARCHAR(255)", "mysql": "VARCHAR(255)"},
    "datetime64[ns]": {"sqlserver": "DATETIME2",     "postgresql": "TIMESTAMP","mysql": "DATETIME"},
}

# Colunas que são claramente PKs
_PK_PATTERNS = ["id_", "sk_"]

# Colunas que devem ser NOT NULL
_NOT_NULL_PATTERNS = ["id_", "sk_", "data", "date", "nome", "name", "status", "tipo", "type"]

# Colunas com tamanho específico
_VARCHAR_OVERRIDES = {
    "cnpj":         50,
    "cpf":          20,
    "cnh":          30,
    "placa":        20,
    "uf":           5,
    "email":        200,
    "telefone":     30,
    "cep":          15,
    "url":          500,
    "descricao":    1000,
    "observacao":   1000,
    "notas":        1000,
    "endereco":     500,
}


def _infer_sql_type(col: str, dtype: str, dialect: str) -> str:
    """Infere o tipo SQL da coluna com base no dtype e no nome."""
    col_lower = col.lower()

    # Colunas numéricas que têm "data" no prefixo mas são inteiros
    if col_lower.startswith("km_") or col_lower.endswith("_km") or col_lower == "km_atual":
        return "BIGINT" if dialect != "mysql" else "BIGINT"

    # Datas por nome
    if any(p in col_lower for p in ["data", "date", "dt_", "_at", "vencimento", "validade"]):
        if dialect == "sqlserver":
            return "DATE"
        return "DATE"

    # IDs inteiros
    if col_lower.startswith(("id_", "sk_")):
        if dialect == "sqlserver":
            return "INT"
        if dialect == "postgresql":
            return "INTEGER"
        return "INT"

    # Percentuais
    if col_lower.endswith("_pct") or "pct" in col_lower or "percentual" in col_lower:
        if dialect == "sqlserver":
            return "DECIMAL(8,2)"
        return "NUMERIC(8,2)"

    # Valores monetários grandes
    if any(p in col_lower for p in ["valor", "preco", "custo", "receita", "lucro", "orcamento",
                                     "honorario", "salario", "taxa", "frete", "desconto"]):
        if dialect == "sqlserver":
            return "DECIMAL(18,2)"
        if dialect == "postgresql":
            return "NUMERIC(18,2)"
        return "DECIMAL(18,2)"

    # Overrides de VARCHAR por nome
    for key, size in _VARCHAR_OVERRIDES.items():
        if key in col_lower:
            if dialect == "sqlserver":
                return f"NVARCHAR({size})"
            return f"VARCHAR({size})"

    return _DTYPE_SQL.get(dtype, _DTYPE_SQL["object"])[dialect]


def _is_pk(col: str) -> bool:
    col_lower = col.lower()
    # Primeira coluna que começa com id_ ou sk_ é PK
    return col_lower.startswith(("id_", "sk_"))


def _is_not_null(col: str) -> bool:
    col_lower = col.lower()
    return any(col_lower.startswith(p) or p in col_lower
               for p in _NOT_NULL_PATTERNS)


def _table_comment(tname: str) -> str:
    """Retorna um comentário descritivo para a tabela."""
    prefixes = {
        "Fato":   "Tabela Fato —",
        "Dim":    "Tabela Dimensão —",
        "dCal":   "Tabela Calendário —",
        "Bridge": "Tabela Bridge —",
    }
    for prefix, label in prefixes.items():
        if tname.startswith(prefix):
            return label
    return "Tabela —"


def gerar_sql(nome_setor: str, tabelas: dict[str, pd.DataFrame], dialect: str = "sqlserver") -> str:
    """
    Gera script DDL (CREATE TABLE) para todas as tabelas do setor.

    Parâmetros
    ----------
    nome_setor : str
        Nome do setor para comentário no topo do script.
    tabelas : dict[str, pd.DataFrame]
        Dicionário com as tabelas geradas.
    dialect : str
        Dialeto SQL: 'sqlserver', 'postgresql' ou 'mysql'.

    Retorna
    -------
    str : Script SQL completo.
    """
    dialect = dialect.lower()
    lines = []

    # ── Cabeçalho ─────────────────────────────────────────────────────────────
    sep = "-" * 70
    lines.append(f"-- {sep}")
    lines.append(f"-- BI Data Generator PRO")
    lines.append(f"-- Setor: {nome_setor}")
    lines.append(f"-- Dialeto: {dialect.upper()}")
    lines.append(f"-- Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    lines.append(f"-- {sep}")
    lines.append("")

    # ── Schema (opcional) ─────────────────────────────────────────────────────
    schema_name = nome_setor.lower().replace(" ", "_").replace("&", "e").replace("/", "_")
    if dialect == "sqlserver":
        lines.append(f"-- Crie o schema antes de executar (opcional):")
        lines.append(f"-- CREATE SCHEMA [{schema_name}];")
        lines.append(f"-- GO")
    elif dialect == "postgresql":
        lines.append(f"-- Crie o schema antes de executar (opcional):")
        lines.append(f"-- CREATE SCHEMA IF NOT EXISTS {schema_name};")
        lines.append(f"-- SET search_path TO {schema_name};")
    lines.append("")

    # ── Ordena tabelas respeitando FKs ────────────────────────────────────────
    ordem = _ordenar_por_fk(tabelas)

    # ── DROP TABLE (ordem inversa para evitar FK issues) ──────────────────────
    lines.append(f"-- {sep}")
    lines.append(f"-- DROP TABLES (execute se precisar recriar — ordem inversa de FK)")
    lines.append(f"-- {sep}")
    for tname in reversed(ordem):
        if dialect == "sqlserver":
            lines.append(f"-- IF OBJECT_ID(N'[dbo].[{tname}]', 'U') IS NOT NULL DROP TABLE [dbo].[{tname}];")
        elif dialect == "postgresql":
            lines.append(f"-- DROP TABLE IF EXISTS {tname} CASCADE;")
        else:
            lines.append(f"-- DROP TABLE IF EXISTS `{tname}`;")
    lines.append("")

    # ── CREATE TABLE por tabela (ordem respeitando FKs) ──────────────────────
    for tname in ordem:
        tdf = tabelas[tname]
        comment = _table_comment(tname)
        lines.append(f"-- {sep}")
        lines.append(f"-- {comment} {tname}")
        lines.append(f"-- Colunas: {len(tdf.columns)}  |  Linhas exemplo: {len(tdf):,}")
        lines.append(f"-- {sep}")

        pk_col = None

        if dialect == "sqlserver":
            lines.append(f"CREATE TABLE [dbo].[{tname}] (")
        elif dialect == "postgresql":
            lines.append(f"CREATE TABLE {tname} (")
        else:
            lines.append(f"CREATE TABLE `{tname}` (")

        col_defs = []
        pk_candidates = []

        for col in tdf.columns:
            dtype_str = str(tdf[col].dtype)
            sql_type  = _infer_sql_type(col, dtype_str, dialect)
            not_null  = "NOT NULL" if _is_not_null(col) else "NULL"

            if _is_pk(col) and pk_col is None:
                pk_col = col
                pk_candidates.append(col)

            if dialect == "sqlserver":
                col_defs.append(f"    [{col}] {sql_type} {not_null}")
            elif dialect == "postgresql":
                col_defs.append(f"    {col} {sql_type} {not_null}")
            else:
                col_defs.append(f"    `{col}` {sql_type} {not_null}")

        # PK constraint
        if pk_col:
            if dialect == "sqlserver":
                col_defs.append(f"    CONSTRAINT [PK_{tname}] PRIMARY KEY ([{pk_col}])")
            elif dialect == "postgresql":
                col_defs.append(f"    CONSTRAINT pk_{tname.lower()} PRIMARY KEY ({pk_col})")
            else:
                col_defs.append(f"    PRIMARY KEY (`{pk_col}`)")

        lines.append(",\n".join(col_defs))

        if dialect == "sqlserver":
            lines.append(");")
            lines.append("GO")
        else:
            lines.append(");")

        lines.append("")

    # ── Índices sugeridos ──────────────────────────────────────────────────────
    lines.append(f"-- {sep}")
    lines.append("-- ÍNDICES SUGERIDOS")
    lines.append(f"-- {sep}")

    for tname, tdf in tabelas.items():
        fk_cols = [c for c in tdf.columns if c.lower().startswith("id_") and c != tdf.columns[0]]
        date_cols = [c for c in tdf.columns if any(p in c.lower() for p in ["data", "date", "dt_"])]

        for col in fk_cols + date_cols:
            idx_name = f"IX_{tname}_{col}"
            if dialect == "sqlserver":
                lines.append(f"CREATE INDEX [{idx_name}] ON [dbo].[{tname}] ([{col}]);")
            elif dialect == "postgresql":
                lines.append(f"CREATE INDEX {idx_name.lower()} ON {tname} ({col});")
            else:
                lines.append(f"CREATE INDEX `{idx_name}` ON `{tname}` (`{col}`);")

    lines.append("")
    lines.append(f"-- {sep}")
    lines.append(f"-- Script gerado pelo BI Data Generator PRO")
    lines.append(f"-- github.com/RodrigoAiosa/bi_data_generator")
    lines.append(f"-- {sep}")

    return "\n".join(lines)


def _format_value(val, dialect: str) -> str:
    """Formata um valor Python para SQL literal."""
    import math

    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "NULL"

    if isinstance(val, bool):
        if dialect == "sqlserver":
            return "1" if val else "0"
        if dialect == "mysql":
            return "1" if val else "0"
        return "TRUE" if val else "FALSE"

    if isinstance(val, (int, float)):
        if isinstance(val, float) and math.isinf(val):
            return "NULL"
        return str(val)

    # Strings e datas: escapa aspas simples
    s = str(val).replace("'", "''")
    return f"'{s}'"




def _ordenar_por_fk(tabelas: dict) -> list[str]:
    """
    Ordena as tabelas respeitando dependências de chave estrangeira.

    Regra simples e robusta:
      1. dCalendario e Dimensões primeiro (não têm FK para Fato)
      2. Bridges depois das Dimensões
      3. Tabelas Fato por último (referenciam Dimensões via id_*)

    Dentro de cada grupo, a ordem do dicionário original é preservada.
    Aplica ordenação topológica via Kahn's algorithm para dependências
    entre Dimensões (ex: DimFilial → DimRegiao).
    """
    from collections import defaultdict, deque

    # Classifica cada tabela em grupo
    def _grupo(nome: str) -> int:
        if nome.startswith("dCal"):          return 0   # Calendário
        if nome.startswith("Dim"):           return 1   # Dimensão
        if nome.startswith("Bridge"):        return 2   # Bridge
        if nome.startswith("Fato"):         return 3   # Fato
        return 1                                        # desconhecido → trata como Dim

    # Detecta dependências: coluna id_X em tabela A → tabela DimX ou tabela X
    def _detectar_deps(nome: str, df) -> set[str]:
        deps = set()
        fk_cols = [c for c in df.columns
                   if c.lower().startswith("id_") and c != df.columns[0]]
        for col in fk_cols:
            sufixo = col[3:]  # remove "id_"
            for candidato in tabelas:
                if candidato == nome:
                    continue
                # Ex: id_produto → DimProduto, id_vendedor → DimVendedor
                candidato_lower = candidato.lower().replace("dim","").replace("fato","")
                if sufixo.lower() in candidato_lower or candidato_lower in sufixo.lower():
                    if _grupo(candidato) <= _grupo(nome):
                        deps.add(candidato)
        return deps

    # Monta grafo de dependências
    deps_map   = {nome: _detectar_deps(nome, df) for nome, df in tabelas.items()}
    in_degree  = defaultdict(int)
    adj        = defaultdict(set)

    for nome, deps in deps_map.items():
        for dep in deps:
            adj[dep].add(nome)
            in_degree[nome] += 1
        if nome not in in_degree:
            in_degree[nome] = 0

    # Kahn's algorithm com prioridade de grupo
    queue = deque(sorted(
        [n for n, d in in_degree.items() if d == 0],
        key=lambda n: (_grupo(n), list(tabelas.keys()).index(n))
    ))
    ordem = []

    while queue:
        nome = queue.popleft()
        ordem.append(nome)
        vizinhos = sorted(adj[nome], key=lambda n: (_grupo(n), list(tabelas.keys()).index(n)))
        for viz in vizinhos:
            in_degree[viz] -= 1
            if in_degree[viz] == 0:
                queue.append(viz)

    # Tabelas não resolvidas (ciclos) — adiciona no final preservando grupo
    nao_resolvidas = [n for n in tabelas if n not in ordem]
    nao_resolvidas.sort(key=lambda n: (_grupo(n), list(tabelas.keys()).index(n)))
    ordem.extend(nao_resolvidas)

    return ordem


def _gerar_ordem_comentario(ordem: list[str], tabelas: dict) -> str:
    """Gera um bloco de comentário explicando a ordem de inserção."""
    linhas = ["-- Ordem de inserção (respeita chaves estrangeiras):"]
    grupos = {"dCal": "Calendário", "Dim": "Dimensão", "Bridge": "Bridge", "Fato": "Fato"}
    for i, nome in enumerate(ordem, 1):
        tipo = next((v for k, v in grupos.items() if nome.startswith(k)), "Tabela")
        linhas.append(f"--   {i:2}. {nome:<35} [{tipo}]  ({len(tabelas[nome]):,} linhas)")
    return "\n".join(linhas)


def gerar_sql_insert(
    nome_setor: str,
    tabelas: dict,
    dialect: str = "sqlserver",
    batch_size: int = 500,
) -> str:
    """
    Gera script SQL com INSERT INTO para popular todas as tabelas.

    Parâmetros
    ----------
    nome_setor  : Nome do setor.
    tabelas     : Dict com DataFrames gerados.
    dialect     : 'sqlserver', 'postgresql' ou 'mysql'.
    batch_size  : Número de linhas por bloco INSERT (default 500).

    Retorna
    -------
    str : Script SQL com todos os INSERTs.
    """
    import pandas as pd
    from datetime import datetime

    dialect   = dialect.lower()
    sep       = "-" * 70
    lines     = []

    # ── Cabeçalho ─────────────────────────────────────────────────────────
    lines.append(f"-- {sep}")
    lines.append(f"-- BI Data Generator PRO — INSERT DATA")
    lines.append(f"-- Setor      : {nome_setor}")
    lines.append(f"-- Dialeto    : {dialect.upper()}")
    lines.append(f"-- Gerado em  : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    total_rows = sum(len(df) for df in tabelas.values())
    lines.append(f"-- Total linhas: {total_rows:,}")
    lines.append(f"-- {sep}")
    lines.append("")

    # ── Ordena tabelas respeitando FKs ────────────────────────────────────────
    ordem = _ordenar_por_fk(tabelas)
    lines.append(_gerar_ordem_comentario(ordem, tabelas))
    lines.append("")

    # ── Configurações por dialeto ──────────────────────────────────────────
    if dialect == "sqlserver":
        lines.append("SET NOCOUNT ON;")
        lines.append("GO")
        lines.append("")
    elif dialect == "mysql":
        lines.append("SET FOREIGN_KEY_CHECKS = 0;")
        lines.append("SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';")
        lines.append("")

    # ── INSERTs por tabela (ordem respeitando FKs) ────────────────────────
    for tname in ordem:
        tdf = tabelas[tname]
        if len(tdf) == 0:
            continue

        lines.append(f"-- {sep}")
        lines.append(f"-- {tname}  ({len(tdf):,} linhas)")
        lines.append(f"-- {sep}")

        # Identidade SQL Server
        has_pk = tdf.columns[0].lower().startswith(("id_", "sk_"))
        if dialect == "sqlserver" and has_pk:
            lines.append(f"SET IDENTITY_INSERT [dbo].[{tname}] ON;")

        # Monta lista de colunas
        if dialect == "sqlserver":
            cols_str = ", ".join(f"[{c}]" for c in tdf.columns)
            table_ref = f"[dbo].[{tname}]"
        elif dialect == "mysql":
            cols_str = ", ".join(f"`{c}`" for c in tdf.columns)
            table_ref = f"`{tname}`"
        else:
            cols_str = ", ".join(tdf.columns)
            table_ref = tname

        # Gera batches de INSERT
        for batch_start in range(0, len(tdf), batch_size):
            batch = tdf.iloc[batch_start : batch_start + batch_size]

            if dialect in ("postgresql", "mysql"):
                # Multi-row INSERT
                lines.append(f"INSERT INTO {table_ref} ({cols_str}) VALUES")
                value_rows = []
                for _, row in batch.iterrows():
                    vals = ", ".join(_format_value(v, dialect) for v in row)
                    value_rows.append(f"    ({vals})")
                lines.append(",\n".join(value_rows) + ";")
            else:
                # SQL Server: INSERT com VALUES multi-row (suportado desde SQL 2008)
                lines.append(f"INSERT INTO {table_ref} ({cols_str}) VALUES")
                value_rows = []
                for _, row in batch.iterrows():
                    vals = ", ".join(_format_value(v, dialect) for v in row)
                    value_rows.append(f"    ({vals})")
                lines.append(",\n".join(value_rows) + ";")

            lines.append("")

        # Fecha IDENTITY_INSERT
        if dialect == "sqlserver" and has_pk:
            lines.append(f"SET IDENTITY_INSERT [dbo].[{tname}] OFF;")
            lines.append("GO")

        lines.append("")

    # ── Rodapé ────────────────────────────────────────────────────────────
    if dialect == "mysql":
        lines.append("SET FOREIGN_KEY_CHECKS = 1;")
        lines.append("")

    lines.append(f"-- {sep}")
    lines.append(f"-- {total_rows:,} linhas inseridas com sucesso")
    lines.append(f"-- BI Data Generator PRO — github.com/RodrigoAiosa/bi_data_generator")
    lines.append(f"-- {sep}")

    return "\n".join(lines)


def gerar_sql_completo(
    nome_setor: str,
    tabelas: dict,
    dialect: str = "sqlserver",
    batch_size: int = 500,
) -> str:
    """
    Gera script SQL completo: DDL (CREATE TABLE) + DML (INSERT INTO).
    Ideal para criar e popular o banco de uma vez só.
    """
    ddl    = gerar_sql(nome_setor, tabelas, dialect)
    dml    = gerar_sql_insert(nome_setor, tabelas, dialect, batch_size)
    sep    = "-" * 70
    header = f"-- {sep}\n-- SCRIPT COMPLETO: DDL + INSERT DATA\n-- {sep}\n\n"
    divider = f"\n\n-- {sep}\n-- INSERT DATA\n-- {sep}\n\n"
    return header + ddl + divider + dml
