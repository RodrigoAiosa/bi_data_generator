"""
tests/test_geracao_setores.py

Regressão básica: TODOS os setores precisam gerar dados sem exceção, com
pelo menos uma tabela Fato e uma dCalendario. Isso sozinho já pega a
maioria dos bugs "sistêmicos" (import quebrado, erro de sintaxe, um
gerador novo mal copiado de outro).
"""
import pandas as pd

from config import obter_gerador
from tests.conftest import DATA_INICIO, DATA_FIM


def test_setor_gera_sem_excecao(nome_setor):
    fn = obter_gerador(nome_setor)
    tabelas = fn(300, DATA_INICIO, DATA_FIM)

    assert isinstance(tabelas, dict) and len(tabelas) > 0, f"{nome_setor}: não gerou nenhuma tabela"

    fato_tables = [t for t in tabelas if t.startswith("Fato")]
    assert fato_tables, f"{nome_setor}: nenhuma tabela Fato* encontrada"

    assert "dCalendario" in tabelas, f"{nome_setor}: falta a tabela dCalendario"

    for nome_tabela, df in tabelas.items():
        assert isinstance(df, pd.DataFrame), f"{nome_setor}/{nome_tabela}: não é um DataFrame"
        assert len(df) > 0, f"{nome_setor}/{nome_tabela}: DataFrame vazio"


def test_setor_com_volume_minimo_e_maximo(nome_setor):
    """Confere as duas pontas do slider de volume (100 e 100.000 linhas) —
    não só o meio do caminho, onde a maioria dos testes manuais roda."""
    fn = obter_gerador(nome_setor)

    tabelas_min = fn(100, DATA_INICIO, DATA_FIM)
    fato_min = [t for t in tabelas_min if t.startswith("Fato")][0]
    assert len(tabelas_min[fato_min]) > 0

    tabelas_max = fn(100_000, DATA_INICIO, DATA_FIM)
    fato_max = [t for t in tabelas_max if t.startswith("Fato")][0]
    assert len(tabelas_max[fato_max]) > 0
