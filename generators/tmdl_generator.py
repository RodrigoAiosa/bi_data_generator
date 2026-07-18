"""
generators/tmdl_generator.py
Gera um arquivo .tmdl (Tabular Model Definition Language) descrevendo o
modelo completo (tabelas, colunas, partições Power Query, relacionamentos
e medidas DAX) para QUALQUER setor produzido pelos geradores deste projeto.

O arquivo gerado segue o mesmo padrão usado pelo Power BI Desktop ao salvar
um modelo no formato TMDL (pasta de projeto / .pbip), pronto para ser usado
como referência de importação (schema + medidas) do dataset gerado.
"""

from __future__ import annotations

import datetime

import pandas as pd

from generators.medidas import (
    _chaves_estrangeiras,
    _colunas_numericas_fato,
    _coluna_data,
    _nome_dimensao,
    _titulo,
)

_CAMINHO_PADRAO = "C:\\Dados\\"


# ── Tipagem de colunas ────────────────────────────────────────────────────────
def _tipo_coluna(serie: "pd.Series") -> tuple[str, str]:
    """Retorna (dataType TMDL, tipo Power Query) para uma coluna."""
    if pd.api.types.is_bool_dtype(serie):
        return "boolean", "type logical"
    if pd.api.types.is_integer_dtype(serie):
        return "int64", "Int64.Type"
    if pd.api.types.is_float_dtype(serie):
        return "double", "type number"
    if pd.api.types.is_datetime64_any_dtype(serie):
        return "dateTime", "type date"

    nao_nulos = serie.dropna()
    if len(nao_nulos) and isinstance(nao_nulos.iloc[0], (datetime.date, datetime.datetime)):
        return "dateTime", "type date"

    return "string", "type text"


# ── Bloco de tabela (colunas + partição Power Query) ──────────────────────────
def _bloco_tabela(nome_tabela: str, df: "pd.DataFrame") -> str:
    linhas = [f"\ttable {nome_tabela}\n"]

    tipos_pq = []
    for col in df.columns:
        tmdl_type, pq_type = _tipo_coluna(df[col])
        tipos_pq.append((col, pq_type))

        linhas.append(f"\t\tcolumn {col}\n")
        linhas.append(f"\t\t\tdataType: {tmdl_type}\n")
        linhas.append("\t\t\tsummarizeBy: none\n")
        linhas.append(f"\t\t\tsourceColumn: {col}\n")
        linhas.append("\n")
        linhas.append("\t\t\tannotation SummarizationSetBy = Automatic\n")
        linhas.append("\n")

    n_cols = len(df.columns)
    tipos_str = ", ".join(f'{{"{col}", {pq}}}' for col, pq in tipos_pq)

    linhas.append(f"\t\tpartition {nome_tabela} = m\n")
    linhas.append("\t\t\tmode: import\n")
    linhas.append("\t\t\tsource =\n")
    linhas.append("\t\t\t\tlet\n")
    linhas.append(
        f'\t\t\t\t    Origem = Csv.Document(File.Contents(CaminhoPasta & "\\{nome_tabela}.csv"),'
        f"[Delimiter=\",\", Columns={n_cols}, Encoding=65001, QuoteStyle=QuoteStyle.None]),\n"
    )
    linhas.append(
        '\t\t\t\t    #"Cabeçalhos Promovidos" = Table.PromoteHeaders(Origem, [PromoteAllScalars=true]),\n'
    )
    linhas.append(
        f'\t\t\t\t    #"Tipo Alterado" = Table.TransformColumnTypes(#"Cabeçalhos Promovidos",{{{tipos_str}}})\n'
    )
    linhas.append("\t\t\t\tin\n")
    linhas.append('\t\t\t\t    #"Tipo Alterado"\n')
    linhas.append("\n")

    return "".join(linhas)


# ── Relacionamentos ────────────────────────────────────────────────────────────
def _e_coluna_chave(col: str) -> bool:
    return col.lower().startswith(("id_", "sk_"))


def _pk_proprio(df: "pd.DataFrame") -> str | None:
    """PK de uma tabela: 1ª coluna, se ela for única linha a linha."""
    if len(df.columns) == 0:
        return None
    primeira = df.columns[0]
    if df[primeira].nunique(dropna=True) == len(df):
        return primeira
    return None


