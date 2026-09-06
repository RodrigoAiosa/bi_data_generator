"""
tests/conftest.py — fixtures compartilhadas entre todos os testes.
"""
import datetime
import sys
from pathlib import Path

import pytest

# Garante que o pacote do projeto seja importável independente de onde o
# pytest é chamado (localmente ou no GitHub Actions).
RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

DATA_INICIO = datetime.date(2024, 1, 1)
DATA_FIM = datetime.date(2024, 12, 31)


@pytest.fixture(scope="session")
def nomes_setores() -> list[str]:
    from config import SETORES
    return list(SETORES)


def pytest_generate_tests(metafunc):
    """Parametriza automaticamente qualquer teste que peça o fixture
    'nome_setor' — roda uma vez por setor (200x), mostrando no relatório
    exatamente QUAL setor falhou, não um bloco genérico."""
    if "nome_setor" in metafunc.fixturenames:
        from config import SETORES
        metafunc.parametrize("nome_setor", list(SETORES))
