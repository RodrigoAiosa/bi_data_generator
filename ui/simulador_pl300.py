"""
ui/simulador_pl300.py: Aba "Simulador PL-300".

Quiz de prática com perguntas 100% originais (escritas para este projeto,
nunca reproduzidas de provas reais), organizadas nos 4 domínios oficiais
do exame PL-300 (Microsoft Certified: Power BI Data Analyst Associate):
Preparar os dados, Modelar os dados, Visualizar e analisar os dados, e
Gerenciar e proteger o Power BI.

Este simulador NÃO substitui o Practice Assessment oficial da Microsoft
(link exibido na tela) e não contém nenhum conteúdo de "exam dump" ou
vazamento de prova real.
"""
import random

import streamlit as st

LINK_PRACTICE_OFICIAL = (
    "https://learn.microsoft.com/en-us/credentials/certifications/data-analyst-associate/"
    "practice/assessment?assessment-type=practice&assessmentId=48&practice-assessment-type=certification"
)
LINK_GUIA_ESTUDO = "https://aka.ms/pl300-StudyGuide"
LINK_CERTIFICACAO = "https://learn.microsoft.com/en-us/credentials/certifications/data-analyst-associate/"

DOMINIOS = [
    "Preparar os dados",
    "Modelar os dados",
    "Visualizar e analisar os dados",
    "Gerenciar e proteger o Power BI",
]


