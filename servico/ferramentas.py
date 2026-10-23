"""
servico/ferramentas.py: back-end das ferramentas (todas as abas além do gerador),
sem Streamlit. Cada ação recebe um dict JSON e devolve um dict JSON.

As ferramentas que dependem da base gerada (SCD, Causais, Sandbox, Pergunte aos
Dados, PL-300 contextual) recebem `base` = {setor, linhas, inicio, fim,
mes_fiscal, seed, anomalia, deriva, idioma} e REGENERAM a mesma base (a geração é
reproduzível por seed), então o servidor não guarda estado entre chamadas.
"""
from __future__ import annotations

import base64
import io
import json
import random
from datetime import date

import pandas as pd

LIMITE_ARQUIVO = 2_000_000  # bytes de texto por download embutido na resposta
LIMITE_UPLOAD = 3_000_000   # bytes (já decodificados) por envio de planilhas


class ErroUsuario(ValueError):
    """Erro com mensagem apropriada para mostrar ao usuário."""


# ── utilitários ──────────────────────────────────────────────────────────────

def df_json(df: pd.DataFrame, n: int = 100) -> dict:
    """DataFrame → {colunas, linhas (n primeiras, tipos JSON), total}."""
    head = df.head(n)
    dados = json.loads(head.to_json(orient="split", date_format="iso", date_unit="s", force_ascii=False))
    return {"colunas": [str(c) for c in dados["columns"]], "linhas": dados["data"], "total": int(len(df))}


def _csv(df: pd.DataFrame) -> str:
    return df.to_csv(index=False)


def _arquivos(**arqs: str) -> dict:
    """Downloads embutidos (texto) — descarta o que passar do limite."""
    return {nome: txt for nome, txt in arqs.items() if len(txt.encode("utf-8")) <= LIMITE_ARQUIVO}


def _base(p: dict, *, bruta: bool = False) -> tuple[dict, str]:
    from servico.pacote import gerar_tabelas
    b = p.get("base")
    if not isinstance(b, dict):
        raise ErroUsuario("Gere uma base primeiro na aba “Gerador de Setores”.")
    try:
        tabelas, _ = gerar_tabelas(
            str(b.get("setor", "")), int(b.get("linhas", 0)),
            date.fromisoformat(b["inicio"]), date.fromisoformat(b["fim"]),
            mes_fiscal=int(b.get("mes_fiscal", 1)),
            anomalia=False if bruta else bool(b.get("anomalia")),
            drift=False if bruta else bool(b.get("deriva")),
            lang=str(b.get("idioma", "pt")), seed=int(b["seed"]) if b.get("seed") is not None else None)
    except (KeyError, TypeError) as e:
        raise ErroUsuario("Parâmetros da base inválidos.") from e
    return tabelas, str(b.get("setor", ""))


# ── formatadores / auditor ───────────────────────────────────────────────────

def formatar_dax(p: dict) -> dict:
    from generators.dax_formatter import formatar_dax as f
    texto = str(p.get("texto", "")).strip()
    if not texto:
        raise ErroUsuario("Cole uma expressão DAX antes de formatar.")
    if len(texto) > 100_000:
        raise ErroUsuario("Texto grande demais (máx. 100.000 caracteres).")
    try:
        return {"resultado": f(texto)}
    except Exception as e:
        raise ErroUsuario(f"Não foi possível formatar essa expressão. Detalhe: {e}") from e


def formatar_m(p: dict) -> dict:
    from generators.m_formatter import formatar_m as f
    texto = str(p.get("texto", "")).strip()
    if not texto:
        raise ErroUsuario("Cole um código M antes de formatar.")
    if len(texto) > 100_000:
        raise ErroUsuario("Texto grande demais (máx. 100.000 caracteres).")
    try:
        return {"resultado": f(texto)}
    except Exception as e:
        raise ErroUsuario(f"Não foi possível formatar esse código M. Detalhe: {e}") from e


