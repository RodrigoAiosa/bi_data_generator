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
import os

import pandas as pd
import streamlit as st

from generators.medidas import _titulo
from generators.tmdl_generator import _tabela_tmdl, _e_chave, _coluna_e_data
from generators.helpers import to_zip
from ui.sugestao_proximo_passo import sugerir

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


def _nome_tabela_consolidada(nomes_originais: list) -> str:
    """
    Acha um nome pra tabela consolidada: usa o prefixo comum entre os
    nomes originais (ex.: 'Vendas_Jan', 'Vendas_Fev' -> 'Vendas'), ou cai
    pra um nome genérico se não achar prefixo comum útil.
    """
    prefixo = os.path.commonprefix(nomes_originais).rstrip("_- ")
    if len(prefixo) >= 3:
        return f"{prefixo}_Consolidado"
    return "TabelaConsolidada"


def _consolidar_planilhas_identicas(tabelas: dict) -> tuple[dict, list]:
    """
    Detecta tabelas com exatamente o MESMO CONJUNTO de colunas (mesmo
    nome, independente da ordem) e consolida todas elas numa única
    tabela fato, empilhando as linhas (pd.concat). É o caso comum de
    receber várias planilhas mensais/regionais com a mesma estrutura
    (ex.: 'Vendas_Jan', 'Vendas_Fev', 'Vendas_Mar').

    Tabelas sem nenhuma outra com o mesmo conjunto de colunas ficam
    exatamente como estavam, sem nenhuma mudança. Cada tabela
    consolidada ganha uma coluna extra '_planilha_origem', indicando de
    qual planilha original aquela linha veio, pra manter rastreabilidade.

    Devolve (novo_dict_de_tabelas, lista_de_avisos_pra_mostrar_na_tela).
    """
    grupos: dict = {}
    for nome, df in tabelas.items():
        assinatura = frozenset(df.columns)
        grupos.setdefault(assinatura, []).append((nome, df))

    resultado: dict = {}
    avisos: list = []
    nomes_usados: set = set(tabelas.keys())

    for lista in grupos.values():
        if len(lista) == 1:
            nome, df = lista[0]
            resultado[nome] = df
            continue

        nomes_originais = [nome for nome, _ in lista]
        nome_consolidado = _nome_tabela_consolidada(nomes_originais)
        if nome_consolidado in nomes_usados:
            sufixo = 2
            while f"{nome_consolidado}_{sufixo}" in nomes_usados:
                sufixo += 1
            nome_consolidado = f"{nome_consolidado}_{sufixo}"
        nomes_usados.add(nome_consolidado)

        partes = []
        for nome, df in lista:
            parte = df.copy()
            parte["_planilha_origem"] = nome
            partes.append(parte)
        df_consolidado = pd.concat(partes, ignore_index=True)

        resultado[nome_consolidado] = df_consolidado
        avisos.append(
            f"{len(lista)} planilhas com colunas idênticas ({', '.join(nomes_originais)}) "
            f"foram consolidadas automaticamente na tabela '{nome_consolidado}' "
            f"({len(df_consolidado)} linhas no total)."
        )

    return resultado, avisos


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

    Quando há mais de uma tabela, todo nome de medida recebe um sufixo
    "(Nome da Tabela)" pra evitar duas medidas com o mesmo nome (ex.:
    "Qtde de Registros" repetido em toda tabela), o que o Power BI/TMDL
    recusa ao importar (erro de "objects cannot be merged"). O sufixo
    também é propagado pras referências internas das medidas de Time
    Intelligence, que citam outras medidas pelo nome dentro da fórmula.
    """
    multi_tabela = len(tabelas) > 1
    resultado = {}
    for nome_tabela, df in tabelas.items():
        sufixo = f" ({nome_tabela})" if multi_tabela else ""
        tipos = tipos_por_tabela.get(nome_tabela, {})
        col_data = tem_calendario.get(nome_tabela)
        medidas = {
            "🧮 Agregações Básicas": [],
            "🔢 Contagens": [],
            "📊 Percentual de Participação": [],
            "📅 Time Intelligence (MoM / YoY / YTD / MTD)": [],
        }

        nome_registros = f"Qtde de Registros{sufixo}"
        medidas["🔢 Contagens"].append({
            "nome": nome_registros,
            "formula": f"{nome_registros} = COUNTROWS('{nome_tabela}')",
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
                nome_distinta = f"Qtde Distinta de {titulo}{sufixo}"
                medidas["🔢 Contagens"].append({
                    "nome": nome_distinta,
                    "formula": f"{nome_distinta} = DISTINCTCOUNT('{nome_tabela}'[{col}])",
                    "descricao": f"Número de valores distintos de '{col}' presentes na tabela.",
                })

            elif tipo in ("Número inteiro", "Número decimal") or eh_numerica_automatica:
                colunas_numericas.append(col)
                titulo = _titulo(col)
                nome_total = f"Total {titulo}{sufixo}"
                nome_media = f"Média {titulo}{sufixo}"
                nome_minimo = f"Mínimo {titulo}{sufixo}"
                nome_maximo = f"Máximo {titulo}{sufixo}"
                nome_pct = f"% do Total {titulo}{sufixo}"
                medidas["🧮 Agregações Básicas"].extend([
                    {"nome": nome_total, "titulo": titulo, "formula": f"{nome_total} = SUM('{nome_tabela}'[{col}])",
                     "descricao": f"Soma de '{nome_tabela}'[{col}] no contexto de filtro atual."},
                    {"nome": nome_media, "titulo": titulo, "formula": f"{nome_media} = AVERAGE('{nome_tabela}'[{col}])",
                     "descricao": f"Média de '{nome_tabela}'[{col}] no contexto de filtro atual."},
                    {"nome": nome_minimo, "titulo": titulo, "formula": f"{nome_minimo} = MIN('{nome_tabela}'[{col}])",
                     "descricao": f"Menor valor de '{nome_tabela}'[{col}] no contexto atual."},
                    {"nome": nome_maximo, "titulo": titulo, "formula": f"{nome_maximo} = MAX('{nome_tabela}'[{col}])",
                     "descricao": f"Maior valor de '{nome_tabela}'[{col}] no contexto atual."},
                ])
                medidas["📊 Percentual de Participação"].append({
                    "nome": nome_pct,
                    "titulo": titulo,
                    "formula": (
                        f"{nome_pct} =\n"
                        f"DIVIDE(\n"
                        f"    [{nome_total}],\n"
                        f"    CALCULATE([{nome_total}], ALL('{nome_tabela}'))\n"
                        f")"
                    ),
                    "descricao": f"Participação percentual do contexto atual sobre o total geral de {titulo}.",
                })

            elif tipo in ("Data", "Data e hora"):
                titulo = _titulo(col)
                nome_data_min = f"{titulo} Mínima{sufixo}"
                nome_data_max = f"{titulo} Máxima{sufixo}"
                medidas["🧮 Agregações Básicas"].extend([
                    {"nome": nome_data_min, "titulo": titulo, "formula": f"{nome_data_min} = MIN('{nome_tabela}'[{col}])",
                     "descricao": f"Data mais antiga em '{nome_tabela}'[{col}]."},
                    {"nome": nome_data_max, "titulo": titulo, "formula": f"{nome_data_max} = MAX('{nome_tabela}'[{col}])",
                     "descricao": f"Data mais recente em '{nome_tabela}'[{col}]."},
                ])

        # ---- Time Intelligence: só quando há coluna de data + Calendario ----
        if col_data and colunas_numericas:
            for col in colunas_numericas:
                titulo = _titulo(col)
                nome_total = f"Total {titulo}{sufixo}"
                nome_mes_anterior = f"{titulo} Mês Anterior{sufixo}"
                nome_mom = f"{titulo} %MoM{sufixo}"
                nome_ano_anterior = f"{titulo} Ano Anterior{sufixo}"
                nome_yoy = f"{titulo} %YoY{sufixo}"
                nome_ytd = f"{titulo} Acumulado no Ano (YTD){sufixo}"
                nome_mtd = f"{titulo} Acumulado no Mês (MTD){sufixo}"

                medidas["📅 Time Intelligence (MoM / YoY / YTD / MTD)"].extend([
                    {
                        "nome": nome_mes_anterior,
                        "titulo": titulo,
                        "formula": (
                            f"{nome_mes_anterior} =\n"
                            f"CALCULATE(\n"
                            f"    [{nome_total}],\n"
                            f"    DATEADD(Calendario[Data], -1, MONTH)\n"
                            f")"
                        ),
                        "descricao": f"Valor de {titulo} no mesmo período do mês anterior.",
                    },
                    {
                        "nome": nome_mom,
                        "titulo": titulo,
                        "formula": (
                            f"{nome_mom} =\n"
                            f"DIVIDE(\n"
                            f"    [{nome_total}] - [{nome_mes_anterior}],\n"
                            f"    [{nome_mes_anterior}]\n"
                            f")"
                        ),
                        "descricao": f"Variação percentual de {titulo} frente ao mês anterior (Month over Month).",
                    },
                    {
                        "nome": nome_ano_anterior,
                        "titulo": titulo,
                        "formula": (
                            f"{nome_ano_anterior} =\n"
                            f"CALCULATE(\n"
                            f"    [{nome_total}],\n"
                            f"    SAMEPERIODLASTYEAR(Calendario[Data])\n"
                            f")"
                        ),
                        "descricao": f"Valor de {titulo} no mesmo período do ano anterior.",
                    },
                    {
                        "nome": nome_yoy,
                        "titulo": titulo,
                        "formula": (
                            f"{nome_yoy} =\n"
                            f"DIVIDE(\n"
                            f"    [{nome_total}] - [{nome_ano_anterior}],\n"
                            f"    [{nome_ano_anterior}]\n"
                            f")"
                        ),
                        "descricao": f"Variação percentual de {titulo} frente ao mesmo período do ano anterior (Year over Year).",
                    },
                    {
                        "nome": nome_ytd,
                        "titulo": titulo,
                        "formula": f"{nome_ytd} = TOTALYTD([{nome_total}], Calendario[Data])",
                        "descricao": f"Acumulado de {titulo} desde o início do ano até a data em contexto.",
                    },
                    {
                        "nome": nome_mtd,
                        "titulo": titulo,
                        "formula": f"{nome_mtd} = TOTALMTD([{nome_total}], Calendario[Data])",
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


def _relacionamentos_genericos(tabelas: dict) -> list:
    """
    Versão do detector de relacionamentos do gerador principal, adaptada
    pro Automatizar BI: a lógica de FK->PK e de resolução de ciclo é a
    mesma, mas sem exigir que as tabelas se chamem "Fato*"/"dCalendario"
    (aqui não existe padrão Fato/Dim, cada tabela enviada é só uma
    tabela). O vínculo com o calendário procura a tabela "Calendario"
    (gerada automaticamente) e vale para qualquer tabela com coluna de
    data, não só as que "parecem fato".
    """
    pk_por_tabela = {nome: df.columns[0] for nome, df in tabelas.items() if len(df.columns)}
    dono_da_pk = {}
    for nome, pk in pk_por_tabela.items():
        dono_da_pk.setdefault(pk, nome)

    pai = {nome: nome for nome in tabelas}

    def _raiz(x):
        while pai[x] != x:
            pai[x] = pai[pai[x]]
            x = pai[x]
        return x

    def _fecha_ciclo(a, b):
        ra, rb = _raiz(a), _raiz(b)
        if ra == rb:
            return True
        pai[ra] = rb
        return False

    blocos = []
    contador = 1
    vistos = set()

    for nome_from, df in tabelas.items():
        pk_propria = df.columns[0] if len(df.columns) else None
        for col in df.columns:
            if not _e_chave(col):
                continue
            if col == pk_propria and nome_from == dono_da_pk.get(col):
                continue
            nome_to = dono_da_pk.get(col)
            if not nome_to or nome_to == nome_from:
                continue
            chave = (nome_from, col, nome_to)
            if chave in vistos:
                continue
            vistos.add(chave)

            inativo = _fecha_ciclo(nome_from, nome_to)

            linhas = [
                f"\trelationship rel_{contador}\n",
                f"\t\tfromColumn: {nome_from}.{col}\n",
                f"\t\ttoColumn: {nome_to}.{col}\n",
            ]
            if inativo:
                linhas.append("\t\tisActive: false\n")
            linhas.append("\n")
            blocos.append("".join(linhas))
            contador += 1

    # Vincula cada tabela com coluna de data à Calendario, usando o MESMO
    # union-find das chaves estrangeiras acima: se essa tabela já está
    # conectada à Calendario por algum caminho de FK (direto ou através de
    # outras tabelas), o novo link fica inativo. Isso garante que TODO o
    # grafo de relacionamentos (FKs + Calendario) forme uma única árvore,
    # sem nenhum caminho duplicado em lugar nenhum do modelo, mesmo em
    # esquemas onde fatos se referenciam entre si (não só fato->dimensão).
    if "Calendario" in tabelas:
        for nome_from, df in tabelas.items():
            if nome_from == "Calendario":
                continue
            candidatas = [c for c in df.columns if _coluna_e_data(c, df[c])]
            if not candidatas:
                continue
            col_data = candidatas[0]
            chave = (nome_from, col_data, "Calendario")
            if chave in vistos:
                continue
            vistos.add(chave)

            inativo = _fecha_ciclo(nome_from, "Calendario")

            linhas = [
                f"\trelationship rel_{contador}\n",
                f"\t\tfromColumn: {nome_from}.{col_data}\n",
                f"\t\ttoColumn: Calendario.Data\n",
            ]
            if inativo:
                linhas.append("\t\tisActive: false\n")
            linhas.append("\n")
            blocos.append("".join(linhas))
            contador += 1

    return blocos


def _medidas_tmdl_bloco(medidas_por_tabela: dict) -> str:
    """Monta a tabela 'Medidas' em formato TMDL a partir do dicionário de
    medidas já gerado pelo Automatizar BI (mesmo formato usado pelo
    gerador principal, para o arquivo abrir igual no Power BI/Tabular Editor).

    Como rede de segurança final, garante que nenhum nome de medida se
    repita: se por qualquer motivo duas medidas chegarem aqui com o mesmo
    nome, a segunda (e as seguintes) recebem um sufixo numérico (" (2)",
    " (3)"...), evitando o erro do Power BI/Tabular Editor de "TMDL
    objects cannot be merged" por nome de medida duplicado.
    """
    if not medidas_por_tabela:
        return ""

    nomes_usados: dict = {}
    linhas = ["\ttable Medidas\n\n"]
    for _nome_tabela, categorias in medidas_por_tabela.items():
        for categoria, lista in categorias.items():
            if not lista:
                continue
            pasta_categoria = categoria.split(" ", 1)[1] if " " in categoria else categoria
            for m in lista:
                nome = m["nome"]
                if nome in nomes_usados:
                    nomes_usados[nome] += 1
                    nome = f"{nome} ({nomes_usados[nome]})"
                else:
                    nomes_usados[nome] = 1

                formula = m["formula"]
                titulo = m.get("titulo")
                display_folder = f"{pasta_categoria}\\{titulo}" if titulo else pasta_categoria
                corpo = formula.split("=", 1)[1].strip() if "=" in formula else formula
                if "\n" in corpo:
                    linhas.append(f"\t\tmeasure '{nome}' = ```\n")
                    for l in corpo.split("\n"):
                        linhas.append(f"\t\t\t{l}\n")
                    linhas.append("\t\t\t```\n")
                else:
                    linhas.append(f"\t\tmeasure '{nome}' = {corpo}\n")
                linhas.append(f"\t\t\tdisplayFolder: {display_folder}\n\n")

    linhas.append("\t\tpartition Medidas = m\n")
    linhas.append("\t\t\tmode: import\n")
    linhas.append("\t\t\tsource =\n")
    linhas.append("\t\t\t\tlet\n")
    linhas.append(
        '\t\t\t\t    Origem = Table.FromRows(Json.Document(Binary.Decompress('
        'Binary.FromText("i44FAA==", BinaryEncoding.Base64), Compression.Deflate)), '
        'let _t = ((type nullable text) meta [Serialized.Text = true]) in type table '
        '[#"Coluna 1" = _t]),\n'
    )
    linhas.append('\t\t\t\t    #"Colunas Removidas" = Table.RemoveColumns(Origem,{"Coluna 1"})\n')
    linhas.append("\t\t\t\tin\n")
    linhas.append('\t\t\t\t    #"Colunas Removidas"\n')
    return "".join(linhas)


def _gerar_tmdl_automatizar(tabelas: dict, medidas_por_tabela: dict) -> str:
    """Monta o model.tmdl completo (parâmetro + tabelas + relacionamentos + medidas)
    pras tabelas enviadas no Automatizar BI, incluindo a Calendario se ela existir."""
    partes = [
        "createOrReplace\n\n"
        '\texpression CaminhoPasta = \n'
        '\t\t\t"C:\\Dados\\" meta [IsParameterQuery=true, List={"C:\\Dados\\"}, '
        'DefaultValue="C:\\Dados\\", Type="Text", IsParameterQueryRequired=true]\n'
        "\t\tannotation PBI_ResultType = Text\n\n"
    ]

    for nome_tabela, df in tabelas.items():
        partes.append(_tabela_tmdl(nome_tabela, df))

    for bloco in _relacionamentos_genericos(tabelas):
        partes.append(bloco)

    medidas_tmdl = _medidas_tmdl_bloco(medidas_por_tabela)
    if medidas_tmdl:
        partes.append(medidas_tmdl)

    return "".join(partes)


def _coluna_categorica_para_pergunta(df: pd.DataFrame, tipos: dict) -> str | None:
    """
    Acha uma coluna de texto com poucas categorias (boa pra 'agrupar por' /
    'qual categoria mais gera X'), ignorando Chave/ID e colunas de texto
    livre (com cardinalidade alta demais pra servir de categoria).
    """
    candidatas = []
    for col, tipo in tipos.items():
        if col not in df.columns:
            continue
        eh_texto = tipo == "Texto" or (tipo == "Detectar automaticamente" and df[col].dtype == "object")
        if not eh_texto:
            continue
        n_unicos = df[col].nunique(dropna=True)
        if 2 <= n_unicos <= 30:
            candidatas.append((col, n_unicos))
    if not candidatas:
        return None
    candidatas.sort(key=lambda x: x[1])  # prioriza a categoria com menos valores distintos
    return candidatas[0][0]


def _gerar_perguntas_negocio(tabelas: dict, tipos_por_tabela: dict, medidas_por_tabela: dict) -> dict:
    """
    Gera perguntas de negócio em linguagem natural a partir das colunas
    REAIS de cada tabela enviada (não uma história fictícia de setor,
    diferente do case de negócio do Gerador de Setores). Cada pergunta
    é ancorada numa medida que o próprio motor já gerou pra essa tabela.
    """
    perguntas_por_tabela = {}
    for nome_tabela, df in tabelas.items():
        tipos = tipos_por_tabela.get(nome_tabela, {})
        categorias_medidas = medidas_por_tabela.get(nome_tabela, {})

        agregacoes = categorias_medidas.get("🧮 Agregações Básicas", [])
        medida_total = next((m for m in agregacoes if m["nome"].startswith("Total ")), None)
        if not medida_total:
            continue  # tabela sem nenhuma coluna numérica agregável, não dá pra ancorar pergunta

        titulo_kpi = medida_total["nome"].replace("Total ", "", 1)
        tem_time_intel = bool(categorias_medidas.get("📅 Time Intelligence (MoM / YoY / YTD / MTD)"))
        col_categoria = _coluna_categorica_para_pergunta(df, tipos)

        perguntas = [f"Qual foi o Total de {titulo_kpi} no período analisado, na tabela '{nome_tabela}'?"]

        if col_categoria:
            titulo_cat = _titulo(col_categoria)
            perguntas.append(f"Qual {titulo_cat} apresenta o maior {titulo_kpi}?")
            perguntas.append(
                f"Existe algum {titulo_cat} responsável por mais da metade do {titulo_kpi} "
                f"total (Princípio de Pareto)?"
            )

        perguntas.append(f"Quais são os 5 registros com maior {titulo_kpi} na tabela '{nome_tabela}'?")

        if tem_time_intel:
            perguntas.append(
                f"Como o {titulo_kpi} evoluiu mês a mês? Houve algum mês com queda "
                f"relevante (%MoM negativo)?"
            )
            perguntas.append(
                f"Qual foi a variação de {titulo_kpi} frente ao mesmo período do ano anterior (%YoY)?"
            )

        perguntas_por_tabela[nome_tabela] = perguntas

    return perguntas_por_tabela


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
        st.error(
            "Não foi possível ler um dos arquivos enviados. Verifique se ele não está "
            "corrompido, vazio, protegido por senha, ou com uma extensão diferente do "
            "conteúdo real (por exemplo, um arquivo .csv salvo com extensão .xlsx), e "
            "tente novamente."
        )
        with st.expander("Detalhe técnico do erro"):
            st.caption(f"{type(e).__name__}: {e}")
        return

    if not tabelas:
        st.warning("Nenhuma tabela foi identificada nos arquivos enviados.")
        return

    tabelas, avisos_consolidacao = _consolidar_planilhas_identicas(tabelas)
    for aviso in avisos_consolidacao:
        st.info(f"🔗 {aviso}")

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
        perguntas_por_tabela = _gerar_perguntas_negocio(tabelas_convertidas, tipos_por_tabela, medidas_por_tabela)

        tabelas_para_tmdl = dict(tabelas_convertidas)
        if calendario is not None:
            tabelas_para_tmdl["Calendario"] = calendario
        tmdl_texto = _gerar_tmdl_automatizar(tabelas_para_tmdl, medidas_por_tabela)

        st.session_state["automatizar_bi_medidas"] = medidas_por_tabela
        st.session_state["automatizar_bi_perguntas"] = perguntas_por_tabela
        st.session_state["automatizar_bi_calendario"] = calendario
        st.session_state["automatizar_bi_tabelas_tmdl"] = tabelas_para_tmdl
        st.session_state["automatizar_bi_tmdl_texto"] = tmdl_texto

    if "automatizar_bi_medidas" in st.session_state:
        medidas_por_tabela = st.session_state["automatizar_bi_medidas"]
        perguntas_por_tabela = st.session_state.get("automatizar_bi_perguntas", {})
        calendario = st.session_state.get("automatizar_bi_calendario")

        if perguntas_por_tabela:
            st.markdown("### ❓ Perguntas de negócio pra explorar seus dados")
            st.caption(
                "Geradas a partir das colunas reais que você enviou (não são um exemplo fictício), "
                "cada uma ancorada numa medida que já foi gerada abaixo."
            )
            for nome_tabela, perguntas in perguntas_por_tabela.items():
                with st.expander(f"📄 {nome_tabela}", expanded=False):
                    for p in perguntas:
                        st.markdown(f"- {p}")

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
        tmdl_texto = st.session_state.get("automatizar_bi_tmdl_texto", "")
        tabelas_para_tmdl = st.session_state.get("automatizar_bi_tabelas_tmdl", {})

        col_dl1, col_dl2, col_dl3 = st.columns(3)

        with col_dl1:
            st.download_button(
                "📥 Baixar todas as medidas (.txt)",
                data=texto_dax.encode("utf-8"),
                file_name="medidas_automatizar_bi.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with col_dl2:
            if calendario is not None:
                st.download_button(
                    "📥 Baixar tabela Calendario (.csv)",
                    data=calendario.to_csv(index=False).encode("utf-8"),
                    file_name="Calendario.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        with col_dl3:
            if tmdl_texto and tabelas_para_tmdl:
                zip_bytes = to_zip(tabelas_para_tmdl, extra_files={"model.tmdl": tmdl_texto})
                st.download_button(
                    "📥 Baixar modelo completo (.zip)",
                    data=zip_bytes,
                    file_name="modelo_automatizar_bi.zip",
                    mime="application/zip",
                    use_container_width=True,
                )

        if tmdl_texto and tabelas_para_tmdl:
            st.caption(
                "O modelo completo traz os CSVs de cada tabela + model.tmdl (tabelas, "
                "relacionamentos e medidas), pronto para importar no Power BI/Tabular Editor."
            )

        sugerir(
            "Alguma das medidas geradas ficou com uma fórmula difícil de ler? "
            "Cola ela na aba **📐 Formatar DAX** e recebe formatada, com indentação e "
            "quebra de linha."
        )