def _banco_perguntas_fixas() -> list:
    """Perguntas originais que não dependem de nenhuma base gerada."""
    return [
        # ── Preparar os dados ────────────────────────────────────────────
        {
            "dominio": "Preparar os dados",
            "pergunta": "Qual etapa do Power Query você usaria para dividir uma coluna de texto em múltiplas colunas com base em um delimitador (ex.: vírgula)?",
            "opcoes": ["Dividir Coluna (Split Column)", "Mesclar Consultas (Merge Queries)", "Anexar Consultas (Append Queries)", "Agrupar Por (Group By)"],
            "correta": 0,
            "explicacao": "Dividir Coluna separa o conteúdo de uma coluna em várias, usando um delimitador ou uma posição de caractere.",
        },
        {
            "dominio": "Preparar os dados",
            "pergunta": "Você quer empilhar duas tabelas com a mesma estrutura de colunas (linhas de uma embaixo da outra). Qual operação do Power Query faz isso?",
            "opcoes": ["Mesclar Consultas (Merge Queries)", "Anexar Consultas (Append Queries)", "Dividir Coluna", "Dinamizar Coluna (Pivot Column)"],
            "correta": 1,
            "explicacao": "Anexar (Append) empilha linhas de tabelas com estrutura parecida; Mesclar (Merge) faz um JOIN, combinando colunas de tabelas diferentes.",
        },
        {
            "dominio": "Preparar os dados",
            "pergunta": "Uma coluna de valores monetários veio como texto, com 'R$' na frente (ex.: 'R$ 150,00'). Qual é o passo mais adequado no Power Query antes de usar essa coluna em uma medida?",
            "opcoes": ["Ignorar, o Power BI ajusta sozinho na hora da medida", "Usar Substituir Valores para remover o texto e depois mudar o tipo da coluna para Número", "Criar direto uma medida DAX somando o texto", "Excluir a coluna e recriar manualmente"],
            "correta": 1,
            "explicacao": "É preciso limpar o texto (remover 'R$', ajustar separador decimal) e só depois definir o tipo de dado correto da coluna, antes de usá-la em cálculos.",
        },
        {
            "dominio": "Preparar os dados",
            "pergunta": "Qual modo de conectividade consulta a fonte de dados a cada interação do relatório, sem importar uma cópia dos dados para o modelo?",
            "opcoes": ["Import", "DirectQuery", "Dataflow", "Dual sempre em modo Import"],
            "correta": 1,
            "explicacao": "No modo DirectQuery, o Power BI consulta a fonte em tempo real a cada interação, em vez de copiar os dados para dentro do modelo (como faz o modo Import).",
        },
        {
            "dominio": "Preparar os dados",
            "pergunta": "Você tem uma pasta com vários arquivos CSV, todos no mesmo formato, e quer aplicar a mesma limpeza automaticamente em cada um. Qual recurso do Power Query melhor resolve isso?",
            "opcoes": ["Uma medida DAX", "A opção 'From Folder' combinada com uma função personalizada", "Segmentação de dados (Slicer)", "Um bookmark"],
            "correta": 1,
            "explicacao": "'From Folder' lê todos os arquivos de uma pasta, e uma função personalizada (Custom Function) aplica a mesma transformação a cada um automaticamente.",
        },

        # ── Modelar os dados ─────────────────────────────────────────────
        {
            "dominio": "Modelar os dados",
            "pergunta": "No modelo estrela (star schema), qual é a direção recomendada do relacionamento entre uma tabela Fato e uma tabela Dimensão?",
            "opcoes": ["Muitos-para-um (Fato → Dimensão), filtro de sentido único", "Um-para-muitos (Dimensão → Fato), filtro de sentido duplo sempre", "Muitos-para-muitos, sempre", "Não deveria existir relacionamento direto"],
            "correta": 0,
            "explicacao": "O padrão do modelo estrela é a fato do lado 'muitos' se relacionando com a dimensão do lado 'um', com o filtro propagando da dimensão para a fato.",
        },
        {
            "dominio": "Modelar os dados",
            "pergunta": "Qual função DAX remove os filtros de uma tabela (mantendo o contexto de linha), útil para calcular o percentual de participação de uma categoria sobre o total geral?",
            "opcoes": ["FILTER", "ALL (dentro de um CALCULATE)", "RELATED", "VALUES"],
            "correta": 1,
            "explicacao": "ALL() remove os filtros aplicados a uma tabela ou coluna; combinada com CALCULATE, é a base clássica do cálculo de '% do total'.",
        },
        {
            "dominio": "Modelar os dados",
            "pergunta": "Você quer trazer o nome do cliente (que está na dimensão Cliente) para uma coluna calculada dentro da tabela Fato, aproveitando um relacionamento já existente. Qual função usa?",
            "opcoes": ["RELATED", "CALCULATE", "SUMX", "ALLEXCEPT"],
            "correta": 0,
            "explicacao": "RELATED busca um valor de uma tabela relacionada (do lado 'um') diretamente no contexto de linha da tabela atual, aproveitando o relacionamento do modelo.",
        },
        {
            "dominio": "Modelar os dados",
            "pergunta": "Existe uma tabela Calendario marcada como 'Date Table' no modelo. Qual função DAX calcula o valor do mesmo período do ano anterior?",
            "opcoes": ["SAMEPERIODLASTYEAR", "EARLIER", "ALLSELECTED", "RANKX"],
            "correta": 0,
            "explicacao": "SAMEPERIODLASTYEAR desloca o contexto de datas para o mesmo período um ano antes, sendo a base das medidas clássicas de Year over Year (YoY).",
        },
        {
            "dominio": "Modelar os dados",
            "pergunta": "Duas tabelas Fato compartilham a mesma tabela Dimensão, e o Power BI recusa um relacionamento direto entre as duas Fatos, acusando 'caminhos ambíguos'. Qual é a causa mais provável?",
            "opcoes": ["Falta de medida DAX nas duas tabelas", "Um ciclo/caminho redundante foi criado no modelo (mais de um caminho para os dados fluírem entre as tabelas)", "A tabela Fato não tem nenhuma coluna numérica", "Erro de sintaxe no Power Query"],
            "correta": 1,
            "explicacao": "Quando existe mais de um caminho de relacionamento ativo entre duas tabelas, o Power BI não sabe por qual caminho propagar o filtro e recusa a ambiguidade.",
        },
        {
            "dominio": "Modelar os dados",
            "pergunta": "O que é uma tabela Bridge (tabela ponte) em modelagem de dados, e quando ela é necessária?",
            "opcoes": ["É outro nome para a tabela calendário", "Resolve relacionamentos muitos-para-muitos entre duas tabelas", "Armazena só as medidas DAX do modelo", "É sempre a tabela principal do modelo estrela"],
            "correta": 1,
            "explicacao": "Uma tabela Bridge fica entre duas tabelas que têm uma relação muitos-para-muitos, quebrando essa relação em duas relações muitos-para-um mais simples de gerenciar.",
        },

        # ── Visualizar e analisar os dados ───────────────────────────────
        {
            "dominio": "Visualizar e analisar os dados",
            "pergunta": "Qual tipo de visual é mais indicado para comparar a evolução de uma métrica ao longo do tempo?",
            "opcoes": ["Gráfico de linhas", "Gráfico de pizza", "Cartão (Card)", "Medidor (Gauge)"],
            "correta": 0,
            "explicacao": "Gráficos de linha são o padrão para mostrar tendência e evolução ao longo de um eixo temporal contínuo.",
        },
        {
            "dominio": "Visualizar e analisar os dados",
            "pergunta": "O que a formatação condicional em uma tabela ou matriz do Power BI permite fazer?",
            "opcoes": ["Colorir células automaticamente com base no valor (ex.: vermelho para negativo)", "Criar uma nova medida DAX automaticamente", "Ordenar a tabela sozinha, sem interação do usuário", "Aplicar segurança em nível de linha"],
            "correta": 0,
            "explicacao": "A formatação condicional aplica cor de fundo, cor de fonte, barras de dados ou ícones a células com base em regras sobre o valor.",
        },
        {
            "dominio": "Visualizar e analisar os dados",
            "pergunta": "Ao clicar em uma barra de um gráfico, todos os outros visuais da página destacam automaticamente os dados relacionados. Como esse comportamento padrão é chamado?",
            "opcoes": ["Drill Through", "Cross-filtering / realce cruzado (highlighting)", "Bookmark", "Hierarquia de dados"],
            "correta": 1,
            "explicacao": "Esse é o comportamento padrão de cross-filtering/highlighting entre visuais de uma mesma página, ativado automaticamente.",
        },
        {
            "dominio": "Visualizar e analisar os dados",
            "pergunta": "Você quer que, ao clicar com o botão direito em um item de um gráfico, o usuário seja levado para uma página de detalhe já filtrada só por aquele item. Qual recurso usa?",
            "opcoes": ["Drill Through", "Slicer sincronizado", "Tooltip de página", "Grupo de visuais"],
            "correta": 0,
            "explicacao": "Drill Through leva o usuário a uma página de detalhe, já filtrada pelo contexto do item clicado na página de origem.",
        },
        {
            "dominio": "Visualizar e analisar os dados",
            "pergunta": "Qual recurso permite salvar um 'estado' específico de filtros e visuais de uma página, para montar uma navegação estilo apresentação (ex.: um botão 'Ver só 2024')?",
            "opcoes": ["Bookmark", "Drill Down", "Segmentação de dados (Slicer)", "Hierarquia"],
            "correta": 0,
            "explicacao": "Bookmarks capturam o estado atual da página (filtros aplicados, visuais visíveis) e podem ser reaplicados com um clique, útil para navegação guiada.",
        },

        # ── Gerenciar e proteger o Power BI ──────────────────────────────
        {
            "dominio": "Gerenciar e proteger o Power BI",
            "pergunta": "O que é RLS (Row-Level Security) no Power BI?",
            "opcoes": ["Uma forma de restringir quais linhas de dado cada usuário vê, com base em regras de segurança", "Um tipo especial de relacionamento entre tabelas", "Um tipo de medida DAX", "Um recurso de formatação condicional"],
            "correta": 0,
            "explicacao": "RLS define regras (geralmente com filtros DAX) que restringem quais linhas de dado cada usuário ou grupo consegue ver no mesmo relatório publicado.",
        },
        {
            "dominio": "Gerenciar e proteger o Power BI",
            "pergunta": "Qual componente é necessário para atualizar automaticamente (refresh agendado) um relatório que usa uma fonte de dados on-premises (dentro da rede da empresa)?",
            "opcoes": ["Gateway de dados On-premises", "DirectQuery", "Bookmark", "Sensitivity label"],
            "correta": 0,
            "explicacao": "O Gateway de dados On-premises é a ponte segura que permite ao serviço do Power BI, na nuvem, acessar fontes de dados que estão dentro da rede local da empresa.",
        },
        {
            "dominio": "Gerenciar e proteger o Power BI",
            "pergunta": "Qual papel de workspace do Power BI permite apenas visualizar os relatórios publicados, sem poder editá-los?",
            "opcoes": ["Visualizador (Viewer)", "Administrador (Admin)", "Colaborador (Contributor)", "Membro (Member)"],
            "correta": 0,
            "explicacao": "O papel Viewer só permite consumir (visualizar/interagir) o conteúdo do workspace, sem permissão de edição.",
        },
        {
            "dominio": "Gerenciar e proteger o Power BI",
            "pergunta": "O que são 'sensitivity labels' (rótulos de confidencialidade) no Power BI?",
            "opcoes": ["Classificações que ajudam a proteger e controlar o compartilhamento de dados sensíveis", "Nomes alternativos para medidas DAX", "Cores de um tema visual", "Um tipo de relacionamento entre tabelas"],
            "correta": 0,
            "explicacao": "Sensitivity labels (via Microsoft Purview Information Protection) classificam e ajudam a proteger relatórios e datasets que contenham dados sensíveis.",
        },
        {
            "dominio": "Gerenciar e proteger o Power BI",
            "pergunta": "Qual é a principal vantagem de configurar Incremental Refresh (atualização incremental) em uma tabela muito grande?",
            "opcoes": ["Atualiza só os dados novos ou alterados, em vez de recarregar a tabela inteira", "Faz o relatório carregar mais devagar de propósito", "Remove a necessidade de qualquer relacionamento no modelo", "Substitui completamente o Power Query"],
            "correta": 0,
            "explicacao": "Incremental Refresh atualiza apenas a fatia de dados nova/alterada (ex.: só o mês atual), reduzindo bastante o tempo de atualização de tabelas grandes.",
        },
    ]


