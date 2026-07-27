"""
ui/automatizar_bi.py: Aba "Automatizar BI".

Permite ao usuário enviar suas próprias planilhas (.csv/.xlsx), revisar e
ajustar o tipo de cada coluna, e gerar automaticamente TODAS as medidas
DAX que a tabela permite: agregações básicas, contagens, percentual de
participação e, quando houver coluna de data, Time Intelligence completo
(MoM/YoY/YTD/MTD), com uma tabela Calendario gerada automaticamente a
partir da própria data enviada. Não depende do padrão Fato/Dim dos
setores prontos: cada tabela enviada é tratada de forma independente.

Também repara automaticamente dois problemas comuns em arquivos
exportados de forma errada:
- CSV colado como texto corrido numa única coluna (sem separar de
  verdade em colunas), detectado quando o próprio nome da coluna já
  contém vírgulas.
- Acentuação quebrada (texto UTF-8 lido como Latin-1, tipo "CobranÃ§a"
  em vez de "Cobrança").
"""
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
    """Sugere o tipo mais provável da coluna, combinando dtype, nome e,
    quando a coluna já é texto (comum depois do reparo de coluna única),
    o conteúdo real dos valores."""
    if pd.api.types.is_bool_dtype(serie):
        return "Verdadeiro/Falso (booleano)"
    if pd.api.types.is_integer_dtype(serie):
        return "Número inteiro"
    if pd.api.types.is_float_dtype(serie):
        return "Número decimal"
    if pd.api.types.is_datetime64_any_dtype(serie):
        return "Data e hora"

    nome = str(serie.name).lower() if serie.name else ""

    # Checa "parece data" ANTES de "parece chave": uma coluna como
    # "id_data" bate nos dois padrões (começa com "id_" e contém "data"),
    # e o papel de data é o que importa pra habilitar o Time Intelligence
    # (mesma prioridade usada no motor principal dos 100 setores prontos).
    if any(p in nome for p in ["data", "date", "dt_"]):
        return "Data"
    if nome.startswith(("id_", "sk_", "cod_")) or nome in ("id", "codigo"):
        return "Chave/ID"

    # A coluna ainda é texto (object), mas pode ter vindo assim só por
    # causa do reparo de "coluna única" (planilha colada sem separar em
    # colunas de verdade). Fareja o CONTEÚDO antes de desistir e chamar
    # de Texto, senão toda coluna numérica reparada perderia a sugestão.
    amostra = serie.dropna().astype(str).str.strip()
    amostra = amostra[amostra != ""].head(50)
    if len(amostra):
        convertidos_num = pd.to_numeric(amostra, errors="coerce")
        if convertidos_num.notna().mean() >= 0.9:
            eh_inteiro = (convertidos_num.dropna() % 1 == 0).all()
            return "Número inteiro" if eh_inteiro else "Número decimal"

        convertidos_data = pd.to_datetime(amostra, errors="coerce", dayfirst=True)
        if convertidos_data.notna().mean() >= 0.9:
            return "Data"

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


def _corrigir_mojibake_texto(texto: str) -> str:
    """Corrige o erro clássico de acentuação (UTF-8 lido como Latin-1/cp1252,
    ex.: 'CobranÃ§a' em vez de 'Cobrança'). Se não for esse o problema,
    devolve o texto original sem alterar."""
    try:
        return texto.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
        return texto


