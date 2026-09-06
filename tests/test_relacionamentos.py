"""
tests/test_relacionamentos.py

Testes do módulo único de detecção de FK (generators/relacionamentos.py).
Cada caso aqui corresponde a um bug REAL já encontrado e corrigido ao
longo do desenvolvimento deste projeto — existem pra nunca mais voltar.
"""
import pandas as pd

from generators.relacionamentos import detectar_fk, detectar_fks_para_dims, extrair_sufixo_chave


def test_prioriza_nome_exato_da_chave_sobre_nome_da_tabela():
    """Caso real: DimEquipe é identificada por id_profissional, um nome que
    não tem nada a ver com "equipe" — a detecção por sufixo de nome de
    tabela sozinha NUNCA acharia essa relação."""
    fato = pd.DataFrame({"id_projeto": [1], "id_profissional": [10]})
    dim = pd.DataFrame({"id_profissional": [10], "nome": ["Ana"]})
    tabelas = {"FatoProjeto": fato, "DimEquipe": dim}

    assert detectar_fk("FatoProjeto", "DimEquipe", tabelas) == ("id_profissional", "id_profissional")


def test_dimensao_com_papel_duplo_encontra_as_duas_colunas():
    """Caso real: FatoMigracao tem id_operadora_origem E id_operadora_destino,
    as duas apontando pra DimOperadora — as duas precisam ser encontradas,
    não só a primeira."""
    fato = pd.DataFrame({
        "id_migracao": [1],
        "id_operadora_origem": [1],
        "id_operadora_destino": [2],
    })
    dim = pd.DataFrame({"id_operadora": [1, 2], "nome": ["Claro", "Vivo"]})
    tabelas = {"FatoMigracao": fato, "DimOperadora": dim}

    resultado = detectar_fks_para_dims(fato, "FatoMigracao", tabelas)
    colunas_encontradas = {col for col, _, _ in resultado}

    assert "id_operadora_origem" in colunas_encontradas
    assert "id_operadora_destino" in colunas_encontradas
    assert len(resultado) == 2


def test_relacionamento_dimensao_para_dimensao_esquema_floco_de_neve():
    """Caso real: DimLote só se conecta a FatoProducao, mas DimGranja só se
    conecta INDIRETAMENTE, via DimLote.id_granja — detectar_fk() precisa
    achar essa relação Dim-para-Dim também, não só Fato-para-Dim."""
    dim_lote = pd.DataFrame({"id_lote": [1], "id_granja": [100]})
    dim_granja = pd.DataFrame({"id_granja": [100], "nome": ["Granja A"]})
    tabelas = {"DimLote": dim_lote, "DimGranja": dim_granja}

    assert detectar_fk("DimLote", "DimGranja", tabelas) == ("id_granja", "id_granja")


def test_nao_inventa_relacionamento_que_nao_existe():
    """Honestidade: se a Fato genuinamente não tem nenhuma coluna que bata
    com a Dim (nem por nome exato, nem por sufixo), devolve None — nunca
    "chuta" uma relação errada só pra dar uma resposta."""
    fato = pd.DataFrame({"id_venda": [1], "valor": [10.0]})
    dim_sem_relacao = pd.DataFrame({"id_produto_totalmente_alheio": [1], "nome": ["X"]})
    tabelas = {"FatoVenda": fato, "DimSemRelacao": dim_sem_relacao}

    assert detectar_fk("FatoVenda", "DimSemRelacao", tabelas) is None


def test_exclui_a_propria_pk_da_lista_de_candidatas_a_fk():
    """Evita que uma tabela ache relação consigo mesma ou com outra Dim só
    por coincidência de nome da PRÓPRIA chave primária."""
    dim_a = pd.DataFrame({"id_a": [1], "nome": ["A"]})
    dim_b = pd.DataFrame({"id_a": [1], "nome": ["B"]})  # nome de PK coincidentemente igual ao de dim_a
    tabelas = {"DimA": dim_a, "DimB": dim_b}

    # DimA não deveria "achar" relação com DimB só porque a PRÓPRIA pk de DimA
    # (id_a, a única coluna dela) tem o mesmo nome da pk de DimB — id_a é a
    # PK da PRÓPRIA DimA, não uma FK candidata.
    assert detectar_fk("DimA", "DimB", tabelas) is None


def test_extrair_sufixo_chave():
    assert extrair_sufixo_chave("id_profissional") == "profissional"
    assert extrair_sufixo_chave("sk_cliente") == "cliente"
    assert extrair_sufixo_chave("id_operadora_origem") == "operadora_origem"


def test_fallback_por_sufixo_ainda_funciona_quando_nao_ha_nome_exato():
    """Regressão: o caso mais simples (que já funcionava antes de qualquer
    correção) não pode quebrar com a unificação."""
    fato = pd.DataFrame({"id_venda": [1], "id_vendedor": [5]})
    dim = pd.DataFrame({"id_vend": [5], "nome": ["João"]})  # PK com nome ligeiramente diferente
    tabelas = {"FatoVenda": fato, "DimVendedor": dim}

    assert detectar_fk("FatoVenda", "DimVendedor", tabelas) == ("id_vendedor", "id_vend")
