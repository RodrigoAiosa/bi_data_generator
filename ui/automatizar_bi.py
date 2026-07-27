"""
ui/automatizar_bi.py: Aba "Automatizar BI".

Permite ao usuário enviar suas próprias planilhas (.csv/.xlsx), revisar e
ajustar o tipo de cada coluna, e gerar automaticamente todas as medidas
DAX que a tabela permite (agregações, contagens e percentual de
participação), sem depender do padrão Fato/Dim dos setores prontos.
"""
import io

import pandas as pd
import streamlit as st

from generators.medidas import _titulo

OPCOES_TIPO = [
    "Detectar automaticamente",
    "Texto",
    "Número inteiro",
    "Número decimal",
    "Data",
    "Data e hora",
    "Verdadeiro/Falso (booleano)",
    "Chave/ID",
]


def _sugerir_tipo(serie: pd.Series) -> str:
    """Sugere o tipo mais provável da coluna, combinando dtype e nome."""
    if pd.api.types.is_bool_dtype(serie):
        return "Verdadeiro/Falso (booleano)"
    if pd.api.types.is_integer_dtype(serie):
        return "Número inteiro"
    if pd.api.types.is_float_dtype(serie):
        return "Número decimal"
    if pd.api.types.is_datetime64_any_dtype(serie):
        return "Data e hora"

    nome = str(serie.name).lower() if serie.name else ""
    if any(p in nome for p in ["data", "date", "dt_"]):
        return "Data"
    if nome.startswith(("id_", "sk_", "cod_")) or nome in ("id", "codigo"):
        return "Chave/ID"
    return "Texto"


def _aplicar_tipos(df: pd.DataFrame, tipos: dict) -> pd.DataFrame:
    """Converte cada coluna do DataFrame conforme o tipo escolhido pelo usuário."""
    df = df.copy()
    for col, tipo in tipos.items():
        if col not in df.columns:
            continue
        try:
            if tipo == "Número inteiro":
                df[col] = pd.to_numeric(df[col], errors="coerce")
            elif tipo == "Número decimal":
                df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)
            elif tipo in ("Data", "Data e hora"):
                df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
            elif tipo == "Verdadeiro/Falso (booleano)":
                df[col] = df[col].astype(str).str.strip().str.lower().isin(
                    ["true", "1", "sim", "yes", "verdadeiro"]
                )
        except Exception:
            pass  # se a conversão falhar, mantém a coluna como veio
    return df


def _ler_arquivos(arquivos) -> dict:
    """Lê os arquivos enviados (.csv/.xlsx, podendo ter várias abas) e devolve {nome_tabela: DataFrame}."""
    tabelas = {}
    for arquivo in arquivos:
        nome_base = arquivo.name.rsplit(".", 1)[0]
        if arquivo.name.lower().endswith(".csv"):
            try:
                df = pd.read_csv(arquivo)
            except Exception:
                arquivo.seek(0)
                df = pd.read_csv(arquivo, sep=";")  # tenta separador ao estilo BR
            tabelas[nome_base] = df
        else:
            planilhas = pd.read_excel(arquivo, sheet_name=None)
            for nome_aba, df in planilhas.items():
                chave = nome_base if len(planilhas) == 1 else f"{nome_base}_{nome_aba}"
                tabelas[chave] = df
    return tabelas


def _gerar_medidas_genericas(tabelas: dict, tipos_por_tabela: dict) -> dict:
    """
    Gera a bateria de medidas DAX possíveis para cada tabela enviada,
    sem exigir o padrão Fato/Dim: cada tabela é tratada de forma
    independente (agregações nas colunas numéricas, contagem distinta
    nas colunas marcadas como Chave/ID, e percentual de participação).
    """
    resultado = {}
    for nome_tabela, df in tabelas.items():
        tipos = tipos_por_tabela.get(nome_tabela, {})
        medidas = {"Agregações Básicas": [], "Contagens": [], "Percentual de Participação": [], "Datas": []}

        medidas["Contagens"].append({
            "nome": "Qtde de Registros",
            "formula": f"COUNTROWS('{nome_tabela}')",
        })

        for col in df.columns:
            tipo = tipos.get(col, "Detectar automaticamente")
            eh_numerica_automatica = (
                tipo == "Detectar automaticamente"
                and pd.api.types.is_numeric_dtype(df[col])
                and not pd.api.types.is_bool_dtype(df[col])
            )

            if tipo == "Chave/ID":
                medidas["Contagens"].append({
                    "nome": f"Qtde Distinta de {_titulo(col)}",
                    "formula": f"DISTINCTCOUNT('{nome_tabela}'[{col}])",
                })

            elif tipo in ("Número inteiro", "Número decimal") or eh_numerica_automatica:
                titulo = _titulo(col)
                medidas["Agregações Básicas"].extend([
                    {"nome": f"Total {titulo}", "formula": f"SUM('{nome_tabela}'[{col}])"},
                    {"nome": f"Média {titulo}", "formula": f"AVERAGE('{nome_tabela}'[{col}])"},
                    {"nome": f"Mínimo {titulo}", "formula": f"MIN('{nome_tabela}'[{col}])"},
                    {"nome": f"Máximo {titulo}", "formula": f"MAX('{nome_tabela}'[{col}])"},
                ])
                medidas["Percentual de Participação"].append({
                    "nome": f"% do Total {titulo}",
                    "formula": (
                        f"DIVIDE([Total {titulo}], "
                        f"CALCULATE([Total {titulo}], ALL('{nome_tabela}')))"
                    ),
                })

            elif tipo in ("Data", "Data e hora"):
                titulo = _titulo(col)
                medidas["Datas"].extend([
                    {"nome": f"{titulo} Mínima", "formula": f"MIN('{nome_tabela}'[{col}])"},
                    {"nome": f"{titulo} Máxima", "formula": f"MAX('{nome_tabela}'[{col}])"},
                ])

        resultado[nome_tabela] = {k: v for k, v in medidas.items() if v}
    return resultado


