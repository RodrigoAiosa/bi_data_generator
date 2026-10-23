"""servico/anomalias.py: injeção de anomalias (sem dependência de UI)."""
import random

import numpy as np
import pandas as pd


def _fmt_num_br(v, decimals=2):
    """Formata número no padrão brasileiro: ponto como milhar, vírgula como decimal."""
    s = f"{v:,.{decimals}f}"
    return s.translate(str.maketrans({",": "\x00", ".": ","})).replace("\x00", ".")


def _injetar_anomalias(tabelas: dict[str, pd.DataFrame]) -> tuple[dict[str, pd.DataFrame], list[dict]]:
    """
    Injeta 4 tipos de anomalias nos dados para prática de análise de causa raiz:
      1. Spike de churn / cancelamentos em um mês aleatório
      2. Produto / item com margem negativa
      3. Sazonalidade extrema (queda abrupta num trimestre)
      4. Outliers de valor (registros com valores 10 a 30x acima da média)

    Retorna as tabelas modificadas e o gabarito: uma lista com o que foi
    alterado exatamente, para quem ensina conferir se a análise do aluno
    encontrou o problema certo.
    """
    tabelas = {k: v.copy() for k, v in tabelas.items()}
    gabarito: list[dict] = []

    fato_key = next((k for k in tabelas if k.startswith("Fato")), None)
    if fato_key is None:
        return tabelas, gabarito

    fato = tabelas[fato_key]
    num_cols = fato.select_dtypes(include="number").columns.tolist()
    date_cols = [c for c in fato.columns if "data" in c.lower() or "date" in c.lower()]
    bool_cols = [c for c in fato.columns if fato[c].dtype == bool]
    val_col   = next((c for c in num_cols if any(k in c for k in ["valor","receita","preco","total","mrr"])), num_cols[0] if num_cols else None)

    # Garante dtype float na coluna de valor: evita erro do pandas ao atribuir
    # multiplicadores fracionários (sazonalidade/outliers) numa coluna int64.
    if val_col is not None and pd.api.types.is_integer_dtype(fato[val_col]):
        fato[val_col] = fato[val_col].astype(float)

    # 1. Spike de churn / cancelamentos num mês aleatório
    if bool_cols and date_cols:
        try:
            date_col = date_cols[0]
            fato[date_col] = pd.to_datetime(fato[date_col], errors="coerce")
            meses = fato[date_col].dt.month.dropna().unique()
            mes_spike = random.choice(list(meses))
            mask = fato[date_col].dt.month == mes_spike
            fato.loc[mask, bool_cols[0]] = True   # força cancelamento/churn no mês
            gabarito.append({
                "tipo": "Spike de Cancelamento/Churn",
                "localizacao": f"Mês {int(mes_spike)} (coluna '{bool_cols[0]}', tabela {fato_key})",
                "detalhe": f"Todos os registros de {fato_key} no mês {int(mes_spike)} tiveram '{bool_cols[0]}' forçado para True. {int(mask.sum())} linhas afetadas.",
            })
        except Exception:
            pass

    # 2. Produto / categoria com margem negativa
    margem_cols = [c for c in num_cols if "margem" in c or "lucro" in c or "desconto" in c]
    if margem_cols:
        if pd.api.types.is_integer_dtype(fato[margem_cols[0]]):
            fato[margem_cols[0]] = fato[margem_cols[0]].astype(float)
        n_neg = max(1, int(len(fato) * 0.04))
        idx = fato.sample(n_neg).index
        media_original = fato[margem_cols[0]].mean()
        fato.loc[idx, margem_cols[0]] = -abs(media_original) * np.random.uniform(1.1, 2.5, n_neg)
        gabarito.append({
            "tipo": "Margem/Lucro Negativo Artificial",
            "localizacao": f"{n_neg} registros aleatórios (coluna '{margem_cols[0]}', tabela {fato_key})",
            "detalhe": f"Valores de '{margem_cols[0]}' foram forçados para negativo (entre 1,1x e 2,5x a média original, em módulo). Média original antes da alteração: {_fmt_num_br(media_original)}.",
        })

    # 3. Sazonalidade extrema: queda de 70% num trimestre aleatório
    if val_col and date_cols:
        try:
            date_col = date_cols[0]
            trimestres = fato[date_col].dt.quarter.dropna().unique()
            trim_queda = random.choice(list(trimestres))
            mask = fato[date_col].dt.quarter == trim_queda
            fato.loc[mask, val_col] = fato.loc[mask, val_col] * 0.30
            gabarito.append({
                "tipo": "Queda Artificial de Sazonalidade",
                "localizacao": f"Trimestre Q{int(trim_queda)} (coluna '{val_col}', tabela {fato_key})",
                "detalhe": f"Valores de '{val_col}' no Q{int(trim_queda)} foram reduzidos para 30% do valor original (queda de 70%). {int(mask.sum())} linhas afetadas.",
            })
        except Exception:
            pass

    # 4. Outliers de valor (1% dos registros com valores extremos)
    if val_col:
        n_out = max(1, int(len(fato) * 0.01))
        idx = fato.sample(n_out).index
        media = fato[val_col].mean()
        fato.loc[idx, val_col] = media * np.random.uniform(10, 30, n_out)
        gabarito.append({
            "tipo": "Outliers de Valor",
            "localizacao": f"{n_out} registros aleatórios (coluna '{val_col}', tabela {fato_key})",
            "detalhe": f"Valores foram multiplicados por um fator entre 10x e 30x a média. Média original antes da alteração: {_fmt_num_br(media)}.",
        })

    tabelas[fato_key] = fato
    return tabelas, gabarito


# ── Cache da geração bruta (pré-anomalia/deriva) ────────────────────────────
# Implementação em ui/cache_utils.py — compartilhada com o botão de SQL da
