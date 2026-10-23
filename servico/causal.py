"""servico/causal.py: cenário causal (lógica pura, extraída de ui/dados_causais.py)."""
import numpy as np
import pandas as pd


def _detectar_coluna_data(df: pd.DataFrame) -> str | None:
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
    for col in df.columns:
        if any(p in col.lower() for p in ["data", "date", "dt_"]):
            return col
    return None


def _colunas_numericas_validas(df: pd.DataFrame) -> list:
    """
    Colunas candidatas a causa/efeito: numéricas de verdade (excluindo
    chave/FK, tipo id_*/sk_*) mais colunas booleanas (tratadas como
    taxa 0/1, ex.: 'usou_personal'), o que amplia bastante quais setores
    têm pelo menos 2 métricas utilizáveis nesse cenário.
    """
    numericas = df.select_dtypes(include="number").columns.tolist()
    booleanas = df.select_dtypes(include="bool").columns.tolist()
    candidatas = [c for c in numericas if not c.lower().startswith(("id_", "sk_"))]
    candidatas += booleanas
    return candidatas


def gerar_cenario_causal_do_setor(
    df_fato: pd.DataFrame, col_data: str, col_causa: str, col_efeito_label: str,
    direcao: int, tem_confundidor: bool, efeito_pct: float, defasagem: int,
    ruido_pct: float, nome_setor: str, fato_nome: str, seed: int | None = None,
) -> tuple[pd.DataFrame, dict]:
    """
    Monta a série temporal real (agregada por semana) da coluna de causa
    escolhida, a partir da base já gerada, e calcula um efeito SIMULADO
    causalmente a partir dela (com defasagem, confundidor e ruído). O
    gabarito documenta exatamente o que é real e o que é simulado.
    """
    rng = np.random.default_rng(seed)

    df = df_fato[[col_data, col_causa]].copy()
    df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
    df = df.dropna(subset=[col_data])
    if df.empty:
        raise ValueError("Não foi possível interpretar a coluna de data dessa tabela fato.")

    serie = df.set_index(col_data).resample("W")[col_causa].sum().reset_index()
    serie.columns = ["data", "causa"]
    n_periodos = len(serie)
    if n_periodos < 6:
        raise ValueError(
            "Poucos períodos pra montar uma série temporal causal (gere a base com um "
            "período mais longo, pelo menos 6 semanas)."
        )

    causa = serie["causa"].values.astype(float)
    desvio = causa.std()
    causa_normalizada = (causa - causa.mean()) / (desvio if desvio else 1)

    confundidor = None
    if tem_confundidor:
        confundidor = 1 + 0.15 * np.sin(2 * np.pi * np.arange(n_periodos) / 52)

    media_abs = float(np.abs(causa).mean())
    base_efeito = media_abs * 4.0 if media_abs else 100.0

    efeito = np.full(n_periodos, base_efeito)
    for t in range(n_periodos):
        t_ref = max(0, t - defasagem)
        contrib_causal = direcao * (efeito_pct / 100) * base_efeito * causa_normalizada[t_ref]
        contrib_confundidor = (confundidor[t] - 1) * base_efeito * 0.5 if confundidor is not None else 0.0
        efeito[t] = base_efeito + contrib_causal + contrib_confundidor

    ruido_efeito = rng.normal(0, base_efeito * (ruido_pct / 100), n_periodos)
    efeito = np.clip(efeito + ruido_efeito, 0, None)

    nome_col_efeito = f"{col_efeito_label} (simulado)"
    df_final = pd.DataFrame({
        "data": serie["data"],
        col_causa: causa.round(2),
        nome_col_efeito: efeito.round(2),
    })
    if confundidor is not None:
        df_final["Índice de Sazonalidade"] = confundidor.round(4)

    gabarito = {
        "setor": nome_setor,
        "tabela_fato": fato_nome,
        "coluna_causa": f"{col_causa} (valores REAIS da base gerada, agregados por semana)",
        "coluna_efeito": f"{nome_col_efeito} (valores 100% SIMULADOS pela fórmula causal)",
        "relacao_causal": f"{col_causa} {'AUMENTA' if direcao > 0 else 'REDUZ'} {col_efeito_label}",
        "forca_do_efeito_pct": efeito_pct,
        "defasagem_em_semanas": defasagem,
        "tem_confundidor": tem_confundidor,
        "intensidade_do_ruido_pct": ruido_pct,
        "aviso": (
            f"A coluna '{col_causa}' usa os valores reais agregados por semana da base de "
            f"'{nome_setor}' que você gerou. Já a coluna '{nome_col_efeito}' não usa os "
            f"valores reais de '{col_efeito_label}' na base original, ela é inteiramente "
            f"recalculada pela fórmula causal, pra garantir que o gabarito seja confiável."
        ),
    }
    return df_final, gabarito


def montar_gabarito_causal_txt(gabarito: dict) -> str:
    linhas = ["GABARITO CAUSAL (não olhe antes de tentar sua própria análise)", ""]
    for chave, valor in gabarito.items():
        linhas.append(f"{chave}: {valor}")
    return "\n".join(linhas)