def _montar_texto_dax(medidas_por_tabela: dict) -> str:
    linhas = ["-- Medidas DAX geradas automaticamente pelo Automatizar BI", ""]
    for nome_tabela, categorias in medidas_por_tabela.items():
        linhas.append(f"-- ===== Tabela: {nome_tabela} =====")
        for categoria, lista in categorias.items():
            linhas.append(f"-- {categoria}")
            for m in lista:
                linhas.append(f"{m['nome']} = {m['formula']}")
            linhas.append("")
    return "\n".join(linhas)


def render_automatizar_bi() -> None:
    st.markdown("## 🤖 Automatizar BI")
    st.caption(
        "Envie suas planilhas (.csv ou .xlsx). Depois de revisar o tipo de cada coluna, "
        "geramos automaticamente todas as medidas DAX que a tabela permite."
    )

    arquivos = st.file_uploader(
        "Envie uma ou mais planilhas",
        type=["csv", "xlsx"],
        accept_multiple_files=True,
        key="upload_automatizar_bi",
    )

    if not arquivos:
        st.info("Nenhum arquivo enviado ainda. Envie um .csv ou .xlsx para começar.")
        return

    try:
        tabelas = _ler_arquivos(arquivos)
    except Exception as e:
        st.error(f"Não foi possível ler um dos arquivos enviados. Detalhe: {e}")
        return

    if not tabelas:
        st.warning("Nenhuma tabela foi identificada nos arquivos enviados.")
        return

    st.success(f"{len(tabelas)} tabela(s) carregada(s): {', '.join(tabelas.keys())}")

    tipos_por_tabela = {}
    for nome_tabela, df in tabelas.items():
        n_linhas_fmt = f"{len(df):,}".replace(",", ".")
        with st.expander(f"📄 {nome_tabela}  ({n_linhas_fmt} linhas, {len(df.columns)} colunas)", expanded=False):
            st.dataframe(df.head(10), use_container_width=True)
            st.markdown("**Selecione o tipo de cada coluna:**")

            tipos_por_tabela[nome_tabela] = {}
            colunas_grid = st.columns(3)
            for i, col in enumerate(df.columns):
                sugestao = _sugerir_tipo(df[col])
                with colunas_grid[i % 3]:
                    tipo_escolhido = st.selectbox(
                        str(col), OPCOES_TIPO,
                        index=OPCOES_TIPO.index(sugestao) if sugestao in OPCOES_TIPO else 0,
                        key=f"tipo_{nome_tabela}_{col}",
                    )
                    tipos_por_tabela[nome_tabela][col] = tipo_escolhido

    if st.button("🧮 Gerar medidas DAX", type="primary", use_container_width=True, key="btn_gerar_medidas_automatizar"):
        tabelas_convertidas = {
            nome_tabela: _aplicar_tipos(df, tipos_por_tabela.get(nome_tabela, {}))
            for nome_tabela, df in tabelas.items()
        }
        medidas_por_tabela = _gerar_medidas_genericas(tabelas_convertidas, tipos_por_tabela)
        st.session_state["automatizar_bi_medidas"] = medidas_por_tabela

    if "automatizar_bi_medidas" in st.session_state:
        medidas_por_tabela = st.session_state["automatizar_bi_medidas"]
        total_medidas = sum(len(lista) for cats in medidas_por_tabela.values() for lista in cats.values())
        st.markdown(f"### 🧮 Medidas DAX sugeridas ({total_medidas})")

        for nome_tabela, categorias in medidas_por_tabela.items():
            st.markdown(f"**{nome_tabela}**")
            for categoria, lista in categorias.items():
                with st.expander(f"{categoria} ({len(lista)})"):
                    for m in lista:
                        st.code(f"{m['nome']} = {m['formula']}", language="dax")

        texto_dax = _montar_texto_dax(medidas_por_tabela)
        st.download_button(
            "📥 Baixar todas as medidas (.txt)",
            data=texto_dax.encode("utf-8"),
            file_name="medidas_automatizar_bi.txt",
            mime="text/plain",
            use_container_width=True,
        )