def _gerar_relacionamentos(tabelas: dict) -> list[tuple[str, str, str, str]]:
    """Retorna lista de (fromTable, fromColumn, toTable, toColumn)."""
    pk_map = {nome: _pk_proprio(df) for nome, df in tabelas.items()}
    relacionamentos: list[tuple[str, str, str, str]] = []
    ja_processadas: set[tuple[str, str]] = set()
    relacionamentos_calendario: list[tuple[str, str, str, str]] = []

    # Reserva de antemão a coluna de data de cada fato (para não ser
    # capturada pelo laço genérico abaixo) — mas só adiciona ao final.
    if "dCalendario" in tabelas:
        for nome_tab, df in tabelas.items():
            if not nome_tab.startswith("Fato"):
                continue
            col_data = _coluna_data(df)
            if col_data:
                relacionamentos_calendario.append((nome_tab, col_data, "dCalendario", "Data"))
                ja_processadas.add((nome_tab, col_data))

    # Demais relacionamentos: coluna id_*/sk_* que bate com a PK de outra tabela
    for nome_tab, df in tabelas.items():
        pk_proprio = pk_map.get(nome_tab)
        for col in df.columns:
            if not _e_coluna_chave(col):
                continue
            if col == pk_proprio:
                continue
            if (nome_tab, col) in ja_processadas:
                continue
            for nome_outra, df_outra in tabelas.items():
                if nome_outra == nome_tab:
                    continue
                if pk_map.get(nome_outra) == col:
                    relacionamentos.append((nome_tab, col, nome_outra, col))
                    ja_processadas.add((nome_tab, col))
                    break

    # Relacionamentos com o calendário aparecem por último, como no Power BI
    relacionamentos.extend(relacionamentos_calendario)
    return relacionamentos


def _bloco_relacionamentos(relacionamentos: list[tuple[str, str, str, str]]) -> str:
    linhas = []
    for i, (de_tab, de_col, para_tab, para_col) in enumerate(relacionamentos, start=1):
        linhas.append(f"\trelationship rel_{i}\n")
        linhas.append(f"\t\tfromColumn: {de_tab}.{de_col}\n")
        linhas.append(f"\t\ttoColumn: {para_tab}.{para_col}\n")
        linhas.append("\n")
    return "".join(linhas)


# ── Medidas DAX ────────────────────────────────────────────────────────────────
def _bloco_measure(nome: str, expr: str, display_folder: str) -> str:
    linhas = []
    if "\n" in expr:
        linhas.append(f"\t\tmeasure '{nome}' = ```\n")
        for linha in expr.split("\n"):
            linhas.append(f"\t\t\t{linha}\n")
        linhas.append("\t\t\t```\n")
        linhas.append(f"\t\t\tdisplayFolder: {display_folder}\n")
    else:
        linhas.append(f"\t\tmeasure '{nome}' = {expr}\n")
        linhas.append(f"\t\t\tdisplayFolder: {display_folder}\n")
    linhas.append("\n")
    return "".join(linhas)


