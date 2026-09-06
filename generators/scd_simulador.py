# -*- coding: utf-8 -*-
"""
generators/scd_simulador.py

Motor da aba "🕰️ Simulador de Dimensões Mutáveis" — pega uma dimensão já
gerada (ex.: DimCliente) e simula a passagem do tempo: gera uma segunda
"fotografia" dela (T1) com um número controlado de mudanças reais
injetadas em cima da original (T0), junto com um GABARITO exato de qual
linha mudou, em que coluna, de que valor pra que valor.

A partir do par T0/T1, também gera as 3 formas clássicas de tratar
Slowly Changing Dimensions:
- Tipo 1 (sobrescreve): a dimensão vira T1 direto, sem guardar histórico
- Tipo 2 (nova linha + intervalo de validade): mantém a linha antiga
  "fechada" e adiciona uma linha nova pro registro atual
- Tipo 3 (coluna "anterior"): mantém uma única linha, guardando o valor
  anterior numa coluna extra ao lado da coluna que mudou

Isso serve tanto pra CONFERIR uma implementação manual (o usuário tenta
sozinho e compara com o gabarito) quanto pra ESTUDAR o resultado correto
diretamente, no mesmo espírito de honestidade já usado em
generators/causal.py (gabarito sempre verificável, nunca "confia em mim").
"""

from __future__ import annotations

import random

import pandas as pd

_DATA_CORTE = pd.Timestamp("2024-07-01")
_DATA_FIM_ABERTA = pd.Timestamp("2099-12-31")

# Colunas que, mesmo sendo texto, não fazem sentido "mudar" nesse exercício
# (são documentos/identificadores pessoais, não atributos de negócio).
_COLUNAS_IMUTAVEIS = {"cpf", "cnpj", "email", "rg", "passaporte"}


class ScdError(Exception):
    """Erro amigável quando a dimensão escolhida não serve pra este exercício."""


def _parece_data_pelo_nome(nome_coluna: str) -> bool:
    """Mesma heurística de generators/sql_generator.py:_infer_sql_type —
    reaproveitada aqui só como checagem simples (não vale a pena importar
    o módulo inteiro pra isso)."""
    col_lower = nome_coluna.lower()
    return (
        any(p in col_lower for p in ["data", "date", "dt_", "vencimento", "validade"])
        or col_lower.endswith("_at")
    )


def _colunas_mutaveis(dim_df: pd.DataFrame) -> list[str]:
    """Colunas candidatas a receber uma mudança: só TEXTO (não booleano —
    mistura tipos na coluna do gabarito e quebra a serialização Arrow do
    Streamlit, além de não ser uma história clássica de SCD), não é a PK,
    não é uma FK (id_/sk_), não é um documento pessoal nem uma data (mudar
    "quando o projeto começou" não é uma história de SCD clássica — o
    clássico é atributo descritivo mudando, tipo cliente trocando de
    cidade), e tem pelo menos 2 valores distintos na dimensão inteira
    (senão não há pra onde 'mudar')."""
    pk = dim_df.columns[0]
    candidatas = []
    for col in dim_df.columns:
        if col == pk:
            continue
        if col.lower().startswith(("id_", "sk_")):
            continue
        if col.lower() in _COLUNAS_IMUTAVEIS:
            continue
        if _parece_data_pelo_nome(col):
            continue
        if not pd.api.types.is_string_dtype(dim_df[col]):
            continue
        if dim_df[col].nunique(dropna=True) < 2:
            continue
        candidatas.append(col)
    return candidatas


