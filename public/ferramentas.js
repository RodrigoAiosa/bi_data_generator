/* Ferramentas (todas as abas além do gerador). Depende de app.js (estado, $, esc, log, t). */
"use strict";

/* ── infraestrutura ────────────────────────────────────────────────────── */
/* Doherty: feedback imediato — barra fina no topo enquanto houver requisição pendente */
let _pend = 0, _tmr = null;
function indicarCarga(on) {
  const b = document.getElementById("topo-prog"); if (!b) return;
  _pend = Math.max(0, _pend + (on ? 1 : -1));
  if (on && _pend === 1) { clearTimeout(_tmr); b.className = ""; void b.offsetWidth; _tmr = setTimeout(() => { b.className = "on"; }, 120); }
  if (!on && _pend === 0) { clearTimeout(_tmr); b.className = "fim"; }
}
async function api(acao, dados = {}) {
  let r, j = null; indicarCarga(true);
  try {
    r = await fetch("/api/ferramenta", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ acao, ...dados }) });
    j = await r.json();
  } catch (_) { throw new Error("Não foi possível conectar. Tente novamente."); }
  finally { indicarCarga(false); }
  if (!r.ok) throw new Error((j && j.erro) || "Não foi possível concluir a operação.");
  return j;
}

function baixar(nome, conteudo, mime = "text/plain;charset=utf-8") {
  const blob = conteudo instanceof Blob ? conteudo : new Blob([conteudo], { type: mime });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob); a.download = nome; document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}
const csvBlob = (txt) => new Blob(["\ufeff" + txt], { type: "text/csv;charset=utf-8" });
const b64Blob = (b64, mime) => { const bin = atob(b64), u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return new Blob([u], { type: mime }); };
const lerTexto = (arq) => new Promise((ok, no) => { const f = new FileReader(); f.onload = () => ok(f.result); f.onerror = no; f.readAsText(arq); });
const lerB64 = (arq) => new Promise((ok, no) => { const f = new FileReader(); f.onload = () => ok(String(f.result).split(",")[1] || ""); f.onerror = no; f.readAsDataURL(arq); });
const fmt = (n, d = 2) => Number(n).toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d });

