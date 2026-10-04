"""
tests/test_cadastro.py

Testes do cadastro obrigatório (gate) antes do uso do app:
  - data_acesso.py: chamadas REST ao Supabase (mockando requests.post,
    sem depender de rede nem de credenciais reais).
  - ui/cadastro.py + gate em app.py: fluxo completo via AppTest, simulando
    Supabase "configurado" (monkeypatch em data_acesso._config) para
    exercitar o bloqueio de verdade — sem isso, o ambiente de teste (sem
    st.secrets) sempre libera o acesso (fail-open), então o gate nunca
    apareceria nos testes.
"""
from pathlib import Path
from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

import data_acesso
import ui.cadastro as cadastro_ui

_CAMINHO_APP = str(Path(__file__).resolve().parent.parent / "app.py")


# ── data_acesso: unitários, sem rede ────────────────────────────────────────

def test_nao_configurado_sem_secrets():
    """Sem supabase_url/supabase_anon_key em st.secrets, o módulo se declara
    não configurado — é o que garante o fail-open (dev local/CI/testes)."""
    assert data_acesso.esta_configurado() is False


def test_email_valido():
    assert data_acesso.email_valido("ana@exemplo.com") is True
    assert data_acesso.email_valido("nao-e-email") is False
    assert data_acesso.email_valido("") is False
    assert data_acesso.email_valido("ana@exemplo") is False  # sem TLD
    assert data_acesso.email_valido("ana@@exemplo.com") is False


def test_celular_valido_aceita_so_digitos_com_ddd():
    assert data_acesso.celular_valido("11999999999") is True   # celular, 11 dígitos
    assert data_acesso.celular_valido("1133334444") is True    # fixo, 10 dígitos


def test_celular_valido_aceita_formatado_mas_valida_pelos_digitos():
    """O usuário pode digitar com máscara — validamos pelos dígitos, mas
    quem persiste (cadastrar) sempre limpa antes de gravar."""
    assert data_acesso.celular_valido("(11) 99999-9999") is True


def test_celular_valido_rejeita_tamanho_errado_ou_letras():
    assert data_acesso.celular_valido("123") is False
    assert data_acesso.celular_valido("") is False
    assert data_acesso.celular_valido("abc99999999") is False


def test_limpar_celular_remove_tudo_que_nao_e_digito():
    assert data_acesso.limpar_celular("(11) 99999-9999") == "11999999999"
    assert data_acesso.limpar_celular("+55 11 99999-9999") == "5511999999999"


def test_cadastrar_grava_celular_limpo(monkeypatch):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    capturado = {}

    def _post_fake(url, json, headers, timeout):
        if url.endswith("/rest/v1/registros"):
            capturado["celular"] = json["celular"]
            return Mock(status_code=201, text="")
        return Mock(status_code=200, json=lambda: 1)  # rpc/obter_id_registro

    monkeypatch.setattr(data_acesso.requests, "post", _post_fake)
    data_acesso.cadastrar("Ana", "Feminino", "ana@exemplo.com", "(11) 99999-9999", "SP", "São Paulo")
    assert capturado["celular"] == "11999999999"


def test_email_cadastrado_sem_configuracao_retorna_none():
    assert data_acesso.email_cadastrado("ana@exemplo.com") is None


def test_obter_id_registro_sem_configuracao_retorna_none():
    assert data_acesso.obter_id_registro("ana@exemplo.com") is None


def test_obter_id_registro_encontrado(monkeypatch):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    resp = Mock(status_code=200)
    resp.json.return_value = 42
    monkeypatch.setattr(data_acesso.requests, "post", lambda *a, **k: resp)
    assert data_acesso.obter_id_registro("ana@exemplo.com") == 42


def test_obter_id_registro_nao_encontrado(monkeypatch):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    resp = Mock(status_code=200)
    resp.json.return_value = None
    monkeypatch.setattr(data_acesso.requests, "post", lambda *a, **k: resp)
    assert data_acesso.obter_id_registro("ninguem@exemplo.com") is None


def test_cadastrar_sem_configuracao_retorna_erro_amigavel():
    ok, erro, id_registro = data_acesso.cadastrar("Ana", "Feminino", "ana@exemplo.com", "11999999999", "SP", "São Paulo")
    assert ok is False
    assert erro != ""
    assert id_registro is None


def test_email_cadastrado_true(monkeypatch):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    resp = Mock(status_code=200)
    resp.json.return_value = True
    monkeypatch.setattr(data_acesso.requests, "post", lambda *a, **k: resp)
    assert data_acesso.email_cadastrado("ana@exemplo.com") is True


