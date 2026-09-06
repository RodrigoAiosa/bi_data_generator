"""
tests/test_scd_simulador.py

Testes do motor da aba "🕰️ Simulador de Dimensões Mutáveis"
(generators/scd_simulador.py).
"""
import pandas as pd
import pytest

from config import obter_gerador
from generators.scd_simulador import gerar_cenario_scd, ScdError
from tests.conftest import DATA_INICIO, DATA_FIM


@pytest.fixture
def dim_controlada() -> pd.DataFrame:
    """Uma dimensão pequena e 100% controlada, pra validar o resultado
    exato (não uma amostra aleatória de um setor real)."""
    return pd.DataFrame({
        "id_cliente": [1, 2, 3, 4, 5],
        "nome": ["Ana", "Bruno", "Carla", "Diego", "Elza"],
        "cidade": ["SP", "RJ", "SP", "MG", "RJ"],
        "segmento": ["Varejo", "Atacado", "Varejo", "Atacado", "Varejo"],
    })


def test_gera_exatamente_o_numero_de_mudancas_pedido(dim_controlada):
    tabelas = {"DimCliente": dim_controlada}
    resultado = gerar_cenario_scd(tabelas, "DimCliente", n_mudancas=3, seed=1)
    assert len(resultado["gabarito"]) == 3


def test_nao_pede_mais_mudancas_do_que_linhas_existem(dim_controlada):
    tabelas = {"DimCliente": dim_controlada}
    resultado = gerar_cenario_scd(tabelas, "DimCliente", n_mudancas=999, seed=1)
    assert len(resultado["gabarito"]) <= len(dim_controlada)


def test_recusa_dimensao_sem_coluna_mutavel():
    """Só chaves e números — nenhuma coluna de texto pra mudar."""
    dim_sem_texto = pd.DataFrame({"id_x": [1, 2, 3], "id_y": [10, 20, 30], "valor": [1.5, 2.5, 3.5]})
    tabelas = {"DimSemTexto": dim_sem_texto}
    with pytest.raises(ScdError):
        gerar_cenario_scd(tabelas, "DimSemTexto", n_mudancas=1)


def test_ignora_colunas_de_data_como_candidatas(dim_controlada):
    """'mudar a data de nascimento' não é uma historia classica de SCD —
    confirma que uma coluna de data nunca aparece no gabarito, mesmo
    quando é a única alternativa de texto disponível."""
    dim = dim_controlada.copy()
    dim["data_cadastro"] = ["2020-01-01", "2020-02-01", "2020-03-01", "2020-04-01", "2020-05-01"]
    tabelas = {"DimCliente": dim}
    resultado = gerar_cenario_scd(tabelas, "DimCliente", n_mudancas=5, seed=1)
    assert "data_cadastro" not in set(resultado["gabarito"]["coluna"])


def test_scd_tipo1_e_identico_ao_snapshot_t1(dim_controlada):
    tabelas = {"DimCliente": dim_controlada}
    resultado = gerar_cenario_scd(tabelas, "DimCliente", n_mudancas=2, seed=1)
    assert resultado["scd_tipo1"].equals(resultado["snapshot_t1"])


def test_scd_tipo2_duplica_so_as_linhas_alteradas(dim_controlada):
    tabelas = {"DimCliente": dim_controlada}
    resultado = gerar_cenario_scd(tabelas, "DimCliente", n_mudancas=2, seed=1)
    pk = resultado["coluna_pk"]
    gabarito = resultado["gabarito"]
    scd2 = resultado["scd_tipo2"]

    pks_alterados = set(gabarito[pk])
    for chave in dim_controlada[pk]:
        linhas = scd2[scd2[pk] == chave]
        esperado = 2 if chave in pks_alterados else 1
        assert len(linhas) == esperado, f"chave {chave}: esperava {esperado} linha(s), achou {len(linhas)}"

    # A linha "fechada" tem o valor ANTIGO e RegistroAtual=False; a "aberta"
    # tem o valor NOVO e RegistroAtual=True.
    for _, g in gabarito.iterrows():
        linhas = scd2[scd2[pk] == g[pk]]
        fechada = linhas[linhas["RegistroAtual"] == False]  # noqa: E712
        aberta = linhas[linhas["RegistroAtual"] == True]  # noqa: E712
        assert fechada.iloc[0][g["coluna"]] == g["valor_antigo"]
        assert aberta.iloc[0][g["coluna"]] == g["valor_novo"]
        assert pd.notna(fechada.iloc[0]["DataFimValidade"])
        assert aberta.iloc[0]["DataFimValidade"] == pd.Timestamp("2099-12-31")