def auditar(p: dict) -> dict:
    from generators.auditor_modelo import auditar_modelo
    texto = str(p.get("texto", "")).strip()
    if not texto:
        raise ErroUsuario("Cole ou envie o TMDL do seu modelo antes de auditar.")
    if len(texto) > 1_500_000:
        raise ErroUsuario("TMDL grande demais (máx. ~1,5 MB de texto).")
    try:
        return {"relatorio": auditar_modelo(texto)}
    except Exception as e:
        raise ErroUsuario(f"Não foi possível analisar esse TMDL. Detalhe: {e}") from e


# ── carrossel ────────────────────────────────────────────────────────────────

def carrossel_paginas(p: dict) -> dict:
    from generators.carrossel_pbi import ArquivoInvalidoError, extrair_paginas_do_zip
    try:
        dados = base64.b64decode(p.get("zip_base64", ""), validate=False)
        paginas = extrair_paginas_do_zip(dados)
    except ArquivoInvalidoError as e:
        raise ErroUsuario(str(e)) from e
    except Exception as e:
        raise ErroUsuario("Não consegui ler esse arquivo como .pbix ou projeto .pbip.") from e
    return {"paginas": [[n, i] for n, i in paginas]}


def carrossel_html(p: dict) -> dict:
    from generators.carrossel_pbi import extrair_report_id_ctid, gerar_html_carrossel, montar_url_embed
    paginas = [(str(n), str(i)) for n, i in p.get("paginas", [])]
    if not paginas:
        raise ErroUsuario("Marque pelo menos uma página para continuar.")
    ids = extrair_report_id_ctid(str(p.get("link", "")))
    if ids is None:
        raise ErroUsuario(
            "Não encontrei o reportId e o ctid nesse texto. Confirme que colou o link (ou o <iframe>) obtido em "
            "Arquivo → Inserir relatório → Site ou portal, no Power BI Service.")
    rid, ctid = ids
    intervalo = max(1, min(3600, int(p.get("intervalo", 10))))
    com_url = [(n, i, montar_url_embed(rid, ctid, i, bool(p.get("chromeless", True)), bool(p.get("auto_auth", True))))
               for n, i in paginas]
    return {"html": gerar_html_carrossel(com_url, intervalo_seg=intervalo),
            "urls": [[n, u] for n, _, u in com_url], "intervalo": intervalo}


# ── PL-300 ───────────────────────────────────────────────────────────────────

def pl300(p: dict) -> dict:
    from servico.pl300 import DOMINIOS, montar_banco_perguntas
    n = int(p.get("n", 10))
    if n not in (5, 10, 15, 20):
        raise ErroUsuario("Quantidade de perguntas inválida.")
    ctx = None
    if isinstance(p.get("base"), dict):
        tabelas, setor = _base(p)
        ctx = {"nome": setor, "tabelas": tabelas}
    banco = montar_banco_perguntas(ctx)
    random.shuffle(banco)
    return {"perguntas": banco[:n], "dominios": DOMINIOS, "contextual": ctx is not None}


# ── SCD ──────────────────────────────────────────────────────────────────────

def scd_info(p: dict) -> dict:
    tabelas, _ = _base(p)
    return {"dimensoes": [{"nome": k, "linhas": int(len(v))} for k, v in tabelas.items() if k.startswith("Dim")]}


def scd(p: dict) -> dict:
    from generators.scd_simulador import ScdError, gerar_cenario_scd
    tabelas, _ = _base(p)
    dim = str(p.get("dim", ""))
    if dim not in tabelas or not dim.startswith("Dim"):
        raise ErroUsuario("Dimensão inválida.")
    try:
        r = gerar_cenario_scd(tabelas, dim, max(1, int(p.get("n_mudancas", 10))))
    except ScdError as e:
        raise ErroUsuario(str(e)) from e
    return {
        "dim": dim, "pk": r["coluna_pk"], "alteradas": int(len(r["gabarito"])), "total": int(len(r["snapshot_t0"])),
        "t0": df_json(r["snapshot_t0"], 200), "t1": df_json(r["snapshot_t1"], 200), "gabarito": df_json(r["gabarito"], 200),
        "tipo1": df_json(r["scd_tipo1"], 200), "tipo2": df_json(r["scd_tipo2"], 200), "tipo3": df_json(r["scd_tipo3"], 200),
        "arquivos": _arquivos(**{
            "scd_t0_antes.csv": _csv(r["snapshot_t0"]), "scd_t1_depois.csv": _csv(r["snapshot_t1"]),
            "scd_gabarito.csv": _csv(r["gabarito"]), "scd_tipo2_resultado.csv": _csv(r["scd_tipo2"])}),
    }


