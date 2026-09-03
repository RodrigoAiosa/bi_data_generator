"""
generators/carrossel_pbi.py

Lê as páginas de um relatório Power BI a partir do próprio arquivo .pbix
(o formato binário padrão — internamente um ZIP contendo Report/Layout,
um JSON em UTF-16LE com a lista de seções) ou, alternativamente, de um
ZIP no formato de projeto mais novo (.pbip com PBIR, pasta
Report/definition/pages/). Devolve, na ordem do relatório, o nome de
exibição de cada página junto com o ID interno (page_id) — o valor que
vai no parâmetro "pageName" de uma URL de embed do Power BI Service.

A partir da lista de páginas selecionadas pelo usuário, monta as URLs
completas de embed e gera um arquivo HTML autônomo que alterna entre
elas automaticamente, a cada N segundos, trocando o "src" de um
<iframe> em tela cheia.
"""

from __future__ import annotations

import io
import json
import zipfile


class ArquivoInvalidoError(Exception):
    """Erro amigável quando o arquivo enviado não tem a estrutura esperada."""


def _extrair_do_layout_classico(zf: zipfile.ZipFile, nomes: list[str]) -> list[tuple[str, str]] | None:
    """
    Tenta ler o formato PADRÃO de um .pbix: um único arquivo 'Report/Layout'
    (em UTF-16LE, às vezes com BOM) contendo um JSON com a lista de
    'sections' — cada uma com 'name' (o page_id usado no pageName da URL
    de embed) e 'displayName' (o nome exibido na aba do relatório).
    Devolve None se não encontrar esse arquivo (não é um erro — pode ser
    que o arquivo enviado use o formato de pasta PBIR, tratado à parte).
    """
    caminho_layout = next(
        (n for n in nomes if n.replace("\\", "/").lower() == "report/layout"),
        None,
    )
    if caminho_layout is None:
        return None

    bruto = zf.read(caminho_layout)
    try:
        texto = bruto.decode("utf-16")  # detecta BOM automaticamente, se houver
    except UnicodeDecodeError:
        texto = bruto.decode("utf-16-le")

    try:
        layout = json.loads(texto)
    except json.JSONDecodeError as e:
        raise ArquivoInvalidoError(f"O arquivo Report/Layout não é um JSON válido: {e}")

    secoes = layout.get("sections", [])
    if not secoes:
        raise ArquivoInvalidoError("O Report/Layout foi encontrado, mas não tem nenhuma página em 'sections'.")

    secoes_ordenadas = sorted(secoes, key=lambda s: s.get("ordinal", 0))
    return [(s.get("displayName") or s.get("name", "?"), s["name"]) for s in secoes_ordenadas]


