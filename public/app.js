/* BI Data Generator PRO — front-end nativo (Vercel + Supabase). Sem frameworks. */
"use strict";

const SUPABASE_URL = "https://rpryvxwvxeuyzpflzzfp.supabase.co";
// Chave pública (publishable): protegida por RLS no banco; nunca usar a service_role aqui.
const SUPABASE_KEY = "sb_publishable_jN6k32gqSQWvDNHfSIoPKg_NPKsn_P4";

const UFS = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"];
const MESES = {
  pt: ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"],
  en: ["January","February","March","April","May","June","July","August","September","October","November","December"],
};

const TXT = {
  pt: {
    gate_sub: "Cadastre-se gratuitamente para gerar bases de dados para Power BI.",
    tab_novo: "Cadastrar", tab_existente: "Já sou cadastrado",
    f_nome: "Nome completo", f_sexo: "Sexo", f_cel: "Celular (com DDD)", f_uf: "Estado", f_cidade: "Cidade",
    btn_cadastrar: "Cadastrar e entrar", btn_entrar: "Entrar", sair: "Sair",
    cfg: "⚙️ Configurações", busca: "Buscar setor", setor: "Setor", linhas: "Linhas na tabela fato",
    ini: "Data inicial", fim: "Data final", fiscal: "Início do ano fiscal",
    anomalia: "Injetar anomalias (causa raiz)", deriva: "Simular deriva temporal",
    gerar: "Gerar base agora", gerando: "Gerando…", indique: "🔗 Seu link de indicação", copiar: "Copiar", copiado: "Copiado!",
    hero_t: "Bases prontas para Power BI",
    hero_p: "Escolha um setor na barra lateral e clique em “Gerar base agora”. Você recebe um .zip com os CSVs das tabelas fato e dimensão, um projeto Power BI com painel de exemplo, medidas DAX, case de negócio e dicionário de dados.",
    resumo: "Resumo da base gerada", preview: "Preview das tabelas", case: "📖 Seu case de negócio",
    gab: "🔍 Gabarito (spoiler)", gab_ver: "Ver gabarito (revela onde estão as anomalias/deriva)",
    colunas: "colunas", linhas_u: "linhas",
    ok: (s, n, seg) => `✅ Base ${s} gerada com sucesso! ${n} tabelas prontas para download (${seg}s).`,
    baixar: (nome, mb) => `📥 Baixar ${nome} (${mb} MB)`,
    baixar_info: "O .zip inclui os CSVs, o projeto Power BI (PowerBI/*.pbip) que abre de qualquer pasta, o model.tmdl, o case de negócio, o gabarito (se houver), o dicionário de dados e o LEIA-ME.txt.",
    medidas: (n) => `🧮 Medidas DAX sugeridas (${n})`,
    e_email: "Informe um e-mail válido.", e_cel: "Informe o celular com DDD (10 ou 11 dígitos).",
    e_dup: "Este e-mail já está cadastrado. Use “Já sou cadastrado”.",
    e_nao: "E-mail não encontrado. Use a aba “Cadastrar”.", e_rede: "Não foi possível conectar. Tente novamente.",
    e_gen: "Não foi possível gerar a base.", e_per: "A data inicial deve ser anterior à final.",
    e_lin: "Informe entre 100 e 100.000 linhas.",
    prog: ["Criando dimensões…", "Gerando tabela fato…", "Calculando métricas…", "Compactando ZIP…"],
  },
  en: {
    gate_sub: "Sign up for free to generate datasets for Power BI.",
    tab_novo: "Sign up", tab_existente: "I'm already registered",
    f_nome: "Full name", f_sexo: "Gender", f_cel: "Mobile (with area code)", f_uf: "State", f_cidade: "City",
    btn_cadastrar: "Sign up and enter", btn_entrar: "Enter", sair: "Sign out",
    cfg: "⚙️ Settings", busca: "Search sector", setor: "Sector", linhas: "Fact table rows",
    ini: "Start date", fim: "End date", fiscal: "Fiscal year start",
    anomalia: "Inject anomalies (root cause)", deriva: "Simulate temporal drift",
    gerar: "Generate dataset now", gerando: "Generating…", indique: "🔗 Your referral link", copiar: "Copy", copiado: "Copied!",
    hero_t: "Power BI-ready datasets",
    hero_p: "Pick a sector in the sidebar and click “Generate dataset now”. You get a .zip with the fact and dimension CSVs, a Power BI project with a sample dashboard, DAX measures, a business case and a data dictionary.",
    resumo: "Generated dataset summary", preview: "Table preview", case: "📖 Your business case",
    gab: "🔍 Answer key (spoiler)", gab_ver: "View answer key (reveals where the anomalies/drift are)",
    colunas: "columns", linhas_u: "rows",
    ok: (s, n, seg) => `✅ ${s} dataset generated! ${n} tables ready to download (${seg}s).`,
    baixar: (nome, mb) => `📥 Download ${nome} (${mb} MB)`,
    baixar_info: "The .zip contains the CSVs, the Power BI project (PowerBI/*.pbip) that opens from any folder, model.tmdl, the business case, the answer key (if any), the data dictionary and README.",
    medidas: (n) => `🧮 Suggested DAX measures (${n})`,
    e_email: "Enter a valid e-mail.", e_cel: "Enter the mobile number with area code (10 or 11 digits).",
    e_dup: "This e-mail is already registered. Use “I'm already registered”.",
    e_nao: "E-mail not found. Use the “Sign up” tab.", e_rede: "Could not connect. Please try again.",
    e_gen: "Could not generate the dataset.", e_per: "Start date must be before end date.",
    e_lin: "Enter between 100 and 100,000 rows.",
    prog: ["Building dimensions…", "Generating fact table…", "Computing metrics…", "Compressing ZIP…"],
  },
};

