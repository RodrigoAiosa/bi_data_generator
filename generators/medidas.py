"""
generators/medidas.py
Gerador automático de uma bateria de medidas DAX para QUALQUER setor produzido
pelos geradores deste projeto (funciona para os 55 setores, sem precisar de
configuração manual por setor).

Funciona com os dois padrões de chave usados no projeto:
  - "id_*"  (padrão mais antigo, ex.: varejo, financeiro, crm, governo...)
  - "sk_*"  (padrão mais novo, ex.: ecommerce, fintech, hotelaria, mobilidade,
             rh, streaming...)

E também com setores multi-fato (ex.: CRM tem FatoOportunidade + FatoAtividade;
Governo tem FatoDespesa + FatoReceita + FatoLicitacao).

Para cada tabela Fato* encontrada em `dados_setor`, identifica:
  - colunas numéricas "de negócio" (ignora chaves id_*/sk_*, partes de data
    como ano/mes/dia_semana/hora, coordenadas e colunas booleanas)
  - a coluna de data da fato (para ligar com dCalendario)
  - as chaves estrangeiras (FKs) que apontam para dimensões (ou outras fatos,
    no caso de relações fato-a-fato / bridge)

E gera, para CADA coluna numérica encontrada, uma bateria de medidas:
  - Agregações básicas: Total, Média, Mínimo, Máximo
  - Contagens: linhas da fato e distinct count de cada dimensão relacionada
  - Percentual de participação (% do Total)
  - Time Intelligence: Mês Anterior, %MoM, Ano Anterior, %YoY, YTD, MTD
"""

import pandas as pd

# Colunas técnicas que nunca devem virar medida, mesmo sendo numéricas.
_COLUNAS_TECNICAS_IGNORADAS = {
    "ano", "mes", "trimestre", "dia", "dia_semana", "hora",
    "latitude", "longitude", "idmesano",
}

_PREFIXOS_CHAVE = ("id_", "sk_")


def _e_coluna_chave(col: str) -> bool:
    """True se a coluna é uma chave (PK/FK) pelo padrão id_*/sk_*."""
    return col.lower().startswith(_PREFIXOS_CHAVE)


def _colunas_numericas_fato(fato: pd.DataFrame) -> list:
    """Colunas numéricas 'de negócio' da fato — ignora chaves e colunas técnicas."""
    colunas = []
    for c in fato.columns:
        if _e_coluna_chave(c):
            continue
        if c.lower() in _COLUNAS_TECNICAS_IGNORADAS:
            continue
        if pd.api.types.is_bool_dtype(fato[c]):
            continue
        if pd.api.types.is_numeric_dtype(fato[c]):
            colunas.append(c)
    return colunas


def _coluna_data(fato: pd.DataFrame) -> str | None:
    """
    Encontra a coluna de data da tabela fato para ligar com dCalendario.
    Prioriza colunas 'id_data*'/'sk_data*' (convenção do projeto) e, na
    ausência delas, qualquer coluna cujo nome contenha 'data' ou que seja
    datetime.
    """
    candidatas = [c for c in fato.columns if "data" in c.lower()]
    if not candidatas:
        candidatas = [c for c in fato.columns if pd.api.types.is_datetime64_any_dtype(fato[c])]
    if not candidatas:
        return None
    # Prioriza a que começa com id_data / sk_data (a FK "oficial" para o calendário)
    for c in candidatas:
        if c.lower().startswith(("id_data", "sk_data")):
            return c
    return candidatas[0]


def _chaves_estrangeiras(fato: pd.DataFrame, pk_propria: str | None) -> list:
    """
    Colunas id_*/sk_* que são chave estrangeira (FK): repetem-se ao longo da
    fato (nunique < total de linhas). A PK da própria fato (1ª coluna,
    normalmente única linha a linha) não entra nessa lista.
    """
    total_linhas = len(fato)
    fks = []
    for c in fato.columns:
        if not _e_coluna_chave(c):
            continue
        if c == pk_propria:
            continue
        if fato[c].nunique(dropna=True) < total_linhas:
            fks.append(c)
    return fks


def _nome_dimensao(fk_coluna: str, dados_setor: dict, fato_key: str) -> str:
    """
    Nome legível da dimensão associada a uma FK: procura, entre todas as
    outras tabelas do setor, qual delas contém essa mesma coluna (geralmente
    como PK). Cobre tanto Dim* quanto relações fato-a-fato (bridge).
    """
    for nome_tabela, df in dados_setor.items():
        if nome_tabela == fato_key:
            continue
        if fk_coluna in df.columns:
            return nome_tabela.replace("Dim", "").replace("Fato", "")
    # Fallback: deriva do nome da própria coluna (id_cliente -> Cliente)
    base = fk_coluna
    for pref in _PREFIXOS_CHAVE:
        if base.lower().startswith(pref):
            base = base[len(pref):]
            break
    return base.replace("_", " ").title()


def _titulo(col: str) -> str:
    """'valor_total' -> 'Valor Total' (nome legível para a medida)."""
    return " ".join(p.capitalize() for p in col.split("_"))


def _medidas_de_uma_fato(dados_setor: dict, fato_key: str) -> dict:
    """Gera a bateria completa de medidas DAX para UMA tabela fato."""
    fato = dados_setor[fato_key]
    pk_propria = fato.columns[0] if len(fato.columns) else None

    col_data = _coluna_data(fato)
    colunas_medida = _colunas_numericas_fato(fato)
    fks = _chaves_estrangeiras(fato, pk_propria)

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
        nome_dim = _nome_dimensao(fk, dados_setor, fato_key)
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


def gerar_bateria_medidas(dados_setor: dict) -> dict:
    """
    Gera a bateria completa de medidas DAX para TODAS as tabelas fato de um
    setor (funciona com qualquer um dos 55 setores deste projeto, incluindo
    setores multi-fato).

    Parâmetros
    ----------
    dados_setor : dict
        Dicionário {nome_tabela: DataFrame} retornado por qualquer gerador
        de generators/*.py (ex.: gerar_varejo(...)), incluindo a dCalendario.

    Retorna
    -------
    dict {fato_key: {categoria: [ {"nome", "formula", "descricao"}, ... ]}}
    """
    fatos = [k for k in dados_setor if k.startswith("Fato")]
    return {fato_key: _medidas_de_uma_fato(dados_setor, fato_key) for fato_key in fatos}
