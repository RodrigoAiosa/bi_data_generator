"""
ui/cache_utils.py — Cache da geração bruta (pré-anomalia/deriva) de um setor.

Evita regerar os dados do zero quando o setor/volume/período não mudaram
desde a última geração — por exemplo, ao clicar em "Gerar & Baixar SQL" logo
depois de já ter gerado os mesmos dados na aba "Gerador de Setores", ou ao
só ligar/desligar anomalia/deriva sem mudar setor/volume/datas.

Módulo separado (em vez de viver em app.py) para poder ser importado tanto
por app.py quanto por ui/sidebar.py sem criar import circular, já que
app.py importa de ui/sidebar.py (não o contrário).
"""

import streamlit as st

from config import SETORES


def _chave_cache(setor: str, n_linhas: int, data_inicio, data_fim) -> tuple:
    return (setor, n_linhas, str(data_inicio), str(data_fim))


def gerar_bruto_com_cache(setor: str, n_linhas: int, data_inicio, data_fim) -> dict:
    """
    Retorna as tabelas cruas (sem anomalia/deriva) do setor, reaproveitando
    o cache em st.session_state quando a chave (setor, volume, datas) é a
    mesma da última geração.

    Seguro reaproveitar o mesmo objeto cacheado sem cópia defensiva: as
    funções de anomalia/deriva sempre copiam antes de modificar (`.copy()`),
    e os geradores de SQL/relatórios gerenciais só leem os DataFrames — não
    escrevem neles.
    """
    chave = _chave_cache(setor, n_linhas, data_inicio, data_fim)
    cache = st.session_state.get("_raw_cache")
    if cache is not None and cache["chave"] == chave:
        return cache["tabelas"]

    fn = SETORES[setor]
    tabelas = fn(n_linhas, data_inicio, data_fim)
    st.session_state["_raw_cache"] = {"chave": chave, "tabelas": tabelas}
    return tabelas
