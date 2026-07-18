"""
generators_bi/medidas.py
Gerador automático de uma bateria de medidas DAX para o modelo estrela
(fato + dimensões) de qualquer setor gerado por generators_bi.setores.

A partir da tabela fato, identifica:
  - colunas numéricas "de negócio" (ignora chaves id_*)
  - a coluna de data da fato (para ligar com dCalendario)
  - as chaves estrangeiras (FKs) que apontam para dimensões

E gera, para CADA coluna numérica encontrada, uma bateria de medidas:
  - Agregações básicas: Total, Média, Mínimo, Máximo
  - Contagens: linhas da fato e distinct count de cada dimensão relacionada
  - Percentual de participação (% do Total)
  - Time Intelligence: Mês Anterior, %MoM, Ano Anterior, %YoY, YTD, MTD
"""

import pandas as pd


def _colunas_numericas_fato(fato: pd.DataFrame) -> list:
    """Colunas numéricas 'de negócio' da fato — ignora chaves (id_*)."""
    return [
        c for c in fato.columns
        if pd.api.types.is_numeric_dtype(fato[c]) and not c.startswith("id_")
    ]


def _coluna_data(fato: pd.DataFrame) -> str | None:
    """Encontra a coluna de data da tabela fato (ex.: 'data', 'data_matricula', 'data_evento')."""
    for c in fato.columns:
        if c.startswith("data") or pd.api.types.is_datetime64_any_dtype(fato[c]):
            return c
    return None


def _chaves_estrangeiras(fato: pd.DataFrame) -> list:
    """
    Colunas id_* que são chave estrangeira (FK): repetem-se ao longo da fato
    (nunique < total de linhas). A PK da própria fato (ex.: id_venda) é única
    linha a linha e não entra nessa lista.
    """
    total_linhas = len(fato)
    return [
        c for c in fato.columns
        if c.startswith("id_") and fato[c].nunique() < total_linhas
    ]


def _nome_dimensao(fk_coluna: str, relacionamentos: list, fato_key: str) -> str:
    """Nome legível da dimensão associada a uma FK, usando RELACIONAMENTOS."""
    for origem, coluna, destino, _pk in relacionamentos:
        if origem == fato_key and coluna == fk_coluna:
            return destino.replace("Dim", "")
    return fk_coluna.replace("id_", "").capitalize()


def _titulo(col: str) -> str:
    """'valor_total' -> 'Valor Total' (nome legível para a medida)."""
    return " ".join(p.capitalize() for p in col.split("_"))


