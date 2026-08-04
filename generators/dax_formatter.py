"""
generators/dax_formatter.py: Motor de formatação de expressões DAX.

Implementa um tokenizador e um formatador que quebram expressões DAX em
múltiplas linhas com indentação por profundidade, no mesmo espírito do
daxformatter.com: cada argumento de função com vírgula vai para sua
própria linha quando a expressão é longa ou tem múltiplos argumentos,
VAR/RETURN cada um na própria linha, e espaçamento consistente ao redor
de operadores.

Não é uma cópia do motor deles (que é proprietário), é uma implementação
própria, tokenizando a expressão e decidindo quebra de linha por
profundidade de parênteses e presença de vírgulas no nível atual.
"""
import re

_LARGURA_MAX = 60

_TOKEN_RE = re.compile(r"""
    (?P<STRING>"(?:[^"\\]|\\.)*") |
    (?P<COMMENT_LINE>//[^\n]*) |
    (?P<COMMENT_DASH>--[^\n]*) |
    (?P<COMMENT_BLOCK>/\*.*?\*/) |
    (?P<COLREF>'(?:[^']|'')*'\s*\[[^\]]+\]|[^\d\W][\w]*\s*\[[^\]]+\]|\[[^\]]+\]) |
    (?P<NUMBER>\d+(?:\.\d+)?) |
    (?P<VAR_KW>\bVAR\b) |
    (?P<RETURN_KW>\bRETURN\b) |
    (?P<FUNC>[^\d\W][\w.]*(?=\s*\())  |
    (?P<IDENT>[^\d\W]\w*) |
    (?P<LPAREN>\() |
    (?P<RPAREN>\)) |
    (?P<COMMA>,) |
    (?P<OP>&&|\|\||<>|<=|>=|:=|[+\-*/=<>&%^]) |
    (?P<WS>\s+)
""", re.VERBOSE | re.DOTALL | re.IGNORECASE | re.UNICODE)

_SEM_ESPACO_ANTES = {"RPAREN", "COMMA"}


class _Grupo:
    """Representa o conteúdo entre um par de parênteses (uma chamada de
    função ou um agrupamento). 'itens' é a lista de argumentos (cada
    argumento é uma lista de tokens/_Grupo, separados pelas vírgulas de
    nível mais alto dentro desse par de parênteses)."""

    def __init__(self):
        self.itens: list = [[]]


def _tokenizar(dax: str) -> list:
    tokens = []
    for m in _TOKEN_RE.finditer(dax):
        kind = m.lastgroup
        if kind == "WS" or (kind or "").startswith("COMMENT"):
            continue
        tokens.append((kind, m.group()))
    return _juntar_sinal_unario(tokens)


def _juntar_sinal_unario(tokens: list) -> list:
    """
    Junta um sinal de menos/mais unário (ex.: o "-1" dentro de
    DATEADD(..., -1, MONTH)) com o número seguinte, num único token, pra
    não sair "- 1" com espaço estranho no meio. Só funde quando o sinal
    claramente não é uma subtração/soma binária (ou seja, quando o token
    anterior é começo de expressão, vírgula, parêntese aberto ou outro
    operador).
    """
    resultado = []
    contextos_unario = {None, "LPAREN", "COMMA", "OP", "VAR_KW", "RETURN_KW"}
    i = 0
    while i < len(tokens):
        kind, val = tokens[i]
        anterior_kind = resultado[-1][0] if resultado else None
        eh_sinal_unario = (
            kind == "OP" and val in ("-", "+")
            and i + 1 < len(tokens) and tokens[i + 1][0] == "NUMBER"
            and anterior_kind in contextos_unario
        )
        if eh_sinal_unario:
            resultado.append(("NUMBER", val + tokens[i + 1][1]))
            i += 2
            continue
        resultado.append((kind, val))
        i += 1
    return resultado


def _parsear(tokens: list) -> list:
    """Transforma a lista plana de tokens numa sequência mesclada de
    tokens e _Grupo (pra cada par de parênteses balanceado)."""
    pos = 0

    def parse_sequencia() -> list:
        nonlocal pos
        seq = []
        while pos < len(tokens):
            kind, val = tokens[pos]
            if kind == "LPAREN":
                pos += 1
                grupo = parse_grupo()
                seq.append(grupo)
                continue
            if kind == "RPAREN":
                return seq
            seq.append((kind, val))
            pos += 1
        return seq

    def parse_grupo() -> _Grupo:
        nonlocal pos
        grupo = _Grupo()
        grupo.itens = [[]]
        while pos < len(tokens):
            kind, val = tokens[pos]
            if kind == "LPAREN":
                pos += 1
                sub = parse_grupo()
                grupo.itens[-1].append(sub)
                continue
            if kind == "RPAREN":
                pos += 1
                return grupo
            if kind == "COMMA":
                grupo.itens.append([])
                pos += 1
                continue
            grupo.itens[-1].append((kind, val))
            pos += 1
        return grupo

    return parse_sequencia()