function tabela(colunas, linhas) {
  return `<div class="tabela-wrap"><table><thead><tr>${colunas.map((c) => `<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>` +
    linhas.map((l) => `<tr>${l.map((v) => `<td>${esc(typeof v === "string" ? v.replace(/T00:00:00$/, "") : v)}</td>`).join("")}</tr>`).join("") + "</tbody></table></div>";
}
const tabelaDf = (d) => tabela(d.colunas, d.linhas) + `<p class="muted"><small>${d.total.toLocaleString("pt-BR")} linha(s) · ${d.colunas.length} coluna(s)${d.total > d.linhas.length ? ` · mostrando ${d.linhas.length}` : ""}</small></p>`;
const msgErro = (el, e) => { el.innerHTML = `<div class="card erro">${esc(e.message || e)}</div>`; };
const carregando = (el, txt = "Processando…") => { el.innerHTML = `<p class="muted" role="status">⏳ ${esc(txt)}</p>`; };
const cab = (titulo, desc) => `<h2>${titulo}</h2><p class="muted">${desc}</p>`;

async function comBotao(btn, fn) {
  const txt = btn.textContent; btn.disabled = true;
  try { await fn(); } finally { btn.disabled = false; btn.textContent = txt; }
}

/* base para as ferramentas que dependem de dados */
function hashSeed(txt) { let h = 2166136261; for (let i = 0; i < txt.length; i++) { h ^= txt.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0) % 2147483647; }
let saltBase = "";
function baseSidebar() {
  const setor = $("setor").value, linhas = linhasVal(), inicio = $("inicio").value, fim = $("fim").value;
  if (!setor) throw new Error("Escolha um setor na barra lateral para começar.");
  if (!(linhas >= 100 && linhas <= 100000)) throw new Error(t("e_lin"));
  if (!inicio || !fim || inicio >= fim) throw new Error(t("e_per"));
  const mes = Number($("mes-fiscal").value);
  return { setor, linhas, inicio, fim, mes_fiscal: mes, anomalia: false, deriva: false, idioma: estado.lang,
    seed: hashSeed([setor, linhas, inicio, fim, mes, saltBase].join("|")) };
}
const baseGerada = () => estado.baseGerada || baseSidebar();

/* ── abas ──────────────────────────────────────────────────────────────── */
const INICIADAS = {};
const TELAS = {};
function abrirAba(id) {
  document.querySelectorAll("#abas-ferramentas button").forEach((b) => b.classList.toggle("ativo", b.dataset.aba === id));
  document.querySelectorAll(".painel").forEach((p) => (p.hidden = p.id !== "p-" + id));
  if (!INICIADAS[id] && TELAS[id]) { INICIADAS[id] = true; TELAS[id]($("p-" + id)); }
  if (typeof log === "function") log("abriu_aba_" + id);
}
document.addEventListener("DOMContentLoaded", () => {
  $("abas-ferramentas").addEventListener("click", (e) => { const b = e.target.closest("button"); if (b) abrirAba(b.dataset.aba); });
});

/* ── Formatar DAX / Formatar M ─────────────────────────────────────────── */
const EX_DAX = [
  "Valor Lance Mês Anterior=CALCULATE([Total Valor Lance],DATEADD(dCalendario[Data],-1,MONTH))",
  "% do Total Vendas=DIVIDE([Total Vendas],CALCULATE([Total Vendas],ALL(FatoVendas)))",
  "Total=SUM(FatoVendas[valor_total])+SUM(FatoVendas[frete])-SUM(FatoVendas[desconto])",
  "Media Movel = VAR TotalAtual = SUM(Vendas[Valor]) VAR TotalAnterior = CALCULATE(SUM(Vendas[Valor]), DATEADD(Calendario[Data], -1, MONTH)) RETURN DIVIDE(TotalAtual, TotalAnterior)",
  "Qtde Distinta de Cliente=DISTINCTCOUNT(FatoVendas[id_cliente])",
  "Receita Acumulada no Ano (YTD)=TOTALYTD([Total Vendas],dCalendario[Data])",
  "Ticket Médio=DIVIDE(SUM(FatoVendas[valor_total]),DISTINCTCOUNT(FatoVendas[id_venda]))",
];
const EX_M = [
  'let Source = Csv.Document(File.Contents("C:\\Dados\\arquivo.csv"),[Delimiter=",", Encoding=65001]), #"Changed Type" = Table.TransformColumnTypes(Source,{{"Coluna1", Int64.Type}}) in #"Changed Type"',
  'let Source = Table.NestedJoin(Vendas, {"id_cliente"}, Clientes, {"id_cliente"}, "Clientes", JoinKind.LeftOuter), #"Expanded Clientes" = Table.ExpandTableColumn(Source, "Clientes", {"nome"}) in #"Expanded Clientes"',
  'let Fonte = Excel.Workbook(File.Contents("C:\\Dados\\vendas.xlsx"), null, true), #"Planilha1_Sheet" = Fonte{[Item="Planilha1",Kind="Sheet"]}[Data], #"Cabeçalhos Promovidos" = Table.PromoteHeaders(#"Planilha1_Sheet", [PromoteAllScalars=true]) in #"Cabeçalhos Promovidos"',
  'let Origem = Table.SelectRows(Vendas, each [valor_total] > 100 and [status] = "Aprovado"), #"Colunas Removidas" = Table.RemoveColumns(Origem,{"observacao", "id_interno"}) in #"Colunas Removidas"',
  'let Source = Table.Group(Vendas, {"id_cliente"}, {{"Total", each List.Sum([valor_total]), type nullable number}}) in Source',
];

function telaFormatador(el, { acao, titulo, desc, rotulo, exemplos, arquivo, evento }) {
  el.innerHTML = cab(titulo, desc) + `
    <label><span>${rotulo}</span><textarea rows="8" id="${acao}-in" placeholder="${esc(exemplos[0])}"></textarea></label>
    <div class="linha-btn"><button class="btn primario" id="${acao}-go">${titulo.split(" ")[0]} Formatar</button><button class="btn" id="${acao}-ex">💡 Usar exemplo</button></div>
    <div id="${acao}-out"></div>`;
  let ultimo = "";
  $(acao + "-ex").onclick = () => {
    const c = exemplos.filter((x) => x !== ultimo); ultimo = c[Math.floor(Math.random() * c.length)];
    $(acao + "-in").value = ultimo; log("usou_exemplo_" + evento);
  };
  $(acao + "-go").onclick = (e) => comBotao(e.currentTarget, async () => {
    const out = $(acao + "-out"), txt = $(acao + "-in").value;
    if (!txt.trim()) return msgErro(out, "Cole o código antes de formatar.");
    try {
      const r = await api(acao, { texto: txt });
      out.innerHTML = `<h3>✅ Formatado</h3><pre id="${acao}-res"></pre><button class="btn" id="${acao}-bx">📥 Baixar como ${arquivo.split(".").pop() === "dax" ? ".dax" : ".m"}</button>`;
      $(acao + "-res").textContent = r.resultado;
      $(acao + "-bx").onclick = () => { baixar(arquivo, r.resultado); log("baixou_" + evento + "_formatado"); };
      log("formatou_" + evento, { volume_linhas: txt.length });
    } catch (err) { msgErro(out, err); log("formatou_" + evento, { status: "erro", erro_detalhe: String(err.message).slice(0, 200) }); }
  });
}
TELAS.dax = (el) => telaFormatador(el, { acao: "formatar_dax", titulo: "📐 Formatar DAX", evento: "dax", arquivo: "medida_formatada.dax", exemplos: EX_DAX, rotulo: "Cole a expressão DAX aqui",
  desc: "Cole uma expressão ou medida DAX bagunçada (tudo numa linha só) e receba ela formatada: cada argumento de função numa linha própria, VAR/RETURN separados, espaçamento consistente." });
TELAS.m = (el) => telaFormatador(el, { acao: "formatar_m", titulo: "🔧 Formatar M", evento: "m", arquivo: "consulta_formatada.m", exemplos: EX_M, rotulo: "Cole o código M aqui",
  desc: "Cole um código M (Power Query) bagunçado e receba ele formatado: cada passo do bloco let…in em sua própria linha, expressões longas quebradas por profundidade, identificadores entre aspas preservados." });

/* ── Auditor de Modelo ─────────────────────────────────────────────────── */
TELAS.auditor = (el) => {
  el.innerHTML = cab("🩺 Auditor de Modelo", "Cole o TMDL de um modelo Power BI seu de verdade e receba uma nota de qualidade com achados acionáveis: medida duplicada, divisão sem DIVIDE(), coluna calculada que poderia ser medida, coluna técnica exposta, nomenclatura inconsistente e organização de pastas.") +
    `<div class="info">💡 No Tabular Editor, clique com o botão direito no modelo → <strong>Advanced Scripting</strong> ou use <strong>Copy as TMDL</strong>/<strong>Script</strong> para pegar o texto completo.</div>
    <label><span>Cole o TMDL do seu modelo aqui</span><textarea rows="10" id="aud-in" placeholder="createOrReplace&#10;&#10;&#9;table Medidas&#10;&#9;&#9;measure 'Total Vendas' = SUM(...)"></textarea></label>
    <label><span>Ou envie um arquivo .tmdl / .txt</span><input type="file" id="aud-file" accept=".tmdl,.txt"></label>
    <div class="linha-btn"><button class="btn primario" id="aud-go">🩺 Auditar modelo</button></div><div id="aud-out"></div>`;
  $("aud-file").onchange = async (e) => { if (e.target.files[0]) $("aud-in").value = await lerTexto(e.target.files[0]); };
  $("aud-go").onclick = (e) => comBotao(e.currentTarget, async () => {
    const out = $("aud-out"), txt = $("aud-in").value;
    if (!txt.trim()) return msgErro(out, "Cole ou envie o TMDL do seu modelo antes de auditar.");
    carregando(out, "Analisando o modelo…");
    try {
      const { relatorio: r } = await api("auditar", { texto: txt });
      const cor = r.nota >= 85 ? "🟢" : r.nota >= 60 ? "🟡" : "🔴", ic = { alta: "🔴", "média": "🟡", baixa: "🔵" }, ord = { alta: 0, "média": 1, baixa: 2 };
      const ach = [...r.achados].sort((a, b) => (ord[a.severidade] ?? 9) - (ord[b.severidade] ?? 9));
      const cls = (s) => (s === "alta" ? "sev-alta" : s === "baixa" ? "sev-baixa" : "sev-media");
      out.innerHTML = `<h3>Resultado da auditoria</h3><div class="metricas">
        <div class="metrica"><small>Nota</small><b>${cor} ${r.nota}/100</b></div><div class="metrica"><small>Medidas analisadas</small><b>${r.resumo.total_medidas}</b></div>
        <div class="metrica"><small>Colunas analisadas</small><b>${r.resumo.total_colunas}</b></div><div class="metrica"><small>Achados</small><b>${r.resumo.total_achados}</b></div></div>` +
        (ach.length ? "<h3>Achados</h3>" + ach.map((a) => `<details class="card ${cls(a.severidade)}"><summary>${ic[a.severidade] || "⚪"} [${esc(a.categoria)}] ${esc(a.mensagem.slice(0, 80))}</summary>
          <p><strong>Onde:</strong> ${esc(a.medida)}</p><p><strong>O que é:</strong> ${esc(a.mensagem)}</p><p><strong>Sugestão:</strong> ${esc(a.sugestao)}</p></details>`).join("")
          : `<div class="card ok">Nenhum achado! Esse modelo passou por todas as checagens.</div>`) +
        `<button class="btn" id="aud-bx">📥 Baixar relatório completo (.txt)</button>`;
      $("aud-bx").onclick = () => {
        const L = ["AUDITORIA DE MODELO POWER BI", "", `Nota: ${r.nota}/100`, `Medidas analisadas: ${r.resumo.total_medidas}`, `Colunas analisadas: ${r.resumo.total_colunas}`,
          `Relacionamentos analisados: ${r.resumo.total_relacionamentos}`, `Total de achados: ${r.resumo.total_achados}`, ""];
        ach.forEach((a) => L.push(`[${a.severidade.toUpperCase()}] ${a.categoria}`, `  Onde: ${a.medida}`, `  ${a.mensagem}`, `  Sugestão: ${a.sugestao}`, ""));
        baixar("auditoria_modelo.txt", L.join("\n")); log("baixou_relatorio_auditor");
      };
      log("auditou_modelo", { volume_linhas: txt.length });
    } catch (err) { msgErro(out, err); }
  });
};

/* ── Carrossel Power BI ────────────────────────────────────────────────── */
TELAS.carrossel = (el) => {
  el.innerHTML = cab("🖥️ Carrossel Power BI", "Envie o <strong>.pbix</strong> do seu relatório (ou o .zip de um projeto .pbip), marque as páginas, cole o <strong>link do relatório publicado</strong> no Power BI Service e baixe um HTML que alterna sozinho entre as páginas a cada X segundos — ótimo para monitor ou TV em modo apresentação. O arquivo é lido no seu navegador: só a lista de páginas vai ao servidor.") +
    `<details class="card"><summary>❓ Onde encontro esse link?</summary><p>No Power BI Service, abra o relatório publicado e vá em <strong>Arquivo → Inserir relatório → Site ou portal</strong>. Cole o link (ou o código &lt;iframe&gt; inteiro): a ferramenta identifica o <code>reportId</code> e o <code>ctid</code> sozinha.</p></details>
    <label><span>Arquivo .pbix (ou .zip de um projeto .pbip)</span><input type="file" id="car-file" accept=".pbix,.zip"></label><div id="car-out"></div>`;
  let paginas = [];
  $("car-file").onchange = async (e) => {
    const out = $("car-out"), f = e.target.files[0]; if (!f) return;
    carregando(out, "Lendo o arquivo…");
    try {
      const dados = new Uint8Array(await f.arrayBuffer());
      const util = fflate.unzipSync(dados, { filter: (x) => { const n = x.name.replace(/\\/g, "/").toLowerCase(); return n === "report/layout" || /definition\/pages\/.*\.json$/.test(n); } });
      if (!Object.keys(util).length) throw new Error("Não encontrei páginas nesse arquivo. Envie um .pbix ou um projeto .pbip (PBIR) compactado em .zip.");
      const mini = fflate.zipSync(Object.fromEntries(Object.entries(util).map(([k, v]) => [k, [v, { level: 6 }]])));
      const r = await api("carrossel_paginas", { zip_base64: btoa(Array.from(mini, (b) => String.fromCharCode(b)).join("")) });
      paginas = r.paginas; desenharCarrossel();
    } catch (err) { msgErro(out, err); }
  };
  function desenharCarrossel() {
    $("car-out").innerHTML = `<div class="info">✅ ${paginas.length} página(s) encontrada(s) no relatório.</div>
      <div class="linha-btn"><button class="btn" id="car-todas">☑️ Marcar todas</button><button class="btn" id="car-nenhuma">⬜ Desmarcar todas</button></div>
      <strong>Marque as páginas que quer incluir:</strong>` +
      paginas.map(([n, id], i) => `<label class="opcao"><input type="checkbox" class="car-pg" data-i="${i}" checked> <span>${esc(n)} <code>${esc(id)}</code></span></label>`).join("") +
      `<label><span>Link (ou código de inserção) do relatório publicado</span><textarea rows="3" id="car-link" placeholder="https://app.powerbi.com/reportEmbed?reportId=...&autoAuth=true&ctid=..."></textarea></label>
      <div class="grade"><label><span>Trocar a cada (segundos)</span><input type="number" id="car-int" min="1" max="3600" value="10"></label>
      <label class="check"><input type="checkbox" id="car-chrome" checked><span>chromeless (sem barra de ferramentas)</span></label>
      <label class="check"><input type="checkbox" id="car-auth" checked><span>autoAuth</span></label></div>
      <div class="linha-btn"><button class="btn primario" id="car-go">📥 Gerar e baixar carrossel.html</button></div><div id="car-res"></div>`;
    $("car-todas").onclick = () => document.querySelectorAll(".car-pg").forEach((c) => (c.checked = true));
    $("car-nenhuma").onclick = () => document.querySelectorAll(".car-pg").forEach((c) => (c.checked = false));
    $("car-go").onclick = (e) => comBotao(e.currentTarget, async () => {
      try {
        const sel = [...document.querySelectorAll(".car-pg:checked")].map((c) => paginas[+c.dataset.i]);
        const r = await api("carrossel_html", { paginas: sel, link: $("car-link").value, intervalo: +$("car-int").value || 10, chromeless: $("car-chrome").checked, auto_auth: $("car-auth").checked });
        baixar("carrossel_powerbi.html", r.html, "text/html;charset=utf-8"); log("baixou_carrossel_html", { volume_linhas: sel.length });
        $("car-res").innerHTML = `<div class="card ok">Pronto! Abra o arquivo em qualquer navegador (de preferência já autenticado no Power BI) e deixe em tela cheia: ele troca de página a cada ${r.intervalo} segundo(s), em loop.</div>
          <details class="card"><summary>📄 ${r.urls.length} URL(s) de embed geradas</summary>${r.urls.map(([n, u], i) => `<p><strong>${i + 1}. ${esc(n)}</strong></p><pre>${esc(u)}</pre>`).join("")}</details>`;
      } catch (err) { msgErro($("car-res"), err); }
    });
  }
};

/* ── PL-300 ────────────────────────────────────────────────────────────── */
TELAS.pl300 = (el) => {
  const hist = { sessao: [], importado: [] };
  let perguntas = [], dominios = [];
  el.innerHTML = cab("🎓 Simulador de Certificação PL-300", "Perguntas de prática 100% originais, organizadas nos 4 domínios oficiais do exame <strong>PL-300 (Microsoft Certified: Power BI Data Analyst Associate)</strong>. Este simulador não reproduz nem substitui o exame real.") +
    `<details class="card"><summary>📎 Fontes oficiais da Microsoft (recomendado usar junto)</summary><ul>
      <li><a href="https://learn.microsoft.com/en-us/credentials/certifications/data-analyst-associate/practice/assessment?assessment-type=practice&assessmentId=48&practice-assessment-type=certification" target="_blank" rel="noopener">Practice Assessment oficial (gratuito)</a></li>
      <li><a href="https://aka.ms/pl300-StudyGuide" target="_blank" rel="noopener">Guia de estudo oficial da prova</a></li>
      <li><a href="https://learn.microsoft.com/en-us/credentials/certifications/data-analyst-associate/" target="_blank" rel="noopener">Página da certificação PL-300</a></li></ul></details>
    <p class="muted" id="pl-ctx">Gere uma base na aba “Gerador de Setores” para ver perguntas usando os seus próprios dados como contexto.</p>
    <label><span>Quantas perguntas no simulado?</span><select id="pl-n"><option>5</option><option selected>10</option><option>15</option><option>20</option></select></label>
    <div class="linha-btn"><button class="btn primario" id="pl-go">🎲 Sortear novo simulado</button></div><div id="pl-prova"></div><div id="pl-res"></div><div id="pl-prog"></div>`;
  const dataHora = () => { const d = new Date(), p = (n) => String(n).padStart(2, "0"); return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`; };
  $("pl-go").onclick = (e) => comBotao(e.currentTarget, async () => {
    $("pl-res").innerHTML = ""; carregando($("pl-prova"), "Sorteando perguntas…");
    try {
      const r = await api("pl300", { n: +$("pl-n").value, ...(estado.baseGerada ? { base: estado.baseGerada } : {}) });
      perguntas = r.perguntas; dominios = r.dominios;
      $("pl-ctx").textContent = r.contextual ? `Algumas perguntas usam a base de ${estado.baseGerada.setor} que você gerou, como contexto.` : $("pl-ctx").textContent;
      $("pl-prova").innerHTML = `<form id="pl-form">` + perguntas.map((p, i) => `<div class="card"><strong>${i + 1}. [${esc(p.dominio)}] ${esc(p.pergunta)}</strong>` +
        p.opcoes.map((o, k) => `<label class="opcao"><input type="radio" name="q${i}" value="${k}"> <span>${esc(o)}</span></label>`).join("") + "</div>").join("") +
        `<button class="btn primario grande" type="submit">✅ Corrigir simulado</button></form>`;
      $("pl-form").onsubmit = (ev) => { ev.preventDefault(); corrigir(); };
      log("abriu_simulador_pl300", { volume_linhas: perguntas.length });
    } catch (err) { msgErro($("pl-prova"), err); }
  });
  function corrigir() {
    const resp = perguntas.map((p, i) => { const c = document.querySelector(`input[name=q${i}]:checked`); return c ? +c.value : null; });
    let acertos = 0; const dom = Object.fromEntries(dominios.map((d) => [d, [0, 0]]));
    perguntas.forEach((p, i) => { dom[p.dominio] = dom[p.dominio] || [0, 0]; dom[p.dominio][1]++; if (resp[i] === p.correta) { acertos++; dom[p.dominio][0]++; } });
    const total = perguntas.length, pct = total ? (acertos / total) * 100 : 0, dh = dataHora();
    hist.sessao.push({ data_hora: dh, acertos, total, pct });
    const limpar = (x) => String(x).replace(/;/g, ",").replace(/\n/g, " ").trim();
    const linhas = ["data_hora;pergunta;resposta_aluno;resposta_correta;total_acertos;total_erros;%total_acerto"];
    perguntas.forEach((p, i) => linhas.push(`${dh};${limpar(p.pergunta)};${limpar(resp[i] == null ? "(não respondida)" : p.opcoes[resp[i]])};${limpar(p.opcoes[p.correta])};${acertos};${total - acertos};${pct.toFixed(1)}`));
    $("pl-res").innerHTML = `<h3>🏁 Resultado: ${acertos}/${total} (${pct.toFixed(0)}%)</h3><div class="metricas">` +
      Object.entries(dom).map(([d, [a, n]]) => `<div class="metrica"><small>${esc(d)}</small><b>${n ? a + "/" + n : "-"}</b></div>`).join("") + `</div>
      <button class="btn" id="pl-bx">📥 Baixar resultado desta prova (.csv)</button>
      <p class="muted">Guarde o arquivo: baixando um a cada prova, você monta seu histórico de evolução.</p><h3>Revisão pergunta a pergunta</h3>` +
      perguntas.map((p, i) => { const ok = resp[i] === p.correta; return `<details class="card"><summary>${ok ? "✅" : "❌"} ${i + 1}. [${esc(p.dominio)}] ${esc(p.pergunta.slice(0, 70))}…</summary>
        <p><strong>Sua resposta:</strong> ${resp[i] == null ? "<em>(não respondida)</em>" : esc(p.opcoes[resp[i]])}</p><p><strong>Resposta correta:</strong> ${esc(p.opcoes[p.correta])}</p><p><strong>Explicação:</strong> ${esc(p.explicacao)}</p></details>`; }).join("");
    $("pl-bx").onclick = () => { baixar(`resultado_pl300_${dh.replace(" ", "_").replace(/:/g, "")}.csv`, csvBlob(linhas.join("\n"))); log("baixou_resultado_pl300", { volume_linhas: total }); };
    log("corrigiu_simulado_pl300", { volume_linhas: total });
    progresso(); $("pl-res").scrollIntoView({ behavior: "smooth" });
  }
  function parseCsv(txt) {
    const L = txt.replace(/^\ufeff/, "").trim().split("\n").filter((l) => l.trim()), out = {};
    for (const l of L.slice(1)) {
      const c = l.split(";"); if (c.length < 7 || out[c[0]]) continue;
      const a = parseInt(c[4], 10), e = parseInt(c[5], 10), p = parseFloat(c[6]); if ([a, e, p].some(Number.isNaN)) continue;
      out[c[0]] = { data_hora: c[0], acertos: a, total: a + e, pct: p };
    }
    return Object.values(out);
  }
  function progresso() {
    const todos = [...hist.importado, ...hist.sessao].sort((a, b) => a.data_hora.localeCompare(b.data_hora)), p = todos.map((x) => x.pct);
    $("pl-prog").innerHTML = `<h3>🏆 Seu progresso</h3><details class="card"><summary>📤 Importar histórico de sessões anteriores (.csv)</summary>
      <p class="muted">Envie os arquivos <code>resultado_pl300_*.csv</code> que você já baixou, para juntar com o progresso desta sessão.</p><input type="file" id="pl-imp" accept=".csv" multiple></details>` +
      (todos.length ? `<div class="metricas"><div class="metrica"><small>Simulados no histórico</small><b>${todos.length}</b></div><div class="metrica"><small>Melhor nota</small><b>${Math.max(...p).toFixed(0)}%</b></div>
        <div class="metrica"><small>Média geral</small><b>${(p.reduce((a, b) => a + b, 0) / p.length).toFixed(0)}%</b></div></div>` + (todos.length > 1 ? graficoLinhas(todos.map((_, i) => i + 1), { "Nota (%)": p }, 0, 100) : "") : `<p class="muted">Faça e corrija seu primeiro simulado para ver seu progresso aqui.</p>`);
    $("pl-imp").onchange = async (e) => {
      hist.importado = []; for (const f of e.target.files) hist.importado.push(...parseCsv(await lerTexto(f))); progresso();
    };
  }
  progresso();
};

