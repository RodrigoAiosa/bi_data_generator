"""
generators/carrossel_pbi.py

Lê o arquivo Report/definition/pages/pages.json de um projeto Power BI
(formato PBIR — a estrutura de pastas que o Power BI Desktop usa desde a
versão que introduziu o PBIP) e devolve, na ordem definida em "pageOrder",
o nome de cada página (lido de definition/pages/{id}/page.json) junto com
o ID da pasta — o valor que vai no parâmetro "pageName" de uma URL de
embed do Power BI Service.

A partir dessa lista, monta as URLs completas de embed e gera um arquivo
HTML autônomo que alterna entre as páginas automaticamente, a cada N
segundos, trocando o "src" de um <iframe> em tela cheia.
"""

from __future__ import annotations

import io
import json
import zipfile


class ArquivoInvalidoError(Exception):
    """Erro amigável quando o ZIP enviado não tem a estrutura esperada."""


def extrair_paginas_do_zip(zip_bytes: bytes) -> list[tuple[str, str]]:
    """
    Recebe os bytes de um .zip contendo (em qualquer nível de pasta) o
    caminho 'definition/pages/pages.json' de um relatório Power BI (PBIR),
    e devolve uma lista ordenada de (nome_da_pagina, page_id).

    Aceita tanto um ZIP do projeto inteiro (.pbip com as pastas .Report e
    .SemanticModel) quanto um ZIP só da pasta .Report — a busca é feita
    pelo final do caminho, não pelo caminho exato, então funciona
    independente de como a pessoa organizou o ZIP.
    """
    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile:
        raise ArquivoInvalidoError(
            "O arquivo enviado não é um .zip válido. Compacte a pasta do seu "
            "projeto Power BI (ou pelo menos a pasta 'Report') em um .zip e tente de novo."
        )

    nomes = zf.namelist()
    caminho_pages_json = next(
        (n for n in nomes if n.replace("\\", "/").lower().endswith("definition/pages/pages.json")),
        None,
    )
    if caminho_pages_json is None:
        raise ArquivoInvalidoError(
            "Não encontrei o arquivo 'definition/pages/pages.json' dentro do ZIP. "
            "Confirme que o ZIP contém a pasta 'Report/definition/pages' do seu "
            "projeto Power BI (formato .pbip com PBIR, não o .pbix binário antigo)."
        )

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
        nome_pagina = page_id  # fallback caso não ache o page.json ou o displayName
        if caminho_page_json:
            try:
                page_json = json.loads(zf.read(caminho_page_json).decode("utf-8"))
                nome_pagina = page_json.get("displayName", page_id)
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        paginas.append((nome_pagina, page_id))

    return paginas


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
