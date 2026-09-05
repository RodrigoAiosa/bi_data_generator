---
name: dax-m-sql-tmdl
description: Use this skill for ANY work on the BI Data Generator PRO project (RodrigoAiosa/bi_data_generator) that touches DAX (generators/dax_engine.py, generators/medidas.py, ui/formatar_dax.py, ui/dax_sandbox.py, generators/qa_engine.py), Power Query M (generators/m_formatter.py, ui/formatar_m.py, generators/tmdl_generator.py's M partitions), TMDL (generators/tmdl_generator.py, generators/auditor_modelo.py), or SQL (generators/sql_generator.py, generators/relatorios_gerenciais.py). It documents the EXACT subset of each language the project actually supports/generates/audits — reading this avoids re-deriving these rules from the code each time. For general project architecture and known bugs, see the sibling skill bi-data-generator-pro — this skill is the language-level reference, that one is the app-level reference.
---

# DAX / M / SQL / TMDL — referência técnica do projeto

Este projeto não usa nenhuma biblioteca de parsing de DAX/M/SQL de verdade —
tudo é regex e heurística escritas à mão, cobrindo deliberadamente um
SUBCONJUNTO pedagógico de cada linguagem (o suficiente pra ensinar/praticar,
não um parser completo). Ao alterar qualquer um desses motores, o primeiro
passo é sempre confirmar o subconjunto atual rodando o código — este arquivo
documenta o estado no momento em que foi escrito, mas pode ter mudado.

## DAX — `generators/dax_engine.py` (motor que EXECUTA DAX de verdade)

Usado pelo DAX Sandbox e pelo Pergunte aos Dados. Funções suportadas:

```python
_FUNCOES_AGREGACAO = {"SUM", "AVERAGE", "MIN", "MAX"}
_FUNCOES_CONHECIDAS = _FUNCOES_AGREGACAO | {"COUNTROWS", "DISTINCTCOUNT", "DIVIDE", "CALCULATE"}
```
Mais operadores aritméticos (`+ - * /`) fora de função. Qualquer outra função
DAX (RANKX, ALLEXCEPT, FILTER como função standalone, SWITCH, IF, variáveis
`VAR/RETURN`, time intelligence nativo como SAMEPERIODLASTYEAR) **não é
suportada** por este motor — se o pedido for adicionar uma dessas, é
extensão nova, não bug.

**Sintaxe de filtro do CALCULATE** (regex `_FILTRO_RE`):
```
Tabela[Coluna] operador valor
```
- `operador` aceito: `= == <> != > < >= <=`
- `valor` pode ser string entre aspas (`"Loja"`), número (`2020`), ou texto
  sem aspas (tratado como string mesmo assim)
- Múltiplos filtros: `CALCULATE(expr, Tabela1[Col]="X", Tabela2[Col]=2020)`
- **Não suporta** filtro por expressão complexa (`Tabela[Col] IN {...}`,
  `FILTER(Tabela, ...)`, comparação entre duas colunas). Só
  `Coluna operador valor-literal`.
- O motor só sabe fazer JOIN automático Fato↔Dim via coluna `id_*`/`sk_*`
  cujo nome bate com a PK da Dim (ver skill `bi-data-generator-pro`,
  seção de armadilhas de FK) — **não sabe** atravessar Fato→Dim→Dim
  (esquema floco de neve) nem fazer JOIN via coluna de data crua
  (por isso ranking por período/mês é resolvido em pandas puro em
  `qa_engine.py`, não delegado a este motor).

**Boa prática que o próprio motor não impõe, mas o Auditor cobra:** sempre
`DIVIDE(numerador, denominador)` em vez de `/` direto — ver seção Auditor.

## Formatar DAX — `generators/dax_formatter.py` (ui/formatar_dax.py)

Pega uma medida numa linha só e formata com indentação por nível de
parênteses (estilo parecido com o DAX Formatter público, mas mão-feito). Não
valida se a medida é executável — só formata o texto. Testar mudanças aqui
sempre olhando a SAÍDA renderizada (indentação visual), não só ausência de
exceção.

## TMDL — dois formatos DIFERENTES, não confundir

Isto já causou confusão real numa sessão anterior — leia com atenção antes
de testar qualquer coisa manualmente.

### Formato 1: PBIP nativo (pasta de projeto real do Power BI Desktop)
Usado por `generators/carrossel_pbi.py` ao ler `Report/definition/pages/`.
Estrutura de PASTAS, um arquivo por página/tabela, sem indentação de
`table`/`column` empilhada (cada conceito é o seu próprio arquivo).

### Formato 2: "createOrReplace" script (Tabular Editor Advanced Scripting)
Usado por `generators/tmdl_generator.py` (o que o app GERA pro usuário
colar no Tabular Editor) E por `generators/auditor_modelo.py` (o que ele
ESPERA receber colado pelo usuário). **Indentação de 2 níveis a partir da
tabela, com TAB de verdade, não espaço:**

```
\ttable FatoVendas
\t\tcolumn id_venda
\t\t\tdataType: int64
\t\t\tsummarizeBy: none
\t\t\tsourceColumn: id_venda

\t\tmeasure 'Total Vendas' = SUM(FatoVendas[valor])
\t\tmeasure TotalSemEspaco = SUM(FatoVendas[valor])
```

- `table` = **1 tab**. `column`/`measure` = **2 tabs** (filhos diretos da
  tabela, não 1 tab a mais que a tabela — é 2 tabs a partir da COLUNA 0,
  não relativo ao `table`).
- Nome da medida/coluna: aspas simples `'Nome Com Espaço'` são
  obrigatórias SE o nome tiver espaço/caractere especial; um nome sem
  espaço pode vir sem aspas (`measure TotalVendas = ...`). O parser do
  Auditor aceita os DOIS formatos — se estiver testando manualmente e o
  resultado vier com contagem zero, a causa mais provável é indentação
  errada (tabs errados) ou ter esquecido as aspas quando o nome tem espaço.
- Ao montar um TMDL de teste manualmente (ex.: `python -c "..."` num
  heredoc), use `\t` explícito, nunca espaços — o parser não aceita
  espaço no lugar de tab.

## Auditor de Modelo — `generators/auditor_modelo.py` (todas as checagens)

| Checagem | Severidade | O que detecta |
|---|---|---|
| `_checar_divisao_direta` | média | `/` direto em vez de `DIVIDE()`. Detecta mesmo com nome de tabela qualificando a coluna (`Tabela[a] / Tabela[b]`), ignora `/` dentro de string literal (datas tipo "25/12/2024") |
| `_checar_medidas_duplicadas` | — | Duas medidas com o mesmo nome |
| `_checar_medidas_sem_pasta` | baixa | Medida sem `displayFolder` definido |
| `_checar_colunas_calculadas_suspeitas` | média | Coluna calculada que poderia ser medida |
| `_checar_chaves_expostas` | baixa | Coluna `id_*`/`sk_*` sem `isHidden: true` |
| `_checar_nomenclatura_inconsistente` | baixa | Mistura de snake_case/Title Case/camelCase nos nomes de medida (só dispara com 4+ medidas e minoria relevante, pra não dar falso positivo em modelo pequeno) |

Nota geral começa em 100 e desconta por achado (ver `auditar_modelo()` pro
peso exato de cada severidade). Ao adicionar uma nova checagem, seguir o
mesmo formato de retorno (`severidade`, `categoria`, `medida`, `mensagem`,
`sugestao`) — a UI (`ui/auditor_modelo.py`) itera essa lista genericamente.

## Linguagem M — `generators/m_formatter.py` (ui/formatar_m.py)

Tokenizador próprio (`_tokenizar` → `_parsear_sequencia` → `_render_*`), não
usa nenhuma lib de parsing. Reconhece a estrutura `let <passo> = <expr>, ...
in <resultado>` e reformata cada passo numa linha própria, indentando por
nível de parênteses/colchetes. Não valida se o M é executável — só
reformata texto. Os passos de M gerados por `tmdl_generator.py`
(`Csv.Document`, `Table.PromoteHeaders`, `Table.TransformColumnTypes`) são
o padrão de referência de "M válido gerado por este projeto", úteis como
exemplo ao testar o formatador.

## SQL — `generators/sql_generator.py` (3 dialetos)

Dialetos aceitos (string exata): `"sqlserver"`, `"postgresql"`, `"mysql"`.

**Mapeamento base de tipo por dtype do pandas → SQL** (`_DTYPE_SQL`):

| dtype pandas | sqlserver | postgresql | mysql |
|---|---|---|---|
| int64 | BIGINT | BIGINT | BIGINT |
| int32 | INT | INTEGER | INT |
| float64 | DECIMAL(18,2) | NUMERIC(18,2) | DECIMAL(18,2) |
| float32 | DECIMAL(10,2) | NUMERIC(10,2) | DECIMAL(10,2) |
| bool | BIT | BOOLEAN | TINYINT(1) |
| object (texto) | NVARCHAR(255) | VARCHAR(255) | VARCHAR(255) |
| datetime64[ns] | DATETIME2 | TIMESTAMP | DATETIME |

**Overrides por nome de coluna** (aplicados ANTES do mapeamento base, nessa
ordem, cada um só dispara se o dtype real bater — nunca força tipo textual
virar numérico nem vice-versa):
1. Nome parece data (`data`, `dt_`, `_data` etc.) E dtype não é
   número/bool → `DATE`
2. Prefixo `id_`/`sk_` E dtype já é int → `INT`/`INTEGER`
3. Sufixo/substring `pct`/`percentual` → `DECIMAL(8,2)`/`NUMERIC(8,2)`
4. Substring de valor monetário (`valor`, `preco`, `custo`, `receita`,
   `lucro`, `orcamento`, `honorario`, `salario`, `taxa`, `frete`,
   `desconto`) E dtype numérico → `DECIMAL(18,2)`/`NUMERIC(18,2)`
5. `_VARCHAR_OVERRIDES` por substring de nome, só se dtype NÃO for
   numérico/bool (evita forçar VARCHAR numa coluna que já é int de
   verdade, ex.: `pontos_cnh` contém "cnh" mas é int64)

**Se for adicionar um novo override por nome**, sempre proteger com uma
checagem de dtype real primeiro — cada guarda de dtype acima existe porque
uma versão anterior sem ela quebrou o INSERT ou uma agregação (histórico
nos comentários do próprio arquivo). Colunas com nome enganoso já
encontradas: `sk_quarto`/`sk_rota` (texto, não INT, apesar do prefixo
`sk_`), `id_plano_atual` (era texto "Starter" antes de virar FK de verdade),
`modelo_receita`/`tipo_taxa`/`fonte_receita` (categorias de texto, não
valores monetários).

**Views de Relatórios Gerenciais** (`generators/relatorios_gerenciais.py`):
KPIs executivos, evolução mensal/anual, %MoM/%YoY, ranking top 20 por
dimensão — deduzidas automaticamente pra QUALQUER setor (usa a mesma
detecção de FK documentada na skill `bi-data-generator-pro`).

## Ao estender qualquer um desses motores

1. Primeiro rode o código real (não assuma) pra confirmar o comportamento
   atual — este arquivo pode estar desatualizado.
2. Teste com os 200 setores (`config.obter_gerador`), não só 1-2 exemplos —
   nomes de coluna "enganosos" (ver lista acima) só aparecem em setores
   específicos.
3. Pra SQL: execute de verdade com DuckDB (`con.execute(sql)`), não só
   confira sintaxe visualmente.
4. Pra DAX/TMDL: compare o resultado calculado com um `groupby`/filtro
   manual em pandas, não confie só em "não deu erro".