def _extrair_do_pbir(zf: zipfile.ZipFile, nomes: list[str]) -> list[tuple[str, str]] | None:
    """
    Tenta ler o formato de PASTA mais novo (.pbip com PBIR, ou um .pbix com
    PBIR habilitado): Report/definition/pages/pages.json (lista 'pageOrder')
    + um definition/pages/{id}/page.json por página (campo 'displayName').
    Devolve None se não encontrar pages.json (trata-se à parte do formato
    clássico acima).
    """
    caminho_pages_json = next(
        (n for n in nomes if n.replace("\\", "/").lower().endswith("definition/pages/pages.json")),
        None,
    )
    if caminho_pages_json is None:
        return None

    try:
        pages_json = json.loads(zf.read(caminho_pages_json).decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ArquivoInvalidoError(f"O arquivo pages.json não é um JSON válido: {e}")

    page_order = pages_json.get("pageOrder", [])
    if not page_order:
        raise ArquivoInvalidoError("O pages.json foi encontrado, mas não tem nenhuma página em 'pageOrder'.")

    paginas: list[tuple[str, str]] = []
    for page_id in page_order:
        caminho_page_json = next(
            (
                n for n in nomes
                if n.replace("\\", "/").lower().endswith(f"definition/pages/{page_id.lower()}/page.json")
            ),
            None,
        )
        nome_pagina = page_id
        if caminho_page_json:
            try:
                page_json = json.loads(zf.read(caminho_page_json).decode("utf-8"))
                nome_pagina = page_json.get("displayName", page_id)
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        paginas.append((nome_pagina, page_id))

    return paginas


def extrair_paginas_do_zip(arquivo_bytes: bytes) -> list[tuple[str, str]]:
    """
    Recebe os bytes de um arquivo Power BI e devolve uma lista ordenada de
    (nome_da_pagina, page_id). Aceita:
    - um .pbix de verdade (o formato binário padrão do Power BI Desktop,
      com Report/Layout no formato clássico);
    - um .pbix com PBIR habilitado, ou o ZIP de um projeto .pbip inteiro
      (ou só da pasta .Report), no formato de pasta mais novo
      (Report/definition/pages/pages.json).
    A detecção é automática — não precisa informar qual formato é.
    """
    try:
        zf = zipfile.ZipFile(io.BytesIO(arquivo_bytes))
    except zipfile.BadZipFile:
        raise ArquivoInvalidoError(
            "Não consegui abrir o arquivo enviado como um pacote Power BI válido. "
            "Confirme que é um arquivo .pbix (ou o .zip do projeto .pbip) e tente de novo."
        )

    nomes = zf.namelist()

    paginas = _extrair_do_layout_classico(zf, nomes)
    if paginas is not None:
        return paginas

    paginas = _extrair_do_pbir(zf, nomes)
    if paginas is not None:
        return paginas

    raise ArquivoInvalidoError(
        "Não encontrei as páginas do relatório dentro do arquivo — nem 'Report/Layout' "
        "(formato .pbix padrão) nem 'Report/definition/pages/pages.json' (formato de "
        "projeto .pbip/PBIR). Confirme que o arquivo enviado é mesmo um .pbix exportado "
        "do Power BI Desktop, ou o .zip de um projeto .pbip."
    )


def montar_url_embed(
    report_id: str, ctid: str, page_id: str,
    chromeless: bool = True, auto_auth: bool = True,
) -> str:
    """Monta a URL de embed do Power BI Service para uma página específica."""
    partes = [
        "https://app.powerbi.com/reportEmbed",
        f"?reportId={report_id}",
    ]
    if auto_auth:
        partes.append("&autoAuth=true")
    partes.append(f"&ctid={ctid}")
    partes.append(f"&pageName={page_id}")
    if chromeless:
        partes.append("&chromeless=true")
    return "".join(partes)


def gerar_html_carrossel(paginas_com_url: list[tuple[str, str, str]], intervalo_seg: int) -> str:
    """
    Gera um HTML autônomo (sem dependências externas) que alterna entre as
    páginas automaticamente a cada `intervalo_seg` segundos, trocando o
    'src' de um <iframe> em tela cheia. Basta abrir o arquivo num navegador
    (ex.: numa TV/monitor de sala) e deixar rodando.

    paginas_com_url: lista de (nome, page_id, url_completa), na ordem de exibição.
    """
    dados_js = json.dumps(
        [{"nome": nome, "url": url} for nome, _pid, url in paginas_com_url],
        ensure_ascii=False,
    )
    intervalo_ms = max(1, int(intervalo_seg)) * 1000

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Carrossel de Relatório Power BI</title>
<style>
  html, body {{ margin: 0; padding: 0; height: 100%; overflow: hidden; background: #000; }}
  iframe {{ width: 100%; height: 100%; border: none; display: block; }}
  #rotulo-pagina {{
    position: fixed; left: 12px; bottom: 12px;
    background: rgba(0,0,0,0.65); color: #fff;
    font-family: Arial, sans-serif; font-size: 14px;
    padding: 6px 12px; border-radius: 6px;
    z-index: 10; pointer-events: none;
  }}
</style>
</head>
<body>
<iframe id="frame-relatorio" src="" allowfullscreen></iframe>
<div id="rotulo-pagina"></div>

<script>
  const PAGINAS = {dados_js};
  const INTERVALO_MS = {intervalo_ms};
  let indiceAtual = 0;

  function mostrarPagina(indice) {{
    const pagina = PAGINAS[indice];
    document.getElementById("frame-relatorio").src = pagina.url;
    document.getElementById("rotulo-pagina").textContent =
      (indice + 1) + " / " + PAGINAS.length + " — " + pagina.nome;
  }}

  mostrarPagina(indiceAtual);
  setInterval(function () {{
    indiceAtual = (indiceAtual + 1) % PAGINAS.length;
    mostrarPagina(indiceAtual);
  }}, INTERVALO_MS);
</script>
</body>
</html>
"""
