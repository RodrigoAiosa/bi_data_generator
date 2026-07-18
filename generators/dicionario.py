"""generators/dicionario.py — Gera dicionário de dados em CSV (PT/EN)."""

import io
import zipfile
import pandas as pd

# ── Descrições PT ─────────────────────────────────────────────────────────────

_DESC_PT: dict[str, str] = {
    # IDs
    "id_":              "Identificador único",
    "sk_":              "Surrogate key (chave substituta)",
    # Datas
    "data_":            "Data do evento",
    "id_data":          "Chave para dCalendario",
    "vencimento":       "Data de vencimento",
    "validade":         "Data de validade",
    # Valores monetários
    "valor_":           "Valor monetário (R$)",
    "receita":          "Receita gerada (R$)",
    "custo_":           "Custo associado (R$)",
    "preco_":           "Preço unitário (R$)",
    "desconto":         "Desconto aplicado",
    "margem":           "Margem percentual",
    "honorario":        "Honorário cobrado (R$)",
    "salario":          "Salário (R$)",
    "frete":            "Valor de frete (R$)",
    "lucro":            "Lucro apurado (R$)",
    "orcamento":        "Orçamento previsto (R$)",
    # Quantidades
    "qtd_":             "Quantidade",
    "volume_":          "Volume físico",
    "quantidade":       "Quantidade de unidades",
    "peso_":            "Peso (kg)",
    "distancia_":       "Distância (km)",
    "duracao_":         "Duração",
    "horas_":           "Horas",
    "litros":           "Volume em litros",
    # Status / flags booleanos
    "status":           "Status do registro",
    "ativo":            "Indica se o registro está ativo",
    "cancelado":        "Indica se foi cancelado",
    "aprovado":         "Indica se foi aprovado",
    "pago":             "Indica se foi pago",
    "concluido":        "Indica se foi concluído",
    "inadimplente":     "Indica inadimplência",
    "devolvido":        "Indica se foi devolvido",
    "ganho":            "Indica se foi ganho",
    "perdido":          "Indica se foi perdido",
    "entregue":         "Indica se foi entregue",
    "ativo":            "Indica se está ativo",
    "ruptura":          "Indica ruptura de estoque",
    "preventiva":       "Indica manutenção preventiva",
    # Textos comuns
    "nome":             "Nome descritivo",
    "descricao":        "Descrição detalhada",
    "tipo_":            "Classificação por tipo",
    "categoria":        "Categoria de negócio",
    "canal":            "Canal de origem ou venda",
    "regiao":           "Região geográfica",
    "uf":               "Unidade federativa (estado)",
    "cidade":           "Município",
    "cnpj":             "CNPJ da empresa",
    "cpf":              "CPF do indivíduo",
    "cnh":              "Carteira Nacional de Habilitação",
    "email":            "Endereço de e-mail",
    "telefone":         "Número de telefone",
    "placa":            "Placa do veículo",
    "marca":            "Marca do produto/veículo",
    "modelo":           "Modelo do produto/veículo",
    "endereco":         "Endereço completo",
    "segmento":         "Segmento de mercado",
    "modalidade":       "Modalidade de atendimento/operação",
    "motivo":           "Motivo ou razão",
    "estagio":          "Estágio do processo",
    "cargo":            "Cargo ou função",
    "especialidade":    "Especialidade profissional",
    # Métricas
    "pct":              "Percentual (%)",
    "taxa_":            "Taxa percentual (%)",
    "score":            "Pontuação / índice",
    "avaliacao":        "Nota de avaliação (1–5)",
    "nps":              "Net Promoter Score (0–100)",
    "mrr":              "Monthly Recurring Revenue",
    "arr":              "Annual Recurring Revenue",
    "churn":            "Indicador de cancelamento / churn",
    "cac":              "Custo de Aquisição de Cliente",
    "ltv":              "Lifetime Value do cliente",
    "roi":              "Retorno sobre investimento (%)",
    "roas":             "Return on Ad Spend",
    "ctr":              "Click-Through Rate (%)",
    "cpc":              "Custo por Clique (R$)",
    "cpa":              "Custo por Aquisição (R$)",
    "fcr":              "Feed Conversion Ratio",
    "map":              "Incremento Médio Anual de Produção",
    "consumo_":         "Consumo registrado",
    "eficiencia":       "Índice de eficiência (%)",
    "produtividade":    "Índice de produtividade",
    "capacidade":       "Capacidade máxima",
    "km_":              "Quilometragem",
}

