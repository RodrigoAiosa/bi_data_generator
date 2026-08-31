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
    Primeiro tenta bater o NOME DA COLUNA de verdade (com _ trocado por
    espaço) na pergunta — a via mais confiável, sem chute. Só recorre a
    sinônimos genéricos (venda/faturamento/receita) se não achar nada."""
    df = tabelas[fato_nome]
    medidas = _medidas_disponiveis(df)

    for col in medidas:
        col_norm = _norm(col.replace("_", " "))
        if col_norm and col_norm in pergunta_norm:
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


def _achar_dimensao(pergunta_norm: str, tabelas: dict) -> str | None:
    """Acha a tabela Dim que a pergunta está citando (ex.: 'vendedor' -> DimVendedor)."""
    for dim_nome in _tabelas_dim(tabelas):
        sufixo = dim_nome[3:].lower()  # remove "Dim"
        if sufixo in pergunta_norm or any(
            p == sufixo or (len(p) > 3 and p in sufixo) for p in pergunta_norm.split()
        ):
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

    # 2) Ranking por dimensão: "qual <dimensão> teve o maior/menor <medida>"
    dim_nome = _achar_dimensao(pergunta_norm, tabelas)
    eh_maior = bool(re.search(r"\bmai(o|s)r\b|\bmais\b|\btop\b", pergunta_norm))
    eh_menor = bool(re.search(r"\bmeno?r\b|\bpior\b|\bmenos\b", pergunta_norm))
    if dim_nome and (eh_maior or eh_menor):
        return _responder_ranking(pergunta_norm, fato_nome, dim_nome, tabelas, ascendente=eh_menor)

    # 3) Ticket médio (caso especial reconhecido por nome, não por coluna)
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

    # Coluna descritiva da dimensão (nome-like), pra mostrar em vez do ID puro
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
    else:
        agrupado = merged.groupby(col_desc)[medida].sum().reset_index(name="valor")

    agrupado = agrupado.sort_values("valor", ascending=ascendente)
    if agrupado.empty:
        return RespostaQA(entendida=False, sugestoes=["Não há dados suficientes para calcular esse ranking."])

    linha_top = agrupado.iloc[0]
    medida_label = medida.replace("_", " ") if medida else "quantidade de registros"
    superlativo = "menor" if ascendente else "maior"
    expr = (
        f'CALCULATE({"COUNTROWS" if contando_linhas else "SUM"}({fato_nome}'
        f'{f"[{medida}]" if medida else ""}), {dim_nome}[{col_desc}]="{linha_top[col_desc]}")'
    )

    return RespostaQA(
        entendida=True,
        resposta_texto=(
            f"**{linha_top[col_desc]}** foi quem teve o {superlativo} {medida_label} "
            f"(**{linha_top['valor']:,.2f}**)."
        ),
        medida_dax=expr,
        valor=float(linha_top["valor"]),
        passos=[
            f"Agrupou {fato_nome} por {dim_nome}[{col_desc}] (via {fato_nome}[{fk_col}] = {dim_nome}[{pk_dim}])",
            f"Somou/contou {medida_label} para cada {dim_nome}[{col_desc}]",
            f"Ordenou {'crescente' if ascendente else 'decrescente'} e pegou o primeiro colocado",
        ],
        tabela_resultado=agrupado.head(10),
    )
