"""
generators/qa_engine.py — "Pergunte aos Dados": traduz uma pergunta de
negócio em português para uma medida DAX (reaproveitando o motor de
generators/dax_engine.py) e mostra a resposta calculada de verdade lado a
lado com a medida equivalente — pra ensinar como transformar uma pergunta
em código, não só entregar o número pronto.

Importante: isto NÃO é um LLM. O projeto não tem nenhuma integração com
IA de linguagem natural de verdade (sem chave de API, sem dependência
paga) — é um motor de reconhecimento de padrões, deliberadamente limitado
a um conjunto pequeno e bem testado de perguntas (agregação simples,
filtro por categoria, ranking por dimensão, ticket médio). Quando a
pergunta foge desse conjunto, o motor diz claramente que não entendeu e
sugere um jeito de reformular — nunca "chuta" uma resposta.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

import pandas as pd

from generators.dax_engine import DaxError, avaliar_medida
from generators.relatorios_gerenciais import _colunas_medida

_SINONIMOS_MEDIDA = {
    "venda": ["valor_total", "valor_venda", "vendas"],
    "vendas": ["valor_total", "valor_venda", "vendas"],
    "faturamento": ["valor_total", "faturamento", "receita"],
    "receita": ["receita", "valor_total", "faturamento"],
    "fatura": ["valor_total", "faturamento"],
}

_PALAVRAS_IGNORAR_MEDIDA = {
    "qual", "foi", "o", "a", "de", "da", "do", "em", "no", "na", "para",
    "por", "total", "soma", "media", "média", "quantos", "quantas",
    "maior", "menor", "existem", "tem", "teve", "foram", "com", "e",
}

_FORA_DE_ESCOPO = [
    "previsao", "previsão", "projecao", "projeção", "tendencia", "tendência",
    "futuro", "proximo mes", "próximo mês", "proximo trimestre", "próximo trimestre",
    "vai vender", "vai crescer", "vai cair", "vai aumentar", "vamos vender",
    "sera que", "será que", "por que", "por quê", "porque", "causa de",
    "motivo de", "explique", "explica por",
]

_TEM_INTENCAO_TOTAL = re.compile(r"\btotal\b|\bsoma\b|\bsomatorio\b|\bsomatório\b|\bquanto\b|\bquanta\b")


def _sem_acento(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _norm(texto: str) -> str:
    return _sem_acento(texto).lower().strip()


@dataclass
class RespostaQA:
    entendida: bool
    resposta_texto: str = ""
    medida_dax: str = ""
    valor: float | None = None
    passos: list[str] = field(default_factory=list)
    tabela_resultado: pd.DataFrame | None = None
    sugestoes: list[str] = field(default_factory=list)


def _tabelas_fato(tabelas: dict[str, pd.DataFrame]) -> list[str]:
    return [t for t in tabelas if t.startswith("Fato")]


def _tabelas_dim(tabelas: dict[str, pd.DataFrame]) -> list[str]:
    return [t for t in tabelas if t.startswith("Dim")]


def _medidas_disponiveis(fato_df: pd.DataFrame) -> list[str]:
    return _colunas_medida(fato_df)


def _achar_coluna_medida(pergunta_norm: str, fato_nome: str, tabelas: dict) -> str | None:
    """Acha qual coluna numérica da tabela fato a pergunta está pedindo.
    Primeiro tenta bater o NOME DA COLUNA de verdade — tanto a forma literal
    com underscore (ex.: 'quantidade_kg', comum quando a pessoa copia o nome
    direto do diagrama do modelo) quanto com _ trocado por espaço (ex.:
    'quantidade kg') — a via mais confiável, sem chute. Só recorre a
    sinônimos genéricos (venda/faturamento/receita) se não achar nada."""
    df = tabelas[fato_nome]
    medidas = _medidas_disponiveis(df)

    for col in medidas:
        col_underscore = col.lower()
        col_espaco = _norm(col.replace("_", " "))
        if col_underscore in pergunta_norm or (col_espaco and col_espaco in pergunta_norm):
            return col

    for palavra, candidatos in _SINONIMOS_MEDIDA.items():
        if palavra in pergunta_norm:
            for candidato in candidatos:
                for col in medidas:
                    if candidato in col.lower():
                        return col

    # Fallback final: só quando a pergunta claramente não menciona nenhuma
    # medida específica (ex.: "quantos registros existem"), não tenta
    # adivinhar uma coluna de valor — quem chama trata esse caso à parte.
    return None


_PERIODOS_TEMPORAIS = [
    (["trimestre"], "Trimestre"),
    (["semestre"], "Semestre"),
    (["ano"], "Ano"),
    (["mes", "mês", "mensal"], "MesAno"),
]


def _achar_periodo_temporal(pergunta_norm: str, cal_df: pd.DataFrame) -> str | None:
    for palavras, coluna in _PERIODOS_TEMPORAIS:
        if coluna in cal_df.columns and any(p in pergunta_norm for p in palavras):
            return coluna
    return None


def _tabela_calendario(tabelas: dict) -> str | None:
    return next((t for t in tabelas if t.startswith("dCal")), None)


def _responder_ranking_temporal(pergunta_norm: str, fato_nome: str, cal_nome: str, periodo_col: str,
                                 tabelas: dict, ascendente: bool) -> RespostaQA:
    fato_df = tabelas[fato_nome]
    cal_df = tabelas[cal_nome]

    date_cols = [c for c in fato_df.columns if "data" in c.lower()]
    if not date_cols:
        return RespostaQA(
            entendida=False,
            sugestoes=[f"Não encontrei uma coluna de data em {fato_nome} para agrupar por período."],
        )
    date_col = date_cols[0]
    medida = _achar_coluna_medida(pergunta_norm, fato_nome, tabelas)
    contando_linhas = medida is None
    eh_media = bool(re.search(r"\bmedi[ao]\b|\bmédia\b", pergunta_norm))

    colunas_fato = [date_col] + ([medida] if medida else [])
    fato_tmp = fato_df[colunas_fato].copy()
    fato_tmp["_data_norm"] = pd.to_datetime(fato_tmp[date_col], errors="coerce").dt.date
    cal_tmp = cal_df[["Data", periodo_col]].copy()
    cal_tmp["_data_norm"] = pd.to_datetime(cal_tmp["Data"], errors="coerce").dt.date

    merged = fato_tmp.merge(cal_tmp[["_data_norm", periodo_col]], on="_data_norm", how="left")
    merged = merged.dropna(subset=[periodo_col])

    if contando_linhas:
        agrupado = merged.groupby(periodo_col).size().reset_index(name="valor")
        funcao_nome = "COUNTROWS"
    elif eh_media:
        agrupado = merged.groupby(periodo_col)[medida].mean().reset_index(name="valor")
        funcao_nome = "AVERAGE"
    else:
        agrupado = merged.groupby(periodo_col)[medida].sum().reset_index(name="valor")
        funcao_nome = "SUM"

    agrupado = agrupado.sort_values("valor", ascending=ascendente)
    if agrupado.empty:
        return RespostaQA(entendida=False, sugestoes=["Não há dados suficientes para calcular esse ranking."])

    linha_top = agrupado.iloc[0]
    medida_label = medida.replace("_", " ") if medida else None
    superlativo = "menor" if ascendente else "maior"
    if contando_linhas:
        rotulo_agregacao = f"{superlativo} número de registros"
    elif eh_media:
        rotulo_agregacao = f"{superlativo} média de {medida_label}"
    else:
        rotulo_agregacao = f"{superlativo} total de {medida_label}"
    valor_periodo = linha_top[periodo_col]
    if isinstance(valor_periodo, float) and valor_periodo.is_integer():
        valor_periodo = int(valor_periodo)
    expr = (
        f'CALCULATE({funcao_nome}({fato_nome}{f"[{medida}]" if medida else ""}), '
        f'{cal_nome}[{periodo_col}]="{valor_periodo}")'
    )

    return RespostaQA(
        entendida=True,
        resposta_texto=(
            f"**{valor_periodo}** foi o período com {rotulo_agregacao} "
            f"(**{linha_top['valor']:,.2f}**)."
        ),
        medida_dax=expr,
        valor=float(linha_top["valor"]),
        passos=[
            f"Agrupou {fato_nome} por {cal_nome}[{periodo_col}] (via {fato_nome}[{date_col}] = {cal_nome}[Data])",
            f"Calculou {funcao_nome} de {medida_label or 'registros'} para cada período",
            f"Ordenou {'crescente' if ascendente else 'decrescente'} e pegou o primeiro colocado",
        ],
        tabela_resultado=agrupado.head(15),
    )


def _palavras(pergunta_norm: str) -> list[str]:
    """Tokeniza a pergunta em palavras limpas, sem pontuação grudada (ex.:
    'abelha?' -> 'abelha'). Usar isto em vez de .split() sempre que for
    comparar palavra a palavra — pontuação grudada faz comparações exatas
    (p == sufixo) falharem silenciosamente."""
    return re.findall(r"[a-z0-9_]+", pergunta_norm)


def _achar_dimensao(pergunta_norm: str, tabelas: dict) -> str | None:
    """Acha a tabela Dim que a pergunta está citando — tanto pelo nome da
    própria tabela (ex.: 'vendedor' -> DimVendedor) quanto por uma coluna
    descritiva dentro dela (ex.: 'espécie de abelha' -> DimColmeia, via a
    coluna especie_abelha, mesmo com uma preposição no meio das palavras)."""
    palavras_pergunta = set(_palavras(pergunta_norm))
    for dim_nome in _tabelas_dim(tabelas):
        sufixo = dim_nome[3:].lower()  # remove "Dim"
        if sufixo in pergunta_norm or any(
            p == sufixo or (len(p) > 3 and p in sufixo) for p in palavras_pergunta
        ):
            return dim_nome

        dim_df = tabelas[dim_nome]
        for col in dim_df.columns:
            cl = col.lower()
            if cl.startswith(("id_", "sk_")):
                continue
            palavras_coluna = [p for p in cl.split("_") if len(p) > 3]
            if palavras_coluna and all(_norm(p) in palavras_pergunta for p in palavras_coluna):
                return dim_nome
    return None


def _achar_filtro_categorico(pergunta_norm: str, tabelas: dict) -> tuple[str, str, str] | None:
    """Procura, em TODAS as colunas categóricas de TODAS as tabelas, um valor
    distinto que apareça como substring da pergunta (ex.: 'sao paulo' na
    pergunta bate com o valor 'São Paulo' de DimFilial[cidade]).
    Retorna (tabela, coluna, valor_original) do primeiro achado, ou None."""
    melhor: tuple[str, str, str] | None = None
    melhor_tamanho = 0
    for nome_tabela, df in tabelas.items():
        for col in df.columns:
            if not pd.api.types.is_string_dtype(df[col]):
                continue
            cl = col.lower()
            if any(k in cl for k in ["nome", "email", "cpf", "cnpj", "endereco",
                                       "descricao", "url", "telefone", "cep", "senha"]):
                continue
            try:
                valores = df[col].dropna().unique()
            except Exception:
                continue
            for valor in valores:
                valor_norm = _norm(str(valor))
                if len(valor_norm) >= 3 and valor_norm in pergunta_norm:
                    if len(valor_norm) > melhor_tamanho:
                        melhor = (nome_tabela, col, str(valor))
                        melhor_tamanho = len(valor_norm)
    return melhor


def _exemplos_padrao(fato_nome: str, medida: str | None) -> list[str]:
    m = medida or "valor_total"
    return [
        f"Qual foi o total de {m.replace('_', ' ')}?",
        f"Qual foi a média de {m.replace('_', ' ')}?",
        f"Quantos registros existem em {fato_nome}?",
    ]


def responder_pergunta(pergunta: str, tabelas: dict[str, pd.DataFrame]) -> RespostaQA:
    fato_tables = _tabelas_fato(tabelas)
    if not fato_tables:
        return RespostaQA(entendida=False, sugestoes=["Este setor não tem uma tabela Fato para consultar."])
    fato_nome = fato_tables[0]  # setores com 1 fato (a grande maioria) — o comum.
    fato_df = tabelas[fato_nome]

    pergunta_norm = _norm(pergunta)
    if not pergunta_norm:
        return RespostaQA(entendida=False, sugestoes=_exemplos_padrao(fato_nome, None))

    if any(p in pergunta_norm for p in _FORA_DE_ESCOPO):
        return RespostaQA(
            entendida=False,
            sugestoes=[
                "Essa pergunta pede previsão ou explicação de causa — isso está fora do que este "
                "motor consegue fazer (ele só calcula agregações de verdade sobre os dados já "
                "existentes, não prevê o futuro nem explica o porquê de algo).",
                "Para explorar relações de causa e efeito, veja a aba 🧬 Dados Causais.",
            ] + _exemplos_padrao(fato_nome, None),
        )

    # 1) "Quantos registros/linhas/vendas/pedidos existem" (contagem simples, sem medida)
    if re.search(r"\bquant[oa]s?\b", pergunta_norm) and not re.search(r"\bquant[oa]s?\b.*\b(vendedor|produto|cliente|filial|categoria)\b", pergunta_norm):
        filtro = _achar_filtro_categorico(pergunta_norm, tabelas)
        if filtro:
            ftabela, fcoluna, fvalor = filtro
            expr = f'CALCULATE(COUNTROWS({fato_nome}), {ftabela}[{fcoluna}]="{fvalor}")'
        else:
            expr = f"COUNTROWS({fato_nome})"
        try:
            valor, passos, _ = avaliar_medida(expr, tabelas)
        except DaxError as e:
            return RespostaQA(entendida=False, sugestoes=[str(e)] + _exemplos_padrao(fato_nome, None))
        return RespostaQA(
            entendida=True,
            resposta_texto=f"**{valor:,.0f}** registro(s).",
            medida_dax=expr,
            valor=valor,
            passos=passos,
        )

    # 2) Ranking por período de tempo: "qual mês/ano teve o maior/menor <medida>"
    cal_nome = _tabela_calendario(tabelas)
    eh_maior = bool(re.search(r"\bmai(o|s)r\b|\bmais\b|\btop\b", pergunta_norm))
    eh_menor = bool(re.search(r"\bmeno?r\b|\bpior\b|\bmenos\b", pergunta_norm))
    periodo_col = _achar_periodo_temporal(pergunta_norm, tabelas[cal_nome]) if cal_nome else None
    dim_nome = _achar_dimensao(pergunta_norm, tabelas)

    if (periodo_col or dim_nome) and (eh_maior or eh_menor):
        # Se a pergunta claramente pede uma medida (total/soma/média) mas não achamos
        # nenhuma coluna correspondente, recusa em vez de silenciosamente contar
        # registros — evita responder "quantidade de registros" quando a pessoa
        # queria "total de valor total" e essa coluna nem existe neste setor.
        tem_intencao_medida = bool(_TEM_INTENCAO_TOTAL.search(pergunta_norm) or re.search(r"\bmedi[ao]\b|\bmédia\b", pergunta_norm))
        medida_tentativa = _achar_coluna_medida(pergunta_norm, fato_nome, tabelas)
        if tem_intencao_medida and medida_tentativa is None:
            return RespostaQA(
                entendida=False,
                sugestoes=[
                    "Encontrei a comparação (maior/menor) e a dimensão, mas não achei a medida "
                    "que você mencionou neste setor.",
                    f"Medidas disponíveis: {', '.join(_medidas_disponiveis(fato_df))}",
                ],
            )
        if periodo_col:
            return _responder_ranking_temporal(pergunta_norm, fato_nome, cal_nome, periodo_col, tabelas, ascendente=eh_menor)
        return _responder_ranking(pergunta_norm, fato_nome, dim_nome, tabelas, ascendente=eh_menor)

    # 4) Ticket médio (caso especial reconhecido por nome, não por coluna)
    if "ticket medio" in pergunta_norm or "ticket médio" in pergunta_norm.replace("é", "e"):
        medida = _achar_coluna_medida(pergunta_norm, fato_nome, tabelas) or _medida_principal(fato_df)
        if medida is None:
            return RespostaQA(entendida=False, sugestoes=_exemplos_padrao(fato_nome, None))
        expr = f"DIVIDE(SUM({fato_nome}[{medida}]), COUNTROWS({fato_nome}))"
        try:
            valor, passos, _ = avaliar_medida(expr, tabelas)
        except DaxError as e:
            return RespostaQA(entendida=False, sugestoes=[str(e)])
        return RespostaQA(
            entendida=True,
            resposta_texto=f"O ticket médio foi de **{valor:,.2f}**.",
            medida_dax=expr,
            valor=valor,
            passos=passos,
        )

    # 4) Agregação simples ou filtrada: total / soma / média / maior / menor de <medida>
    medida = _achar_coluna_medida(pergunta_norm, fato_nome, tabelas)
    if medida is None:
        return RespostaQA(
            entendida=False,
            sugestoes=[
                "Não encontrei nenhuma medida numérica correspondente na sua pergunta.",
                f"Medidas disponíveis neste setor: {', '.join(_medidas_disponiveis(fato_df))}",
            ] + _exemplos_padrao(fato_nome, None),
        )

    if re.search(r"\bmedi[ao]\b|\bmédia\b", pergunta_norm):
        funcao = "AVERAGE"
    elif eh_maior:
        funcao = "MAX"
    elif eh_menor:
        funcao = "MIN"
    elif _TEM_INTENCAO_TOTAL.search(pergunta_norm):
        funcao = "SUM"
    else:
        # Achou uma medida na frase, mas nenhuma intenção clara de agregação
        # (total/soma/média/maior/menor) — não assume SUM só porque bateu o
        # nome de uma coluna. Melhor recusar do que arriscar responder uma
        # pergunta que na verdade pedia outra coisa (previsão, opinião etc.).
        return RespostaQA(
            entendida=False,
            sugestoes=[
                "Encontrei a medida, mas não identifiquei claramente o que fazer com ela "
                "(somar, tirar a média, achar o maior/menor valor?).",
            ] + _exemplos_padrao(fato_nome, medida),
        )

    filtro = _achar_filtro_categorico(pergunta_norm, tabelas)
    expr_interna = f"{funcao}({fato_nome}[{medida}])"
    if filtro:
        ftabela, fcoluna, fvalor = filtro
        expr = f'CALCULATE({expr_interna}, {ftabela}[{fcoluna}]="{fvalor}")'
    else:
        expr = expr_interna

    try:
        valor, passos, _ = avaliar_medida(expr, tabelas)
    except DaxError as e:
        return RespostaQA(entendida=False, sugestoes=[str(e)])

    rotulo = {"SUM": ("o", "total"), "AVERAGE": ("a", "média"), "MAX": ("o", "maior valor"), "MIN": ("o", "menor valor")}[funcao]
    artigo, rotulo_texto = rotulo
    return RespostaQA(
        entendida=True,
        resposta_texto=f"{artigo.capitalize()} {rotulo_texto} de {medida.replace('_', ' ')} foi **{valor:,.2f}**.",
        medida_dax=expr,
        valor=valor,
        passos=passos,
    )


def _medida_principal(fato_df: pd.DataFrame) -> str | None:
    medidas = _medidas_disponiveis(fato_df)
    return medidas[0] if medidas else None


def _responder_ranking(pergunta_norm: str, fato_nome: str, dim_nome: str,
                        tabelas: dict, ascendente: bool) -> RespostaQA:
    from generators.dax_engine import _detectar_fk  # reaproveita a mesma heurística de FK

    fk = _detectar_fk(fato_nome, dim_nome, tabelas)
    if fk is None:
        return RespostaQA(
            entendida=False,
            sugestoes=[f"Não encontrei um relacionamento entre {fato_nome} e {dim_nome}."],
        )
    fk_col, pk_dim = fk
    fato_df = tabelas[fato_nome]
    dim_df = tabelas[dim_nome]

    medida = _achar_coluna_medida(pergunta_norm, fato_nome, tabelas)
    contando_linhas = medida is None
    eh_media = bool(re.search(r"\bmedi[ao]\b|\bmédia\b", pergunta_norm))

    # Coluna descritiva da dimensão: prioriza a coluna que a pergunta
    # realmente mencionou (ex.: 'espécie de abelha' -> especie_abelha), e só
    # cai no fallback genérico (primeira coluna de texto) se nenhuma bater.
    palavras_pergunta = set(_palavras(pergunta_norm))
    col_desc = None
    for c in dim_df.columns:
        cl = c.lower()
        if cl.startswith(("id_", "sk_")) or cl in ("email", "cpf", "cnpj", "endereco"):
            continue
        palavras_coluna = [p for p in cl.split("_") if len(p) > 3]
        if palavras_coluna and all(_norm(p) in palavras_pergunta for p in palavras_coluna):
            col_desc = c
            break
    if col_desc is None:
        col_desc = next(
            (c for c in dim_df.columns if pd.api.types.is_string_dtype(dim_df[c])
             and c.lower() not in ("email", "cpf", "cnpj", "endereco")),
            pk_dim,
        )

    merged = fato_df[[fk_col] + ([medida] if medida else [])].merge(
        dim_df[[pk_dim, col_desc]], left_on=fk_col, right_on=pk_dim, how="left"
    )
    if contando_linhas:
        agrupado = merged.groupby(col_desc).size().reset_index(name="valor")
        funcao_nome = "COUNTROWS"
    elif eh_media:
        agrupado = merged.groupby(col_desc)[medida].mean().reset_index(name="valor")
        funcao_nome = "AVERAGE"
    else:
        agrupado = merged.groupby(col_desc)[medida].sum().reset_index(name="valor")
        funcao_nome = "SUM"

    agrupado = agrupado.sort_values("valor", ascending=ascendente)
    if agrupado.empty:
        return RespostaQA(entendida=False, sugestoes=["Não há dados suficientes para calcular esse ranking."])

    linha_top = agrupado.iloc[0]
    medida_label = medida.replace("_", " ") if medida else None
    superlativo = "menor" if ascendente else "maior"
    if contando_linhas:
        artigo, rotulo_agregacao = "o", f"{superlativo} número de registros"
    elif eh_media:
        artigo, rotulo_agregacao = "a", f"{superlativo} média de {medida_label}"
    else:
        artigo, rotulo_agregacao = "o", f"{superlativo} total de {medida_label}"
    expr = (
        f'CALCULATE({funcao_nome}({fato_nome}'
        f'{f"[{medida}]" if medida else ""}), {dim_nome}[{col_desc}]="{linha_top[col_desc]}")'
    )

    return RespostaQA(
        entendida=True,
        resposta_texto=(
            f"**{linha_top[col_desc]}** foi quem teve {artigo} {rotulo_agregacao} "
            f"(**{linha_top['valor']:,.2f}**)."
        ),
        medida_dax=expr,
        valor=float(linha_top["valor"]),
        passos=[
            f"Agrupou {fato_nome} por {dim_nome}[{col_desc}] (via {fato_nome}[{fk_col}] = {dim_nome}[{pk_dim}])",
            f"Calculou {funcao_nome} de {medida_label or 'registros'} para cada {dim_nome}[{col_desc}]",
            f"Ordenou {'crescente' if ascendente else 'decrescente'} e pegou o primeiro colocado",
        ],
        tabela_resultado=agrupado.head(10),
    )