const $ = (id) => document.getElementById(id);
const estado = { lang: "pt", idRegistro: null, email: "", sessao: "", inicio: Date.now(), setores: [], resultado: null, abaAtiva: 0 };

const t = (k, ...a) => { const v = TXT[estado.lang][k]; return typeof v === "function" ? v(...a) : v; };
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const guardar = (k, v) => { try { v == null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch (_) {} };
const ler = (k) => { try { return localStorage.getItem(k); } catch (_) { return null; } };

/* ── Supabase (REST/RPC com chave pública) ─────────────────────────────── */
async function sb(caminho, corpo, extra = {}) {
  const r = await fetch(`${SUPABASE_URL}/rest/v1/${caminho}`, {
    method: "POST",
    headers: { apikey: SUPABASE_KEY, Authorization: `Bearer ${SUPABASE_KEY}`, "Content-Type": "application/json", ...extra },
    body: JSON.stringify(corpo),
  });
  return r;
}
const rpc = async (nome, corpo) => { try { const r = await sb(`rpc/${nome}`, corpo); return r.ok ? await r.json() : null; } catch (_) { return null; } };

function dispositivo() {
  const ua = navigator.userAgent;
  const d = /Mobi|Android|iPhone/i.test(ua) ? "Mobile" : /iPad|Tablet/i.test(ua) ? "Tablet" : "Desktop";
  const n = /Edg\//.test(ua) ? "Edge" : /OPR\//.test(ua) ? "Opera" : /Chrome\//.test(ua) ? "Chrome" : /Firefox\//.test(ua) ? "Firefox" : /Safari\//.test(ua) ? "Safari" : "Outro";
  return [d, n];
}

function log(acao, extra = {}) {
  if (!estado.sessao) return;
  const p = {
    id_registro: estado.idRegistro, id_sessao: estado.sessao, tipo_evento: "clique", acao,
    duracao_segundos: Math.round((Date.now() - estado.inicio) / 1000), ...extra,
  };
  sb("logs_uso", p, { Prefer: "return=minimal" }).catch(() => {});
}

function iniciarSessao() {
  estado.sessao = Math.random().toString(16).slice(2, 10);
  estado.inicio = Date.now();
  const [d, n] = dispositivo();
  sb("logs_uso", { id_registro: estado.idRegistro, id_sessao: estado.sessao, tipo_evento: "sessao_inicio",
    dispositivo: d, navegador: n, idioma_interface: estado.lang }, { Prefer: "return=minimal" }).catch(() => {});
  const ref = new URLSearchParams(location.search).get("ref");
  if (ref) {
    rpc("registrar_clique_compartilhamento", { p_codigo: ref, p_id_sessao: estado.sessao });
    history.replaceState(null, "", location.pathname);
  }
}

/* ── i18n ──────────────────────────────────────────────────────────────── */
function aplicarIdioma() {
  document.documentElement.lang = estado.lang === "en" ? "en" : "pt-BR";
  document.querySelectorAll("[data-i18n]").forEach((el) => { const v = TXT[estado.lang][el.dataset.i18n]; if (typeof v === "string") el.textContent = v; });
  $("btn-lang").textContent = estado.lang === "pt" ? "EN" : "PT";
  $("gate-lang").textContent = estado.lang === "pt" ? "English" : "Português";
  const sel = $("mes-fiscal"), atual = sel.value || "1";
  sel.innerHTML = MESES[estado.lang].map((m, i) => `<option value="${i + 1}">${m}</option>`).join("");
  sel.value = atual;
  if (estado.resultado) desenhar(estado.resultado);
}
function trocarIdioma() { estado.lang = estado.lang === "pt" ? "en" : "pt"; guardar("idioma", estado.lang); aplicarIdioma(); log("trocou_idioma"); }

/* ── Cadastro / login ──────────────────────────────────────────────────── */
const emailOk = (e) => /^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$/.test((e || "").trim());
const soDigitos = (s) => (s || "").replace(/\D+/g, "");
function mascaraCel(v) {
  const d = soDigitos(v).slice(0, 11);
  if (d.length <= 2) return d ? `(${d}` : "";
  if (d.length <= 6) return `(${d.slice(0, 2)}) ${d.slice(2)}`;
  if (d.length <= 10) return `(${d.slice(0, 2)}) ${d.slice(2, 6)}-${d.slice(6)}`;
  return `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`;
}
const msgGate = (txt, ok = false) => { const m = $("gate-msg"); m.textContent = txt || ""; m.className = "msg" + (ok ? " ok" : ""); };

async function carregarCidades(uf) {
  const dl = $("lista-cidades"); dl.innerHTML = "";
  if (!uf) return;
  try {
    const r = await fetch(`https://servicodados.ibge.gov.br/api/v1/localidades/estados/${uf}/municipios`);
    const j = await r.json();
    dl.innerHTML = j.map((c) => `<option value="${esc(c.nome)}">`).join("");
  } catch (_) { /* campo de texto livre continua funcionando */ }
}

async function entrarComEmail(email) {
  const ok = await rpc("email_cadastrado", { p_email: email });
  if (ok === null) return msgGate(t("e_rede"));
  if (!ok) return msgGate(t("e_nao"));
  const id = await rpc("obter_id_registro", { p_email: email });
  concluirLogin(email, id);
}

async function cadastrar(f) {
  const d = Object.fromEntries(new FormData(f));
  if (!emailOk(d.email)) return msgGate(t("e_email"));
  const cel = soDigitos(d.celular);
  if (!/^\d{10,11}$/.test(cel)) return msgGate(t("e_cel"));
  let r;
  try {
    r = await sb("registros", { nome_completo: d.nome.trim(), sexo: d.sexo, email: d.email.trim(), celular: cel, estado: d.estado, cidade: d.cidade.trim() },
      { Prefer: "return=minimal" });
  } catch (_) { return msgGate(t("e_rede")); }
  if (r.status === 409) return msgGate(t("e_dup"));
  if (!r.ok) return msgGate(t("e_rede"));
  const id = await rpc("obter_id_registro", { p_email: d.email.trim() });
  concluirLogin(d.email.trim(), id);
}

function concluirLogin(email, id) {
  estado.email = email; estado.idRegistro = id;
  guardar("email", email); guardar("idRegistro", id == null ? null : String(id));
  abrirApp();
}

async function abrirApp() {
  $("gate").hidden = true; $("app").hidden = false;
  aplicarIdioma();
  if (!estado.sessao) iniciarSessao();
  if (!estado.setores.length) await carregarSetores();
  if (estado.idRegistro) {
    const cod = await rpc("criar_link_compartilhamento", { p_id_registro: Number(estado.idRegistro) });
    if (typeof cod === "string" && cod) { $("link-ref").value = `${location.origin}/?ref=${cod}`; $("indicacao").hidden = false; }
  }
}

function sair() {
  guardar("email", null); guardar("idRegistro", null);
  estado.email = ""; estado.idRegistro = null; estado.sessao = "";
  $("app").hidden = true; $("gate").hidden = false;
}

/* ── Setores e geração ─────────────────────────────────────────────────── */
const normalizar = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
function preencherSetores() {
  const q = normalizar($("busca").value.trim()), sel = $("setor"), atual = sel.value;
  const lista = estado.setores.filter((s) => normalizar(s).includes(q));
  sel.innerHTML = lista.map((s) => `<option>${esc(s)}</option>`).join("");
  if (lista.includes(atual)) sel.value = atual;
}
async function carregarSetores() {
  try { estado.setores = (await (await fetch("/api/setores")).json()).setores; } catch (_) { estado.setores = []; }
  preencherSetores();
}

function mostrarErro(txt) { const e = $("erro"); e.textContent = txt; e.hidden = !txt; }

async function gerar() {
  mostrarErro("");
  const setor = $("setor").value, linhas = parseInt($("linhas").value, 10);
  const inicio = $("inicio").value, fim = $("fim").value;
  if (!(linhas >= 100 && linhas <= 100000)) return mostrarErro(t("e_lin"));
  if (!inicio || !fim || inicio >= fim) return mostrarErro(t("e_per"));
  const anomalia = $("anomalia").checked, deriva = $("deriva").checked;

  const btn = $("btn-gerar"); btn.disabled = true; btn.textContent = t("gerando");
  $("hero").hidden = true; $("resultado").hidden = true; $("progresso").hidden = false;
  let i = 0; const passos = TXT[estado.lang].prog;
  const anima = () => { $("prog-txt").textContent = passos[Math.min(i, passos.length - 1)]; $("barra-in").style.width = [20, 50, 75, 92][Math.min(i, 3)] + "%"; i++; };
  anima(); const timer = setInterval(anima, linhas > 20000 ? 3500 : 1200);

  try {
    const base = { setor, linhas, inicio, fim, mes_fiscal: Number($("mes-fiscal").value), anomalia, deriva, idioma: estado.lang,
      seed: Math.floor(Math.random() * 2147483647) };
    const r = await fetch("/api/gerar", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(base) });
    let j = null; try { j = await r.json(); } catch (_) {}
    if (!r.ok || !j || !j.resumo) throw new Error((j && j.erro) || t("e_gen"));
    estado.resultado = j; estado.baseGerada = base;
    desenhar(j);
    log("gerou_base", { setor_gerado: setor, volume_linhas: linhas, anomalia_ativada: anomalia, deriva_temporal_ativada: deriva });
  } catch (e) {
    $("hero").hidden = false;
    mostrarErro(e.message || t("e_gen"));
    log("gerou_base", { setor_gerado: setor, volume_linhas: linhas, status: "erro", erro_detalhe: String(e.message).slice(0, 200) });
  } finally {
    clearInterval(timer); $("progresso").hidden = true; btn.disabled = false; btn.textContent = t("gerar");
  }
}

