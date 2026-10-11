"""
generators/pbip_relatorio.py
Monta o MOCKUP do relatório Power BI (formato PBIR: 1 arquivo JSON por página
e por visual) do projeto .pbip: visual minimalista e moderno, com cartões de
KPI, gráficos e filtros (segmentações) escolhidos automaticamente a partir
das tabelas e medidas DAX de cada setor.

Inspirado no "Montador de Projetos" do AtlasAPI (página 1280x720, cabeçalho,
cartões brancos arredondados sobre fundo cinza-claro, cor de destaque por
tema), mas escrito para o formato PBIR (visual.json) em vez do report.json
clássico.

Uma página por tabela fato (máx. 4). Cada página tem:
  - cabeçalho com título e subtítulo
  - até 3 segmentações (Ano + 2 colunas categóricas da fato)
  - 4 cartões (contagem + totais/médias da própria fato)
  - gráfico de linha (evolução mensal), 2 de barras e 1 tabela de detalhe

Só usa colunas da própria fato, de dCalendario e medidas da tabela
"Medidas": não depende de relacionamentos adicionais além dos já criados
pelo modelo semântico (fato -> dCalendario).
"""

from __future__ import annotations

import hashlib
import json

import pandas as pd

_BASE = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"
SCHEMA_VISUAL = f"{_BASE}/visualContainer/2.0.0/schema.json"
SCHEMA_PAGE = f"{_BASE}/page/1.3.0/schema.json"
SCHEMA_PAGES = f"{_BASE}/pagesMetadata/1.0.0/schema.json"

LARGURA, ALTURA, MARGEM = 1280, 720, 24
MAX_PAGINAS = 4

# (cor de destaque, tom claro) — um por setor, escolhido por hash do nome.
_TEMAS = [
    ("#4F46E5", "#EEF2FF"),  # índigo
    ("#0D9488", "#F0FDFA"),  # verde-água
    ("#2563EB", "#EFF6FF"),  # azul
    ("#7C3AED", "#F5F3FF"),  # violeta
    ("#DB2777", "#FDF2F8"),  # rosa
    ("#EA580C", "#FFF7ED"),  # laranja
    ("#059669", "#ECFDF5"),  # verde
]
_FUNDO = "#F3F4F6"
_TEXTO = "#111827"
_TEXTO_SUAVE = "#6B7280"
_BORDA = "#E5E7EB"


# ── Expressões de consulta (semanticQuery) ────────────────────────────────────
def _lit(v: str) -> dict:
    return {"expr": {"Literal": {"Value": v}}}


def _txt(s: str) -> dict:
    return _lit("'" + s.replace("'", "''") + "'")


def _cor(hexa: str) -> dict:
    return {"solid": {"color": _txt(hexa)}}


def _col(tabela: str, coluna: str) -> dict:
    return {"Column": {"Expression": {"SourceRef": {"Entity": tabela}}, "Property": coluna}}


def _med(nome: str) -> dict:
    return {"Measure": {"Expression": {"SourceRef": {"Entity": "Medidas"}}, "Property": nome}}


def _proj(campo: dict, tabela: str, nome: str, rotulo: str | None = None) -> dict:
    p = {"field": campo, "queryRef": f"{tabela}.{nome}", "nativeQueryRef": nome}
    if rotulo:
        p["displayName"] = rotulo
    return p


def _rotulo(coluna: str) -> str:
    return coluna.replace("_", " ").strip().capitalize()


# ── Moldura dos visuais ───────────────────────────────────────────────────────
def _moldura(titulo: str | None) -> dict:
    obj = {
        "background": [{"properties": {"show": _lit("true"), "color": _cor("#FFFFFF")}}],
        "border": [{"properties": {"show": _lit("true"), "color": _cor(_BORDA), "radius": _lit("12D")}}],
    }
    if titulo:
        obj["title"] = [{"properties": {
            "show": _lit("true"),
            "text": _txt(titulo),
            "fontColor": _cor(_TEXTO_SUAVE),
            "fontSize": _lit("11D"),
        }}]
    else:
        obj["title"] = [{"properties": {"show": _lit("false")}}]
    return obj