def test_email_cadastrado_false(monkeypatch):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    resp = Mock(status_code=200)
    resp.json.return_value = False
    monkeypatch.setattr(data_acesso.requests, "post", lambda *a, **k: resp)
    assert data_acesso.email_cadastrado("ninguem@exemplo.com") is False


def test_email_cadastrado_erro_rede_retorna_none(monkeypatch):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))

    def _explode(*a, **k):
        raise ConnectionError("sem rede")

    monkeypatch.setattr(data_acesso.requests, "post", _explode)
    assert data_acesso.email_cadastrado("ana@exemplo.com") is None


def test_cadastrar_sucesso(monkeypatch):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))

    def _post_fake(url, json=None, headers=None, timeout=None):
        if url.endswith("/rest/v1/registros"):
            # "return=minimal": INSERT bem-sucedido não devolve corpo (a
            # tabela só tem política de SELECT... na verdade não tem
            # nenhuma, de propósito — ver comentário em cadastrar()).
            return Mock(status_code=201, text="")
        return Mock(status_code=200, json=lambda: 7)  # rpc/obter_id_registro

    monkeypatch.setattr(data_acesso.requests, "post", _post_fake)
    ok, erro, id_registro = data_acesso.cadastrar("Ana", "Feminino", "ana@exemplo.com", "11999999999", "SP", "São Paulo")
    assert ok is True
    assert erro == ""
    assert id_registro == 7


def test_cadastrar_email_duplicado(monkeypatch):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    resp = Mock(status_code=409, text="duplicate key value violates unique constraint")
    monkeypatch.setattr(data_acesso.requests, "post", lambda *a, **k: resp)
    ok, erro, id_registro = data_acesso.cadastrar("Ana", "Feminino", "ana@exemplo.com", "11999999999", "SP", "São Paulo")
    assert ok is False
    assert erro == "duplicado"
    assert id_registro is None


def test_cadastrar_erro_rede(monkeypatch):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))

    def _explode(*a, **k):
        raise ConnectionError("sem rede")

    monkeypatch.setattr(data_acesso.requests, "post", _explode)
    ok, erro, id_registro = data_acesso.cadastrar("Ana", "Feminino", "ana@exemplo.com", "11999999999", "SP", "São Paulo")
    assert ok is False
    assert erro == "erro_rede"
    assert id_registro is None


# ── Gate completo, simulando Supabase configurado ───────────────────────────

def _rodar_com_supabase_configurado(monkeypatch) -> AppTest:
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    at = AppTest.from_file(_CAMINHO_APP, default_timeout=180)
    at.run()
    assert not at.exception
    return at


def test_gate_bloqueia_quando_supabase_configurado(monkeypatch):
    """Com Supabase 'configurado' e sem cadastro na sessão, o resto do app
    (sidebar com o seletor de 200 setores, abas do gerador) não deve
    renderizar — só a tela de cadastro."""
    at = _rodar_com_supabase_configurado(monkeypatch)
    # O seletor de setor (>100 opções) só existe depois do gate liberar.
    assert not any(len(s.options) > 100 for s in at.sidebar.selectbox)
    # A tela de cadastro tem os campos de texto do formulário.
    assert len(at.text_input) >= 5


def test_gate_libera_apos_cadastro_bem_sucedido(monkeypatch):
    """Simula a API do IBGE fora do ar (retorna []) — o campo cidade deve
    cair para texto livre, e o cadastro precisa continuar funcionando."""
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    monkeypatch.setattr(data_acesso.requests, "post", lambda *a, **k: Mock(status_code=201, text=""))
    monkeypatch.setattr(cadastro_ui, "buscar_cidades", lambda uf: [])

    at = AppTest.from_file(_CAMINHO_APP, default_timeout=180)
    at.run()

    # Preenche todos os campos de texto do formulário de cadastro (primeira
    # aba) com valores válidos e envia.
    for ti in at.text_input:
        rotulo = (ti.label or "").lower()
        if "mail" in rotulo:
            valor = "ana@exemplo.com"
        elif "celular" in rotulo or "phone" in rotulo:
            valor = "11999999999"
        else:
            valor = "Preenchido"
        ti.set_value(valor)

    botao = next(b for b in at.button if _s_btn_cadastrar(b))
    botao.click().run()
    assert not at.exception
    assert bool(at.session_state.get("cadastro_ok")) is True


