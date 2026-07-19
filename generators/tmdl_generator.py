"""
generators/tmdl_generator.py — Gera um arquivo .tmdl (Tabular Model Definition
Language) completo a partir das tabelas de um setor, pronto para colar em
Tabular Editor 3 (janela TMDL) ou Power BI Desktop (modo TMDL).

O arquivo gerado contém:
  - Parâmetro "CaminhoPasta" (o usuário ajusta o caminho antes de importar)
  - Todas as tabelas (Dim*, Fato*, Bridge*, dCalendario) com colunas tipadas
  - Partições Power Query (M) que leem os CSVs exportados no ZIP
  - Relacionamentos entre Fato/Dimensões (incluindo dCalendario)
  - Uma tabela "Medidas" com toda a bateria de DAX gerada por
    generators/medidas.py (mesmas medidas exibidas na aba de preview)

Funciona para qualquer um dos setores deste projeto, sem configuração manual,
reaproveitando as mesmas convenções de nomenclatura (id_*/sk_*) usadas em
generators/medidas.py e generators/sql_generator.py.
"""

import re

import pandas as pd

from generators.medidas import gerar_bateria_medidas

_PREFIXOS_CHAVE = ("id_", "sk_")


# ── Helpers de tipo ──────────────────────────────────────────────────────────
def _is_key_col(col: str) -> bool:
    return col.lower().startswith(_PREFIXOS_CHAVE)