def _visual_json(nome: str, x: int, y: int, w: int, h: int, z: int, visual: dict) -> dict:
    return {
        "$schema": SCHEMA_VISUAL,
        "name": nome,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
        "visual": visual,
    }


def _cartao(med: str, rotulo: str, cor: str) -> dict:
    return {
        "visualType": "card",
        "query": {"queryState": {"Values": {"projections": [_proj(_med(med), "Medidas", med, rotulo)]}}},
        "objects": {
            "labels": [{"properties": {"color": _cor(cor), "fontSize": _lit("26D")}}],
            "categoryLabels": [{"properties": {"show": _lit("true"), "color": _cor(_TEXTO_SUAVE), "fontSize": _lit("11D")}}],
        },
        "visualContainerObjects": _moldura(None),
        "drillFilterOtherVisuals": True,
    }


def _grafico(tipo: str, cat_tab: str, cat_col: str, med: str, cor: str, titulo: str,
             ordenar_por_medida: bool, rotulo_cat: str | None = None) -> dict:
    q = {"queryState": {
        "Category": {"projections": [_proj(_col(cat_tab, cat_col), cat_tab, cat_col, rotulo_cat)]},
        "Y": {"projections": [_proj(_med(med), "Medidas", med)]},
    }}
    if ordenar_por_medida:
        q["sortDefinition"] = {"sort": [{"field": _med(med), "direction": "Descending"}]}
    return {
        "visualType": tipo,
        "query": q,
        "objects": {
            "dataPoint": [{"properties": {"fill": _cor(cor)}}],
            "legend": [{"properties": {"show": _lit("false")}}],
        },
        "visualContainerObjects": _moldura(titulo),
        "drillFilterOtherVisuals": True,
    }


def _segmentacao(tabela: str, coluna: str, rotulo: str) -> dict:
    return {
        "visualType": "slicer",
        "query": {"queryState": {"Values": {"projections": [_proj(_col(tabela, coluna), tabela, coluna, rotulo)]}}},
        "objects": {
            "data": [{"properties": {"mode": _txt("Dropdown")}}],
            "header": [{"properties": {"show": _lit("false")}}],
        },
        "visualContainerObjects": _moldura(rotulo),
        "drillFilterOtherVisuals": True,
    }


def _tabela(tab: str, colunas: list[str], medidas: list[str]) -> dict:
    proj = [_proj(_col(tab, c), tab, c, _rotulo(c)) for c in colunas]
    proj += [_proj(_med(m), "Medidas", m) for m in medidas]
    return {
        "visualType": "tableEx",
        "query": {"queryState": {"Values": {"projections": proj}}},
        "objects": {},
        "visualContainerObjects": _moldura("Detalhamento"),
        "drillFilterOtherVisuals": True,
    }


def _texto(linhas: list[tuple[str, str, str, bool]]) -> dict:
    """Caixa de texto: lista de (texto, tamanho, cor, negrito), um parágrafo cada."""
    paragrafos = []
    for texto, tamanho, cor, negrito in linhas:
        estilo = {"fontSize": tamanho, "color": cor, "fontFamily": "Segoe UI"}
        if negrito:
            estilo["fontWeight"] = "bold"
        paragrafos.append({"textRuns": [{"value": texto, "textStyle": estilo}]})
    return {
        "visualType": "textbox",
        "objects": {"general": [{"properties": {"paragraphs": paragrafos}}]},
        "visualContainerObjects": {"background": [{"properties": {"show": _lit("false")}}]},
    }


# ── Escolha automática do que mostrar ─────────────────────────────────────────
def _categoricas(df: pd.DataFrame) -> list[str]:
    """Colunas de texto de baixa cardinalidade (boas p/ filtro e gráfico),
    das mais enxutas (3-12 valores) para as maiores."""
    cands = []
    for c in df.columns:
        if c.lower().startswith(("id_", "sk_")) or "data" in c.lower():
            continue
        s = df[c]
        if not (pd.api.types.is_object_dtype(s) or pd.api.types.is_string_dtype(s)):
            continue
        n = s.nunique(dropna=True)
        if 2 <= n <= 25:
            cands.append((0 if 3 <= n <= 12 else 1, n, c))
    return [c for _, _, c in sorted(cands)]