/* ── gráfico de linhas (SVG) ───────────────────────────────────────────── */
const CORES = ["#F2C811", "#5aa9ff", "#3ecf8e", "#ff6b6b"];
function graficoLinhas(x, series, yMin, yMax) {
  const W = 760, H = 280, m = { l: 56, r: 12, t: 12, b: 28 }, nomes = Object.keys(series);
  const vals = nomes.flatMap((n) => series[n]).filter((v) => v != null);
  const lo = yMin ?? Math.min(...vals), hi = yMax ?? Math.max(...vals), span = hi - lo || 1;
  const px = (i) => m.l + (x.length < 2 ? 0 : (i / (x.length - 1)) * (W - m.l - m.r)), py = (v) => m.t + (1 - (v - lo) / span) * (H - m.t - m.b);
  let g = "";
  for (let k = 0; k <= 4; k++) { const v = lo + (span * k) / 4, y = py(v); g += `<line x1="${m.l}" x2="${W - m.r}" y1="${y}" y2="${y}" stroke="#333"/><text x="${m.l - 6}" y="${y + 4}" text-anchor="end" fill="#a8a8a8" font-size="11">${fmt(v, span < 10 ? 1 : 0)}</text>`; }
  g += `<text x="${m.l}" y="${H - 8}" fill="#a8a8a8" font-size="11">${esc(String(x[0]))}</text><text x="${W - m.r}" y="${H - 8}" text-anchor="end" fill="#a8a8a8" font-size="11">${esc(String(x[x.length - 1]))}</text>`;
  nomes.forEach((n, s) => { const pts = series[n].map((v, i) => (v == null ? null : `${px(i).toFixed(1)},${py(v).toFixed(1)}`)).filter(Boolean).join(" "); g += `<polyline fill="none" stroke="${CORES[s % 4]}" stroke-width="2" points="${pts}"/>`; });
  return `<svg class="grafico" viewBox="0 0 ${W} ${H}" role="img" aria-label="Gráfico de linhas">${g}</svg><div class="legenda">${nomes.map((n, s) => `<span><i style="background:${CORES[s % 4]}"></i>${esc(n)}</span>`).join("")}</div>`;
}

