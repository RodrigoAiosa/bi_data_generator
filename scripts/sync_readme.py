# -*- coding: utf-8 -*-
"""
scripts/sync_readme.py

Recalcula os números reais do projeto (setores, medidas DAX, abas) e
atualiza toda menção a eles dentro do README.md — sem tocar em mais nada
do texto. Usa os mesmos números que scripts/sync_apresentacao.py calcula
(via scripts/fatos_projeto.py), então os dois nunca divergem entre si.

Rodado automaticamente pelo GitHub Action .github/workflows/sync-apresentacao.yml
a cada push na main que mexa em config.py, app.py ou generators/**. Também
pode ser rodado manualmente:

    python scripts/sync_readme.py           # aplica as mudanças
    python scripts/sync_readme.py --check   # só mostra o que mudaria, não salva

Assim como sync_apresentacao.py, isso só sincroniza NÚMEROS — se uma aba
nova for adicionada, a contagem "10 abas" vira "11 abas" em todo lugar
automaticamente, mas a FRASE descrevendo cada aba (a lista por extenso no
topo do README) continua exigindo edição manual, porque isso é texto
qualitativo, não um número derivável do código.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CAMINHO_README = RAIZ / "README.md"

sys.path.insert(0, str(RAIZ))

from scripts.fatos_projeto import contar_setores, contar_medidas_dax_por_setor, contar_ferramentas  # noqa: E402

# Cada padrão captura só o NÚMERO a substituir (grupo 1), preservando o
# resto do texto ao redor exatamente como está — não reescreve a frase.
_PADRAO_SETORES = re.compile(r"(\d[\d.]*)(\s+setores\b)")
_PADRAO_MEDIDAS = re.compile(r"(\d[\d.]*)(\s+medidas(?:\s+DAX)?\s+diferentes\b)")
_PADRAO_ABAS = re.compile(r"(\*\*)(\d+)(\s+abas\*\*)")

_INICIO_TABELA = "| Setor | Medidas DAX |"


def _montar_tabela_medidas(medidas_por_setor: dict[str, int]) -> str:
    linhas = [_INICIO_TABELA, "| --- | --- |"]
    for nome, qtd in sorted(medidas_por_setor.items(), key=lambda item: -item[1]):
        linhas.append(f"| {nome} | {qtd} |")
    return "\n".join(linhas)


def atualizar_tabela_medidas_por_setor(medidas_por_setor: dict[str, int], aplicar: bool) -> list[str]:
    """Substitui a tabela inteira 'Setor | Medidas DAX' pelo conteúdo
    recalculado, sem tocar em nada antes ou depois dela. A tabela vai do
    cabeçalho conhecido até a primeira linha em branco seguinte."""
    texto = CAMINHO_README.read_text(encoding="utf-8")

    inicio = texto.find(_INICIO_TABELA)
    if inicio == -1:
        return [f"AVISO: não encontrei a tabela '{_INICIO_TABELA}' no README — pulei essa parte."]

    fim = texto.find("\n\n", inicio)
    if fim == -1:
        return ["AVISO: não encontrei o fim da tabela de medidas — pulei essa parte."]

    tabela_atual = texto[inicio:fim]
    tabela_nova = _montar_tabela_medidas(medidas_por_setor)

    if tabela_atual.strip() == tabela_nova.strip():
        return []

    if aplicar:
        texto = texto[:inicio] + tabela_nova + texto[fim:]
        CAMINHO_README.write_text(texto, encoding="utf-8")

    return ["Tabela 'Setor | Medidas DAX' recalculada (200 linhas)."]


def atualizar_readme(n_setores: int, n_medidas: int, n_ferramentas: int, aplicar: bool) -> list[str]:
    texto = CAMINHO_README.read_text(encoding="utf-8")
    original = texto
    mudancas: list[str] = []
    medidas_fmt = f"{n_medidas:,}".replace(",", ".")

    def _sub_setores(m: re.Match) -> str:
        if m.group(1) != str(n_setores):
            mudancas.append(f"'{m.group(1)}{m.group(2)}' -> '{n_setores}{m.group(2)}'")
        return f"{n_setores}{m.group(2)}"

    def _sub_medidas(m: re.Match) -> str:
        if m.group(1) != medidas_fmt:
            mudancas.append(f"'{m.group(1)}{m.group(2)}' -> '{medidas_fmt}{m.group(2)}'")
        return f"{medidas_fmt}{m.group(2)}"

    def _sub_abas(m: re.Match) -> str:
        if m.group(2) != str(n_ferramentas):
            mudancas.append(f"'{m.group(1)}{m.group(2)}{m.group(3)}' -> '{m.group(1)}{n_ferramentas}{m.group(3)}'")
        return f"{m.group(1)}{n_ferramentas}{m.group(3)}"

    texto = _PADRAO_SETORES.sub(_sub_setores, texto)
    texto = _PADRAO_MEDIDAS.sub(_sub_medidas, texto)
    texto = _PADRAO_ABAS.sub(_sub_abas, texto)

    if aplicar and texto != original:
        CAMINHO_README.write_text(texto, encoding="utf-8")

    return mudancas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Só mostra o que mudaria, não salva o arquivo.")
    args = parser.parse_args()

    print("Recalculando números reais do projeto...")
    n_setores = contar_setores()
    n_ferramentas = contar_ferramentas()
    print(f"  Setores: {n_setores}")
    print(f"  Ferramentas (abas): {n_ferramentas}")
    print("  Medidas DAX por setor (gerando amostra dos 200 setores, ~5s)...")
    medidas_por_setor = contar_medidas_dax_por_setor()
    n_medidas = sum(medidas_por_setor.values())
    print(f"  Medidas DAX (total): {n_medidas}")

    mudancas = atualizar_readme(n_setores, n_medidas, n_ferramentas, aplicar=not args.check)
    mudancas += atualizar_tabela_medidas_por_setor(medidas_por_setor, aplicar=not args.check)

    if not mudancas:
        print("\n✅ O README já está com os números corretos — nada pra atualizar.")
    else:
        verbo = "Seriam feitas" if args.check else "Foram feitas"
        print(f"\n{verbo} {len(mudancas)} mudança(s):")
        for m in mudancas:
            print(f"  - {m}")
        if not args.check:
            print(f"\n✅ Arquivo salvo: {CAMINHO_README}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
