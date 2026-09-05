---
name: bi-data-generator-pro
description: Use this skill for ANY task on the BI Data Generator PRO project — repo RodrigoAiosa/bi_data_generator, deployed at ai-bidatagenerator.streamlit.app. Trigger whenever the user mentions "BI Data Generator", pastes that repo/app URL, asks to add/fix a sector generator, edit a tab, work with DAX/TMDL/SQL generation in this app, or commit/push to this repo. This skill exists specifically to avoid re-deriving the architecture, conventions, and known gotchas from scratch — read it BEFORE exploring the codebase.
---

# BI Data Generator PRO — conhecimento acumulado do projeto

Streamlit app que gera dados sintéticos de BI (modelo estrela) para praticar
Power BI/DAX/SQL. 200 setores de negócio, 10 abas, ~10.700 medidas DAX
geradas automaticamente. Sem nenhuma dependência de LLM/IA em nenhuma
funcionalidade — tudo é regra/heurística determinística (isso é uma escolha
de design deliberada, não uma limitação a "corrigir").

Este arquivo existe pra evitar redescobrir do zero, numa conversa nova, coisas
que já custaram bastante investigação numa sessão anterior. Leia isto **antes**
de explorar o código. Números concretos (contagem de setores, abas etc.) podem
ficar desatualizados — confirme rodando o código (comandos abaixo) em vez de
confiar cegamente neste arquivo pra esses valores específicos.

## Stack e ambiente

- Streamlit + pandas + numpy + faker + plotly + openpyxl + duckdb (dev/teste).
  **Não usa polars** (isso já foi um erro real encontrado na apresentação do
  projeto — não reintroduza).
- Sem nenhuma integração de LLM/IA (nem Anthropic, nem OpenAI). Qualquer
  funcionalidade de "linguagem natural" (ex.: Pergunte aos Dados) é motor de
  regex/heurística, não um modelo de linguagem. Não sugira "usar um LLM pra
  melhorar isso" sem que o usuário peça explicitamente — é uma decisão de
  design (app gratuito, sem custo de API, sem depender de terceiro pago).
- `requirements.txt` é a fonte da verdade de dependências reais.

## Arquitetura (onde fica cada coisa)

- `config.py` — `SETORES` é um dict **nome de exibição → nome do módulo em
  generators/ (string)**, carregado sob demanda (lazy-load, feito numa
  otimização de performance). **NUNCA chame `SETORES[nome](...)` direto** —
  isso vai falhar com `TypeError: 'str' object is not callable`. Use sempre:
  ```python
  from config import obter_gerador
  fn = obter_gerador(nome_do_setor)
  tabelas = fn(n_linhas, data_inicio, data_fim)
  ```
- `generators/<setor>.py` — um arquivo por setor (ou por grupo de setores
  relacionados), cada um com uma função `gerar_<setor>(n, start, end) -> dict[str, pd.DataFrame]`.
- `generators/medidas.py` — sugestão automática de medidas DAX por categoria.
- `generators/dax_engine.py` — motor que EXECUTA DAX de verdade contra os
  dados gerados (usado no DAX Sandbox e no Pergunte aos Dados). Suporta
  subconjunto pedagógico: SUM, AVERAGE, MIN, MAX, COUNTROWS, DISTINCTCOUNT,
  DIVIDE, CALCULATE com filtro.
- `generators/qa_engine.py` — motor de perguntas em português → DAX (aba
  "Pergunte aos Dados"). É reconhecimento de padrões, não NLU de verdade.
  Tem barreiras explícitas contra responder previsão/causa (fora do escopo).
- `generators/sql_generator.py` — DDL/INSERT/script completo, 3 dialetos.
- `generators/relatorios_gerenciais.py` — Views SQL de KPI/evolução/ranking.
- `generators/tmdl_generator.py` — gera texto TMDL no formato "createOrReplace"
  (pra colar no Tabular Editor) — **tudo vem indentado 1 nível a mais** do
  que um `.tmdl` nativo de projeto PBIP exigiria. Se for reaproveitar essas
  funções pra outro formato, precisa "dedentar" 1 tab de cada linha.
- `generators/auditor_modelo.py` — audita TMDL colado pelo usuário. Esse
  parser espera o MESMO formato "createOrReplace" de 2 níveis: `table X` em
  1 tab, `column`/`measure` em 2 tabs (não é o formato PBIP nativo de 1
  tab/2 tabs a partir da raiz — cuidado ao testar isso manualmente, é fácil
  errar a indentação e achar que o parser está quebrado quando na verdade é
  o texto de teste que está errado).
