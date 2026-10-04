-- =============================================================================
-- RELATÓRIO DE RASTREABILIDADE DA DIVULGAÇÃO  (BD_BIDATAGENERATOR / Supabase)
--
-- Responde: quem compartilhou o link, quem clicou, o que essas pessoas fizeram
-- no app e quantas viraram cadastro.
--
-- Fontes:
--   compartilhamentos            1 link (código) por pessoa cadastrada
--   cliques_compartilhamento     1 linha por sessão que abriu um link ?ref=
--   registros                    cadastros (dados pessoais — só o dono lê)
--   logs_uso                     sessões e ações (id_sessao liga o clique ao uso)
--
-- COMO USAR no SQL Editor do Supabase: o editor mostra só o resultado do
-- ÚLTIMO comando. Selecione UM bloco (de "-- [n]" até o ";") e clique em Run.
-- Somente leitura: nenhum comando altera dados.
--
-- Definições usadas nos blocos abaixo:
--   clique_valido      = sessão diferente do próprio divulgador (exclui o
--                        "autoclique": o divulgador abrindo o seu link)
--   novo_cadastro      = na sessão do clique houve clicou_cadastrar com sucesso
--   ja_era_cadastrado  = na sessão houve clicou_verificar_cadastro com sucesso
--   (quem já era cadastrado e só confirmou o e-mail NÃO conta como conversão)
-- =============================================================================


-- [0] BASE REUTILIZÁVEL ---------------------------------------------------------
-- View de apoio: 1 linha por clique, já com divulgador, visitante, perfil da
-- sessão (dispositivo/navegador/idioma) e as ações realizadas. Os blocos
-- seguintes consultam esta view. Rode este bloco UMA vez (é idempotente).
create or replace view public.vw_rastreio_detalhe
with (security_invoker = true) as
select
    c.id_clique,
    c.data_hora_clique,
    comp.codigo,
    comp.id_registro                         as id_divulgador,
    rd.nome_completo                         as divulgador,
    c.id_sessao,
    s.dispositivo,
    s.navegador,
    s.idioma_interface                       as idioma,
    a.id_visitante,
    rv.nome_completo                         as visitante,
    coalesce(a.id_visitante = comp.id_registro, false)           as autoclique,
    coalesce(a.novo_cadastro, false)                             as novo_cadastro,
    coalesce(a.ja_era_cadastrado, false)                         as ja_era_cadastrado,
    coalesce(a.qtd_acoes, 0)                                     as qtd_acoes,
    coalesce(a.gerou_base, false)                                as gerou_base,
    a.acoes                                                      as acoes_realizadas,
    -- só considerado quando a sessão tem cadastro novo, para medir "tempo até cadastrar"
    case when a.novo_cadastro
         then round(extract(epoch from (a.data_cadastro - c.data_hora_clique)))
    end                                                          as seg_clique_ate_cadastro
from public.cliques_compartilhamento c
join public.compartilhamentos comp on comp.id_compartilhamento = c.id_compartilhamento
join public.registros         rd   on rd.id_registro = comp.id_registro
left join lateral (
    select dispositivo, navegador, idioma_interface
      from public.logs_uso
     where id_sessao = c.id_sessao and tipo_evento = 'sessao_inicio'
     order by data_hora_evento
     limit 1
) s on true
left join lateral (
    select max(id_registro)                                                       as id_visitante,
           bool_or(acao = 'clicou_cadastrar' and status = 'sucesso')              as novo_cadastro,
           bool_or(acao = 'clicou_verificar_cadastro' and status = 'sucesso')     as ja_era_cadastrado,
           min(data_hora_evento) filter (where acao = 'clicou_cadastrar' and status = 'sucesso') as data_cadastro,
           count(*) filter (where tipo_evento = 'clique'
                              and acao not in ('clicou_cadastrar','clicou_verificar_cadastro',
                                               'trocou_idioma_tela_cadastro'))    as qtd_acoes,
           bool_or(acao = 'gerou_base')                                           as gerou_base,
           string_agg(distinct acao, ', ') filter (where tipo_evento = 'clique')  as acoes
      from public.logs_uso
     where id_sessao = c.id_sessao
) a on true
left join public.registros rv on rv.id_registro = a.id_visitante;

revoke all on public.vw_rastreio_detalhe from anon, authenticated;


-- [1] RESUMO GERAL (cartões) ----------------------------------------------------
select
    (select count(*) from public.registros)                                   as total_cadastros,
    (select count(*) from public.compartilhamentos)                           as links_gerados,
    (select count(distinct id_divulgador)
       from public.vw_rastreio_detalhe where not autoclique)                  as divulgadores_com_clique,
    count(*) filter (where not autoclique)                                    as cliques_validos,
    count(*) filter (where autoclique)                                        as autocliques,
    count(distinct id_sessao) filter (where not autoclique)                   as sessoes_indicadas,
    count(*) filter (where not autoclique and novo_cadastro)                  as novos_cadastros_por_indicacao,
    count(*) filter (where not autoclique and ja_era_cadastrado)              as ja_cadastrados,
    round(100.0 * count(*) filter (where not autoclique and novo_cadastro)
          / nullif(count(*) filter (where not autoclique), 0), 1)             as taxa_conversao_pct,
    round(100.0 * count(*) filter (where not autoclique and gerou_base)
          / nullif(count(*) filter (where not autoclique), 0), 1)             as pct_indicados_que_geraram_base,
    min(data_hora_clique)                                                     as primeiro_clique,
    max(data_hora_clique)                                                     as ultimo_clique
from public.vw_rastreio_detalhe;