def _medidas_da_fato(medidas_por_fato: dict, fato: str) -> dict:
    """{'registros': nome|None, 'totais': [...], 'medias': [...], 'distintas': [...]}"""
    cats = medidas_por_fato.get(fato, {})
    nomes = {cat.split(" ", 1)[-1]: [m["nome"] for m in lista] for cat, lista in cats.items()}
    agreg = next((v for k, v in nomes.items() if k.startswith("Agrega")), [])
    cont = next((v for k, v in nomes.items() if k.startswith("Contagens")), [])
    return {
        "registros": next((n for n in cont if n.startswith("Qtde de Registros")), None),
        "distintas": [n for n in cont if n.startswith("Qtde Distinta")],
        "totais": [n for n in agreg if n.startswith("Total ")],
        "medias": [n for n in agreg if n.startswith("Média ")],
    }


def _pagina(idx: int, fato: str, df: pd.DataFrame, medidas: dict, tem_calendario: bool,
            titulo_setor: str, tema: tuple[str, str], tabela_detalhe_cols: list[str]) -> dict[str, dict]:
    """Devolve {id_visual: visual.json} de uma página."""
    cor, cor_clara = tema
    cats = _categoricas(df)
    visuais: dict[str, dict] = {}
    z = [0]

    def add(nome: str, x: int, y: int, w: int, h: int, visual: dict):
        z[0] += 1
        visuais[nome] = _visual_json(nome, x, y, w, h, z[0], visual)

    util = LARGURA - 2 * MARGEM
    # Cabeçalho
    add("cabecalho", MARGEM, 14, util, 56, _texto([
        (f"{titulo_setor} · {fato.removeprefix('Fato')}", "20pt", _TEXTO, True),
        ("Painel de exemplo gerado pelo BI Data Generator", "10pt", _TEXTO_SUAVE, False),
    ]))

    # Segmentações (filtros)
    filtros: list[tuple[str, str, str]] = []
    if tem_calendario:
        filtros.append(("dCalendario", "Ano", "Ano"))
    for c in cats[:2]:
        filtros.append((fato, c, _rotulo(c)))
    y_f, h_f = 78, 58
    gap = 16
    n_f = max(len(filtros), 1)
    w_f = (util - gap * (n_f - 1)) // n_f if filtros else util
    w_f = min(w_f, 300)
    for i, (t, c, r) in enumerate(filtros):
        add(f"filtro{i + 1}", MARGEM + i * (w_f + gap), y_f, w_f, h_f, _segmentacao(t, c, r))

    # Cartões
    cartoes: list[tuple[str, str]] = []
    if medidas["registros"]:
        cartoes.append((medidas["registros"], "Registros"))
    for m in medidas["totais"][:2]:
        cartoes.append((m, m))
    if medidas["medias"]:
        cartoes.append((medidas["medias"][0], medidas["medias"][0]))
    for m in medidas["distintas"]:
        if len(cartoes) >= 4:
            break
        cartoes.append((m, m))
    for m in medidas["totais"][2:]:
        if len(cartoes) >= 4:
            break
        cartoes.append((m, m))
    cartoes = cartoes[:4]
    y_c, h_c = 150, 96
    n_c = max(len(cartoes), 1)
    w_c = (util - gap * (n_c - 1)) // n_c
    for i, (m, r) in enumerate(cartoes):
        add(f"cartao{i + 1}", MARGEM + i * (w_c + gap), y_c, w_c, h_c, _cartao(m, r, cor))

    # Medida principal dos gráficos
    principal = (medidas["totais"] or [medidas["registros"]] or [None])[0] or medidas["registros"]
    secundaria = medidas["registros"] or principal
    if principal is None:
        return visuais

    y1, h1 = y_c + h_c + 16, 216
    y2 = y1 + h1 + 16
    h2 = ALTURA - y2 - 16
    w_esq = int(util * 0.58)
    w_dir = util - w_esq - gap

    if tem_calendario:
        add("grafico_linha", MARGEM, y1, w_esq, h1,
            _grafico("lineChart", "dCalendario", "MesAno", principal, cor, f"{principal} por mês", False, "Mês"))
    elif cats:
        add("grafico_linha", MARGEM, y1, w_esq, h1,
            _grafico("clusteredColumnChart", fato, cats[0], principal, cor, f"{principal} por {_rotulo(cats[0]).lower()}", True))
    if cats:
        add("grafico_barra1", MARGEM + w_esq + gap, y1, w_dir, h1,
            _grafico("clusteredBarChart", fato, cats[0], principal, cor, f"{principal} por {_rotulo(cats[0]).lower()}", True))
    if len(cats) >= 2:
        add("grafico_barra2", MARGEM, y2, w_dir, h2,
            _grafico("clusteredColumnChart", fato, cats[1], secundaria, cor, f"{secundaria} por {_rotulo(cats[1]).lower()}", True))
    elif cats:
        add("grafico_barra2", MARGEM, y2, w_dir, h2,
            _grafico("clusteredColumnChart", fato, cats[0], secundaria, cor, f"{secundaria} por {_rotulo(cats[0]).lower()}", True))
    if tabela_detalhe_cols:
        add("tabela", MARGEM + w_dir + gap, y2, util - w_dir - gap, h2,
            _tabela(fato, tabela_detalhe_cols, [principal] if principal != medidas["registros"] else []))
    return visuais


