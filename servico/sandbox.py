"""servico/sandbox.py: exemplos do DAX Sandbox (extraído de ui/dax_sandbox.py)."""
from generators.relacionamentos import detectar_fk as _detectar_fk


_EXEMPLOS_GENERICOS = [
    "Total = SUM({fato}[{medida}])",
    "Média = AVERAGE({fato}[{medida}])",
    "Qtd Registros = COUNTROWS({fato})",
    "Ticket Médio = DIVIDE(SUM({fato}[{medida}]), COUNTROWS({fato}))",
]


def _exemplo_com_calculate(fato: str, medida: str, dim: str, coluna_dim: str, valor: str) -> str:
    return f'Total Filtrado = CALCULATE(SUM({fato}[{medida}]), {dim}[{coluna_dim}]="{valor}")'


def _achar_medida_e_exemplos(tabelas: dict) -> tuple[str, str, list[str]]:
    fato_tables = [t for t in tabelas if t.startswith("Fato")]
    if not fato_tables:
        return "", "", []
    fato = fato_tables[0]
    df = tabelas[fato]
    numericas = [c for c in df.columns if df[c].dtype.kind in "if" and not c.lower().startswith(("id_", "sk_"))]
    if not numericas:
        return fato, "", []
    medida = numericas[0]
    exemplos = [e.format(fato=fato, medida=medida) for e in _EXEMPLOS_GENERICOS]

    dim_tables = [t for t in tabelas if t.startswith("Dim")]
    for dim in dim_tables:
        fk = _detectar_fk(fato, dim, tabelas)
        if not fk:
            continue
        dim_df = tabelas[dim]
        cats = [
            c for c in dim_df.columns
            if (dim_df[c].dtype == object or str(dim_df[c].dtype) == "str")
            and 2 <= dim_df[c].nunique() <= 20
        ]
        if cats:
            coluna_dim = cats[0]
            valor = str(dim_df[coluna_dim].iloc[0])
            exemplos.append(_exemplo_com_calculate(fato, medida, dim, coluna_dim, valor))
            break

    return fato, medida, exemplos