# ── Dados causais ────────────────────────────────────────────────────────────

def causal_info(p: dict) -> dict:
    from servico.causal import _colunas_numericas_validas, _detectar_coluna_data
    tabelas, _ = _base(p)
    fatos = {}
    for k, df in tabelas.items():
        if not k.startswith("Fato"):
            continue
        fatos[k] = {"data": _detectar_coluna_data(df), "colunas": [str(c) for c in _colunas_numericas_validas(df)]}
    return {"fatos": fatos}


def causal(p: dict) -> dict:
    from servico.causal import gerar_cenario_causal_do_setor, montar_gabarito_causal_txt, _detectar_coluna_data, _colunas_numericas_validas
    tabelas, setor = _base(p)
    fato = str(p.get("fato", ""))
    if fato not in tabelas or not fato.startswith("Fato"):
        raise ErroUsuario("Tabela fato inválida.")
    df = tabelas[fato]
    col_data = _detectar_coluna_data(df)
    validas = _colunas_numericas_validas(df)
    causa, efeito = str(p.get("causa", "")), str(p.get("efeito", ""))
    if not col_data:
        raise ErroUsuario("A tabela não tem coluna de data para montar uma série temporal.")
    if causa not in validas or efeito not in validas or causa == efeito:
        raise ErroUsuario("Escolha duas colunas numéricas diferentes para causa e efeito.")
    direcao = -1 if int(p.get("direcao", 1)) < 0 else 1
    try:
        d, gab = gerar_cenario_causal_do_setor(
            df, col_data, causa, efeito, direcao, bool(p.get("confundidor", True)),
            float(min(60, max(5, p.get("efeito_pct", 20)))), int(min(8, max(0, p.get("defasagem", 2)))),
            float(min(50, max(0, p.get("ruido_pct", 15)))), setor, fato)
    except ValueError as e:
        raise ErroUsuario(str(e)) from e
    cols = [c for c in d.columns if c != "data" and "Sazonalidade" not in c]
    return {
        "serie": {"x": [str(x)[:10] for x in d["data"]], "series": {c: [None if pd.isna(v) else float(v) for v in d[c]] for c in cols}},
        "amostra": df_json(d, 10), "gabarito": {k: str(v) for k, v in gab.items()},
        "arquivos": _arquivos(**{"dados_causais.csv": _csv(d), "gabarito_causal.txt": montar_gabarito_causal_txt(gab)}),
    }


# ── Sandbox DAX ──────────────────────────────────────────────────────────────

def _relacoes(tabelas: dict) -> list[dict]:
    from generators.relacionamentos import detectar_fk
    fatos = [t for t in tabelas if t.startswith("Fato")]
    dims = [t for t in tabelas if t.startswith("Dim")]
    cals = [t for t in tabelas if t.startswith("dCal")]
    outras = [t for t in tabelas if t not in fatos + dims + cals]
    rel: list[dict] = []
    for f in fatos:
        rel += [{"de": f, "para": d, "tipo": "direta"} for d in dims if detectar_fk(f, d, tabelas)]
        if any("data" in c.lower() for c in tabelas[f].columns):
            rel += [{"de": f, "para": c, "tipo": "data"} for c in cals]
    for o in outras:
        rel += [{"de": o, "para": d, "tipo": "direta"} for d in dims if detectar_fk(o, d, tabelas)]
    for a in dims:
        rel += [{"de": a, "para": b, "tipo": "indireta"} for b in dims if a != b and detectar_fk(a, b, tabelas)]
    return rel