/* ── SCD ───────────────────────────────────────────────────────────────── */
TELAS.scd = async (el) => {
  el.innerHTML = cab("🕰️ Simulador de Dimensões Mutáveis", "Pratique <strong>Slowly Changing Dimensions</strong>, um dos assuntos mais cobrados no PL-300. A ferramenta pega uma dimensão da base gerada, simula a passagem do tempo com mudanças reais e monta o <strong>gabarito exato</strong> junto com o resultado correto dos 3 tratamentos clássicos (Tipo 1, 2 e 3).") + `<div id="scd-corpo"></div>`;
  $("p-scd").dataset.carregado = "";
  await montar();
  async function montar() {
    const c = $("scd-corpo"); carregando(c, "Carregando dimensões…");
    let info;
    try { info = await api("scd_info", { base: baseGerada() }); } catch (err) { INICIADAS.scd = false; return msgErro(c, err); }
    if (!info.dimensoes.length) return (c.innerHTML = `<div class="aviso">Essa base não tem nenhuma tabela de dimensão para usar neste exercício.</div>`);
    c.innerHTML = `<p class="muted">Usando a base de <strong>${esc(baseGerada().setor)}</strong>.</p><label><span>Dimensão</span><select id="scd-dim">${info.dimensoes.map((d) => `<option value="${esc(d.nome)}" data-n="${d.linhas}">${esc(d.nome)}</option>`).join("")}</select></label>
      <label><span class="slider-l"><span>Quantas linhas devem mudar entre as duas fotografias?</span><b id="scd-nv">10</b></span><input type="range" id="scd-n" min="1" max="10" value="10"></label>
      <div class="linha-btn"><button class="btn primario" id="scd-go">🕰️ Gerar cenário</button></div><div id="scd-out"></div>`;
    const ajusta = () => { const n = +$("scd-dim").selectedOptions[0].dataset.n, mx = Math.max(1, Math.min(n, 100)); $("scd-n").max = mx; $("scd-n").value = Math.min(+$("scd-n").value, mx); $("scd-nv").textContent = $("scd-n").value; };
    $("scd-dim").onchange = ajusta; $("scd-n").oninput = () => ($("scd-nv").textContent = $("scd-n").value); ajusta();
    $("scd-go").onclick = (e) => comBotao(e.currentTarget, async () => {
      const out = $("scd-out"); carregando(out, "Gerando cenário…");
      try {
        const r = await api("scd", { base: baseGerada(), dim: $("scd-dim").value, n_mudancas: +$("scd-n").value });
        const desc = { tipo1: "<strong>SCD Tipo 1</strong>: a linha é sobrescrita com o valor novo — simples, mas perde o histórico. Bom quando o dado antigo não tem valor analítico (ex.: corrigir erro de digitação).",
          tipo2: "<strong>SCD Tipo 2</strong>: a linha antiga é preservada (com <code>DataFimValidade</code> e <code>RegistroAtual = False</code>) e uma nova é adicionada — precisa de chave substituta (<code>sk_scd</code>). Único que preserva o histórico completo.",
          tipo3: "<strong>SCD Tipo 3</strong>: uma linha por chave, guardando o valor anterior numa coluna irmã (<code>&lt;coluna&gt;_Anterior</code>). Só guarda a ÚLTIMA mudança." };
        out.innerHTML = `<div class="card ok">Cenário gerado em cima de <strong>${esc(r.dim)}</strong> (${r.alteradas} linha(s) alterada(s), de ${r.total} no total).</div>
          <h3>🔎 As duas fotografias</h3><div class="dois"><div><strong>T0 (antes)</strong>${tabelaDf(r.t0)}</div><div><strong>T1 (depois)</strong>${tabelaDf(r.t1)}</div></div>
          <details class="card"><summary>🔍 Ver gabarito (spoiler — tente identificar as mudanças antes)</summary>${tabelaDf(r.gabarito)}</details>
          <h3>🧩 Os 3 tratamentos clássicos de SCD</h3><div class="sub-abas" id="scd-sub"><button class="ativo" data-t="tipo1">Tipo 1 (sobrescreve)</button><button data-t="tipo2">Tipo 2 (histórico)</button><button data-t="tipo3">Tipo 3 (coluna anterior)</button></div><div id="scd-tipo"></div>
          <h3>📥 Download</h3><div class="linha-btn" id="scd-dl"></div>`;
        const mostra = (t) => { $("scd-tipo").innerHTML = `<p class="muted">${desc[t]}</p>` + tabelaDf(r[t]); document.querySelectorAll("#scd-sub button").forEach((b) => b.classList.toggle("ativo", b.dataset.t === t)); };
        $("scd-sub").onclick = (ev) => { const b = ev.target.closest("button"); if (b) mostra(b.dataset.t); }; mostra("tipo1");
        const nomes = { "scd_t0_antes.csv": "T0 (antes)", "scd_t1_depois.csv": "T1 (depois)", "scd_gabarito.csv": "Gabarito", "scd_tipo2_resultado.csv": "SCD Tipo 2 (completo)" };
        $("scd-dl").innerHTML = Object.keys(r.arquivos).map((k) => `<button class="btn" data-f="${esc(k)}">${esc(nomes[k] || k)}</button>`).join("");
        $("scd-dl").onclick = (ev) => { const b = ev.target.closest("button"); if (b) { baixar(b.dataset.f, csvBlob(r.arquivos[b.dataset.f])); log("baixou_scd"); } };
        log("gerou_scd", { setor_gerado: baseGerada().setor, volume_linhas: r.alteradas });
      } catch (err) { msgErro(out, err); }
    });
  }
};