def gerar_bateria_medidas(dados_setor: dict, fato_key: str, relacionamentos: list) -> dict:
    """
    Gera a bateria completa de medidas DAX para a tabela fato de um setor.

    Parâmetros
    ----------
    dados_setor : dict
        Dicionário {nome_tabela: DataFrame} retornado por um gerador de setor
        (ex.: gerar_varejo(...)), incluindo a dCalendario.
    fato_key : str
        Nome da tabela fato dentro de dados_setor (ex.: "FatoVendas").
    relacionamentos : list
        Lista de tuplas (origem, coluna, destino, pk) — RELACIONAMENTOS[setor].

    Retorna
    -------
    dict {categoria: [ {"nome": str, "formula": str, "descricao": str}, ... ]}
    """
    fato = dados_setor[fato_key]
    col_data = _coluna_data(fato)
    colunas_medida = _colunas_numericas_fato(fato)
    fks = _chaves_estrangeiras(fato)

    medidas = {
        "🧮 Agregações Básicas": [],
        "🔢 Contagens": [],
        "📊 Percentual de Participação": [],
        "📅 Time Intelligence (MoM / YoY / YTD / MTD)": [],
    }

    # ---- 1. Agregações básicas: Total, Média, Mínimo, Máximo ----------------
    for col in colunas_medida:
        titulo = _titulo(col)
        medidas["🧮 Agregações Básicas"].extend([
            {
                "nome": f"Total {titulo}",
                "formula": f"Total {titulo} = SUM({fato_key}[{col}])",
                "descricao": f"Soma de {fato_key}[{col}] no contexto de filtro atual.",
            },
            {
                "nome": f"Média {titulo}",
                "formula": f"Média {titulo} = AVERAGE({fato_key}[{col}])",
                "descricao": f"Média de {fato_key}[{col}] no contexto de filtro atual.",
            },
            {
                "nome": f"Mínimo {titulo}",
                "formula": f"Mínimo {titulo} = MIN({fato_key}[{col}])",
                "descricao": f"Menor valor de {fato_key}[{col}] no contexto atual.",
            },
            {
                "nome": f"Máximo {titulo}",
                "formula": f"Máximo {titulo} = MAX({fato_key}[{col}])",
                "descricao": f"Maior valor de {fato_key}[{col}] no contexto atual.",
            },
        ])

    # ---- 2. Contagens ---------------------------------------------------------
    medidas["🔢 Contagens"].append({
        "nome": "Qtde de Registros",
        "formula": f"Qtde de Registros = COUNTROWS({fato_key})",
        "descricao": f"Quantidade de linhas da tabela fato {fato_key} no contexto atual.",
    })
    for fk in fks:
        nome_dim = _nome_dimensao(fk, relacionamentos, fato_key)
        medidas["🔢 Contagens"].append({
            "nome": f"Qtde Distinta de {nome_dim}",
            "formula": f"Qtde Distinta de {nome_dim} = DISTINCTCOUNT({fato_key}[{fk}])",
            "descricao": f"Número de {nome_dim.lower()}(s) distintos presentes na fato.",
        })

    # ---- 3. Percentual de participação (% do total) ---------------------------
    for col in colunas_medida:
        titulo = _titulo(col)
        medidas["📊 Percentual de Participação"].append({
            "nome": f"% do Total {titulo}",
            "formula": (
                f"% do Total {titulo} =\n"
                f"DIVIDE(\n"
                f"    [Total {titulo}],\n"
                f"    CALCULATE([Total {titulo}], ALL({fato_key}))\n"
                f")"
            ),
            "descricao": f"Participação percentual do contexto atual sobre o total geral de {titulo}.",
        })

    # ---- 4. Time Intelligence (requer coluna de data + dCalendario) -----------
    if col_data and "dCalendario" in dados_setor:
        for col in colunas_medida:
            titulo = _titulo(col)
            medidas["📅 Time Intelligence (MoM / YoY / YTD / MTD)"].extend([
                {
                    "nome": f"{titulo} Mês Anterior",
                    "formula": (
                        f"{titulo} Mês Anterior =\n"
                        f"CALCULATE(\n"
                        f"    [Total {titulo}],\n"
                        f"    DATEADD(dCalendario[Data], -1, MONTH)\n"
                        f")"
                    ),
                    "descricao": f"Valor de {titulo} no mesmo período do mês anterior.",
                },
                {
                    "nome": f"{titulo} %MoM",
                    "formula": (
                        f"{titulo} %MoM =\n"
                        f"DIVIDE(\n"
                        f"    [Total {titulo}] - [{titulo} Mês Anterior],\n"
                        f"    [{titulo} Mês Anterior]\n"
                        f")"
                    ),
                    "descricao": f"Variação percentual de {titulo} frente ao mês anterior (Month over Month).",
                },
                {
                    "nome": f"{titulo} Ano Anterior",
                    "formula": (
                        f"{titulo} Ano Anterior =\n"
                        f"CALCULATE(\n"
                        f"    [Total {titulo}],\n"
                        f"    SAMEPERIODLASTYEAR(dCalendario[Data])\n"
                        f")"
                    ),
                    "descricao": f"Valor de {titulo} no mesmo período do ano anterior.",
                },
                {
                    "nome": f"{titulo} %YoY",
                    "formula": (
                        f"{titulo} %YoY =\n"
                        f"DIVIDE(\n"
                        f"    [Total {titulo}] - [{titulo} Ano Anterior],\n"
                        f"    [{titulo} Ano Anterior]\n"
                        f")"
                    ),
                    "descricao": f"Variação percentual de {titulo} frente ao mesmo período do ano anterior (Year over Year).",
                },
                {
                    "nome": f"{titulo} Acumulado no Ano (YTD)",
                    "formula": f"{titulo} Acumulado no Ano (YTD) = TOTALYTD([Total {titulo}], dCalendario[Data])",
                    "descricao": f"Acumulado de {titulo} desde o início do ano até a data em contexto.",
                },
                {
                    "nome": f"{titulo} Acumulado no Mês (MTD)",
                    "formula": f"{titulo} Acumulado no Mês (MTD) = TOTALMTD([Total {titulo}], dCalendario[Data])",
                    "descricao": f"Acumulado de {titulo} desde o início do mês até a data em contexto.",
                },
            ])

    return medidas
