import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .helpers import new_ids, dcalendario, rand_dates

def gerar_ecommerce(n_linhas: int, start_date, end_date) -> dict[str, pd.DataFrame]:
    """
    Gera dados do setor de E-commerce (Star Schema)
    
    Tabelas geradas:
    - FatoPedido: Pedidos realizados
    - DimCliente: Clientes da loja
    - DimProduto: Produtos vendidos
    - DimPlataforma: Canais de venda
    - DimPagamento: Métodos de pagamento
    - DimFrete: Transportadoras e fretes
    - dCalendario: Tabela calendário
    """
    # Converte para datetime se necessário
    if isinstance(start_date, str):
        start = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        start = start_date
    
    if isinstance(end_date, str):
        end = datetime.strptime(end_date, "%Y-%m-%d")
    else:
        end = end_date
    
    # ========== DIMENSÕES ==========
    
    # DimCliente (500-3000 clientes)
    n_clientes = min(3000, max(500, n_linhas // 10))
    cliente_ids = new_ids(n_clientes, "CLI")
    
    sexos = ["M", "F", "Prefiro não informar"]
    ufs = ["SP", "RJ", "MG", "RS", "BA", "PR", "PE", "CE", "SC", "GO", "DF", "ES", "AM", "PA", "MA"]
    
    dim_cliente = pd.DataFrame({
        "sk_cliente": cliente_ids,
        "id_cliente": cliente_ids,
        "nome": [f"Cliente {i+1}" for i in range(n_clientes)],
        "email": [f"cliente{i+1}@email.com" for i in range(n_clientes)],
        "telefone": [f"({np.random.randint(11,99)}) 9{np.random.randint(1000,9999)}-{np.random.randint(1000,9999)}" 
                     for _ in range(n_clientes)],
        "sexo": np.random.choice(sexos, n_clientes, p=[0.48, 0.48, 0.04]),
        "idade": np.random.randint(18, 80, n_clientes),
        "uf": np.random.choice(ufs, n_clientes),
        "cidade": [f"Cidade {np.random.randint(1,50)}" for _ in range(n_clientes)],
        "data_cadastro": rand_dates(start - timedelta(days=730), start, n_clientes),
        "score_fidelidade": np.random.randint(0, 100, n_clientes),
        "segmento": np.random.choice(["Bronze", "Prata", "Ouro", "Platina", "Diamante"], n_clientes, 
                                      p=[0.4, 0.3, 0.15, 0.1, 0.05])
    })
    
    # DimProduto (200-1000 produtos)
    n_produtos = min(1000, max(200, n_linhas // 20))
    produto_ids = new_ids(n_produtos, "PRO")
    
    categorias = ["Eletrônicos", "Moda", "Casa e Decoração", "Beleza", "Esportes", 
                  "Livros", "Brinquedos", "Alimentos", "Ferramentas", "Informática",
                  "Saúde", "Automotivo", "Pet Shop", "Jardim", "Papelaria"]
    
    dim_produto = pd.DataFrame({
        "sk_produto": produto_ids,
        "id_produto": produto_ids,
        "nome_produto": [f"Produto {i+1}" for i in range(n_produtos)],
        "categoria": np.random.choice(categorias, n_produtos),
        "subcategoria": [f"Sub{np.random.randint(1,10)}" for _ in range(n_produtos)],
        "preco_unitario": np.random.uniform(10, 2000, n_produtos).round(2),
        "custo_unitario": np.random.uniform(5, 1000, n_produtos).round(2),
        "peso_kg": np.random.uniform(0.1, 10, n_produtos).round(2),
        "marca": [f"Marca {np.random.randint(1,30)}" for _ in range(n_produtos)],
        "estoque_inicial": np.random.randint(0, 500, n_produtos)
    })
    
    # DimPlataforma
    plataformas = ["Website", "App iOS", "App Android", "WhatsApp", "Marketplace", "Instagram Shop"]
    
    dim_plataforma = pd.DataFrame({
        "sk_plataforma": new_ids(len(plataformas), "PLA"),
        "nome_plataforma": plataformas,
        "taxa_comissao": [0.0, 0.0, 0.0, 0.0, 0.12, 0.08],
        "conversao_media": np.random.uniform(0.01, 0.05, len(plataformas)).round(3)
    })
    
    # DimPagamento
    metodos = ["Cartão Crédito", "Cartão Débito", "PIX", "Boleto", "PayPal", "Mercado Pago", "PicPay"]
    parcelamentos = [1, 2, 3, 4, 5, 6, 8, 10, 12]
    
    dim_pagamento = pd.DataFrame({
        "sk_pagamento": new_ids(len(metodos), "PAG"),
        "metodo": metodos,
        "max_parcelas": np.random.choice([1, 3, 6, 12, 18], len(metodos)),
        "taxa_juros": np.random.uniform(0, 0.05, len(metodos)).round(3),
        "tempo_aprovacao_segundos": np.random.choice([1, 5, 10, 30, 60], len(metodos))
    })
    
    # DimFrete
    transportadoras = ["Correios", "Jadlog", "Loggi", "Total Express", "DHL", "FedEx", "Rappi", "Mercado Envios"]
    
    dim_frete = pd.DataFrame({
        "sk_frete": new_ids(len(transportadoras), "FRE"),
        "transportadora": transportadoras,
        "prazo_medio_dias": np.random.randint(2, 20, len(transportadoras)),
        "valor_kg": np.random.uniform(2, 20, len(transportadoras)).round(2),
        "rastreamento_disponivel": np.random.choice([True, False], len(transportadoras), p=[0.9, 0.1])
    })
    
    # ========== TABELA FATO ==========
    # Gerar pedidos
    datas_pedido = rand_dates(start, end, n_linhas)
    
    # Selecionar chaves estrangeiras
    cliente_keys = np.random.choice(dim_cliente["sk_cliente"], n_linhas)
    produto_keys = np.random.choice(dim_produto["sk_produto"], n_linhas)
    plataforma_keys = np.random.choice(dim_plataforma["sk_plataforma"], n_linhas)
    pagamento_keys = np.random.choice(dim_pagamento["sk_pagamento"], n_linhas)
    frete_keys = np.random.choice(dim_frete["sk_frete"], n_linhas)
    
    # Calcular valores
    precos = dim_produto.set_index("sk_produto")["preco_unitario"].to_dict()
    custos = dim_produto.set_index("sk_produto")["custo_unitario"].to_dict()
    pesos = dim_produto.set_index("sk_produto")["peso_kg"].to_dict()
    
    quantidade = np.random.randint(1, 6, n_linhas)
    valor_produtos = [precos.get(pk, 50) * q for pk, q in zip(produto_keys, quantidade)]
    custo_produtos = [custos.get(pk, 25) * q for pk, q in zip(produto_keys, quantidade)]
    
    # Calcular frete (baseado no peso e transportadora)
    valor_frete_base = [pesos.get(pk, 1) * q * np.random.uniform(3, 10) for pk, q in zip(produto_keys, quantidade)]
    
    # Fator de frete por transportadora
    fretes_dict = dim_frete.set_index("sk_frete")["valor_kg"].to_dict()
    fator_frete = [fretes_dict.get(fk, 5) for fk in frete_keys]
    valor_frete = [vfb * ff / 5 for vfb, ff in zip(valor_frete_base, fator_frete)]
    
    # Desconto (0-30%)
    desconto_percent = np.random.uniform(0, 0.3, n_linhas).round(2)
    desconto_valor = [vp * dp for vp, dp in zip(valor_produtos, desconto_percent)]
    
    valor_total = [vp + vf - dv for vp, vf, dv in zip(valor_produtos, valor_frete, desconto_valor)]
    
    # Status do pedido
    status = np.random.choice(
        ["Entregue", "Processando", "Cancelado", "Devolvido", "Extraviado", "Em trânsito"],
        n_linhas,
        p=[0.65, 0.12, 0.08, 0.05, 0.02, 0.08]
    )
    
    # Avaliação (1-5, apenas entregues)
    avaliacao = [np.random.randint(1, 6) if s == "Entregue" and np.random.random() < 0.6 else None 
                 for s in status]
    
    # Data de entrega (apenas para entregues)
    data_entrega = []
    for d, s in zip(datas_pedido, status):
        if s == "Entregue":
            prazo = np.random.randint(2, 20)
            data_entrega.append(d + timedelta(days=prazo))
        else:
            data_entrega.append(None)
    
    # Margem de lucro
    margem_lucro = [(vp - cp) / vp * 100 if vp > 0 else 0 
                    for vp, cp in zip(valor_produtos, custo_produtos)]
    
    fato_pedido = pd.DataFrame({
        "sk_pedido": new_ids(n_linhas, "PED"),
        "data_pedido": datas_pedido,
        "data_entrega": data_entrega,
        "quantidade": quantidade,
        "valor_produtos": [round(vp, 2) for vp in valor_produtos],
        "valor_frete": [round(vf, 2) for vf in valor_frete],
        "desconto": [round(dv, 2) for dv in desconto_valor],
        "desconto_percentual": desconto_percent,
        "valor_total": [round(vt, 2) for vt in valor_total],
        "custo_produtos": [round(cp, 2) for cp in custo_produtos],
        "margem_lucro_percentual": [round(ml, 2) for ml in margem_lucro],
        "status": status,
        "avaliacao": avaliacao,
        "tempo_entrega_dias": [(de - d).days if de else None for d, de in zip(datas_pedido, data_entrega)],
        "sk_cliente": cliente_keys,
        "sk_produto": produto_keys,
        "sk_plataforma": plataforma_keys,
        "sk_pagamento": pagamento_keys,
        "sk_frete": frete_keys
    })
    
    return {
        "FatoPedido": fato_pedido,
        "DimCliente": dim_cliente,
        "DimProduto": dim_produto,
        "DimPlataforma": dim_plataforma,
        "DimPagamento": dim_pagamento,
        "DimFrete": dim_frete,
        "dCalendario": dcalendario(start, end)
    }
