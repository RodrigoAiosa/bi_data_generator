# -*- coding: utf-8 -*-
"""
scripts/fatos_projeto.py

Funções que recalculam os números REAIS do projeto (quantidade de
setores, de medidas DAX geradas, e de abas/ferramentas) direto do código
— nunca um número fixo mantido à mão. Usado por sync_apresentacao.py e
sync_readme.py, pra garantir que os dois nunca divirjam entre si (o
mesmo motivo pelo qual generators/relacionamentos.py existe: uma conta
só, reaproveitada em todo lugar que precisa dela).
"""

from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))


def contar_setores() -> int:
    from config import SETORES
    return len(SETORES)


def contar_medidas_dax_por_setor(amostra_por_setor: int = 50) -> dict[str, int]:
    """Igual a contar_medidas_dax(), mas devolve a contagem de CADA setor
    individualmente (nome -> quantidade), não só o total somado. Usada pra
    manter em sincronia tanto o total quanto a tabela por-setor do README —
    gerando os dados uma vez só, evitando duas rodadas (com contagens
    ligeiramente diferentes, já que a amostra usa dados aleatórios) para o
    total e para a tabela."""
    from config import SETORES, obter_gerador
    from generators.medidas import gerar_bateria_medidas

    inicio = datetime.date(2024, 1, 1)
    fim = datetime.date(2024, 12, 31)
    resultado: dict[str, int] = {}
    for nome in SETORES:
        fn = obter_gerador(nome)
        tabelas = fn(amostra_por_setor, inicio, fim)
        medidas = gerar_bateria_medidas(tabelas)
        resultado[nome] = sum(len(lista) for cats in medidas.values() for lista in cats.values())
    return resultado


def contar_medidas_dax(amostra_por_setor: int = 50) -> int:
    """Gera uma amostra pequena de cada setor (rápido, ~5s pros 200) e soma
    a bateria de medidas DAX sugeridas — a mesma lógica usada em produção."""
    return sum(contar_medidas_dax_por_setor(amostra_por_setor).values())


def contar_ferramentas() -> int:
    """Conta quantas abas existem de verdade em app.py, lendo a lista
    passada pra st.tabs([...]) — não um número fixo mantido à mão."""
    texto_app = (RAIZ / "app.py").read_text(encoding="utf-8")
    m = re.search(r"st\.tabs\(\s*\[(.*?)\]\s*,?\s*\)", texto_app, re.DOTALL)
    if not m:
        raise RuntimeError("Não encontrei a chamada st.tabs([...]) em app.py — layout mudou?")
    lista_literal = m.group(1)
    # Cada aba é uma string entre aspas — conta quantas strings tem na lista
    abas = re.findall(r'"[^"]*"', lista_literal)
    return len(abas)
