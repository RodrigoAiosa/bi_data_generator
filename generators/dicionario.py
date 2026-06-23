"""generators/dicionario.py — Gera dicionário de dados em Excel."""

import io
import pandas as pd

# Descrições por padrão de nome de coluna
_DESC: dict[str, str] = {
    # IDs
    "id_":          "Identificador único",
    "sk_":          "Surrogate key (chave substituta)",
    # Datas
    "data_":        "Data do evento",
    "id_data":      "Chave para dCalendario",
    # Valores
    "valor_":       "Valor monetário (R$)",
    "receita":      "Receita gerada (R$)",
    "custo_":       "Custo associado (R$)",
    "preco_":       "Preço unitário (R$)",
    "desconto":     "Desconto aplicado",
    "margem":       "Margem percentual",
    # Quantidades
    "qtd_":         "Quantidade",
    "volume_":      "Volume físico",
    "quantidade":   "Quantidade de unidades",
    # Status / flags
    "status":       "Status do registro",
    "ativo":        "Indica se o registro está ativo",
    "cancelado":    "Indica se foi cancelado",
    "aprovado":     "Indica se foi aprovado",
    # Textos comuns
    "nome":         "Nome descritivo",
    "descricao":    "Descrição detalhada",
    "tipo_":        "Classificação por tipo",
    "categoria":    "Categoria de negócio",
    "canal":        "Canal de origem ou venda",
    "regiao":       "Região geográfica",
    "uf":           "Unidade federativa (estado)",
    "cidade":       "Município",
    "cnpj":         "CNPJ da empresa",
    "cpf":          "CPF do indivíduo",
    "email":        "Endereço de e-mail",
    "telefone":     "Número de telefone",
    # Métricas
    "pct":          "Percentual (%)",
    "taxa_":        "Taxa percentual (%)",
    "score":        "Pontuação / índice",
    "avaliacao":    "Nota de avaliação",
    "nps":          "Net Promoter Score",
    "mrr":          "Monthly Recurring Revenue",
    "arr":          "Annual Recurring Revenue",
    "churn":        "Indicador de cancelamento",
}

_TIPO_MAP = {
    "int64":    "Inteiro",
    "int32":    "Inteiro",
    "float64":  "Decimal",
    "float32":  "Decimal",
    "object":   "Texto",
    "bool":     "Booleano",
    "datetime64[ns]": "Data/Hora",
}

_TABELA_DESC = {
    "FatoVenda":        "Registros de vendas realizadas",
    "FatoPedido":       "Pedidos de clientes",
    "FatoTransacao":    "Transações financeiras",
    "FatoAtividade":    "Atividades e interações registradas",
    "FatoOportunidade": "Oportunidades no funil de vendas",
    "FatoProducao":     "Registros de produção",
    "FatoPartida":      "Partidas e eventos esportivos",
    "FatoReserva":      "Reservas e hospedagens",
    "FatoPlay":         "Reproduções de conteúdo (plays)",
    "FatoAssinatura":   "Assinaturas e contratos recorrentes",
    "FatoProcesso":     "Processos jurídicos",
    "FatoExtracao":     "Extrações minerais",
    "FatoViagem":       "Corridas e viagens",
    "FatoHorasTrabalhadas": "Horas trabalhadas por colaborador",
    "FatoDespesa":      "Despesas orçamentárias",
    "FatoReceita":      "Arrecadações e receitas governamentais",
    "FatoLicitacao":    "Licitações e contratos públicos",
    "FatoEstoque":      "Movimentações de estoque",
    "FatoCusto":        "Custos operacionais",
    "dCalendario":      "Tabela calendário para análises temporais",
}


def _inferir_desc(col: str) -> str:
    col_lower = col.lower()
    for pattern, desc in _DESC.items():
        if col_lower.startswith(pattern) or col_lower == pattern or pattern in col_lower:
            return desc
    return "—"


def gerar_dicionario(nome_setor: str, tabelas: dict[str, pd.DataFrame]) -> bytes:
    """
    Gera um ZIP com o dicionário de dados em CSV (sem dependências extras).

    Contém:
      - 00_resumo.csv        : visão geral de todas as tabelas
      - <NomeTabela>.csv     : dicionário coluna a coluna de cada tabela
    """
    import zipfile

    buf = io.BytesIO()

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:

        # ── Resumo geral ─────────────────────────────────────────────────
        resumo_rows = []
        for tname, tdf in tabelas.items():
            tipo = ("Fato" if tname.startswith("Fato")
                    else "Calendário" if tname.startswith("dCal")
                    else "Dimensão")
            resumo_rows.append({
                "Tabela":     tname,
                "Tipo":       tipo,
                "Linhas":     len(tdf),
                "Colunas":    len(tdf.columns),
                "Descrição":  _TABELA_DESC.get(tname, f"Tabela do setor {nome_setor}"),
            })

        csv_resumo = io.StringIO()
        pd.DataFrame(resumo_rows).to_csv(csv_resumo, index=False)
        zf.writestr("00_resumo.csv", csv_resumo.getvalue())

        # ── Dicionário por tabela ─────────────────────────────────────────
        for tname, tdf in tabelas.items():
            rows = []
            for col in tdf.columns:
                dtype  = str(tdf[col].dtype)
                sample = tdf[col].dropna().iloc[0] if len(tdf[col].dropna()) > 0 else "—"
                rows.append({
                    "Coluna":     col,
                    "Tipo":       _TIPO_MAP.get(dtype, dtype),
                    "Descrição":  _inferir_desc(col),
                    "Exemplo":    str(sample)[:60],
                    "Nulos":      int(tdf[col].isna().sum()),
                    "Únicos":     int(tdf[col].nunique()),
                })

            csv_tbl = io.StringIO()
            pd.DataFrame(rows).to_csv(csv_tbl, index=False)
            zf.writestr(f"{tname}.csv", csv_tbl.getvalue())

    return buf.getvalue()