def _corrigir_mojibake_df(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica a correção de acentuação em toda coluna de texto (e nos
    próprios nomes de coluna), só quando detectar o padrão quebrado
    (ex.: 'Ã' seguido de outro caractere)."""
    df = df.copy()
    df.columns = [
        _corrigir_mojibake_texto(c) if isinstance(c, str) and ("Ã" in c or "Â" in c) else c
        for c in df.columns
    ]
    for col in df.select_dtypes(include="object").columns:
        amostra = df[col].dropna().astype(str)
        if amostra.empty:
            continue
        tem_padrao_quebrado = amostra.str.contains("Ã.|Â.", regex=True).any()
        if not tem_padrao_quebrado:
            continue
        try:
            df.loc[amostra.index, col] = amostra.apply(_corrigir_mojibake_texto)
        except Exception:
            pass
    return df


def _reparar_coluna_unica(df: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    """
    Alguns arquivos chegam com todas as colunas despejadas como texto
    corrido numa única célula por linha (ex.: o cabeçalho vira o nome de
    uma única coluna "id,nome,valor", e cada linha vira a string
    "1,Ana,150.5"). Isso acontece quando o arquivo foi exportado sem
    separar de fato em colunas. Se detectar esse padrão (uma única
    coluna cujo próprio nome já contém vírgulas), tenta separar de volta
    usando vírgula como delimitador.

    Devolve (dataframe, foi_reparado).
    """
    if len(df.columns) != 1:
        return df, False

    nome_coluna = str(df.columns[0])
    if "," not in nome_coluna:
        return df, False

    novos_nomes = [c.strip() for c in nome_coluna.split(",")]
    try:
        dividido = df[df.columns[0]].astype(str).str.split(",", expand=True)
        if dividido.shape[1] != len(novos_nomes):
            return df, False  # não bate o número de colunas, não arrisca reparar
        dividido.columns = novos_nomes
        return dividido, True
    except Exception:
        return df, False


def _ler_arquivos(arquivos) -> tuple[dict, list]:
    """
    Lê os arquivos enviados (.csv/.xlsx, podendo ter várias abas) e
    devolve ({nome_tabela: DataFrame}, avisos_de_reparo).
    """
    tabelas = {}
    avisos = []
    for arquivo in arquivos:
        nome_base = arquivo.name.rsplit(".", 1)[0]
        if arquivo.name.lower().endswith(".csv"):
            try:
                df = pd.read_csv(arquivo)
            except Exception:
                arquivo.seek(0)
                df = pd.read_csv(arquivo, sep=";")  # tenta separador ao estilo BR
            df, reparado = _reparar_coluna_unica(df)
            if reparado:
                avisos.append(nome_base)
            tabelas[nome_base] = _corrigir_mojibake_df(df)
        else:
            planilhas = pd.read_excel(arquivo, sheet_name=None)
            for nome_aba, df in planilhas.items():
                chave = nome_base if len(planilhas) == 1 else f"{nome_base}_{nome_aba}"
                df, reparado = _reparar_coluna_unica(df)
                if reparado:
                    avisos.append(chave)
                tabelas[chave] = _corrigir_mojibake_df(df)
    return tabelas, avisos


def _coluna_data_da_tabela(df: pd.DataFrame, tipos: dict) -> str | None:
    """Acha a coluna de data de uma tabela: prioriza o que o usuário marcou
    como Data/Data e hora; se ninguém marcou, cai para qualquer coluna que
    já seja datetime de verdade."""
    for col, tipo in tipos.items():
        if tipo in ("Data", "Data e hora") and col in df.columns:
            return col
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
    return None


def _gerar_calendario(tabelas: dict, tipos_por_tabela: dict) -> tuple[pd.DataFrame | None, dict]:
    """
    Gera uma tabela Calendario cobrindo do menor ao maior valor de data
    encontrado em qualquer tabela enviada (olhando só as colunas marcadas
    como Data/Data e hora). Devolve (calendario, {tabela: coluna_de_data}).
    """
    colunas_data = {}
    series_datas = []
    for nome_tabela, df in tabelas.items():
        col = _coluna_data_da_tabela(df, tipos_por_tabela.get(nome_tabela, {}))
        if col:
            colunas_data[nome_tabela] = col
            validas = df[col].dropna()
            if len(validas):
                series_datas.append(validas)

    if not series_datas:
        return None, {}

    todas = pd.concat(series_datas)
    data_min, data_max = todas.min(), todas.max()
    if pd.isna(data_min) or pd.isna(data_max):
        return None, {}

    calendario = pd.DataFrame({"Data": pd.date_range(data_min, data_max, freq="D")})
    calendario["Ano"] = calendario["Data"].dt.year
    calendario["Mes"] = calendario["Data"].dt.month
    calendario["MesAno"] = calendario["Data"].dt.strftime("%m/%Y")
    return calendario, colunas_data


def _gerar_medidas_genericas(tabelas: dict, tipos_por_tabela: dict, tem_calendario: dict) -> dict:
    """
    Gera a bateria COMPLETA de medidas DAX possíveis para cada tabela
    enviada: agregações básicas, contagens, percentual de participação e,
    quando a tabela tiver coluna de data (e a Calendario existir), Time
    Intelligence completo (MoM/YoY/YTD/MTD), o mesmo menu de medidas
    usado nos 100 setores prontos, só que sem exigir o padrão Fato/Dim.
    """
    resultado = {}
    for nome_tabela, df in tabelas.items():
        tipos = tipos_por_tabela.get(nome_tabela, {})
        col_data = tem_calendario.get(nome_tabela)
        medidas = {
            "🧮 Agregações Básicas": [],
            "🔢 Contagens": [],
            "📊 Percentual de Participação": [],
            "📅 Time Intelligence (MoM / YoY / YTD / MTD)": [],
        }

        medidas["🔢 Contagens"].append({
            "nome": "Qtde de Registros",
            "formula": f"Qtde de Registros = COUNTROWS('{nome_tabela}')",
            "descricao": f"Quantidade de linhas da tabela '{nome_tabela}' no contexto atual.",
        })

        colunas_numericas = []
        for col in df.columns:
            tipo = tipos.get(col, "Detectar automaticamente")
            eh_numerica_automatica = (
                tipo == "Detectar automaticamente"
                and pd.api.types.is_numeric_dtype(df[col])
                and not pd.api.types.is_bool_dtype(df[col])
            )

            if tipo == "Chave/ID":
                titulo = _titulo(col)
                medidas["🔢 Contagens"].append({
                    "nome": f"Qtde Distinta de {titulo}",
                    "formula": f"Qtde Distinta de {titulo} = DISTINCTCOUNT('{nome_tabela}'[{col}])",
                    "descricao": f"Número de valores distintos de '{col}' presentes na tabela.",
                })

            elif tipo in ("Número inteiro", "Número decimal") or eh_numerica_automatica:
                colunas_numericas.append(col)
                titulo = _titulo(col)
                medidas["🧮 Agregações Básicas"].extend([
                    {"nome": f"Total {titulo}", "formula": f"Total {titulo} = SUM('{nome_tabela}'[{col}])",
                     "descricao": f"Soma de '{nome_tabela}'[{col}] no contexto de filtro atual."},
                    {"nome": f"Média {titulo}", "formula": f"Média {titulo} = AVERAGE('{nome_tabela}'[{col}])",
                     "descricao": f"Média de '{nome_tabela}'[{col}] no contexto de filtro atual."},
                    {"nome": f"Mínimo {titulo}", "formula": f"Mínimo {titulo} = MIN('{nome_tabela}'[{col}])",
                     "descricao": f"Menor valor de '{nome_tabela}'[{col}] no contexto atual."},
                    {"nome": f"Máximo {titulo}", "formula": f"Máximo {titulo} = MAX('{nome_tabela}'[{col}])",
                     "descricao": f"Maior valor de '{nome_tabela}'[{col}] no contexto atual."},
                ])
                medidas["📊 Percentual de Participação"].append({
                    "nome": f"% do Total {titulo}",
                    "formula": (
                        f"% do Total {titulo} =\n"
                        f"DIVIDE(\n"
                        f"    [Total {titulo}],\n"
                        f"    CALCULATE([Total {titulo}], ALL('{nome_tabela}'))\n"
                        f")"
                    ),
                    "descricao": f"Participação percentual do contexto atual sobre o total geral de {titulo}.",
                })

            elif tipo in ("Data", "Data e hora"):
                titulo = _titulo(col)
                medidas["🧮 Agregações Básicas"].extend([
                    {"nome": f"{titulo} Mínima", "formula": f"{titulo} Mínima = MIN('{nome_tabela}'[{col}])",
                     "descricao": f"Data mais antiga em '{nome_tabela}'[{col}]."},
                    {"nome": f"{titulo} Máxima", "formula": f"{titulo} Máxima = MAX('{nome_tabela}'[{col}])",
                     "descricao": f"Data mais recente em '{nome_tabela}'[{col}]."},
                ])

        # ---- Time Intelligence: só quando há coluna de data + Calendario ----
        if col_data and colunas_numericas:
            for col in colunas_numericas:
                titulo = _titulo(col)
                medidas["📅 Time Intelligence (MoM / YoY / YTD / MTD)"].extend([
                    {
                        "nome": f"{titulo} Mês Anterior",
                        "formula": (
                            f"{titulo} Mês Anterior =\n"
                            f"CALCULATE(\n"
                            f"    [Total {titulo}],\n"
                            f"    DATEADD(Calendario[Data], -1, MONTH)\n"
                            f")"
                        ),
                        "descricao": f"Valor de {titulo} no mesmo período do mês anterior.",
                    },
                    {
                        "nome": f"{titulo} %MoM",
                        "formula": (
                            f"{titulo} %MoM =\n"
                            f"DIVIDE(\n"
                            f"    [Total {titulo}] - [{titulo} Mês Anterior],\n"
                            f"    [{titulo} Mês Anterior]\n"
                            f")"
                        ),
                        "descricao": f"Variação percentual de {titulo} frente ao mês anterior (Month over Month).",
                    },
                    {
                        "nome": f"{titulo} Ano Anterior",
                        "formula": (
                            f"{titulo} Ano Anterior =\n"
                            f"CALCULATE(\n"
                            f"    [Total {titulo}],\n"
                            f"    SAMEPERIODLASTYEAR(Calendario[Data])\n"
                            f")"
                        ),
                        "descricao": f"Valor de {titulo} no mesmo período do ano anterior.",
                    },
                    {
                        "nome": f"{titulo} %YoY",
                        "formula": (
                            f"{titulo} %YoY =\n"
                            f"DIVIDE(\n"
                            f"    [Total {titulo}] - [{titulo} Ano Anterior],\n"
                            f"    [{titulo} Ano Anterior]\n"
                            f")"
                        ),
                        "descricao": f"Variação percentual de {titulo} frente ao mesmo período do ano anterior (Year over Year).",
                    },
                    {
                        "nome": f"{titulo} Acumulado no Ano (YTD)",
                        "formula": f"{titulo} Acumulado no Ano (YTD) = TOTALYTD([Total {titulo}], Calendario[Data])",
                        "descricao": f"Acumulado de {titulo} desde o início do ano até a data em contexto.",
                    },
                    {
                        "nome": f"{titulo} Acumulado no Mês (MTD)",
                        "formula": f"{titulo} Acumulado no Mês (MTD) = TOTALMTD([Total {titulo}], Calendario[Data])",
                        "descricao": f"Acumulado de {titulo} desde o início do mês até a data em contexto.",
                    },
                ])

        resultado[nome_tabela] = {k: v for k, v in medidas.items() if v}
    return resultado


def _montar_texto_dax(medidas_por_tabela: dict, tem_calendario: bool) -> str:
    linhas = ["-- Medidas DAX geradas automaticamente pelo Automatizar BI", ""]
    if tem_calendario:
        linhas.append(
            "-- Este pacote inclui uma tabela Calendario. No Power BI, relacione "
            "Calendario[Data] com a coluna de data de cada tabela antes de usar "
            "as medidas de Time Intelligence (MoM/YoY/YTD/MTD)."
        )
        linhas.append("")
    for nome_tabela, categorias in medidas_por_tabela.items():
        linhas.append(f"-- ===== Tabela: {nome_tabela} =====")
        for categoria, lista in categorias.items():
            linhas.append(f"-- {categoria}")
            for m in lista:
                linhas.append(m["formula"])
                linhas.append("")
        linhas.append("")
    return "\n".join(linhas)


def render_automatizar_bi() -> None:
    st.markdown("## 🤖 Automatizar BI")
    st.caption(
        "Envie suas planilhas (.csv ou .xlsx). Depois de revisar o tipo de cada coluna, "
        "geramos automaticamente todas as medidas DAX que a tabela permite, incluindo "
        "Time Intelligence quando houver coluna de data."
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
        tabelas, avisos_reparo = _ler_arquivos(arquivos)
    except Exception as e:
        st.error(f"Não foi possível ler um dos arquivos enviados. Detalhe: {e}")
        return

    if not tabelas:
        st.warning("Nenhuma tabela foi identificada nos arquivos enviados.")
        return

    st.success(f"{len(tabelas)} tabela(s) carregada(s): {', '.join(tabelas.keys())}")

    if avisos_reparo:
        st.warning(
            f"⚠️ As tabelas **{', '.join(avisos_reparo)}** chegaram com todas as colunas "
            f"despejadas numa única coluna de texto (sinal de que o arquivo original não "
            f"foi separado em colunas de verdade). Elas foram reconstruídas automaticamente "
            f"usando vírgula como separador. Confira o preview abaixo pra garantir que ficou certo."
        )

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
        calendario, colunas_data = _gerar_calendario(tabelas_convertidas, tipos_por_tabela)
        medidas_por_tabela = _gerar_medidas_genericas(tabelas_convertidas, tipos_por_tabela, colunas_data)

        st.session_state["automatizar_bi_medidas"] = medidas_por_tabela
        st.session_state["automatizar_bi_calendario"] = calendario

    if "automatizar_bi_medidas" in st.session_state:
        medidas_por_tabela = st.session_state["automatizar_bi_medidas"]
        calendario = st.session_state.get("automatizar_bi_calendario")
        total_medidas = sum(len(lista) for cats in medidas_por_tabela.values() for lista in cats.values())
        st.markdown(f"### 🧮 Medidas DAX sugeridas ({total_medidas})")

        if calendario is not None:
            st.info(
                f"📅 Uma tabela **Calendario** foi gerada automaticamente "
                f"({calendario['Data'].min().strftime('%d/%m/%Y')} a {calendario['Data'].max().strftime('%d/%m/%Y')}), "
                f"habilitando as medidas de Time Intelligence. No Power BI, relacione "
                f"`Calendario[Data]` com a coluna de data de cada tabela."
            )

        for nome_tabela, categorias in medidas_por_tabela.items():
            st.markdown(f"**{nome_tabela}**")
            for categoria, lista in categorias.items():
                with st.expander(f"{categoria} ({len(lista)})"):
                    for m in lista:
                        st.code(m["formula"], language="dax")

        texto_dax = _montar_texto_dax(medidas_por_tabela, calendario is not None)

        if calendario is not None:
            col_dl1, col_dl2 = st.columns(2)
        else:
            col_dl1, col_dl2 = st.columns(1)[0], None

        with col_dl1:
            st.download_button(
                "📥 Baixar todas as medidas (.txt)",
                data=texto_dax.encode("utf-8"),
                file_name="medidas_automatizar_bi.txt",
                mime="text/plain",
                use_container_width=True,
            )
        if calendario is not None and col_dl2 is not None:
            with col_dl2:
                st.download_button(
                    "📥 Baixar tabela Calendario (.csv)",
                    data=calendario.to_csv(index=False).encode("utf-8"),
                    file_name="Calendario.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
