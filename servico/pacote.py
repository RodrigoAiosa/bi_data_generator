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
from servico.ferramentas import df_json

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


def gerar_tabelas(setor: str, n_linhas: int, inicio: date, fim: date, *, mes_fiscal: int = 1,
                  anomalia: bool = False, drift: bool = False, lang: str = "pt",
                  seed: int | None = None) -> tuple[dict, list[dict]]:
    """Gera as tabelas (e o gabarito de anomalias/deriva). Com `seed`, o resultado é
    reproduzível: as ferramentas que dependem da base (SCD, Causais, Sandbox,
    Pergunte aos Dados) regeneram exatamente a mesma base a cada chamada."""
    import random

    import numpy as np
    from faker import Faker

    lang = "en" if lang == "en" else "pt"
    validar_parametros(setor, n_linhas, inicio, fim, mes_fiscal)
    contexto.definir(lang, mes_fiscal)
    try:
        # O módulo do setor sorteia "pools" já no import (primeira chamada do processo).
        # Importa sob uma seed FIXA para esses pools serem idênticos em qualquer
        # instância/processo, e só depois aplica a seed da base.
        def _semear(v: int) -> None:
            random.seed(v)
            np.random.seed(v % (2**32))
            Faker.seed(v)
            # `rng` é um Generator de módulo, importado por nome nos geradores:
            # precisa ser reiniciado no próprio objeto (não substituído).
            from generators import helpers as _h
            _h.rng.bit_generator.state = np.random.default_rng(v).bit_generator.state

        if seed is not None:
            _semear(0)
        gerador = obter_gerador(setor)
        if seed is not None:
            _semear(seed)
        tabelas = gerador(n_linhas, inicio, fim)
        gabarito: list[dict] = []
        if anomalia:
            tabelas, g = _injetar_anomalias(tabelas)
            gabarito.extend(g)
        if drift:
            tabelas, g = injetar_concept_drift(tabelas)
            gabarito.extend(g)
    finally:
        contexto.limpar()
    return tabelas, gabarito


def gerar_pacote(setor: str, n_linhas: int, inicio: date, fim: date, *,
                 mes_fiscal: int = 1, anomalia: bool = False, drift: bool = False,
                 lang: str = "pt", seed: int | None = None) -> tuple[bytes, dict]:
    """Retorna (bytes_do_zip, resumo). `resumo` é JSON-serializável e traz
    tabelas (contagem, colunas, 20 primeiras linhas) e medidas DAX."""
    lang = "en" if lang == "en" else "pt"
    validar_parametros(setor, n_linhas, inicio, fim, mes_fiscal)
    t0 = time.perf_counter()
    tabelas, gabarito = gerar_tabelas(setor, n_linhas, inicio, fim, mes_fiscal=mes_fiscal,
                                      anomalia=anomalia, drift=drift, lang=lang, seed=seed)
    contexto.definir(lang, mes_fiscal)
    try:
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
             "amostra": df_json(v, 20)["linhas"]}
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