function urlDoZip(j) {
  if (j.zip_url) return j.zip_url;
  const bin = atob(j.zip_base64), buf = new Uint8Array(bin.length);
  for (let k = 0; k < bin.length; k++) buf[k] = bin.charCodeAt(k);
  return URL.createObjectURL(new Blob([buf], { type: "application/zip" }));
}

function desenhar(j) {
  const r = j.resumo;
  $("resultado").hidden = false;
  $("ok-txt").textContent = t("ok", r.setor, r.tabelas.length, r.segundos);
  const a = $("btn-baixar");
  if (a.dataset.blob) URL.revokeObjectURL(a.dataset.blob);
  const href = urlDoZip(j);
  a.href = href; a.download = j.zip_nome; a.dataset.blob = j.zip_url ? "" : href;
  a.textContent = t("baixar", j.zip_nome, (r.tamanho_zip / 1048576).toFixed(1));
  a.onclick = () => log("baixou_zip", { setor_gerado: r.setor });
  $("baixar-info").textContent = t("baixar_info");

  $("cards").innerHTML = r.tabelas.map((x) => {
    const ic = x.nome.startsWith("dCal") ? "📅" : x.nome.startsWith("Fato") ? "📊" : x.nome.startsWith("Bridge") ? "🔗" : "📋";
    return `<div class="stat"><small>${ic}</small><b>${x.linhas.toLocaleString(estado.lang === "pt" ? "pt-BR" : "en-US")}</b><span>${esc(x.nome)}</span><small>${x.colunas.length} ${t("colunas")}</small></div>`;
  }).join("");

  $("abas").innerHTML = r.tabelas.map((x, k) => `<button data-k="${k}" class="${k === estado.abaAtiva ? "ativo" : ""}">${esc(x.nome)}</button>`).join("");
  $("abas").onclick = (e) => { const b = e.target.closest("button"); if (b) { estado.abaAtiva = +b.dataset.k; desenhar(j); } };
  const tab = r.tabelas[Math.min(estado.abaAtiva, r.tabelas.length - 1)];
  $("tabela").innerHTML = `<table><thead><tr>${tab.colunas.map((c) => `<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>` +
    tab.amostra.map((l) => `<tr>${l.map((v) => `<td>${esc(v)}</td>`).join("")}</tr>`).join("") + "</tbody></table>";

  $("case").textContent = r.case.replace(/\*\*/g, "");
  $("gab-wrap").hidden = !(r.gabarito && r.gabarito.length);
  $("gab").innerHTML = (r.gabarito || []).map((g, k) => `<p><strong>${k + 1}. ${esc(g.tipo)}</strong><br><small>${esc(g.localizacao)}</small><br>${esc(g.detalhe)}</p>`).join("");

  let total = 0, html = "";
  for (const [fato, cats] of Object.entries(r.medidas)) {
    html += `<h4>${esc(fato)}</h4>`;
    for (const [cat, lista] of Object.entries(cats)) {
      total += lista.length;
      html += `<details class="card"><summary>${esc(cat)} (${lista.length})</summary>` +
        lista.map((m) => `<p><strong>${esc(m.nome)}</strong></p><pre>${esc(m.formula)}</pre><small class="muted">${esc(m.descricao)}</small>`).join("") + "</details>";
    }
  }
  $("med-t").textContent = t("medidas", total);
  $("medidas").innerHTML = html;
}

/* ── Inicialização ─────────────────────────────────────────────────────── */
function iniciar() {
  const l = ler("idioma"); if (l === "en" || l === "pt") estado.lang = l; else if (/^en/i.test(navigator.language)) estado.lang = "en";
  document.querySelector('select[name="estado"]').innerHTML = '<option value="">—</option>' + UFS.map((u) => `<option>${u}</option>`).join("");
  const hoje = new Date(), ano = hoje.getFullYear();
  $("inicio").value = `${ano - 2}-01-01`; $("fim").value = `${ano}-12-31`;

  document.querySelectorAll(".tab").forEach((b) => b.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((x) => x.classList.toggle("ativo", x === b));
    $("form-novo").hidden = b.dataset.modo !== "novo"; $("form-existente").hidden = b.dataset.modo === "novo"; msgGate("");
  }));
  document.querySelector('input[name="celular"]').addEventListener("input", (e) => { e.target.value = mascaraCel(e.target.value); });
  document.querySelector('select[name="estado"]').addEventListener("change", (e) => carregarCidades(e.target.value));
  $("form-novo").addEventListener("submit", (e) => { e.preventDefault(); msgGate(""); cadastrar(e.target); });
  $("form-existente").addEventListener("submit", (e) => {
    e.preventDefault(); msgGate(""); const em = new FormData(e.target).get("email").trim();
    emailOk(em) ? entrarComEmail(em) : msgGate(t("e_email"));
  });
  $("gate-lang").addEventListener("click", () => { trocarIdioma(); });
  $("btn-lang").addEventListener("click", trocarIdioma);
  $("btn-sair").addEventListener("click", sair);
  $("btn-menu").addEventListener("click", () => $("lateral").classList.toggle("aberta"));
  $("busca").addEventListener("input", preencherSetores);
  $("btn-gerar").addEventListener("click", () => { $("lateral").classList.remove("aberta"); gerar(); });
  $("btn-copiar").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText($("link-ref").value); $("btn-copiar").textContent = t("copiado"); setTimeout(() => ($("btn-copiar").textContent = t("copiar")), 1500); log("copiou_link"); } catch (_) { $("link-ref").select(); }
  });

  const email = ler("email");
  if (email) { estado.email = email; const id = ler("idRegistro"); estado.idRegistro = id ? Number(id) : null; abrirApp(); }
  else { $("gate").hidden = false; aplicarIdioma(); if (new URLSearchParams(location.search).get("ref")) iniciarSessao(); }
}
document.addEventListener("DOMContentLoaded", iniciar);