/* ── Dados Causais ─────────────────────────────────────────────────────── */
TELAS.causal = async (el) => {
  el.innerHTML = cab("🧬 Dados Causais", "Diferente do resto do gerador (dados só estatisticamente plausíveis), aqui a relação causa-efeito é conhecida de propósito, construída em cima do setor que você já gerou. Ideal para praticar inferência causal, teste A/B e marketing mix modeling com o gabarito certo na mão.") + `<div id="cau-corpo"></div>`;
  const c = $("cau-corpo"); carregando(c, "Carregando colunas…");
  let info; try { info = await api("causal_info", { base: baseGerada() }); } catch (err) { INICIADAS.causal = false; return msgErro(c, err); }
  const fatos = Object.entries(info.fatos).filter(([, f]) => f.data && f.colunas.length >= 2);
  if (!fatos.length) return (c.innerHTML = `<div class="aviso">Essa base não tem uma tabela fato com coluna de data e pelo menos 2 colunas numéricas.</div>`);
  c.innerHTML = `<p class="muted">Usando a base de <strong>${esc(baseGerada().setor)}</strong> como cenário causal.</p>
    <label><span>Tabela fato</span><select id="cau-fato">${fatos.map(([k]) => `<option>${esc(k)}</option>`).join("")}</select></label>
    <div class="dois"><label><span>Qual coluna é a CAUSA? (valores reais, agregados por semana)</span><select id="cau-causa"></select></label>
    <label><span>Qual coluna representa o EFEITO? (valor 100% simulado)</span><select id="cau-efeito"></select></label></div>
    <span class="rotulo">A causa AUMENTA ou REDUZ o efeito?</span><label class="opcao"><input type="radio" name="cau-dir" value="1" checked> Aumenta</label><label class="opcao"><input type="radio" name="cau-dir" value="-1"> Reduz</label>
    <label class="check"><input type="checkbox" id="cau-conf" checked><span>Incluir um confundidor (sazonalidade)?</span></label>
    <div class="grade"><label><span class="slider-l"><span>Força do efeito causal (%)</span><b id="cau-ev">20</b></span><input type="range" id="cau-ef" min="5" max="60" value="20"></label>
    <label><span class="slider-l"><span>Defasagem (semanas)</span><b id="cau-dv">2</b></span><input type="range" id="cau-df" min="0" max="8" value="2"></label>
    <label><span class="slider-l"><span>Intensidade do ruído (%)</span><b id="cau-rv">15</b></span><input type="range" id="cau-rf" min="0" max="50" value="15"></label></div>
    <div class="linha-btn"><button class="btn primario" id="cau-go">🧬 Gerar cenário causal</button></div><div id="cau-out"></div>`;
  const cols = () => info.fatos[$("cau-fato").value].colunas;
  const preenche = () => { const cs = cols(); $("cau-causa").innerHTML = cs.map((x) => `<option>${esc(x)}</option>`).join(""); efeitoOpc(); };
  const efeitoOpc = () => { $("cau-efeito").innerHTML = cols().filter((x) => x !== $("cau-causa").value).map((x) => `<option>${esc(x)}</option>`).join(""); };
  $("cau-fato").onchange = preenche; $("cau-causa").onchange = efeitoOpc; preenche();
  [["ef", "ev"], ["df", "dv"], ["rf", "rv"]].forEach(([a, b]) => ($("cau-" + a).oninput = () => ($("cau-" + b).textContent = $("cau-" + a).value)));
  $("cau-go").onclick = (e) => comBotao(e.currentTarget, async () => {
    const out = $("cau-out"); carregando(out, "Gerando cenário…");
    try {
      const r = await api("causal", { base: baseGerada(), fato: $("cau-fato").value, causa: $("cau-causa").value, efeito: $("cau-efeito").value,
        direcao: +document.querySelector("input[name=cau-dir]:checked").value, confundidor: $("cau-conf").checked, efeito_pct: +$("cau-ef").value, defasagem: +$("cau-df").value, ruido_pct: +$("cau-rf").value });
      out.innerHTML = `<h3>📈 Causa e efeito ao longo do tempo</h3>${graficoLinhas(r.serie.x, r.serie.series)}<h3>🔬 Amostra dos dados</h3>${tabelaDf(r.amostra)}
        <details class="card"><summary>🔍 Ver gabarito causal (spoiler, tente sua análise antes de abrir)</summary>${Object.entries(r.gabarito).map(([k, v]) => `<p><strong>${esc(k)}</strong>: ${esc(v)}</p>`).join("")}</details>
        <div class="linha-btn"><button class="btn" id="cau-b1">📥 Baixar dados (.csv)</button><button class="btn" id="cau-b2">📥 Baixar gabarito causal (.txt)</button></div>`;
      $("cau-b1").onclick = () => { baixar("dados_causais.csv", csvBlob(r.arquivos["dados_causais.csv"])); log("baixou_dados_causais"); };
      $("cau-b2").onclick = () => { baixar("gabarito_causal.txt", r.arquivos["gabarito_causal.txt"]); log("baixou_gabarito_causal"); };
      log("gerou_dados_causais", { setor_gerado: baseGerada().setor });
    } catch (err) { msgErro(out, err); }
  });
};

