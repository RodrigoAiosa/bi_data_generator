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


def _sufixo_fato(fato_key: str) -> str:
    """'FatoRodada' -> 'Rodada' (usado para desambiguar nomes de medida repetidos entre fatos)."""
    nome = fato_key[4:] if fato_key.startswith("Fato") else fato_key
    return nome or fato_key


def _medidas_de_uma_fato(
    dados_setor: dict,
    fato_key: str,
    multi_fato: bool,
    titulos_reservados: dict,
    contagens_reservadas: dict,
) -> dict:
    """
    Gera a bateria completa de medidas DAX para UMA tabela fato.

    `multi_fato`, `titulos_reservados` e `contagens_reservadas` vêm de
    `gerar_bateria_medidas` e são compartilhados entre todas as fatos do
    setor: garantem que, quando duas fatos diferentes produziriam a MESMA
    medida (ex.: duas fatos com FK para a mesma dimensão, ou o mesmo nome de
    coluna de negócio), a segunda ocorrência ganhe um sufixo com o nome da
    fato — evitando medidas duplicadas no modelo (erro no Power BI/TMDL).
    """
    fato = dados_setor[fato_key]
    pk_propria = fato.columns[0] if len(fato.columns) else None
    sufixo = _sufixo_fato(fato_key)

    col_data = _coluna_data(fato)
    colunas_medida = _colunas_numericas_fato(fato)
    fks = _chaves_estrangeiras(fato, pk_propria)
    if col_data:
        # A FK de data não deve entrar como "dimensão" de Qtde Distinta: já é
        # tratada separadamente pelo Time Intelligence. Mantê-la aqui também
        # causava falsos-positivos de resolução (ex.: duas fatos com a mesma
        # coluna id_data podiam se confundir uma com a outra em _nome_dimensao).
        fks = [fk for fk in fks if fk != col_data]

    medidas = {
        "🧮 Agregações Básicas": [],
        "🔢 Contagens": [],
        "📊 Percentual de Participação": [],
        "📅 Time Intelligence (MoM / YoY / YTD / MTD)": [],
    }

    # Resolve, uma única vez por coluna, o título "efetivo" (com ou sem
    # sufixo de desambiguação) — usado de forma consistente nas 3 seções
    # abaixo (agregações, % participação e time intelligence), já que elas
    # se referenciam por nome dentro da MESMA fato.
    titulo_efetivo = {}
    for col in colunas_medida:
        titulo_base = _titulo(col)
        dono = titulos_reservados.get(titulo_base)
        if dono is not None and dono != fato_key:
            titulo_efetivo[col] = f"{titulo_base} ({sufixo})"
        else:
            titulo_efetivo[col] = titulo_base
            titulos_reservados.setdefault(titulo_base, fato_key)

    # ---- 1. Agregações básicas: Total, Média, Mínimo, Máximo ----------------
    for col in colunas_medida:
        titulo = titulo_efetivo[col]
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
    nome_registros = "Qtde de Registros"
    if multi_fato:
        # "Qtde de Registros" é o mesmo literal para qualquer fato — em
        # setores multi-fato SEMPRE colide, então sempre desambiguamos.
        nome_registros = f"Qtde de Registros ({sufixo})"
    medidas["🔢 Contagens"].append({
        "nome": nome_registros,
        "formula": f"{nome_registros} = COUNTROWS({fato_key})",
        "descricao": f"Quantidade de linhas da tabela fato {fato_key} no contexto atual.",
    })
    for fk in fks:
        nome_dim = _nome_dimensao(fk, dados_setor, fato_key)
        nome_base = f"Qtde Distinta de {nome_dim}"
        dono = contagens_reservadas.get(nome_base)
        if dono is not None and dono != fato_key:
            nome_contagem = f"{nome_base} ({sufixo})"
        else:
            nome_contagem = nome_base
            contagens_reservadas.setdefault(nome_base, fato_key)
        medidas["🔢 Contagens"].append({
            "nome": nome_contagem,
            "formula": f"{nome_contagem} = DISTINCTCOUNT({fato_key}[{fk}])",
            "descricao": f"Número de {nome_dim.lower()}(s) distintos presentes na fato.",
        })

    # ---- 3. Percentual de participação (% do total) ---------------------------
    for col in colunas_medida:
        titulo = titulo_efetivo[col]
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
            titulo = titulo_efetivo[col]
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
    setor (funciona com qualquer um dos 60 setores deste projeto, incluindo
    setores multi-fato).

    Em setores com mais de uma tabela fato, desambigua automaticamente
    medidas que colidiriam (mesmo nome vindo de fatos diferentes — ex.: duas
    fatos com FK para a mesma dimensão, ou colunas de negócio com o mesmo
    nome) acrescentando o nome da fato entre parênteses, evitando o erro de
    "measure duplicada" no Power BI/TMDL.

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
    multi_fato = len(fatos) > 1
    titulos_reservados: dict = {}
    contagens_reservadas: dict = {}
    return {
        fato_key: _medidas_de_uma_fato(
            dados_setor, fato_key, multi_fato, titulos_reservados, contagens_reservadas
        )
        for fato_key in fatos
    }
