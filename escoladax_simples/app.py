"""
app.py
EscolaDAX — Gerador de dados fictícios (modelo estrela) + bateria de medidas DAX
por setor de negócio, para praticar Power BI / DAX / modelagem dimensional.
"""

from datetime import date

import streamlit as st

from generators_bi import (
    SETORES,
    RELACIONAMENTOS,
    to_zip,
    gerar_bateria_medidas,
)

st.set_page_config(page_title="EscolaDAX", page_icon="📊", layout="wide")

# ------------------------------------------------------------------------
# Cabeçalho
# ------------------------------------------------------------------------
st.title("📊 EscolaDAX")
st.caption(
    "Gere dados fictícios em modelo estrela (fato + dimensões) para o setor "
    "que você quiser, baixe os CSVs e receba uma bateria pronta de medidas "
    "DAX para praticar no Power BI."
)

# ------------------------------------------------------------------------
# Barra lateral — parâmetros
# ------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Parâmetros")

    setor = st.selectbox("Setor de negócio", list(SETORES.keys()))

    n_linhas = st.slider(
        "Quantidade de linhas na tabela fato",
        min_value=100,
        max_value=10_000,
        value=2_000,
        step=100,
    )

    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data inicial", value=date(2023, 1, 1))
    with col2:
        data_fim = st.date_input("Data final", value=date(2025, 12, 31))

    gerar = st.button("🚀 Gerar dados", type="primary", use_container_width=True)

# ------------------------------------------------------------------------
# Estado da sessão
# ------------------------------------------------------------------------
if "dados_setor" not in st.session_state:
    st.session_state.dados_setor = None
    st.session_state.setor_atual = None

if gerar:
    if data_inicio >= data_fim:
        st.error("A data inicial precisa ser anterior à data final.")
    else:
        with st.spinner("Gerando dados fictícios..."):
            gerador = SETORES[setor]
            st.session_state.dados_setor = gerador(n_linhas, data_inicio, data_fim)
            st.session_state.setor_atual = setor

dados_setor = st.session_state.dados_setor

# ------------------------------------------------------------------------
# Conteúdo principal
# ------------------------------------------------------------------------
if dados_setor is None:
    st.info("👈 Escolha um setor e clique em **Gerar dados** para começar.")
else:
    setor_atual = st.session_state.setor_atual
    fato_key = next(k for k in dados_setor if k.startswith("Fato"))
    fato = dados_setor[fato_key]

    tab_dados, tab_modelo, tab_medidas = st.tabs(
        ["🗂️ Tabelas", "🔗 Modelo Estrela", "🧮 Medidas DAX"]
    )

    # ---- Aba 1: tabelas ---------------------------------------------------
    with tab_dados:
        st.subheader(f"Tabelas geradas — {setor_atual}")

        c1, c2, c3 = st.columns(3)
        c1.metric("Tabelas", len(dados_setor))
        c2.metric(f"Linhas em {fato_key}", f"{len(fato):,}".replace(",", "."))
        c3.metric("Período", f"{data_inicio:%d/%m/%Y} – {data_fim:%d/%m/%Y}")

        nome_tabela = st.selectbox("Tabela", list(dados_setor.keys()))
        st.dataframe(dados_setor[nome_tabela], use_container_width=True)

        st.download_button(
            "⬇️ Baixar todas as tabelas (.zip de CSVs)",
            data=to_zip(dados_setor),
            file_name=f"{setor_atual.split(' ', 1)[-1].lower()}_escoladax.zip",
            mime="application/zip",
            use_container_width=True,
        )

    # ---- Aba 2: modelo estrela ---------------------------------------------
    with tab_modelo:
        st.subheader("Relacionamentos do modelo estrela")
        relacionamentos = RELACIONAMENTOS.get(setor_atual, [])
        if relacionamentos:
            st.table(
                [
                    {
                        "Tabela origem": origem,
                        "Coluna (FK)": coluna,
                        "Tabela destino": destino,
                        "Coluna (PK)": pk,
                    }
                    for origem, coluna, destino, pk in relacionamentos
                ]
            )
        else:
            st.warning("Nenhum relacionamento cadastrado para este setor.")

    # ---- Aba 3: medidas DAX -------------------------------------------------
    with tab_medidas:
        st.subheader("Bateria de medidas DAX geradas")
        relacionamentos = RELACIONAMENTOS.get(setor_atual, [])
        medidas = gerar_bateria_medidas(dados_setor, fato_key, relacionamentos)

        for categoria, lista in medidas.items():
            if not lista:
                continue
            with st.expander(f"{categoria} ({len(lista)})", expanded=False):
                for m in lista:
                    st.markdown(f"**{m['nome']}**")
                    st.code(m["formula"], language="dax")
                    st.caption(m["descricao"])
                    st.divider()
