"""
generators/tmdl_generator.py
Gera um arquivo TMDL (model.tmdl) completo — tabelas, colunas, partitions
(Power Query apontando para os CSVs), relacionamentos e todas as medidas DAX
da bateria gerada em generators/medidas.py — para QUALQUER setor do projeto.
"""

from __future__ import annotations

import pandas as pd

from generators.medidas import gerar_bateria_medidas

_PREFIXOS_CHAVE = ("id_", "sk_")


def _tmdl_dtype(dtype) -> tuple[str, str]:
    """Mapeia dtype pandas -> (dataType TMDL, tipo M para TransformColumnTypes)."""
    if pd.api.types.is_datetime64_any_dtype(dtype):
        return "dateTime", "type date"
    if pd.api.types.is_bool_dtype(dtype):
        return "boolean", "type logical"
    if pd.api.types.is_integer_dtype(dtype):
        return "int64", "Int64.Type"
    if pd.api.types.is_float_dtype(dtype):
        return "double", "type number"
    return "string", "type text"


def _coluna_e_data(col: str, serie: pd.Series) -> bool:
    if pd.api.types.is_datetime64_any_dtype(serie):
        return True
    name = col.lower()
    return name == "data" or name.startswith(("id_data", "sk_data")) or name.endswith("_data")


def _m_query(nome_tabela: str, df: pd.DataFrame) -> str:
    """Gera o bloco 'source =' em linguagem M, lendo o CSV correspondente."""
    n_cols = len(df.columns)
    tipos = []
    for c in df.columns:
        serie = df[c]
        if _coluna_e_data(c, serie):
            tipos.append(f'{{"{c}", type date}}')
            continue
        _, m_type = _tmdl_dtype(serie.dtype)
        tipos.append(f'{{"{c}", {m_type}}}')
    tipos_str = ", ".join(tipos)

    return (
        "\t\t\tsource =\n"
        "\t\t\t\tlet\n"
        f'\t\t\t\t    Origem = Csv.Document(File.Contents(CaminhoPasta & "\\{nome_tabela}.csv"),'
        f'[Delimiter=",", Columns={n_cols}, Encoding=65001, QuoteStyle=QuoteStyle.None]),\n'
        '\t\t\t\t    #"Cabeçalhos Promovidos" = Table.PromoteHeaders(Origem, [PromoteAllScalars=true]),\n'
        f'\t\t\t\t    #"Tipo Alterado" = Table.TransformColumnTypes(#"Cabeçalhos Promovidos",{{{tipos_str}}})\n'
        "\t\t\t\tin\n"
        '\t\t\t\t    #"Tipo Alterado"\n'
    )


def _tabela_tmdl(nome_tabela: str, df: pd.DataFrame) -> str:
    linhas = [f"\ttable {nome_tabela}\n\n"]
    for c in df.columns:
        serie = df[c]
        if _coluna_e_data(c, serie):
            tmdl_type = "dateTime"
        else:
            tmdl_type, _ = _tmdl_dtype(serie.dtype)
        linhas.append(f"\t\tcolumn {c}\n")
        linhas.append(f"\t\t\tdataType: {tmdl_type}\n")
        linhas.append("\t\t\tsummarizeBy: none\n")
        linhas.append(f"\t\t\tsourceColumn: {c}\n\n")
        linhas.append("\t\t\tannotation SummarizationSetBy = Automatic\n\n")

    linhas.append(f"\t\tpartition {nome_tabela} = m\n")
    linhas.append("\t\t\tmode: import\n")
    linhas.append(_m_query(nome_tabela, df))
    linhas.append("\n")
    return "".join(linhas)


def _e_chave(col: str) -> bool:
    return col.lower().startswith(_PREFIXOS_CHAVE)


