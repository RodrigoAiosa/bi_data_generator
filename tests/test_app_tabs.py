"""
tests/test_app_tabs.py

Testes de fumaça (smoke tests) das 10 abas: clica nos botões de verdade
via streamlit.testing.v1.AppTest e confere ausência de exceção. Não
substitui os testes de unidade mais específicos (test_relacionamentos.py,
test_pbip_generation.py) — é a rede de segurança que pega quando alguma
mudança quebra a MONTAGEM da UI em si (import errado, key duplicada,
argumento faltando), que os testes de unidade não veem porque testam só
as funções de generators/ diretamente, sem passar pelo Streamlit.
"""
from pathlib import Path

from streamlit.testing.v1 import AppTest

_CAMINHO_APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _rodar_app() -> AppTest:
    at = AppTest.from_file(_CAMINHO_APP, default_timeout=180)
    at.run()
    assert not at.exception, f"Exceção ao carregar o app: {at.exception}"
    return at


def _selecionar_setor(at: AppTest, trecho_nome: str) -> None:
    seletor = [s for s in at.sidebar.selectbox if len(s.options) > 100][0]
    opcao = next(o for o in seletor.options if trecho_nome in o)
    seletor.set_value(opcao).run()


def test_carrega_sem_excecao():
    _rodar_app()


def test_sidebar_sem_aviso_de_label_vazio(capsys):
    """Achado no QA anterior: 4 widgets da sidebar usavam label="" +
    label_visibility="collapsed", gerando aviso do proprio Streamlit sobre
    acessibilidade (label vazio nao serve pra leitor de tela). Corrigido
    dando um label de verdade a cada um (o mesmo texto ja mostrado
    visualmente acima via markdown customizado), mantendo escondido
    visualmente. Este teste trava que isso nao volte."""
    _rodar_app()
    saida = capsys.readouterr()
    texto_completo = saida.out + saida.err
    assert "empty value" not in texto_completo.lower()
    assert "label got" not in texto_completo.lower()


def test_gerador_de_setores():
    at = _rodar_app()
    btn = next(b for b in at.button if b.label == "Gerar base agora")
    btn.click().run()
    assert not at.exception


def test_automatizar_bi_carrega():
    # Smoke test simples: a aba renderiza sem exigir upload de arquivo.
    at = _rodar_app()
    assert not at.exception


def test_simulador_pl300():
    at = _rodar_app()
    btn = next(b for b in at.button if "ortear" in (b.label or ""))
    btn.click().run()
    assert not at.exception


def test_dados_causais():
    at = _rodar_app()
    btn_gerar = next(b for b in at.button if b.label == "Gerar base agora")
    btn_gerar.click().run()
    btn_causal = next(b for b in at.button if "ausal" in (b.label or ""))
    btn_causal.click().run()
    assert not at.exception


def test_formatar_dax():
    at = _rodar_app()
    entrada = next(t for t in at.text_area if t.key == "formatar_dax_entrada")
    entrada.set_value('Total=CALCULATE(SUM(FatoVendas[valor]),FatoVendas[canal]="Loja")').run()
    btn = next(b for b in at.button if b.key == "btn_formatar_dax")
    btn.click().run()
    assert not at.exception


def test_formatar_m():
    at = _rodar_app()
    entrada = next(t for t in at.text_area if t.key == "formatar_m_entrada")
    entrada.set_value('let Origem = Csv.Document(File.Contents("C:\\dados.csv")) in Origem').run()
    btn = next(b for b in at.button if b.key == "btn_formatar_m")
    btn.click().run()
    assert not at.exception


def test_auditor_de_modelo():
    at = _rodar_app()
    tmdl = "\ttable FatoVendas\n\t\tmeasure 'Total' = SUM(FatoVendas[valor])\n"
    entrada = next(t for t in at.text_area if t.key == "auditor_tmdl_entrada")
    entrada.set_value(tmdl).run()
    btn = next(b for b in at.button if b.key == "btn_auditar_modelo")
    btn.click().run()
    assert not at.exception


def test_dax_sandbox():
    at = _rodar_app()
    btn_carregar = next(b for b in at.button if b.key == "dax_sandbox_carregar")
    btn_carregar.click().run()
    assert not at.exception


def test_pergunte_aos_dados():
    at = _rodar_app()
    btn_carregar = next(b for b in at.button if b.key == "qa_carregar")
    btn_carregar.click().run()
    entrada = next(t for t in at.text_input if t.key == "qa_pergunta")
    entrada.set_value("Quantos registros existem?").run()
    btn_perguntar = next(b for b in at.button if b.key == "qa_perguntar")
    btn_perguntar.click().run()
    assert not at.exception


def test_carrossel_power_bi_carrega():
    # Smoke test simples: a aba renderiza sem exigir upload de arquivo.
    at = _rodar_app()
    assert not at.exception


def test_botao_download_pptx_presente():
    at = _rodar_app()
    btns = [b for b in at.download_button if b.key == "dl_apresentacao_pptx"]
    assert len(btns) == 1


def test_botao_pbip_marcado_como_beta():
    """O template .pbip já passou por 3 rodadas de correção com base em
    erros reais do Power BI Desktop — precisa continuar sinalizado como
    beta até ganhar mais confiança (não remover este teste sem decisão
    consciente de "promover" a funcionalidade)."""
    at = _rodar_app()
    btn_gerar = next(b for b in at.button if b.label == "Gerar base agora")
    btn_gerar.click().run()

    btns_pbip = [b for b in at.download_button if "pbip" in (b.label or "").lower()]
    assert len(btns_pbip) == 1
    assert "Beta" in btns_pbip[0].label

    avisos_beta = [w for w in at.warning if "Beta" in w.value]
    assert len(avisos_beta) == 1
