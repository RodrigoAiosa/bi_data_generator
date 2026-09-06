"""
generators/relacionamentos.py

Único lugar do projeto com a lógica de detecção de relacionamento (FK) entre
tabelas Fato/Dimensão — e entre Dimensão/Dimensão (esquema floco de neve).

Antes desta unificação, a MESMA heurística existia copiada em 3 lugares
diferentes (ui/dax_sandbox.py, generators/dax_engine.py,
generators/relatorios_gerenciais.py), e uma variação dela (usada pra achar
qual dimensão uma PERGUNTA em português está citando, não pra achar o par
de colunas de um relacionamento já conhecido) em generators/qa_engine.py.
Cada correção de bug nessa heurística (ex.: o commit bb27d66, que ensinou o
projeto a priorizar nome exato de coluna-chave antes do nome da tabela)
precisava ser replicada manualmente nos 3 primeiros lugares — risco real de
esquecer um deles numa correção futura. qa_engine.py continua com sua
própria função (_achar_dimensao), porque o problema que ela resolve é
genuinamente diferente (dado um texto em português, qual dimensão ele está
citando — não dado dois nomes de tabela já conhecidos, qual é o par de
colunas), mas reaproveita extrair_sufixo_chave() daqui pra não duplicar
nem essa peça menor.
"""

from __future__ import annotations

import pandas as pd


def extrair_sufixo_chave(nome_coluna: str) -> str:
    """Tira o prefixo id_/sk_ de uma coluna-chave, devolvendo só a parte que
    identifica o que ela referencia (ex.: 'id_profissional' -> 'profissional',
    'sk_cliente' -> 'cliente'). Usada tanto pra comparar uma FK da Fato com o
    nome de uma tabela Dim (detectar_fk) quanto pra comparar a PK de uma Dim
    com as palavras de uma pergunta em português (qa_engine._achar_dimensao)."""
    return nome_coluna.split("_", 1)[1] if "_" in nome_coluna else nome_coluna[3:]


def _bate_nome_exato(coluna_fk: str, pk_destino: str) -> bool:
    return coluna_fk.lower() == pk_destino.lower()


def _bate_por_sufixo(coluna_fk: str, tabela_destino: str) -> bool:
    sufixo_col = extrair_sufixo_chave(coluna_fk)
    sufixo_destino = tabela_destino[3:].lower() if tabela_destino.startswith("Dim") else tabela_destino.lower()
    return sufixo_col.lower() in sufixo_destino or sufixo_destino in sufixo_col.lower()


def _colunas_fk_candidatas(tabela_origem: str, tabelas: dict[str, pd.DataFrame]) -> list[str]:
    pk_proprio = tabelas[tabela_origem].columns[0]
    return [
        c for c in tabelas[tabela_origem].columns
        if c.lower().startswith(("id_", "sk_")) and c != pk_proprio
    ]


def detectar_fk(tabela_origem: str, tabela_destino: str, tabelas: dict[str, pd.DataFrame]) -> tuple[str, str] | None:
    """
    Acha o par (coluna_fk_na_origem, coluna_pk_no_destino) que liga duas
    tabelas específicas — funciona tanto pra Fato-para-Dimensão quanto pra
    Dimensão-para-Dimensão (esquema floco de neve), já que a lógica não
    assume nada sobre qual das duas é a Fato. Usada quando já se sabe QUAIS
    duas tabelas comparar (ex.: "essas duas se relacionam?").

    Prioridade de correspondência:
    1) Nome EXATO da coluna-chave (ex.: FatoProjeto.id_profissional ==
       DimEquipe.id_profissional) — o sinal mais confiável que existe,
       porque não depende do nome da TABELA bater com nada; uma dimensão
       pode muito bem ser identificada por uma chave cujo nome não tem
       nada a ver com o nome da própria tabela (ex.: "DimEquipe" é
       identificada por "id_profissional", não por "id_equipe").
    2) Fallback por sufixo do nome da tabela de destino (ex.: 'id_vendedor'
       batendo com 'DimVendedor') — usado só quando a correspondência
       exata não encontra nada.

    A própria PK da tabela de origem é excluída da lista de colunas
    candidatas a FK — sem isso, comparar Dimensão-contra-Dimensão corria
    risco de uma tabela "achar" relação consigo mesma por coincidência.

    Se a origem tiver MAIS DE UMA coluna que se relaciona com o mesmo
    destino (dimensão com papel duplo, ex.: id_operadora_origem e
    id_operadora_destino apontando pra DimOperadora), esta função devolve
    só a PRIMEIRA encontrada — para enumerar TODAS, use
    detectar_fks_para_dims().
    """
    if tabela_destino not in tabelas or tabela_origem not in tabelas:
        return None

    pk_destino = tabelas[tabela_destino].columns[0]
    fk_cols = _colunas_fk_candidatas(tabela_origem, tabelas)

    for col in fk_cols:
        if _bate_nome_exato(col, pk_destino):
            return col, pk_destino

    for col in fk_cols:
        if _bate_por_sufixo(col, tabela_destino):
            return col, pk_destino

    return None


def detectar_fks_para_dims(fato_df: pd.DataFrame, fato_nome: str, tabelas: dict[str, pd.DataFrame]) -> list[tuple[str, str, str]]:
    """
    Retorna a lista de (coluna_fk, nome_tabela_dim, coluna_pk) para TODAS
    as dimensões que se relacionam com fato_nome — inclusive dimensões com
    papel duplo (ex.: DimOperadora aparecendo duas vezes, uma para
    id_operadora_origem e outra para id_operadora_destino). Por isso itera
    por COLUNA (não por dimensão, ao contrário de detectar_fk): uma
    dimensão só consegue "achar" uma coluna por vez, mas uma Fato pode ter
    várias colunas apontando pra mesma dimensão.

    Reaproveita os mesmos predicados de correspondência (_bate_nome_exato,
    _bate_por_sufixo) usados por detectar_fk, então nunca diverge da mesma
    lógica de prioridade usada em qualquer outro lugar do projeto.
    """
    dim_tables = [n for n in tabelas if n.startswith("Dim") and n != fato_nome]
    fk_cols = _colunas_fk_candidatas(fato_nome, tabelas)

    resultado = []
    for col in fk_cols:
        melhor = None

        for dim_nome in dim_tables:
            pk_dim = tabelas[dim_nome].columns[0]
            if _bate_nome_exato(col, pk_dim):
                melhor = dim_nome
                break

        if melhor is None:
            for dim_nome in dim_tables:
                if _bate_por_sufixo(col, dim_nome):
                    melhor = dim_nome
                    break

        if melhor:
            pk_dim = tabelas[melhor].columns[0]
            resultado.append((col, melhor, pk_dim))

    return resultado
