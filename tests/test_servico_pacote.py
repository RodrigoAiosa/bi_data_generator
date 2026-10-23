"""Testes do serviço sem Streamlit (usado pela função serverless da Vercel)."""
import io
import sys
import zipfile
from datetime import date

import pytest

from servico.pacote import gerar_pacote, listar_setores, validar_parametros

INI, FIM = date(2024, 1, 1), date(2024, 12, 31)


def test_pacote_contem_bases_powerbi_e_docs():
    z, r = gerar_pacote(listar_setores()[0], 200, INI, FIM, anomalia=True, drift=True)
    nomes = zipfile.ZipFile(io.BytesIO(z)).namelist()
    assert any(n.endswith(".csv") for n in nomes)
    assert any(n.endswith(".pbip") for n in nomes)
    assert {"model.tmdl", "case_negocio.txt", "gabarito.txt", "LEIA-ME.txt"} <= set(nomes)
    assert any(n.startswith("Dicionario/") for n in nomes)
    assert r["tabelas"] and r["medidas"]


def test_ingles_e_mes_fiscal_nao_vazam_para_proxima_chamada():
    gerar_pacote("🐾 Pet & Veterinária", 200, INI, FIM, lang="en", mes_fiscal=7)
    import contexto
    assert contexto.lang() is None and contexto.mes_fiscal() is None


@pytest.mark.parametrize("args", [
    ("Setor inexistente", 500, INI, FIM, 1), (listar_setores()[0], 50, INI, FIM, 1),
    (listar_setores()[0], 500, FIM, INI, 1), (listar_setores()[0], 500, INI, FIM, 13),
])
def test_validacao(args):
    with pytest.raises(ValueError):
        validar_parametros(*args)