# ── Descrições EN ─────────────────────────────────────────────────────────────

_DESC_EN: dict[str, str] = {
    # IDs
    "id_":              "Unique identifier",
    "sk_":              "Surrogate key",
    # Dates
    "data_":            "Event date",
    "id_data":          "Foreign key to Calendar table",
    "vencimento":       "Due date",
    "validade":         "Expiration date",
    # Monetary
    "valor_":           "Monetary value (R$)",
    "receita":          "Generated revenue (R$)",
    "custo_":           "Associated cost (R$)",
    "preco_":           "Unit price (R$)",
    "desconto":         "Applied discount",
    "margem":           "Profit margin percentage",
    "honorario":        "Professional fee (R$)",
    "salario":          "Salary (R$)",
    "frete":            "Freight value (R$)",
    "lucro":            "Net profit (R$)",
    "orcamento":        "Budgeted amount (R$)",
    # Quantities
    "qtd_":             "Quantity",
    "volume_":          "Physical volume",
    "quantidade":       "Number of units",
    "peso_":            "Weight (kg)",
    "distancia_":       "Distance (km)",
    "duracao_":         "Duration",
    "horas_":           "Hours",
    "litros":           "Volume in liters",
    # Boolean flags
    "status":           "Record status",
    "ativo":            "Indicates whether the record is active",
    "cancelado":        "Indicates whether it was cancelled",
    "aprovado":         "Indicates whether it was approved",
    "pago":             "Indicates whether it was paid",
    "concluido":        "Indicates whether it was completed",
    "inadimplente":     "Indicates payment default",
    "devolvido":        "Indicates whether it was returned",
    "ganho":            "Indicates a won deal",
    "perdido":          "Indicates a lost deal",
    "entregue":         "Indicates successful delivery",
    "ruptura":          "Indicates stock outage",
    "preventiva":       "Indicates preventive maintenance",
    # Text
    "nome":             "Descriptive name",
    "descricao":        "Detailed description",
    "tipo_":            "Type classification",
    "categoria":        "Business category",
    "canal":            "Origin or sales channel",
    "regiao":           "Geographic region",
    "uf":               "Brazilian state abbreviation",
    "cidade":           "City / municipality",
    "cnpj":             "Brazilian company tax ID (CNPJ)",
    "cpf":              "Brazilian individual tax ID (CPF)",
    "cnh":              "Brazilian driver's license number",
    "email":            "Email address",
    "telefone":         "Phone number",
    "placa":            "Vehicle license plate",
    "marca":            "Product or vehicle brand",
    "modelo":           "Product or vehicle model",
    "endereco":         "Full address",
    "segmento":         "Market segment",
    "modalidade":       "Service or operation modality",
    "motivo":           "Reason or cause",
    "estagio":          "Process stage",
    "cargo":            "Job title or role",
    "especialidade":    "Professional specialty",
    # Metrics
    "pct":              "Percentage (%)",
    "taxa_":            "Percentage rate (%)",
    "score":            "Score or index",
    "avaliacao":        "Rating (1–5)",
    "nps":              "Net Promoter Score (0–100)",
    "mrr":              "Monthly Recurring Revenue",
    "arr":              "Annual Recurring Revenue",
    "churn":            "Churn / cancellation indicator",
    "cac":              "Customer Acquisition Cost",
    "ltv":              "Customer Lifetime Value",
    "roi":              "Return on Investment (%)",
    "roas":             "Return on Ad Spend",
    "ctr":              "Click-Through Rate (%)",
    "cpc":              "Cost per Click (R$)",
    "cpa":              "Cost per Acquisition (R$)",
    "fcr":              "Feed Conversion Ratio",
    "map":              "Mean Annual Production increment",
    "consumo_":         "Recorded consumption",
    "eficiencia":       "Efficiency index (%)",
    "produtividade":    "Productivity index",
    "capacidade":       "Maximum capacity",
    "km_":              "Mileage / distance in km",
}

# ── Tipo de dado PT/EN ────────────────────────────────────────────────────────

_TIPO_MAP_PT = {
    "int64":          "Inteiro",
    "int32":          "Inteiro",
    "float64":        "Decimal",
    "float32":        "Decimal",
    "object":         "Texto",
    "bool":           "Booleano",
    "datetime64[ns]": "Data/Hora",
}