def _s_btn_cadastrar(botao) -> bool:
    return botao.label in ("Cadastrar e começar", "Register and start")


def test_cidade_vira_selectbox_quando_ha_lista_de_cidades(monkeypatch):
    """Quando o IBGE responde, a cidade deixa de ser texto livre e vira uma
    lista das cidades do estado selecionado."""
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    monkeypatch.setattr(data_acesso.requests, "post", lambda *a, **k: Mock(status_code=201, text=""))
    monkeypatch.setattr(cadastro_ui, "buscar_cidades", lambda uf: ["Campinas", "São Paulo"] if uf == "SP" else [])

    at = AppTest.from_file(_CAMINHO_APP, default_timeout=180)
    at.run()

    # Estado padrão do selectbox é o primeiro (AC) — troca pra SP, que tem
    # cidades mockadas, disparando o rerun que popula o seletor de cidade.
    estado_sel = next(s for s in at.selectbox if s.label in ("Estado", "State"))
    estado_sel.set_value("SP").run()

    cidade_sel = next(s for s in at.selectbox if s.label in ("Cidade", "City"))
    assert list(cidade_sel.options) == ["Campinas", "São Paulo"]
    cidade_sel.set_value("São Paulo")

    for ti in at.text_input:
        rotulo = (ti.label or "").lower()
        if "mail" in rotulo:
            ti.set_value("ana@exemplo.com")
        elif "celular" in rotulo or "phone" in rotulo:
            ti.set_value("11999999999")
        else:
            ti.set_value("Preenchido")

    botao = next(b for b in at.button if _s_btn_cadastrar(b))
    botao.click().run()
    assert not at.exception
    assert bool(at.session_state.get("cadastro_ok")) is True


def test_estado_outro_nao_busca_cidades(monkeypatch):
    """'Fora do Brasil / Outro' deve manter cidade como texto livre e nunca
    chamar a API do IBGE."""
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    chamadas = []
    monkeypatch.setattr(cadastro_ui, "buscar_cidades", lambda uf: chamadas.append(uf) or [])

    at = AppTest.from_file(_CAMINHO_APP, default_timeout=180)
    at.run()

    estado_sel = next(s for s in at.selectbox if s.label in ("Estado", "State"))
    estado_sel.set_value("Fora do Brasil / Outro").run()

    # A primeira renderização (estado padrão "AC") busca cidades normalmente;
    # o que importa é que, com "Outro" selecionado, a UF especial nunca é
    # passada pra buscar_cidades.
    assert "Fora do Brasil / Outro" not in chamadas
    assert not any(s.label in ("Cidade", "City") for s in at.selectbox)
    assert any((ti.label or "") in ("Cidade", "City") for ti in at.text_input)


def test_gate_fail_open_sem_configuracao_nao_bloqueia():
    """Sem secrets (caso real deste ambiente de teste/CI), o gate nunca deve
    aparecer — é a rede de segurança que garante que a suíte antiga
    (test_app_tabs.py) continua funcionando sem depender do Supabase."""
    at = AppTest.from_file(_CAMINHO_APP, default_timeout=180)
    at.run()
    assert not at.exception
    assert len(at.tabs) == 11


# ── Link de divulgação (compartilhamento + rastreio de cliques) ─────────────

def _rpc_fake(respostas, chamadas):
    def _post(url, json, headers, timeout):
        nome = url.rsplit("/", 1)[-1]
        chamadas.append((nome, json))
        valor = respostas.get(nome)
        if valor is None:
            return Mock(status_code=500, text="erro")
        return Mock(status_code=200, json=lambda: valor)
    return _post


def test_criar_link_compartilhamento_devolve_codigo(monkeypatch):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    chamadas = []
    monkeypatch.setattr(data_acesso.requests, "post",
                        _rpc_fake({"criar_link_compartilhamento": "abc123def4"}, chamadas))
    assert data_acesso.criar_link_compartilhamento(7) == "abc123def4"
    assert chamadas == [("criar_link_compartilhamento", {"p_id_registro": 7})]


def test_criar_link_compartilhamento_falhas_viram_none(monkeypatch):
    assert data_acesso.criar_link_compartilhamento(7) is None          # sem config
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    assert data_acesso.criar_link_compartilhamento(None) is None       # sem id
    monkeypatch.setattr(data_acesso.requests, "post", _rpc_fake({}, []))
    assert data_acesso.criar_link_compartilhamento(7) is None          # HTTP 500

    def _explode(*a, **k):
        raise RuntimeError("rede")
    monkeypatch.setattr(data_acesso.requests, "post", _explode)
    assert data_acesso.criar_link_compartilhamento(7) is None          # exceção