def _looks_like_date(series: pd.Series, col_name: str) -> bool:
    """Heurística: coluna é de data pelo dtype ou pelo nome/valores."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    if "data" in col_name.lower() or "date" in col_name.lower():
        return True
    non_null = series.dropna()
    if len(non_null) and hasattr(non_null.iloc[0], "year") and hasattr(non_null.iloc[0], "month"):
        return True
    return False


def _tmdl_dtype(col: str, series: pd.Series) -> tuple[str, str]:
    """Retorna (dataType TMDL, tipo M) para uma coluna."""
    if pd.api.types.is_bool_dtype(series):
        return "boolean", "type logical"
    if _looks_like_date(series, col):
        return "dateTime", "type date"
    if pd.api.types.is_integer_dtype(series):
        return "int64", "Int64.Type"
    if pd.api.types.is_float_dtype(series):
        return "double", "type number"
    return "string", "type text"


def _quote_ident(nome: str) -> str:
    """Aplica aspas simples em identificadores com espaço/caractere especial."""
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nome):
        return nome
    return f"'{nome}'"


def _emoji_free(txt: str) -> str:
    """Remove emojis/ícones do nome da categoria, mantendo texto e pontuação."""
    return re.sub(r"[^\w\sÀ-ÿ%()/-]", "", txt).strip()


# ── Tabelas + colunas + partições M ──────────────────────────────────────────
def _gerar_partition(tname: str, tdf: pd.DataFrame) -> list[str]:
    n_cols = len(tdf.columns)
    tipos = ", ".join(
        f'{{"{col}", {_tmdl_dtype(col, tdf[col])[1]}}}' for col in tdf.columns
    )
    return [
        f"\t\tpartition {tname} = m",
        "\t\t\tmode: import",
        "\t\t\tsource =",
        "\t\t\t\tlet",
        f'\t\t\t\t    Origem = Csv.Document(File.Contents(CaminhoPasta & "\\{tname}.csv"),'
        f'[Delimiter=",", Columns={n_cols}, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
        '\t\t\t\t    #"Cabeçalhos Promovidos" = Table.PromoteHeaders(Origem, [PromoteAllScalars=true]),',
        f'\t\t\t\t    #"Tipo Alterado" = Table.TransformColumnTypes(#"Cabeçalhos Promovidos",{{{tipos}}})',
        "\t\t\tin",
        '\t\t\t    #"Tipo Alterado"',
    ]


def _gerar_tabela(tname: str, tdf: pd.DataFrame) -> list[str]:
    linhas = [f"\ttable {tname}", ""]
    for col in tdf.columns:
        dtype, _ = _tmdl_dtype(col, tdf[col])
        linhas.append(f"\t\tcolumn {col}")
        linhas.append(f"\t\t\tdataType: {dtype}")
        linhas.append("\t\t\tsummarizeBy: none")
        linhas.append(f"\t\t\tsourceColumn: {col}")
        linhas.append("")
        linhas.append("\t\t\tannotation SummarizationSetBy = Automatic")
        linhas.append("")
    linhas.extend(_gerar_partition(tname, tdf))
    return linhas


# ── Relacionamentos ──────────────────────────────────────────────────────────
def _detectar_relacionamentos(tabelas: dict[str, pd.DataFrame]) -> list[tuple[str, str, str, str]]:
    """
    Detecta (fromTable, fromColumn, toTable, toColumn) usando a convenção de
    chaves do projeto: colunas id_*/sk_* que casam com a 1ª coluna (PK) de
    outra tabela, além da ligação Fato/Bridge -> dCalendario pela data.
    """
    relacionamentos: list[tuple[str, str, str, str]] = []
    usados: set[tuple[str, str]] = set()

    pks = {df.columns[0]: nome for nome, df in tabelas.items() if len(df.columns)}

    for nome, df in tabelas.items():
        pk_propria = df.columns[0] if len(df.columns) else None
        for col in df.columns:
            if col == pk_propria or not _is_key_col(col):
                continue
            destino = pks.get(col)
            if destino is None or destino == nome:
                continue
            relacionamentos.append((nome, col, destino, col))
            usados.add((nome, col))

    if "dCalendario" in tabelas and len(tabelas["dCalendario"].columns):
        col_calendario = tabelas["dCalendario"].columns[0]
        for nome, df in tabelas.items():
            if nome == "dCalendario" or not nome.startswith(("Fato", "Bridge")):
                continue
            candidatas = [c for c in df.columns if "data" in c.lower() or "date" in c.lower()]
            if not candidatas:
                continue
            col_data = next(
                (c for c in candidatas if c.lower().startswith(("id_data", "sk_data"))),
                candidatas[0],
            )
            if (nome, col_data) in usados:
                continue
            relacionamentos.append((nome, col_data, "dCalendario", col_calendario))
            usados.add((nome, col_data))

    return relacionamentos


def _gerar_relacionamentos(tabelas: dict[str, pd.DataFrame]) -> list[str]:
    linhas = []
    for i, (de_tabela, de_coluna, para_tabela, para_coluna) in enumerate(
        _detectar_relacionamentos(tabelas), 1
    ):
        linhas.append(f"\trelationship rel_{i}")
        linhas.append(f"\t\tfromColumn: {de_tabela}.{de_coluna}")
        linhas.append(f"\t\ttoColumn: {para_tabela}.{para_coluna}")
        linhas.append("")
    return linhas


# ── Tabela de Medidas (reaproveita generators/medidas.py) ───────────────────
def _gerar_tabela_medidas(tabelas: dict[str, pd.DataFrame]) -> list[str]:
    medidas_por_fato = gerar_bateria_medidas(tabelas)
    linhas = ["\ttable Medidas", ""]

    multi_fato = len(medidas_por_fato) > 1

    for fato_key, categorias in medidas_por_fato.items():
        for categoria, lista in categorias.items():
            if not lista:
                continue
            categoria_limpa = _emoji_free(categoria)
            for m in lista:
                nome_medida = _quote_ident(m["nome"].replace("'", "''"))
                _, expr_part = m["formula"].split("=", 1)
                expr = expr_part.strip()

                if "\n" in expr:
                    linhas.append(f"\t\tmeasure {nome_medida} = ```")
                    for linha_formula in expr.split("\n"):
                        linhas.append(f"\t\t\t{linha_formula}")
                    linhas.append("\t\t\t```")
                else:
                    linhas.append(f"\t\tmeasure {nome_medida} = {expr}")

                pasta = categoria_limpa if not m.get("titulo") else f"{categoria_limpa}\\{m['titulo']}"
                if multi_fato:
                    pasta = f"{fato_key}\\{pasta}"
                linhas.append(f"\t\t\tdisplayFolder: {pasta}")
                linhas.append("")

    # Tabela "vazia" para hospedar as medidas (mesmo padrão gerado pelo Power BI
    # ao criar uma tabela via "Inserir Dados" sem nenhuma linha).
    linhas.extend([
        "\t\tpartition Medidas = m",
        "\t\t\tmode: import",
        "\t\t\tsource =",
        "\t\t\t\tlet",
        '\t\t\t\t    Origem = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i44FAA==", '
        'BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta '
        '[Serialized.Text = true]) in type table [#"Coluna 1" = _t]),',
        '\t\t\t\t    #"Colunas Removidas" = Table.RemoveColumns(Origem,{"Coluna 1"})',
        "\t\t\tin",
        '\t\t\t    #"Colunas Removidas"',
    ])
    return linhas


# ── Função principal ─────────────────────────────────────────────────────────
def gerar_tmdl(nome_setor: str, tabelas: dict[str, pd.DataFrame]) -> str:
    """
    Gera o script TMDL completo do modelo semântico: parâmetro de pasta,
    tabelas com colunas tipadas e partições Power Query, relacionamentos e
    a tabela de Medidas DAX. Pronto para colar em Tabular Editor 3 (janela
    TMDL) ou Power BI Desktop (modo de edição TMDL).
    """
    caminho_base = f"C:\\Dados\\{nome_setor.replace(' ', '_')}"

    linhas = [
        "createOrReplace",
        "",
        "\texpression CaminhoPasta =",
        f'\t\t\t"{caminho_base}" meta [IsParameterQuery=true, List={{"{caminho_base}"}}, '
        f'DefaultValue="{caminho_base}", Type="Text", IsParameterQueryRequired=true]',
        "\t\tannotation PBI_ResultType = Text",
        "",
    ]

    for tname, tdf in tabelas.items():
        linhas.extend(_gerar_tabela(tname, tdf))
        linhas.append("")

    linhas.extend(_gerar_relacionamentos(tabelas))
    linhas.append("")

    linhas.extend(_gerar_tabela_medidas(tabelas))

    return "\n".join(linhas)
