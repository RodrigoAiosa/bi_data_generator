"""
generators/auditor_modelo.py: Motor de auditoria de modelo Power BI (TMDL).

Recebe um TMDL de verdade (colado ou enviado pelo usuário, de um modelo
real dele, não gerado por este projeto) e roda um conjunto de checagens
de qualidade e boas práticas, devolvendo uma nota (0 a 100) e uma lista
de achados categorizados, cada um com sugestão de correção.

Suporta o formato de script único do TMDL (o mesmo produzido pelo
"Script" do Tabular Editor 3 e pelo próprio gerador deste projeto):
blocos `table`, `column`, `measure`, `relationship`.

Implementação própria, baseada em análise de texto/regex, não em
nenhuma biblioteca ou serviço externo de análise de modelo.
"""
import re

_PADRAO_CHAVE = re.compile(r"^(id_|sk_|fk_)", re.IGNORECASE)
_FUNCOES_AGREGACAO = (
    "SUM(", "SUMX(", "COUNT(", "COUNTX(", "COUNTROWS(", "AVERAGE(", "AVERAGEX(",
    "DISTINCTCOUNT(", "CALCULATE(", "MIN(", "MAX(", "MINX(", "MAXX(",
)


def _extrair_medidas(texto: str) -> list:
    """
    Extrai cada medida do TMDL: nome, fórmula completa (corpo, sem o
    'measure X = ' na frente) e displayFolder (vazio se não tiver).
    Suporta tanto fórmula numa linha só quanto em bloco ``` ... ```.
    Parser linha a linha (não regex único), pra não depender de haver
    linha em branco ou displayFolder entre uma medida e a próxima.
    """
    medidas = []
    linhas = texto.split("\n")
    i = 0
    while i < len(linhas):
        m = re.match(r"^\s*measure\s+'([^']+)'\s*=\s*(.*)$", linhas[i])
        if not m:
            i += 1
            continue

        nome = m.group(1)
        resto = m.group(2).strip()

        if resto == "```":
            corpo_linhas = []
            i += 1
            while i < len(linhas) and linhas[i].strip() != "```":
                corpo_linhas.append(linhas[i].strip())
                i += 1
            formula = "\n".join(corpo_linhas)
            i += 1
        else:
            formula = resto
            i += 1

        pasta = ""
        while i < len(linhas):
            linha_atual = linhas[i].strip()
            if not linha_atual:
                i += 1
                continue
            m_pasta = re.match(r"^displayFolder:\s*(.+)$", linha_atual)
            if m_pasta:
                pasta = m_pasta.group(1).strip()
                i += 1
            break

        medidas.append({"nome": nome, "formula": formula, "pasta": pasta})

    return medidas


def _extrair_colunas(texto: str) -> list:
    """
    Extrai cada coluna de cada tabela: nome, se é calculada (tem
    'expression ='), se está marcada isHidden, e a tabela dona.
    """
    colunas = []
    tabela_atual = None
    linhas = texto.split("\n")
    bloco_coluna = None

    for linha in linhas:
        m_tabela = re.match(r"^\ttable\s+(\S+)", linha)
        if m_tabela:
            tabela_atual = m_tabela.group(1)
            continue

        m_coluna = re.match(r"^\t\tcolumn\s+(\S+)", linha)
        if m_coluna:
            if bloco_coluna:
                colunas.append(bloco_coluna)
            bloco_coluna = {
                "tabela": tabela_atual, "nome": m_coluna.group(1).strip("'\""),
                "calculada": False, "hidden": False,
            }
            continue

        if bloco_coluna is not None:
            if re.search(r"\bexpression\s*=", linha):
                bloco_coluna["calculada"] = True
            if re.search(r"\bisHidden:\s*true", linha, re.IGNORECASE):
                bloco_coluna["hidden"] = True
            if re.match(r"^\t\t(measure|column|table)\b", linha) and not re.match(r"^\t\tcolumn\s+" + re.escape(bloco_coluna["nome"]), linha):
                colunas.append(bloco_coluna)
                bloco_coluna = None

    if bloco_coluna:
        colunas.append(bloco_coluna)

    return colunas


def _extrair_relacionamentos(texto: str) -> list:
    """Extrai cada relacionamento: tabelas/colunas envolvidas e se está ativo."""
    relacionamentos = []
    padrao = re.compile(
        r"relationship\s+\S+\s*\n"
        r"\s*fromColumn:\s*(\S+)\.(\S+)\s*\n"
        r"\s*toColumn:\s*(\S+)\.(\S+)\s*\n"
        r"(\s*isActive:\s*false\s*\n)?"
    )
    for m in padrao.finditer(texto):
        relacionamentos.append({
            "tabela_from": m.group(1), "coluna_from": m.group(2),
            "tabela_to": m.group(3), "coluna_to": m.group(4),
            "ativo": m.group(5) is None,
        })
    return relacionamentos


def _normalizar_formula(formula: str) -> str:
    return re.sub(r"\s+", " ", formula).strip().upper()


def _checar_divisao_direta(medidas: list) -> list:
    achados = []
    for m in medidas:
        formula = m["formula"]
        if "DIVIDE(" in formula.upper():
            continue
        if re.search(r"[\]\)]\s*/\s*[\[\(]", formula):
            achados.append({
                "severidade": "média", "categoria": "Divisão sem DIVIDE()",
                "medida": m["nome"],
                "mensagem": f"A medida '{m['nome']}' usa divisão direta (/) em vez de DIVIDE().",
                "sugestao": "Troque por DIVIDE(numerador, denominador) para evitar erro de divisão por zero.",
            })
    return achados


