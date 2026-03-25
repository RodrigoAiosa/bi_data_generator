"""ui/estado_inicial.py — Tela de boas-vindas (antes de gerar dados)."""

import streamlit as st

from config import SETORES_INFO


def render_estado_inicial() -> None:
    """Renderiza instruções de uso, flip-cards de setores e explicação do Star Schema."""

    # ── Como usar ──────────────────────────────────────────────────────────
    st.markdown('<h3 class="section-header">Como usar</h3>', unsafe_allow_html=True)
    st.markdown("""
    <div class="steps-grid">
        <div class="step-card">
            <span class="step-num">01</span>
            <span class="step-icon">🏭</span>
            <div class="step-title">Escolha o setor</div>
            <div class="step-text">Selecione entre 10 setores com dados contextualmente corretos</div>
        </div>
        <div class="step-card">
            <span class="step-num">02</span>
            <span class="step-icon">📅</span>
            <div class="step-title">Defina o período</div>
            <div class="step-text">Configure as datas — a dCalendario é gerada automaticamente</div>
        </div>
        <div class="step-card">
            <span class="step-num">03</span>
            <span class="step-icon">🚀</span>
            <div class="step-title">Clique em Gerar</div>
            <div class="step-text">A base completa é gerada em segundos com relações íntegras</div>
        </div>
        <div class="step-card">
            <span class="step-num">04</span>
            <span class="step-icon">📦</span>
            <div class="step-title">Baixe o .zip</div>
            <div class="step-text">CSVs prontos para importar no Power BI, Tableau ou Python</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Flip-cards de setores ──────────────────────────────────────────────
    st.markdown('<h3 class="section-header">Setores disponíveis</h3>', unsafe_allow_html=True)

    cards_html = '<div class="sector-grid">'
    for ico, nome, desc in SETORES_INFO:
        cards_html += f"""
        <div class="flip-wrapper">
          <div class="flip-inner">
            <div class="flip-front">
              <span class="sector-card-icon">{ico}</span>
              <div class="sector-card-name">{nome}</div>
            </div>
            <div class="flip-back">
              <div class="flip-back-title">{nome}</div>
              <div class="flip-back-desc">{desc}</div>
            </div>
          </div>
        </div>"""
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    # ── Star Schema info ───────────────────────────────────────────────────
    st.markdown('<h3 class="section-header">Estrutura Star Schema</h3>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        Cada base inclui <strong>Tabela Fato</strong> com chaves estrangeiras (<code>id_*</code>) e métricas,
        <strong>Tabelas Dimensão</strong> com chaves primárias e atributos descritivos, e
        <strong>dCalendario</strong> com Data, Ano, Mês, MesAno e IdMesAno — compatível com Power Query.
        Tudo exportado em CSVs compactados em um único <code>.zip</code>.
    </div>
    """, unsafe_allow_html=True)