def test_registrar_clique_compartilhamento(monkeypatch):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    chamadas = []
    monkeypatch.setattr(data_acesso.requests, "post",
                        _rpc_fake({"registrar_clique_compartilhamento": True}, chamadas))
    assert data_acesso.registrar_clique_compartilhamento("abc123def4", "s1") is True
    assert chamadas[0][1] == {"p_codigo": "abc123def4", "p_id_sessao": "s1"}
    assert data_acesso.registrar_clique_compartilhamento("", "s1") is False
    monkeypatch.setattr(data_acesso.requests, "post",
                        _rpc_fake({"registrar_clique_compartilhamento": False}, []))
    assert data_acesso.registrar_clique_compartilhamento("x" * 10, "s1") is False


def test_url_compartilhamento():
    assert data_acesso.montar_url_compartilhamento("abc") == \
        "https://ai-bidatagenerator.streamlit.app/?ref=abc"


def test_ref_na_url_registra_clique_uma_vez_por_sessao(monkeypatch):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    chamadas = []
    monkeypatch.setattr(data_acesso.requests, "post",
                        _rpc_fake({"registrar_clique_compartilhamento": True}, chamadas))
    at = AppTest.from_file(_CAMINHO_APP, default_timeout=180)
    at.query_params["ref"] = "abc123def4"
    at.run()
    assert not at.exception
    at.run()  # rerun na mesma sessão: não pode duplicar
    cliques = [c for c in chamadas if c[0] == "registrar_clique_compartilhamento"]
    assert len(cliques) == 1
    assert cliques[0][1]["p_codigo"] == "abc123def4"
    assert cliques[0][1]["p_id_sessao"] == at.session_state["id_sessao"]


def test_sem_ref_nao_registra_clique(monkeypatch):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    chamadas = []
    monkeypatch.setattr(data_acesso.requests, "post",
                        _rpc_fake({"registrar_clique_compartilhamento": True}, chamadas))
    at = AppTest.from_file(_CAMINHO_APP, default_timeout=180)
    at.run()
    assert not at.exception
    assert not [c for c in chamadas if c[0] == "registrar_clique_compartilhamento"]


def _cadastrar_novo_usuario(monkeypatch, codigo):
    monkeypatch.setattr(data_acesso, "_config", lambda: ("https://fake.supabase.co", "chave"))
    respostas = {"obter_id_registro": 5}
    if codigo:
        respostas["criar_link_compartilhamento"] = codigo

    def _post(url, json, headers, timeout):
        if url.endswith("/rest/v1/registros"):
            return Mock(status_code=201, text="")
        return _rpc_fake(respostas, [])(url, json, headers, timeout)

    monkeypatch.setattr(data_acesso.requests, "post", _post)
    monkeypatch.setattr(cadastro_ui, "buscar_cidades", lambda uf: [])
    at = AppTest.from_file(_CAMINHO_APP, default_timeout=180)
    at.run()
    for ti in at.text_input:
        rotulo = (ti.label or "").lower()
        ti.set_value("ana@exemplo.com" if "mail" in rotulo
                     else "11999999999" if ("celular" in rotulo or "phone" in rotulo)
                     else "Preenchido")
    next(b for b in at.button if _s_btn_cadastrar(b)).click().run()
    assert not at.exception
    return at


def test_apos_cadastro_mostra_link_de_divulgacao(monkeypatch):
    at = _cadastrar_novo_usuario(monkeypatch, "abc123def4")
    assert at.session_state["cadastro_ok"] is True
    # Ainda na tela de compartilhar: o app principal não renderizou.
    assert not any(len(s.options) > 100 for s in at.sidebar.selectbox)
    assert any("?ref=abc123def4" in c.value for c in at.code)
    # "Continuar" libera o app e não mostra a tela de novo.
    next(b for b in at.button if b.key == "share_continuar_btn").click().run()
    assert not at.exception
    assert any(len(s.options) > 100 for s in at.sidebar.selectbox)
    assert not any("?ref=" in c.value for c in at.code)


def test_cadastro_sem_codigo_de_link_vai_direto_pro_app(monkeypatch):
    """Se a RPC de link falhar, a tela de compartilhar é pulada (fail-open)."""
    at = _cadastrar_novo_usuario(monkeypatch, None)
    assert at.session_state["cadastro_ok"] is True
    assert any(len(s.options) > 100 for s in at.sidebar.selectbox)