/* ── DAX Sandbox ───────────────────────────────────────────────────────── */
function desenharModelo(m) {
  const rel = m.relacoes.map((r) => `<li><strong>${esc(r.de)}</strong> → ${esc(r.para)} <span class="muted">(${{ direta: "muitos-para-um", data: "por data", indireta: "floco de neve" }[r.tipo]})</span></li>`).join("");
  return `<div class="modelo">${m.tabelas.map((t) => `<div class="tcard ${t.tipo}"><h5>${esc(t.nome)} <small>(${t.linhas.toLocaleString("pt-BR")})</small></h5><ul>${t.colunas.map((c) => `<li>${c === t.pk ? "🔑 " : ""}${esc(c)}</li>`).join("")}</ul></div>`).join("")}</div>
    <p class="muted">Fatos (amarelo), Dimensões (verde) e Calendário (azul). Relacionamentos detectados:</p><ul>${rel || "<li>Nenhum relacionamento detectado.</li>"}</ul>`;
}
TELAS.sandbox = (el) => {
  el.innerHTML = cab("🧮 DAX Sandbox", "Escreva uma medida DAX e veja o resultado calculado de verdade contra os dados do setor e volume escolhidos na barra lateral — não é só formatação, é o cálculo real nas linhas geradas. Suporta SUM, AVERAGE, MIN, MAX, COUNTROWS, DISTINCTCOUNT, DIVIDE, CALCULATE (com filtros, inclusive cruzando para uma dimensão relacionada) e operadores aritméticos.") +
    `<div class="linha-btn"><button class="btn" id="sb-rec">🔄 Carregar/recarregar dados do setor</button></div><div id="sb-corpo"></div>`;
  let modelo = null;
  const carregar = async () => {
    const c = $("sb-corpo"); carregando(c, "Carregando dados do setor…");
    try {
      modelo = await api("sandbox_modelo", { base: baseSidebar() });
      c.innerHTML = `<details class="card"><summary>📊 Modelo do setor (clique para ver)</summary>${desenharModelo(modelo)}</details>` +
        (modelo.exemplos.length ? `<label><span>Exemplos prontos</span><select id="sb-ex"><option value="">— escrever a minha —</option>${modelo.exemplos.map((x) => `<option>${esc(x)}</option>`).join("")}</select></label>`
          : `<div class="aviso">Não encontrei uma coluna numérica de medida neste setor para sugerir exemplos.</div>`) +
        `<label><span>Medida DAX</span><textarea rows="4" id="sb-expr" placeholder="${esc(modelo.fato ? `Total = SUM(${modelo.fato}[${modelo.medida}])` : "Total = SUM(Tabela[Coluna])")}"></textarea></label>
        <div class="linha-btn"><button class="btn primario" id="sb-go">▶️ Executar</button></div><div id="sb-out"></div>`;
      if ($("sb-ex")) $("sb-ex").onchange = (e) => { if (e.target.value) $("sb-expr").value = e.target.value; };
      $("sb-go").onclick = (e) => comBotao(e.currentTarget, async () => {
        const out = $("sb-out"); carregando(out, "Calculando…");
        try {
          const r = await api("sandbox_exec", { base: baseSidebar(), expressao: $("sb-expr").value });
          out.innerHTML = `<div class="card ok"><strong>${esc(r.nome)}</strong> = <strong>${fmt(r.valor, 4)}</strong></div><details class="card" open><summary>🔍 Passo a passo do cálculo</summary><ul>${r.passos.map((p) => `<li>${esc(p)}</li>`).join("")}</ul></details>`;
          log("dax_sandbox_executou", { setor_gerado: baseSidebar().setor });
        } catch (err) { msgErro(out, err); }
      });
    } catch (err) { msgErro(c, err); }
  };
  $("sb-rec").onclick = (e) => comBotao(e.currentTarget, async () => { saltBase = String(Math.random()); await carregar(); log("dax_sandbox_recarregou_dados"); });
  carregar();
};