-- [2] RANKING DE DIVULGADORES ----------------------------------------------------
-- Todos os links gerados, inclusive os que ninguém clicou (cliques = 0).
select
    comp.id_registro                                         as id_divulgador,
    r.nome_completo                                          as divulgador,
    comp.codigo,
    'https://ai-bidatagenerator.streamlit.app/?ref=' || comp.codigo as link,
    comp.data_hora_criacao                                   as link_criado_em,
    count(d.id_clique) filter (where not d.autoclique)       as cliques,
    count(d.id_clique) filter (where d.autoclique)           as autocliques,
    count(*) filter (where d.novo_cadastro and not d.autoclique)       as novos_cadastros,
    round(100.0 * count(*) filter (where d.novo_cadastro and not d.autoclique)
          / nullif(count(d.id_clique) filter (where not d.autoclique), 0), 1) as conversao_pct,
    max(d.data_hora_clique)                                  as ultimo_clique
from public.compartilhamentos comp
join public.registros r on r.id_registro = comp.id_registro
left join public.vw_rastreio_detalhe d on d.codigo = comp.codigo
group by comp.id_registro, r.nome_completo, comp.codigo, comp.data_hora_criacao
order by novos_cadastros desc, cliques desc, link_criado_em;


-- [3] DETALHE: UMA LINHA POR CLIQUE (quem indicou -> quem veio -> o que fez) --------
select
    data_hora_clique,
    divulgador,
    codigo,
    id_sessao,
    coalesce(visitante, '(anônimo: não se cadastrou)')  as visitante,
    case when autoclique         then 'autoclique'
         when novo_cadastro      then 'novo cadastro'
         when ja_era_cadastrado  then 'já era cadastrado'
         else 'só visitou' end                          as resultado,
    dispositivo, navegador, idioma,
    qtd_acoes,
    acoes_realizadas,
    seg_clique_ate_cadastro
from public.vw_rastreio_detalhe
order by data_hora_clique desc;


-- [4] FUNIL DA DIVULGAÇÃO ----------------------------------------------------------
-- Clique -> usou o app (alguma ação além do cadastro) -> gerou base -> cadastrou.
select etapa, qtd, round(100.0 * qtd / nullif(max(qtd) over (), 0), 1) as pct_do_topo
from (
    select 1 as ordem, '1. Clicaram no link' as etapa, count(*) as qtd
      from public.vw_rastreio_detalhe where not autoclique
    union all
    select 2, '2. Cadastraram (novo cadastro)', count(*)
      from public.vw_rastreio_detalhe where not autoclique and novo_cadastro
    union all
    select 3, '3. Usaram alguma função do app', count(*)
      from public.vw_rastreio_detalhe where not autoclique and qtd_acoes > 0
    union all
    select 4, '4. Geraram uma base', count(*)
      from public.vw_rastreio_detalhe where not autoclique and gerou_base
) f
order by ordem;


-- [5] EVOLUÇÃO DIÁRIA (fuso de São Paulo; as colunas já gravam horário de SP) -----
select
    data_hora_clique::date                                       as dia,
    count(*) filter (where not autoclique)                       as cliques,
    count(*) filter (where not autoclique and novo_cadastro)     as novos_cadastros,
    count(distinct id_divulgador) filter (where not autoclique)  as divulgadores_ativos
from public.vw_rastreio_detalhe
group by 1
order by 1 desc;


-- [6] PERFIL DE QUEM CLICOU (dispositivo / navegador / idioma) -----------------------
select
    coalesce(dispositivo, '(sem sessão)') as dispositivo,
    coalesce(navegador,  '(sem sessão)')  as navegador,
    coalesce(idioma,     '(sem sessão)')  as idioma,
    count(*)                              as cliques,
    count(*) filter (where novo_cadastro) as novos_cadastros
from public.vw_rastreio_detalhe
where not autoclique
group by 1, 2, 3
order by cliques desc;


-- [7] CADEIA DE INDICAÇÃO: quem foi indicado por quem -------------------------------
-- Cadastros novos vindos de link, e se o indicado também já gerou o próprio link
-- (isso mostra se a divulgação está "se multiplicando").
select
    d.divulgador                                   as indicado_por,
    d.visitante                                    as novo_cadastro,
    d.data_hora_clique                             as clicou_em,
    d.seg_clique_ate_cadastro                      as segundos_ate_cadastrar,
    (c2.id_compartilhamento is not null)           as indicado_tem_link,
    coalesce((select count(*) from public.vw_rastreio_detalhe x
               where x.id_divulgador = d.id_visitante and not x.autoclique), 0) as cliques_no_link_do_indicado
from public.vw_rastreio_detalhe d
left join public.compartilhamentos c2 on c2.id_registro = d.id_visitante
where d.novo_cadastro and not d.autoclique
order by d.data_hora_clique;


-- [8] CADASTROS SEM LINK GERADO (para auditoria) ------------------------------------
-- Cadastros anteriores à funcionalidade, ou em que a geração do link falhou
-- (a geração é best-effort). Dica: criar_link_compartilhamento(id) cria o link
-- de qualquer um deles sob demanda.
select r.id_registro, r.nome_completo, r.data_hora_inf as cadastrado_em
from public.registros r
left join public.compartilhamentos comp on comp.id_registro = r.id_registro
where comp.id_compartilhamento is null
order by r.id_registro;


-- [9] CONSISTÊNCIA: cliques cuja sessão não existe em logs_uso ----------------------
-- Deve retornar 0 linhas. Se aparecer algo, o ?ref= chegou antes do log da sessão
-- ou o id_sessao foi forjado.
select c.id_clique, c.id_sessao, c.data_hora_clique
from public.cliques_compartilhamento c
where not exists (select 1 from public.logs_uso l where l.id_sessao = c.id_sessao);