- `generators/carrossel_pbi.py` — lê páginas de um `.pbix` real (formato
  clássico `Report/Layout`, JSON em UTF-16LE) OU de um projeto `.pbip`/PBIR
  (pasta `Report/definition/pages/`), detecção automática dos dois formatos.
- `ui/<nome>.py` — um `render_<nome>()` por aba, chamado em `app.py`.
- `ui/cache_utils.py` — cache compartilhado entre abas (`gerar_bruto_com_cache`).
  DAX Sandbox, Pergunte aos Dados e a aba principal reaproveitam o MESMO
  objeto gerado quando setor+volume+datas batem (confirmado com `is`, não só
  valores iguais).
- `styles/css.py` — todo o CSS customizado num único lugar (`_CSS` triplo-aspas
  + `inject_css()`). Tema Power BI (fundo escuro `#121212`, amarelo `#F2C811`).
- `app.py` — monta as abas via `st.tabs(...)`, importa cada `render_*`.

## As 10 abas (nomes exatos usados no código, `key=` dos botões principais)

1. Gerador de Setores — `Gerar base agora`
2. Automatizar BI — upload de planilha própria
3. Simulador PL-300 — `key=None`, label `🎲 Sortear novo simulado`
4. Dados Causais — `🧬 Gerar cenário causal`
5. Formatar DAX — `key=btn_formatar_dax`, `text_area(key=formatar_dax_entrada)`
6. Formatar M — `key=btn_formatar_m`, `text_area(key=formatar_m_entrada)`
7. Auditor de Modelo — `key=btn_auditar_modelo`, `text_area(key=auditor_tmdl_entrada)`
8. DAX Sandbox — `key=dax_sandbox_carregar` / `dax_sandbox_executar`. Setor
   vem da sidebar (não tem seletor próprio).
9. Pergunte aos Dados — `key=qa_carregar` / `qa_perguntar`. Setor também vem
   da sidebar. Sem LLM (ver acima).
10. Carrossel Power BI — ferramenta autônoma, não depende de setor gerado.

## Regra de ouro: nunca declare algo pronto sem testar de verdade

Esta é a lição mais cara desta base de código — praticamente todo bug real
encontrado nas últimas sessões só apareceu depois de EXECUTAR de verdade, não
de ler o código. Ler o código e "parecer certo" não é evidência suficiente.

- **Geração de dados**: rode `obter_gerador(nome)(n, start, end)` pra TODOS
  os 200 setores antes de considerar uma mudança segura, não só 1-2 exemplos.
- **SQL gerado**: não basta checar sintaxe — EXECUTE de verdade com DuckDB:
  ```python
  import duckdb
  con = duckdb.connect(':memory:')
  con.execute(sql)  # levanta exceção se o SQL estiver errado de verdade
  ```
- **UI do Streamlit**: use `streamlit.testing.v1.AppTest`, clique nos botões
  de verdade (`.click().run()`), leia `at.exception`, `at.success`,
  `at.error` — não assuma que "deveria funcionar".
- **CSS/mobile**: este sandbox tem Playwright com Chromium **já baixado e
  em cache** em `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` (não
  precisa rodar `playwright install`, que provavelmente falha por causa das
  restrições de rede do sandbox). Renderize de verdade e tire screenshot:
  ```python
  from playwright.sync_api import sync_playwright
  with sync_playwright() as p:
      browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
      page = browser.new_page(viewport={"width": 360, "height": 900})
      page.goto("file:///tmp/teste.html")
      page.screenshot(path="/tmp/out.png")
  ```
  Um bug de card sobrepondo no mobile só apareceu simulando zoom de
  acessibilidade (fonte ~130%) — no zoom padrão o CSS "parecia" correto.
- **PPTX**: sempre gere as imagens de cada slide alterado (LibreOffice →
  PDF → `pdftoppm`) e olhe de verdade antes de entregar. Um `str_replace`
  de texto que atravessa runs com formatações diferentes (ex.: marcador de
  bullet em negrito + texto normal) pode herdar a formatação errada — já
  aconteceu e só foi visto no render, não na leitura do XML.
- **Rodar o app inteiro**: sempre termine com boot real
  (`streamlit run app.py --server.headless true` + `curl` pra HTTP 200) e
  regressão dos 200 setores antes de considerar uma mudança pronta.

## Armadilhas específicas já corrigidas (não reintroduzir)