/* ── Pergunte aos Dados ────────────────────────────────────────────────── */
TELAS.pergunte = (el) => {
  el.innerHTML = cab("💬 Pergunte aos Dados", "Escolha uma pergunta de negócio na lista e veja a resposta calculada de verdade contra os dados do setor e volume escolhidos na barra lateral, junto com a medida DAX equivalente. <strong>Importante:</strong> isto não é um assistente de IA — é um motor de reconhecimento de padrões, limitado a agregações (total, média, contagem, ranking, ticket médio), filtro por período e comparação entre dois períodos. Ele nunca prevê o futuro nem explica causas.") +
    `<div class="linha-btn"><button class="btn" id="qa-rec">🔄 Carregar/recarregar dados do setor</button></div><div id="qa-corpo"></div>`;
  const carregar = async () => {
    const c = $("qa-corpo"); carregando(c, "Montando a lista de perguntas possíveis para este setor…");
    try {
      const base = baseSidebar(), r = await api("qa_catalogo", { base });
      c.innerHTML = `<label><span>Sua pergunta — ${r.perguntas.length} perguntas possíveis neste setor</span><input type="search" id="qa-filtro" placeholder="Digite para filtrar (ex.: total, mês, maior)"></label>
        <select id="qa-sel" size="8" aria-label="Perguntas"></select><div class="linha-btn"><button class="btn primario" id="qa-go">🔎 Perguntar</button></div><div id="qa-out"></div>`;
      const lista = () => { const q = $("qa-filtro").value.toLowerCase(); $("qa-sel").innerHTML = r.perguntas.filter((p) => p.texto.toLowerCase().includes(q)).map((p) => `<option value="${esc(p.texto)}">${esc(p.categoria.split(" ")[0])}  ${esc(p.texto)}</option>`).join(""); };
      $("qa-filtro").oninput = lista; lista();
      $("qa-go").onclick = (e) => comBotao(e.currentTarget, async () => {
        const out = $("qa-out"), pergunta = $("qa-sel").value;
        if (!pergunta) return msgErro(out, "Escolha uma pergunta na lista antes de clicar em Perguntar.");
        carregando(out, "Calculando…");
        try {
          const a = await api("qa_perguntar", { base, pergunta });
          if (!a.entendida) { out.innerHTML = `<div class="card erro">Não consegui entender essa pergunta com o vocabulário que reconheço.</div>${(a.sugestoes || []).map((s) => `<p class="muted">💡 ${esc(s)}</p>`).join("")}`; return; }
          out.innerHTML = `<div class="card ok">${esc(a.resposta).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")}</div>${a.aviso ? `<div class="aviso">${esc(a.aviso)}</div>` : ""}<pre>${esc(a.dax)}</pre>` +
            (a.passos.length ? `<details class="card" open><summary>🔍 Passo a passo</summary><ul>${a.passos.map((p) => `<li>${esc(p)}</li>`).join("")}</ul></details>` : "") + (a.tabela ? tabelaDf(a.tabela) : "");
          log("qa_perguntou", { volume_linhas: pergunta.length });
        } catch (err) { msgErro(out, err); }
      });
    } catch (err) { msgErro(c, err); }
  };
  $("qa-rec").onclick = (e) => comBotao(e.currentTarget, async () => { saltBase = String(Math.random()); await carregar(); log("qa_recarregou_dados"); });
  carregar();
};