def test_scd_tipo2_tem_chave_substituta_unica(dim_controlada):
    """sk_scd precisa ser única linha a linha, já que a PK natural se
    repete pras linhas que mudaram."""
    tabelas = {"DimCliente": dim_controlada}
    resultado = gerar_cenario_scd(tabelas, "DimCliente", n_mudancas=3, seed=1)
    scd2 = resultado["scd_tipo2"]
    assert scd2["sk_scd"].is_unique


def test_scd_tipo3_guarda_valor_anterior_na_coluna_irma(dim_controlada):
    tabelas = {"DimCliente": dim_controlada}
    resultado = gerar_cenario_scd(tabelas, "DimCliente", n_mudancas=2, seed=1)
    pk = resultado["coluna_pk"]
    gabarito = resultado["gabarito"]
    scd3 = resultado["scd_tipo3"]

    for _, g in gabarito.iterrows():
        col_anterior = f"{g['coluna']}_Anterior"
        assert col_anterior in scd3.columns
        linha = scd3[scd3[pk] == g[pk]].iloc[0]
        assert linha[col_anterior] == g["valor_antigo"]
        assert linha[g["coluna"]] == g["valor_novo"]


def test_scd_tipo3_nao_marca_linhas_que_nao_mudaram(dim_controlada):
    tabelas = {"DimCliente": dim_controlada}
    resultado = gerar_cenario_scd(tabelas, "DimCliente", n_mudancas=1, seed=1)
    pk = resultado["coluna_pk"]
    gabarito = resultado["gabarito"]
    scd3 = resultado["scd_tipo3"]

    pk_alterada = gabarito.iloc[0][pk]
    coluna_alterada = gabarito.iloc[0]["coluna"]
    col_anterior = f"{coluna_alterada}_Anterior"

    for chave in dim_controlada[pk]:
        if chave == pk_alterada:
            continue
        linha = scd3[scd3[pk] == chave].iloc[0]
        assert pd.isna(linha[col_anterior]), f"chave {chave} não deveria ter valor em {col_anterior}"


def test_gabarito_nunca_mistura_tipo_na_mesma_coluna(dim_controlada):
    """Já foi um bug real: se colunas de tipos diferentes (texto e bool)
    puderem ser escolhidas em linhas diferentes, valor_antigo/valor_novo
    ficam com tipo misto e quebram a serialização Arrow do Streamlit.
    Confirma que isso não acontece mais."""
    tabelas = {"DimCliente": dim_controlada}
    resultado = gerar_cenario_scd(tabelas, "DimCliente", n_mudancas=5, seed=1)
    gabarito = resultado["gabarito"]
    tipos_antigo = {type(v) for v in gabarito["valor_antigo"]}
    tipos_novo = {type(v) for v in gabarito["valor_novo"]}
    assert len(tipos_antigo) == 1, f"tipos mistos em valor_antigo: {tipos_antigo}"
    assert len(tipos_novo) == 1, f"tipos mistos em valor_novo: {tipos_novo}"


def test_scd_em_todas_as_dimensoes_do_setor(nome_setor):
    """Regressão nos 200 setores: cada dimensão OU gera um cenário válido,
    OU recusa com ScdError (nunca uma exceção não tratada)."""
    fn = obter_gerador(nome_setor)
    tabelas = fn(300, DATA_INICIO, DATA_FIM)
    for dim_nome in [t for t in tabelas if t.startswith("Dim")]:
        try:
            resultado = gerar_cenario_scd(tabelas, dim_nome, n_mudancas=5, seed=1)
            assert len(resultado["gabarito"]) > 0
            assert len(resultado["scd_tipo2"]) == len(tabelas[dim_nome]) + len(resultado["gabarito"])
        except ScdError:
            pass  # recusa esperada e tratada — não é uma falha