def _bloco_tabela_medidas(tabelas: dict) -> str:
    fatos = [k for k in tabelas if k.startswith("Fato")]
    if not fatos:
        return ""

    multi_fato = len(fatos) > 1

    linhas = ["\ttable Medidas\n\n"]

    for fato_key in fatos:
        fato = tabelas[fato_key]
        col_data = _coluna_data(fato)
        colunas_medida = _colunas_numericas_fato(fato)
        pk_propria = fato.columns[0] if len(fato.columns) else None
        fks = _chaves_estrangeiras(fato, pk_propria)

        prefixo_pasta = f"{fato_key}\\" if multi_fato else ""

        # Agregações básicas (uma subpasta por coluna de negócio)
        for col in colunas_medida:
            titulo = _titulo(col)
            pasta = f"{prefixo_pasta}Agregações Básicas\\{titulo}"
            linhas.append(_bloco_measure(f"Total {titulo}", f"SUM({fato_key}[{col}])", pasta))
            linhas.append(_bloco_measure(f"Média {titulo}", f"AVERAGE({fato_key}[{col}])", pasta))
            linhas.append(_bloco_measure(f"Mínimo {titulo}", f"MIN({fato_key}[{col}])", pasta))
            linhas.append(_bloco_measure(f"Máximo {titulo}", f"MAX({fato_key}[{col}])", pasta))

        # Contagens (sem subpasta)
        pasta_contagens = f"{prefixo_pasta}Contagens"
        linhas.append(_bloco_measure("Qtde de Registros", f"COUNTROWS({fato_key})", pasta_contagens))
        for fk in fks:
            nome_dim = _nome_dimensao(fk, tabelas, fato_key)
            linhas.append(_bloco_measure(
                f"Qtde Distinta de {nome_dim}", f"DISTINCTCOUNT({fato_key}[{fk}])", pasta_contagens
            ))

        # Percentual de participação
        for col in colunas_medida:
            titulo = _titulo(col)
            pasta = f"{prefixo_pasta}Percentual de Participação\\{titulo}"
            expr = (
                "DIVIDE(\n"
                f"    [Total {titulo}],\n"
                f"    CALCULATE([Total {titulo}], ALL({fato_key}))\n"
                ")"
            )
            linhas.append(_bloco_measure(f"% do Total {titulo}", expr, pasta))

        # Time Intelligence
        if col_data and "dCalendario" in tabelas:
            for col in colunas_medida:
                titulo = _titulo(col)
                pasta = f"{prefixo_pasta}Time Intelligence (MoM / YoY / YTD / MTD)\\{titulo}"
                linhas.append(_bloco_measure(
                    f"{titulo} Mês Anterior",
                    f"CALCULATE(\n    [Total {titulo}],\n    DATEADD(dCalendario[Data], -1, MONTH)\n)",
                    pasta,
                ))
                linhas.append(_bloco_measure(
                    f"{titulo} %MoM",
                    f"DIVIDE(\n    [Total {titulo}] - [{titulo} Mês Anterior],\n    [{titulo} Mês Anterior]\n)",
                    pasta,
                ))
                linhas.append(_bloco_measure(
                    f"{titulo} Ano Anterior",
                    f"CALCULATE(\n    [Total {titulo}],\n    SAMEPERIODLASTYEAR(dCalendario[Data])\n)",
                    pasta,
                ))
                linhas.append(_bloco_measure(
                    f"{titulo} %YoY",
                    f"DIVIDE(\n    [Total {titulo}] - [{titulo} Ano Anterior],\n    [{titulo} Ano Anterior]\n)",
                    pasta,
                ))
                linhas.append(_bloco_measure(
                    f"{titulo} Acumulado no Ano (YTD)",
                    f"TOTALYTD([Total {titulo}], dCalendario[Data])",
                    pasta,
                ))
                linhas.append(_bloco_measure(
                    f"{titulo} Acumulado no Mês (MTD)",
                    f"TOTALMTD([Total {titulo}], dCalendario[Data])",
                    pasta,
                ))

    # Partição técnica (tabela "vazia" só para hospedar as medidas — mesma
    # técnica usada pelo Power BI Desktop ao criar uma tabela de medidas).
    linhas.append("\t\tpartition Medidas = m\n")
    linhas.append("\t\t\tmode: import\n")
    linhas.append("\t\t\tsource =\n")
    linhas.append("\t\t\t\tlet\n")
    linhas.append(
        '\t\t\t\t    Origem = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText'
        '("i44FAA==", BinaryEncoding.Base64), Compression.Deflate)), '
        'let _t = ((type nullable text) meta [Serialized.Text = true]) in '
        'type table [#"Coluna 1" = _t]),\n'
    )
    linhas.append(
        '\t\t\t\t    #"Colunas Removidas" = Table.RemoveColumns(Origem,{"Coluna 1"})\n'
    )
    linhas.append("\t\t\t\tin\n")
    linhas.append('\t\t\t\t    #"Colunas Removidas"\n')

    return "".join(linhas)


# ── Função principal ────────────────────────────────────────────────────────────
def gerar_tmdl(nome_setor: str, tabelas: dict) -> str:
    """
    Gera o conteúdo completo de um arquivo model.tmdl para o conjunto de
    tabelas de um setor (dict {nome_tabela: DataFrame}), no mesmo formato
    usado pelo Power BI Desktop (TMDL / .pbip).
    """
    partes = ["createOrReplace\n\n"]

    # Parâmetro de caminho da pasta
    partes.append(f'\texpression CaminhoPasta =\n')
    partes.append(
        f'\t\t\t"{_CAMINHO_PADRAO}" meta [IsParameterQuery=true, '
        f'List={{"{_CAMINHO_PADRAO}"}}, DefaultValue="{_CAMINHO_PADRAO}", '
        f'Type="Text", IsParameterQueryRequired=true]\n'
    )
    partes.append("\t\tannotation PBI_ResultType = Text\n\n")

    # Ordena tabelas: tudo antes, dCalendario por último
    ordem = [t for t in tabelas if t != "dCalendario"]
    if "dCalendario" in tabelas:
        ordem.append("dCalendario")

    for nome_tab in ordem:
        partes.append(_bloco_tabela(nome_tab, tabelas[nome_tab]))

    # Relacionamentos
    relacionamentos = _gerar_relacionamentos(tabelas)
    partes.append(_bloco_relacionamentos(relacionamentos))

    # Tabela de medidas
    partes.append(_bloco_tabela_medidas(tabelas))

    return "".join(partes)
