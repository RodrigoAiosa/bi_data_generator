"""
generators/m_formatter.py: Motor de formatação de código M (Power Query).

Reaproveita o mesmo princípio do formatador de DAX (tokenizar e quebrar
por profundidade de parênteses/colchetes/chaves), adaptado pra sintaxe
própria do M: bloco `let ... in ...`, cada passo numa linha própria,
identificadores entre aspas (#"Nome do Passo"), record `[Campo = valor]`
e lista `{item1, item2}`.

Implementação própria, não chama nenhum serviço externo.
"""
import re

_LARGURA_MAX = 60

_TOKEN_RE = re.compile(r"""
    (?P<QIDENT>\#"(?:[^"]|"")*") |
    (?P<STRING>"(?:[^"]|"")*") |
    (?P<COMMENT_LINE>//[^\n]*) |
    (?P<COMMENT_BLOCK>/\*.*?\*/) |
    (?P<NUMBER>\d+(?:\.\d+)?) |
    (?P<KEYWORD>\b(?:let|in|each|if|then|else|try|otherwise|and|or|not|error|meta|type|as|is)\b) |
    (?P<IDENT>[^\d\W][\w.]*) |
    (?P<ARROW>=>) |
    (?P<LPAREN>\() | (?P<RPAREN>\)) |
    (?P<LBRACE>\{) | (?P<RBRACE>\}) |
    (?P<LBRACKET>\[) | (?P<RBRACKET>\]) |
    (?P<OP>\.\.|<>|<=|>=|[+\-*/=<>&,]) |
    (?P<WS>\s+)
""", re.VERBOSE | re.DOTALL | re.UNICODE | re.IGNORECASE)

_ABERTURAS = {"LPAREN": ("(", ")", "RPAREN"), "LBRACE": ("{", "}", "RBRACE"), "LBRACKET": ("[", "]", "RBRACKET")}
_FECHAMENTOS = {"RPAREN", "RBRACE", "RBRACKET"}
_SEM_ESPACO_ANTES = {"RPAREN", "RBRACE", "RBRACKET", "OP_VIRGULA"}


class _Grupo:
    """Conteúdo entre um par de parênteses/chaves/colchetes. 'itens' é a
    lista de argumentos, separados pelas vírgulas de nível mais alto
    dentro desse par."""

    def __init__(self, abre_kind: str):
        self.abre_kind = abre_kind
        self.itens: list = [[]]


def _tokenizar(m_bruto: str) -> list:
    tokens = []
    for m in _TOKEN_RE.finditer(m_bruto):
        kind = m.lastgroup
        if kind == "WS" or (kind or "").startswith("COMMENT"):
            continue
        tokens.append((kind, m.group()))
    return tokens


def _parsear_sequencia(tokens: list) -> list:
    """Transforma a lista plana de tokens numa sequência mesclada de
    tokens e _Grupo, pra cada par de parênteses/chaves/colchetes."""
    pos = 0

    def parse_seq() -> list:
        nonlocal pos
        seq = []
        while pos < len(tokens):
            kind, val = tokens[pos]
            if kind in _ABERTURAS:
                pos += 1
                seq.append(parse_grupo(kind))
                continue
            if kind in _FECHAMENTOS:
                return seq
            seq.append((kind, val))
            pos += 1
        return seq

    def parse_grupo(abre_kind: str) -> _Grupo:
        nonlocal pos
        grupo = _Grupo(abre_kind)
        while pos < len(tokens):
            kind, val = tokens[pos]
            if kind in _ABERTURAS:
                pos += 1
                sub = parse_grupo(kind)
                grupo.itens[-1].append(sub)
                continue
            if kind in _FECHAMENTOS:
                pos += 1
                return grupo
            if kind == "OP" and val == ",":
                grupo.itens.append([])
                pos += 1
                continue
            grupo.itens[-1].append((kind, val))
            pos += 1
        return grupo

    return parse_seq()


def _render_token(kind: str, val: str) -> str:
    if kind == "KEYWORD":
        return val.lower()
    return val


def _junta(partes: list, item, prev_kind: str, texto: str) -> str:
    if not partes:
        return texto
    if item[0] == "OP" and item[1] == ",":
        return texto
    if isinstance(item, tuple) and item[0] in _FECHAMENTOS:
        return texto
    return " " + texto


def _render_sequencia_flat(seq: list) -> str:
    partes = []
    prev_kind = None
    for item in seq:
        if isinstance(item, _Grupo):
            texto = _render_grupo_flat(item)
            if partes and prev_kind != "IDENT":
                partes.append(" ")
            partes.append(texto)
            prev_kind = "GROUP"
            continue
        kind, val = item
        texto = _render_token(kind, val)
        if not partes or kind in _FECHAMENTOS:
            partes.append(texto)
        else:
            partes.append(" ")
            partes.append(texto)
        prev_kind = kind
    return "".join(partes)