def _checar_medidas_duplicadas(medidas: list) -> list:
    achados = []
    grupos: dict = {}
    for m in medidas:
        chave = _normalizar_formula(m["formula"])
        grupos.setdefault(chave, []).append(m["nome"])

    for nomes in grupos.values():
        if len(nomes) > 1:
            achados.append({
                "severidade": "alta", "categoria": "Medida duplicada",
                "medida": ", ".join(nomes),
                "mensagem": f"As medidas {', '.join(f'{n!r}' for n in nomes)} têm exatamente a mesma fórmula.",
                "sugestao": "Mantenha só uma e aponte as demais como referência, ou apague as redundantes.",
            })
    return achados


def _checar_medidas_sem_pasta(medidas: list) -> list:
    sem_pasta = [m["nome"] for m in medidas if not m["pasta"]]
    if not sem_pasta:
        return []
    return [{
        "severidade": "baixa", "categoria": "Organização (displayFolder)",
        "medida": ", ".join(sem_pasta[:10]) + (f" (+{len(sem_pasta) - 10})" if len(sem_pasta) > 10 else ""),
        "mensagem": f"{len(sem_pasta)} medida(s) sem displayFolder definido.",
        "sugestao": "Organize as medidas em pastas (ex.: Agregações Básicas, Time Intelligence) para facilitar navegação no relatório.",
    }]


def _checar_colunas_calculadas_suspeitas(colunas: list) -> list:
    achados = []
    for c in colunas:
        if not c["calculada"]:
            continue
        achados.append({
            "severidade": "média", "categoria": "Coluna calculada que pode virar medida",
            "medida": f"{c['tabela']}[{c['nome']}]",
            "mensagem": f"'{c['tabela']}[{c['nome']}]' é uma coluna calculada.",
            "sugestao": "Se o cálculo não depende de contexto de linha específico, considere virar medida: ocupa menos memória e recalcula sob demanda.",
        })
    return achados


def _checar_chaves_expostas(colunas: list) -> list:
    expostas = [f"{c['tabela']}[{c['nome']}]" for c in colunas if _PADRAO_CHAVE.match(c["nome"]) and not c["hidden"]]
    if not expostas:
        return []
    return [{
        "severidade": "baixa", "categoria": "Coluna técnica exposta",
        "medida": ", ".join(expostas[:10]) + (f" (+{len(expostas) - 10})" if len(expostas) > 10 else ""),
        "mensagem": f"{len(expostas)} coluna(s) de chave/FK sem isHidden.",
        "sugestao": "Marque colunas técnicas (id_*, sk_*, fk_*) como ocultas (isHidden: true) para não confundir quem usa o relatório.",
    }]


def _checar_nomenclatura_inconsistente(medidas: list) -> list:
    if len(medidas) < 4:
        return []

    def _estilo(nome: str) -> str:
        if "_" in nome:
            return "snake_case"
        if nome[:1].isupper() and " " in nome:
            return "Title Case"
        if nome[:1].islower():
            return "camelCase"
        return "outro"

    estilos = [_estilo(m["nome"]) for m in medidas]
    contagem = {e: estilos.count(e) for e in set(estilos)}
    if len(contagem) <= 1:
        return []

    predominante = max(contagem, key=contagem.get)
    minoritarios = sum(v for k, v in contagem.items() if k != predominante)
    if minoritarios < max(2, len(medidas) * 0.15):
        return []

    return [{
        "severidade": "baixa", "categoria": "Nomenclatura inconsistente",
        "medida": "(modelo inteiro)",
        "mensagem": f"As medidas misturam estilos de nomenclatura ({', '.join(contagem.keys())}), a maioria em {predominante}.",
        "sugestao": "Padronize um estilo só de nome de medida em todo o modelo, facilita achar e manter.",
    }]


def auditar_modelo(texto_tmdl: str) -> dict:
    """
    Roda todas as checagens no TMDL informado e devolve um relatório
    estruturado: {"nota": int, "achados": [...], "resumo": {...}}.
    """
    medidas = _extrair_medidas(texto_tmdl)
    colunas = _extrair_colunas(texto_tmdl)
    relacionamentos = _extrair_relacionamentos(texto_tmdl)

    achados = []
    achados += _checar_divisao_direta(medidas)
    achados += _checar_medidas_duplicadas(medidas)
    achados += _checar_medidas_sem_pasta(medidas)
    achados += _checar_colunas_calculadas_suspeitas(colunas)
    achados += _checar_chaves_expostas(colunas)
    achados += _checar_nomenclatura_inconsistente(medidas)

    pesos = {"alta": 8, "média": 4, "baixa": 1.5}
    desconto_total = sum(pesos.get(a["severidade"], 1) for a in achados)
    nota = max(0, round(100 - desconto_total))

    return {
        "nota": nota,
        "achados": achados,
        "resumo": {
            "total_medidas": len(medidas),
            "total_colunas": len(colunas),
            "total_relacionamentos": len(relacionamentos),
            "total_achados": len(achados),
        },
    }