- **Detecção de relacionamento (FK)**: existem ~4 implementações parecidas
  (`ui/dax_sandbox.py:_detectar_fk`, `generators/dax_engine.py:_detectar_fk`,
  `generators/relatorios_gerenciais.py:_detectar_fks_para_dims`,
  `generators/qa_engine.py:_achar_dimensao`). Todas devem **priorizar nome
  EXATO da coluna-chave** (ex.: `id_profissional` na Fato == `id_profissional`
  PK da Dim) antes de cair na heurística de sufixo-por-nome-de-tabela — o
  nome da tabela pode não ter nada a ver com o nome da própria coluna-chave
  (ex.: `DimEquipe` identificada por `id_profissional`, não por `id_equipe`).
  Excluir sempre a própria PK da tabela de origem da lista de colunas
  candidatas a FK (evita falso positivo Dim-contra-Dim).
- **Esquema floco de neve**: dimensões que só se conectam indiretamente
  (via outra dimensão, ex. `DimTalhao.id_fazenda` → `DimFazenda`) precisam
  de detecção Dim-para-Dim separada da detecção Fato-para-Dim — já
  implementada no diagrama (`ui/dax_sandbox.py:_montar_dot`), desenhada com
  linha pontilhada pra diferenciar de relação direta.
- **Diagrama Graphviz**: conecte SEMPRE em nível de tabela
  (`"A" -> "B"`), nunca em porta de coluna específica
  (`"A":"col":e -> "B":"col2":w`) — porta de coluna fazia a linha atravessar
  por dentro do cartão quando os nós ficavam empilhados na mesma coluna do
  layout. `splines="ortho"` com `rankdir="LR"` pode travar o Graphviz
  (`maze.c` assertion) em alguns grafos reais — `rankdir="TB"` é estável.
- **Cards CSS com altura fixa**: qualquer elemento `position:absolute` dentro
  de um container de altura fixa PRECISA de `overflow:hidden`, senão o
  conteúdo vaza visualmente pro elemento vizinho em zoom/fonte maior (não
  aparece no zoom padrão — só testando zoom maior é que aparece).
  `overflow-wrap: break-word` também é necessário pra palavra longa não
  vazar pro lado antes do corte vertical.
- **Formato numérico brasileiro**: `pd.to_numeric()` não entende
  `"R$ 1.234,56"` (vírgula decimal, ponto de milhar) — converte pra NaN
  silenciosamente, sem erro. Sempre normalizar (remover símbolo de moeda,
  trocar separador de milhar/decimal) antes de converter. Ver
  `ui/automatizar_bi.py:_normalizar_numero_br`.
- **Fuso horário**: `datetime.now()` sem timezone pega o horário do
  SERVIDOR (Streamlit Cloud roda em UTC), não o do Brasil. Usar sempre
  `datetime.now(ZoneInfo("America/Sao_Paulo"))` em qualquer timestamp
  mostrado ao usuário (`tzdata` já está no requirements.txt).
- **Pergunte aos Dados — nunca "chutar"**: o motor tem barreiras explícitas
  pra recusar perguntas de previsão/causa, medidas sem relação genuína, e
  avisa quando um período mencionado não existe nos dados — em vez de
  responder algo plausível mas errado. Ao estender esse motor, mantenha essa
  postura: prefira recusar com mensagem clara a arriscar uma resposta errada.

## Fluxo de trabalho git com o usuário

O usuário não usa Claude Code para tudo — parte do trabalho é feita aqui,
via chat, com o usuário colando um token do GitHub (fine-grained, escopo só
nesse repo, Contents read/write) a cada push. Nesse caso:

```bash
git remote set-url origin https://<TOKEN>@github.com/RodrigoAiosa/bi_data_generator.git
git push origin main
git remote set-url origin https://github.com/RodrigoAiosa/bi_data_generator.git  # remover o token IMEDIATAMENTE depois
```

Nunca deixe o token no remote depois do push. Se o usuário disser "usa o
mesmo token" numa mesma conversa, reutilize sem pedir de novo — mas cada
conversa nova não tem esse token (não persiste entre sessões).

O usuário também tem o Claude Code configurado localmente nessa máquina
(autenticado via `gh auth login`, sem precisar de token nenhum) — se ele
disser que vai usar o Claude Code pra alguma tarefa, não é preciso pedir
token, ele mesmo faz o push por lá.

## Antes de fechar qualquer tarefa

1. Testar de verdade (ver seção "regra de ouro" acima) — nunca só ler o código.
2. Regressão dos 200 setores (`obter_gerador` + geração, sem exceção).
3. Boot real do app (HTTP 200).
4. Commit com mensagem detalhada (o que foi encontrado, causa raiz, o que
   foi testado e como) — as mensagens de commit deste projeto documentam o
   processo de investigação, não só o resultado.
5. Perguntar se o usuário quer fazer push agora (ele decide o momento).
