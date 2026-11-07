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
    sql_t: "🗄️ Gerar SQL", sql_hint: "Gera DDL, INSERT ou script completo para o setor selecionado.", sql_dial: "Dialeto", sql_tipo: "Tipo de script",
    sql_warn: "⚠️ INSERT usa o volume definido no controle acima.", sql_btn: "⬇️ Gerar & Baixar SQL", pptx: "📊 Apresentação (.pptx)",
    sql_ddl: "CREATE TABLE (DDL)", sql_ins: "INSERT INTO (dados)", sql_full: "Completo (DDL + INSERT + Relatórios)", sql_rel: "📊 Somente Relatórios Gerenciais (Views)",
    sql_gerando: "Gerando script SQL…", sql_prev: "👁️ Preview SQL", sql_trunc: "-- ... (truncado, baixe o arquivo para o script completo)",
    hero_s1: "setores", hero_s2: "linhas", hero_s3: "download", hero_s4: "grátis",
    achados: (n) => `${n} setor(es) encontrado(s)`, vazio: "Nenhum setor encontrado — mostrando todos.",
    avancado: "Opções avançadas", linhas_dica: "Aceita 5000, 5.000 ou 5k · de 100 a 100.000", atalho: "Atalhos: / busca · Ctrl+Enter gera",
    prox_t: "Próximos passos", prox_1: "Extraia o .zip em uma pasta.", prox_2: "Abra PowerBI/*.pbip no Power BI Desktop.", prox_3: "Teste as medidas DAX e tente resolver o case de negócio.",
    gate_sub: "Cadastre-se gratuitamente para gerar bases de dados para Power BI.",
    tab_novo: "Cadastrar", tab_existente: "Já sou cadastrado",
    leg_obrig: "obrigatório", opc: "(opcional)", d_cel: "DDD + 9 dígitos", d_ok: "✓ Tudo certo", e_nome: "Informe nome e sobrenome.", confianca: "🔒 Usamos seus dados só para identificar seu acesso e melhorar a ferramenta.", cadastrando: "Cadastrando…", f_nome: "Nome completo", f_sexo: "Sexo", f_cel: "Celular (com DDD)", f_uf: "Estado", f_cidade: "Cidade", c_escolha_uf: "Selecione o estado primeiro", c_carregando: "Carregando…", c_escolha: "Selecione a cidade", c_erro: "Não foi possível carregar as cidades",
    btn_cadastrar: "Cadastrar e entrar", btn_entrar: "Entrar", sair: "Sair",
    cfg: "⚙️ Configurações", busca: "Buscar setor", setor: "Setor", linhas: "Linhas na tabela fato",
    ini: "Data inicial", fim: "Data final", fiscal: "Início do ano fiscal",
    anomalia: "Injetar anomalias (causa raiz)", deriva: "Simular deriva temporal",
    gerar: "Gerar base agora", gerando: "Gerando…", indique: "🔗 Seu link de indicação", conv_t: "🎉 Cadastro concluído!", conv_p: "Convide colegas que estudam dados. Este é o seu link pessoal: quando alguém se cadastrar por ele, você vê quantas pessoas indicou.", conv_msg: "Pessoal, uso o BI Data Generator para treinar Power BI, DAX e SQL com bases realistas (200 setores, até 100 mil linhas). É gratuito: ", conv_wa: "WhatsApp", conv_li: "LinkedIn", conv_em: "E-mail", conv_ok: "Continuar", conv_res: (c, n) => `Seu link: ${c} clique(s) · ${n} cadastro(s) por indicação`, copiar: "Copiar", copiado: "Copiado!",
    hero_t: "Bases prontas para Power BI",
    hero_p: "Escolha um setor na barra lateral e clique em “Gerar base agora”. Você recebe um .zip com os CSVs das tabelas fato e dimensão, um projeto Power BI com painel de exemplo, medidas DAX, case de negócio e dicionário de dados.",
    resumo: "Resumo da base gerada", preview: "Preview das tabelas", case: "📖 Seu case de negócio",
    gab: "🔍 Gabarito (spoiler)", gab_ver: "Ver gabarito (revela onde estão as anomalias/deriva)",
    colunas: "colunas", linhas_u: "linhas",
    ok: (s, n, seg) => `✅ Base ${s} gerada com sucesso! ${n} tabelas prontas para download (${seg}s).`,
    baixar: (nome, mb) => `📥 Baixar ${nome} (${mb} MB)`,
    baixar_info: "O .zip inclui os CSVs, o projeto Power BI (PowerBI/*.pbip) que abre de qualquer pasta, o model.tmdl, o case de negócio, o gabarito (se houver), o dicionário de dados e o LEIA-ME.txt.",
    medidas: (n) => `🧮 Medidas DAX sugeridas (${n})`,
    e_email: "Informe um e-mail válido.", e_cel: "Informe um celular válido com DDD, ex.: (11) 99999-9999.",
    e_dup: "Este e-mail já está cadastrado. Use “Já sou cadastrado”.",
    e_nao: "E-mail não encontrado. Use a aba “Cadastrar”.", e_rede: "Não foi possível conectar. Tente novamente.",
    e_gen: "Não foi possível gerar a base.", e_per: "A data inicial deve ser anterior à final.",
    e_lin: "Informe entre 100 e 100.000 linhas.",
    prog: ["Criando dimensões…", "Gerando tabela fato…", "Calculando métricas…", "Compactando ZIP…"],
  },
  en: {
    sql_t: "🗄️ Generate SQL", sql_hint: "Generates DDL, INSERT or full script for the selected sector.", sql_dial: "Dialect", sql_tipo: "Script type",
    sql_warn: "⚠️ INSERT uses the volume set above.", sql_btn: "⬇️ Generate & Download SQL", pptx: "📊 Presentation (.pptx)",
    sql_ddl: "CREATE TABLE (DDL)", sql_ins: "INSERT INTO (data)", sql_full: "Full (DDL + INSERT + Reports)", sql_rel: "📊 Managerial Reports Only (Views)",
    sql_gerando: "Generating SQL script…", sql_prev: "👁️ SQL Preview", sql_trunc: "-- ... (truncated, download the file for the full script)",
    hero_s1: "sectors", hero_s2: "rows", hero_s3: "download", hero_s4: "free",
    achados: (n) => `${n} sector(s) found`, vazio: "No sector found — showing all.",
    avancado: "Advanced options", linhas_dica: "Accepts 5000, 5,000 or 5k · from 100 to 100,000", atalho: "Shortcuts: / search · Ctrl+Enter generates",
    prox_t: "Next steps", prox_1: "Unzip the file into a folder.", prox_2: "Open PowerBI/*.pbip in Power BI Desktop.", prox_3: "Try the DAX measures and solve the business case.",
    gate_sub: "Sign up for free to generate datasets for Power BI.",
    tab_novo: "Sign up", tab_existente: "I'm already registered",
    leg_obrig: "required", opc: "(optional)", d_cel: "Area code + 9 digits", d_ok: "✓ Looks good", e_nome: "Enter first and last name.", confianca: "🔒 We use your data only to identify your access and improve the tool.", cadastrando: "Signing up…", f_nome: "Full name", f_sexo: "Gender", f_cel: "Mobile (with area code)", f_uf: "State", f_cidade: "City", c_escolha_uf: "Select the state first", c_carregando: "Loading…", c_escolha: "Select the city", c_erro: "Could not load the cities",
    btn_cadastrar: "Sign up and enter", btn_entrar: "Enter", sair: "Sign out",
    cfg: "⚙️ Settings", busca: "Search sector", setor: "Sector", linhas: "Fact table rows",
    ini: "Start date", fim: "End date", fiscal: "Fiscal year start",
    anomalia: "Inject anomalies (root cause)", deriva: "Simulate temporal drift",
    gerar: "Generate dataset now", gerando: "Generating…", indique: "🔗 Your referral link", conv_t: "🎉 You're in!", conv_p: "Invite colleagues who study data. This is your personal link: when someone signs up through it, you can see how many people you referred.", conv_msg: "I use BI Data Generator to practice Power BI, DAX and SQL with realistic datasets (200 sectors, up to 100k rows). It's free: ", conv_wa: "WhatsApp", conv_li: "LinkedIn", conv_em: "E-mail", conv_ok: "Continue", conv_res: (c, n) => `Your link: ${c} click(s) · ${n} signup(s) by referral`, copiar: "Copy", copiado: "Copied!",
    hero_t: "Power BI-ready datasets",
    hero_p: "Pick a sector in the sidebar and click “Generate dataset now”. You get a .zip with the fact and dimension CSVs, a Power BI project with a sample dashboard, DAX measures, a business case and a data dictionary.",
    resumo: "Generated dataset summary", preview: "Table preview", case: "📖 Your business case",
    gab: "🔍 Answer key (spoiler)", gab_ver: "View answer key (reveals where the anomalies/drift are)",
    colunas: "columns", linhas_u: "rows",
    ok: (s, n, seg) => `✅ ${s} dataset generated! ${n} tables ready to download (${seg}s).`,
    baixar: (nome, mb) => `📥 Download ${nome} (${mb} MB)`,
    baixar_info: "The .zip contains the CSVs, the Power BI project (PowerBI/*.pbip) that opens from any folder, model.tmdl, the business case, the answer key (if any), the data dictionary and README.",
    medidas: (n) => `🧮 Suggested DAX measures (${n})`,
    e_email: "Enter a valid e-mail.", e_cel: "Enter a valid Brazilian mobile number with area code, e.g. (11) 99999-9999.",
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
    body: JSON.stringify(corpo), keepalive: true,
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

/* Origem do acesso: utm_source > indicação (?ref=) > domínio de referência > direto */
function origemAcesso() {
  const q = new URLSearchParams(location.search);
  const utm = (q.get("utm_source") || "").trim().toLowerCase().slice(0, 40);
  if (utm) return "utm:" + utm;
  if (q.get("ref")) return "indicação";
  try {
    const h = new URL(document.referrer).hostname.replace(/^www\./, "");
    if (h && h !== location.hostname.replace(/^www\./, "")) return h.slice(0, 60);
  } catch (_) {}
  return "direto";
}
/* Campanha (grupo/post): utm_campaign normalizado */
function campanhaAcesso() {
  const c = (new URLSearchParams(location.search).get("utm_campaign") || "").trim().toLowerCase().replace(/[^a-z0-9_-]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 80);
  return c || null;
}
const ssGet = (k) => { try { return sessionStorage.getItem(k); } catch (_) { return null; } };
const ssSet = (k, v) => { try { v == null ? sessionStorage.removeItem(k) : sessionStorage.setItem(k, v); } catch (_) {} };

/* A sessão começa na abertura do site (antes do cadastro) e segue após o login */
const REF_TTL = 30 * 864e5;
function guardarRef() {
  const ref = (new URLSearchParams(location.search).get("ref") || "").trim().toLowerCase();
  if (/^[a-z0-9]{6,32}$/.test(ref)) guardar("ref", JSON.stringify({ c: ref, t: Date.now() }));
}
function lerRef() {
  try { const o = JSON.parse(ler("ref") || "null"); if (o && /^[a-z0-9]{6,32}$/.test(o.c) && Date.now() - o.t < REF_TTL) return o.c; } catch (_) {}
  return null;
}
function iniciarSessao() {
  if (estado.sessao) return;
  const existente = ssGet("sessaoId");
  estado.sessao = existente || Math.random().toString(16).slice(2, 10);
  estado.inicio = Number(ssGet("sessaoInicio")) || Date.now();
  guardarRef();
  if (!existente) {
    ssSet("sessaoId", estado.sessao); ssSet("sessaoInicio", String(estado.inicio));
    const [d, n] = dispositivo();
    sb("logs_uso", { id_registro: estado.idRegistro, id_sessao: estado.sessao, tipo_evento: "sessao_inicio", acao: "abriu_site",
      origem: origemAcesso(), campanha: campanhaAcesso(), dispositivo: d, navegador: n, idioma_interface: estado.lang }, { Prefer: "return=minimal" }).catch(() => {});
    const ref = new URLSearchParams(location.search).get("ref");
    if (ref) {
      rpc("registrar_clique_compartilhamento", { p_codigo: ref, p_id_sessao: estado.sessao });
      history.replaceState(null, "", location.pathname);
    }
  }
  iniciarBatimento();
}

/* Batimento: a cada 60 s com a aba visível (máx. 120) e ao sair/ocultar a aba — mede o tempo real de uso */
let _batidas = 0, _timerBat = null;
function batimento(final = false) {
  if (!estado.sessao || _batidas >= 120) return;
  _batidas++;
  sb("logs_uso", { id_registro: estado.idRegistro, id_sessao: estado.sessao, tipo_evento: "batimento", acao: final ? "saiu_aba" : "batimento",
    duracao_segundos: Math.round((Date.now() - estado.inicio) / 1000) }, { Prefer: "return=minimal" }).catch(() => {});
}
function iniciarBatimento() {
  if (_timerBat) return;
  _timerBat = setInterval(() => { if (document.visibilityState === "visible") batimento(); }, 60000);
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") batimento(true); });
}

/* ── i18n ──────────────────────────────────────────────────────────────── */
function aplicarIdioma() {
  document.documentElement.lang = estado.lang === "en" ? "en" : "pt-BR";
  document.querySelectorAll("[data-i18n]").forEach((el) => { const v = TXT[estado.lang][el.dataset.i18n]; if (typeof v === "string") el.textContent = v; });
  [["conv-t", "conv_t"], ["conv-p", "conv_p"], ["conv-wa", "conv_wa"], ["conv-li", "conv_li"], ["conv-em", "conv_em"], ["conv-ok", "conv_ok"]].forEach(([i, k]) => { const el = $(i); if (el) el.textContent = t(k); });
  const cc = $("conv-copiar"); if (cc) cc.textContent = t("copiar");
  $("btn-lang").textContent = estado.lang === "pt" ? "EN" : "PT";
  $("gate-lang").textContent = estado.lang === "pt" ? "English" : "Português";
  const st_ = $("sql-tipo"), at = st_.value || "ddl";
  st_.innerHTML = [["ddl", "sql_ddl"], ["insert", "sql_ins"], ["completo", "sql_full"], ["relatorios", "sql_rel"]].map(([v, k]) => `<option value="${v}">${esc(t(k))}</option>`).join("");
  st_.value = at; $("sql-aviso").hidden = !["insert", "completo"].includes(at);
  const sel = $("mes-fiscal"), atual = sel.value || "1";
  sel.innerHTML = MESES[estado.lang].map((m, i) => `<option value="${i + 1}">${m}</option>`).join("");
  sel.value = atual;
  if (estado.resultado) desenhar(estado.resultado);
}
function trocarIdioma() { estado.lang = estado.lang === "pt" ? "en" : "pt"; guardar("idioma", estado.lang); aplicarIdioma(); log("trocou_idioma"); }

/* ── Cadastro / login ──────────────────────────────────────────────────── */
// E-mail: parte local sem pontos no início/fim/duplicados; domínio com rótulos válidos e TLD só com letras
const RE_EMAIL = /^(?!\.)(?!.*\.\.)[A-Za-z0-9._%+-]{1,64}(?<!\.)@(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,24}$/;
// Celular BR: DDD válido + 9 + 8 dígitos (11 dígitos), sem sequências repetidas
const RE_CEL = /^(?:1[1-9]|2[12478]|3[1-578]|4[1-9]|5[1345]|6[1-9]|7[1345779]|8[1-9]|9[1-9])9\d{8}$/;
let CAMPOS = [];
const nomeOk = (n) => { const v = (n || "").trim(); return v.length >= 5 && v.length <= 120 && /^\p{L}[\p{L}'’.\- ]*\s+\p{L}[\p{L}'’.\- ]*$/u.test(v); };
function validarCampo(c) {
  const vazio = !c.el.value.trim(), bom = !vazio && c.ok(c.el.value), d = $(c.dica);
  c.el.classList.toggle("invalido", !vazio && !bom); c.el.classList.toggle("valido", bom);
  c.el.setAttribute("aria-invalid", !vazio && !bom ? "true" : "false");
  c.el.setCustomValidity(vazio ? t(c.el.name === "email" ? "e_email" : c.msg) : bom ? "" : t(c.msg));
  d.className = "dica" + (bom ? " ok" : !vazio ? " erro" : "");
  d.textContent = bom ? t("d_ok") : !vazio ? t(c.msg) : (c.base ? t(c.base) : "");
  return bom;
}
const emailOk = (e) => { const v = (e || "").trim(); return v.length <= 254 && RE_EMAIL.test(v); };
const celOk = (c) => { const d = (c || "").replace(/\D+/g, ""); return RE_CEL.test(d) && !/^(\d)\1+$/.test(d.slice(2)); };
const soDigitos = (s) => (s || "").replace(/\D+/g, "");
function mascaraCel(v) {
  const d = soDigitos(v).slice(0, 11);
  if (d.length <= 2) return d ? `(${d}` : "";
  if (d.length <= 6) return `(${d.slice(0, 2)}) ${d.slice(2)}`;
  if (d.length <= 10) return `(${d.slice(0, 2)}) ${d.slice(2, 6)}-${d.slice(6)}`;
  return `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`;
}
const msgGate = (txt, ok = false) => { const m = $("gate-msg"); m.textContent = txt || ""; m.className = "msg" + (ok ? " ok" : ""); };

let _cidades = null;
async function carregarCidades(uf) {
  const sel = $("sel-cidade");
  const vazio = (txt) => `<option value="">${esc(txt)}</option>`;
  if (!uf) { sel.innerHTML = vazio(t("c_escolha_uf")); sel.disabled = true; return; }
  sel.disabled = true; sel.innerHTML = vazio(t("c_carregando"));
  try {
    if (!_cidades) _cidades = await (await fetch("/cidades.json")).json();
    const lista = _cidades[uf] || [];
    if (uf !== document.querySelector('select[name="estado"]').value) return; // trocou de estado enquanto carregava
    sel.innerHTML = vazio(t("c_escolha")) + lista.map((c) => `<option value="${esc(c)}">${esc(c)}</option>`).join("");
    sel.disabled = false;
  } catch (_) { sel.innerHTML = vazio(t("c_erro")); }
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
  CAMPOS.forEach((c) => { c.el.dataset.tocou = "1"; });
  const ruins = CAMPOS.filter((c) => !validarCampo(c));
  if (ruins.length) { ruins[0].el.focus(); return msgGate(t(ruins[0].msg)); }
  const cel = soDigitos(d.celular), mail = d.email.trim().toLowerCase();
  const btn = $("btn-cadastrar"), txt = btn.textContent;
  btn.disabled = true; btn.textContent = t("cadastrando"); btn.setAttribute("aria-busy", "true");
  const livre = () => { btn.disabled = false; btn.textContent = txt; btn.removeAttribute("aria-busy"); };
  let r;
  try {
    r = await sb("registros", { nome_completo: d.nome.trim(), sexo: d.sexo || null, email: mail, celular: cel, estado: d.estado || null, cidade: d.cidade || null, codigo_indicacao: lerRef() },
      { Prefer: "return=minimal" });
  } catch (_) { livre(); return msgGate(t("e_rede")); }
  if (r.status === 409) { livre(); return msgGate(t("e_dup")); }
  if (!r.ok) { livre(); return msgGate(t("e_rede")); }
  const id = await rpc("obter_id_registro", { p_email: mail });
  guardar("ref", null);
  livre();
  concluirLogin(mail, id, true);
}

function concluirLogin(email, id, novo = false) {
  estado.email = email; estado.idRegistro = id;
  guardar("email", email); guardar("idRegistro", id == null ? null : String(id));
  abrirApp(novo);
}

async function abrirApp(novo = false) {
  $("gate").hidden = true; $("app").hidden = false;
  aplicarIdioma();
  if (!estado.sessao) iniciarSessao();
  if (!estado.setores.length) await carregarSetores();
  if (estado.idRegistro) {
    const cod = await rpc("criar_link_compartilhamento", { p_id_registro: Number(estado.idRegistro) });
    if (typeof cod === "string" && cod) { $("link-ref").value = `${location.origin}/?ref=${cod}`; $("indicacao").hidden = false; if (novo) abrirConvite(); resumoIndicacoes(); }
  }
}

function linkIndicacao() { return $("link-ref").value; }
function textoConvite() { return t("conv_msg") + linkIndicacao(); }
function abrirConvite() {
  $("conv-link").value = linkIndicacao();
  const d = $("dlg-convite");
  if (typeof d.showModal === "function") d.showModal(); else d.setAttribute("open", "");
  log("viu_convite");
}
async function resumoIndicacoes() {
  if (!estado.idRegistro) return;
  const r = await rpc("resumo_indicacoes", { p_id_registro: Number(estado.idRegistro) });
  if (r && typeof r === "object") { $("ind-resumo").textContent = t("conv_res", r.cliques, r.cadastros); $("ind-resumo").hidden = false; }
}
function compartilhar(canal) {
  const url = linkIndicacao(), txt = textoConvite();
  const u = canal === "wa" ? "https://wa.me/?text=" + encodeURIComponent(txt)
    : canal === "li" ? "https://www.linkedin.com/sharing/share-offsite/?url=" + encodeURIComponent(url)
    : "mailto:?subject=" + encodeURIComponent("BI Data Generator") + "&body=" + encodeURIComponent(txt);
  log("compartilhou_" + canal);
  if (canal === "em") location.href = u; else window.open(u, "_blank", "noopener");
}

function sair() {
  guardar("email", null); guardar("idRegistro", null);
  estado.email = ""; estado.idRegistro = null; estado.sessao = ""; ssSet("sessaoId", null); ssSet("sessaoInicio", null);
  $("app").hidden = true; $("gate").hidden = false;
}

/* ── Setores e geração ─────────────────────────────────────────────────── */
/* Postel: aceita "5000", "5.000", "5 000", "5k", "1,5k" */
function lerLinhas(txt) {
  let v = String(txt || "").trim().toLowerCase().replace(/\s/g, "");
  const k = /k$/.test(v); v = v.replace(/k$/, "");
  if (k) v = v.replace(",", ".") ; else v = v.replace(/[.,](?=\d{3}(\D|$))/g, "");
  let n = parseFloat(v.replace(/[^0-9.]/g, "")); if (!isFinite(n)) return NaN;
  if (k) n *= 1000; return Math.round(n);
}
const linhasVal = () => { const n = lerLinhas($("linhas").value); return isFinite(n) ? n : NaN; };
function mostrarLinhas(n) { $("linhas").value = n.toLocaleString("pt-BR"); $("linhas-r").value = Math.min(100000, Math.max(100, n)); }
const normalizar = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
function preencherSetores() {
  const q = normalizar($("busca").value.trim()), sel = $("setor"), atual = sel.value;
  let lista = estado.setores.filter((s) => normalizar(s).includes(q));
  const info = $("busca-info");
  if (q && !lista.length) { info.textContent = t("vazio"); lista = estado.setores; } else info.textContent = q ? t("achados", lista.length) : "";
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
  const setor = $("setor").value, linhas = linhasVal();
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

async function gerarSql() {
  const out = $("sql-out"), btn = $("btn-sql");
  let base;
  try { base = baseSidebar(); } catch (e) { out.innerHTML = `<div class="card erro">${esc(e.message)}</div>`; return; }
  btn.disabled = true; out.innerHTML = `<p class="muted" role="status">⏳ ${esc(t("sql_gerando"))}</p>`;
  try {
    const r = await api("sql", { base, dialeto: $("sql-dial").value, tipo: $("sql-tipo").value });
    let href;
    if (r.url) href = r.url;
    else if (r.zip_base64) href = URL.createObjectURL(b64Blob(r.zip_base64, "application/zip"));
    else href = URL.createObjectURL(new Blob([r.sql], { type: "text/plain;charset=utf-8" }));
    out.innerHTML = `<p class="muted"><small>✅ ${estado.lang === "pt" ? "Gerado em" : "Generated in"} ${r.segundos}s</small></p>
      <a class="btn primario" href="${esc(href)}" download="${esc(r.nome)}">📥 ${esc(r.nome)} (${r.kb.toLocaleString("pt-BR")} KB)</a>
      <details open><summary>${esc(t("sql_prev"))}</summary><pre>${esc(r.preview)}${r.truncado ? "\n\n" + esc(t("sql_trunc")) : ""}</pre></details>`;
    out.querySelector("a").addEventListener("click", () => log("baixou_sql", { setor_gerado: base.setor }));
    log("gerou_sql", { setor_gerado: base.setor, volume_linhas: base.linhas });
  } catch (e) {
    out.innerHTML = `<div class="card erro">${esc(e.message)}</div>`;
    log("gerou_sql", { setor_gerado: base.setor, volume_linhas: base.linhas, status: "erro", erro_detalhe: String(e.message).slice(0, 200) });
  } finally { btn.disabled = false; }
}

/* ── Inicialização ─────────────────────────────────────────────────────── */
function iniciar() {
  const l = ler("idioma"); if (l === "en" || l === "pt") estado.lang = l; else if (/^en/i.test(navigator.language)) estado.lang = "en";
  document.querySelector('select[name="estado"]').innerHTML = '<option value="">—</option>' + UFS.map((u) => `<option>${u}</option>`).join("");
  carregarCidades("");
  const hoje = new Date(), ano = hoje.getFullYear();
  $("inicio").value = `${ano - 2}-01-01`; $("fim").value = `${ano}-12-31`;

  document.querySelectorAll(".tab").forEach((b) => b.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((x) => x.classList.toggle("ativo", x === b));
    $("form-novo").hidden = b.dataset.modo !== "novo"; $("form-existente").hidden = b.dataset.modo === "novo"; msgGate("");
  }));
  CAMPOS = [
    { el: document.querySelector('#form-novo input[name="nome"]'), ok: nomeOk, msg: "e_nome", dica: "d-nome", base: "" },
    { el: document.querySelector('#form-novo input[name="email"]'), ok: emailOk, msg: "e_email", dica: "d-email", base: "" },
    { el: document.querySelector('#form-novo input[name="celular"]'), ok: celOk, msg: "e_cel", dica: "d-cel", base: "d_cel" },
  ];
  CAMPOS.forEach((c) => {
    c.el.addEventListener("blur", () => { if (c.el.name !== "celular") c.el.value = c.el.value.trim(); c.el.dataset.tocou = "1"; validarCampo(c); });
    c.el.addEventListener("input", () => { if (c.el.name === "celular") c.el.value = mascaraCel(c.el.value); if (c.el.dataset.tocou) validarCampo(c); else c.el.setCustomValidity(""); });
  });
  document.querySelectorAll('#form-existente input[name="email"]').forEach((el) => el.addEventListener("input", () => el.setCustomValidity("")));
  document.querySelector('select[name="estado"]').addEventListener("change", (e) => carregarCidades(e.target.value));
  $("conv-copiar").addEventListener("click", async () => { try { await navigator.clipboard.writeText(textoConvite()); } catch (_) { $("conv-link").select(); document.execCommand("copy"); } $("conv-copiar").textContent = "✅ " + t("copiado"); log("copiou_link"); setTimeout(() => ($("conv-copiar").textContent = t("copiar")), 1500); });
  $("conv-wa").addEventListener("click", () => compartilhar("wa")); $("conv-li").addEventListener("click", () => compartilhar("li")); $("conv-em").addEventListener("click", () => compartilhar("em"));
  $("conv-ok").addEventListener("click", () => $("dlg-convite").close());
  $("form-novo").addEventListener("submit", (e) => { e.preventDefault(); msgGate(""); cadastrar(e.target); });
  $("form-existente").addEventListener("submit", (e) => {
    e.preventDefault(); msgGate(""); const em = new FormData(e.target).get("email").trim();
    emailOk(em) ? entrarComEmail(em) : msgGate(t("e_email"));
  });
  $("gate-lang").addEventListener("click", () => { trocarIdioma(); });
  $("btn-lang").addEventListener("click", trocarIdioma);
  $("btn-sair").addEventListener("click", sair);
  $("btn-menu").addEventListener("click", () => {
    if (window.matchMedia("(max-width:820px)").matches) $("lateral").classList.toggle("aberta");
    else document.querySelector(".corpo").classList.toggle("recolhido");
  });
  $("busca").addEventListener("input", preencherSetores);
  $("linhas-r").addEventListener("input", () => mostrarLinhas(Number($("linhas-r").value)));
  $("linhas").addEventListener("blur", () => { let n = linhasVal(); if (!isFinite(n)) n = 5000; mostrarLinhas(Math.min(100000, Math.max(100, n))); });
  $("linhas").setAttribute("maxlength", "9");
  $("linhas").addEventListener("input", () => {
    const n = linhasVal();
    if (isFinite(n) && n > 100000) { mostrarLinhas(100000); return; }   // teto: nunca aceita mais que 100.000
    if (isFinite(n)) $("linhas-r").value = Math.min(100000, Math.max(100, n));
  });
  $("busca").addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); $("btn-gerar").click(); } });
  document.addEventListener("keydown", (e) => {
    const alvo = e.target.tagName, digitando = ["INPUT", "TEXTAREA", "SELECT"].includes(alvo);
    if (e.key === "/" && !digitando && !$("app").hidden) { e.preventDefault(); $("busca").focus(); }
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey) && !$("app").hidden) { e.preventDefault(); $("btn-gerar").click(); }
  });
  $("sql-tipo").addEventListener("change", () => { $("sql-aviso").hidden = !["insert", "completo"].includes($("sql-tipo").value); });
  $("btn-pptx").addEventListener("click", () => log("baixou_apresentacao"));
  $("btn-sql").addEventListener("click", gerarSql);
  $("btn-gerar").addEventListener("click", () => { $("lateral").classList.remove("aberta"); gerar(); });
  $("btn-copiar").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText($("link-ref").value); $("btn-copiar").textContent = t("copiado"); setTimeout(() => ($("btn-copiar").textContent = t("copiar")), 1500); log("copiou_link"); } catch (_) { $("link-ref").select(); }
  });

  const email = ler("email");
  if (email) { estado.email = email; const id = ler("idRegistro"); estado.idRegistro = id ? Number(id) : null; abrirApp(); }
  else { $("gate").hidden = false; aplicarIdioma(); iniciarSessao(); }
}
document.addEventListener("DOMContentLoaded", iniciar);