def gerar_relatorio(base: str, nome_setor: str, tabelas: dict[str, pd.DataFrame],
                    medidas_por_fato: dict, fatos_com_calendario: set[str] | None = None) -> dict[str, str]:
    """Arquivos de páginas/visuais do relatório. `base` = '<pasta>.Report'.
    Devolve {caminho: json} com pages.json, page.json e visual.json."""
    tema = _TEMAS[int(hashlib.md5(nome_setor.encode("utf-8")).hexdigest(), 16) % len(_TEMAS)]
    tem_cal = "dCalendario" in tabelas and "Ano" in tabelas["dCalendario"].columns \
        and "MesAno" in tabelas["dCalendario"].columns
    fatos = [n for n in tabelas if n.startswith("Fato") and n in medidas_por_fato][:MAX_PAGINAS]

    arquivos: dict[str, str] = {}
    ordem: list[str] = []
    for i, fato in enumerate(fatos, start=1):
        df = tabelas[fato]
        medidas = _medidas_da_fato(medidas_por_fato, fato)
        # a fato precisa ter relação com dCalendario: só usamos o calendário se ela tem coluna de data
        tem_data = tem_cal and fato in (fatos_com_calendario or set())
        cols_det = [c for c in df.columns if not c.lower().startswith(("id_", "sk_"))][:4]
        nome_pag = f"pagina{i}"
        visuais = _pagina(i, fato, df, medidas, tem_data, nome_setor, tema, cols_det[:3])
        if not visuais:
            continue
        ordem.append(nome_pag)
        pag = {
            "$schema": SCHEMA_PAGE,
            "name": nome_pag,
            "displayName": fato.removeprefix("Fato") or fato,
            "displayOption": "FitToPage",
            "height": ALTURA,
            "width": LARGURA,
            "objects": {"background": [{"properties": {"color": _cor(_FUNDO), "transparency": _lit("0D")}}]},
        }
        arquivos[f"{base}/definition/pages/{nome_pag}/page.json"] = json.dumps(pag, indent=2, ensure_ascii=False)
        for vid, v in visuais.items():
            arquivos[f"{base}/definition/pages/{nome_pag}/visuals/{vid}/visual.json"] = \
                json.dumps(v, indent=2, ensure_ascii=False)

    if not ordem:  # setor sem fato com medidas: mantém uma página vazia
        ordem = ["pagina1"]
        arquivos[f"{base}/definition/pages/pagina1/page.json"] = json.dumps({
            "$schema": SCHEMA_PAGE, "name": "pagina1", "displayName": "Página 1",
            "displayOption": "FitToPage", "height": ALTURA, "width": LARGURA,
        }, indent=2, ensure_ascii=False)

    arquivos[f"{base}/definition/pages/pages.json"] = json.dumps(
        {"$schema": SCHEMA_PAGES, "pageOrder": ordem, "activePageName": ordem[0]},
        indent=2, ensure_ascii=False)
    return arquivos