def _banco_perguntas_contextuais() -> list:
    """
    Perguntas que usam a base recém-gerada (Gerador de Setores) como
    contexto, quando existir uma em st.session_state. Se não houver
    nenhuma base gerada ainda, usa um cenário genérico no lugar.
    """
    dados_gerados = st.session_state.get("ultima_geracao")
    if dados_gerados:
        nome_setor = dados_gerados["nome"]
        tabelas = dados_gerados["tabelas"]
        fato_key = next((k for k in tabelas if k.startswith("Fato")), None)
        if fato_key:
            df_fato = tabelas[fato_key]
            num_cols = df_fato.select_dtypes(include="number").columns.tolist()
            col_numerica = num_cols[0] if num_cols else "valor_total"
        else:
            fato_key, col_numerica = "sua tabela fato", "valor_total"
    else:
        nome_setor, fato_key, col_numerica = "Varejo", "FatoVendas", "valor_total"

    return [
        {
            "dominio": "Modelar os dados",
            "pergunta": (
                f"Na base de '{nome_setor}' que você gerou, a tabela '{fato_key}' tem uma coluna "
                f"'{col_numerica}'. Você quer uma medida que mostre a variação percentual desse valor "
                f"em relação ao mês anterior (%MoM). Qual combinação de funções DAX é a base correta?"
            ),
            "opcoes": [
                "DIVIDE([Total atual] - [Total do mês anterior via DATEADD], [Total do mês anterior via DATEADD])",
                "SUM da coluna direto, sem nenhuma outra função",
                "COUNTROWS da tabela inteira",
                "RELATED apontando para a própria tabela fato",
            ],
            "correta": 0,
            "explicacao": (
                "%MoM se calcula comparando o valor do período atual com o mesmo valor deslocado um mês "
                "para trás (normalmente via CALCULATE + DATEADD(Calendario[Data], -1, MONTH)), e usando "
                "DIVIDE para a variação percentual (evita erro de divisão por zero)."
            ),
        },
        {
            "dominio": "Preparar os dados",
            "pergunta": (
                f"Você recebeu a tabela '{fato_key}' em CSV e percebeu que a coluna de data veio como "
                f"texto no formato 'DD/MM/AAAA'. Qual é o passo correto no Power Query antes de usar "
                f"essa coluna numa relação com uma tabela calendário?"
            ),
            "opcoes": [
                "Mudar o tipo da coluna para Data, definindo a localidade correta (ex.: Português-Brasil) para o formato ser interpretado certo",
                "Deixar como texto mesmo, o relacionamento funciona igual",
                "Excluir a coluna de data",
                "Renomear a coluna, sem mudar o tipo",
            ],
            "correta": 0,
            "explicacao": (
                "Ao converter texto para Data, é importante informar a localidade certa quando o formato "
                "é ambíguo (ex.: '05/03/2024' pode ser 5 de março ou 3 de maio dependendo da região), "
                "senão o Power Query pode interpretar errado."
            ),
        },
        {
            "dominio": "Gerenciar e proteger o Power BI",
            "pergunta": (
                f"Você publicou o relatório de '{nome_setor}' e quer que cada gerente regional veja "
                f"só os dados da própria região na tabela '{fato_key}', sem duplicar o relatório. "
                f"Qual recurso resolve isso?"
            ),
            "opcoes": [
                "RLS (Row-Level Security), com uma regra de filtro baseada na região do usuário",
                "Criar uma cópia do relatório para cada região",
                "Um Bookmark por região",
                "Um Slicer visível só para alguns usuários"
            ],
            "correta": 0,
            "explicacao": "RLS permite manter um único relatório, restringindo o que cada usuário vê a partir de regras de segurança definidas no modelo.",
        },
    ]