/* ── Automatizar BI ────────────────────────────────────────────────────── */
TELAS.automatizar = (el) => {
  el.innerHTML = cab("🤖 Automatizar BI", "Envie suas planilhas (.csv ou .xlsx, até ~3 MB no total). Depois de revisar o tipo de cada coluna, geramos automaticamente todas as medidas DAX que a tabela permite, incluindo Time Intelligence quando houver coluna de data.") +
    `<label><span>Envie uma ou mais planilhas</span><input type="file" id="au-file" accept=".csv,.xlsx" multiple></label><div id="au-out"></div>`;
  let arquivos = [], leitura = null;
  $("au-file").onchange = async (e) => {
    const out = $("au-out"); arquivos = [];
    if (!e.target.files.length) return (out.innerHTML = "");
    carregando(out, "Lendo as planilhas…");
    try {
      for (const f of e.target.files) arquivos.push({ nome: f.name, base64: await lerB64(f) });
      leitura = await api("automatizar_ler", { arquivos });
      out.innerHTML = `<div class="card ok">${leitura.tabelas.length} tabela(s) carregada(s): ${leitura.tabelas.map((x) => esc(x.nome)).join(", ")}</div>` +
        leitura.avisos_consolidacao.map((a) => `<div class="info">🔗 ${esc(a)}</div>`).join("") +
        (leitura.avisos_reparo.length ? `<div class="aviso">⚠️ As tabelas <strong>${leitura.avisos_reparo.map(esc).join(", ")}</strong> chegaram com todas as colunas numa única coluna de texto e foram reconstruídas usando vírgula como separador. Confira o preview.</div>` : "") +
        leitura.tabelas.map((t, ti) => `<details class="card"><summary>📄 ${esc(t.nome)} (${t.linhas.toLocaleString("pt-BR")} linhas, ${t.colunas.length} colunas)</summary>${tabelaDf(t.amostra)}
          <strong>Selecione o tipo de cada coluna:</strong><div class="grade">${t.colunas.map((c, ci) => `<label><span>${esc(c.nome)}</span><select data-t="${ti}" data-c="${ci}">${leitura.opcoes_tipo.map((o) => `<option${o === c.sugestao ? " selected" : ""}>${esc(o)}</option>`).join("")}</select></label>`).join("")}</div></details>`).join("") +
        `<div class="linha-btn"><button class="btn primario" id="au-go">🧮 Gerar medidas DAX</button></div><div id="au-res"></div>`;
      $("au-go").onclick = (ev) => comBotao(ev.currentTarget, gerar);
    } catch (err) { msgErro(out, err); }
  };
  async function gerar() {
    const res = $("au-res"); carregando(res, "Gerando medidas…");
    const tipos = {}; document.querySelectorAll("#au-out select[data-t]").forEach((s) => { const t = leitura.tabelas[+s.dataset.t]; (tipos[t.nome] = tipos[t.nome] || {})[t.colunas[+s.dataset.c].nome] = s.value; });
    try {
      const r = await api("automatizar_gerar", { arquivos, tipos });
      const tot = Object.values(r.medidas).reduce((a, cats) => a + Object.values(cats).reduce((b, l) => b + l.length, 0), 0);
      const pergs = Object.entries(r.perguntas || {});
      res.innerHTML = (pergs.length ? `<h3>❓ Perguntas de negócio para explorar seus dados</h3><p class="muted">Geradas a partir das colunas reais que você enviou, ancoradas nas medidas geradas abaixo.</p>` +
        pergs.map(([t, ps]) => `<details class="card"><summary>📄 ${esc(t)}</summary><ul>${ps.map((p) => `<li>${esc(p)}</li>`).join("")}</ul></details>`).join("") : "") +
        `<h3>🧮 Medidas DAX sugeridas (${tot})</h3>` + (r.calendario ? `<div class="info">📅 Uma tabela <strong>Calendario</strong> foi gerada (${r.calendario.de} a ${r.calendario.ate}), habilitando Time Intelligence. No Power BI, relacione <code>Calendario[Data]</code> com a coluna de data de cada tabela.</div>` : "") +
        Object.entries(r.medidas).map(([t, cats]) => `<h4>${esc(t)}</h4>` + Object.entries(cats).map(([c, l]) => `<details class="card"><summary>${esc(c)} (${l.length})</summary>${l.map((m) => `<pre>${esc(m.formula)}</pre>`).join("")}</details>`).join("")).join("") +
        `<div class="linha-btn" id="au-dl"></div><p class="muted">O modelo completo traz os CSVs de cada tabela + model.tmdl (tabelas, relacionamentos e medidas), pronto para importar no Power BI/Tabular Editor.</p>`;
      const dl = $("au-dl"); const add = (txt, fn) => { const b = document.createElement("button"); b.className = "btn"; b.textContent = txt; b.onclick = fn; dl.appendChild(b); };
      if (r.arquivos["medidas_automatizar_bi.txt"]) add("📥 Baixar todas as medidas (.txt)", () => { baixar("medidas_automatizar_bi.txt", r.arquivos["medidas_automatizar_bi.txt"]); log("automatizar_bi_baixou_medidas"); });
      if (r.arquivos["Calendario.csv"]) add("📥 Baixar tabela Calendario (.csv)", () => { baixar("Calendario.csv", csvBlob(r.arquivos["Calendario.csv"])); log("automatizar_bi_baixou_calendario"); });
      if (r.zip_base64) add("📥 Baixar modelo completo (.zip)", () => { baixar("modelo_automatizar_bi.zip", b64Blob(r.zip_base64, "application/zip")); log("automatizar_bi_baixou_modelo_zip"); });
      log("automatizar_bi_gerou_medidas", { volume_linhas: leitura.tabelas.length });
    } catch (err) { msgErro(res, err); }
  }
};