_TIPO_MAP_EN = {
    "int64":          "Integer",
    "int32":          "Integer",
    "float64":        "Decimal",
    "float32":        "Decimal",
    "object":         "Text",
    "bool":           "Boolean",
    "datetime64[ns]": "DateTime",
}

# ── Descrição de tabelas PT/EN ────────────────────────────────────────────────

_TABELA_DESC_PT = {
    "FatoVenda":            "Registros de vendas realizadas",
    "FatoPedido":           "Pedidos de clientes",
    "FatoTransacao":        "Transações financeiras",
    "FatoAtividade":        "Atividades e interações registradas",
    "FatoOportunidade":     "Oportunidades no funil de vendas",
    "FatoProducao":         "Registros de produção",
    "FatoPartida":          "Partidas e eventos esportivos",
    "FatoReserva":          "Reservas e hospedagens",
    "FatoPlay":             "Reproduções de conteúdo (plays)",
    "FatoAssinatura":       "Assinaturas e contratos recorrentes",
    "FatoProcesso":         "Processos jurídicos",
    "FatoExtracao":         "Extrações minerais",
    "FatoViagem":           "Corridas e viagens",
    "FatoHorasTrabalhadas": "Horas trabalhadas por colaborador",
    "FatoDespesa":          "Despesas orçamentárias",
    "FatoReceita":          "Arrecadações e receitas governamentais",
    "FatoLicitacao":        "Licitações e contratos públicos",
    "FatoEstoque":          "Movimentações de estoque",
    "FatoCusto":            "Custos operacionais",
    "FatoAbastecimento":    "Abastecimentos de combustível",
    "FatoManutencao":       "Manutenções de veículos/equipamentos",
    "FatoSessao":           "Sessões de atendimento",
    "FatoRodada":           "Rodadas de investimento",
    "FatoMetrica":          "Métricas de desempenho de startups",
    "FatoServico":          "Serviços prestados",
    "FatoAgenda":           "Agendamentos de serviços",
    "FatoEntrega":          "Entregas last mile",
    "FatoEvento":           "Eventos e shows realizados",
    "FatoFornecedor":       "Contratos com fornecedores de eventos",
    "FatoExame":            "Exames laboratoriais realizados",
    "FatoDesempenho":       "Desempenho de unidades franqueadas",
    "FatoTaxa":             "Taxas pagas pelas franqueadas",
    "FatoCota":             "Cotas de condomínio",
    "FatoOcorrencia":       "Ocorrências e chamados no condomínio",
    "FatoOperacao":         "Operações de missões aeroespaciais",
    "dCalendario":          "Tabela calendário para análises temporais",
}

_TABELA_DESC_EN = {
    "FatoVenda":            "Sales transaction records",
    "FatoPedido":           "Customer orders",
    "FatoTransacao":        "Financial transactions",
    "FatoAtividade":        "Recorded activities and interactions",
    "FatoOportunidade":     "Sales pipeline opportunities",
    "FatoProducao":         "Production records",
    "FatoPartida":          "Sports matches and events",
    "FatoReserva":          "Reservations and stays",
    "FatoPlay":             "Content plays / streams",
    "FatoAssinatura":       "Subscriptions and recurring contracts",
    "FatoProcesso":         "Legal proceedings",
    "FatoExtracao":         "Mineral extraction records",
    "FatoViagem":           "Rides and trips",
    "FatoHorasTrabalhadas": "Hours worked per employee",
    "FatoDespesa":          "Budget expenditures",
    "FatoReceita":          "Government collections and revenues",
    "FatoLicitacao":        "Public tenders and contracts",
    "FatoEstoque":          "Inventory movements",
    "FatoCusto":            "Operational costs",
    "FatoAbastecimento":    "Fuel supply records",
    "FatoManutencao":       "Vehicle / equipment maintenance records",
    "FatoSessao":           "Care / therapy sessions",
    "FatoRodada":           "Investment funding rounds",
    "FatoMetrica":          "Startup performance metrics",
    "FatoServico":          "Services rendered",
    "FatoAgenda":           "Service appointments",
    "FatoEntrega":          "Last-mile delivery records",
    "FatoEvento":           "Events and shows",
    "FatoFornecedor":       "Event supplier contracts",
    "FatoExame":            "Laboratory test results",
    "FatoDesempenho":       "Franchise unit performance",
    "FatoTaxa":             "Franchise fees paid",
    "FatoCota":             "Condominium fee payments",
    "FatoOcorrencia":       "Condominium incidents and tickets",
    "FatoOperacao":         "Aerospace mission operations",
    "dCalendario":          "Calendar table for time-based analysis",
}