def _relacionamentos(tabelas: dict[str, pd.DataFrame]) -> list[str]:
    """
    Detecta relacionamentos FK -> PK entre as tabelas geradas: para cada
    coluna id_*/sk_* de cada tabela (que não seja a PK própria, 1ª coluna),
    procura outra tabela onde essa coluna é a PK (1ª coluna).
    """
    pk_por_tabela = {nome: df.columns[0] for nome, df in tabelas.items() if len(df.columns)}
    dono_da_pk: dict[str, str] = {}
    for nome, pk in pk_por_tabela.items():
        dono_da_pk.setdefault(pk, nome)  # primeira tabela que "possui" essa PK

    blocos = []
    contador = 1
    vistos = set()

    for nome_from, df in tabelas.items():
        pk_propria = df.columns[0] if len(df.columns) else None
        for col in df.columns:
            if not _e_chave(col):
                continue
            if col == pk_propria and nome_from == dono_da_pk.get(col):
                continue
            nome_to = dono_da_pk.get(col)
            if not nome_to or nome_to == nome_from:
                continue
            chave = (nome_from, col, nome_to)
            if chave in vistos:
                continue
            vistos.add(chave)
            blocos.append(
                f"\trelationship rel_{contador}\n"
                f"\t\tfromColumn: {nome_from}.{col}\n"
                f"\t\ttoColumn: {nome_to}.{col}\n\n"
            )
            contador += 1

    # dCalendario: liga pela coluna de data da(s) fato(s)
    if "dCalendario" in tabelas:
        for nome_from, df in tabelas.items():
            if not nome_from.startswith("Fato"):
                continue
            candidatas = [c for c in df.columns if _coluna_e_data(c, df[c])]
            if not candidatas:
                continue
            col_data = candidatas[0]
            chave = (nome_from, col_data, "dCalendario")
            if chave in vistos:
                continue
            vistos.add(chave)
            blocos.append(
                f"\trelationship rel_{contador}\n"
                f"\t\tfromColumn: {nome_from}.{col_data}\n"
                f"\t\ttoColumn: dCalendario.Data\n\n"
            )
            contador += 1

    return blocos


def _medidas_tmdl(tabelas: dict[str, pd.DataFrame]) -> str:
    """Monta a tabela 'Medidas' com todas as medidas DAX organizadas por displayFolder."""
    medidas_por_fato = gerar_bateria_medidas(tabelas)
    if not medidas_por_fato:
        return ""

    linhas = ["\ttable Medidas\n\n"]
    for fato_key, categorias in medidas_por_fato.items():
        for categoria, lista in categorias.items():
            if not lista:
                continue
            pasta_categoria = categoria.split(" ", 1)[1] if " " in categoria else categoria
            for m in lista:
                nome = m["nome"]
                formula = m["formula"]
                titulo = m.get("titulo")
                display_folder = f"{pasta_categoria}\\{titulo}" if titulo else pasta_categoria

                if "\n" in formula:
                    corpo = formula.split("=", 1)[1].strip() if "=" in formula else formula
                    linhas.append(f"\t\tmeasure '{nome}' = ```\n")
                    for l in corpo.split("\n"):
                        linhas.append(f"\t\t\t{l}\n")
                    linhas.append("\t\t\t```\n")
                else:
                    expressao = formula.split("=", 1)[1].strip() if "=" in formula else formula
                    linhas.append(f"\t\tmeasure '{nome}' = {expressao}\n")

                linhas.append(f"\t\t\tdisplayFolder: {display_folder}\n\n")

    linhas.append("\t\tpartition Medidas = m\n")
    linhas.append("\t\t\tmode: import\n")
    linhas.append("\t\t\tsource =\n")
    linhas.append("\t\t\t\tlet\n")
    linhas.append(
        '\t\t\t\t    Origem = Table.FromRows(Json.Document(Binary.Decompress('
        'Binary.FromText("i44FAA==", BinaryEncoding.Base64), Compression.Deflate)), '
        'let _t = ((type nullable text) meta [Serialized.Text = true]) in type table '
        '[#"Coluna 1" = _t]),\n'
    )
    linhas.append('\t\t\t\t    #"Colunas Removidas" = Table.RemoveColumns(Origem,{"Coluna 1"})\n')
    linhas.append("\t\t\t\tin\n")
    linhas.append('\t\t\t\t    #"Colunas Removidas"\n')
    return "".join(linhas)


def gerar_tmdl(nome_setor: str, tabelas: dict[str, pd.DataFrame]) -> str:
    """
    Gera o conteúdo completo do arquivo model.tmdl para o setor, incluindo:
      - parâmetro CaminhoPasta (Power Query)
      - todas as tabelas (Dim*, Fato*, Bridge*, dCalendario) com colunas,
        tipos e partition M apontando para os CSVs de mesmo nome
      - relacionamentos detectados entre FK/PK
      - tabela "Medidas" com toda a bateria de medidas DAX do setor
    """
    partes = []

    partes.append(
        "createOrReplace\n\n"
        '\texpression CaminhoPasta = \n'
        '\t\t\t"C:\\Dados\\" meta [IsParameterQuery=true, List={"C:\\Dados\\"}, '
        'DefaultValue="C:\\Dados\\", Type="Text", IsParameterQueryRequired=true]\n'
        "\t\tannotation PBI_ResultType = Text\n\n"
    )

    for nome_tabela, df in tabelas.items():
        partes.append(_tabela_tmdl(nome_tabela, df))

    for bloco in _relacionamentos(tabelas):
        partes.append(bloco)

    medidas_tmdl = _medidas_tmdl(tabelas)
    if medidas_tmdl:
        partes.append(medidas_tmdl)

    return "".join(partes)