def sandbox_modelo(p: dict) -> dict:
    from servico.sandbox import _achar_medida_e_exemplos
    tabelas, _ = _base(p, bruta=True)
    fato, medida, exemplos = _achar_medida_e_exemplos(tabelas)
    tipo = lambda t: "fato" if t.startswith("Fato") else "dim" if t.startswith("Dim") else "calendario" if t.startswith("dCal") else "outra"  # noqa: E731
    return {
        "tabelas": [{"nome": k, "tipo": tipo(k), "linhas": int(len(v)), "colunas": [str(c) for c in v.columns], "pk": str(v.columns[0])}
                    for k, v in tabelas.items()],
        "relacoes": _relacoes(tabelas), "fato": fato, "medida": medida, "exemplos": exemplos,
    }


def sandbox_exec(p: dict) -> dict:
    from generators.dax_engine import DaxError, avaliar_medida
    expr = str(p.get("expressao", "")).strip()
    if not expr:
        raise ErroUsuario("Escreva uma medida DAX antes de executar.")
    if len(expr) > 20_000:
        raise ErroUsuario("Expressão grande demais.")
    tabelas, _ = _base(p, bruta=True)
    try:
        valor, passos, nome = avaliar_medida(expr, tabelas)
    except DaxError as e:
        raise ErroUsuario(f"❌ {e}") from e
    except Exception as e:
        raise ErroUsuario("Não consegui avaliar essa expressão. Confira a sintaxe (ex.: SUM(Tabela[Coluna]), "
                          "DIVIDE(a, b), CALCULATE(expr, Tabela[Coluna]=\"valor\")). "
                          f"Detalhe técnico: {type(e).__name__}: {e}") from e
    return {"nome": nome, "valor": float(valor), "passos": [str(x) for x in passos]}


# ── Pergunte aos Dados ───────────────────────────────────────────────────────

def qa_catalogo(p: dict) -> dict:
    from generators.qa_perguntas import gerar_catalogo
    tabelas, _ = _base(p, bruta=True)
    return {"perguntas": [{"categoria": q.categoria, "texto": q.texto} for q in gerar_catalogo(tabelas)]}


def qa_perguntar(p: dict) -> dict:
    from generators.qa_engine import responder_pergunta
    pergunta = str(p.get("pergunta", "")).strip()
    if not pergunta:
        raise ErroUsuario("Escolha uma pergunta na lista antes de clicar em Perguntar.")
    tabelas, _ = _base(p, bruta=True)
    r = responder_pergunta(pergunta, tabelas)
    if not r.entendida:
        return {"entendida": False, "sugestoes": list(r.sugestoes or [])}
    return {"entendida": True, "resposta": r.resposta_texto, "aviso": r.aviso, "dax": r.medida_dax,
            "passos": list(r.passos or []),
            "tabela": df_json(r.tabela_resultado, 200) if r.tabela_resultado is not None else None}


# ── Automatizar BI (planilhas do usuário) ────────────────────────────────────

class _Arquivo(io.BytesIO):
    def __init__(self, nome: str, dados: bytes):
        super().__init__(dados)
        self.name = nome


def _carregar_planilhas(p: dict):
    from servico import automatizar as a
    itens = p.get("arquivos") or []
    if not itens or len(itens) > 10:
        raise ErroUsuario("Envie de 1 a 10 planilhas (.csv ou .xlsx).")
    arquivos, total = [], 0
    for it in itens:
        nome = str(it.get("nome", "arquivo"))
        if not nome.lower().endswith((".csv", ".xlsx")):
            raise ErroUsuario(f"Formato não suportado: {nome}. Envie .csv ou .xlsx.")
        dados = base64.b64decode(it.get("base64", ""))
        total += len(dados)
        arquivos.append(_Arquivo(nome, dados))
    if total > LIMITE_UPLOAD:
        raise ErroUsuario("As planilhas passam de 3 MB no total. Envie arquivos menores (ou uma amostra das linhas).")
    try:
        tabelas, avisos = a._ler_arquivos(arquivos)
    except Exception as e:
        raise ErroUsuario("Não foi possível ler um dos arquivos enviados. Verifique se ele não está corrompido, vazio, "
                          "protegido por senha ou com extensão diferente do conteúdo real. "
                          f"Detalhe: {type(e).__name__}: {e}") from e
    if not tabelas:
        raise ErroUsuario("Nenhuma tabela foi identificada nos arquivos enviados.")
    tabelas, avisos_cons = a._consolidar_planilhas_identicas(tabelas)
    return a, tabelas, avisos, avisos_cons