def _render_grupo_flat(grupo: "_Grupo") -> str:
    abre, fecha, _ = _ABERTURAS[grupo.abre_kind]
    args = [_render_sequencia_flat(arg) for arg in grupo.itens]
    return abre + ", ".join(args) + fecha


def _render_sequencia(seq: list, indent: int) -> str:
    partes = []
    prev_kind = None
    for item in seq:
        if isinstance(item, _Grupo):
            texto = _render_grupo(item, indent)
            if partes and prev_kind != "IDENT":
                partes.append(" ")
            partes.append(texto)
            prev_kind = "GROUP"
            continue
        kind, val = item
        texto = _render_token(kind, val)
        if not partes or kind in _FECHAMENTOS:
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

    abre, fecha, _ = _ABERTURAS[grupo.abre_kind]
    prefixo_arg = "    " * (indent + 1)
    prefixo_fecho = "    " * indent
    linhas = [prefixo_arg + _render_sequencia(arg, indent + 1) for arg in grupo.itens]
    corpo = ",\n".join(linhas)
    return abre + "\n" + corpo + "\n" + prefixo_fecho + fecha


def _dividir_passos_top_level(tokens: list):
    """
    Acha 'let' e 'in' de nível 0 (fora de qualquer parênteses/colchete/
    chave). Se não encontrar os dois, devolve None (não é um bloco
    let..in, cai no formatador genérico de expressão única).
    Devolve (lista_de_passos, tokens_expressao_final).
    """
    profundidade = 0
    pos_let, pos_in = None, None
    for i, (kind, val) in enumerate(tokens):
        if kind in _ABERTURAS:
            profundidade += 1
        elif kind in _FECHAMENTOS:
            profundidade -= 1
        elif profundidade == 0 and kind == "KEYWORD" and val.lower() == "let" and pos_let is None:
            pos_let = i
        elif profundidade == 0 and kind == "KEYWORD" and val.lower() == "in" and pos_let is not None and pos_in is None:
            pos_in = i

    if pos_let is None or pos_in is None:
        return None

    tokens_passos = tokens[pos_let + 1:pos_in]
    tokens_final = tokens[pos_in + 1:]

    passos, atual, profundidade2 = [], [], 0
    for kind, val in tokens_passos:
        if kind in _ABERTURAS:
            profundidade2 += 1
        elif kind in _FECHAMENTOS:
            profundidade2 -= 1
        if kind == "OP" and val == "," and profundidade2 == 0:
            passos.append(atual)
            atual = []
            continue
        atual.append((kind, val))
    if atual:
        passos.append(atual)

    return passos, tokens_final


def _render_passo(tokens_passo: list) -> str:
    """Renderiza um passo 'Nome = Expressão' com indentação de 1 nível."""
    profundidade, pos_igual = 0, None
    for i, (kind, val) in enumerate(tokens_passo):
        if kind in _ABERTURAS:
            profundidade += 1
        elif kind in _FECHAMENTOS:
            profundidade -= 1
        elif profundidade == 0 and kind == "OP" and val == "=" and pos_igual is None:
            pos_igual = i
            break

    if pos_igual is None:
        seq = _parsear_sequencia(tokens_passo)
        return "    " + _render_sequencia(seq, 1)

    nome_texto = _render_sequencia_flat(_parsear_sequencia(tokens_passo[:pos_igual]))
    seq_expr = _parsear_sequencia(tokens_passo[pos_igual + 1:])
    expr_texto = _render_sequencia(seq_expr, 1)
    return f"    {nome_texto} = {expr_texto}"


def formatar_m(texto: str) -> str:
    """
    Formata um código M (Power Query): se detectar um bloco `let ...
    in ...`, coloca cada passo em sua própria linha (indentado),
    quebrando expressões longas por profundidade de parênteses/colchetes/
    chaves; senão, formata como uma expressão única.
    """
    texto = texto.strip()
    if not texto:
        return ""

    tokens = _tokenizar(texto)
    if not tokens:
        return texto

    dividido = _dividir_passos_top_level(tokens)
    if dividido is None:
        seq = _parsear_sequencia(tokens)
        return _render_sequencia(seq, 0)

    passos, tokens_final = dividido
    linhas_passos = [_render_passo(p) for p in passos if p]
    corpo_passos = ",\n".join(linhas_passos)

    seq_final = _parsear_sequencia(tokens_final)
    texto_final = _render_sequencia(seq_final, 1)

    return f"let\n{corpo_passos}\nin\n    {texto_final}"
