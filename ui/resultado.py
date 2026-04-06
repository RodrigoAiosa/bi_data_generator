"""ui/resultado.py — Métricas, preview de tabelas, dashboard e download."""

import pandas as pd
import streamlit as st

from generators.helpers import to_zip


def render_resultado(nome: str, tabelas: dict[str, pd.DataFrame]) -> None:
    """Renderiza métricas, abas de preview e botão de download do ZIP."""

    st.markdown(
        f'<div class="success-box">✅ Base <strong>{nome}</strong> gerada com sucesso!'
        f' {len(tabelas)} tabelas prontas para download.</div>',
        unsafe_allow_html=True,
    )

    # ── Resumo das tabelas ─────────────────────────────────────────────────
    st.markdown('<h3 class="section-header-plain">Resumo da base gerada</h3>', unsafe_allow_html=True)

    n_cols = min(len(tabelas), 7)
    cols   = st.columns(n_cols)

    for i, (tname, tdf) in enumerate(tabelas.items()):
        # Ícone baseado no tipo da tabela
        if tname.startswith("dCal"):
            icon = "📅"
        elif tname.startswith("Fato"):
            icon = "📊"
        elif tname.startswith("Bridge"):
            icon = "🔗"
        else:
            icon = "📋"
            
        with cols[i % n_cols]:
            st.markdown(f"""
            <div class="stat-card">
                <span class="stat-card-icon">{icon}</span>
                <span class="stat-number">{len(tdf):,}</span>
                <span class="stat-label">{tname}</span>
                <span class="stat-sublabel">{len(tdf.columns)} colunas</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Preview das tabelas (incluindo bridges) ────────────────────────────
    st.markdown('<h3 class="section-header">Preview das tabelas</h3>', unsafe_allow_html=True)

    # Separar tabelas principais e bridges
    main_tables = {k: v for k, v in tabelas.items() if not k.startswith("Bridge")}
    bridge_tables = {k: v for k, v in tabelas.items() if k.startswith("Bridge")}
    
    # Tabs para tabelas principais
    if main_tables:
        tabs = st.tabs(list(main_tables.keys()))
        for tab, (tname, tdf) in zip(tabs, main_tables.items()):
            with tab:
                st.dataframe(tdf.head(20), use_container_width=True)
                st.caption(f"{len(tdf):,} linhas · {len(tdf.columns)} colunas")
    
    # Exibir bridges em expansor separado (se existirem)
    if bridge_tables:
        with st.expander("🔗 Tabelas Bridge (Relacionamentos N:N)"):
            for tname, tdf in bridge_tables.items():
                st.markdown(f"**{tname}**")
                st.dataframe(tdf.head(20), use_container_width=True)
                st.caption(f"{len(tdf):,} linhas · {len(tdf.columns)} colunas")
                st.divider()

    # ── Download ───────────────────────────────────────────────────────────
    st.markdown('<h3 class="section-header-plain">Download</h3>', unsafe_allow_html=True)

    zip_bytes    = to_zip(tabelas)
    nome_arquivo = f"Base_BI_{nome.replace(' ', '_')}.zip"

    st.download_button(
        label=f"📥 Baixar {nome_arquivo}",
        data=zip_bytes,
        file_name=nome_arquivo,
        mime="application/zip",
        use_container_width=True,
        type="primary",
    )

    st.markdown("""
    <div class="info-box">
        <strong>💡 Dica Power BI:</strong> Importe os CSVs e crie relações usando as colunas
        <code>sk_*</code> (FK) da tabela Fato para as respectivas dimensões.
        Conecte <code>dCalendario[Data]</code> ao campo de data da tabela Fato.
    </div>
    """, unsafe_allow_html=True)


def render_dashboard(nome: str, tabelas: dict[str, pd.DataFrame]) -> None:
    """Renderiza dashboard interativo com métricas e visualizações básicas."""
    
    st.markdown(f'<h3 class="section-header">📊 Dashboard - {nome}</h3>', unsafe_allow_html=True)
    
    # Identificar a tabela fato (principal)
    fato_tables = [name for name in tabelas.keys() if name.startswith("Fato")]
    
    if not fato_tables:
        st.info("ℹ️ Nenhuma tabela fato encontrada para gerar o dashboard.")
        return
    
    fato_name = fato_tables[0]
    fato_df = tabelas[fato_name]
    
    # ── Métricas principais ────────────────────────────────────────────────
    st.markdown('<h4 class="section-header-plain">📈 Métricas Gerais</h4>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total de Registros", f"{len(fato_df):,}")
    
    with col2:
        # Tenta encontrar coluna de valor/monetária
        valor_patterns = ['valor', 'total', 'preco', 'diaria', 'receita', 'custo', 'comissao']
        valor_cols = [col for col in fato_df.columns if any(p in col.lower() for p in valor_patterns)]
        
        if valor_cols:
            total_valor = fato_df[valor_cols[0]].sum()
            st.metric(f"💰 Total {valor_cols[0]}", f"R$ {total_valor:,.2f}")
        else:
            # Conta chaves estrangeiras como alternativa
            fk_cols = [col for col in fato_df.columns if col.startswith('sk_')]
            st.metric("🔗 Relacionamentos", f"{len(fk_cols)} dimensões")
    
    with col3:
        # Tenta encontrar coluna de quantidade/tempo
        qtd_patterns = ['qtd', 'quantidade', 'dias', 'minutos', 'horas', 'duracao']
        qtd_cols = [col for col in fato_df.columns if any(p in col.lower() for p in qtd_patterns)]
        
        if qtd_cols:
            total_qtd = fato_df[qtd_cols[0]].sum()
            # Formatação inteligente
            if 'minutos' in qtd_cols[0].lower():
                st.metric(f"⏱️ Total {qtd_cols[0]}", f"{total_qtd:,.0f} min")
            elif 'dias' in qtd_cols[0].lower():
                st.metric(f"📅 Total {qtd_cols[0]}", f"{total_qtd:,.0f} dias")
            else:
                st.metric(f"📦 Total {qtd_cols[0]}", f"{total_qtd:,.0f}")
        else:
            st.metric("📋 Colunas", f"{len(fato_df.columns)}")
    
    with col4:
        st.metric("🗂️ Tabelas no Modelo", f"{len(tabelas)}")
    
    st.divider()
    
    # ── Preview dos dados da Fato ──────────────────────────────────────────
    st.markdown('<h4 class="section-header-plain">🔍 Preview da Tabela Fato</h4>', unsafe_allow_html=True)
    st.dataframe(fato_df.head(100), use_container_width=True)
    
    # ── Distribuições simples ──────────────────────────────────────────────
    # Identificar colunas categóricas e numéricas
    categorical_cols = fato_df.select_dtypes(include=['object', 'category']).columns.tolist()
    numeric_cols = fato_df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    if categorical_cols or numeric_cols:
        st.markdown('<h4 class="section-header-plain">📊 Análises Rápidas</h4>', unsafe_allow_html=True)
        
        col_left, col_right = st.columns(2)
        
        # Gráfico de barras para colunas categóricas (esquerda)
        with col_left:
            if categorical_cols:
                # Filtra colunas com poucas categorias
                valid_cats = [col for col in categorical_cols if fato_df[col].nunique() <= 15 and fato_df[col].nunique() > 1]
                if valid_cats:
                    selected_cat = st.selectbox("Distribuição por categoria:", valid_cats, key="cat_select")
                    if selected_cat:
                        st.markdown(f"**{selected_cat}**")
                        st.bar_chart(fato_df[selected_cat].value_counts().head(10))
                else:
                    st.info("Nenhuma coluna categórica com distribuição relevante.")
            else:
                st.info("Nenhuma coluna categórica disponível.")
        
        # Gráfico de linha para séries temporais (direita)
        with col_right:
            # Procura coluna de data
            date_cols = [col for col in fato_df.columns if 'data' in col.lower() or 'date' in col.lower()]
            if date_cols and numeric_cols:
                date_col = date_cols[0]
                fato_df[date_col] = pd.to_datetime(fato_df[date_col])
                
                # Permite agrupar por período
                period = st.selectbox("Agrupar por:", ["Dia", "Mês", "Trimestre"], key="period_select")
                
                if period == "Dia":
                    grouped = fato_df.groupby(fato_df[date_col].dt.date)[numeric_cols[0]].sum()
                elif period == "Mês":
                    grouped = fato_df.groupby(fato_df[date_col].dt.to_period("M"))[numeric_cols[0]].sum()
                else:
                    grouped = fato_df.groupby(fato_df[date_col].dt.to_period("Q"))[numeric_cols[0]].sum()
                
                st.markdown(f"**Evolução de {numeric_cols[0]} ao longo do tempo**")
                st.line_chart(grouped)
            else:
                st.info("Colunas de data ou numéricas não encontradas para análise temporal.")
    
    # ── Tabelas Bridge (se existirem) ──────────────────────────────────────
    bridge_tables = {k: v for k, v in tabelas.items() if k.startswith("Bridge")}
    if bridge_tables:
        with st.expander("🔗 Tabelas Bridge (Relacionamentos N:N)"):
            for tname, tdf in bridge_tables.items():
                st.markdown(f"**{tname}**")
                st.dataframe(tdf.head(50), use_container_width=True)
                st.caption(f"{len(tdf):,} relações")
                st.divider()
    
    # ── Dicas de relacionamento ────────────────────────────────────────────
    st.markdown("""
    <div class="info-box" style="margin-top: 20px;">
        <strong>💡 Dica para Power BI / Tableau:</strong><br>
        • Conecte as colunas <code>sk_*</code> (FK) da tabela Fato às respectivas dimensões<br>
        • Use <code>dCalendario[Data]</code> para análises temporais<br>
        • Tabelas Bridge (🔗) resolvem relações muitos-para-muitos (N:N)<br>
        • Para melhor performance, mantenha as relações 1:N entre dimensões e fato
    </div>
    """, unsafe_allow_html=True)