# ── Funções auxiliares ────────────────────────────────────────────────────────

def _inferir_desc(col: str, lang: str = "pt") -> str:
    """Infere a descrição de uma coluna pelo nome, no idioma solicitado."""
    desc_map = _DESC_EN if lang == "en" else _DESC_PT
    col_lower = col.lower()
    for pattern, desc in desc_map.items():
        if col_lower.startswith(pattern) or col_lower == pattern or pattern in col_lower:
            return desc
    return "—"


def _get_lang() -> str:
    """Lê o idioma atual do session_state do Streamlit."""
    try:
        import streamlit as st
        return st.session_state.get("lang", "pt")
    except Exception:
        return "pt"


# ── Função principal ──────────────────────────────────────────────────────────

def gerar_dicionario(
    nome_setor: str,
    tabelas: dict[str, pd.DataFrame],
    lang: str | None = None,
) -> bytes:
    """
    Gera um ZIP com o dicionário de dados em CSV.

    Contém:
      - 00_resumo.csv     : visão geral de todas as tabelas
      - <NomeTabela>.csv  : dicionário coluna a coluna de cada tabela

    Parâmetros
    ----------
    nome_setor : Nome do setor para o comentário de fallback.
    tabelas    : Dicionário com os DataFrames gerados.
    lang       : 'pt' | 'en'. Se None, lê do session_state.
    """
    if lang is None:
        lang = _get_lang()

    tipo_map   = _TIPO_MAP_EN   if lang == "en" else _TIPO_MAP_PT
    tabela_desc = _TABELA_DESC_EN if lang == "en" else _TABELA_DESC_PT

    # Labels das colunas dos CSVs
    if lang == "en":
        h_resumo = ["Table", "Type", "Rows", "Columns", "Description"]
        h_dict   = ["Column", "Data Type", "Description", "Example", "Nulls", "Unique Values"]
        tipo_fato   = "Fact"
        tipo_dim    = "Dimension"
        tipo_cal    = "Calendar"
        fallback    = f"Table from {nome_setor} sector"
    else:
        h_resumo = ["Tabela", "Tipo", "Linhas", "Colunas", "Descrição"]
        h_dict   = ["Coluna", "Tipo", "Descrição", "Exemplo", "Nulos", "Únicos"]
        tipo_fato   = "Fato"
        tipo_dim    = "Dimensão"
        tipo_cal    = "Calendário"
        fallback    = f"Tabela do setor {nome_setor}"

    buf = io.BytesIO()

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:

        # ── Resumo geral ──────────────────────────────────────────────────
        resumo_rows = []
        for tname, tdf in tabelas.items():
            tipo = (tipo_fato if tname.startswith("Fato")
                    else tipo_cal if tname.startswith("dCal")
                    else tipo_dim)
            resumo_rows.append({
                h_resumo[0]: tname,
                h_resumo[1]: tipo,
                h_resumo[2]: len(tdf),
                h_resumo[3]: len(tdf.columns),
                h_resumo[4]: tabela_desc.get(tname, fallback),
            })

        csv_resumo = io.StringIO()
        pd.DataFrame(resumo_rows).to_csv(csv_resumo, index=False)
        zf.writestr("00_resumo.csv" if lang == "pt" else "00_summary.csv",
                    csv_resumo.getvalue())

        # ── Dicionário por tabela ─────────────────────────────────────────
        for tname, tdf in tabelas.items():
            rows = []
            for col in tdf.columns:
                dtype  = str(tdf[col].dtype)
                sample = tdf[col].dropna().iloc[0] if len(tdf[col].dropna()) > 0 else "—"
                rows.append({
                    h_dict[0]: col,
                    h_dict[1]: tipo_map.get(dtype, dtype),
                    h_dict[2]: _inferir_desc(col, lang),
                    h_dict[3]: str(sample)[:60],
                    h_dict[4]: int(tdf[col].isna().sum()),
                    h_dict[5]: int(tdf[col].nunique()),
                })

            csv_tbl = io.StringIO()
            pd.DataFrame(rows).to_csv(csv_tbl, index=False)
            zf.writestr(f"{tname}.csv", csv_tbl.getvalue())

    return buf.getvalue()