def automatizar_ler(p: dict) -> dict:
    a, tabelas, avisos, avisos_cons = _carregar_planilhas(p)
    return {
        "opcoes_tipo": a.OPCOES_TIPO, "avisos_reparo": avisos, "avisos_consolidacao": avisos_cons,
        "tabelas": [{"nome": k, "linhas": int(len(df)), "amostra": df_json(df, 10),
                     "colunas": [{"nome": str(c), "sugestao": a._sugerir_tipo(df[c])} for c in df.columns]}
                    for k, df in tabelas.items()],
    }


def automatizar_gerar(p: dict) -> dict:
    from generators.helpers import to_zip
    a, tabelas, _, _ = _carregar_planilhas(p)
    tipos_in = p.get("tipos") or {}
    tipos = {nome: {str(c): (tipos_in.get(nome, {}).get(str(c)) if tipos_in.get(nome, {}).get(str(c)) in a.OPCOES_TIPO
                              else a._sugerir_tipo(df[c])) for c in df.columns}
             for nome, df in tabelas.items()}
    conv = {nome: a._aplicar_tipos(df, tipos[nome]) for nome, df in tabelas.items()}
    cal, col_data = a._gerar_calendario(conv, tipos)
    medidas = a._gerar_medidas_genericas(conv, tipos, col_data)
    perguntas = a._gerar_perguntas_negocio(conv, tipos, medidas)
    para_tmdl = dict(conv)
    if cal is not None:
        para_tmdl["Calendario"] = cal
    tmdl = a._gerar_tmdl_automatizar(para_tmdl, medidas)
    texto_dax = a._montar_texto_dax(medidas, cal is not None)
    arquivos = _arquivos(**{"medidas_automatizar_bi.txt": texto_dax})
    if cal is not None:
        arquivos.update(_arquivos(**{"Calendario.csv": _csv(cal)}))
    zip_b64 = None
    if tmdl and para_tmdl:
        zb = to_zip(para_tmdl, extra_files={"model.tmdl": tmdl})
        if len(zb) <= 2_000_000:
            zip_b64 = base64.b64encode(zb).decode()
    return {
        "perguntas": perguntas,
        "medidas": {t: {c: [{"nome": m.get("nome", ""), "formula": m["formula"]} for m in lista] for c, lista in cats.items()}
                    for t, cats in medidas.items()},
        "calendario": None if cal is None else {"de": cal["Data"].min().strftime("%d/%m/%Y"), "ate": cal["Data"].max().strftime("%d/%m/%Y")},
        "arquivos": arquivos, "zip_base64": zip_b64,
    }


ACOES = {
    "formatar_dax": formatar_dax, "formatar_m": formatar_m, "auditar": auditar,
    "carrossel_paginas": carrossel_paginas, "carrossel_html": carrossel_html,
    "pl300": pl300, "scd_info": scd_info, "scd": scd, "causal_info": causal_info, "causal": causal,
    "sandbox_modelo": sandbox_modelo, "sandbox_exec": sandbox_exec, "qa_catalogo": qa_catalogo, "qa_perguntar": qa_perguntar,
    "automatizar_ler": automatizar_ler, "automatizar_gerar": automatizar_gerar,
}


def executar(corpo: dict) -> dict:
    fn = ACOES.get(str(corpo.get("acao", "")))
    if fn is None:
        raise ErroUsuario("Ação desconhecida.")
    return fn(corpo)