def _render_token(kind: str, val: str) -> str:
    if kind in ("VAR_KW", "RETURN_KW"):
        return val.upper()
    return val


def _render_sequencia_flat(seq: list) -> str:
    partes = []
    prev_kind = None
    for item in seq:
        if isinstance(item, _Grupo):
            texto = _render_grupo_flat(item)
            if partes and prev_kind != "FUNC":
                partes.append(" ")
            partes.append(texto)
            prev_kind = "GROUP"
            continue
        kind, val = item
        texto = _render_token(kind, val)
        if not partes or kind in _SEM_ESPACO_ANTES:
            partes.append(texto)
        else:
            partes.append(" ")
            partes.append(texto)
        prev_kind = kind
    return "".join(partes)


def _render_grupo_flat(grupo: "_Grupo") -> str:
    args = [_render_sequencia_flat(arg) for arg in grupo.itens]
    return "(" + ", ".join(args) + ")"


def _render_sequencia(seq: list, indent: int) -> str:
    partes = []
    prev_kind = None
    for item in seq:
        if isinstance(item, _Grupo):
            texto = _render_grupo(item, indent)
            if partes and prev_kind != "FUNC":
                partes.append(" ")
            partes.append(texto)
            prev_kind = "GROUP"
            continue
        kind, val = item
        texto = _render_token(kind, val)
        if not partes or kind in _SEM_ESPACO_ANTES:
            partes.append(texto)
        else:
            partes.append(" ")
            partes.append(texto)
        prev_kind = kind
    return "".join(partes)


def _render_grupo(grupo: "_Grupo", indent: int) -> str:
    flat = _render_grupo_flat(grupo)
    n_args = len(grupo.itens)
    cabe_numa_linha = n_args <= 1 and len(flat) <= _LARGURA_MAX
    if cabe_numa_linha:
        return flat

    prefixo_arg = "    " * (indent + 1)
    prefixo_fecho = "    " * indent
    linhas = []
    for arg in grupo.itens:
        texto_arg = _render_sequencia(arg, indent + 1)
        linhas.append(prefixo_arg + texto_arg)
    corpo = ",\n".join(linhas)
    return "(\n" + corpo + "\n" + prefixo_fecho + ")"


def _separar_nome_medida(dax_bruto: str):
    """Se o texto vier no formato 'Nome da Medida = expressão', separa o
    nome do resto. Se não bater esse padrão (ex.: só a expressão, sem
    nome), devolve (None, texto_original)."""
    m = re.match(r"^\s*([^\d\W][\w ]*?)\s*=\s*(?!=)(.+)$", dax_bruto, re.DOTALL | re.UNICODE)
    if m and "(" not in m.group(1) and not re.search(r"\bVAR\b|\bRETURN\b", m.group(1), re.IGNORECASE):
        return m.group(1).strip(), m.group(2)
    return None, dax_bruto


def _render_raiz(seq: list) -> str:
    """Segmenta a sequência de nível 0 em blocos por VAR/RETURN, cada um
    formatado e colocado em sua própria linha (ou bloco de linhas)."""
    blocos = []
    atual = []
    for item in seq:
        if isinstance(item, tuple) and item[0] in ("VAR_KW", "RETURN_KW") and atual:
            blocos.append(atual)
            atual = [item]
        else:
            atual.append(item)
    if atual:
        blocos.append(atual)

    linhas = [_render_sequencia(bloco, 0) for bloco in blocos]
    return "\n".join(linhas)


def formatar_dax(texto: str) -> str:
    """
    Formata uma expressão DAX: quebra em múltiplas linhas com indentação
    por profundidade de parênteses (cada argumento de função com vírgula
    numa linha própria, quando a expressão é longa ou tem múltiplos
    argumentos), VAR/RETURN cada um na sua linha, espaçamento consistente
    ao redor de operadores.
    """
    texto = texto.strip()
    if not texto:
        return ""

    nome_medida, expressao = _separar_nome_medida(texto)

    tokens = _tokenizar(expressao)
    if not tokens:
        return texto  # não deu pra tokenizar nada reconhecível, devolve como veio

    seq = _parsear(tokens)
    corpo_formatado = _render_raiz(seq)

    if nome_medida is None:
        return corpo_formatado

    linha_unica = f"{nome_medida} = {corpo_formatado}"
    if "\n" not in corpo_formatado and len(linha_unica) <= _LARGURA_MAX:
        return linha_unica
    return f"{nome_medida} =\n" + "\n".join("    " + l if l else l for l in corpo_formatado.split("\n"))