def gerar_cenario_scd(
    tabelas: dict[str, pd.DataFrame],
    nome_dim: str,
    n_mudancas: int,
    seed: int | None = None,
) -> dict:
    """
    Gera o cenário completo de dimensão mutável a partir de uma dimensão
    já existente em `tabelas[nome_dim]`.

    Devolve um dict com:
    - snapshot_t0, snapshot_t1: as duas fotografias da dimensão
    - gabarito: DataFrame (pk, coluna, valor_antigo, valor_novo)
    - scd_tipo1, scd_tipo2, scd_tipo3: os 3 resultados corretos
    - coluna_pk: nome da coluna de chave primária da dimensão
    """
    if nome_dim not in tabelas:
        raise ScdError(f"Dimensão '{nome_dim}' não encontrada na base gerada.")

    dim_original = tabelas[nome_dim]
    pk = dim_original.columns[0]
    colunas_mutaveis = _colunas_mutaveis(dim_original)

    if not colunas_mutaveis:
        raise ScdError(
            f"'{nome_dim}' não tem nenhuma coluna com pelo menos 2 valores "
            "diferentes pra simular uma mudança (fora chaves e documentos "
            "pessoais). Tente outra dimensão."
        )

    n_mudancas = max(1, min(n_mudancas, len(dim_original)))

    rng = random.Random(seed)
    linhas_escolhidas = rng.sample(list(dim_original.index), n_mudancas)

    snapshot_t0 = dim_original.copy()
    snapshot_t1 = dim_original.copy()
    registros_gabarito = []

    for idx in linhas_escolhidas:
        coluna = rng.choice(colunas_mutaveis)
        valor_atual = dim_original.at[idx, coluna]
        valores_alternativos = [
            v for v in dim_original[coluna].dropna().unique() if v != valor_atual
        ]
        if not valores_alternativos:
            continue  # linha/coluna sem alternativa real de sobra, pula
        valor_novo = rng.choice(valores_alternativos)

        snapshot_t1.at[idx, coluna] = valor_novo
        registros_gabarito.append({
            pk: dim_original.at[idx, pk],
            "coluna": coluna,
            "valor_antigo": valor_atual,
            "valor_novo": valor_novo,
        })

    if not registros_gabarito:
        raise ScdError(
            f"Não consegui gerar nenhuma mudança de verdade em '{nome_dim}' "
            "com os dados atuais — tente aumentar o volume de dados gerado "
            "ou escolher outra dimensão."
        )

    gabarito = pd.DataFrame(registros_gabarito)

    scd_tipo1 = snapshot_t1.copy()
    scd_tipo2 = _montar_scd_tipo2(snapshot_t0, snapshot_t1, pk, gabarito)
    scd_tipo3 = _montar_scd_tipo3(snapshot_t1, pk, gabarito)

    return {
        "snapshot_t0": snapshot_t0,
        "snapshot_t1": snapshot_t1,
        "gabarito": gabarito,
        "scd_tipo1": scd_tipo1,
        "scd_tipo2": scd_tipo2,
        "scd_tipo3": scd_tipo3,
        "coluna_pk": pk,
    }


def _montar_scd_tipo2(t0: pd.DataFrame, t1: pd.DataFrame, pk: str, gabarito: pd.DataFrame) -> pd.DataFrame:
    """SCD Tipo 2: linhas que mudaram viram DUAS linhas (a antiga, fechada
    com DataFimValidade; e uma nova, aberta) — precisa de uma chave
    substituta (sk_scd) própria, já que a PK natural se repete."""
    pks_alterados = set(gabarito[pk])
    linhas = []
    sk_seq = 1

    for _, linha_t1 in t1.iterrows():
        chave = linha_t1[pk]
        if chave in pks_alterados:
            linha_antiga = t0.loc[t0[pk] == chave].iloc[0].to_dict()
            linha_antiga.update({
                "sk_scd": sk_seq, "DataInicioValidade": pd.NaT,
                "DataFimValidade": _DATA_CORTE, "RegistroAtual": False,
            })
            linhas.append(linha_antiga)
            sk_seq += 1

            linha_nova = linha_t1.to_dict()
            linha_nova.update({
                "sk_scd": sk_seq, "DataInicioValidade": _DATA_CORTE,
                "DataFimValidade": _DATA_FIM_ABERTA, "RegistroAtual": True,
            })
            linhas.append(linha_nova)
            sk_seq += 1
        else:
            linha = linha_t1.to_dict()
            linha.update({
                "sk_scd": sk_seq, "DataInicioValidade": pd.NaT,
                "DataFimValidade": _DATA_FIM_ABERTA, "RegistroAtual": True,
            })
            linhas.append(linha)
            sk_seq += 1

    colunas_ordem = ["sk_scd"] + list(t1.columns) + ["DataInicioValidade", "DataFimValidade", "RegistroAtual"]
    return pd.DataFrame(linhas)[colunas_ordem]


def _montar_scd_tipo3(t1: pd.DataFrame, pk: str, gabarito: pd.DataFrame) -> pd.DataFrame:
    """SCD Tipo 3: continua UMA linha por chave, mas cada coluna que teve
    alguma mudança registrada ganha uma coluna irmã '<coluna>_Anterior',
    preenchida só nas linhas que de fato mudaram naquela coluna."""
    resultado = t1.copy()
    colunas_alteradas = gabarito["coluna"].unique()

    for coluna in colunas_alteradas:
        nome_coluna_anterior = f"{coluna}_Anterior"
        resultado[nome_coluna_anterior] = pd.NA
        subset = gabarito[gabarito["coluna"] == coluna]
        for _, registro in subset.iterrows():
            mask = resultado[pk] == registro[pk]
            resultado.loc[mask, nome_coluna_anterior] = registro["valor_antigo"]

    return resultado