def _montar_banco_perguntas() -> list:
    return _banco_perguntas_fixas() + _banco_perguntas_contextuais()


def render_simulador_pl300() -> None:
    st.markdown("## 🎓 Simulador de Certificação PL-300")
    st.caption(
        "Perguntas de prática 100% originais, escritas para este projeto e organizadas nos "
        "4 domínios oficiais do exame **PL-300 (Microsoft Certified: Power BI Data Analyst Associate)**. "
        "Este simulador não reproduz nem substitui o exame real."
    )

    with st.expander("📎 Fontes oficiais da Microsoft (recomendado usar junto)", expanded=False):
        st.markdown(f"- [Practice Assessment oficial (gratuito)]({LINK_PRACTICE_OFICIAL})")
        st.markdown(f"- [Guia de estudo oficial da prova]({LINK_GUIA_ESTUDO})")
        st.markdown(f"- [Página da certificação PL-300]({LINK_CERTIFICACAO})")

    if "ultima_geracao" in st.session_state:
        st.info(f"Algumas perguntas abaixo usam a base de **{st.session_state['ultima_geracao']['nome']}** que você gerou, como contexto.")
    else:
        st.caption("Gere uma base na aba 'Gerador de Setores' para ver perguntas usando os seus próprios dados como contexto.")

    n_perguntas = st.selectbox("Quantas perguntas no simulado?", [5, 10, 15, 20], index=1)

    if st.button("🎲 Sortear novo simulado", use_container_width=True):
        banco = _montar_banco_perguntas()
        random.shuffle(banco)
        st.session_state["pl300_perguntas"] = banco[:n_perguntas]
        st.session_state["pl300_respostas"] = {}
        st.session_state.pop("pl300_corrigido", None)

    if "pl300_perguntas" not in st.session_state:
        return

    perguntas = st.session_state["pl300_perguntas"]

    with st.form("form_pl300"):
        for i, p in enumerate(perguntas):
            st.markdown(f"**{i + 1}. [{p['dominio']}] {p['pergunta']}**")
            escolha = st.radio(
                "Escolha uma opção:", p["opcoes"], index=None,
                key=f"pl300_resposta_{i}", label_visibility="collapsed",
            )
            st.session_state["pl300_respostas"][i] = escolha
            st.markdown("")
        enviado = st.form_submit_button("✅ Corrigir simulado", use_container_width=True, type="primary")

    if enviado:
        st.session_state["pl300_corrigido"] = True

    if st.session_state.get("pl300_corrigido"):
        acertos = 0
        por_dominio = {d: [0, 0] for d in DOMINIOS}

        for i, p in enumerate(perguntas):
            resposta = st.session_state["pl300_respostas"].get(i)
            correta_texto = p["opcoes"][p["correta"]]
            acertou = resposta == correta_texto
            por_dominio[p["dominio"]][1] += 1
            if acertou:
                acertos += 1
                por_dominio[p["dominio"]][0] += 1

        total = len(perguntas)
        pct = (acertos / total * 100) if total else 0
        st.markdown(f"### 🏁 Resultado: {acertos}/{total} ({pct:.0f}%)")

        cols = st.columns(len(DOMINIOS))
        for col, dominio in zip(cols, DOMINIOS):
            acertos_d, total_d = por_dominio[dominio]
            with col:
                st.metric(dominio, f"{acertos_d}/{total_d}" if total_d else "-")

        st.markdown("### Revisão pergunta a pergunta")
        for i, p in enumerate(perguntas):
            resposta = st.session_state["pl300_respostas"].get(i)
            correta_texto = p["opcoes"][p["correta"]]
            acertou = resposta == correta_texto
            icone = "✅" if acertou else "❌"
            with st.expander(f"{icone} {i + 1}. [{p['dominio']}] {p['pergunta'][:70]}..."):
                st.markdown(f"**Sua resposta:** {resposta if resposta else '_(não respondida)_'}")
                st.markdown(f"**Resposta correta:** {correta_texto}")
                st.markdown(f"**Explicação:** {p['explicacao']}")
