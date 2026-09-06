"""
tests/test_sql_generation.py

O SQL gerado precisa ser SQL de verdade — não basta "parecer certo",
precisa EXECUTAR sem erro. Roda de fato num banco DuckDB em memória.
"""
import duckdb

from config import obter_gerador
from generators.sql_generator import gerar_sql_completo
from tests.conftest import DATA_INICIO, DATA_FIM


def test_sql_completo_executa_no_duckdb(nome_setor):
    fn = obter_gerador(nome_setor)
    tabelas = fn(200, DATA_INICIO, DATA_FIM)

    sql = gerar_sql_completo(nome_setor, tabelas, dialect="postgresql")
    assert sql.strip(), f"{nome_setor}: gerar_sql_completo devolveu string vazia"

    con = duckdb.connect(":memory:")
    try:
        con.execute(sql)
    except Exception as e:
        raise AssertionError(f"{nome_setor}: SQL gerado falhou ao executar no DuckDB: {e}")
    finally:
        con.close()
