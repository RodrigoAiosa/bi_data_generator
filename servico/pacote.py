"""
servico/pacote.py: monta o pacote completo (bases CSV + projeto Power BI +
case de negócio + gabarito + dicionário) de um setor, sem nenhuma
dependência de Streamlit. É o núcleo usado pela função serverless da Vercel.
"""
from __future__ import annotations

import io
import time
import zipfile
from datetime import date

import contexto
from config import SETORES, obter_gerador
from generators.case_negocio import detectar_kpi_label, gerar_case_negocio
from generators.concept_drift import injetar_concept_drift
from generators.dicionario import gerar_dicionario
from generators.helpers import to_zip
from generators.medidas import gerar_bateria_medidas
from generators.pbip_generator import gerar_pbip
from generators.pbip_leiame import LEIAME_PBIP
from generators.tmdl_generator import gerar_tmdl
from servico.anomalias import _injetar_anomalias

MIN_LINHAS = 100
MAX_LINHAS = 100_000


def listar_setores() -> list[str]:
    return sorted(SETORES.keys())


def _formatar_gabarito(gabarito: list[dict], lang: str) -> str:
    if not gabarito:
        return ""
    titulo = ("GABARITO: Anomalias e Deriva Temporal Injetadas" if lang == "pt"
              else "ANSWER KEY: Injected Anomalies and Concept Drift")
    linhas = [titulo, "=" * len(titulo), ""]
    for i, item in enumerate(gabarito, 1):
        linhas.append(f"{i}. {item['tipo']}")
        linhas.append(f"   {'Localização' if lang == 'pt' else 'Location'}: {item['localizacao']}")
        linhas.append(f"   {'Detalhe' if lang == 'pt' else 'Detail'}: {item['detalhe']}")
        linhas.append("")
    return "\n".join(linhas)


def validar_parametros(setor: str, n_linhas: int, inicio: date, fim: date, mes_fiscal: int) -> None:
    if setor not in SETORES:
        raise ValueError("Setor inválido.")
    if not MIN_LINHAS <= n_linhas <= MAX_LINHAS:
        raise ValueError(f"O volume deve estar entre {MIN_LINHAS} e {MAX_LINHAS} linhas.")
    if inicio >= fim:
        raise ValueError("A data inicial deve ser anterior à data final.")
    if (fim - inicio).days > 366 * 15:
        raise ValueError("O período máximo é de 15 anos.")
    if not 1 <= mes_fiscal <= 12:
        raise ValueError("Mês fiscal inválido.")


def gerar_pacote(setor: str, n_linhas: int, inicio: date, fim: date, *,
                 mes_fiscal: int = 1, anomalia: bool = False, drift: bool = False,
                 lang: str = "pt") -> tuple[bytes, dict]:
    """Retorna (bytes_do_zip, resumo). `resumo` é JSON-serializável e traz
    tabelas (contagem, colunas, 20 primeiras linhas) e medidas DAX."""
    lang = "en" if lang == "en" else "pt"
    validar_parametros(setor, n_linhas, inicio, fim, mes_fiscal)
    t0 = time.perf_counter()
    contexto.definir(lang, mes_fiscal)
    try:
        tabelas = obter_gerador(setor)(n_linhas, inicio, fim)
        gabarito: list[dict] = []
        if anomalia:
            tabelas, g = _injetar_anomalias(tabelas)
            gabarito.extend(g)
        if drift:
            tabelas, g = injetar_concept_drift(tabelas)
            gabarito.extend(g)

        case_texto = gerar_case_negocio(setor, detectar_kpi_label(tabelas), lang=lang,
                                        anomalia_ativa=anomalia, drift_ativo=drift)
        arquivos = {"model.tmdl": gerar_tmdl(setor, tabelas), "case_negocio.txt": case_texto,
                    "LEIA-ME.txt": LEIAME_PBIP}
        gab_txt = _formatar_gabarito(gabarito, lang)
        if gab_txt:
            arquivos["gabarito.txt"] = gab_txt
        for caminho, conteudo in gerar_pbip(setor, tabelas).items():
            arquivos[f"PowerBI/{caminho}"] = conteudo
        zip_bytes = to_zip(tabelas, extra_files=arquivos)

        # Dicionário de dados (zip aninhado → pasta Dicionario/ no zip principal)
        dic = gerar_dicionario(setor, tabelas, lang=lang)
        buf = io.BytesIO(zip_bytes)
        with zipfile.ZipFile(buf, "a", zipfile.ZIP_DEFLATED) as zf, \
                zipfile.ZipFile(io.BytesIO(dic)) as zd:
            for nome in zd.namelist():
                zf.writestr(f"Dicionario/{nome}", zd.read(nome))
        zip_bytes = buf.getvalue()

        medidas = gerar_bateria_medidas(tabelas)
    finally:
        contexto.limpar()

    resumo = {
        "setor": setor,
        "segundos": round(time.perf_counter() - t0, 2),
        "tabelas": [
            {"nome": k, "linhas": int(len(v)), "colunas": list(map(str, v.columns)),
             "amostra": v.head(20).astype(object).where(v.head(20).notna(), None)
                          .astype(str).values.tolist()}
            for k, v in tabelas.items()
        ],
        "case": case_texto,
        "gabarito": gabarito,
        "medidas": {
            fato: {cat: [{"nome": m["nome"], "formula": m["formula"], "descricao": m["descricao"]}
                         for m in lista]
                   for cat, lista in cats.items() if lista}
            for fato, cats in medidas.items()
        },
        "tamanho_zip": len(zip_bytes),
    }
    return zip_bytes, resumo
